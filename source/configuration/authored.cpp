#include "authored.hpp"
#include "content.hpp"
#include "authored_schemas.hpp"
#include <algorithm>
#include <cmath>
#include <functional>
#include <limits>
#include <memory>
#include <regex>

namespace syspane::configuration {
namespace {
using protocol::Error;
void require(bool value,const char* code){if(!value)throw Error(code);}
const std::map<std::string,Json>& schemas(){
    static const std::map<std::string,Json> value=[] {
        std::map<std::string,Json> result;
        for(const char* text:{settings_schema,scene_v0_2_schema,scene_v0_3_schema,scene_v0_4_schema,scene_v0_5_schema,layout_schema,binding_schema,visibility_schema,command_v0_2_schema,command_v0_3_schema,command_v0_4_schema,command_v0_5_schema,command_v0_6_schema,command_v0_7_schema,command_v0_8_schema,command_result_schema,content_package_schema,content_catalog_schema,preset_schema,theme_schema,theme_v0_2_schema,resource_selection_v0_2_schema}){
            auto item=Json::parse(text);result.emplace(item["$id"].get<std::string>(),std::move(item));
        }
        return result;
    }();return value;
}
const Json& schema(const char* name){return schemas().at(std::string("https://schemas.example.invalid/syspane/")+name+".schema.json");}
const std::regex& pattern(const std::string& text){
    // Only the compiled-in schemas supply patterns. Compile that finite set once;
    // authored strings never add cache entries. The immutable map is shared safely
    // by independent configuration and recovery workers.
    static const std::map<std::string,std::regex> patterns=[] {
        std::map<std::string,std::regex> result;
        const std::function<void(const Json&)> collect=[&](const Json& node){
            if(node.is_object()&&node.contains("pattern")&&node["pattern"].is_string()){
                const auto value=node["pattern"].get<std::string>();result.emplace(value,std::regex(value));
            }
            if(node.is_structured())for(const auto& child:node)collect(child);
        };
        for(const auto& entry:schemas())collect(entry.second);
        return result;
    }();
    return patterns.at(text);
}
enum SchemaType:unsigned {NoType=0,Object=1,Array=2,String=4,Null=8,Boolean=16,Number=32,Integer=64};
unsigned schema_type(const std::string& kind){
    if(kind=="object")return Object;
    if(kind=="array")return Array;
    if(kind=="string")return String;
    if(kind=="null")return Null;
    if(kind=="boolean")return Boolean;
    if(kind=="number")return Number;
    if(kind=="integer")return Integer;
    throw Error("schema.unsupported");
}
struct CompiledSchema {
    using Children=std::vector<const CompiledSchema*>;
    const CompiledSchema *ref=nullptr,*negation=nullptr,*condition=nullptr,*then_branch=nullptr,*else_branch=nullptr;
    const CompiledSchema *property_names=nullptr,*items=nullptr,*contains=nullptr;
    const Json *constant=nullptr,*enumeration=nullptr;
    const std::regex* pattern=nullptr;
    std::optional<unsigned> types;
    std::optional<Children> one,any,all;
    std::map<std::string,const CompiledSchema*> properties;
    std::vector<std::string> required;
    bool additional=true,unique=false;
    std::size_t max_properties=std::numeric_limits<std::size_t>::max(),min_items=0,max_items=std::numeric_limits<std::size_t>::max();
    std::size_t min_length=0,max_length=std::numeric_limits<std::size_t>::max();
    std::optional<double> minimum,maximum;
};
class SchemaGraph {
    // Addresses refer only to immutable compiled-in schemas. Insert a stable node
    // before following references so cycles cannot recurse during construction.
    std::map<const Json*,std::unique_ptr<CompiledSchema>> nodes;
    const CompiledSchema* compile(const Json& s,const Json& root){
        const auto found=nodes.find(&s);if(found!=nodes.end())return found->second.get();
        auto owned=std::make_unique<CompiledSchema>();auto* n=owned.get();nodes.emplace(&s,std::move(owned));
        if(s.contains("$ref")){
            const auto ref=s["$ref"].get<std::string>();const auto hash=ref.find('#');
            const auto name=ref.substr(0,hash);const auto& doc=name.empty()?root:schemas().at(name);
            const auto& target=hash==std::string::npos?doc:doc.at(Json::json_pointer(ref.substr(hash+1)));
            n->ref=compile(target,doc);
        }
        if(s.contains("type")){
            unsigned mask=0;const auto& t=s["type"];
            if(t.is_string())mask=schema_type(t.get<std::string>());else for(const auto& k:t)mask|=schema_type(k.get<std::string>());
            n->types=mask;
        }
        if(s.contains("const"))n->constant=&s["const"];
        if(s.contains("enum"))n->enumeration=&s["enum"];
        const auto children=[&](const char* key,std::optional<CompiledSchema::Children>& out){
            if(s.contains(key)){out.emplace();for(const auto& child:s[key])out->push_back(compile(child,root));}
        };
        children("oneOf",n->one);children("anyOf",n->any);children("allOf",n->all);
        const auto child=[&](const char* key){return s.contains(key)?compile(s[key],root):nullptr;};
        n->negation=child("not");n->condition=child("if");n->then_branch=child("then");n->else_branch=child("else");
        n->property_names=child("propertyNames");n->items=child("items");n->contains=child("contains");
        if(s.contains("required"))n->required=s["required"].get<std::vector<std::string>>();
        if(s.contains("properties"))for(auto it=s["properties"].begin();it!=s["properties"].end();++it)n->properties.emplace(it.key(),compile(it.value(),root));
        n->additional=s.value("additionalProperties",true);n->unique=s.value("uniqueItems",false);
        n->max_properties=s.value("maxProperties",n->max_properties);
        n->min_items=s.value("minItems",n->min_items);n->max_items=s.value("maxItems",n->max_items);
        n->min_length=s.value("minLength",n->min_length);n->max_length=s.value("maxLength",n->max_length);
        if(s.contains("minimum"))n->minimum=s["minimum"].get<double>();
        if(s.contains("maximum"))n->maximum=s["maximum"].get<double>();
        if(s.contains("pattern"))n->pattern=&pattern(s["pattern"].get_ref<const std::string&>());
        return n;
    }
public:
    SchemaGraph(){for(const auto& entry:schemas())compile(entry.second,entry.second);}
    const CompiledSchema& at(const Json& s)const{return *nodes.at(&s);}
};
const CompiledSchema& compiled_schema(const char* name){
    // C++ static initialization publishes only the completed immutable graph.
    // No authored value or evaluation result is retained here.
    static const SchemaGraph graph;return graph.at(schema(name));
}
bool matches(const CompiledSchema& s,const Json& v,unsigned depth=0){
    require(depth<64,"schema.depth");
    if(s.ref&&!matches(*s.ref,v,depth+1))return false;
    if(s.types){
        unsigned actual=v.is_object()?Object:v.is_array()?Array:v.is_string()?String:v.is_null()?Null:v.is_boolean()?Boolean:NoType;
        if(v.is_number()){
            const double n=v.get<double>();
            if(std::isfinite(n))actual=Number|(std::floor(n)==n?Integer:NoType);
        }
        if(!(actual&*s.types))return false;
    }
    if(s.constant&&*s.constant!=v)return false;
    if(s.enumeration&&std::find(s.enumeration->begin(),s.enumeration->end(),v)==s.enumeration->end())return false;
    for(const auto* group:{&s.one,&s.any,&s.all})if(*group){
        std::size_t count=0;for(const auto* child:**group)if(matches(*child,v,depth+1))++count;
        if((group==&s.one&&count!=1)||(group==&s.any&&!count)||(group==&s.all&&count!=(**group).size()))return false;
    }
    if(s.negation&&matches(*s.negation,v,depth+1))return false;
    if(s.condition){
        const auto* branch=matches(*s.condition,v,depth+1)?s.then_branch:s.else_branch;
        if(branch&&!matches(*branch,v,depth+1))return false;
    }
    if(v.is_object()){
        if(v.size()>s.max_properties)return false;
        for(const auto& k:s.required)if(!v.contains(k))return false;
        for(auto it=v.begin();it!=v.end();++it){
            if(s.property_names&&!matches(*s.property_names,it.key(),depth+1))return false;
            const auto property=s.properties.find(it.key());
            if(property!=s.properties.end()){
                if(!matches(*property->second,it.value(),depth+1))return false;
            }else if(!s.additional)return false;
        }
    }
    if(v.is_array()){
        if(s.contains){
            bool found=false;for(const auto& item:v)if(matches(*s.contains,item,depth+1)){found=true;break;}
            if(!found)return false;
        }
        if(v.size()<s.min_items||v.size()>s.max_items)return false;
        for(std::size_t i=0;i<v.size();++i){
            if(s.items&&!matches(*s.items,v[i],depth+1))return false;
            if(s.unique)for(std::size_t j=0;j<i;++j)if(v[i]==v[j])return false;
        }
    }
    if(v.is_string()){
        const auto& text=v.get_ref<const std::string&>();
        if(s.min_length||s.max_length!=std::numeric_limits<std::size_t>::max()){
            const auto length=static_cast<std::size_t>(std::count_if(text.begin(),text.end(),[](unsigned char c){return (c&0xc0)!=0x80;}));
            if(length<s.min_length||length>s.max_length)return false;
        }
        if(s.pattern&&!std::regex_search(text,*s.pattern))return false;
    }
    if(v.is_number()){
        const auto n=v.get<double>();if(!std::isfinite(n))return false;
        if((s.minimum&&n<*s.minimum)||(s.maximum&&n>*s.maximum))return false;
    }
    return true;
}
void structural(const Json& value,const char* name,std::size_t limit,protocol::ParseProfile profile=protocol::ParseProfile::ordinary){
    const auto text=value.dump();require(text.size()<=limit,"authored.size");require(protocol::parse(text,profile)==value,"authored.encoding");
    require(matches(compiled_schema(name),value),"authored.schema");
}
std::uint64_t revision(const Json& v){
    require(v.is_string(),"authored.revision");const auto n=protocol::decimal(v.get_ref<const std::string&>());
    require(n.has_value(),"authored.revision");return *n;
}
void plain(const Json& value){
    const auto& s=value.get_ref<const std::string&>();require(s.size()<=4096,"scene.text");
    require(std::count(s.begin(),s.end(),'\n')<64,"scene.text");
    for(std::size_t i=0;i<s.size();++i){const auto c=static_cast<unsigned char>(s[i]);
        require((c>=32||c==10)&&c!=127,"scene.text");
        if(c==0xc2&&i+1<s.size())require(static_cast<unsigned char>(s[i+1])<0x80||static_cast<unsigned char>(s[i+1])>0x9f,"scene.text");}
}
void content_semantics(const Json& w){
    const auto& kind=w["kind"];const auto& c=w["content"];const auto& bindings=w["bindings"];
    if(kind=="text")plain(c["body"]);
    if(kind=="value"||kind=="status"||kind=="chart")require(bindings[0]["kind"]!="selector"||bindings[0]["mode"]=="singleton","scene.binding");
    if(kind=="table"){
        require(c["columns"].size()==bindings.size(),"scene.columns");Json shape;std::set<std::string> fields;
        for(const auto& column:c["columns"])plain(column["label"]);
        for(const auto& b:bindings){require(b["kind"]=="selector"&&b["mode"]=="collection","scene.binding");auto query=b;query.erase("field");
            require(shape.is_null()||shape==query,"scene.columns");shape=std::move(query);require(fields.insert(b["field"].get<std::string>()).second,"scene.columns");}
    }
    if(kind=="chart"&&c["axis"]["mode"]=="fixed")require(c["axis"]["minimum"].get<double>()<c["axis"]["maximum"].get<double>(),"scene.axis");
    if(kind=="image"){plain(c["alt"]);validate_content_path(c["asset"]["path"].get<std::string>());}
}
void scene_semantics(const Json& scene){
    (void)revision(scene["revision"]);std::map<std::string,const Json*> widgets;std::map<std::string,unsigned> owned;
    for(const auto& widget:scene["widgets"]){
        if(scene["schema_version"]!="0.2.0")content_semantics(widget);
        if(widget.contains("visibility"))validate_visibility_document(widget["visibility"]);
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
namespace {void font_semantics(const Json& font){const auto& family=font.at("family").get_ref<const std::string&>();require(!family.empty()&&family.size()<=512&&family.front()!=' '&&family.back()!=' ',"theme.family");
            // Older native regex engines disagree on escaped control ranges.
            // Enforce the literal-name contract over validated UTF-8 bytes too.
            for(std::size_t i=0;i<family.size();++i){const auto c=static_cast<unsigned char>(family[i]);require(c>=32&&c!=127&&c!=',',"theme.family");
                if(c==0xc2&&i+1<family.size()){const auto next=static_cast<unsigned char>(family[i+1]);require(next<0x80||next>0x9f,"theme.family");}}}}
void validate_content_document(const Json& value,const std::string& kind){
    require(kind=="content-catalog"||kind=="content-package"||kind=="preset"||kind=="theme"||kind=="resource-selection","content.kind");
    const bool typography=kind=="theme"&&value.is_object()&&value.value("schema_version",Json())=="0.2.0";
    const auto name=std::string((typography||kind=="resource-selection")?"0.2.0/":"0.1.0/")+kind;structural(value,name.c_str(),kind=="resource-selection"?4096:kind=="content-catalog"?16384:(kind=="content-package"?65536:262144));
    if(typography){
        font_semantics(value.at("font"));if(value.contains("font_roles"))for(const auto& font:value.at("font_roles"))font_semantics(font);
    }
}
void validate_scene_document(const Json& value){const auto version=value.is_object()?value.value("schema_version",Json()):Json();structural(value,version=="0.5.0"?"0.5.0/scene":version=="0.4.0"?"0.4.0/scene":version=="0.3.0"?"0.3.0/scene":"0.2.0/scene",262144);(void)revision(value["revision"]);scene_semantics(value);}
Json upgrade_scene_content(const Json& value){
    validate_scene_document(value);if(value["schema_version"]!="0.2.0")return value;auto next=value;next["schema_version"]="0.3.0";
    for(auto& w:next["widgets"]){const auto& kind=w["kind"];require(kind!="chart"&&kind!="image","scene.content_required");w["content"]=Json::object();
        if(kind=="text")w["content"]["body"]=w["title"];
        if(kind=="table"){w["content"]["columns"]=Json::array();for(const auto& b:w["bindings"])w["content"]["columns"].push_back({{"label",b["field"]}});}}
    validate_scene_document(next);return next;
}
void validate_binding_document(const Json& value){structural(value,"0.1.0/binding",262144);}
void validate_visibility_document(const Json& value){structural(value,"0.1.0/visibility",65536);}
void validate_authored(const Authored& value){
    structural(value.settings,"0.1.0/settings",16384);validate_scene_document(value.scene);
    require(revision(value.settings["revision"])==revision(value.scene["revision"]),"authored.mixed_revision");
}
ValidatedAuthored::ValidatedAuthored(const Authored& value):documents_(std::make_shared<const Authored>(value)){
    validate_authored(*documents_);
}
const Authored& ValidatedAuthored::documents()const{require(static_cast<bool>(documents_),"authored.snapshot");return *documents_;}
Json parse_command(std::string_view bytes){
    require(!bytes.empty()&&bytes.size()<=protocol::large_command_limit,"command.size");
    auto value=protocol::parse(bytes,protocol::ParseProfile::large_command);
    if(!(value.is_object()&&(value.value("schema_version",Json())=="0.5.0"||value.value("schema_version",Json())=="0.6.0"||value.value("schema_version",Json())=="0.7.0"||value.value("schema_version",Json())=="0.8.0"))){
        require(bytes.size()<=protocol::command_limit,"command.size");value=protocol::parse(bytes);
    }
    return value;
}
void validate_command(const Json& value){
    const auto version=value.is_object()&&value.contains("schema_version")?value["schema_version"]:Json();
    structural(value,version=="0.8.0"?"0.8.0/command":version=="0.7.0"?"0.7.0/command":version=="0.6.0"?"0.6.0/command":version=="0.5.0"?"0.5.0/command":version=="0.4.0"?"0.4.0/command":version=="0.3.0"?"0.3.0/command":"0.2.0/command",
        (version=="0.5.0"||version=="0.6.0"||version=="0.7.0"||version=="0.8.0")?protocol::large_command_limit:protocol::command_limit,(version=="0.5.0"||version=="0.6.0"||version=="0.7.0"||version=="0.8.0")?protocol::ParseProfile::large_command:protocol::ParseProfile::ordinary);
    if(version=="0.8.0"&&!value["theme_edit"].is_null()){font_semantics(value["theme_edit"]["font"]);if(!value["theme_edit"]["font_roles"].is_null())for(const auto& font:value["theme_edit"]["font_roles"])font_semantics(font);}
    (void)revision(value["expected_revision"]);(void)revision(value["policy_generation"]);
    std::set<std::string> paths;bool scene=false;
    for(const auto& op:value["operations"]){
        if(op["op"]=="scene.replace"){
            require(!scene,"command.duplicate_scene");scene=true;scene_semantics(op["scene"]);
            if(version=="0.5.0"||version=="0.6.0"||version=="0.7.0"||version=="0.8.0")validate_scene_document(op["scene"]);
            require(op["scene"]["revision"]==value["expected_revision"],"command.scene_revision");
        }else require(paths.insert(op["path"].get<std::string>()).second,"command.duplicate_path");
    }
}
void validate_command_result(const Json& value){
    structural(value,"0.1.0/command-result",4096);
    if(!value["revision"].is_null())(void)revision(value["revision"]);
}
void authorize_authored(const Json& command,const Authority& authority,const Policy& policy,std::uint64_t current){
    require(authority.authenticated&&authority.role_grants.count(authority.role)&&
        (authority.role=="console"||authority.role=="desktop"||authority.role=="saver_settings")&&policy.available,"policy.denied");
    require(revision(command["policy_generation"])==policy.revision,"policy.changed");
    require(revision(command["expected_revision"])==current,"revision.changed");
    require(!policy.denied_capabilities.count(command["intent"]=="commit"?"settings.commit":"settings.preview"),"policy.denied");
    if(command.value("schema_version",Json())=="0.7.0"||command.value("schema_version",Json())=="0.8.0")require(!policy.denied_capabilities.count("configuration.visibility"),"policy.denied");
    if(command.value("schema_version",Json())=="0.8.0"){
        require(!policy.denied_capabilities.count("configuration.theme-overrides")&&!policy.denied_capabilities.count("theme.typography"),"policy.denied");
        if(!command.at("theme_edit").is_null())require(authority.role!="saver_settings"&&!policy.denied_capabilities.count("theme.edit"),"policy.denied");
    }
    if(command.contains("content"))require(!policy.denied_capabilities.count("content.select"),"policy.denied");
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
