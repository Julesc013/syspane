#include "editor_draft.hpp"
#include <algorithm>
#include <cmath>
#include <functional>

namespace syspane::interfaces {
namespace {
namespace c=configuration;
void need(bool value,const char* code){if(!value)throw protocol::Error(code);}
Json& widget(Json& scene,const std::string& id){
    for(auto& w:scene["widgets"])if(w["id"]==id)return w;
    throw protocol::Error("editor.target");
}
bool exists(const Json& scene,const std::string& id){
    return std::any_of(scene["widgets"].begin(),scene["widgets"].end(),[&](const auto& w){return w["id"]==id;});
}
Json& children(Json& scene,const std::optional<std::string>& parent){
    if(!parent)return scene["roots"];
    auto& w=widget(scene,*parent);need(w["kind"]=="group","editor.parent");return w["children"];
}
Json& owner(Json& scene,const std::string& id){
    if(std::find(scene["roots"].begin(),scene["roots"].end(),id)!=scene["roots"].end())return scene["roots"];
    for(auto& w:scene["widgets"])if(w.contains("children")&&std::find(w["children"].begin(),w["children"].end(),id)!=w["children"].end())return w["children"];
    throw protocol::Error("editor.owner");
}
std::set<std::string> subtree(Json& scene,const std::vector<std::string>& ids){
    need(!ids.empty()&&ids.size()<=256,"editor.targets");std::set<std::string> all;
    std::function<void(const std::string&)> visit=[&](const std::string& id){
        need(all.insert(id).second,"editor.overlap");auto& w=widget(scene,id);
        if(w.contains("children"))for(const auto& child:w["children"])visit(child.get<std::string>());
    };
    for(const auto& id:ids)visit(id);
    return all;
}
void erase_ids(Json& list,const std::set<std::string>& ids){
    list.erase(std::remove_if(list.begin(),list.end(),[&](const auto& id){return ids.count(id.template get<std::string>())!=0;}),list.end());
}
void at_index(Json& list,std::size_t index,const std::vector<std::string>& ids){
    need(index<=list.size(),"editor.index");
    for(const auto& id:ids){list.insert(list.begin()+static_cast<Json::difference_type>(index),id);++index;}
}
void apply(Json& scene,const WidgetPropertyEdit& edit){
    const char* key=nullptr;
    switch(edit.property){case WidgetProperty::title:key="title";break;case WidgetProperty::display:key="display";break;
        case WidgetProperty::layout:key="layout";break;case WidgetProperty::priority:key="priority";break;default:throw protocol::Error("editor.property");}
    widget(scene,edit.id)[key]=edit.value;
}
void apply(Json& scene,const WidgetContentEdit& edit){auto& w=widget(scene,edit.id);w["bindings"]=edit.bindings;w["content"]=edit.content;}
void apply(Json& scene,const SceneThemeEdit& edit){scene["theme_id"]=edit.theme?Json(*edit.theme):Json();}
void apply(Json& scene,const InsertWidget& edit){
    need(edit.widget.is_object()&&edit.widget.contains("id")&&edit.widget["id"].is_string(),"editor.widget");
    const auto id=edit.widget["id"].get<std::string>();need(protocol::identifier(id)&&!exists(scene,id),"editor.identity");
    need(!edit.widget.contains("children")||(edit.widget["children"].is_array()&&edit.widget["children"].empty()),"editor.children");
    at_index(children(scene,edit.parent),edit.index,{id});scene["widgets"].push_back(edit.widget);
}
void apply(Json& scene,const RemoveWidgets& edit){
    const auto all=subtree(scene,edit.ids);erase_ids(scene["roots"],all);
    for(auto& w:scene["widgets"])if(w.contains("children"))erase_ids(w["children"],all);
    auto& rows=scene["widgets"];rows.erase(std::remove_if(rows.begin(),rows.end(),[&](const auto& w){return all.count(w["id"].template get<std::string>())!=0;}),rows.end());
}
void apply(Json& scene,const ReparentWidgets& edit){
    const auto all=subtree(scene,edit.ids);need(!edit.parent||!all.count(*edit.parent),"editor.cycle");
    (void)children(scene,edit.parent);
    for(const auto& id:edit.ids)erase_ids(owner(scene,id),{id});
    at_index(children(scene,edit.parent),edit.index,edit.ids);
}
void apply(Json& scene,const DuplicateWidgets& edit){
    const auto all=subtree(scene,edit.ids);need(all.size()==edit.mapping.size(),"editor.mapping");std::set<std::string> fresh;
    for(const auto& row:edit.mapping)need(all.count(row.first)&&protocol::identifier(row.second)&&!exists(scene,row.second)&&fresh.insert(row.second).second,"editor.mapping");
    Json copies=Json::array();
    for(const auto& w:scene["widgets"])if(all.count(w["id"].get<std::string>())){
        auto copy=w;copy["id"]=edit.mapping.at(w["id"].get<std::string>());
        if(copy.contains("children"))for(auto& child:copy["children"])child=edit.mapping.at(child.get<std::string>());
        copies.push_back(std::move(copy));
    }
    for(const auto& id:edit.ids){auto& list=owner(scene,id);const auto index=static_cast<std::size_t>(std::distance(list.begin(),std::find(list.begin(),list.end(),id)))+1;at_index(list,index,{edit.mapping.at(id)});}
    for(auto& w:copies)scene["widgets"].push_back(std::move(w));
}
void apply(Json& scene,const MoveWidgets& edit){
    need(std::isfinite(edit.dx)&&std::isfinite(edit.dy),"editor.number");(void)subtree(scene,edit.ids);
    for(const auto& id:edit.ids){auto& base=widget(scene,id)["layout"]["base"];need(base["kind"]=="fixed","editor.fixed");
        base["x"]=base["x"].get<double>()+edit.dx;base["y"]=base["y"].get<double>()+edit.dy;}
}
void apply(Json& scene,const ResizeWidget& edit){
    need(std::isfinite(edit.width)&&std::isfinite(edit.height),"editor.number");auto& base=widget(scene,edit.id)["layout"]["base"];
    need(base["kind"]=="fixed","editor.fixed");base["width"]=edit.width;base["height"]=edit.height;
}
std::vector<std::string> surviving(const Json& scene,const std::vector<std::string>& ids){
    std::vector<std::string> out;for(const auto& w:scene["widgets"]){const auto id=w["id"].get<std::string>();if(std::find(ids.begin(),ids.end(),id)!=ids.end())out.push_back(id);}return out;
}
}
EditorDraft::EditorDraft(c::Authority a,c::Policy p,c::Authored value,std::string epoch,std::optional<SettingsResources> resources,bool large_commands)
    :transaction_(std::move(a),std::move(p),std::move(value),std::move(epoch),std::move(resources),large_commands){}
const Json* EditorDraft::scene()const{return available()?&transaction_.draft_->scene:nullptr;}
void EditorDraft::select(std::vector<std::string> ids){
    transaction_.editable();need(ids.size()<=256,"editor.targets");std::set<std::string> unique;
    for(const auto& id:ids)need(unique.insert(id).second&&exists(*scene(),id),"editor.selection");
    selected_=surviving(*scene(),ids);
}
std::size_t EditorDraft::history_bytes()const{std::size_t n=0;for(const auto& e:undo_)n+=e.bytes;for(const auto& e:redo_)n+=e.bytes;return n;}
void EditorDraft::clear_history(){undo_.clear();redo_.clear();}
bool EditorDraft::execute(const std::vector<SceneEdit>& edits){
    transaction_.editable();need(!edits.empty()&&edits.size()<=128,"editor.operations");auto candidate=*scene();
    try{for(const auto& edit:edits)std::visit([&](const auto& op){apply(candidate,op);},edit);}
    catch(const Json::exception&){throw protocol::Error("editor.operation");}
    if(candidate==*scene())return false;
    Change change{{*scene(),selected_},{candidate,surviving(candidate,selected_)},0};
    change.bytes=change.before.scene.dump().size()+change.after.scene.dump().size()+Json(change.before.selection).dump().size()+Json(change.after.selection).dump().size();
    auto next=undo_;next.push_back(change);std::size_t bytes=0;for(const auto& entry:next)bytes+=entry.bytes;
    while(next.size()>64||bytes>8*1024*1024){bytes-=next.front().bytes;next.pop_front();}
    auto selection=change.after.selection;transaction_.replace_scene(std::move(candidate));
    selected_.swap(selection);undo_.swap(next);redo_.clear();return true;
}
bool EditorDraft::travel(bool forward){
    transaction_.editable();auto& from=forward?redo_:undo_;auto& to=forward?undo_:redo_;if(from.empty())return false;
    const auto& change=from.back();const auto& target=forward?change.after:change.before;
    auto destination=to;destination.push_back(change);auto selection=target.selection;
    transaction_.replace_scene(target.scene);selected_.swap(selection);to.swap(destination);from.pop_back();return true;
}
bool EditorDraft::undo(){return travel(false);}
bool EditorDraft::redo(){return travel(true);}
void EditorDraft::discard(){transaction_.revert();clear_history();selected_=surviving(*scene(),selected_);}
void EditorDraft::close(){transaction_.close();clear_history();selected_.clear();}
void EditorDraft::policy(c::Policy policy){transaction_.policy(std::move(policy));if(!available()){clear_history();selected_.clear();}}
void EditorDraft::reload(c::Authored v,std::string epoch,std::optional<SettingsResources> resources){transaction_.reload(std::move(v),std::move(epoch),std::move(resources));clear_history();selected_.clear();}
void EditorDraft::settled(bool changed){if(changed&&available()&&last_result()["outcome"]=="accepted")clear_history();}
bool EditorDraft::complete(std::uint64_t ticket,const Json& result){const bool changed=transaction_.complete(ticket,result);settled(changed);return changed;}
bool EditorDraft::reconciled(std::uint64_t ticket,const std::string& query,const std::string& epoch,const Json& result){const bool changed=transaction_.reconciled(ticket,query,epoch,result);settled(changed);return changed;}
}
