#include "editor_layout_form.hpp"
#include "private_text.hpp"
#include <gtk/gtk.h>
#include <algorithm>
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
std::string text(GtkWidget* w){GtkTextIter a,z;auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(w));gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string out=raw;g_free(raw);return out;}
void text(GtkWidget* w,const std::string& value){gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),value.c_str(),static_cast<gint>(value.size()));}
void name(GtkWidget* w,const char* label,const std::string& id){atk_object_set_name(gtk_widget_get_accessible(w),label);atk_object_set_description(gtk_widget_get_accessible(w),("editor.layout."+id).c_str());}
void wipe(GtkWidget* w){auto* m=gtk_combo_box_get_model(GTK_COMBO_BOX(w));GtkTreeIter i;if(gtk_tree_model_get_iter_first(m,&i))do{gtk_list_store_set(GTK_LIST_STORE(m),&i,0,"",-1);}while(gtk_tree_model_iter_next(m,&i));gtk_combo_box_text_remove_all(GTK_COMBO_BOX_TEXT(w));}
void visible(GtkWidget* w,bool show){gtk_widget_set_no_show_all(w,!show);if(show)gtk_widget_show_all(w);else gtk_widget_hide(w);}
}
struct EditorLayoutForm::Impl {
    GtkWidget *parent,*window,*box,*notebook,*error,*add_button,*remove_button,*variant_actions,*note,*assignment_note,*set_button,*cancel_button;
    std::map<std::string,GtkWidget*> fields,combos,rows;
    Json original;std::string id,kind,mode="layout";std::vector<std::string> wrap_ids;LayoutInput input;std::size_t selected=0;bool active=false,updating=false;
    std::function<bool(const std::vector<SceneEdit>&)> apply;std::function<void(bool)> finished;std::function<void()> failed;
    void row(GtkWidget* into,const char* label,GtkWidget* w,const char* key){auto* b=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);auto* l=gtk_label_new(label);gtk_label_set_xalign(GTK_LABEL(l),0);gtk_widget_set_size_request(l,170,-1);gtk_box_pack_start(GTK_BOX(b),l,FALSE,FALSE,0);gtk_box_pack_start(GTK_BOX(b),w,TRUE,TRUE,0);gtk_box_pack_start(GTK_BOX(into),b,FALSE,FALSE,0);rows[key]=b;}
    void field(GtkWidget* into,const char* key,const char* label,unsigned limit=64){auto* w=private_text(limit,false);fields[key]=w;name(w,label,key);gtk_widget_set_size_request(w,230,25);row(into,label,w,key);}
    void combo(GtkWidget* into,const char* key,const char* label){auto* w=gtk_combo_box_text_new();combos[key]=w;name(w,label,key);row(into,label,w,key);}
    GtkWidget* button(GtkWidget* into,const char* key,const char* label){auto* w=gtk_button_new_with_label(label);name(w,label,key);gtk_box_pack_start(GTK_BOX(into),w,FALSE,FALSE,0);g_object_set_data_full(G_OBJECT(w),"layout-action",g_strdup(key),g_free);g_signal_connect(w,"clicked",G_CALLBACK(+[](GtkWidget* w,gpointer p){auto& o=*static_cast<Impl*>(p);o.event([&]{o.action(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"layout-action")));});}),this);return w;}
    GtkWidget* page(const char* label){auto* w=gtk_box_new(GTK_ORIENTATION_VERTICAL,5);gtk_container_set_border_width(GTK_CONTAINER(w),8);gtk_notebook_append_page(GTK_NOTEBOOK(notebook),w,gtk_label_new(label));return w;}
    Impl(GtkWidget* p,std::function<bool(const std::vector<SceneEdit>&)> a,std::function<void(bool)> f,std::function<void()> e):parent(p),apply(std::move(a)),finished(std::move(f)),failed(std::move(e)){
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);g_object_ref_sink(window);gtk_window_set_title(GTK_WINDOW(window),"SysPane Layout");gtk_window_set_modal(GTK_WINDOW(window),TRUE);gtk_window_set_resizable(GTK_WINDOW(window),FALSE);box=gtk_box_new(GTK_ORIENTATION_VERTICAL,6);gtk_container_set_border_width(GTK_CONTAINER(box),10);gtk_container_add(GTK_CONTAINER(window),box);
        note=gtk_label_new("");name(note,"","note");gtk_label_set_line_wrap(GTK_LABEL(note),TRUE);gtk_label_set_max_width_chars(GTK_LABEL(note),56);gtk_box_pack_start(GTK_BOX(box),note,FALSE,FALSE,0);field(box,"title","Container title",512);
        combo(box,"variant","Layout variant");variant_actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(box),variant_actions,FALSE,FALSE,0);add_button=button(variant_actions,"add","Add breakpoint");remove_button=button(variant_actions,"remove","Remove breakpoint");field(box,"threshold","Minimum display width");combo(box,"kind","Layout kind");
        notebook=gtk_notebook_new();gtk_box_pack_start(GTK_BOX(box),notebook,TRUE,TRUE,0);auto* geometry=page("Geometry");
        for(const char* key:{"x","y","width","height","width_min","width_preferred","width_max","height_min","height_preferred","height_max","gap_dip","columns"})field(geometry,key,key);
        for(const char* key:{"anchor","axis","overflow"})combo(geometry,key,key);
        auto* assignment=page("Assignment");combo(assignment,"display_kind","Display identifier kind");field(assignment,"display_value","Display ID / role",256);combo(assignment,"priority","Priority");field(assignment,"sibling","Sibling position (from 0)");
        assignment_note=gtk_label_new("Changing display moves the entire top-level group and its descendants. Missing displays keep their assignment.");gtk_label_set_line_wrap(GTK_LABEL(assignment_note),TRUE);gtk_label_set_max_width_chars(GTK_LABEL(assignment_note),56);gtk_box_pack_start(GTK_BOX(assignment),assignment_note,FALSE,FALSE,0);
        error=gtk_label_new("");name(error,"","error");gtk_label_set_line_wrap(GTK_LABEL(error),TRUE);gtk_label_set_max_width_chars(GTK_LABEL(error),60);gtk_box_pack_start(GTK_BOX(box),error,FALSE,FALSE,0);
        auto* actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(box),actions,FALSE,FALSE,0);set_button=button(actions,"set","Set layout");cancel_button=button(actions,"cancel","Cancel layout");
        g_signal_connect(combos.at("kind"),"changed",G_CALLBACK(+[](GtkComboBox*,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.save();o.kind=o.chosen("kind");o.input.variants.at(o.selected).kind=o.kind;o.load();});}),this);
        g_signal_connect(combos.at("variant"),"changed",G_CALLBACK(+[](GtkComboBox*,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.save();const int n=gtk_combo_box_get_active(GTK_COMBO_BOX(o.combos.at("variant")));need(n>=0&&static_cast<std::size_t>(n)<o.input.variants.size(),"editor.layout_variant");o.selected=static_cast<std::size_t>(n);o.load();});}),this);
        g_signal_connect(window,"delete-event",G_CALLBACK(+[](GtkWidget*,GdkEvent*,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.event([&]{o.finish();});return TRUE;}),this);
        g_signal_connect(window,"key-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventKey* e,gpointer p)->gboolean{if(e->keyval!=GDK_KEY_Escape)return FALSE;auto& o=*static_cast<Impl*>(p);o.event([&]{o.finish();});return TRUE;}),this);
    }
    void options(const char* key,const std::vector<std::string>& values,const std::string& value){wipe(combos.at(key));int index=-1;for(std::size_t n=0;n<values.size();++n){gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combos.at(key)),values[n].c_str());if(values[n]==value)index=static_cast<int>(n);}gtk_combo_box_set_active(GTK_COMBO_BOX(combos.at(key)),index);}
    std::string chosen(const char* key)const{auto* raw=gtk_combo_box_text_get_active_text(GTK_COMBO_BOX_TEXT(combos.at(key)));need(raw,"editor.layout_choice");std::string value=raw;g_free(raw);return value;}
    void save(){if(kind.empty())return;auto& f=input.variants.at(selected).by_kind.at(kind);for(auto& row:f)row.second=fields.count(row.first)?text(fields.at(row.first)):chosen(row.first.c_str());
        if(selected)input.thresholds.at(selected-1)=text(fields.at("threshold"));
        input.display_kind=chosen("display_kind");input.display_value=text(fields.at("display_value"));input.priority=chosen("priority");input.sibling=text(fields.at("sibling"));}
    void load(){updating=true;kind=input.variants.at(selected).kind;const auto& f=input.variants.at(selected).by_kind.at(kind);
        const auto& w=*std::find_if(original.at("widgets").begin(),original.at("widgets").end(),[&](const Json& v){return v.at("id")==id;});
        options("kind",w.at("kind")=="group"?std::vector<std::string>{"fixed","canvas","stack","grid"}:std::vector<std::string>{"fixed","flow"},kind);
        std::vector<std::string> variants{"Base"};for(std::size_t n=0;n<input.thresholds.size();++n)variants.push_back("Breakpoint "+std::to_string(n+1));options("variant",variants,variants.at(selected));
        options("display_kind",{"local_id","role"},input.display_kind);options("priority",{"essential","normal","secondary"},input.priority);
        text(fields.at("threshold"),selected?input.thresholds.at(selected-1):"");gtk_widget_set_sensitive(fields.at("threshold"),selected!=0);text(fields.at("display_value"),input.display_value);text(fields.at("sibling"),input.sibling);
        for(const auto& key:std::vector<std::string>{"x","y","width","height","width_min","width_preferred","width_max","height_min","height_preferred","height_max","gap_dip","columns","anchor","axis","overflow"}){
            const auto found=f.find(key);const bool show=found!=f.end();auto* row=rows.at(key);gtk_widget_set_no_show_all(row,!show);if(show)gtk_widget_show_all(row);else gtk_widget_hide(row);
            if(fields.count(key))text(fields.at(key),show?found->second:"");
            else if(show)options(key.c_str(),key=="anchor"?std::vector<std::string>{"start","center","end","stretch"}:key=="axis"?std::vector<std::string>{"horizontal","vertical"}:std::vector<std::string>{"scroll","diagnose"},found->second);else wipe(combos.at(key));
        }
        gtk_widget_set_sensitive(add_button,input.variants.size()<9);gtk_widget_set_sensitive(remove_button,selected!=0);
        visible(rows.at("title"),mode=="wrap");visible(note,mode!="layout");
        for(auto* w:{rows.at("variant"),variant_actions,rows.at("threshold"),rows.at("kind"),notebook})visible(w,mode!="unwrap");
        for(auto* w:{rows.at("display_kind"),rows.at("display_value"),rows.at("sibling"),assignment_note})visible(w,mode=="layout");
        gtk_label_set_text(GTK_LABEL(note),mode=="wrap"?"Keep each child's layout rules and reflow in a new container. Positions, sizes and clipping may change.":mode=="unwrap"?"Remove this container and keep each child's layout rules in the enclosing parent. Children reflow; removing clipping may reveal content.":"");
        const char* label=mode=="wrap"?"Wrap and reflow":mode=="unwrap"?"Unwrap and reflow":"Set layout";gtk_button_set_label(GTK_BUTTON(set_button),label);name(set_button,label,"set");
        label=mode=="layout"?"Cancel layout":"Cancel";gtk_button_set_label(GTK_BUTTON(cancel_button),label);name(cancel_button,label,"cancel");
        gtk_label_set_text(GTK_LABEL(error),"");updating=false;
    }
    void action(const std::string& value){if(value=="cancel"){finish();return;}if(mode=="unwrap"){need(value=="set","editor.container_action");const bool changed=apply({UnwrapWidget{id}});finish(changed);return;}save();if(value=="set"){const bool changed=mode=="wrap"?apply({WrapWidgets{wrap_ids,id,text(fields.at("title")),layout_value(input,true),input.priority}}):apply(layout_edits(original,id,input));finish(changed);}
        else if(value=="add"){need(input.variants.size()<9,"editor.layout_variants");const auto copy=input.variants.at(selected);input.variants.push_back(copy);input.thresholds.push_back("");selected=input.variants.size()-1;load();}
        else if(value=="remove"){need(selected>0,"editor.layout_variant");input.variants.erase(input.variants.begin()+static_cast<std::ptrdiff_t>(selected));input.thresholds.erase(input.thresholds.begin()+static_cast<std::ptrdiff_t>(selected-1));--selected;load();}}
    void open(const Json& scene,const std::string& target,const std::string& operation="layout",const std::vector<std::string>& ids={}){erase();try{original=scene;id=target;mode=operation;wrap_ids=ids;input=layout_input(scene,id);text(fields.at("title"),mode=="wrap"?"Container":"");selected=0;load();gtk_window_set_title(GTK_WINDOW(window),mode=="layout"?"SysPane Layout":mode=="wrap"?"Wrap in container":"Unwrap container");gtk_notebook_set_current_page(GTK_NOTEBOOK(notebook),0);auto* top=gtk_widget_get_toplevel(parent);need(GTK_IS_WINDOW(top),"editor.layout_parent");gtk_window_set_transient_for(GTK_WINDOW(window),GTK_WINDOW(top));gtk_window_set_position(GTK_WINDOW(window),GTK_WIN_POS_CENTER_ON_PARENT);active=true;gtk_widget_show_all(window);gtk_window_present(GTK_WINDOW(window));}catch(...){erase();throw;}}
    void wrap(const Json& scene,const std::vector<std::string>& ids,const std::string& fresh){
        need(!ids.empty(),"editor.targets");const auto& widgets=scene.at("widgets");const auto at=std::find_if(widgets.begin(),widgets.end(),[&](const Json& w){return w.at("id")==ids[0];});need(at!=widgets.end(),"editor.target");
        Json seed={{"roots",Json::array({fresh})},{"widgets",Json::array({{{"id",fresh},{"kind","group"},{"display",at->at("display")},{"priority","normal"},{"children",Json::array()},
            {"layout",{{"base",{{"kind","stack"},{"axis","vertical"},{"gap_dip",8},{"overflow","diagnose"}}}}}}})}};open(seed,fresh,"wrap",ids);
    }
    void unwrap(const Json& scene,const std::string& target){const auto& widgets=scene.at("widgets");const auto at=std::find_if(widgets.begin(),widgets.end(),[&](const Json& w){return w.at("id")==target;});need(at!=widgets.end()&&at->at("kind")=="group","editor.group");open(scene,target,"unwrap");}
    void erase(){active=false;updating=true;for(const auto& f:fields)text(f.second,"");for(const auto& c:combos)wipe(c.second);gtk_label_set_text(GTK_LABEL(error),"");gtk_label_set_text(GTK_LABEL(note),"");original=nullptr;id.clear();kind.clear();mode="layout";wrap_ids.clear();input={};selected=0;gtk_widget_hide(window);updating=false;}
    void finish(bool changed=false){erase();auto* top=gtk_widget_get_toplevel(parent);if(GTK_IS_WINDOW(top))gtk_window_present(GTK_WINDOW(top));finished(changed);}
    template<class F>void event(F f)noexcept{try{if(active)f();}catch(const protocol::Error&){updating=false;gtk_label_set_text(GTK_LABEL(error),"Layout was not changed. Check finite dimensions, ordered thresholds and bounds, identifiers, sibling position and current permissions.");}catch(...){erase();try{failed();}catch(...){}}}
    ~Impl(){erase();gtk_widget_destroy(window);g_object_unref(window);}
};
EditorLayoutForm::EditorLayoutForm(GtkWidget* p,std::function<bool(const std::vector<SceneEdit>&)> a,std::function<void(bool)> f,std::function<void()> e):impl_(std::make_unique<Impl>(p,std::move(a),std::move(f),std::move(e))){}
EditorLayoutForm::~EditorLayoutForm()=default;void EditorLayoutForm::open(const Json& scene,const std::string& id){impl_->open(scene,id);}void EditorLayoutForm::erase(){impl_->erase();}bool EditorLayoutForm::opened()const{return impl_->active;}
void EditorLayoutForm::wrap(const Json& scene,const std::vector<std::string>& ids,const std::string& id){impl_->wrap(scene,ids,id);}void EditorLayoutForm::unwrap(const Json& scene,const std::string& id){impl_->unwrap(scene,id);}
}
