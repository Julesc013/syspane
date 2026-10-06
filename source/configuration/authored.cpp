#include "authored.hpp"
#include "authored_schemas.hpp"
#include <algorithm>
#include <cmath>
#include <functional>
#include <regex>

namespace syspane::configuration {
namespace {
using protocol::Error;
void require(bool value,const char* code){if(!value)throw Error(code);}
const std::map<std::string,Json>& schemas(){
    static const std::map<std::string,Json> value=[] {
        std::map<std::string,Json> result;
        for(const char* text:{settings_schema,scene_v0_2_schema,layout_schema,binding_schema,command_v0_2_schema,command_v0_3_schema,content_package_schema,content_catalog_schema,preset_schema,theme_schema}){
            auto item=Json::parse(text);result.emplace(item["$id"].get<std::string>(),std::move(item));
        }
        return result;
    }();return value;
}
const Json& schema(const char* name){return schemas().at(std::string("https://schemas.example.invalid/syspane/")+name+".schema.json");}
bool type(const Json& v,const std::string& kind){
    if(kind=="object")return v.is_object();
    if(kind=="array")return v.is_array();
    if(kind=="string")return v.is_string();
    if(kind=="null")return v.is_null();
    if(kind=="boolean")return v.is_boolean();
    if(kind=="number")return v.is_number()&&std::isfinite(v.get<double>());
    if(kind=="integer")return v.is_number()&&std::isfinite(v.get<double>())&&std::floor(v.get<double>())==v.get<double>();
    throw Error("schema.unsupported");
}
bool matches(const Json& s,const Json& v,const Json& root,unsigned depth=0){
    require(depth<64,"schema.depth");
    if(s.contains("$ref")){
        const auto ref=s["$ref"].get<std::string>();const auto hash=ref.find('#');
        const auto name=ref.substr(0,hash);const auto& doc=name.empty()?root:schemas().at(name);
        const auto& target=hash==std::string::npos?doc:doc.at(Json::json_pointer(ref.substr(hash+1)));
        if(!matches(target,v,doc,depth+1))return false;
    }
    if(s.contains("type")){
        bool valid=false;const auto& t=s["type"];
        if(t.is_string())valid=type(v,t.get<std::string>());else for(const auto& k:t)valid=valid||type(v,k.get<std::string>());
        if(!valid)return false;
    }
    if(s.contains("const")&&s["const"]!=v)return false;
    if(s.contains("enum")&&std::find(s["enum"].begin(),s["enum"].end(),v)==s["enum"].end())return false;
    for(const char* key:{"oneOf","anyOf","allOf"})if(s.contains(key)){
        std::size_t count=0;for(const auto& child:s[key])if(matches(child,v,root,depth+1))++count;
        if((std::string(key)=="oneOf"&&count!=1)||(std::string(key)=="anyOf"&&!count)||
           (std::string(key)=="allOf"&&count!=s[key].size()))return false;
    }
    if(s.contains("not")&&matches(s["not"],v,root,depth+1))return false;
    if(s.contains("if")){
        const char* branch=matches(s["if"],v,root,depth+1)?"then":"else";
        if(s.contains(branch)&&!matches(s[branch],v,root,depth+1))return false;
    }
    if(v.is_object()){
        if(s.contains("maxProperties")&&v.size()>s["maxProperties"].get<std::size_t>())return false;
        if(s.contains("required"))for(const auto& k:s["required"])if(!v.contains(k.get<std::string>()))return false;
        for(auto it=v.begin();it!=v.end();++it){
            if(s.contains("propertyNames")&&!matches(s["propertyNames"],it.key(),root,depth+1))return false;
            if(s.contains("properties")&&s["properties"].contains(it.key())){
                if(!matches(s["properties"][it.key()],it.value(),root,depth+1))return false;
            }else if(s.contains("additionalProperties")&&!s["additionalProperties"].get<bool>())return false;
        }
    }
    if(v.is_array()){
        if((s.contains("minItems")&&v.size()<s["minItems"].get<std::size_t>())||
           (s.contains("maxItems")&&v.size()>s["maxItems"].get<std::size_t>()))return false;
        for(std::size_t i=0;i<v.size();++i){
            if(s.contains("items")&&!matches(s["items"],v[i],root,depth+1))return false;
            if(s.value("uniqueItems",false))for(std::size_t j=0;j<i;++j)if(v[i]==v[j])return false;
        }
    }
    if(v.is_string()){
        const auto& text=v.get_ref<const std::string&>();
        const auto length=static_cast<std::size_t>(std::count_if(text.begin(),text.end(),[](unsigned char c){return (c&0xc0)!=0x80;}));
        if((s.contains("minLength")&&length<s["minLength"].get<std::size_t>())||
           (s.contains("maxLength")&&length>s["maxLength"].get<std::size_t>()))return false;
        if(s.contains("pattern")&&!std::regex_search(text,std::regex(s["pattern"].get<std::string>())))return false;
    }
    if(v.is_number()){
        const auto n=v.get<double>();if(!std::isfinite(n))return false;
        if((s.contains("minimum")&&n<s["minimum"].get<double>())||(s.contains("maximum")&&n>s["maximum"].get<double>()))return false;
    }
    return true;
}
void structural(const Json& value,const char* name,std::size_t limit){
    const auto text=value.dump();require(text.size()<=limit,"authored.size");require(protocol::parse(text)==value,"authored.encoding");
    const auto& s=schema(name);require(matches(s,value,s),"authored.schema");
}
std::uint64_t revision(const Json& v){
    require(v.is_string(),"authored.revision");const auto n=protocol::decimal(v.get_ref<const std::string&>());
    require(n.has_value(),"authored.revision");return *n;
}
void scene_semantics(const Json& scene){
    (void)revision(scene["revision"]);std::map<std::string,const Json*> widgets;std::map<std::string,unsigned> owned;
    for(const auto& widget:scene["widgets"]){
        require(widgets.emplace(widget["id"].get<std::string>(),&widget).second,"scene.duplicate");
        const auto& layout=widget["layout"];std::vector<Json> variants{layout["base"]};double previous=-1;
        if(layout.contains("breakpoints"))for(const auto& point:layout["breakpoints"]){
            const auto width=point["min_width_dip"].get<double>();require(width>previous,"scene.breakpoints");previous=width;variants.push_back(point["layout"]);
        }
        for(const auto& variant:variants){
            const auto kind=variant["kind"].get<std::string>();const bool group=widget["kind"]=="group";
            require(group?(kind=="canvas"||kind=="stack"||kind=="grid"||kind=="fixed"):(kind=="fixed"||kind=="flow"),"scene.layout_kind");
            if(kind=="flow")for(const char* axis:{"width","height"}){
                const auto& b=variant[axis];require(b["min"].get<double>()<=b["preferred"].get<double>()&&b["preferred"].get<double>()<=b["max"].get<double>(),"scene.layout_bounds");
            }
        }
    }
    for(const auto& id:scene["roots"])++owned[id.get<std::string>()];
    for(const auto& row:widgets)if(row.second->contains("children"))for(const auto& id:(*row.second)["children"])++owned[id.get<std::string>()];
    require(owned.size()==widgets.size(),"scene.ownership");
    for(const auto& row:owned)require(row.second==1&&widgets.count(row.first),"scene.ownership");
    std::set<std::string> visited;
    std::function<void(const std::string&,unsigned)> visit=[&](const std::string& id,unsigned depth){
        require(depth<=16,"scene.depth");require(visited.insert(id).second,"scene.cycle");
        const auto& widget=*widgets.at(id);if(widget.contains("children"))for(const auto& child:widget["children"])visit(child.get<std::string>(),depth+1);
    };
    for(const auto& id:scene["roots"])visit(id.get<std::string>(),1);
    require(visited.size()==widgets.size(),"scene.cycle");
}
}
std::uint64_t authored_revision(const Authored& value){return revision(value.settings.at("revision"));}
void validate_content_document(const Json& value,const std::string& kind){
    require(kind=="content-catalog"||kind=="content-package"||kind=="preset"||kind=="theme","content.kind");
    const auto name="0.1.0/"+kind;structural(value,name.c_str(),kind=="content-catalog"?16384:(kind=="content-package"?65536:262144));
}
void validate_scene_document(const Json& value){structural(value,"0.2.0/scene",262144);(void)revision(value["revision"]);scene_semantics(value);}
void validate_authored(const Authored& value){
    structural(value.settings,"0.1.0/settings",16384);structural(value.scene,"0.2.0/scene",262144);
    require(revision(value.settings["revision"])==revision(value.scene["revision"]),"authored.mixed_revision");scene_semantics(value.scene);
}
void validate_command(const Json& value){
    structural(value,value.is_object()&&value.contains("schema_version")&&value["schema_version"]=="0.3.0"?"0.3.0/command":"0.2.0/command",16384);(void)revision(value["expected_revision"]);(void)revision(value["policy_generation"]);
    std::set<std::string> paths;bool scene=false;
    for(const auto& op:value["operations"]){
        if(op["op"]=="scene.replace"){
            require(!scene,"command.duplicate_scene");scene=true;scene_semantics(op["scene"]);
            require(op["scene"]["revision"]==value["expected_revision"],"command.scene_revision");
        }else require(paths.insert(op["path"].get<std::string>()).second,"command.duplicate_path");
    }
}
void authorize_authored(const Json& command,const Authority& authority,const Policy& policy,std::uint64_t current){
    require(authority.authenticated&&authority.role_grants.count(authority.role)&&
        (authority.role=="console"||authority.role=="desktop"||authority.role=="saver_settings")&&policy.available,"policy.denied");
    require(revision(command["policy_generation"])==policy.revision,"policy.changed");
    require(revision(command["expected_revision"])==current,"revision.changed");
    require(!policy.denied_capabilities.count(command["intent"]=="commit"?"settings.commit":"settings.preview"),"policy.denied");
    if(command["schema_version"]=="0.3.0")require(!policy.denied_capabilities.count("content.select"),"policy.denied");
    for(const auto& op:command["operations"]){
        const auto name=op["op"].get<std::string>();require(!policy.denied_capabilities.count(name),"policy.denied");
        if(name=="scene.replace")require(authority.role!="saver_settings","policy.denied");
        else{
            const auto found=policy.forced.find(op["path"].get<std::string>());
            require(found==policy.forced.end()||found->second==op["value"],"policy.forced");
        }
    }
}
Authored prepare_authored(const Authored& current,const Json& command,const Authority& authority,const Policy& policy){
    validate_authored(current);validate_command(command);authorize_authored(command,authority,policy,authored_revision(current));
    Authored candidate=current;
    for(const auto& op:command["operations"]){
        if(op["op"]=="scene.replace")candidate.scene=op["scene"];
        else{const auto path=op["path"].get<std::string>();const auto dot=path.find('.');candidate.settings[path.substr(0,dot)][path.substr(dot+1)]=op["value"];}
    }
    validate_authored(candidate);return candidate;
}
}
