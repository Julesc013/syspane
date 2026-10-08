#include "editor_form.hpp"
#include "editor_snap.hpp"
#include "editor_content_form.hpp"
#include "editor_binding_form.hpp"
#include "editor_visibility_form.hpp"
#include "editor_create_form.hpp"
#include "editor_layout_form.hpp"
#include "private_text.hpp"
#include <gtk/gtk.h>
#include <algorithm>
#include <cmath>
#include <locale>
#include <iomanip>
#include <regex>
#include <set>
#include <sstream>
#include <thread>

namespace syspane::interfaces {
namespace {
namespace c=configuration;namespace s=scene;namespace v=rendering;
void need(bool b,const char* code){if(!b)throw protocol::Error(code);}
std::string text(GtkWidget* w){auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(w));GtkTextIter a,z;gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string value=raw;g_free(raw);return value;}
void text(GtkWidget* w,const std::string& value){if(text(w)!=value)gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),value.c_str(),static_cast<gint>(value.size()));}
void accessible(GtkWidget* w,const std::string& name,const std::string& id){atk_object_set_name(gtk_widget_get_accessible(w),name.c_str());atk_object_set_description(gtk_widget_get_accessible(w),id.c_str());}
double number(const std::string& value){
    static const std::regex grammar("^-?(0|[1-9][0-9]*)([.][0-9]+)?$");need(std::regex_match(value,grammar),"editor.number");
    std::istringstream input(value);input.imbue(std::locale::classic());double n=0;input>>n;need(input&&input.eof()&&std::isfinite(n),"editor.number");return n;
}
const Json& authored_widget(const Json& scene,const std::string& id){for(const auto& w:scene["widgets"])if(w["id"]==id)return w;throw protocol::Error("editor.target");}
bool contains(const s::Rect& r,double x,double y){return x>=r.x&&y>=r.y&&x<r.x+r.width&&y<r.y+r.height;}
void immediate_style(GtkWidget* widget,gpointer provider){
    gtk_style_context_add_provider(gtk_widget_get_style_context(widget),GTK_STYLE_PROVIDER(provider),GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    if(GTK_IS_CONTAINER(widget))gtk_container_forall(GTK_CONTAINER(widget),immediate_style,provider);
}
}
struct EditorForm::Impl {
    EditorDraft draft;c::Authority authority;c::Policy current;Json settings;std::optional<SettingsResources> resources;s::Topology topology;std::string display,worker;
    std::vector<v::SurfaceProvider> providers;std::unique_ptr<v::SceneSurface> surface;std::map<std::string,model::Tick> ticks;
    Actions actions;std::thread::id thread=std::this_thread::get_id();bool closed=false,updating=false,dispatching=false,fields_dirty=false,drawing=false;std::string error;
    GtkWidget *root=nullptr,*canvas=nullptr,*tree=nullptr,*status=nullptr,*guidance=nullptr;GtkListStore* model=nullptr;std::vector<GtkWidget*> owned;
    std::map<std::string,GtkWidget*> buttons,fields;std::vector<s::Node> nodes;std::set<std::string> hidden,diagnostics;bool large_frames=false;
    std::unique_ptr<EditorVisibilityForm> visibility;std::unique_ptr<EditorContentForm> content;std::unique_ptr<EditorBindingForm> binding;std::unique_ptr<EditorCreateForm> creation;std::unique_ptr<EditorLayoutForm> layout_form;int field_variant=-2;
    bool snap_grid=false,snap_guides=false,show_grid=false;s::Unit grid_spacing=8*s::dip;
    struct Gesture {double x,y,dx=0,dy=0,pixel_per_unit=1.0/64;bool resize=false;std::vector<s::Node> nodes;std::optional<SnapInput> input;SnapResult result{0,0,{},{}};};std::optional<Gesture> gesture;
    guint timer=0;
    Impl(c::Authority a,c::Policy p,c::Authored value,std::string epoch,SettingsResources r,s::Topology t,std::string d,std::vector<v::SurfaceProvider> ps,std::string w,Actions callbacks,bool large_commands)
      :draft(a,p,value,std::move(epoch),r,large_commands),authority(std::move(a)),current(std::move(p)),settings(std::move(value.settings)),resources(std::move(r)),topology(std::move(t)),display(std::move(d)),worker(std::move(w)),providers(std::move(ps)),actions(std::move(callbacks)){large_frames=large_commands;}
    void owner()const{if(thread!=std::this_thread::get_id()||dispatching)throw std::logic_error("editor.owner");}
    std::uint64_t now()const{return static_cast<std::uint64_t>(g_get_monotonic_time()/1000);}
    GtkWidget* own(GtkWidget* w){g_object_ref_sink(w);owned.push_back(w);return w;}
    GtkWidget* label(const char* value){auto* w=own(gtk_label_new(value));gtk_label_set_xalign(GTK_LABEL(w),0);return w;}
    const s::Display& viewport()const{for(const auto& d:topology.displays)if(d.id==display)return d;for(const auto& d:topology.displays)if(d.id==topology.fallback)return d;throw protocol::Error("editor.display");}
    bool protected_selection()const{if(!draft.scene())return false;for(const auto& id:draft.selection())if(edit_protected(*draft.scene(),id))return true;return false;}
    bool own_locks()const{if(!draft.scene()||draft.selection().empty())return false;for(const auto& id:draft.selection())if(!authored_widget(*draft.scene(),id).value("edit_locked",false))return false;return true;}
    bool visibility_supported()const{if(!large_frames||!resources)return false;for(const char* cap:{"scene.content","scene.edit-locks","scene.visibility","configuration.edit-locks","configuration.visibility"})if(!resources->capabilities.count(cap))return false;return true;}
    void presentation(const v::SurfaceFrame& frame){nodes=frame.layout.nodes;hidden.clear();diagnostics.clear();for(const auto& w:frame.widgets){if(!w.presented)hidden.insert(w.id);if(w.diagnostic)diagnostics.insert(w.id);}}
    bool editing()const{return draft.available()&&!draft.active_request()&&draft.state()!=DraftState::conflict&&(!content||!content->opened())&&(!binding||!binding->opened())&&(!creation||!creation->opened())&&(!layout_form||!layout_form->opened())&&(!visibility||!visibility->opened());}
    void ready()const{need(editing(),"editor.unavailable");need(!fields_dirty,"editor.properties_pending");}
    bool clear(){nodes.clear();hidden.clear();diagnostics.clear();if(canvas){atk_object_set_name(gtk_widget_get_accessible(canvas),"");if(!drawing)gtk_widget_queue_draw(canvas);}return true;}
    void stop_preview(){gesture.reset();ticks.clear();if(surface)surface->close();clear();}
    void resolve_nodes(){
        // Input can arrive again before GTK's next draw. Resolve with the same
        // renderer now so a valid queued key is not mistaken for a hidden variant.
        if(surface&&draft.available())surface->paint(now(),ticks,[this](auto,const v::SurfaceFrame* frame){if(frame)presentation(*frame);});
    }
    void preview(){
        if(!draft.available()||!resources){settings=nullptr;resources.reset();stop_preview();return;}
        settings["revision"]=(*draft.scene())["revision"];
        v::SurfaceConfig cfg;cfg.authored={settings,*draft.scene()};cfg.resources=resources->catalog->resources(resources->selection,cfg.authored);cfg.topology=topology;cfg.capabilities=resources->capabilities;cfg.experimental_visibility=visibility_supported();
        if(surface&&surface->status().code==v::SurfaceCode::closed){need(surface->poll_image_jobs(),"editor.renderer_stopping");surface.reset();}
        if(surface)surface->replace(std::move(cfg),now());
        else surface=std::make_unique<v::SceneSurface>(authority,current,std::move(cfg),providers,[this]{return clear();},worker,v::SurfaceAudience::inspector);
        resolve_nodes();gtk_widget_queue_draw(canvas);
    }
    const s::Node* node(const std::string& id)const{for(const auto& n:nodes)if(n.id==id&&n.display==viewport().id)return &n;return nullptr;}
    bool fixed(const std::string& id)const{if(!draft.scene())return false;const auto* n=node(id);return n&&active_layout(id).at("kind")=="fixed";}
    void message(const std::string& value){gtk_label_set_text(GTK_LABEL(status),value.c_str());}
    void guide_feedback(){
        if(!guidance)return;
        std::ostringstream value;value.imbue(std::locale::classic());value<<std::setprecision(17);
        if(gesture&&gesture->input&&draft.available()){
            const auto& d=viewport();const auto& r=gesture->result;
            if(r.x)value<<"X guide: "<<(r.x->position-d.bounds.x)/64.0<<" DIP";
            if(r.y){if(r.x)value<<"; ";value<<"Y guide: "<<(r.y->position-d.bounds.y)/64.0<<" DIP";}
        }
        gtk_label_set_text(GTK_LABEL(guidance),value.str().c_str());
    }
    void sync(bool values=false){
        updating=true;if(values||!draft.available())fields_dirty=false;
        const bool protected_ids=protected_selection();const bool enabled=editing()&&!fields_dirty;const bool one=draft.selection().size()==1;
        const Json* selected=one&&draft.scene()?&authored_widget(*draft.scene(),draft.selection()[0]):nullptr;
        if(values||!draft.available()){
            fields_dirty=false;field_variant=selected&&fixed(draft.selection()[0])?node(draft.selection()[0])->variant:-2;
            for(auto& row:fields){std::string value;
                if(selected){if(row.first=="title")value=(*selected)["title"];
                    else if(row.first=="body"){if((*selected)["kind"]=="text")value=selected->contains("content")?(*selected)["content"]["body"].get<std::string>():selected->at("title").get<std::string>();}
                    else if(fixed(draft.selection()[0]))value=active_layout(draft.selection()[0]).at(row.first).dump();}
                text(row.second,value);
            }
        }
        for(auto& row:fields)gtk_widget_set_sensitive(row.second,editing()&&!protected_ids&&selected&&(row.first=="title"||(row.first=="body"&&(*selected)["kind"]=="text")||((row.first!="body")&&fixed(draft.selection()[0]))));
        // Apply each final state once. Temporarily disabling an enabled button
        // on every repaint cancels a keyboard activation held across that frame.
        for(auto& row:buttons){const auto& id=row.first;bool active=enabled;
            if(id=="undo")active=enabled&&draft.undo_count();else if(id=="redo")active=enabled&&draft.redo_count();
            else if(id=="apply")active=!fields_dirty&&draft.may_submit("commit");else if(id=="cancel")active=editing();
            else if(id=="cancel-request")active=draft.available()&&draft.active_request().has_value();else if(id=="reload")active=!closed&&!draft.active_request();
            else if(id=="properties")active=editing()&&selected&&fields_dirty;else if(id=="revert-fields")active=editing()&&fields_dirty;
            else if(id=="duplicate"||id=="delete")active=enabled&&!draft.selection().empty();
            else if(id=="group")active=enabled&&draft.selection().size()>=2;
            else if(id=="ungroup")active=enabled&&selected&&selected->at("kind")=="group";
            else if(id=="wrap")active=enabled&&!draft.selection().empty();
            else if(id=="unwrap")active=enabled&&selected&&selected->at("kind")=="group";
            else if(id.substr(0,6)=="align-")active=enabled&&draft.selection().size()>=2;
            else if(id.substr(0,6)=="space-")active=enabled&&draft.selection().size()>=3;
            if(id=="bindings")active=enabled&&selected&&draft.scene()->at("schema_version")!="0.2.0"&&(selected->at("kind")=="value"||selected->at("kind")=="status"||selected->at("kind")=="chart"||selected->at("kind")=="table");
            if(id=="layout")active=enabled&&selected;
            if(id=="insert")active=enabled&&draft.scene()&&draft.scene()->at("schema_version")!="0.2.0";
            if(id=="visibility")active=enabled&&draft.visibility_available()&&!draft.selection().empty();
            if(id=="lock")active=enabled&&draft.locks_available()&&!draft.selection().empty();
            if(protected_ids&&(id=="properties"||id=="duplicate"||id=="delete"||id=="group"||id=="ungroup"||id=="wrap"||id=="unwrap"||id=="layout"||id=="bindings"||id=="content"||id=="visibility"||id.substr(0,6)=="align-"||id.substr(0,6)=="space-"))active=false;
            if((content&&content->opened())||(binding&&binding->opened())||(creation&&creation->opened())||(layout_form&&layout_form->opened())||(visibility&&visibility->opened()))active=false;
            gtk_widget_set_sensitive(row.second,active);
        }
        const char* lock_label=own_locks()?"Unlock":"Lock";if(std::string(gtk_button_get_label(GTK_BUTTON(buttons.at("lock"))))!=lock_label){gtk_button_set_label(GTK_BUTTON(buttons.at("lock")),lock_label);accessible(buttons.at("lock"),lock_label,"editor.lock");}
        gtk_widget_set_sensitive(tree,enabled);gtk_widget_set_sensitive(canvas,enabled);
        std::string value;
        if(!draft.available())value="Editor unavailable";
        else if(draft.state()==DraftState::pending)value="Request pending; storage outcome is not known.";
        else if(draft.state()==DraftState::unknown)value="Outcome unknown; retrieve the original request.";
        else if(draft.state()==DraftState::conflict)value="Configuration changed; reload before applying.";
        else if(fields_dirty)value="Property fields have not been applied to the draft.";
        else if(!draft.last_result().is_null()&&draft.last_result()["outcome"]=="accepted")value="Saved durably; activation pending. Visibility unconfirmed.";
        else value=draft.dirty()?"Draft changes have not been saved.":"No draft changes.";
        if(draft.revision())value+=" Revision "+std::to_string(*draft.revision());
        if(!error.empty()&&draft.available())value=error;
        const bool unavailable=draft.available()&&surface&&surface->status().code==v::SurfaceCode::alternative;
        if(unavailable)value+=" Preview unavailable. Use Layout or Undo to recover.";
        else if(selected){const auto* n=node(draft.selection()[0]);value+=n?(n->variant<0?" Active layout: Base":" Active layout: Breakpoint "+std::to_string(n->variant+1)):" Not on this display";}
        if(selected&&edit_locked(*draft.scene(),draft.selection()[0]))value+=selected->value("edit_locked",false)?" Locked":" Locked by container";
        else if(protected_ids)value+=" Contains locked objects";
        if(selected&&hidden.count(draft.selection()[0]))value+=" Content hidden by condition.";
        else if(selected&&diagnostics.count(draft.selection()[0]))value+=" Conditional content has a diagnostic.";
        message(value);guide_feedback();updating=false;
    }
    void list(){
        updating=true;GtkTreeIter it;if(gtk_tree_model_get_iter_first(GTK_TREE_MODEL(model),&it))do{gtk_list_store_set(model,&it,0,"",1,"",-1);}while(gtk_tree_model_iter_next(GTK_TREE_MODEL(model),&it));
        gtk_list_store_clear(model);auto* selection=gtk_tree_view_get_selection(GTK_TREE_VIEW(tree));
        if(draft.scene())for(const auto& w:(*draft.scene())["widgets"]){const auto id=w["id"].get<std::string>(),title=w["title"].get<std::string>();gtk_list_store_append(model,&it);gtk_list_store_set(model,&it,0,id.c_str(),1,title.c_str(),-1);
            if(std::find(draft.selection().begin(),draft.selection().end(),id)!=draft.selection().end())gtk_tree_selection_select_iter(selection,&it);}
        updating=false;
    }
    void changed(){gesture.reset();error.clear();preview();list();sync(true);}
    void selected(std::vector<std::string> ids,bool from_tree=false){ready();draft.select(std::move(ids));if(!from_tree)list();sync(true);gtk_widget_queue_draw(canvas);}
    void execute(const std::vector<SceneEdit>& edits){ready();draft.execute(edits);changed();}
    void properties(){
        need(editing()&&draft.selection().size()==1,"editor.selection");const auto id=draft.selection()[0];const auto& w=authored_widget(*draft.scene(),id);
        need(field_variant==-2||(node(id)&&node(id)->variant==field_variant),"editor.layout_changed");
        std::vector<SceneEdit> edits{WidgetPropertyEdit{id,WidgetProperty::title,text(fields["title"])}};
        if(w["kind"]=="text"&&w.contains("content"))edits.push_back(WidgetContentEdit{id,w["bindings"],{{"body",text(fields["body"])}}});
        if(fixed(id)){auto layout=w["layout"];const int index=node(id)->variant;auto& target=index<0?layout["base"]:layout["breakpoints"][static_cast<std::size_t>(index)]["layout"];for(const char* key:{"x","y","width","height"})target[key]=number(text(fields[key]));edits.push_back(WidgetPropertyEdit{id,WidgetProperty::layout,std::move(layout)});}
        draft.execute(edits);fields_dirty=false;changed();
    }
    void duplicate(){
        ready();need(!draft.selection().empty(),"editor.selection");std::map<std::string,std::string> mapping;
        std::function<void(const std::string&)> visit=[&](const std::string& id){need(mapping.emplace(id,actions.widget_id()).second,"editor.overlap");const auto& w=authored_widget(*draft.scene(),id);if(w.contains("children"))for(const auto& child:w["children"])visit(child);};
        std::vector<std::string> copies;
        for(const auto& id:draft.selection()){visit(id);copies.push_back(mapping.at(id));}
        execute({DuplicateWidgets{draft.selection(),mapping}});selected(std::move(copies));
    }
    void add(){
        ready();const auto id=actions.widget_id();Json w={{"id",id},{"kind","text"},{"title","Text"},{"display",{{"local_id",viewport().id}}},
            {"layout",{{"base",{{"kind","fixed"},{"x",20},{"y",20},{"width",180},{"height",80}}}}},{"bindings",Json::array()},{"priority","normal"}};
        if((*draft.scene())["schema_version"]!="0.2.0")w["content"]={{"body","Text"}};
        execute({InsertWidget{w,std::nullopt,(*draft.scene())["roots"].size()}});selected({id});
    }
    void dispatch(const std::function<void()>& f){dispatching=true;try{f();dispatching=false;}catch(...){dispatching=false;throw;}}
    void submit(){ready();const auto q=draft.begin("commit",actions.request_id());sync();if(q)try{dispatch([&]{actions.submit(*q);});}catch(...){draft.disconnected();sync();}}
    void arrange(const std::string& id){
        ready();gesture.reset();resolve_nodes();const auto ids=draft.selection();need(!ids.empty(),"editor.targets");const s::Node* first=nullptr;std::vector<int> indices;
        for(const auto& selected_id:ids){need(fixed(selected_id),"editor.arrange_geometry");const auto* n=node(selected_id);
            const auto& b=active_layout(selected_id);indices.push_back(n->variant);
            need(n->box.width==std::ceil(b["width"].get<double>()*64)&&n->box.height==std::ceil(b["height"].get<double>()*64),"editor.arrange_geometry");
            need(!first||(n->parent==first->parent&&n->display==first->display),"editor.arrange_scope");first=n;}
        if(id=="space-horizontal"||id=="space-vertical")execute({DistributeWidgets{ids,id=="space-horizontal"?Spacing::horizontal:Spacing::vertical,indices}});
        else {static const std::map<std::string,Alignment> kinds={{"align-left",Alignment::left},{"align-hcenter",Alignment::hcenter},{"align-right",Alignment::right},
            {"align-top",Alignment::top},{"align-vcenter",Alignment::vcenter},{"align-bottom",Alignment::bottom}};execute({AlignWidgets{ids,kinds.at(id),indices}});}
    }
    const Json& active_layout(const std::string& id)const{
        const auto* n=node(id);need(n!=nullptr,"editor.group_geometry");const auto& l=authored_widget(*draft.scene(),id).at("layout");
        return n->variant<0?l.at("base"):l.at("breakpoints").at(static_cast<std::size_t>(n->variant)).at("layout");
    }
    void group_geometry(const std::string& id,bool parent=false)const{
        const auto& l=active_layout(id);const auto* n=node(id);
        need(l.at("kind")=="fixed"||(parent&&l.at("kind")=="canvas"),"editor.group_geometry");
        need(n->box.width==std::ceil(l.at("width").get<double>()*64)&&n->box.height==std::ceil(l.at("height").get<double>()*64),"editor.group_geometry");
    }
    void group(bool remove){
        ready();gesture.reset();resolve_nodes();const auto ids=draft.selection();need(!ids.empty(),"editor.targets");
        for(const auto& id:ids){group_geometry(id);need(node(id)->parent==node(ids[0])->parent,"editor.arrange_scope");}
        const auto parent=node(ids[0])->parent;if(!parent.empty())group_geometry(parent,true);
        if(remove){need(ids.size()==1,"editor.selection");const auto& w=authored_widget(*draft.scene(),ids[0]);need(w.at("kind")=="group","editor.group");
            for(const auto& child:w.at("children"))group_geometry(child.get<std::string>());
            execute({UngroupWidget{ids[0]}});
        }else execute({GroupWidgets{ids,actions.widget_id(),"Group"}});
    }
    SnapInput capture_snap(const std::vector<s::Node>& selected,bool resize){
        need(!selected.empty(),"editor.selection");const auto& d=viewport();SnapInput in;in.selection=selected[0].box;in.resize=resize;
        in.grid=snap_grid;in.guides=snap_guides;in.spacing=grid_spacing;in.origin_x=d.bounds.x;in.origin_y=d.bounds.y;
        const auto parent=selected[0].parent;std::set<std::string> ids;
        for(const auto& n:selected){need(n.parent==parent&&ids.insert(n.id).second,"editor.arrange_scope");group_geometry(n.id);
            const auto right=std::max(in.selection.x+in.selection.width,n.box.x+n.box.width),bottom=std::max(in.selection.y+in.selection.height,n.box.y+n.box.height);
            in.selection.x=std::min(in.selection.x,n.box.x);in.selection.y=std::min(in.selection.y,n.box.y);in.selection.width=right-in.selection.x;in.selection.height=bottom-in.selection.y;}
        if(parent.empty())in.area={d.work.x+d.safe.left,d.work.y+d.safe.top,d.work.width-d.safe.left-d.safe.right,d.work.height-d.safe.top-d.safe.bottom};
        else {group_geometry(parent,true);in.area=node(parent)->content;}
        for(const auto& n:nodes)if(n.display==d.id&&n.parent==parent&&!ids.count(n.id))in.siblings.push_back({n.id,n.box});
        (void)snap(in);return in;
    }
    void option(const std::string& id){
        ready();gesture.reset();
        if(id=="grid-spacing"){grid_spacing=grid_spacing==32*64?4*64:grid_spacing*2;const auto label="Grid "+std::to_string(grid_spacing/64)+" DIP";gtk_button_set_label(GTK_BUTTON(buttons.at(id)),label.c_str());accessible(buttons.at(id),label,"editor.grid-spacing");}
        else {const bool active=gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(buttons.at(id)));if(id=="snap-grid")snap_grid=active;else if(id=="snap-guides")snap_guides=active;else show_grid=active;}
        guide_feedback();gtk_widget_queue_draw(canvas);
    }
    void command(const std::string& id){
        if(id=="insert"){ready();gesture.reset();need(resources.has_value(),"editor.resources");
            if(!creation)creation=std::make_unique<EditorCreateForm>(root,[this](const CreateInput& input){
                need(resources.has_value(),"editor.resources");const auto snapshot=resources->catalog->resources(resources->selection,{settings,*draft.scene()});
                auto edit=create_widget(*draft.scene(),input,"editor:proposed",{{"local_id",viewport().id}},content_choices(*snapshot));edit.widget["id"]=actions.widget_id();return draft.execute({edit});
            },[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});
            const auto snapshot=resources->catalog->resources(resources->selection,{settings,*draft.scene()});creation->open(*draft.scene(),draft.selection(),content_choices(*snapshot));sync();}
        else if(id=="visibility"){ready();gesture.reset();need(draft.visibility_available()&&!draft.selection().empty()&&!protected_selection(),"editor.visibility_unavailable");
            if(!visibility)visibility=std::make_unique<EditorVisibilityForm>(root,[this](const std::optional<SetWidgetVisibility>& edit){need(draft.visibility_available(),"editor.visibility_unavailable");return edit?draft.execute({*edit}):false;},[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});
            visibility->open(*draft.scene(),draft.selection());sync();}
        else if(id=="bindings"){ready();gesture.reset();need(draft.selection().size()==1,"editor.selection");
            if(!binding)binding=std::make_unique<EditorBindingForm>(root,[this](const std::vector<SceneEdit>& edits){return draft.execute(edits);},[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});
            binding->open(authored_widget(*draft.scene(),draft.selection()[0]));sync();}
        else if(id=="content"){ready();gesture.reset();need(resources.has_value(),"editor.resources");const auto snapshot=resources->catalog->resources(resources->selection,{settings,*draft.scene()});const Json* w=draft.selection().size()==1?&authored_widget(*draft.scene(),draft.selection()[0]):nullptr;
            // Construct native modal chrome only when the user opens it. Hidden
            // dialog focus/accessibility initialization must not join editor entry.
            if(!content)content=std::make_unique<EditorContentForm>(root,[this](const std::vector<SceneEdit>& edits){return draft.execute(edits);},[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});
            content->open(*draft.scene(),w,*snapshot);sync();}
        else if(id=="layout"||id=="wrap"||id=="unwrap"){ready();gesture.reset();need(id=="wrap"?!draft.selection().empty():draft.selection().size()==1,"editor.selection");
            if(!layout_form)layout_form=std::make_unique<EditorLayoutForm>(root,[this](const std::vector<SceneEdit>& edits){return draft.execute(edits);},[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});
            if(id=="wrap")layout_form->wrap(*draft.scene(),draft.selection(),actions.widget_id());else if(id=="unwrap")layout_form->unwrap(*draft.scene(),draft.selection()[0]);else layout_form->open(*draft.scene(),draft.selection()[0]);sync();}
        else if(id=="lock"){ready();gesture.reset();execute({SetWidgetLocks{draft.selection(),!own_locks()}});}
        else if(id=="properties")properties();else if(id=="revert-fields"){fields_dirty=false;error.clear();sync(true);}
        else if(id=="apply")submit();else if(id=="reload")dispatch(actions.reload);
        else if(id=="cancel-request"){const auto q=draft.cancel_request();if(q)try{dispatch([&]{actions.cancel(*q);});}catch(...){draft.disconnected();sync();}}
        else if(id=="cancel"){draft.discard();shut();dispatch(actions.exit);}
        else if(id=="add")add();else if(id=="duplicate")duplicate();else if(id=="delete")execute({RemoveWidgets{draft.selection()}});
        else if(id=="group"||id=="ungroup")group(id=="ungroup");
        else if(id=="snap-grid"||id=="snap-guides"||id=="show-grid"||id=="grid-spacing")option(id);
        else if(id.substr(0,6)=="align-"||id.substr(0,6)=="space-")arrange(id);
        else {ready();if(id=="undo")draft.undo();else if(id=="redo")draft.redo();changed();}
    }
    void point(double x,double y,bool shift){
        ready();gtk_widget_grab_focus(canvas);if(visibility_supported()||snap_grid||snap_guides)resolve_nodes();const auto& d=viewport();const double factor=gtk_widget_get_scale_factor(canvas);x=x*factor+d.pixel_x;y=y*factor+d.pixel_y;
        const s::Node* hit=nullptr;for(auto i=nodes.rbegin();i!=nodes.rend();++i)if(i->display==d.id&&!hidden.count(i->id)&&contains(i->pixels,x,y)){hit=&*i;break;}
        if(!hit){selected({});return;}const auto id=hit->id;auto ids=draft.selection();const auto found=std::find(ids.begin(),ids.end(),id);
        if(shift){if(found==ids.end())ids.push_back(id);else ids.erase(found);selected(std::move(ids));return;}
        if(found==ids.end())selected({id});
        if(protected_selection()){gesture.reset();gtk_widget_queue_draw(canvas);return;}
        Gesture g;g.x=x;g.y=y;
        for(const auto& selected_id:draft.selection()){if(!fixed(selected_id)){gtk_widget_queue_draw(canvas);return;}g.nodes.push_back(*node(selected_id));}
        g.resize=g.nodes.size()==1&&x>=g.nodes[0].pixels.x+g.nodes[0].pixels.width-8&&y>=g.nodes[0].pixels.y+g.nodes[0].pixels.height-8;
        g.pixel_per_unit=static_cast<double>(d.scale_numerator)/(64*d.scale_denominator);if(snap_grid||snap_guides)g.input=capture_snap(g.nodes,g.resize);
        gesture=std::move(g);gtk_widget_queue_draw(canvas);
    }
    void motion(double x,double y,bool bypass){if(!gesture)return;const auto& d=viewport();const double factor=gtk_widget_get_scale_factor(canvas);auto& g=*gesture;g.dx=x*factor+d.pixel_x-g.x;g.dy=y*factor+d.pixel_y-g.y;
        if(g.input){const double dx=std::round(g.dx/g.pixel_per_unit),dy=std::round(g.dy/g.pixel_per_unit);need(std::isfinite(dx)&&std::isfinite(dy)&&std::abs(dx)<=134217728&&std::abs(dy)<=134217728,"editor.snap_input");
            g.input->dx=static_cast<s::Unit>(dx);g.input->dy=static_cast<s::Unit>(dy);g.input->bypass=bypass;g.result=snap(*g.input);g.dx=g.result.dx*g.pixel_per_unit;g.dy=g.result.dy*g.pixel_per_unit;}
        guide_feedback();gtk_widget_queue_draw(canvas);}
    void release(double x,double y,bool bypass){if(!gesture)return;motion(x,y,bypass);const auto g=*gesture;gesture.reset();guide_feedback();const auto& d=viewport();const double scale=static_cast<double>(d.scale_denominator)/d.scale_numerator;
        if(g.dx==0&&g.dy==0){gtk_widget_queue_draw(canvas);return;}
        if(g.resize){const auto& base=active_layout(g.nodes[0].id);execute({ResizeWidget{g.nodes[0].id,base["width"].get<double>()+g.dx*scale,base["height"].get<double>()+g.dy*scale,g.nodes[0].variant}});}
        else {std::vector<int> indices;for(const auto& n:g.nodes)indices.push_back(n.variant);execute({MoveWidgets{draft.selection(),g.dx*scale,g.dy*scale,indices}});}
    }
    bool key(GdkEventKey* e){
        if(e->keyval==GDK_KEY_Escape){gesture.reset();guide_feedback();gtk_widget_queue_draw(canvas);return true;}
        if((e->state&GDK_CONTROL_MASK)&&(e->keyval==GDK_KEY_z||e->keyval==GDK_KEY_Z)){command(e->state&GDK_SHIFT_MASK?"redo":"undo");return true;}
        if(e->keyval==GDK_KEY_Delete){command("delete");return true;}
        double x=0,y=0;const double amount=e->state&GDK_SHIFT_MASK?10:1;
        if(e->keyval==GDK_KEY_Left)x=-amount;else if(e->keyval==GDK_KEY_Right)x=amount;else if(e->keyval==GDK_KEY_Up)y=-amount;else if(e->keyval==GDK_KEY_Down)y=amount;else return false;
        ready();need(!draft.selection().empty(),"editor.selection");for(const auto& id:draft.selection())need(fixed(id),"editor.fixed_variant");
        if(e->state&GDK_MOD1_MASK){need(draft.selection().size()==1,"editor.selection");const auto id=draft.selection()[0];const auto& b=active_layout(id);execute({ResizeWidget{id,b["width"].get<double>()+x,b["height"].get<double>()+y,node(id)->variant}});}
        else {std::vector<int> indices;for(const auto& id:draft.selection())indices.push_back(node(id)->variant);execute({MoveWidgets{draft.selection(),x,y,indices}});}
        return true;
    }
    void draw(cairo_t* cr){
        struct Drawing {bool& flag;explicit Drawing(bool& f):flag(f){flag=true;}~Drawing(){flag=false;}} guard(drawing);
        cairo_set_source_rgb(cr,0,0,0);cairo_paint(cr);if(!surface||!draft.available())return;
        const auto d=viewport();const double factor=gtk_widget_get_scale_factor(canvas);cairo_save(cr);cairo_scale(cr,1/factor,1/factor);
        surface->paint(now(),ticks,[&](auto,const v::SurfaceFrame* frame){
            if(!frame)return;
            presentation(*frame);std::string description;
            for(const auto& w:frame->widgets){if(!w.presented)continue;if(description.size()+w.accessible.size()>65536){description+="\nMore content in inspector";break;}description+=w.accessible+"\n";}
            atk_object_set_name(gtk_widget_get_accessible(canvas),description.c_str());
            if(!gesture||draft.scene()->at("schema_version")=="0.5.0")for(const auto& image:frame->displays)if(image.display==d.id){
                std::vector<std::uint32_t> argb(static_cast<std::size_t>(image.width)*image.height);for(std::size_t n=0;n<argb.size();++n)argb[n]=(static_cast<std::uint32_t>(image.rgba[n*4+3])<<24)|(static_cast<std::uint32_t>(image.rgba[n*4])<<16)|(static_cast<std::uint32_t>(image.rgba[n*4+1])<<8)|image.rgba[n*4+2];
                auto* bitmap=cairo_image_surface_create_for_data(reinterpret_cast<unsigned char*>(argb.data()),CAIRO_FORMAT_ARGB32,static_cast<int>(image.width),static_cast<int>(image.height),static_cast<int>(image.width*4));cairo_set_source_surface(cr,bitmap,0,0);cairo_paint(cr);cairo_surface_destroy(bitmap);
            }
            const double device_per_unit=static_cast<double>(d.scale_numerator)/(64*d.scale_denominator);
            if(show_grid){s::Unit multiple=1;while(d.bounds.width/(grid_spacing*multiple)+d.bounds.height/(grid_spacing*multiple)+2>512)++multiple;
                cairo_set_source_rgb(cr,0.2,0.2,0.2);cairo_set_line_width(cr,1);
                for(s::Unit x=0;x<=d.bounds.width;x+=grid_spacing*multiple){const double px=std::floor(x*device_per_unit)+0.5;cairo_move_to(cr,px,0);cairo_line_to(cr,px,d.bounds.height*device_per_unit);}
                for(s::Unit y=0;y<=d.bounds.height;y+=grid_spacing*multiple){const double py=std::floor(y*device_per_unit)+0.5;cairo_move_to(cr,0,py);cairo_line_to(cr,d.bounds.width*device_per_unit,py);}cairo_stroke(cr);
            }
            cairo_set_source_rgb(cr,0,0.6,1);cairo_set_line_width(cr,2);
            const auto selected_nodes=gesture?gesture->nodes:nodes;
            for(const auto& n:selected_nodes)if(n.display==d.id&&std::find(draft.selection().begin(),draft.selection().end(),n.id)!=draft.selection().end()){
                double x=n.pixels.x-d.pixel_x,y=n.pixels.y-d.pixel_y,w=n.pixels.width,h=n.pixels.height;
                if(gesture){if(gesture->resize){w+=gesture->dx;h+=gesture->dy;}else{x+=gesture->dx;y+=gesture->dy;}}
                cairo_rectangle(cr,x+1,y+1,w-2,h-2);cairo_stroke(cr);if(draft.selection().size()==1&&fixed(n.id)){cairo_rectangle(cr,x+w-8,y+h-8,8,8);cairo_fill(cr);}
            }
            if(gesture&&gesture->input){const auto& r=gesture->result;cairo_set_source_rgb(cr,1,0,1);cairo_set_line_width(cr,1);
                if(r.x){const double px=std::floor((r.x->position-d.bounds.x)*device_per_unit)+0.5;cairo_move_to(cr,px,0);cairo_line_to(cr,px,d.bounds.height*device_per_unit);}
                if(r.y){const double py=std::floor((r.y->position-d.bounds.y)*device_per_unit)+0.5;cairo_move_to(cr,0,py);cairo_line_to(cr,d.bounds.width*device_per_unit,py);}cairo_stroke(cr);}
        });cairo_restore(cr);
        // Selection can arrive after telemetry erased native caches but before
        // this frame resolved them. Hydrate clean fields once geometry returns;
        // never replace a user's pending property input during repaint.
        const bool resolved_fields=!fields_dirty&&draft.selection().size()==1&&fixed(draft.selection()[0])&&field_variant!=node(draft.selection()[0])->variant;
        sync(resolved_fields);
    }
    void shut(){if(closed)return;closed=true;if(content)content->erase();if(binding)binding->erase();if(creation)creation->erase();if(layout_form)layout_form->erase();if(visibility)visibility->erase();draft.close();fields_dirty=false;settings=nullptr;resources.reset();stop_preview();if(tree){list();sync(true);}}
    template<class F> void event(F f)noexcept{try{if(!closed)f();}catch(const protocol::Error& e){gesture.reset();const std::string code=e.what();
        guide_feedback();error=code=="editor.number"?"Enter a number using digits and an optional decimal point.":code=="editor.layout_changed"?"Layout changed; Revert fields before applying.":
            code=="editor.arrange_geometry"||code=="editor.arrange_scope"?"Arrange needs fixed widgets in the same parent and display, with no size expansion.":
            code=="editor.group_geometry"||code=="editor.group_layout"||code=="editor.fixed"?"Grouping needs fixed layouts and a fixed or canvas parent, with no size expansion.":
            code=="editor.visibility_container"?"Clear this container's visibility condition before removing it.":
            code=="editor.group_clip"?"Ungroup would reveal clipped content. Adjust the group or child layouts first.":
            code=="editor.spacing_overlap"?"There is not enough room for equal gaps between the endpoints.":"This edit could not be applied. Check the selection and property values.";
        message(error);gtk_widget_queue_draw(canvas);}catch(...){try{shut();}catch(...){}}}
    ~Impl(){if(timer)g_source_remove(timer);try{shut();}catch(...){}surface.reset();if(root)gtk_widget_destroy(root);for(auto i=owned.rbegin();i!=owned.rend();++i)g_object_unref(*i);if(model)g_object_unref(model);}
};
EditorForm::EditorForm(c::Authority a,c::Policy p,c::Authored value,std::string epoch,SettingsResources resources,s::Topology topology,std::string display,std::vector<v::SurfaceProvider> providers,std::string worker,Actions actions,bool large_commands)
 :impl_(std::make_unique<Impl>(std::move(a),std::move(p),std::move(value),std::move(epoch),std::move(resources),std::move(topology),std::move(display),std::move(providers),std::move(worker),std::move(actions),large_commands)){
    auto& i=*impl_;need(i.actions.request_id&&i.actions.widget_id&&i.actions.submit&&i.actions.cancel&&i.actions.reload&&i.actions.exit,"editor.actions");
    i.root=i.own(gtk_box_new(GTK_ORIENTATION_VERTICAL,4));auto* top=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,4);gtk_box_pack_start(GTK_BOX(i.root),top,FALSE,FALSE,0);
    auto button=[&](GtkWidget* box,const char* id,const char* label){auto* w=i.own(gtk_button_new_with_label(label));i.buttons[id]=w;accessible(w,label,std::string("editor.")+id);g_object_set_data_full(G_OBJECT(w),"editor-action",g_strdup(id),g_free);gtk_box_pack_start(GTK_BOX(box),w,FALSE,FALSE,0);
        g_signal_connect(w,"clicked",G_CALLBACK(+[](GtkWidget* w,gpointer p){auto& o=*static_cast<Impl*>(p);o.event([&]{o.command(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"editor-action")));});}),&i);};
    for(const auto& b:std::vector<std::pair<const char*,const char*>>{{"undo","Undo"},{"redo","Redo"},{"apply","Apply"},{"cancel","Cancel session"},{"cancel-request","Cancel request"},{"reload","Reload"},{"content","Content"},{"bindings","Bindings"},{"layout","Layout"}})button(top,b.first,b.second);
    auto* middle=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,6);gtk_box_pack_start(GTK_BOX(i.root),middle,TRUE,TRUE,0);i.canvas=i.own(gtk_drawing_area_new());gtk_widget_set_size_request(i.canvas,500,420);gtk_widget_set_can_focus(i.canvas,TRUE);
    accessible(i.canvas,"","editor.canvas");gtk_widget_add_events(i.canvas,GDK_BUTTON_PRESS_MASK|GDK_BUTTON_RELEASE_MASK|GDK_POINTER_MOTION_MASK|GDK_KEY_PRESS_MASK|GDK_FOCUS_CHANGE_MASK);gtk_box_pack_start(GTK_BOX(middle),i.canvas,TRUE,TRUE,0);
    auto* side=gtk_box_new(GTK_ORIENTATION_VERTICAL,3);gtk_widget_set_size_request(side,270,-1);gtk_box_pack_start(GTK_BOX(middle),side,FALSE,FALSE,0);
    i.model=gtk_list_store_new(2,G_TYPE_STRING,G_TYPE_STRING);i.tree=i.own(gtk_tree_view_new_with_model(GTK_TREE_MODEL(i.model)));gtk_tree_view_set_enable_search(GTK_TREE_VIEW(i.tree),FALSE);accessible(i.tree,"Scene objects","editor.objects");
    auto* column=gtk_tree_view_column_new_with_attributes("Scene objects",gtk_cell_renderer_text_new(),"text",1,nullptr);gtk_tree_view_append_column(GTK_TREE_VIEW(i.tree),column);auto* selection=gtk_tree_view_get_selection(GTK_TREE_VIEW(i.tree));gtk_tree_selection_set_mode(selection,GTK_SELECTION_MULTIPLE);
    auto* scroll=gtk_scrolled_window_new(nullptr,nullptr);gtk_widget_set_size_request(scroll,-1,105);gtk_container_add(GTK_CONTAINER(scroll),i.tree);gtk_box_pack_start(GTK_BOX(side),scroll,FALSE,FALSE,0);
    for(const auto& row:std::vector<std::pair<const char*,const char*>>{{"title","Title"},{"body","Text body"},{"x","X (DIP)"},{"y","Y (DIP)"},{"width","Width (DIP)"},{"height","Height (DIP)"}}){
        auto* line=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,4);auto* label=i.label(row.second);gtk_widget_set_size_request(label,85,-1);gtk_box_pack_start(GTK_BOX(line),label,FALSE,FALSE,0);
        const std::string id=row.first;auto* field=i.own(private_text(id=="title"?512:id=="body"?1024:64,id=="body"));i.fields[id]=field;gtk_widget_set_size_request(field,150,id=="body"?50:25);accessible(field,row.second,"editor.value."+id);gtk_label_set_mnemonic_widget(GTK_LABEL(label),field);gtk_box_pack_start(GTK_BOX(line),field,TRUE,TRUE,0);gtk_box_pack_start(GTK_BOX(side),line,FALSE,FALSE,0);
        g_signal_connect(gtk_text_view_get_buffer(GTK_TEXT_VIEW(field)),"changed",G_CALLBACK(+[](GtkTextBuffer*,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.fields_dirty=true;o.sync();});}),&i);
    }
    auto* prop=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,3);gtk_box_pack_start(GTK_BOX(side),prop,FALSE,FALSE,0);button(prop,"properties","Set properties");button(prop,"revert-fields","Revert fields");
    auto check=[&](GtkWidget* box,const char* id,const char* label){auto* w=i.own(gtk_check_button_new_with_label(label));i.buttons[id]=w;accessible(w,label,std::string("editor.")+id);g_object_set_data_full(G_OBJECT(w),"editor-action",g_strdup(id),g_free);gtk_box_pack_start(GTK_BOX(box),w,FALSE,FALSE,0);
        g_signal_connect(w,"toggled",G_CALLBACK(+[](GtkWidget* w,gpointer p){auto& o=*static_cast<Impl*>(p);o.event([&]{o.command(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"editor-action")));});}),&i);};
    auto* snapping=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,3);gtk_box_pack_start(GTK_BOX(side),snapping,FALSE,FALSE,0);check(snapping,"snap-grid","Snap to grid");check(snapping,"snap-guides","Snap to guides");
    auto* grid=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,3);gtk_box_pack_start(GTK_BOX(side),grid,FALSE,FALSE,0);check(grid,"show-grid","Show grid");button(grid,"grid-spacing","Grid 8 DIP");button(grid,"visibility","Visibility");
    auto* containers=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,3);gtk_box_pack_start(GTK_BOX(side),containers,FALSE,FALSE,0);button(containers,"wrap","Wrap...");button(containers,"unwrap","Unwrap...");button(containers,"lock","Lock");
    i.guidance=i.label("");accessible(i.guidance,"","editor.guidance");gtk_widget_set_size_request(i.guidance,-1,20);gtk_box_pack_start(GTK_BOX(containers),i.guidance,TRUE,TRUE,0);
    auto* bottom=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,4);gtk_box_pack_start(GTK_BOX(i.root),bottom,FALSE,FALSE,0);button(bottom,"add","Add text");button(bottom,"duplicate","Duplicate");button(bottom,"delete","Delete");
    auto* align=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,3);gtk_box_pack_start(GTK_BOX(i.root),align,FALSE,FALSE,0);
    for(const auto& b:std::vector<std::pair<const char*,const char*>>{{"insert","Add widget"},{"align-left","Align left"},{"align-hcenter","Center horizontally"},{"align-right","Align right"},{"align-top","Align top"},{"align-vcenter","Center vertically"},{"align-bottom","Align bottom"}})button(align,b.first,b.second);
    button(bottom,"space-horizontal","Space horizontally");button(bottom,"space-vertical","Space vertically");
    button(bottom,"group","Group");button(bottom,"ungroup","Ungroup");
    i.status=i.label("");accessible(i.status,"","editor.status");gtk_label_set_line_wrap(GTK_LABEL(i.status),TRUE);gtk_box_pack_start(GTK_BOX(i.root),i.status,FALSE,FALSE,0);
    g_signal_connect(selection,"changed",G_CALLBACK(+[](GtkTreeSelection* selection,gpointer p){auto& o=*static_cast<Impl*>(p);if(o.updating)return;o.event([&]{std::vector<std::string> ids;GtkTreeModel* model=nullptr;auto* rows=gtk_tree_selection_get_selected_rows(selection,&model);
        for(auto* row=rows;row;row=row->next){GtkTreeIter it;if(gtk_tree_model_get_iter(model,&it,static_cast<GtkTreePath*>(row->data))){gchar* id=nullptr;gtk_tree_model_get(model,&it,0,&id,-1);ids.emplace_back(id);g_free(id);}}g_list_free_full(rows,reinterpret_cast<GDestroyNotify>(gtk_tree_path_free));o.selected(std::move(ids),true);});}),&i);
    g_signal_connect(i.canvas,"draw",G_CALLBACK(+[](GtkWidget*,cairo_t* cr,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);if(o.closed){cairo_set_source_rgb(cr,0,0,0);cairo_paint(cr);}else o.event([&]{o.draw(cr);});return TRUE;}),&i);
    g_signal_connect(i.canvas,"button-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventButton* e,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);if(e->button!=1)return FALSE;o.event([&]{o.point(e->x,e->y,e->state&GDK_SHIFT_MASK);});return TRUE;}),&i);
    g_signal_connect(i.canvas,"motion-notify-event",G_CALLBACK(+[](GtkWidget*,GdkEventMotion* e,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.event([&]{o.motion(e->x,e->y,e->state&GDK_CONTROL_MASK);});return TRUE;}),&i);
    g_signal_connect(i.canvas,"button-release-event",G_CALLBACK(+[](GtkWidget*,GdkEventButton* e,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);if(e->button!=1)return FALSE;o.event([&]{o.release(e->x,e->y,e->state&GDK_CONTROL_MASK);});return TRUE;}),&i);
    g_signal_connect(i.canvas,"key-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventKey* e,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);bool handled=false;o.event([&]{handled=o.key(e);});return handled;}),&i);
    g_signal_connect(i.canvas,"focus-out-event",G_CALLBACK(+[](GtkWidget*,GdkEventFocus*,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.gesture.reset();o.guide_feedback();gtk_widget_queue_draw(o.canvas);return FALSE;}),&i);
    g_signal_connect(i.root,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer p){static_cast<Impl*>(p)->shut();}),&i);
    // Sensitive/focus style transitions otherwise keep the shared frame clock
    // painting after policy erasure. Apply state changes immediately within this
    // editor; preserve theme values and the desktop's animation preference.
    auto* style=gtk_css_provider_new();gtk_css_provider_load_from_data(style,"* { transition: none; }",-1,nullptr);
    immediate_style(i.root,style);g_object_unref(style);
    // GTK publishes accessible focus from normal-idle work. A paint can take
    // longer than this interval; periodic refresh must yield to that work rather
    // than keeping higher-priority drawing continuously ready. Unavailable drafts
    // already queued their clearing paint; do not keep repainting that empty view.
    i.preview();i.list();i.sync(true);i.timer=g_timeout_add_full(G_PRIORITY_LOW,40,+[](gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);try{if(o.surface)o.surface->poll_image_jobs();if(!o.closed&&o.draft.available())gtk_widget_queue_draw(o.canvas);}catch(...){o.shut();}return G_SOURCE_CONTINUE;},&i,nullptr);
}
EditorForm::~EditorForm()=default;
GtkWidget* EditorForm::widget()const{impl_->owner();return impl_->root;}
void EditorForm::complete(std::uint64_t ticket,const Json& result){auto& i=*impl_;i.owner();if(i.closed)return;try{if(i.draft.complete(ticket,result))i.changed();}catch(...){i.sync();throw;}}
void EditorForm::reconciled(std::uint64_t ticket,const std::string& query,const std::string& epoch,const Json& result){auto& i=*impl_;i.owner();if(i.closed)return;try{if(i.draft.reconciled(ticket,query,epoch,result))i.changed();}catch(...){i.sync();throw;}}
void EditorForm::disconnected(){auto& i=*impl_;i.owner();if(i.closed)return;if(i.content)i.content->erase();if(i.binding)i.binding->erase();if(i.creation)i.creation->erase();if(i.layout_form)i.layout_form->erase();if(i.visibility)i.visibility->erase();i.draft.disconnected();i.gesture.reset();i.sync();}
void EditorForm::policy(c::Policy policy){auto& i=*impl_;i.owner();if(i.closed)return;if(i.content)i.content->erase();if(i.binding)i.binding->erase();if(i.creation)i.creation->erase();if(i.layout_form)i.layout_form->erase();if(i.visibility)i.visibility->erase();i.gesture.reset();i.draft.policy(policy);i.current=std::move(policy);if(i.surface)i.surface->policy(i.current,i.now());
    if(!i.draft.available()){i.settings=nullptr;i.resources.reset();i.stop_preview();i.list();}else i.resolve_nodes();i.sync();}
void EditorForm::reload(c::Authored value,std::string epoch,SettingsResources resources){auto& i=*impl_;i.owner();if(i.closed)return;
    if(i.content)i.content->erase();
    if(i.binding)i.binding->erase();
    if(i.creation)i.creation->erase();
    if(i.layout_form)i.layout_form->erase();
    if(i.visibility)i.visibility->erase();
    if(i.surface&&i.surface->status().code==v::SurfaceCode::closed)need(i.surface->poll_image_jobs(),"editor.renderer_stopping");
    i.draft.reload(value,std::move(epoch),resources);i.settings=std::move(value.settings);i.resources=std::move(resources);i.fields_dirty=false;i.changed();}
void EditorForm::topology(s::Topology topology,std::string display){auto& i=*impl_;i.owner();if(i.closed)return;if(i.content)i.content->erase();if(i.binding)i.binding->erase();if(i.creation)i.creation->erase();if(i.layout_form)i.layout_form->erase();if(i.visibility)i.visibility->erase();i.gesture.reset();i.topology=std::move(topology);i.display=std::move(display);i.preview();i.sync(!i.fields_dirty);}
recovery::DataAttachment EditorForm::attach(const std::string& p,const protocol::TelemetryBinding& b,std::uint64_t now){auto& i=*impl_;i.owner();return i.surface?i.surface->attach(p,b,now):recovery::DataAttachment{recovery::DataCode::closed};}
recovery::DataResult EditorForm::receive(const std::string& p,std::uint64_t t,std::uint64_t r,std::string_view bytes,std::uint64_t now,const model::Tick& tick){auto& i=*impl_;i.owner();if(!i.surface)return {recovery::DataCode::closed};const auto result=i.surface->receive(p,t,r,bytes,now,tick);i.ticks[p]=tick;return result;}
recovery::DataCode EditorForm::heartbeat(const std::string& p,std::uint64_t t,std::uint64_t r,std::uint64_t q,std::uint64_t now){auto& i=*impl_;i.owner();return i.surface?i.surface->heartbeat(p,t,r,q,now):recovery::DataCode::closed;}
recovery::DataCode EditorForm::disconnect(const std::string& p,std::uint64_t t,std::uint64_t r,std::uint64_t now){auto& i=*impl_;i.owner();return i.surface?i.surface->disconnect(p,t,r,now):recovery::DataCode::closed;}
void EditorForm::close(){impl_->owner();impl_->shut();}
}
