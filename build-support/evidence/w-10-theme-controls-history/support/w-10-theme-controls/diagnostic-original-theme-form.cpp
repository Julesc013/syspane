#include "editor_theme_form.hpp"
#include "private_text.hpp"
#include <gtk/gtk.h>
#include <set>
#include <vector>
namespace syspane::interfaces {
namespace {
using configuration::Json;
void need(bool b,const char* code){if(!b)throw protocol::Error(code);}
void name(GtkWidget* w,const char* label,const std::string& id){atk_object_set_name(gtk_widget_get_accessible(w),label);atk_object_set_description(gtk_widget_get_accessible(w),("editor.theme."+id).c_str());}
std::string text(GtkWidget* w){auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(w));GtkTextIter a,z;gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string v=raw;g_free(raw);return v;}
void text(GtkWidget* w,const std::string& v){gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),v.c_str(),static_cast<gint>(v.size()));}
void wipe(GtkWidget* w){auto* m=gtk_combo_box_get_model(GTK_COMBO_BOX(w));GtkTreeIter i;if(gtk_tree_model_get_iter_first(m,&i))do{gtk_list_store_set(GTK_LIST_STORE(m),&i,0,"",-1);}while(gtk_tree_model_iter_next(m,&i));gtk_combo_box_text_remove_all(GTK_COMBO_BOX_TEXT(w));}
}
struct EditorThemeForm::Impl {
    GtkWidget *parent,*window,*box,*enabled,*error,*note;std::map<std::string,GtkWidget*> fields,combos,buttons;
    Json original;std::map<std::string,FontInput> fonts;std::set<std::string> roles;std::string target;bool active=false,updating=false;
    std::function<bool(const std::optional<Json>&)> apply;std::function<void(bool)> finished;std::function<void()> failed;
    void row(const char* title,GtkWidget* w){auto* b=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);auto* l=gtk_label_new(title);gtk_label_set_xalign(GTK_LABEL(l),0);gtk_widget_set_size_request(l,130,-1);gtk_box_pack_start(GTK_BOX(b),l,FALSE,FALSE,0);gtk_box_pack_start(GTK_BOX(b),w,TRUE,TRUE,0);gtk_box_pack_start(GTK_BOX(box),b,FALSE,FALSE,0);}
    void combo(const char* id,const char* title){auto* w=gtk_combo_box_text_new();combos[id]=w;name(w,title,id);row(title,w);}
    void field(const char* id,const char* title,unsigned bound){auto* w=private_text(bound,false);fields[id]=w;name(w,title,id);gtk_widget_set_size_request(w,260,25);row(title,w);}
    void button(GtkWidget* into,const char* id,const char* title){auto* w=gtk_button_new_with_label(title);buttons[id]=w;name(w,title,id);gtk_box_pack_start(GTK_BOX(into),w,FALSE,FALSE,0);g_object_set_data_full(G_OBJECT(w),"theme-action",g_strdup(id),g_free);g_signal_connect(w,"clicked",G_CALLBACK(+[](GtkWidget* w,gpointer p){auto& o=*static_cast<Impl*>(p);o.event([&]{o.command(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"theme-action")));});}),this);}
    std::string chosen(const char* id)const{auto* raw=gtk_combo_box_text_get_active_text(GTK_COMBO_BOX_TEXT(combos.at(id)));need(raw,"editor.theme_choice");std::string v=raw;g_free(raw);return v;}
    void options(const char* id,const std::vector<std::string>& values,const std::string& selected){wipe(combos.at(id));int at=-1;for(std::size_t n=0;n<values.size();++n){gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combos.at(id)),values[n].c_str());if(values[n]==selected)at=static_cast<int>(n);}need(at>=0,"editor.theme_choice");gtk_combo_box_set_active(GTK_COMBO_BOX(combos.at(id)),at);}
    Impl(GtkWidget* p,std::function<bool(const std::optional<Json>&)> a,std::function<void(bool)> f,std::function<void()> e):parent(p),apply(std::move(a)),finished(std::move(f)),failed(std::move(e)){
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);g_object_ref_sink(window);gtk_window_set_title(GTK_WINDOW(window),"SysPane Fonts");gtk_window_set_modal(GTK_WINDOW(window),TRUE);gtk_window_set_resizable(GTK_WINDOW(window),FALSE);
        box=gtk_box_new(GTK_ORIENTATION_VERTICAL,6);gtk_container_set_border_width(GTK_CONTAINER(box),10);gtk_container_add(GTK_CONTAINER(window),box);
        combo("mode","Role overrides");combo("target","Font target");enabled=gtk_check_button_new_with_label("Use this role font");name(enabled,"Use this role font","enabled");gtk_box_pack_start(GTK_BOX(box),enabled,FALSE,FALSE,0);
        field("family","Font family",512);field("size","Size (DIP)",64);field("weight","Weight (100..900)",64);combo("style","Style");
        note=gtk_label_new("");error=gtk_label_new("");for(auto* w:{note,error}){gtk_label_set_line_wrap(GTK_LABEL(w),TRUE);gtk_label_set_max_width_chars(GTK_LABEL(w),58);gtk_label_set_xalign(GTK_LABEL(w),0);gtk_box_pack_start(GTK_BOX(box),w,FALSE,FALSE,0);}name(note,"","note");name(error,"","error");
        auto* actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(box),actions,FALSE,FALSE,0);button(actions,"set","Set fonts");button(actions,"reset","Use settings theme");button(actions,"cancel","Cancel fonts");
        g_signal_connect(combos.at("target"),"changed",G_CALLBACK(+[](GtkComboBox*,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.capture();o.show();});}),this);
        g_signal_connect(combos.at("mode"),"changed",G_CALLBACK(+[](GtkComboBox*,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.capture();o.sync();});}),this);
        g_signal_connect(enabled,"toggled",G_CALLBACK(+[](GtkToggleButton* w,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.capture();if(gtk_toggle_button_get_active(w))o.roles.insert(o.target);else o.roles.erase(o.target);o.sync();});}),this);
        g_signal_connect(window,"delete-event",G_CALLBACK(+[](GtkWidget*,GdkEvent*,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.event([&]{o.finish();});return TRUE;}),this);
        g_signal_connect(window,"key-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventKey* e,gpointer p)->gboolean{if(e->keyval!=GDK_KEY_Escape)return FALSE;auto& o=*static_cast<Impl*>(p);o.event([&]{o.finish();});return TRUE;}),this);
    }
    void capture(){if(target.empty())return;fonts.at(target)={text(fields.at("family")),text(fields.at("size")),text(fields.at("weight")),chosen("style")};}
    void sync(){const bool base=target=="Base",custom=chosen("mode")=="Customize roles",edit=base||(custom&&roles.count(target));gtk_widget_set_sensitive(enabled,!base&&custom);for(const auto& f:fields)gtk_widget_set_sensitive(f.second,edit);gtk_widget_set_sensitive(combos.at("style"),edit);}
    void show(){updating=true;target=chosen("target");const auto& f=fonts.at(target);text(fields.at("family"),f.family);text(fields.at("size"),f.size_dip);text(fields.at("weight"),f.weight);options("style",{"normal","italic","oblique"},f.style);gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(enabled),roles.count(target)!=0);sync();updating=false;}
    void open(const Json& theme){erase();updating=true;try{original=theme;const auto input=theme_control_input(theme);fonts["Base"]=input.fonts.font;
        for(const auto& role:std::vector<std::pair<std::string,std::string>>{{"Body","body"},{"Label","label"},{"Value","value"},{"Diagnostic","diagnostic"}}){const auto it=input.fonts.roles.find(role.second);fonts[role.first]=it==input.fonts.roles.end()?input.fonts.font:it->second;if(it!=input.fonts.roles.end())roles.insert(role.first);}
        options("mode",{"Use base font for all roles","Customize roles"},input.explicit_roles?"Customize roles":"Use base font for all roles");options("target",{"Base","Body","Label","Value","Diagnostic"},"Base");show();
        gtk_label_set_text(GTK_LABEL(note),"Disabled roles use the base font. Set changes the draft; Apply saves it. Use settings theme restores the theme selected in settings.");auto* top=gtk_widget_get_toplevel(parent);need(GTK_IS_WINDOW(top),"editor.theme_parent");gtk_window_set_transient_for(GTK_WINDOW(window),GTK_WINDOW(top));gtk_window_set_position(GTK_WINDOW(window),GTK_WIN_POS_CENTER_ON_PARENT);active=true;updating=false;gtk_widget_show_all(window);gtk_window_present(GTK_WINDOW(window));
        }catch(...){erase();throw;}}
    void erase(){active=false;updating=true;for(const auto& f:fields)text(f.second,"");for(const auto& c:combos)wipe(c.second);gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(enabled),FALSE);gtk_label_set_text(GTK_LABEL(note),"");gtk_label_set_text(GTK_LABEL(error),"");original=nullptr;fonts.clear();roles.clear();target.clear();gtk_widget_hide(window);updating=false;}
    void finish(bool changed=false){erase();auto* top=gtk_widget_get_toplevel(parent);if(GTK_IS_WINDOW(top))gtk_window_present(GTK_WINDOW(top));finished(changed);}
    void command(const std::string& id){if(id=="cancel"){finish();return;}if(id=="reset"){finish(apply(std::nullopt));return;}need(id=="set","editor.theme_action");capture();ThemeControlInput input;input.fonts.font=fonts.at("Base");input.explicit_roles=chosen("mode")=="Customize roles";
        for(const auto& role:std::vector<std::pair<std::string,std::string>>{{"Body","body"},{"Label","label"},{"Value","value"},{"Diagnostic","diagnostic"}})if(roles.count(role.first))input.fonts.roles.emplace(role.second,fonts.at(role.first));
        const auto candidate=theme_control_edit(original,input);finish(candidate.dump()==original.dump()?false:apply(candidate));
    }
    template<class F>void event(F f)noexcept{try{if(active)f();}catch(const protocol::Error&){updating=false;gtk_label_set_text(GTK_LABEL(error),"Fonts could not be set. Use one literal family, a finite size from 9 to 72 DIP, weight 100..900 in steps of 100, and a listed style. Check current permissions; apply a newly selected base theme before editing its fonts.");}catch(...){erase();try{failed();}catch(...){}}}
    ~Impl(){erase();gtk_widget_destroy(window);g_object_unref(window);}
};
EditorThemeForm::EditorThemeForm(GtkWidget* p,std::function<bool(const std::optional<Json>&)> a,std::function<void(bool)> f,std::function<void()> e):impl_(std::make_unique<Impl>(p,std::move(a),std::move(f),std::move(e))){}
EditorThemeForm::~EditorThemeForm()=default;void EditorThemeForm::open(const Json& v){impl_->open(v);}void EditorThemeForm::erase(){impl_->erase();}bool EditorThemeForm::opened()const{return impl_->active;}
}
