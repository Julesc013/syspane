#include "scene_inspector.hpp"
#include "scene_inspector_model.hpp"
#include <gtk/gtk.h>
#include <thread>
namespace syspane::interfaces {
namespace {
namespace r=rendering;namespace d=recovery;namespace c=configuration;
enum {key_column,item_column,information_column};
std::string text(GtkTreeModel* model,GtkTreeIter* iter,int column){gchar* value=nullptr;gtk_tree_model_get(model,iter,column,&value,-1);std::string out=value?value:"";g_free(value);return out;}
}
struct SceneInspector::Impl {
    std::thread::id thread=std::this_thread::get_id();bool batch=false,closed=false;
    GtkWidget *root=nullptr,*tree=nullptr,*summary=nullptr,*button=nullptr;GtkTreeStore* store=nullptr;
    std::unique_ptr<r::SceneSurface> surface;std::string summary_key;
    std::map<std::string,GtkTreeIter> rows;
    std::map<std::string,bool> expansion;
    GtkTreeModel* model()const{return GTK_TREE_MODEL(store);}
    void owner()const{if(thread!=std::this_thread::get_id()||batch)throw std::logic_error("inspector.owner");}
    void clear_summary(){summary_key.clear();if(summary)gtk_label_set_text(GTK_LABEL(summary),"");}
    void blank(GtkTreeIter* parent=nullptr){GtkTreeIter iter;if(!store||!gtk_tree_model_iter_children(model(),&iter,parent))return;
        do{blank(&iter);gtk_tree_store_set(store,&iter,key_column,"",item_column,"",information_column,"",-1);}while(gtk_tree_model_iter_next(model(),&iter));}
    void clear(){clear_summary();rows.clear();expansion.clear();if(store){blank();gtk_tree_store_clear(store);}}
    bool invalidated(){if(!batch)clear();return true;}
    void shut(){closed=true;clear();if(surface&&!batch)surface->close();}
    ~Impl(){shut();surface.reset();if(root)gtk_widget_destroy(root);for(auto* w:{button,summary,tree,root})if(w)g_object_unref(w);if(store)g_object_unref(store);}
    void reconcile(const std::vector<InspectorRow>& desired,GtkTreeIter* parent=nullptr){
        std::map<std::string,GtkTreeIter> current;GtkTreeIter iter;
        if(gtk_tree_model_iter_children(model(),&iter,parent))do{current.emplace(text(model(),&iter,key_column),iter);}while(gtk_tree_model_iter_next(model(),&iter));
        std::set<std::string> wanted;for(const auto& row:desired)wanted.insert(row.key);
        for(auto& old:current)if(!wanted.count(old.first)){blank(&old.second);gtk_tree_store_set(store,&old.second,key_column,"",item_column,"",information_column,"",-1);gtk_tree_store_remove(store,&old.second);}
        GtkTreeIter previous;bool first=true;int expected=0;
        for(const auto& row:desired){auto found=current.find(row.key);GtkTreeIter at;
            if(found==current.end())gtk_tree_store_insert_after(store,&at,parent,first?nullptr:&previous);else at=found->second;
            auto* path=gtk_tree_model_get_path(model(),&at);const auto position=gtk_tree_path_get_indices(path)[gtk_tree_path_get_depth(path)-1];gtk_tree_path_free(path);
            if(position!=expected)gtk_tree_store_move_after(store,&at,first?nullptr:&previous);
            if(text(model(),&at,key_column)!=row.key||text(model(),&at,item_column)!=row.item||text(model(),&at,information_column)!=row.information)
                gtk_tree_store_set(store,&at,key_column,row.key.c_str(),item_column,row.item.c_str(),information_column,row.information.c_str(),-1);
            rows.emplace(row.key,at);reconcile(row.children,&at);previous=at;first=false;++expected;
        }
    }
    void present(const r::SurfaceFrame* frame){
        if(!frame||closed){clear();return;}const auto projected=inspector_rows(*frame);
        std::vector<std::string> selection;GtkTreePath* path=nullptr;GtkTreeViewColumn* column=nullptr;gtk_tree_view_get_cursor(GTK_TREE_VIEW(tree),&path,&column);
        if(path)gtk_tree_path_free(path);
        GtkTreeIter selected;if(gtk_tree_selection_get_selected(gtk_tree_view_get_selection(GTK_TREE_VIEW(tree)),nullptr,&selected)){do{selection.push_back(text(model(),&selected,key_column));GtkTreeIter parent;if(!gtk_tree_model_iter_parent(model(),&parent,&selected))break;selected=parent;}while(true);}
        rows.clear();reconcile(projected);
        if(!summary_key.empty()&&!rows.count(summary_key))clear_summary();
        for(auto it=expansion.begin();it!=expansion.end();)if(!rows.count(it->first))it=expansion.erase(it);else ++it;
        expand(projected);
        bool restored=false;for(const auto& key:selection){const auto found=rows.find(key);if(found==rows.end())continue;
            GtkTreePath* current=nullptr;gtk_tree_view_get_cursor(GTK_TREE_VIEW(tree),&current,nullptr);auto* next=gtk_tree_model_get_path(model(),&found->second);
            if(!current||gtk_tree_path_compare(current,next))gtk_tree_view_set_cursor(GTK_TREE_VIEW(tree),next,column,FALSE);
            if(current)gtk_tree_path_free(current);
            gtk_tree_path_free(next);restored=true;break;}
        if(!selection.empty()&&!restored)gtk_tree_selection_unselect_all(gtk_tree_view_get_selection(GTK_TREE_VIEW(tree)));
    }
    void expand(const std::vector<InspectorRow>& desired){for(const auto& row:desired)if(!row.children.empty()){
        const auto state=expansion.emplace(row.key,true).first;auto* p=gtk_tree_model_get_path(model(),&rows.at(row.key));
        if(state->second){gtk_tree_view_expand_row(GTK_TREE_VIEW(tree),p,FALSE);expand(row.children);}
        else gtk_tree_view_collapse_row(GTK_TREE_VIEW(tree),p);
        gtk_tree_path_free(p);}}
    void run(std::uint64_t now,const std::map<std::string,model::Tick>& ticks,const std::function<void()>& action){
        owner();if(closed)return;batch=true;
        try{action();if(!closed)surface->paint(now,ticks,[&](auto,const auto* frame){present(frame);});batch=false;if(closed)surface->close();}
        catch(...){batch=false;shut();throw;}
    }
    void request(){if(closed||batch)return;GtkTreeIter selected;auto* selection=gtk_tree_view_get_selection(GTK_TREE_VIEW(tree));
        if(!gtk_tree_selection_get_selected(selection,nullptr,&selected)){clear_summary();return;}
        summary_key=text(model(),&selected,key_column);const auto value=text(model(),&selected,item_column)+"\n"+text(model(),&selected,information_column);
        gtk_label_set_text(GTK_LABEL(summary),value.c_str());}
};
SceneInspector::SceneInspector(c::Authority authority,c::Policy policy,r::SurfaceConfig config,std::vector<r::SurfaceProvider> providers,std::string worker,Translator translate,r::ImageFactory images):impl_(std::make_unique<Impl>()){
    auto& i=*impl_;std::map<std::string,std::string> labels={{"inspector.item","Item"},{"inspector.information","Information"},{"inspector.summary","_Summary"},{"inspector.requested_summary","Requested summary"}};
    for(auto& label:labels){if(translate)label.second=translate(label.first);if(label.second.empty()||label.second.size()>1024||label.second.find('\0')!=std::string::npos||!g_utf8_validate(label.second.data(),static_cast<gssize>(label.second.size()),nullptr))throw protocol::Error("inspector.translation");}
    i.surface=std::make_unique<r::SceneSurface>(std::move(authority),std::move(policy),std::move(config),std::move(providers),[&i]{return i.invalidated();},std::move(worker),r::SurfaceAudience::inspector,std::move(images));
    i.store=gtk_tree_store_new(3,G_TYPE_STRING,G_TYPE_STRING,G_TYPE_STRING);i.root=gtk_box_new(GTK_ORIENTATION_VERTICAL,8);g_object_ref_sink(i.root);
    auto* scroll=gtk_scrolled_window_new(nullptr,nullptr);gtk_box_pack_start(GTK_BOX(i.root),scroll,TRUE,TRUE,0);
    i.tree=gtk_tree_view_new_with_model(i.model());g_object_ref_sink(i.tree);gtk_container_add(GTK_CONTAINER(scroll),i.tree);gtk_tree_view_set_enable_search(GTK_TREE_VIEW(i.tree),FALSE);
    for(const auto& pair:{std::make_pair(item_column,"inspector.item"),std::make_pair(information_column,"inspector.information")}){
        auto* cell=gtk_cell_renderer_text_new();auto* column=gtk_tree_view_column_new_with_attributes(labels.at(pair.second).c_str(),cell,"text",pair.first,nullptr);
        gtk_tree_view_column_set_resizable(column,TRUE);gtk_tree_view_column_set_sizing(column,GTK_TREE_VIEW_COLUMN_AUTOSIZE);gtk_tree_view_append_column(GTK_TREE_VIEW(i.tree),column);}
    atk_object_set_name(gtk_widget_get_accessible(i.tree),labels.at("inspector.information").c_str());atk_object_set_description(gtk_widget_get_accessible(i.tree),"syspane.scene.inspector");
    g_signal_connect(i.tree,"row-expanded",G_CALLBACK(+[](GtkTreeView*,GtkTreeIter* iter,GtkTreePath*,gpointer p){auto& owner=*static_cast<Impl*>(p);try{if(!owner.batch&&!owner.closed)owner.expansion[text(owner.model(),iter,key_column)]=true;}catch(...){owner.shut();}}),&i);
    g_signal_connect(i.tree,"row-collapsed",G_CALLBACK(+[](GtkTreeView*,GtkTreeIter* iter,GtkTreePath*,gpointer p){auto& owner=*static_cast<Impl*>(p);try{if(!owner.batch&&!owner.closed)owner.expansion[text(owner.model(),iter,key_column)]=false;}catch(...){owner.shut();}}),&i);
    i.button=gtk_button_new_with_mnemonic(labels.at("inspector.summary").c_str());g_object_ref_sink(i.button);gtk_box_pack_start(GTK_BOX(i.root),i.button,FALSE,FALSE,0);
    i.summary=gtk_label_new("");g_object_ref_sink(i.summary);gtk_label_set_xalign(GTK_LABEL(i.summary),0);gtk_label_set_line_wrap(GTK_LABEL(i.summary),TRUE);gtk_box_pack_start(GTK_BOX(i.root),i.summary,FALSE,FALSE,0);
    atk_object_set_description(gtk_widget_get_accessible(i.summary),"syspane.scene.requested-summary");atk_object_set_name(gtk_widget_get_accessible(i.summary),labels.at("inspector.requested_summary").c_str());
    g_signal_connect(i.button,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& owner=*static_cast<Impl*>(p);try{owner.request();}catch(...){owner.shut();}}),&i);
    g_signal_connect(i.root,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& owner=*static_cast<Impl*>(p);try{owner.shut();}catch(...){owner.clear();}}),&i);
}
SceneInspector::~SceneInspector()=default;
GtkWidget* SceneInspector::widget()const{impl_->owner();return impl_->root;}
d::DataAttachment SceneInspector::attach(const std::string& producer,const protocol::TelemetryBinding& binding,std::uint64_t now,const std::map<std::string,model::Tick>& ticks){auto& i=*impl_;d::DataAttachment result{d::DataCode::closed};i.run(now,ticks,[&]{result=i.surface->attach(producer,binding,now);});return result;}
d::DataResult SceneInspector::receive(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::string_view bytes,std::uint64_t now,const model::Tick& tick,const std::map<std::string,model::Tick>& other){auto& i=*impl_;d::DataResult result{d::DataCode::closed};auto ticks=other;ticks[producer]=tick;i.run(now,ticks,[&]{result=i.surface->receive(producer,token,revision,bytes,now,tick,other);});return result;}
d::DataCode SceneInspector::heartbeat(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now,const std::map<std::string,model::Tick>& ticks){auto& i=*impl_;d::DataCode result=d::DataCode::closed;i.run(now,ticks,[&]{result=i.surface->heartbeat(producer,token,revision,sequence,now);});return result;}
d::DataCode SceneInspector::gap(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t now,const std::map<std::string,model::Tick>& ticks){auto& i=*impl_;d::DataCode result=d::DataCode::closed;i.run(now,ticks,[&]{result=i.surface->gap(producer,token,revision,now);});return result;}
d::DataCode SceneInspector::disconnect(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t now,const std::map<std::string,model::Tick>& ticks){auto& i=*impl_;d::DataCode result=d::DataCode::closed;i.run(now,ticks,[&]{result=i.surface->disconnect(producer,token,revision,now);});return result;}
void SceneInspector::refresh(std::uint64_t now,const std::map<std::string,model::Tick>& ticks){impl_->run(now,ticks,[]{});}
void SceneInspector::policy(c::Policy policy,std::uint64_t now){auto& i=*impl_;i.owner();if(i.closed)return;i.clear();try{i.surface->policy(std::move(policy),now);i.run(now,{},[]{});}catch(...){i.shut();throw;}}
void SceneInspector::replace(r::SurfaceConfig config,std::uint64_t now){auto& i=*impl_;i.owner();if(i.closed)return;i.clear();try{i.surface->replace(std::move(config),now);i.run(now,{},[]{});}catch(...){i.shut();throw;}}
void SceneInspector::close(){impl_->owner();impl_->shut();}
bool SceneInspector::poll_image_jobs(){auto& i=*impl_;i.owner();try{const auto done=i.surface->poll_image_jobs();if(i.surface->status().code==r::SurfaceCode::alternative)i.clear();return done;}catch(...){i.shut();throw;}}
r::SurfaceStatus SceneInspector::status()const{impl_->owner();return impl_->surface->status();}
}
