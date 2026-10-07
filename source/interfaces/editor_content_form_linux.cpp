#include "editor_content_form.hpp"
#include "private_text.hpp"
#include <gtk/gtk.h>
#include <algorithm>
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
std::string text(GtkWidget* w){GtkTextIter a,z;auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(w));gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string result=raw;g_free(raw);return result;}
void text(GtkWidget* w,const std::string& value){gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),value.c_str(),static_cast<gint>(value.size()));}
void accessible(GtkWidget* w,const char* label,const std::string& id){atk_object_set_name(gtk_widget_get_accessible(w),label);atk_object_set_description(gtk_widget_get_accessible(w),("editor.content."+id).c_str());}
void wipe_combo(GtkWidget* w){auto* model=gtk_combo_box_get_model(GTK_COMBO_BOX(w));GtkTreeIter it;
    if(gtk_tree_model_get_iter_first(model,&it))do{gtk_list_store_set(GTK_LIST_STORE(model),&it,0,"",-1);}while(gtk_tree_model_iter_next(model,&it));
    gtk_combo_box_text_remove_all(GTK_COMBO_BOX_TEXT(w));
}
}
struct EditorContentForm::Impl {
    GtkWidget *parent,*window,*box,*error;std::map<std::string,GtkWidget*> fields,combos,sections,buttons;
    Json selected;ContentInput input;ContentChoices choices;int column=-1;bool active=false,updating=false;
    std::function<bool(const std::vector<SceneEdit>&)> apply;std::function<void(bool)> finished;std::function<void()> failed;
    GtkWidget* section(const char* id){auto* v=gtk_box_new(GTK_ORIENTATION_VERTICAL,5);gtk_box_pack_start(GTK_BOX(box),v,FALSE,FALSE,0);sections[id]=v;gtk_widget_set_no_show_all(v,TRUE);return v;}
    GtkWidget* row(GtkWidget* section,const char* label,GtkWidget* control){auto* r=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);auto* l=gtk_label_new(label);gtk_label_set_xalign(GTK_LABEL(l),0);gtk_widget_set_size_request(l,145,-1);gtk_label_set_mnemonic_widget(GTK_LABEL(l),control);gtk_box_pack_start(GTK_BOX(r),l,FALSE,FALSE,0);gtk_box_pack_start(GTK_BOX(r),control,TRUE,TRUE,0);gtk_box_pack_start(GTK_BOX(section),r,FALSE,FALSE,0);return control;}
    void field(GtkWidget* section,const char* id,const char* label,unsigned count=64,bool multiline=false){auto* w=private_text(count,multiline);fields[id]=w;accessible(w,label,id);gtk_widget_set_size_request(w,280,multiline?55:25);row(section,label,w);}
    void combo(GtkWidget* section,const char* id,const char* label){auto* w=gtk_combo_box_text_new();combos[id]=w;accessible(w,label,id);row(section,label,w);}
    void button(GtkWidget* section,const char* id,const char* label){auto* w=gtk_button_new_with_label(label);buttons[id]=w;accessible(w,label,id);gtk_box_pack_start(GTK_BOX(section),w,FALSE,FALSE,0);g_object_set_data_full(G_OBJECT(w),"content-action",g_strdup(id),g_free);
        g_signal_connect(w,"clicked",G_CALLBACK(+[](GtkWidget* w,gpointer p){auto& o=*static_cast<Impl*>(p);o.event([&]{o.command(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"content-action")));});}),this);}
    Impl(GtkWidget* p,std::function<bool(const std::vector<SceneEdit>&)> a,std::function<void(bool)> f,std::function<void()> e):parent(p),apply(std::move(a)),finished(std::move(f)),failed(std::move(e)){
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);g_object_ref_sink(window);gtk_window_set_title(GTK_WINDOW(window),"SysPane Content");gtk_window_set_modal(GTK_WINDOW(window),TRUE);gtk_window_set_resizable(GTK_WINDOW(window),FALSE);
        box=gtk_box_new(GTK_ORIENTATION_VERTICAL,8);gtk_container_set_border_width(GTK_CONTAINER(box),12);gtk_container_add(GTK_CONTAINER(window),box);
        auto* table=section("table");combo(table,"column","Column source");field(table,"label","Column label",128,true);
        auto* order=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(table),order,FALSE,FALSE,0);button(order,"up","Move column up");button(order,"down","Move column down");
        auto* chart=section("chart");field(chart,"window_ms","History window (ms)");field(chart,"max_points","Maximum points");combo(chart,"interpolation","Interpolation");combo(chart,"axis","Axis mode");combo(chart,"include_zero","Include zero");field(chart,"minimum","Minimum");field(chart,"maximum","Maximum");
        auto* image=section("image");combo(image,"asset","Image asset");field(image,"alt","Alternative text",1024,true);field(image,"width_dip","Preferred width (DIP)");field(image,"height_dip","Preferred height (DIP)");combo(image,"fit","Image fit");
        auto* note=section("note");gtk_box_pack_start(GTK_BOX(note),gtk_label_new("No additional widget content fields."),FALSE,FALSE,0);
        combo(box,"theme","Scene theme");error=gtk_label_new("");accessible(error,"","error");gtk_label_set_line_wrap(GTK_LABEL(error),TRUE);gtk_box_pack_start(GTK_BOX(box),error,FALSE,FALSE,0);
        auto* actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(box),actions,FALSE,FALSE,0);button(actions,"set","Set content");button(actions,"cancel","Cancel content");
        g_signal_connect(combos.at("column"),"changed",G_CALLBACK(+[](GtkComboBox* w,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.save_column();o.column=gtk_combo_box_get_active(w);o.column_value();});}),this);
        g_signal_connect(combos.at("axis"),"changed",G_CALLBACK(+[](GtkComboBox*,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.axis_fields();});}),this);
        g_signal_connect(window,"delete-event",G_CALLBACK(+[](GtkWidget*,GdkEvent*,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.event([&]{o.command("cancel");});return TRUE;}),this);
        g_signal_connect(window,"key-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventKey* e,gpointer p)->gboolean{if(e->keyval!=GDK_KEY_Escape)return FALSE;auto& o=*static_cast<Impl*>(p);o.event([&]{o.command("cancel");});return TRUE;}),this);
    }
    void options(const char* id,const std::vector<std::string>& values,int index){auto* w=combos.at(id);wipe_combo(w);for(const auto& value:values)gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(w),value.c_str());gtk_combo_box_set_active(GTK_COMBO_BOX(w),index);}
    void choices_into(const char* id,const std::vector<ContentChoice>& values,const Json& selected_value){std::vector<std::string> labels;int n=-1;for(std::size_t i=0;i<values.size();++i){labels.push_back(values[i].label);if(values[i].value==selected_value){need(n<0,"editor.content_choice");n=static_cast<int>(i);}}need(n>=0||values.empty(),"editor.content_choice");options(id,labels,n);}
    void save_column(){if(column>=0){need(static_cast<std::size_t>(column)<input.columns.size(),"editor.content_columns");input.columns[static_cast<std::size_t>(column)].label=text(fields.at("label"));}}
    void column_value(){text(fields.at("label"),column<0?"":input.columns.at(static_cast<std::size_t>(column)).label);gtk_widget_set_sensitive(buttons.at("up"),column>0);gtk_widget_set_sensitive(buttons.at("down"),column>=0&&static_cast<std::size_t>(column+1)<input.columns.size());}
    void columns(){std::vector<std::string> names;for(const auto& c:input.columns)names.push_back(selected.at("bindings").at(c.original).at("field").get<std::string>());options("column",names,column);column_value();}
    void axis_fields(){const bool fixed=gtk_combo_box_get_active(GTK_COMBO_BOX(combos.at("axis")))==1;gtk_widget_set_sensitive(fields.at("minimum"),fixed);gtk_widget_set_sensitive(fields.at("maximum"),fixed);gtk_widget_set_sensitive(combos.at("include_zero"),!fixed);}
    std::string combo_value(const char* id)const{auto* raw=gtk_combo_box_text_get_active_text(GTK_COMBO_BOX_TEXT(combos.at(id)));need(raw!=nullptr,"editor.content_choice");std::string result=raw;g_free(raw);return result;}
    Json chosen(const char* id,const std::vector<ContentChoice>& values)const{const int n=gtk_combo_box_get_active(GTK_COMBO_BOX(combos.at(id)));need(n>=0&&static_cast<std::size_t>(n)<values.size(),"editor.content_choice");return values[static_cast<std::size_t>(n)].value;}
    void open(const Json& scene,const Json* widget,const configuration::ResourceSet& resources){
        erase();need(scene.at("schema_version")!="0.2.0","editor.content_version");updating=true;
        try{choices=content_choices(resources);if(widget){selected=*widget;input=content_input(selected);}const std::string kind=selected.is_null()?"none":selected.at("kind").get<std::string>();
            for(const auto& f:input.fields)if(fields.count(f.first))text(fields.at(f.first),f.second);
            if(kind=="table"){column=0;columns();}
            else if(kind=="chart"){options("interpolation",{"linear","step"},input.fields.at("interpolation")=="linear"?0:1);options("axis",{"auto","fixed"},input.fields.at("axis")=="auto"?0:1);options("include_zero",{"true","false"},input.fields.at("include_zero")=="true"?0:1);axis_fields();}
            else if(kind=="image"){choices_into("asset",choices.images,input.asset);const auto fit=input.fields.at("fit");options("fit",{"contain","cover","stretch"},fit=="contain"?0:fit=="cover"?1:2);}
            choices_into("theme",choices.themes,scene.at("theme_id"));
            for(const auto& s:sections){const bool visible=s.first==kind||(s.first=="note"&&kind!="table"&&kind!="chart"&&kind!="image");if(visible){gtk_widget_set_no_show_all(s.second,FALSE);gtk_widget_show_all(s.second);gtk_widget_set_no_show_all(s.second,TRUE);}else gtk_widget_hide(s.second);}
            auto* top=gtk_widget_get_toplevel(parent);need(GTK_IS_WINDOW(top),"editor.content_parent");gtk_window_set_transient_for(GTK_WINDOW(window),GTK_WINDOW(top));gtk_window_set_position(GTK_WINDOW(window),GTK_WIN_POS_CENTER_ON_PARENT);
            active=true;updating=false;gtk_widget_show_all(window);gtk_window_present(GTK_WINDOW(window));
        }catch(...){erase();throw;}
    }
    void erase(){updating=true;active=false;for(const auto& f:fields)text(f.second,"");for(const auto& c:combos)wipe_combo(c.second);gtk_label_set_text(GTK_LABEL(error),"");selected=nullptr;input={};choices={};column=-1;gtk_widget_hide(window);updating=false;}
    void finish(bool changed=false){erase();auto* top=gtk_widget_get_toplevel(parent);if(GTK_IS_WINDOW(top))gtk_window_present(GTK_WINDOW(top));finished(changed);}
    void command(const std::string& id){
        need(active,"editor.content_closed");if(id=="cancel"){finish();return;}
        if(id=="up"||id=="down"){save_column();const int next=column+(id=="up"?-1:1);need(column>=0&&next>=0&&static_cast<std::size_t>(next)<input.columns.size(),"editor.content_columns");std::swap(input.columns[static_cast<std::size_t>(column)],input.columns[static_cast<std::size_t>(next)]);column=next;updating=true;columns();updating=false;return;}
        need(id=="set","editor.content_action");save_column();for(const auto& f:fields)if(f.first!="label")input.fields[f.first]=text(f.second);
        const std::string kind=selected.is_null()?"none":selected.at("kind").get<std::string>();
        if(kind=="chart")for(const char* key:{"interpolation","axis","include_zero"})input.fields[key]=combo_value(key);
        if(kind=="image"){input.fields["fit"]=combo_value("fit");input.asset=chosen("asset",choices.images);}
        std::vector<SceneEdit> edits;if(kind=="table"||kind=="chart"||kind=="image")edits.push_back(content_edit(selected,input,choices));edits.push_back(content_theme(chosen("theme",choices.themes),choices));const bool changed=apply(edits);finish(changed);
    }
    template<class F>void event(F f)noexcept{try{if(active)f();}catch(const protocol::Error& e){updating=false;const std::string code=e.what();gtk_label_set_text(GTK_LABEL(error),code=="editor.content_number"?"Enter a finite decimal number (an exponent is allowed).":code=="editor.content_integer"?"Enter a whole number within the field limits.":code=="editor.content_axis"?"Maximum must be greater than minimum.":code=="editor.content_dimensions"?"Image dimensions must be between 1 and 4096 DIP.":"Content could not be applied. Check values, resources and current permissions.");}catch(...){erase();try{failed();}catch(...){}}}
    ~Impl(){erase();gtk_widget_destroy(window);g_object_unref(window);}
};
EditorContentForm::EditorContentForm(GtkWidget* parent,std::function<bool(const std::vector<SceneEdit>&)> apply,std::function<void(bool)> finished,std::function<void()> failed):impl_(std::make_unique<Impl>(parent,std::move(apply),std::move(finished),std::move(failed))){}
EditorContentForm::~EditorContentForm()=default;
void EditorContentForm::open(const Json& scene,const Json* selected,const configuration::ResourceSet& resources){impl_->open(scene,selected,resources);}
void EditorContentForm::erase(){impl_->erase();}
bool EditorContentForm::opened()const{return impl_->active;}
}
