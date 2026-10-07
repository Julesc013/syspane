#include "content.hpp"
#include "digest.hpp"
#include <algorithm>
#include <functional>

namespace syspane::configuration {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
std::string lower(std::string text){for(auto& c:text)if(c>='A'&&c<='Z')c=static_cast<char>(c-'A'+'a');return text;}
void paths(const Json& assets){
    std::set<std::string> names;std::map<std::string,std::string> spellings;
    for(const auto& a:assets){const auto path=a["path"].get<std::string>();validate_content_path(path);
        need(names.insert(lower(path)).second,"content.path_collision");
        for(std::size_t begin=0;;){const auto end=path.find('/',begin);const auto prefix=path.substr(0,end);
            const auto inserted=spellings.emplace(lower(prefix),prefix);need(inserted.second||inserted.first->second==prefix,"content.path_collision");
            if(end==std::string::npos)break;
            begin=end+1;
        }
    }
    for(const auto& name:names)for(auto slash=name.find('/');slash!=std::string::npos;slash=name.find('/',slash+1))
        need(!names.count(name.substr(0,slash)),"content.path_collision");
}
void pin_valid(const Json& pin){
    need(protocol::members(pin,{"id","version","sha256"}),"content.pin");
    for(const char* k:{"id","version","sha256"})need(pin[k].is_string(),"content.pin");
    need(protocol::identifier(pin["id"].get<std::string>())&&pin["version"].get_ref<const std::string&>().size()<=64,"content.pin");
    const auto& hash=pin["sha256"].get_ref<const std::string&>();need(hash.size()==64&&hash.find_first_not_of("0123456789abcdef")==std::string::npos,"content.pin");
}
Json command(const Authored& base,const std::string& request,std::uint64_t generation,const Json& ops){
    return {{"schema_version","0.2.0"},{"request_id",request},{"expected_revision",base.settings["revision"]},
        {"policy_generation",std::to_string(generation)},{"intent","preview"},{"operations",ops}};
}
}
void validate_content_path(const std::string& path){
    need(!path.empty()&&path.size()<=512&&lower(path.substr(0,path.find('/')))!="manifest.json","content.path");
    need(path.find_first_not_of("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._- /")==std::string::npos,"content.path");
    std::size_t begin=0;unsigned count=0;
    for(;;){const auto end=path.find('/',begin);const auto part=path.substr(begin,end==std::string::npos?end:end-begin);
        need(!part.empty()&&part!="."&&part!=".."&&part.back()!='.'&&part.back()!=' '&&++count<=16,"content.path");
        const auto name=lower(part.substr(0,part.find('.')));
        need(name!="con"&&name!="prn"&&name!="aux"&&name!="nul"&&
            !(name.size()==4&&(name.substr(0,3)=="com"||name.substr(0,3)=="lpt")&&name[3]>='1'&&name[3]<='9'),"content.path");
        if(end==std::string::npos)break;
        begin=end+1;
    }
}
Json parse_content_json(std::string_view bytes,std::size_t maximum){
    need(bytes.size()<=maximum,"content.size");
    while(!bytes.empty()&&(bytes.back()==' '||bytes.back()=='\t'||bytes.back()=='\r'||bytes.back()=='\n'))bytes.remove_suffix(1);
    return protocol::parse(bytes);
}
Json validate_content_manifest(std::string_view bytes){
    auto manifest=parse_content_json(bytes,65536);validate_content_document(manifest,"content-package");paths(manifest["assets"]);
    need(manifest["kind"]!="widget","content.kind");std::set<std::string> ids;std::uint64_t total=0;
    for(const auto& dep:manifest["dependencies"])need(ids.insert(dep["id"].get<std::string>()).second,"content.duplicate_dependency");
    for(const auto& asset:manifest["assets"])total+=asset["bytes"].get<std::uint64_t>();
    need(total==manifest["total_unpacked_bytes"].get<std::uint64_t>()&&total<=67108864,"content.total");
    const auto entry=manifest["kind"].get<std::string>()+".json";bool found=false;
    for(const auto& asset:manifest["assets"])if(asset["path"]==entry){need(asset["media_type"]=="application/json","content.entry");found=true;}
    need(found,"content.entry");return manifest;
}
ContentCatalog::ContentCatalog(std::vector<ContentPackage> packages){
    need(!packages.empty()&&packages.size()<=64,"content.capacity");std::size_t count=0,total=0;
    std::map<std::pair<std::string,std::string>,std::size_t> identities;
    for(auto& bytes:packages){
        auto manifest=validate_content_manifest(bytes.manifest);
        need(identities.emplace(std::make_pair(manifest["package_id"].get<std::string>(),manifest["version"].get<std::string>()),entries_.size()).second,"content.duplicate_package");
        need(bytes.assets.size()==manifest["assets"].size(),"content.assets");
        for(const auto& asset:manifest["assets"]){
            const auto found=bytes.assets.find(asset["path"].get<std::string>());need(found!=bytes.assets.end(),"content.assets");const auto& raw=found->second;
            need(raw.size()==asset["bytes"].get<std::size_t>()&&content_sha256(raw)==asset["sha256"],"content.digest");
            total+=raw.size();need(++count<=1024&&total<=67108864,"content.capacity");
            if(asset["media_type"]=="application/json")(void)parse_content_json(raw);
        }
        const auto kind=manifest["kind"].get<std::string>();const auto& raw=bytes.assets.at(kind+".json");auto document=parse_content_json(raw);
        if(kind=="scene")validate_scene_document(document);else validate_content_document(document,kind);
        if(kind=="preset"){
            need(document["version"]==manifest["version"],"content.version");std::set<std::string> keys;
            for(const auto& setting:document["settings"]){need(keys.insert(setting["path"].get<std::string>()).second,"content.duplicate_setting");
                Json q={{"schema_version","0.2.0"},{"request_id","validate"},{"expected_revision","0"},{"policy_generation","0"},{"intent","preview"},
                    {"operations",Json::array({{{"op","settings.set"},{"path",setting["path"]},{"value",setting["value"]}}})}};validate_command(q);}
        }
        Json pin={{"id",document[kind+"_id"]},{"version",manifest["version"]},{"sha256",sha256(raw)}};
        entries_.push_back({std::make_shared<const ContentPackage>(std::move(bytes)),std::move(manifest),std::move(document),std::move(pin),{}});
    }
    std::vector<unsigned> heights(entries_.size(),0);std::set<std::size_t> visiting;
    std::function<unsigned(std::size_t)> visit=[&](std::size_t i){
        if(heights[i])return heights[i];
        need(visiting.insert(i).second,"content.cycle");auto& e=entries_[i];e.closure.insert(i);unsigned height=1;
        for(const auto& dep:e.manifest["dependencies"]){
            const auto found=identities.find({dep["id"].get<std::string>(),dep["version"].get<std::string>()});need(found!=identities.end(),"content.dependency");
            const auto j=found->second;need(sha256(entries_[j].bytes->manifest)==dep["sha256"],"content.dependency");
            height=std::max(height,1+visit(j));need(height<=8,"content.depth");e.closure.insert(entries_[j].closure.begin(),entries_[j].closure.end());
        }
        visiting.erase(i);heights[i]=height;return height;
    };
    for(std::size_t i=0;i<entries_.size();++i)(void)visit(i);
}
std::size_t ContentCatalog::lookup(const Json& pin,const char* kind,const std::set<std::size_t>& scope)const{
    pin_valid(pin);std::optional<std::size_t> result;
    for(auto i:scope)if(entries_[i].manifest["kind"]==kind&&entries_[i].pin==pin){need(!result,"content.ambiguous");result=i;}
    need(result.has_value(),"content.reference");return *result;
}
ContentCatalog::Selection ContentCatalog::select(const Json& package_pin,const Json& selected)const{
    pin_valid(selected);pin_valid(package_pin);
    std::set<std::size_t> selected_package;
    for(std::size_t i=0;i<entries_.size();++i){const auto& e=entries_[i];
        if(e.manifest["package_id"]==package_pin["id"]&&e.manifest["version"]==package_pin["version"]&&sha256(e.bytes->manifest)==package_pin["sha256"])selected_package.insert(i);}
    const auto leaf=lookup(selected,"preset",selected_package);const auto& scope=entries_[leaf].closure;
    std::set<std::pair<std::string,std::string>> documents;
    for(auto i:scope)need(documents.emplace(entries_[i].pin["id"].get<std::string>(),entries_[i].pin["version"].get<std::string>()).second,"content.ambiguous");
    std::vector<std::size_t> chain;std::set<std::size_t> visited;auto cursor=leaf;
    for(;;){need(chain.size()<8&&visited.insert(cursor).second,"content.parent_depth");chain.push_back(cursor);const auto& e=entries_[cursor];
        (void)lookup(e.document["scene"],"scene",e.closure);if(!e.document["theme"].is_null())(void)lookup(e.document["theme"],"theme",e.closure);
        if(e.document["parent"].is_null())break;
        cursor=lookup(e.document["parent"],"preset",e.closure);
    }
    std::reverse(chain.begin(),chain.end());return {leaf,std::move(chain)};
}
ResourceSnapshot ContentCatalog::resources(const Json& selection,const Authored& candidate)const{
    need(protocol::members(selection,{"package","preset"}),"content.selection");validate_authored(candidate);
    const auto selected=select(selection["package"],selection["preset"]);const auto& scope=entries_[selected.leaf].closure;
    auto result=std::shared_ptr<ResourceSet>(new ResourceSet);result->selection_=selection;
    for(auto i:scope){const auto& e=entries_[i];result->packages_.push_back(e.bytes);
        for(const auto& cap:e.manifest["required_capabilities"])result->required_.insert(cap.get<std::string>());
        if(e.manifest["kind"]=="preset")for(const auto& cap:e.document["required_capabilities"])result->required_.insert(cap.get<std::string>());}
    const auto id=candidate.scene["theme_id"].is_null()?candidate.settings["display"]["theme_id"]:candidate.scene["theme_id"];
    const auto& pin=entries_[selected.leaf].document["theme"];std::optional<std::size_t> theme;
    if(!pin.is_null()&&pin["id"]==id)theme=lookup(pin,"theme",scope);
    else for(auto i:scope)if(entries_[i].manifest["kind"]=="theme"&&entries_[i].pin["id"]==id){need(!theme,"content.ambiguous");theme=i;}
    need(theme.has_value(),"content.theme");result->theme_pin_=entries_[*theme].pin;result->theme_=entries_[*theme].document;
    if(candidate.scene["schema_version"]!="0.2.0")result->required_.insert("scene.content");
    if((candidate.scene["schema_version"]=="0.4.0"||candidate.scene["schema_version"]=="0.5.0"))result->required_.insert("scene.edit-locks");
    if(candidate.scene["schema_version"]=="0.5.0")result->required_.insert("scene.visibility");
    validate_resource_binding(*result,candidate);return result;
}
void validate_resource_binding(const ResourceSet& resources,const Authored& candidate){
    validate_authored(candidate);const auto id=candidate.scene["theme_id"].is_null()?candidate.settings["display"]["theme_id"]:candidate.scene["theme_id"];
    need(id==resources.theme()["theme_id"],"content.theme");
    if(candidate.scene["schema_version"]=="0.2.0")return;
    need(resources.required().count("scene.content")!=0,"resource.contract");
    if((candidate.scene["schema_version"]=="0.4.0"||candidate.scene["schema_version"]=="0.5.0"))need(resources.required().count("scene.edit-locks")!=0,"resource.contract");
    if(candidate.scene["schema_version"]=="0.5.0")need(resources.required().count("scene.visibility")!=0,"resource.contract");
    // ResourceSet can only be made by ContentCatalog, which verified every byte.
    // Index immutable manifests once; repeated image references must not rehash
    // up to 64 MiB of identical media for each widget or presentation validation.
    std::map<std::string,Json> manifests;
    for(const auto& bytes:resources.packages()){
        auto m=parse_content_json(bytes->manifest,65536);Json pin={{"id",m["package_id"]},{"version",m["version"]},{"sha256",sha256(bytes->manifest)}};
        manifests.emplace(pin.dump(),std::move(m));}
    for(const auto& w:candidate.scene["widgets"])if(w["kind"]=="image"){
        const auto& ref=w["content"]["asset"];bool found=false;
        const auto manifest=manifests.find(ref["package"].dump());need(manifest!=manifests.end(),"content.asset");
        for(const auto& asset:manifest->second["assets"])if(asset["path"]==ref["path"]){const auto& media=asset["media_type"];
            need(!found&&(media=="image/png"||media=="image/jpeg"||media=="image/svg+xml")&&asset["sha256"]==ref["sha256"],"content.asset");found=true;}
        need(found,"content.asset");
    }
}
void authorize_resources(const ResourceSet& resources,const Policy& policy,const std::set<std::string>& capabilities){
    need(policy.available,"policy.denied");
    for(const auto& cap:resources.required())need(capabilities.count(cap)&&!policy.denied_capabilities.count(cap),"policy.denied");
}
PresetPlan ContentCatalog::preview(const Json& package_pin,const Json& selected,const Authored& baseline,const std::string& request,
    const Authority& authority,const Policy& policy,const std::set<std::string>& capabilities)const{
    validate_authored(baseline);const auto selection=select(package_pin,selected);const auto leaf=selection.leaf;const auto& scope=entries_[leaf].closure;
    PresetPlan result;result.package_pins=Json::array();result.preset_pins=Json::array();result.setting_origins=Json::object();
    std::set<std::string> missing;std::map<std::string,Json> sorted;
    auto requirements=[&](const Json& document){
        auto has=[&](const std::string& cap){return capabilities.count(cap)&&!policy.denied_capabilities.count(cap);};
        for(const auto& cap:document["required_capabilities"])need(has(cap.get<std::string>()),"content.capability");
        for(const auto& cap:document["optional_capabilities"])if(!has(cap.get<std::string>()))missing.insert(cap.get<std::string>());
    };
    for(auto i:scope){const auto& e=entries_[i];requirements(e.manifest);if(e.manifest["kind"]=="preset")requirements(e.document);
        Json pin={{"id",e.manifest["package_id"]},{"version",e.manifest["version"]},{"sha256",sha256(e.bytes->manifest)}};
        sorted.emplace(pin.dump(),pin);result.packages.push_back(e.bytes);}
    for(const auto& row:sorted)result.package_pins.push_back(row.second);
    result.missing_optional=Json::array();for(const auto& cap:missing)result.missing_optional.push_back(cap);
    std::map<std::string,Json> values;
    for(auto i:selection.chain){const auto& e=entries_[i];result.preset_pins.push_back(e.pin);
        for(const auto& setting:e.document["settings"]){const auto key=setting["path"].get<std::string>();values[key]=setting["value"];result.setting_origins[key]=e.pin;}}
    const auto& leafdoc=entries_[leaf].document;auto scene=entries_[lookup(leafdoc["scene"],"scene",scope)].document;
    scene["revision"]=baseline.settings["revision"];
    if(!leafdoc["theme"].is_null())scene["theme_id"]=leafdoc["theme"]["id"];
    Json ops=Json::array();for(const auto& row:values)ops.push_back({{"op","settings.set"},{"path",row.first},{"value",row.second}});
    ops.push_back({{"op","scene.replace"},{"scene",scene}});result.command=command(baseline,request,policy.revision,ops);
    if(capabilities.count("configuration.large-commands")||scene["schema_version"]!="0.2.0"){result.command["schema_version"]=capabilities.count("configuration.large-commands")?"0.5.0":"0.4.0";result.command["content"]={{"package",package_pin},{"preset",selected}};}
    if(scene["schema_version"]=="0.5.0"){need(capabilities.count("configuration.visibility")&&capabilities.count("configuration.edit-locks")&&capabilities.count("configuration.large-commands"),"resource.capability");result.command["schema_version"]="0.7.0";}
    if(scene["schema_version"]=="0.4.0"){need(capabilities.count("configuration.edit-locks")&&capabilities.count("configuration.large-commands"),"resource.capability");result.command["schema_version"]="0.6.0";}
    result.candidate=prepare_authored(baseline,result.command,authority,policy);
    const auto theme_id=scene["theme_id"].is_null()?result.candidate.settings["display"]["theme_id"]:scene["theme_id"];
    std::optional<std::size_t> theme;
    if(!leafdoc["theme"].is_null())theme=lookup(leafdoc["theme"],"theme",scope);
    else for(auto i:scope)if(entries_[i].manifest["kind"]=="theme"&&entries_[i].pin["id"]==theme_id){need(!theme,"content.ambiguous");theme=i;}
    need(theme.has_value(),"content.theme");result.theme=entries_[*theme].document;
    if(result.command.contains("content"))authorize_resources(*resources(result.command["content"],result.candidate),policy,capabilities);
    return result;
}
}
