#include "editor_form.hpp"
#include "private_text.hpp"
#include <gtk/gtk.h>
#include <algorithm>
#include <cmath>
#include <locale>
#include <regex>
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
}
struct EditorForm::Impl {
    EditorDraft draft;c::Authority authority;c::Policy current;Json settings;std::optional<SettingsResources> resources;s::Topology topology;std::string display,worker;
    std::vector<v::SurfaceProvider> providers;std::unique_ptr<v::SceneSurface> surface;std::map<std::string,model::Tick> ticks;
    Actions actions;std::thread::id thread=std::this_thread::get_id();bool closed=false,updating=false,dispatching=false,fields_dirty=false,drawing=false;std::string error;
    GtkWidget *root=nullptr,*canvas=nullptr,*tree=nullptr,*status=nullptr;GtkListStore* model=nullptr;std::vector<GtkWidget*> owned;
    std::map<std::string,GtkWidget*> buttons,fields;std::vector<s::Node> nodes;
    struct Gesture {double x,y,dx=0,dy=0;bool resize=false;std::vector<s::Node> nodes;};std::optional<Gesture> gesture;
    guint timer=0;
    Impl(c::Authority a,c::Policy p,c::Authored value,std::string epoch,SettingsResources r,s::Topology t,std::string d,std::vector<v::SurfaceProvider> ps,std::string w,Actions callbacks)
      :draft(a,p,value,std::move(epoch),r),authority(std::move(a)),current(std::move(p)),settings(std::move(value.settings)),resources(std::move(r)),topology(std::move(t)),display(std::move(d)),worker(std::move(w)),providers(std::move(ps)),actions(std::move(callbacks)){}
    void owner()const{if(thread!=std::this_thread::get_id()||dispatching)throw std::logic_error("editor.owner");}
    std::uint64_t now()const{return static_cast<std::uint64_t>(g_get_monotonic_time()/1000);}
    GtkWidget* own(GtkWidget* w){g_object_ref_sink(w);owned.push_back(w);return w;}
    GtkWidget* label(const char* value){auto* w=own(gtk_label_new(value));gtk_label_set_xalign(GTK_LABEL(w),0);return w;}
    const s::Display& viewport()const{for(const auto& d:topology.displays)if(d.id==display)return d;for(const auto& d:topology.displays)if(d.id==topology.fallback)return d;throw protocol::Error("editor.display");}
    bool editing()const{return draft.available()&&!draft.active_request()&&draft.state()!=DraftState::conflict;}
    void ready()const{need(editing(),"editor.unavailable");need(!fields_dirty,"editor.properties_pending");}
    bool clear(){nodes.clear();if(canvas){atk_object_set_name(gtk_widget_get_accessible(canvas),"");if(!drawing)gtk_widget_queue_draw(canvas);}return true;}
    void stop_preview(){gesture.reset();ticks.clear();if(surface)surface->close();clear();}
    void resolve_nodes(){
        // Input can arrive again before GTK's next draw. Resolve with the same
        // renderer now so a valid queued key is not mistaken for a hidden variant.
        if(surface&&draft.available())surface->paint(now(),ticks,[this](auto,const v::SurfaceFrame* frame){if(frame)nodes=frame->layout.nodes;});
    }
    void preview(){
        if(!draft.available()||!resources){settings=nullptr;resources.reset();stop_preview();return;}
        settings["revision"]=(*draft.scene())["revision"];
        v::SurfaceConfig cfg;cfg.authored={settings,*draft.scene()};cfg.resources=resources->catalog->resources(resources->selection,cfg.authored);cfg.topology=topology;cfg.capabilities=resources->capabilities;
        if(surface&&surface->status().code==v::SurfaceCode::closed){need(surface->poll_image_jobs(),"editor.renderer_stopping");surface.reset();}
        if(surface)surface->replace(std::move(cfg),now());
        else surface=std::make_unique<v::SceneSurface>(authority,current,std::move(cfg),providers,[this]{return clear();},worker,v::SurfaceAudience::inspector);
        resolve_nodes();gtk_widget_queue_draw(canvas);
    }
    const s::Node* node(const std::string& id)const{for(const auto& n:nodes)if(n.id==id&&n.display==viewport().id)return &n;return nullptr;}
    bool fixed(const std::string& id)const{if(!draft.scene())return false;const auto* n=node(id);return n&&n->variant==-1&&authored_widget(*draft.scene(),id)["layout"]["base"]["kind"]=="fixed";}
    void message(const std::string& value){gtk_label_set_text(GTK_LABEL(status),value.c_str());}
    void sync(bool values=false){
        updating=true;if(values||!draft.available())fields_dirty=false;
        const bool enabled=editing()&&!fields_dirty;const bool one=draft.selection().size()==1;
        const Json* selected=one&&draft.scene()?&authored_widget(*draft.scene(),draft.selection()[0]):nullptr;
        if(values||!draft.available()){
            fields_dirty=false;
            for(auto& row:fields){std::string value;
                if(selected){if(row.first=="title")value=(*selected)["title"];
                    else if(row.first=="body"){if((*selected)["kind"]=="text")value=selected->contains("content")?(*selected)["content"]["body"].get<std::string>():selected->at("title").get<std::string>();}
                    else if((*selected)["layout"]["base"]["kind"]=="fixed")value=(*selected)["layout"]["base"][row.first].dump();}
                text(row.second,value);
            }
        }
        for(auto& row:fields)gtk_widget_set_sensitive(row.second,editing()&&selected&&(row.first=="title"||(row.first=="body"&&(*selected)["kind"]=="text")||((row.first!="body")&&fixed(draft.selection()[0]))));
        for(auto& row:buttons)gtk_widget_set_sensitive(row.second,enabled);
        gtk_widget_set_sensitive(buttons["undo"],enabled&&draft.undo_count());gtk_widget_set_sensitive(buttons["redo"],enabled&&draft.redo_count());
        gtk_widget_set_sensitive(buttons["apply"],!fields_dirty&&draft.may_submit("commit"));gtk_widget_set_sensitive(buttons["cancel"],editing());
        gtk_widget_set_sensitive(buttons["cancel-request"],draft.available()&&draft.active_request().has_value());gtk_widget_set_sensitive(buttons["reload"],!closed&&!draft.active_request());
        gtk_widget_set_sensitive(buttons["properties"],editing()&&selected&&fields_dirty);gtk_widget_set_sensitive(buttons["revert-fields"],editing()&&fields_dirty);
        gtk_widget_set_sensitive(buttons["duplicate"],enabled&&!draft.selection().empty());gtk_widget_set_sensitive(buttons["delete"],enabled&&!draft.selection().empty());
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
        message(value);updating=false;
    }
    void list(){
        updating=true;GtkTreeIter it;if(gtk_tree_model_get_iter_first(GTK_TREE_MODEL(model),&it))do{gtk_list_store_set(model,&it,0,"",1,"",-1);}while(gtk_tree_model_iter_next(GTK_TREE_MODEL(model),&it));
        gtk_list_store_clear(model);auto* selection=gtk_tree_view_get_selection(GTK_TREE_VIEW(tree));
        if(draft.scene())for(const auto& w:(*draft.scene())["widgets"]){const auto id=w["id"].get<std::string>(),title=w["title"].get<std::string>();gtk_list_store_append(model,&it);gtk_list_store_set(model,&it,0,id.c_str(),1,title.c_str(),-1);
            if(std::find(draft.selection().begin(),draft.selection().end(),id)!=draft.selection().end())gtk_tree_selection_select_iter(selection,&it);}
        updating=false;
    }
    void changed(){gesture.reset();error.clear();preview();list();sync(true);}
    void selected(std::vector<std::string> ids){ready();draft.select(std::move(ids));list();sync(true);gtk_widget_queue_draw(canvas);}
    void execute(const std::vector<SceneEdit>& edits){ready();draft.execute(edits);changed();}
    void properties(){
        need(editing()&&draft.selection().size()==1,"editor.selection");const auto id=draft.selection()[0];const auto& w=authored_widget(*draft.scene(),id);
        std::vector<SceneEdit> edits{WidgetPropertyEdit{id,WidgetProperty::title,text(fields["title"])}};
        if(w["kind"]=="text"&&w.contains("content"))edits.push_back(WidgetContentEdit{id,w["bindings"],{{"body",text(fields["body"])}}});
        if(fixed(id)){auto layout=w["layout"];for(const char* key:{"x","y","width","height"})layout["base"][key]=number(text(fields[key]));edits.push_back(WidgetPropertyEdit{id,WidgetProperty::layout,std::move(layout)});}
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
        if((*draft.scene())["schema_version"]=="0.3.0")w["content"]={{"body","Text"}};
        execute({InsertWidget{w,std::nullopt,(*draft.scene())["roots"].size()}});selected({id});
    }
    void dispatch(const std::function<void()>& f){dispatching=true;try{f();dispatching=false;}catch(...){dispatching=false;throw;}}
    void submit(){ready();const auto q=draft.begin("commit",actions.request_id());sync();if(q)try{dispatch([&]{actions.submit(*q);});}catch(...){draft.disconnected();sync();}}
    void command(const std::string& id){
        if(id=="properties")properties();else if(id=="revert-fields"){fields_dirty=false;error.clear();sync(true);}
        else if(id=="apply")submit();else if(id=="reload")dispatch(actions.reload);
        else if(id=="cancel-request"){const auto q=draft.cancel_request();if(q)try{dispatch([&]{actions.cancel(*q);});}catch(...){draft.disconnected();sync();}}
        else if(id=="cancel"){draft.discard();shut();dispatch(actions.exit);}
        else if(id=="add")add();else if(id=="duplicate")duplicate();else if(id=="delete")execute({RemoveWidgets{draft.selection()}});
        else {ready();if(id=="undo")draft.undo();else if(id=="redo")draft.redo();changed();}
    }
    void point(double x,double y,bool shift){
        ready();gtk_widget_grab_focus(canvas);const auto& d=viewport();const double factor=gtk_widget_get_scale_factor(canvas);x=x*factor+d.pixel_x;y=y*factor+d.pixel_y;
        const s::Node* hit=nullptr;for(auto i=nodes.rbegin();i!=nodes.rend();++i)if(i->display==d.id&&contains(i->pixels,x,y)){hit=&*i;break;}
        if(!hit){selected({});return;}const auto id=hit->id;auto ids=draft.selection();const auto found=std::find(ids.begin(),ids.end(),id);
        if(shift){if(found==ids.end())ids.push_back(id);else ids.erase(found);selected(std::move(ids));return;}
        if(found==ids.end())selected({id});
        Gesture g;g.x=x;g.y=y;
        for(const auto& selected_id:draft.selection()){need(fixed(selected_id),"editor.fixed_variant");g.nodes.push_back(*node(selected_id));}
        g.resize=g.nodes.size()==1&&x>=g.nodes[0].pixels.x+g.nodes[0].pixels.width-8&&y>=g.nodes[0].pixels.y+g.nodes[0].pixels.height-8;
        gesture=std::move(g);gtk_widget_queue_draw(canvas);
    }
    void motion(double x,double y){if(!gesture)return;const auto& d=viewport();const double factor=gtk_widget_get_scale_factor(canvas);gesture->dx=x*factor+d.pixel_x-gesture->x;gesture->dy=y*factor+d.pixel_y-gesture->y;gtk_widget_queue_draw(canvas);}
    void release(double x,double y){if(!gesture)return;motion(x,y);const auto g=*gesture;gesture.reset();const auto& d=viewport();const double scale=static_cast<double>(d.scale_denominator)/d.scale_numerator;
        if(g.dx==0&&g.dy==0){gtk_widget_queue_draw(canvas);return;}
        if(g.resize){const auto& base=authored_widget(*draft.scene(),g.nodes[0].id)["layout"]["base"];execute({ResizeWidget{g.nodes[0].id,base["width"].get<double>()+g.dx*scale,base["height"].get<double>()+g.dy*scale}});}
        else execute({MoveWidgets{draft.selection(),g.dx*scale,g.dy*scale}});
    }
    bool key(GdkEventKey* e){
        if(e->keyval==GDK_KEY_Escape){gesture.reset();gtk_widget_queue_draw(canvas);return true;}
        if((e->state&GDK_CONTROL_MASK)&&(e->keyval==GDK_KEY_z||e->keyval==GDK_KEY_Z)){command(e->state&GDK_SHIFT_MASK?"redo":"undo");return true;}
        if(e->keyval==GDK_KEY_Delete){command("delete");return true;}
        double x=0,y=0;const double amount=e->state&GDK_SHIFT_MASK?10:1;
        if(e->keyval==GDK_KEY_Left)x=-amount;else if(e->keyval==GDK_KEY_Right)x=amount;else if(e->keyval==GDK_KEY_Up)y=-amount;else if(e->keyval==GDK_KEY_Down)y=amount;else return false;
        ready();need(!draft.selection().empty(),"editor.selection");for(const auto& id:draft.selection())need(fixed(id),"editor.fixed_variant");
        if(e->state&GDK_MOD1_MASK){need(draft.selection().size()==1,"editor.selection");const auto id=draft.selection()[0];const auto& b=authored_widget(*draft.scene(),id)["layout"]["base"];execute({ResizeWidget{id,b["width"].get<double>()+x,b["height"].get<double>()+y}});}
        else execute({MoveWidgets{draft.selection(),x,y}});
        return true;
    }
    void draw(cairo_t* cr){
        struct Drawing {bool& flag;explicit Drawing(bool& f):flag(f){flag=true;}~Drawing(){flag=false;}} guard(drawing);
        cairo_set_source_rgb(cr,0,0,0);cairo_paint(cr);if(!surface||!draft.available())return;
        const auto d=viewport();const double factor=gtk_widget_get_scale_factor(canvas);cairo_save(cr);cairo_scale(cr,1/factor,1/factor);
        surface->paint(now(),ticks,[&](auto,const v::SurfaceFrame* frame){
            if(!frame)return;
            nodes=frame->layout.nodes;std::string description;
            for(const auto& w:frame->widgets){if(description.size()+w.accessible.size()>65536){description+="\nMore content in inspector";break;}description+=w.accessible+"\n";}
            atk_object_set_name(gtk_widget_get_accessible(canvas),description.c_str());
            if(!gesture)for(const auto& image:frame->displays)if(image.display==d.id){
                std::vector<std::uint32_t> argb(static_cast<std::size_t>(image.width)*image.height);for(std::size_t n=0;n<argb.size();++n)argb[n]=(static_cast<std::uint32_t>(image.rgba[n*4+3])<<24)|(static_cast<std::uint32_t>(image.rgba[n*4])<<16)|(static_cast<std::uint32_t>(image.rgba[n*4+1])<<8)|image.rgba[n*4+2];
                auto* bitmap=cairo_image_surface_create_for_data(reinterpret_cast<unsigned char*>(argb.data()),CAIRO_FORMAT_ARGB32,static_cast<int>(image.width),static_cast<int>(image.height),static_cast<int>(image.width*4));cairo_set_source_surface(cr,bitmap,0,0);cairo_paint(cr);cairo_surface_destroy(bitmap);
            }
            cairo_set_source_rgb(cr,0,0.6,1);cairo_set_line_width(cr,2);
            const auto selected_nodes=gesture?gesture->nodes:nodes;
            for(const auto& n:selected_nodes)if(n.display==d.id&&std::find(draft.selection().begin(),draft.selection().end(),n.id)!=draft.selection().end()){
                double x=n.pixels.x-d.pixel_x,y=n.pixels.y-d.pixel_y,w=n.pixels.width,h=n.pixels.height;
                if(gesture){if(gesture->resize){w+=gesture->dx;h+=gesture->dy;}else{x+=gesture->dx;y+=gesture->dy;}}
                cairo_rectangle(cr,x+1,y+1,w-2,h-2);cairo_stroke(cr);if(draft.selection().size()==1){cairo_rectangle(cr,x+w-8,y+h-8,8,8);cairo_fill(cr);}
            }
        });cairo_restore(cr);sync();
    }
    void shut(){if(closed)return;closed=true;draft.close();fields_dirty=false;settings=nullptr;resources.reset();stop_preview();if(tree){list();sync(true);}}
    template<class F> void event(F f)noexcept{try{if(!closed)f();}catch(const protocol::Error& e){gesture.reset();error=std::string(e.what())=="editor.number"?"Enter a number using digits and an optional decimal point.":"This edit could not be applied. Check the selection and property values.";message(error);gtk_widget_queue_draw(canvas);}catch(...){try{shut();}catch(...){}}}
    ~Impl(){if(timer)g_source_remove(timer);try{shut();}catch(...){}surface.reset();if(root)gtk_widget_destroy(root);for(auto i=owned.rbegin();i!=owned.rend();++i)g_object_unref(*i);if(model)g_object_unref(model);}
};
EditorForm::EditorForm(c::Authority a,c::Policy p,c::Authored value,std::string epoch,SettingsResources resources,s::Topology topology,std::string display,std::vector<v::SurfaceProvider> providers,std::string worker,Actions actions)
 :impl_(std::make_unique<Impl>(std::move(a),std::move(p),std::move(value),std::move(epoch),std::move(resources),std::move(topology),std::move(display),std::move(providers),std::move(worker),std::move(actions))){
    auto& i=*impl_;need(i.actions.request_id&&i.actions.widget_id&&i.actions.submit&&i.actions.cancel&&i.actions.reload&&i.actions.exit,"editor.actions");
    i.root=i.own(gtk_box_new(GTK_ORIENTATION_VERTICAL,4));auto* top=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,4);gtk_box_pack_start(GTK_BOX(i.root),top,FALSE,FALSE,0);
    auto button=[&](GtkWidget* box,const char* id,const char* label){auto* w=i.own(gtk_button_new_with_label(label));i.buttons[id]=w;accessible(w,label,std::string("editor.")+id);g_object_set_data_full(G_OBJECT(w),"editor-action",g_strdup(id),g_free);gtk_box_pack_start(GTK_BOX(box),w,FALSE,FALSE,0);
        g_signal_connect(w,"clicked",G_CALLBACK(+[](GtkWidget* w,gpointer p){auto& o=*static_cast<Impl*>(p);o.event([&]{o.command(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"editor-action")));});}),&i);};
    for(const auto& b:std::vector<std::pair<const char*,const char*>>{{"undo","Undo"},{"redo","Redo"},{"apply","Apply"},{"cancel","Cancel session"},{"cancel-request","Cancel request"},{"reload","Reload"}})button(top,b.first,b.second);
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
    auto* bottom=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,4);gtk_box_pack_start(GTK_BOX(i.root),bottom,FALSE,FALSE,0);button(bottom,"add","Add text");button(bottom,"duplicate","Duplicate");button(bottom,"delete","Delete");
    i.status=i.label("");accessible(i.status,"","editor.status");gtk_label_set_line_wrap(GTK_LABEL(i.status),TRUE);gtk_box_pack_start(GTK_BOX(i.root),i.status,FALSE,FALSE,0);
    g_signal_connect(selection,"changed",G_CALLBACK(+[](GtkTreeSelection* selection,gpointer p){auto& o=*static_cast<Impl*>(p);if(o.updating)return;o.event([&]{std::vector<std::string> ids;GtkTreeModel* model=nullptr;auto* rows=gtk_tree_selection_get_selected_rows(selection,&model);
        for(auto* row=rows;row;row=row->next){GtkTreeIter it;if(gtk_tree_model_get_iter(model,&it,static_cast<GtkTreePath*>(row->data))){gchar* id=nullptr;gtk_tree_model_get(model,&it,0,&id,-1);ids.emplace_back(id);g_free(id);}}g_list_free_full(rows,reinterpret_cast<GDestroyNotify>(gtk_tree_path_free));o.selected(std::move(ids));});}),&i);
    g_signal_connect(i.canvas,"draw",G_CALLBACK(+[](GtkWidget*,cairo_t* cr,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);if(o.closed){cairo_set_source_rgb(cr,0,0,0);cairo_paint(cr);}else o.event([&]{o.draw(cr);});return TRUE;}),&i);
    g_signal_connect(i.canvas,"button-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventButton* e,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);if(e->button!=1)return FALSE;o.event([&]{o.point(e->x,e->y,e->state&GDK_SHIFT_MASK);});return TRUE;}),&i);
    g_signal_connect(i.canvas,"motion-notify-event",G_CALLBACK(+[](GtkWidget*,GdkEventMotion* e,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.event([&]{o.motion(e->x,e->y);});return TRUE;}),&i);
    g_signal_connect(i.canvas,"button-release-event",G_CALLBACK(+[](GtkWidget*,GdkEventButton* e,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);if(e->button!=1)return FALSE;o.event([&]{o.release(e->x,e->y);});return TRUE;}),&i);
    g_signal_connect(i.canvas,"key-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventKey* e,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);bool handled=false;o.event([&]{handled=o.key(e);});return handled;}),&i);
    g_signal_connect(i.canvas,"focus-out-event",G_CALLBACK(+[](GtkWidget*,GdkEventFocus*,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.gesture.reset();gtk_widget_queue_draw(o.canvas);return FALSE;}),&i);
    g_signal_connect(i.root,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer p){static_cast<Impl*>(p)->shut();}),&i);
    i.preview();i.list();i.sync(true);i.timer=g_timeout_add(40,+[](gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);try{if(o.surface)o.surface->poll_image_jobs();if(!o.closed)gtk_widget_queue_draw(o.canvas);}catch(...){o.shut();}return G_SOURCE_CONTINUE;},&i);
}
EditorForm::~EditorForm()=default;
GtkWidget* EditorForm::widget()const{impl_->owner();return impl_->root;}
void EditorForm::complete(std::uint64_t ticket,const Json& result){auto& i=*impl_;i.owner();if(i.closed)return;try{if(i.draft.complete(ticket,result))i.changed();}catch(...){i.sync();throw;}}
void EditorForm::reconciled(std::uint64_t ticket,const std::string& query,const std::string& epoch,const Json& result){auto& i=*impl_;i.owner();if(i.closed)return;try{if(i.draft.reconciled(ticket,query,epoch,result))i.changed();}catch(...){i.sync();throw;}}
void EditorForm::disconnected(){auto& i=*impl_;i.owner();if(i.closed)return;i.draft.disconnected();i.gesture.reset();i.sync();}
void EditorForm::policy(c::Policy policy){auto& i=*impl_;i.owner();if(i.closed)return;i.gesture.reset();i.draft.policy(policy);i.current=std::move(policy);if(i.surface)i.surface->policy(i.current,i.now());
    if(!i.draft.available()){i.settings=nullptr;i.resources.reset();i.stop_preview();i.list();}else i.resolve_nodes();i.sync();}
void EditorForm::reload(c::Authored value,std::string epoch,SettingsResources resources){auto& i=*impl_;i.owner();if(i.closed)return;
    if(i.surface&&i.surface->status().code==v::SurfaceCode::closed)need(i.surface->poll_image_jobs(),"editor.renderer_stopping");
    i.draft.reload(value,std::move(epoch),resources);i.settings=std::move(value.settings);i.resources=std::move(resources);i.fields_dirty=false;i.changed();}
void EditorForm::topology(s::Topology topology,std::string display){auto& i=*impl_;i.owner();if(i.closed)return;i.gesture.reset();i.topology=std::move(topology);i.display=std::move(display);i.preview();i.sync();}
recovery::DataAttachment EditorForm::attach(const std::string& p,const protocol::TelemetryBinding& b,std::uint64_t now){auto& i=*impl_;i.owner();return i.surface?i.surface->attach(p,b,now):recovery::DataAttachment{recovery::DataCode::closed};}
recovery::DataResult EditorForm::receive(const std::string& p,std::uint64_t t,std::uint64_t r,std::string_view bytes,std::uint64_t now,const model::Tick& tick){auto& i=*impl_;i.owner();if(!i.surface)return {recovery::DataCode::closed};const auto result=i.surface->receive(p,t,r,bytes,now,tick);i.ticks[p]=tick;return result;}
recovery::DataCode EditorForm::heartbeat(const std::string& p,std::uint64_t t,std::uint64_t r,std::uint64_t q,std::uint64_t now){auto& i=*impl_;i.owner();return i.surface?i.surface->heartbeat(p,t,r,q,now):recovery::DataCode::closed;}
recovery::DataCode EditorForm::disconnect(const std::string& p,std::uint64_t t,std::uint64_t r,std::uint64_t now){auto& i=*impl_;i.owner();return i.surface?i.surface->disconnect(p,t,r,now):recovery::DataCode::closed;}
void EditorForm::close(){impl_->owner();impl_->shut();}
}
