#include "editor_fragment.hpp"
#include <algorithm>
#include <functional>
namespace syspane::interfaces::detail {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
bool supported(const Json& v){return v=="0.3.0"||v=="0.4.0"||v=="0.5.0";}
Json read(std::string_view bytes){
    const auto f=configuration::parse_content_json(bytes,262144);
    need(protocol::members(f,{"format","schema_version","scene_version","roots","widgets"})&&
        f["format"]=="syspane.scene-fragment"&&f["schema_version"]=="0.1.0"&&supported(f["scene_version"]),"clipboard.format");
    Json scene={{"schema_version",f["scene_version"]},{"scene_id","scene:fragment"},{"revision","0"},{"theme_id",nullptr},{"roots",f["roots"]},{"widgets",f["widgets"]}};
    configuration::validate_scene_document(scene);need(!scene["widgets"].empty()&&!scene["roots"].empty(),"clipboard.empty");return scene;
}
}
std::string selection_fragment(const Json& scene,const std::vector<std::string>& selected){
    need(supported(scene.at("schema_version")),"clipboard.version");
    need(!selected.empty()&&selected.size()<=256,"clipboard.empty");
    std::map<std::string,const Json*> rows;std::map<std::string,std::string> parents;
    for(const auto& w:scene.at("widgets")){
        const auto id=w.at("id").get<std::string>();rows.emplace(id,&w);
        if(w.contains("children"))for(const auto& c:w.at("children"))parents.emplace(c.get<std::string>(),id);
    }
    const std::set<std::string> chosen(selected.begin(),selected.end());std::vector<std::string> roots;std::set<std::string> included;
    std::function<void(const std::string&)> visit=[&](const std::string& id){
        if(!included.insert(id).second)return;
        const auto& w=*rows.at(id);if(w.contains("children"))for(const auto& c:w.at("children"))visit(c.get<std::string>());
    };
    for(const auto& w:scene.at("widgets")){
        const auto id=w.at("id").get<std::string>();if(!chosen.count(id))continue;
        bool nested=false;auto parent=parents.find(id);
        while(parent!=parents.end()){if(chosen.count(parent->second)){nested=true;break;}parent=parents.find(parent->second);}
        if(!nested){roots.push_back(id);visit(id);}
    }
    Json widgets=Json::array();for(const auto& w:scene.at("widgets"))if(included.count(w.at("id").get<std::string>()))widgets.push_back(w);
    const Json f={{"format","syspane.scene-fragment"},{"schema_version","0.1.0"},{"scene_version",scene.at("schema_version")},{"roots",roots},{"widgets",std::move(widgets)}};
    auto bytes=f.dump();(void)read(bytes);return bytes;
}
std::vector<std::string> fragment_ids(std::string_view bytes){
    const auto scene=read(bytes);std::vector<std::string> ids;
    for(const auto& w:scene.at("widgets"))ids.push_back(w.at("id").get<std::string>());
    return ids;
}
std::vector<std::string> paste_fragment(Json& scene,const PasteWidgets& edit){
    const auto fragment=read(edit.bytes);need(supported(scene.at("schema_version")),"clipboard.version");
    need(scene.at("widgets").size()+fragment.at("widgets").size()<=256,"clipboard.capacity");
    need(edit.mapping.size()==fragment.at("widgets").size(),"editor.mapping");std::set<std::string> ids;
    for(const auto& w:scene.at("widgets"))ids.insert(w.at("id").get<std::string>());
    for(const auto& w:fragment.at("widgets")){
        const auto mapped=edit.mapping.find(w.at("id").get<std::string>());
        need(mapped!=edit.mapping.end()&&protocol::identifier(mapped->second)&&ids.insert(mapped->second).second,"editor.mapping");
    }
    Json* destination=&scene["roots"];
    if(edit.parent){
        destination=nullptr;for(auto& w:scene["widgets"])if(w.at("id")==*edit.parent){need(w.at("kind")=="group","editor.parent");destination=&w["children"];break;}
        need(destination!=nullptr,"editor.parent");
    }
    need(edit.index<=destination->size(),"editor.index");auto index=edit.index;
    for(const auto& id:fragment.at("roots")){destination->insert(destination->begin()+static_cast<Json::difference_type>(index),edit.mapping.at(id.get<std::string>()));++index;}
    // The parent pointer is no longer used after appending rows can reallocate.
    std::vector<std::string> selection;const auto& roots=fragment.at("roots");
    for(const auto& w:fragment.at("widgets")){
        auto copy=w;const auto id=w.at("id").get<std::string>();copy["id"]=edit.mapping.at(id);
        if(copy.contains("children"))for(auto& child:copy["children"])child=edit.mapping.at(child.get<std::string>());
        if(std::find(roots.begin(),roots.end(),id)!=roots.end())selection.push_back(edit.mapping.at(id));
        scene["widgets"].push_back(std::move(copy));
    }
    if(fragment.at("schema_version").get<std::string>()>scene.at("schema_version").get<std::string>())scene["schema_version"]=fragment.at("schema_version");
    return selection;
}
}
