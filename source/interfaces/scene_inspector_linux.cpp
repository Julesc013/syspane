#include "scene_inspector.hpp"
#include "scene_inspector_admission.hpp"
#include "scene_inspector_model.hpp"
#include <gtk/gtk.h>
#include <thread>
#include <limits>
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
    std::unique_ptr<InspectorAdmission> admission;
    std::shared_ptr<const InspectorRenderFactory> renders;
    std::shared_ptr<const InspectorRenderSetup> setup;
    std::unique_ptr<InspectorRenderTask> renderer;
    std::unique_ptr<InspectorRenderResult> adopted;
    r::SurfaceStatus rendered;
    std::uint64_t last_ticket=0,next_submit=0;std::optional<std::uint64_t> highest_policy;
    bool replacement=false;
    std::map<std::string,GtkTreeIter> rows;
    std::map<std::string,bool> expansion;
    GtkTreeModel* model()const{return GTK_TREE_MODEL(store);}
    void owner()const{if(thread!=std::this_thread::get_id()||batch)throw std::logic_error("inspector.owner");}
    void clear_summary(){summary_key.clear();if(summary)gtk_label_set_text(GTK_LABEL(summary),"");}
    void blank(GtkTreeIter* parent=nullptr){GtkTreeIter iter;if(!store||!gtk_tree_model_iter_children(model(),&iter,parent))return;
        do{blank(&iter);gtk_tree_store_set(store,&iter,key_column,"",item_column,"",information_column,"",-1);}while(gtk_tree_model_iter_next(model(),&iter));}
    void clear(){if(admission)admission->reset();adopted.reset();clear_summary();rows.clear();expansion.clear();if(store){blank();gtk_tree_store_clear(store);}
        if(tree){auto* columns=gtk_tree_view_get_columns(GTK_TREE_VIEW(tree));
            for(auto* item=columns;item;item=item->next)gtk_tree_view_column_queue_resize(GTK_TREE_VIEW_COLUMN(item->data));
            g_list_free(columns);}}
    bool invalidated(){if(!batch)clear();return true;}
    void shut(){closed=true;replacement=false;setup.reset();clear();if(renderer)renderer->close();if(surface&&!batch)surface->close();rendered={r::SurfaceCode::closed,0,0,"surface.closed"};}
    ~Impl(){shut();admission.reset();surface.reset();if(root)gtk_widget_destroy(root);for(auto* w:{button,summary,tree,root})if(w)g_object_unref(w);if(store)g_object_unref(store);}
    bool reconcile(const std::vector<InspectorRow>& desired,GtkTreeIter* parent=nullptr){
        bool changed=false;
        std::map<std::string,GtkTreeIter> current;GtkTreeIter iter;
        if(gtk_tree_model_iter_children(model(),&iter,parent))do{current.emplace(text(model(),&iter,key_column),iter);}while(gtk_tree_model_iter_next(model(),&iter));
        std::set<std::string> wanted;for(const auto& row:desired)wanted.insert(row.key);
        for(auto& old:current)if(!wanted.count(old.first)){blank(&old.second);gtk_tree_store_set(store,&old.second,key_column,"",item_column,"",information_column,"",-1);gtk_tree_store_remove(store,&old.second);changed=true;}
        GtkTreeIter previous;bool first=true;int expected=0;
        for(const auto& row:desired){auto found=current.find(row.key);GtkTreeIter at;
            if(found==current.end()){gtk_tree_store_insert_after(store,&at,parent,first?nullptr:&previous);changed=true;}else at=found->second;
            auto* path=gtk_tree_model_get_path(model(),&at);const auto position=gtk_tree_path_get_indices(path)[gtk_tree_path_get_depth(path)-1];gtk_tree_path_free(path);
            if(position!=expected){gtk_tree_store_move_after(store,&at,first?nullptr:&previous);changed=true;}
            if(text(model(),&at,key_column)!=row.key||text(model(),&at,item_column)!=row.item||text(model(),&at,information_column)!=row.information){
                gtk_tree_store_set(store,&at,key_column,row.key.c_str(),item_column,row.item.c_str(),information_column,row.information.c_str(),-1);changed=true;}
            rows.emplace(row.key,at);if(reconcile(row.children,&at))changed=true;previous=at;first=false;++expected;
        }
        return changed;
    }
    void present(const r::SurfaceFrame* frame){
        if(!frame||closed){clear();return;}present_rows(inspector_rows(*frame));
    }
    void present_rows(const std::vector<InspectorRow>& projected){
        if(closed){clear();return;}
        std::vector<std::string> selection;GtkTreePath* path=nullptr;GtkTreeViewColumn* column=nullptr;gtk_tree_view_get_cursor(GTK_TREE_VIEW(tree),&path,&column);
        if(path)gtk_tree_path_free(path);
        GtkTreeIter selected;if(gtk_tree_selection_get_selected(gtk_tree_view_get_selection(GTK_TREE_VIEW(tree)),nullptr,&selected)){do{selection.push_back(text(model(),&selected,key_column));GtkTreeIter parent;if(!gtk_tree_model_iter_parent(model(),&parent,&selected))break;selected=parent;}while(true);}
        rows.clear();if(!reconcile(projected))return;
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
    void run(std::uint64_t now,const std::map<std::string,model::Tick>& ticks,const std::function<void()>& action,const PhaseObserver& observer={}){
        owner();if(renders){shut();throw protocol::Error("inspector.async_operation");}if(closed)return;batch=true;
        bool observing=static_cast<bool>(observer);
        const auto emit=[&](Phase phase,gint64 begin,bool completed){
            if(!observing)return;
            bool accepted=false;
            try{accepted=observer(phase,static_cast<std::uint64_t>(g_get_monotonic_time()-begin),completed);}catch(...){}
            if(!accepted){observing=false;throw protocol::Error("inspector.phase_observer");}
        };
        const auto measure=[&](Phase phase,const auto& operation){
            if(!observing){operation();return;}
            const auto begin=g_get_monotonic_time();
            try{operation();}catch(...){emit(phase,begin,false);throw;}
            emit(phase,begin,true);
        };
        try{measure(Phase::admission,action);if(!closed)measure(Phase::paint,[&]{surface->paint(now,ticks,[&](auto,const auto* frame){measure(Phase::presentation,[&]{present(frame);});});});batch=false;if(closed)surface->close();}
        catch(...){batch=false;shut();throw;}
    }
    void update(InspectorRenderInput input,std::uint64_t stamp,const PhaseObserver& observer){
        owner();if(closed)return;
        if(!setup||input.scope.profile!=setup->profile){shut();return;}
        bool observing=static_cast<bool>(observer);batch=true;std::uint64_t acknowledgement=0;
        const auto emit=[&](Phase phase,gint64 begin,bool completed){
            if(!observing)return;
            bool accepted=false;
            try{accepted=observer(phase,static_cast<std::uint64_t>(g_get_monotonic_time()-begin),completed);}catch(...){}
            if(!accepted){observing=false;throw protocol::Error("inspector.phase_observer");}
        };
        const auto measure=[&](Phase phase,const auto& operation){
            if(!observing){operation();return;}const auto begin=g_get_monotonic_time();
            try{operation();}catch(...){emit(phase,begin,false);throw;}emit(phase,begin,true);
        };
        try{
            measure(Phase::admission,[&]{
                if(adopted&&adopted->active&&!adopted->current(input,setup->profile,stamp,false))clear();
                if(replacement){
                    if(renderer&&!renderer->status().stopped)return;
                    renderer.reset();last_ticket=next_submit=0;replacement=false;
                }
                if(!setup->policy.available){rendered={r::SurfaceCode::restricted,0,0,"policy.denied"};return;}
                if(!renderer)renderer=(*renders)(setup);
                if(stamp>=next_submit){
                    (void)renderer->submit(input);
                    if(stamp>std::numeric_limits<std::uint64_t>::max()-100)throw protocol::Error("inspector.render_clock");
                    next_submit=stamp+100;
                }
            });
            measure(Phase::adoption,[&]{
                if(replacement||!renderer||!setup->policy.available)return;
                const auto state=renderer->status();
                if(!state.error.empty()){shut();rendered={r::SurfaceCode::alternative,0,0,state.error};return;}
                auto value=renderer->take();if(!value||value->ticket<=last_ticket||!value->current(input,setup->profile,stamp))return;
                // Keep the original qualified projection between unchanged native
                // publications. Clock-only age updates must not churn GTK cells.
                if(adopted&&adopted->active&&value->active&&!adopted->time_dependent&&!value->time_dependent&&
                   adopted->input.delivery->frame==value->input.delivery->frame&&
                   adopted->status.code==value->status.code&&adopted->status.reason==value->status.reason&&
                   adopted->status.widgets==value->status.widgets&&adopted->status.pixels==value->status.pixels)return;
                measure(Phase::presentation,[&]{present_rows(value->rows);});
                last_ticket=value->ticket;rendered=value->status;
                value->rows.clear();adopted=std::move(value);
                acknowledgement=last_ticket;
            });
            if(acknowledgement)renderer->acknowledge(acknowledgement);
            batch=false;
        }catch(...){batch=false;shut();throw;}
    }
    void retire(std::shared_ptr<const InspectorRenderSetup> next){
        clear();if(renderer)renderer->close();setup=std::move(next);replacement=true;rendered={r::SurfaceCode::empty,0,0,{}};
    }
    void request(){if(closed||batch)return;GtkTreeIter selected;auto* selection=gtk_tree_view_get_selection(GTK_TREE_VIEW(tree));
        if(!gtk_tree_selection_get_selected(selection,nullptr,&selected)){clear_summary();return;}
        summary_key=text(model(),&selected,key_column);const auto value=text(model(),&selected,item_column)+"\n"+text(model(),&selected,information_column);
        gtk_label_set_text(GTK_LABEL(summary),value.c_str());}
};
SceneInspector::SceneInspector(c::Authority authority,c::Policy policy,r::SurfaceConfig config,std::vector<r::SurfaceProvider> providers,std::string worker,Translator translate,r::ImageFactory images,std::shared_ptr<const InspectorRenderFactory> renders,std::uint64_t profile):impl_(std::make_unique<Impl>()){
    auto& i=*impl_;std::map<std::string,std::string> labels={{"inspector.item","Item"},{"inspector.information","Information"},{"inspector.summary","_Summary"},{"inspector.requested_summary","Requested summary"}};
    for(auto& label:labels){if(translate)label.second=translate(label.first);if(label.second.empty()||label.second.size()>1024||label.second.find('\0')!=std::string::npos||!g_utf8_validate(label.second.data(),static_cast<gssize>(label.second.size()),nullptr))throw protocol::Error("inspector.translation");}
    if(renders){
        if(!profile||!worker.empty()||images)throw protocol::Error("inspector.render_setup");
        auto setup=std::make_shared<InspectorRenderSetup>();setup->authority=std::move(authority);setup->policy=std::move(policy);
        setup->config=std::make_shared<const r::SurfaceConfig>(std::move(config));setup->providers=std::move(providers);setup->profile=profile;
        if(setup->policy.available)i.highest_policy=setup->policy.revision;
        i.setup=std::move(setup);i.renders=std::move(renders);
    }else{
        i.surface=std::make_unique<r::SceneSurface>(std::move(authority),std::move(policy),std::move(config),std::move(providers),[&i]{return i.invalidated();},std::move(worker),r::SurfaceAudience::inspector,std::move(images));
        i.admission=std::make_unique<InspectorAdmission>(*i.surface);
    }
    i.store=gtk_tree_store_new(3,G_TYPE_STRING,G_TYPE_STRING,G_TYPE_STRING);i.root=gtk_box_new(GTK_ORIENTATION_VERTICAL,8);g_object_ref_sink(i.root);
    auto* scroll=gtk_scrolled_window_new(nullptr,nullptr);gtk_box_pack_start(GTK_BOX(i.root),scroll,TRUE,TRUE,0);
    i.tree=gtk_tree_view_new_with_model(i.model());g_object_ref_sink(i.tree);gtk_container_add(GTK_CONTAINER(scroll),i.tree);gtk_tree_view_set_enable_search(GTK_TREE_VIEW(i.tree),FALSE);
    for(const auto& pair:{std::make_pair(item_column,"inspector.item"),std::make_pair(information_column,"inspector.information")}){
        auto* cell=gtk_cell_renderer_text_new();auto* column=gtk_tree_view_column_new_with_attributes(labels.at(pair.second).c_str(),cell,"text",pair.first,nullptr);
        gtk_tree_view_column_set_sizing(column,GTK_TREE_VIEW_COLUMN_GROW_ONLY);gtk_tree_view_column_set_resizable(column,TRUE);gtk_tree_view_append_column(GTK_TREE_VIEW(i.tree),column);}
    atk_object_set_name(gtk_widget_get_accessible(i.tree),labels.at("inspector.information").c_str());atk_object_set_description(gtk_widget_get_accessible(i.tree),"syspane.scene.inspector");
    g_signal_connect(i.tree,"row-expanded",G_CALLBACK(+[](GtkTreeView*,GtkTreeIter* iter,GtkTreePath*,gpointer p){auto& owner=*static_cast<Impl*>(p);try{if(!owner.batch&&!owner.closed)owner.expansion[text(owner.model(),iter,key_column)]=true;}catch(...){owner.shut();}}),&i);
    g_signal_connect(i.tree,"row-collapsed",G_CALLBACK(+[](GtkTreeView*,GtkTreeIter* iter,GtkTreePath*,gpointer p){auto& owner=*static_cast<Impl*>(p);try{if(!owner.batch&&!owner.closed)owner.expansion[text(owner.model(),iter,key_column)]=false;}catch(...){owner.shut();}}),&i);
    i.button=gtk_button_new_with_mnemonic(labels.at("inspector.summary").c_str());g_object_ref_sink(i.button);gtk_box_pack_start(GTK_BOX(i.root),i.button,FALSE,FALSE,0);
    i.summary=gtk_label_new("");g_object_ref_sink(i.summary);gtk_label_set_xalign(GTK_LABEL(i.summary),0);gtk_label_set_line_wrap(GTK_LABEL(i.summary),TRUE);gtk_box_pack_start(GTK_BOX(i.root),i.summary,FALSE,FALSE,0);
    atk_object_set_description(gtk_widget_get_accessible(i.summary),"syspane.scene.requested-summary");atk_object_set_name(gtk_widget_get_accessible(i.summary),labels.at("inspector.requested_summary").c_str());
    g_signal_connect(i.button,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& owner=*static_cast<Impl*>(p);try{owner.request();}catch(...){owner.shut();}}),&i);
    g_signal_connect(i.root,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& owner=*static_cast<Impl*>(p);try{owner.shut();}catch(...){owner.clear();}}),&i);
    if(i.renders&&i.setup->policy.available)i.renderer=(*i.renders)(i.setup);
}
SceneInspector::~SceneInspector()=default;
GtkWidget* SceneInspector::widget()const{impl_->owner();return impl_->root;}
bool SceneInspector::background()const{impl_->owner();return static_cast<bool>(impl_->renders);}
d::DataAttachment SceneInspector::attach(const std::string& producer,const protocol::TelemetryBinding& binding,std::uint64_t now,const std::map<std::string,model::Tick>& ticks){auto& i=*impl_;d::DataAttachment result{d::DataCode::closed};i.run(now,ticks,[&]{result=i.surface->attach(producer,binding,now);});return result;}
d::DataResult SceneInspector::receive(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::string_view bytes,std::uint64_t now,const model::Tick& tick,const std::map<std::string,model::Tick>& other){auto& i=*impl_;d::DataResult result{d::DataCode::closed};auto ticks=other;ticks[producer]=tick;i.run(now,ticks,[&]{result=i.surface->receive(producer,token,revision,bytes,now,tick,other);});return result;}
d::DataCode SceneInspector::heartbeat(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now,const std::map<std::string,model::Tick>& ticks){auto& i=*impl_;d::DataCode result=d::DataCode::closed;i.run(now,ticks,[&]{result=i.surface->heartbeat(producer,token,revision,sequence,now);});return result;}
d::DataCode SceneInspector::gap(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t now,const std::map<std::string,model::Tick>& ticks){auto& i=*impl_;d::DataCode result=d::DataCode::closed;i.run(now,ticks,[&]{result=i.surface->gap(producer,token,revision,now);});return result;}
d::DataCode SceneInspector::disconnect(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t now,const std::map<std::string,model::Tick>& ticks){auto& i=*impl_;d::DataCode result=d::DataCode::closed;i.run(now,ticks,[&]{result=i.surface->disconnect(producer,token,revision,now);});return result;}
void SceneInspector::refresh(std::uint64_t now,const std::map<std::string,model::Tick>& ticks,const PhaseObserver& observer){auto& i=*impl_;i.owner();if(i.renders){if(i.closed)return;InspectorRenderInput input;input.scope={i.setup->profile,0};input.ticks=ticks;i.update(std::move(input),now,observer);}else i.run(now,ticks,[]{},observer);}
void SceneInspector::deliver(const d::TelemetryDelivery& value,d::DeliveryScope current,std::uint64_t now,const PhaseObserver& observer){
    auto& i=*impl_;i.owner();if(i.closed)return;
    if(i.renders){InspectorRenderInput input;input.delivery=value;input.scope=current;i.update(std::move(input),now,observer);return;}
    if(!i.admission->compatible(current)){i.shut();return;}
    std::map<std::string,model::Tick> ticks;
    i.run(now,ticks,[&]{
        ticks=i.admission->admit(value,current,now);
    },observer);
}
void SceneInspector::policy(c::Policy policy,std::uint64_t now){auto& i=*impl_;i.owner();if(i.closed)return;
    if(i.renders){
        if(policy.available&&i.highest_policy&&policy.revision<=*i.highest_policy)policy.available=false;
        if(policy.available)i.highest_policy=policy.revision;
        auto next=std::make_shared<InspectorRenderSetup>(*i.setup);next->policy=std::move(policy);i.retire(std::move(next));
        if(!i.setup->policy.available)i.rendered={r::SurfaceCode::restricted,0,0,"policy.denied"};
        return;
    }
    i.clear();try{i.surface->policy(std::move(policy),now);i.run(now,{},[]{});}catch(...){i.shut();throw;}}
void SceneInspector::replace(r::SurfaceConfig config,std::uint64_t now){auto& i=*impl_;i.owner();if(i.closed)return;
    if(i.renders){auto next=std::make_shared<InspectorRenderSetup>(*i.setup);next->config=std::make_shared<const r::SurfaceConfig>(std::move(config));i.retire(std::move(next));return;}
    i.clear();try{i.surface->replace(std::move(config),now);i.run(now,{},[]{});}catch(...){i.shut();throw;}}
void SceneInspector::close(){impl_->owner();impl_->shut();}
bool SceneInspector::poll_image_jobs(){auto& i=*impl_;i.owner();if(i.renders)return !i.renderer||i.renderer->status().stopped;try{const auto done=i.surface->poll_image_jobs();if(i.surface->status().code==r::SurfaceCode::alternative)i.clear();return done;}catch(...){i.shut();throw;}}
r::SurfaceStatus SceneInspector::status()const{impl_->owner();return impl_->renders?impl_->rendered:impl_->surface->status();}
}
