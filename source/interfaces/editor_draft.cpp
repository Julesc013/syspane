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
Json& variant(Json& scene,const std::string& id,int index){
    auto& layout=widget(scene,id).at("layout");need(index>=-1&&index<8,"editor.layout_variant");
    if(index==-1)return layout.at("base");
    need(layout.contains("breakpoints")&&static_cast<std::size_t>(index)<layout.at("breakpoints").size(),"editor.layout_variant");
    return layout.at("breakpoints").at(static_cast<std::size_t>(index)).at("layout");
}
int variant_index(const std::vector<std::string>& ids,const std::vector<int>& indices,const std::string& id){
    need(indices.empty()||indices.size()==ids.size(),"editor.layout_variants");
    return indices.empty()?-1:indices.at(static_cast<std::size_t>(std::distance(ids.begin(),std::find(ids.begin(),ids.end(),id))));
}
void apply(Json& scene,const RootDisplayEdit& edit){
    need(std::find(scene.at("roots").begin(),scene.at("roots").end(),edit.root)!=scene.at("roots").end(),"editor.layout_root");
    for(const auto& id:subtree(scene,{edit.root}))widget(scene,id)["display"]=edit.display;
}
void apply(Json& scene,const MoveWidgets& edit){
    need(std::isfinite(edit.dx)&&std::isfinite(edit.dy),"editor.number");(void)subtree(scene,edit.ids);
    for(const auto& id:edit.ids){auto& base=variant(scene,id,variant_index(edit.ids,edit.variants,id));need(base["kind"]=="fixed","editor.fixed");
        base["x"]=base["x"].get<double>()+edit.dx;base["y"]=base["y"].get<double>()+edit.dy;}
}
void apply(Json& scene,const ResizeWidget& edit){
    need(std::isfinite(edit.width)&&std::isfinite(edit.height),"editor.number");auto& base=variant(scene,edit.id,edit.variant);
    need(base["kind"]=="fixed","editor.fixed");base["width"]=edit.width;base["height"]=edit.height;
}
struct Box {std::string id;std::int64_t x,y,width,height;};
std::int64_t unit(const Json& value,double minimum,double maximum,bool extent){
    need(value.is_number(),"editor.number");const auto n=value.get<double>();
    need(std::isfinite(n)&&n>=minimum&&n<=maximum,"editor.number");
    return static_cast<std::int64_t>(extent?std::ceil(n*64):std::round(n*64));
}
Box fixed_box(const Json& base,const std::string& id){
    need(base.at("kind")=="fixed","editor.fixed");
    return {id,unit(base.at("x"),-100000,100000,false),unit(base.at("y"),-100000,100000,false),
        unit(base.at("width"),32,32768,true),unit(base.at("height"),16,32768,true)};
}
std::vector<Json*> variants(Json& w){
    auto& layout=w.at("layout");std::vector<Json*> result{&layout.at("base")};
    if(layout.contains("breakpoints")){need(layout["breakpoints"].is_array(),"editor.layout");for(auto& point:layout["breakpoints"])result.push_back(&point.at("layout"));}
    return result;
}
void translate_variants(Json& w,std::int64_t dx,std::int64_t dy){
    for(auto* variant:variants(w)){const auto box=fixed_box(*variant,w.at("id"));(*variant)["x"]=static_cast<double>(box.x+dx)/64;(*variant)["y"]=static_cast<double>(box.y+dy)/64;}
}
std::vector<Box> arrange_boxes(Json& scene,const std::vector<std::string>& ids,std::size_t minimum,const std::vector<int>& indices={}){
    need(ids.size()>=minimum,"editor.targets");(void)subtree(scene,ids);
    auto& list=owner(scene,ids.front());const auto display=widget(scene,ids.front()).at("display");
    for(const auto& id:ids)need(&owner(scene,id)==&list&&widget(scene,id).at("display")==display,"editor.arrange_scope");
    std::vector<Box> boxes;
    for(const auto& item:list){const auto id=item.get<std::string>();if(std::find(ids.begin(),ids.end(),id)==ids.end())continue;
        boxes.push_back(fixed_box(variant(scene,id,variant_index(ids,indices,id)),id));
    }
    return boxes;
}
void apply(Json& scene,const AlignWidgets& edit){
    bool vertical=false;int anchor=0;
    switch(edit.alignment){
        case Alignment::left:break;case Alignment::hcenter:anchor=1;break;case Alignment::right:anchor=2;break;
        case Alignment::top:vertical=true;break;case Alignment::vcenter:vertical=true;anchor=1;break;case Alignment::bottom:vertical=true;anchor=2;break;
        default:throw protocol::Error("editor.alignment");
    }
    const auto boxes=arrange_boxes(scene,edit.ids,2,edit.variants);auto left=vertical?boxes[0].y:boxes[0].x;
    auto right=left+(vertical?boxes[0].height:boxes[0].width);
    for(const auto& b:boxes){const auto pos=vertical?b.y:b.x;left=std::min(left,pos);right=std::max(right,pos+(vertical?b.height:b.width));}
    for(const auto& b:boxes){const auto extent=vertical?b.height:b.width;auto pos=left;
        if(anchor==2)pos=right-extent;
        else if(anchor==1){const auto twice=left+right-extent;pos=twice/2+((twice%2)?(twice<0?-1:1):0);}
        variant(scene,b.id,variant_index(edit.ids,edit.variants,b.id))[vertical?"y":"x"]=static_cast<double>(pos)/64;
    }
}
void apply(Json& scene,const DistributeWidgets& edit){
    need(edit.spacing==Spacing::horizontal||edit.spacing==Spacing::vertical,"editor.spacing");const bool vertical=edit.spacing==Spacing::vertical;
    auto boxes=arrange_boxes(scene,edit.ids,3,edit.variants);
    auto origin=[&](const Box& b){return vertical?b.y:b.x;};auto extent=[&](const Box& b){return vertical?b.height:b.width;};
    std::stable_sort(boxes.begin(),boxes.end(),[&](const Box& a,const Box& b){return origin(a)<origin(b);});
    auto gaps=origin(boxes.back())-origin(boxes.front());
    for(std::size_t i=0;i+1<boxes.size();++i)gaps-=extent(boxes[i]);
    need(gaps>=0,"editor.spacing_overlap");const auto count=static_cast<std::int64_t>(boxes.size()-1),q=gaps/count,r=gaps%count;
    auto pos=origin(boxes.front());
    for(std::size_t i=1;i+1<boxes.size();++i){pos+=extent(boxes[i-1])+q+(static_cast<std::int64_t>(i)<=r?1:0);
        variant(scene,boxes[i].id,variant_index(edit.ids,edit.variants,boxes[i].id))[vertical?"y":"x"]=static_cast<double>(pos)/64;}
}
void apply(Json& scene,const GroupWidgets& edit){
    need(protocol::identifier(edit.id)&&!exists(scene,edit.id),"editor.identity");const auto boxes=arrange_boxes(scene,edit.ids,2);
    auto left=boxes[0].x,top=boxes[0].y,right=left+boxes[0].width,bottom=top+boxes[0].height;
    std::vector<std::string> members;
    for(const auto& root:boxes){members.push_back(root.id);for(const auto* layout:variants(widget(scene,root.id))){const auto b=fixed_box(*layout,root.id);
        left=std::min(left,b.x);top=std::min(top,b.y);right=std::max(right,b.x+b.width);bottom=std::max(bottom,b.y+b.height);}}
    Json group={{"id",edit.id},{"kind","group"},{"title",edit.title},{"display",widget(scene,members[0]).at("display")},
        {"layout",{{"base",{{"kind","fixed"},{"x",static_cast<double>(left)/64},{"y",static_cast<double>(top)/64},
            {"width",static_cast<double>(right-left)/64},{"height",static_cast<double>(bottom-top)/64}}}}},
        {"bindings",Json::array()},{"priority","normal"},{"children",members}};
    if(scene.at("schema_version")=="0.3.0")group["content"]=Json::object();
    for(const auto& id:members)translate_variants(widget(scene,id),-left,-top);
    auto& list=owner(scene,members[0]);const auto index=static_cast<std::size_t>(std::distance(list.begin(),std::find(list.begin(),list.end(),members[0])));
    erase_ids(list,std::set<std::string>(members.begin(),members.end()));at_index(list,index,{edit.id});scene["widgets"].push_back(std::move(group));
}
void apply(Json& scene,const UngroupWidget& edit){
    const auto group=widget(scene,edit.id);need(group.at("kind")=="group","editor.group");
    need(!group.at("layout").contains("breakpoints")||group["layout"]["breakpoints"].empty(),"editor.group_layout");
    const auto box=fixed_box(group.at("layout").at("base"),edit.id);const auto members=group.at("children").get<std::vector<std::string>>();
    for(const auto& id:members){auto& w=widget(scene,id);need(w.at("display")==group.at("display"),"editor.arrange_scope");
        for(const auto* layout:variants(w)){const auto b=fixed_box(*layout,id);
            need(b.x>=0&&b.y>=0&&b.x+b.width<=box.width&&b.y+b.height<=box.height,"editor.group_clip");}
        translate_variants(w,box.x,box.y);
    }
    auto& list=owner(scene,edit.id);const auto index=static_cast<std::size_t>(std::distance(list.begin(),std::find(list.begin(),list.end(),edit.id)));
    erase_ids(list,{edit.id});at_index(list,index,members);auto& rows=scene["widgets"];
    rows.erase(std::remove_if(rows.begin(),rows.end(),[&](const auto& w){return w["id"]==edit.id;}),rows.end());
}
template<class T> void edit_selection(Json& scene,std::vector<std::string>&,const T& edit){apply(scene,edit);}
void edit_selection(Json& scene,std::vector<std::string>& selection,const GroupWidgets& edit){apply(scene,edit);selection={edit.id};}
void edit_selection(Json& scene,std::vector<std::string>& selection,const InsertWidget& edit){apply(scene,edit);if(edit.select_inserted)selection={edit.widget.at("id").get<std::string>()};}
void edit_selection(Json& scene,std::vector<std::string>& selection,const UngroupWidget& edit){
    const auto members=widget(scene,edit.id).at("children").get<std::vector<std::string>>();apply(scene,edit);selection=members;
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
    transaction_.editable();need(!edits.empty()&&edits.size()<=128,"editor.operations");auto candidate=*scene();auto selected=selected_;
    try{for(const auto& edit:edits)std::visit([&](const auto& op){edit_selection(candidate,selected,op);},edit);}
    catch(const Json::exception&){throw protocol::Error("editor.operation");}
    if(candidate==*scene())return false;
    Change change{{*scene(),selected_},{candidate,surviving(candidate,selected)},0};
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
