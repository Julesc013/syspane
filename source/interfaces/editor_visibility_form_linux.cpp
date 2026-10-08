#include "editor_visibility_form.hpp"
#include "editor_binding_form.hpp"
#include "private_text.hpp"
#include <gtk/gtk.h>
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
std::string text(GtkWidget* w){GtkTextIter a,z;auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(w));gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string out=raw;g_free(raw);return out;}
void text(GtkWidget* w,const std::string& value){gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),value.c_str(),static_cast<gint>(value.size()));}
void name(GtkWidget* w,const char* label,const std::string& id){atk_object_set_name(gtk_widget_get_accessible(w),label);atk_object_set_description(gtk_widget_get_accessible(w),("editor.visibility."+id).c_str());}
void wipe(GtkWidget* w){auto* m=gtk_combo_box_get_model(GTK_COMBO_BOX(w));GtkTreeIter i;if(gtk_tree_model_get_iter_first(m,&i))do{gtk_list_store_set(GTK_LIST_STORE(m),&i,0,"",-1);}while(gtk_tree_model_iter_next(m,&i));gtk_combo_box_text_remove_all(GTK_COMBO_BOX_TEXT(w));}
}
struct EditorVisibilityForm::Impl {
    GtkWidget *parent,*window,*box,*error,*summary,*note;std::map<std::string,GtkWidget*> fields,combos,buttons;
    std::unique_ptr<EditorBindingForm> source;VisibilityInput input;std::vector<std::string> ids;bool active=false,updating=false;
    std::function<bool(const std::optional<SetWidgetVisibility>&)> apply;std::function<void(bool)> finished;std::function<void()> failed;
    void row(const char* label,GtkWidget* w){auto* b=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);auto* l=gtk_label_new(label);gtk_label_set_xalign(GTK_LABEL(l),0);gtk_widget_set_size_request(l,130,-1);gtk_box_pack_start(GTK_BOX(b),l,FALSE,FALSE,0);gtk_box_pack_start(GTK_BOX(b),w,TRUE,TRUE,0);gtk_box_pack_start(GTK_BOX(box),b,FALSE,FALSE,0);}
    void combo(const char* id,const char* label){auto* w=gtk_combo_box_text_new();combos[id]=w;name(w,label,id);row(label,w);}
    void field(const char* id,const char* label,unsigned limit,bool multiline=false){auto* w=private_text(limit,multiline);fields[id]=w;name(w,label,id);gtk_widget_set_size_request(w,320,multiline?50:25);row(label,w);
        g_signal_connect(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),"insert-text",G_CALLBACK(+[](GtkTextBuffer* b,GtkTextIter*,gchar*,gint n,gpointer data){
            const auto bound=GPOINTER_TO_UINT(data);GtkTextIter a;GtkTextIter z;gtk_text_buffer_get_bounds(b,&a,&z);auto* old=gtk_text_buffer_get_text(b,&a,&z,FALSE);const auto bytes=std::char_traits<char>::length(old);g_free(old);
            if(n<0||bytes>bound||static_cast<std::size_t>(n)>bound-bytes)g_signal_stop_emission_by_name(b,"insert-text");
        }),GUINT_TO_POINTER(limit));}
    void button(GtkWidget* into,const char* id,const char* label){auto* w=gtk_button_new_with_label(label);buttons[id]=w;name(w,label,id);gtk_box_pack_start(GTK_BOX(into),w,FALSE,FALSE,0);g_object_set_data_full(G_OBJECT(w),"visibility-action",g_strdup(id),g_free);g_signal_connect(w,"clicked",G_CALLBACK(+[](GtkWidget* w,gpointer p){auto& o=*static_cast<Impl*>(p);o.event([&]{o.command(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"visibility-action")));});}),this);}
    GtkWidget* label(const char* id){auto* w=gtk_label_new("");name(w,"",id);gtk_label_set_line_wrap(GTK_LABEL(w),TRUE);gtk_label_set_max_width_chars(GTK_LABEL(w),58);gtk_label_set_xalign(GTK_LABEL(w),0);gtk_box_pack_start(GTK_BOX(box),w,FALSE,FALSE,0);return w;}
    Impl(GtkWidget* p,std::function<bool(const std::optional<SetWidgetVisibility>&)> a,std::function<void(bool)> f,std::function<void()> e):parent(p),apply(std::move(a)),finished(std::move(f)),failed(std::move(e)){
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);g_object_ref_sink(window);gtk_window_set_title(GTK_WINDOW(window),"SysPane Visibility");gtk_window_set_modal(GTK_WINDOW(window),TRUE);gtk_window_set_resizable(GTK_WINDOW(window),FALSE);
        box=gtk_box_new(GTK_ORIENTATION_VERTICAL,6);gtk_container_set_border_width(GTK_CONTAINER(box),10);gtk_container_add(GTK_CONTAINER(window),box);
        combo("mode","Show content");summary=label("source-summary");auto* source_actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(box),source_actions,FALSE,FALSE,0);button(source_actions,"source","Choose source...");
        combo("op","Comparison");combo("type","Value type");combo("encoding","Text format");field("value","Condition value",4096,true);field("unit","Unit",64);note=label("note");error=label("error");
        auto* actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(box),actions,FALSE,FALSE,0);button(actions,"set","Set visibility");button(actions,"cancel","Cancel visibility");
        g_signal_connect(combos.at("mode"),"changed",G_CALLBACK(+[](GtkComboBox*,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.sync();});}),this);
        g_signal_connect(window,"delete-event",G_CALLBACK(+[](GtkWidget*,GdkEvent*,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.event([&]{o.finish();});return TRUE;}),this);
        g_signal_connect(window,"key-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventKey* e,gpointer p)->gboolean{if(e->keyval!=GDK_KEY_Escape)return FALSE;auto& o=*static_cast<Impl*>(p);o.event([&]{o.finish();});return TRUE;}),this);
    }
    std::string chosen(const char* id)const{auto* raw=gtk_combo_box_text_get_active_text(GTK_COMBO_BOX_TEXT(combos.at(id)));need(raw,"editor.visibility_choice");std::string out=raw;g_free(raw);return out;}
    void options(const char* id,const std::vector<std::string>& values,const std::string& selected){wipe(combos.at(id));int index=-1;for(std::size_t n=0;n<values.size();++n){gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combos.at(id)),values[n].c_str());if(values[n]==selected)index=static_cast<int>(n);}need(index>=0,"editor.visibility_choice");gtk_combo_box_set_active(GTK_COMBO_BOX(combos.at(id)),index);}
    void sync(){const bool conditional=chosen("mode")=="When condition matches";const bool nested=source&&source->opened();
        for(const auto& c:combos)gtk_widget_set_sensitive(c.second,!nested&&(c.first=="mode"||conditional));
        for(const auto& f:fields)gtk_widget_set_sensitive(f.second,!nested&&conditional);
        for(const auto& b:buttons)gtk_widget_set_sensitive(b.second,!nested&&(b.first!="source"||conditional));
        const auto value="Source: "+input.binding.at("field").get<std::string>()+" ("+input.binding.at("kind").get<std::string>()+")";gtk_label_set_text(GTK_LABEL(summary),value.c_str());
    }
    void open(const Json& scene,const std::vector<std::string>& selected){erase();updating=true;try{input=visibility_input(scene,selected);ids=selected;
        std::vector<std::string> modes{"Always show","When condition matches"};if(input.mode=="keep")modes.push_back("Keep unchanged");options("mode",modes,input.mode=="keep"?"Keep unchanged":input.mode=="always"?"Always show":"When condition matches");
        options("op",{"eq","ne","lt","le","gt","ge"},input.comparison.op);options("type",{"text","boolean","number"},input.comparison.type);options("encoding",{"literal","escaped"},input.comparison.encoding);text(fields.at("value"),input.comparison.value);text(fields.at("unit"),input.unit);
        gtk_label_set_text(GTK_LABEL(note),input.mode=="keep"?"Own conditions differ. Choose a mode to replace all selected own rules. Container conditions still apply.":"Edit this object's own condition. Container conditions still apply. New rules start with local network receive bytes greater than 0 byte.");
        auto* top=gtk_widget_get_toplevel(parent);need(GTK_IS_WINDOW(top),"editor.visibility_parent");gtk_window_set_transient_for(GTK_WINDOW(window),GTK_WINDOW(top));gtk_window_set_position(GTK_WINDOW(window),GTK_WIN_POS_CENTER_ON_PARENT);active=true;sync();updating=false;gtk_widget_show_all(window);gtk_window_present(GTK_WINDOW(window));
        }catch(...){erase();throw;}}
    void erase(){active=false;updating=true;if(source)source->erase();for(const auto& f:fields)text(f.second,"");for(const auto& c:combos)wipe(c.second);for(auto* l:{summary,note,error})gtk_label_set_text(GTK_LABEL(l),"");input={};ids.clear();gtk_widget_hide(window);updating=false;}
    void finish(bool changed=false){erase();auto* top=gtk_widget_get_toplevel(parent);if(GTK_IS_WINDOW(top))gtk_window_present(GTK_WINDOW(top));finished(changed);}
    void command(const std::string& id){if(id=="cancel"){finish();return;}need(!source||!source->opened(),"editor.visibility_nested");if(id=="source"){
            if(!source)source=std::make_unique<EditorBindingForm>(window,[this](const std::vector<SceneEdit>& edits){need(edits.size()==1&&std::holds_alternative<WidgetContentEdit>(edits[0]),"editor.visibility_binding");const auto& edit=std::get<WidgetContentEdit>(edits[0]);need(edit.bindings.size()==1,"editor.visibility_binding");visibility_source(edit.bindings[0]);const bool changed=input.binding!=edit.bindings[0];input.binding=edit.bindings[0];return changed;},[this](bool){if(active)sync();},[this]{erase();failed();});
            source->open({{"id","condition"},{"kind","value"},{"content",Json::object()},{"bindings",Json::array({input.binding})}});sync();return;
        }
        need(id=="set","editor.visibility_action");const auto mode=chosen("mode");input.mode=mode=="Always show"?"always":mode=="When condition matches"?"conditional":"keep";
        input.comparison={"",chosen("op"),chosen("type"),text(fields.at("value")),chosen("encoding")};input.unit=text(fields.at("unit"));const bool changed=apply(visibility_edit(ids,input));finish(changed);
    }
    template<class F>void event(F f)noexcept{try{if(active)f();}catch(const protocol::Error& e){updating=false;const std::string code=e.what();gtk_label_set_text(GTK_LABEL(error),code=="editor.binding_number"||code=="editor.binding_integer_range"?"Enter a finite JSON number; whole numbers must fit signed or unsigned 64-bit storage.":code=="editor.binding_text"?"Escaped text needs one quoted JSON string, with valid escapes.":"Visibility could not be applied. Check the source, value, operator, unit and current permissions. Text and boolean values need eq/ne and unit 1.");}catch(...){erase();try{failed();}catch(...){}}}
    ~Impl(){erase();source.reset();gtk_widget_destroy(window);g_object_unref(window);}
};
EditorVisibilityForm::EditorVisibilityForm(GtkWidget* p,std::function<bool(const std::optional<SetWidgetVisibility>&)> a,std::function<void(bool)> f,std::function<void()> e):impl_(std::make_unique<Impl>(p,std::move(a),std::move(f),std::move(e))){}
EditorVisibilityForm::~EditorVisibilityForm()=default;void EditorVisibilityForm::open(const Json& scene,const std::vector<std::string>& ids){impl_->open(scene,ids);}void EditorVisibilityForm::erase(){impl_->erase();}bool EditorVisibilityForm::opened()const{return impl_->active;}
}
