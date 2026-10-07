#include "editor_binding_form.hpp"
#include "private_text.hpp"
#include <algorithm>
#include <gtk/gtk.h>
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
std::string text(GtkWidget* w){GtkTextIter a,z;auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(w));gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string out=raw;g_free(raw);return out;}
void text(GtkWidget* w,const std::string& value){gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),value.c_str(),static_cast<gint>(value.size()));}
void name(GtkWidget* w,const char* label,const std::string& id){atk_object_set_name(gtk_widget_get_accessible(w),label);atk_object_set_description(gtk_widget_get_accessible(w),("editor.binding."+id).c_str());}
void wipe(GtkWidget* w){auto* m=gtk_combo_box_get_model(GTK_COMBO_BOX(w));GtkTreeIter i;if(gtk_tree_model_get_iter_first(m,&i))do{gtk_list_store_set(GTK_LIST_STORE(m),&i,0,"",-1);}while(gtk_tree_model_iter_next(m,&i));gtk_combo_box_text_remove_all(GTK_COMBO_BOX_TEXT(w));}
}
struct EditorBindingForm::Impl {
    GtkWidget *parent,*window,*box,*notebook,*error;std::map<std::string,GtkWidget*> fields,combos,buttons,sections;
    Json original;BindingInput input;std::vector<std::string> columns;int column=-1,predicate=-1,sort=-1;bool active=false,updating=false;
    std::function<bool(const std::vector<SceneEdit>&)> apply;std::function<void(bool)> finished;std::function<void()> failed;
    GtkWidget* section(GtkWidget* into,const char* id){auto* b=gtk_box_new(GTK_ORIENTATION_VERTICAL,4);gtk_box_pack_start(GTK_BOX(into),b,FALSE,FALSE,0);sections[id]=b;gtk_widget_set_no_show_all(b,TRUE);return b;}
    void row(GtkWidget* into,const char* label,GtkWidget* w){auto* b=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);auto* l=gtk_label_new(label);gtk_label_set_xalign(GTK_LABEL(l),0);gtk_widget_set_size_request(l,135,-1);gtk_box_pack_start(GTK_BOX(b),l,FALSE,FALSE,0);gtk_box_pack_start(GTK_BOX(b),w,TRUE,TRUE,0);gtk_box_pack_start(GTK_BOX(into),b,FALSE,FALSE,0);}
    void field(GtkWidget* into,const char* id,const char* label,unsigned limit=256,bool multiline=false){auto* w=private_text(limit,multiline);fields[id]=w;name(w,label,id);gtk_widget_set_size_request(w,320,multiline?50:25);row(into,label,w);}
    void combo(GtkWidget* into,const char* id,const char* label){auto* w=gtk_combo_box_text_new();combos[id]=w;name(w,label,id);row(into,label,w);}
    void button(GtkWidget* into,const std::string& id,const char* label){auto* w=gtk_button_new_with_label(label);buttons[id]=w;name(w,label,id);gtk_box_pack_start(GTK_BOX(into),w,FALSE,FALSE,0);g_object_set_data_full(G_OBJECT(w),"binding-action",g_strdup(id.c_str()),g_free);g_signal_connect(w,"clicked",G_CALLBACK(+[](GtkWidget* w,gpointer p){auto& o=*static_cast<Impl*>(p);o.event([&]{o.command(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"binding-action")));});}),this);}
    GtkWidget* page(const char* title,const char* id){auto* w=gtk_box_new(GTK_ORIENTATION_VERTICAL,4);gtk_container_set_border_width(GTK_CONTAINER(w),8);auto* l=gtk_label_new(title);name(l,title,id);gtk_notebook_append_page(GTK_NOTEBOOK(notebook),w,l);return w;}
    void list_controls(GtkWidget* into,const char* prefix){auto* b=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(into),b,FALSE,FALSE,0);for(const char* a:{"Add","Remove","Up","Down"})button(b,std::string(prefix)+a,a);}
    Impl(GtkWidget* p,std::function<bool(const std::vector<SceneEdit>&)> a,std::function<void(bool)> f,std::function<void()> e):parent(p),apply(std::move(a)),finished(std::move(f)),failed(std::move(e)){
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);g_object_ref_sink(window);gtk_window_set_title(GTK_WINDOW(window),"SysPane Bindings");gtk_window_set_modal(GTK_WINDOW(window),TRUE);gtk_window_set_resizable(GTK_WINDOW(window),FALSE);
        box=gtk_box_new(GTK_ORIENTATION_VERTICAL,6);gtk_container_set_border_width(GTK_CONTAINER(box),10);gtk_container_add(GTK_CONTAINER(window),box);
        combo(box,"column","Column");field(box,"field","Value field");combo(box,"kind","Binding kind");
        notebook=gtk_notebook_new();gtk_box_pack_start(GTK_BOX(box),notebook,TRUE,TRUE,0);
        auto* target=page("Target","target-tab");auto* scope=section(target,"scope");combo(scope,"scope","Scope");field(scope,"asset_id","Registered asset");field(scope,"entity_type","Entity type");
        auto* selector=section(target,"selector");field(selector,"limit","Result limit",3);
        auto* direct=section(target,"direct");field(direct,"producer_id","Producer");field(direct,"producer_epoch","Producer epoch");field(direct,"entity_id","Entity");
        auto* persistent=section(target,"persistent_pin");field(persistent,"namespace","Key namespace");combo(persistent,"key_encoding","Key text format");field(persistent,"key","Persistent key",4096,true);
        auto* legacy=section(target,"unresolved_pin");gtk_box_pack_start(GTK_BOX(legacy),gtk_label_new("Legacy pin: preserve it or explicitly choose a new binding kind."),FALSE,FALSE,0);
        auto* predicates=page("Filter","filter-tab");sections["predicate-page"]=predicates;combo(predicates,"predicate","Predicate");field(predicates,"predicate_field","Filter field");combo(predicates,"op","Comparison");combo(predicates,"type","Value type");combo(predicates,"encoding","Text format");field(predicates,"value","Filter value",4096,true);list_controls(predicates,"predicate-");
        auto* sorts=page("Order","order-tab");sections["sort-page"]=sorts;combo(sorts,"sort","Sort key");field(sorts,"sort_field","Sort field");combo(sorts,"direction","Direction");list_controls(sorts,"sort-");
        error=gtk_label_new("");name(error,"","error");gtk_label_set_line_wrap(GTK_LABEL(error),TRUE);gtk_label_set_max_width_chars(GTK_LABEL(error),70);gtk_box_pack_start(GTK_BOX(box),error,FALSE,FALSE,0);
        auto* actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,5);gtk_box_pack_start(GTK_BOX(box),actions,FALSE,FALSE,0);button(actions,"set","Set bindings");button(actions,"cancel","Cancel bindings");
        for(const char* id:{"column","predicate","sort","kind","scope"}){
            auto* w=combos.at(id);g_object_set_data_full(G_OBJECT(w),"binding-combo",g_strdup(id),g_free);g_signal_connect(w,"changed",G_CALLBACK(+[](GtkComboBox* w,gpointer p){auto& o=*static_cast<Impl*>(p);if(!o.updating)o.event([&]{o.changed(static_cast<const char*>(g_object_get_data(G_OBJECT(w),"binding-combo")));});}),this);
        }
        g_signal_connect(window,"delete-event",G_CALLBACK(+[](GtkWidget*,GdkEvent*,gpointer p)->gboolean{auto& o=*static_cast<Impl*>(p);o.event([&]{o.finish();});return TRUE;}),this);
        g_signal_connect(window,"key-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventKey* e,gpointer p)->gboolean{if(e->keyval!=GDK_KEY_Escape)return FALSE;auto& o=*static_cast<Impl*>(p);o.event([&]{o.finish();});return TRUE;}),this);
    }
    std::string chosen(const char* id)const{auto* raw=gtk_combo_box_text_get_active_text(GTK_COMBO_BOX_TEXT(combos.at(id)));need(raw,"editor.binding_choice");std::string out=raw;g_free(raw);return out;}
    void options(const char* id,const std::vector<std::string>& values,int index){wipe(combos.at(id));for(const auto& s:values)gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combos.at(id)),s.c_str());gtk_combo_box_set_active(GTK_COMBO_BOX(combos.at(id)),index);}
    void options(const char* id,const std::vector<std::string>& values,const std::string& selected){int index=-1;for(std::size_t n=0;n<values.size();++n)if(values[n]==selected)index=static_cast<int>(n);need(index>=0,"editor.binding_choice");options(id,values,index);}
    void save_rows(){if(predicate>=0)input.predicates.at(static_cast<std::size_t>(predicate))={text(fields.at("predicate_field")),chosen("op"),chosen("type"),text(fields.at("value")),chosen("encoding")};if(sort>=0)input.sort.at(static_cast<std::size_t>(sort))={text(fields.at("sort_field")),chosen("direction")};}
    void rows(){
        updating=true;std::vector<std::string> labels;for(std::size_t n=0;n<input.predicates.size();++n)labels.push_back("Predicate "+std::to_string(n+1));options("predicate",labels,predicate);labels.clear();for(std::size_t n=0;n<input.sort.size();++n)labels.push_back("Sort key "+std::to_string(n+1));options("sort",labels,sort);
        const PredicateInput p=predicate<0?PredicateInput{"","eq","text",""}:input.predicates.at(static_cast<std::size_t>(predicate));text(fields.at("predicate_field"),p.field);text(fields.at("value"),p.value);options("op",{"eq","ne"},p.op);options("type",{"text","boolean","number"},p.type);options("encoding",{"literal","escaped"},p.encoding);
        const SortInput s=sort<0?SortInput{"","ascending"}:input.sort.at(static_cast<std::size_t>(sort));text(fields.at("sort_field"),s.field);options("direction",{"ascending","descending"},s.direction);
        for(const char* id:{"predicate_field","value"}){gtk_widget_set_sensitive(fields.at(id),predicate>=0);}
        for(const char* id:{"op","type","encoding"}){gtk_widget_set_sensitive(combos.at(id),predicate>=0);}
        gtk_widget_set_sensitive(fields.at("sort_field"),sort>=0);gtk_widget_set_sensitive(combos.at("direction"),sort>=0);
        for(const std::string prefix:{"predicate-","sort-"}){const bool pfx=prefix=="predicate-";const auto size=pfx?input.predicates.size():input.sort.size();const int index=pfx?predicate:sort;gtk_widget_set_sensitive(buttons.at(prefix+"Add"),size<(pfx?16u:8u));gtk_widget_set_sensitive(buttons.at(prefix+"Remove"),index>=0);gtk_widget_set_sensitive(buttons.at(prefix+"Up"),index>0);gtk_widget_set_sensitive(buttons.at(prefix+"Down"),index>=0&&static_cast<std::size_t>(index+1)<size);}
        updating=false;
    }
    void kind(){const auto k=chosen("kind");for(const char* id:{"scope","selector","direct","persistent_pin","unresolved_pin"}){
        const bool visible=k==id||(std::string(id)=="scope"&&(k=="selector"||k=="persistent_pin"));auto* w=sections.at(id);if(visible){gtk_widget_set_no_show_all(w,FALSE);gtk_widget_show_all(w);gtk_widget_set_no_show_all(w,TRUE);}else gtk_widget_hide(w);
        }gtk_widget_set_sensitive(sections.at("predicate-page"),k=="selector");gtk_widget_set_sensitive(sections.at("sort-page"),k=="selector");gtk_widget_set_sensitive(fields.at("asset_id"),chosen("scope")=="registered_asset");gtk_widget_set_sensitive(fields.at("field"),k!="unresolved_pin");}
    void changed(const std::string& id){if(id=="column"){if(column>=0)columns.at(static_cast<std::size_t>(column))=text(fields.at("field"));column=gtk_combo_box_get_active(GTK_COMBO_BOX(combos.at("column")));need(column>=0,"editor.binding_column");text(fields.at("field"),columns.at(static_cast<std::size_t>(column)));}
        else if(id=="predicate"||id=="sort"){save_rows();(id=="predicate"?predicate:sort)=gtk_combo_box_get_active(GTK_COMBO_BOX(combos.at(id)));rows();}else kind();}
    void open(const Json& widget){erase();updating=true;try{
        original=widget;need(widget.contains("content")&&!widget.at("bindings").empty(),"editor.binding_widget");input=binding_input(widget.at("bindings")[0]);
        for(const auto& f:fields)text(f.second,input.fields.count(f.first)?input.fields.at(f.first):"");
        for(const auto& b:widget.at("bindings")){columns.push_back(b.at("field"));}
        std::vector<std::string> labels;
        for(std::size_t n=0;n<columns.size();++n){labels.push_back(widget.at("kind")=="table"?std::to_string(n+1)+". "+widget.at("content").at("columns")[n].at("label").get<std::string>():"Value");}
        column=0;options("column",labels,0);
        const bool table=widget.at("kind")=="table";std::vector<std::string> kinds=table?std::vector<std::string>{"selector"}:std::vector<std::string>{"selector","direct","persistent_pin"};if(input.fields.at("kind")=="unresolved_pin")kinds.push_back("unresolved_pin");options("kind",kinds,input.fields.at("kind"));
        options("scope",{"local_host","current_session","registered_asset"},input.fields.count("scope")?input.fields.at("scope"):"local_host");
        options("key_encoding",{"literal","escaped"},input.fields.count("key_encoding")?input.fields.at("key_encoding"):"literal");
        if(!input.fields.count("limit")){text(fields.at("limit"),"1");}
        predicate=input.predicates.empty()?-1:0;sort=input.sort.empty()?-1:0;rows();updating=true;kind();gtk_notebook_set_current_page(GTK_NOTEBOOK(notebook),0);
        auto* top=gtk_widget_get_toplevel(parent);need(GTK_IS_WINDOW(top),"editor.binding_parent");gtk_window_set_transient_for(GTK_WINDOW(window),GTK_WINDOW(top));gtk_window_set_position(GTK_WINDOW(window),GTK_WIN_POS_CENTER_ON_PARENT);active=true;updating=false;gtk_widget_show_all(window);gtk_window_present(GTK_WINDOW(window));
        }catch(...){erase();throw;}}
    void erase(){active=false;updating=true;for(const auto& f:fields)text(f.second,"");for(const auto& c:combos)wipe(c.second);gtk_label_set_text(GTK_LABEL(error),"");original=nullptr;input={};columns.clear();column=predicate=sort=-1;gtk_widget_hide(window);updating=false;}
    void finish(bool changed=false){erase();auto* top=gtk_widget_get_toplevel(parent);if(GTK_IS_WINDOW(top))gtk_window_present(GTK_WINDOW(top));finished(changed);}
    void command(const std::string& id){if(id=="cancel"){finish();return;}save_rows();
        if(id=="set"){need(column>=0,"editor.binding_column");columns.at(static_cast<std::size_t>(column))=text(fields.at("field"));for(const auto& f:fields)input.fields[f.first]=text(f.second);input.fields["kind"]=chosen("kind");input.fields["scope"]=chosen("scope");input.fields["key_encoding"]=chosen("key_encoding");if(input.fields["kind"]=="unresolved_pin")input.fields["entity_id"]=original.at("bindings")[0].at("entity_id");const bool changed=apply({binding_edit(original,input,columns)});finish(changed);return;}
        const bool p=id.substr(0,10)=="predicate-";need(p||id.substr(0,5)=="sort-","editor.binding_action");const auto a=id.substr(p?10:5);auto& index=p?predicate:sort;
        auto modify=[&](auto& list,const auto& blank){if(a=="Add"){need(list.size()<(p?16u:8u),"editor.binding_rows");list.push_back(blank);index=static_cast<int>(list.size())-1;}
            else{need(index>=0&&static_cast<std::size_t>(index)<list.size(),"editor.binding_row");if(a=="Remove"){list.erase(list.begin()+index);index=list.empty()?-1:std::min(index,static_cast<int>(list.size())-1);}else{need(a=="Up"||a=="Down","editor.binding_action");const int next=index+(a=="Up"?-1:1);need(next>=0&&static_cast<std::size_t>(next)<list.size(),"editor.binding_row");std::swap(list[static_cast<std::size_t>(index)],list[static_cast<std::size_t>(next)]);index=next;}}};
        if(p)modify(input.predicates,PredicateInput{"","eq","text",""});else modify(input.sort,SortInput{"","ascending"});rows();
    }
    template<class F>void event(F f)noexcept{try{if(active)f();}catch(const protocol::Error& e){updating=false;const std::string code=e.what();gtk_label_set_text(GTK_LABEL(error),code=="editor.binding_number"||code=="editor.binding_integer_range"?"Enter a finite JSON number; whole numbers must fit signed or unsigned 64-bit storage.":code=="editor.binding_text"?"Escaped text needs one quoted JSON string, with valid escapes.":code=="editor.binding_boolean"?"Enter true or false for a boolean value.":code=="editor.binding_duplicate"?"Each table column needs a different value field.":"Bindings could not be applied. Check active fields, row limits and current permissions.");}catch(...){erase();try{failed();}catch(...){}}}
    ~Impl(){erase();gtk_widget_destroy(window);g_object_unref(window);}
};
EditorBindingForm::EditorBindingForm(GtkWidget* p,std::function<bool(const std::vector<SceneEdit>&)> a,std::function<void(bool)> f,std::function<void()> e):impl_(std::make_unique<Impl>(p,std::move(a),std::move(f),std::move(e))){}
EditorBindingForm::~EditorBindingForm()=default;
void EditorBindingForm::open(const Json& w){impl_->open(w);}void EditorBindingForm::erase(){impl_->erase();}bool EditorBindingForm::opened()const{return impl_->active;}
}
