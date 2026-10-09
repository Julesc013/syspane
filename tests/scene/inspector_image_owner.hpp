#pragma once
// Held native-task contract: the UI cannot destroy a cancelled, unreaped task.
namespace inspector_image_owner {
inline GtkTreeModel* model(GtkWidget* widget){
    if(GTK_IS_TREE_VIEW(widget))return gtk_tree_view_get_model(GTK_TREE_VIEW(widget));
    if(!GTK_IS_CONTAINER(widget))return nullptr;
    auto* children=gtk_container_get_children(GTK_CONTAINER(widget));GtkTreeModel* found=nullptr;
    for(auto* item=children;item&&!found;item=item->next)found=model(GTK_WIDGET(item->data));
    g_list_free(children);return found;
}
inline std::string information(GtkWidget* widget){
    auto* tree=model(widget);fixture::need(tree!=nullptr,"inspector image native model");GtkTreeIter iter;
    if(!gtk_tree_model_get_iter_first(tree,&iter))return {};
    gchar* text=nullptr;gtk_tree_model_get(tree,&iter,2,&text,-1);std::string result=text?text:"";g_free(text);return result;
}
struct State {bool ready=false,cancelled=false,reaped=false,destroyed=false;unsigned starts=0,takes=0;};
struct Task final:syspane::rendering::ImageTask {
    State& state;explicit Task(State& value):state(value){}
    ~Task()override{state.destroyed=true;}
    syspane::rendering::ImageJobStatus poll()override{
        using Code=syspane::rendering::ImageJobState;
        return {state.cancelled?(state.reaped?Code::cancelled:Code::stopping):state.ready?Code::ready:Code::running,{},state.reaped};
    }
    void cancel()override{state.cancelled=true;}
    syspane::scene::Image take()override{fixture::need(state.ready&&state.reaped&&!state.cancelled,"inspector image take authority");++state.takes;return {1,1,{0,255,0,255}};}
    std::uint64_t process_id()const override{return 0;}
};
inline void run(const std::string& root){
    namespace v=syspane::rendering;namespace ui=syspane::interfaces;
    for(bool complete:{false,true}){
        State state;const auto bytes=fixture::image_bytes(root);
        v::ImageFactory factory=[&](std::string media,std::string input){fixture::need(media=="image/png"&&input==bytes,"inspector exact image input");++state.starts;return std::make_unique<Task>(state);};
        auto cfg=fixture::image_config(root);auto policy=fixture::chart_policy();policy.disclosure[{"desktop","inspector"}]={"operational"};
        ui::SceneInspector view({true,"desktop",{"desktop"}},policy,std::move(cfg),{},"/must-not-use-path-fallback",{},factory);
        view.refresh(1);fixture::need(state.starts==1&&!state.destroyed&&!view.poll_image_jobs(),"inspector held image ownership");
        fixture::need(information(view.widget())=="Public image\nImage loading","inspector loading information");
        if(complete){state.ready=state.reaped=true;view.refresh(2);fixture::need(state.takes==1&&state.destroyed&&view.poll_image_jobs(),"inspector completed image adoption");fixture::need(information(view.widget())=="Public image\nImage ready","inspector ready information");}
        view.close();fixture::need(view.status().code==v::SurfaceCode::closed,"inspector closed surface");
        fixture::need(information(view.widget()).empty(),"inspector closed native information");
        if(!complete){fixture::need(state.cancelled&&!view.poll_image_jobs()&&!state.destroyed,"inspector cancellation awaits reap");state.reaped=true;fixture::need(view.poll_image_jobs()&&state.destroyed&&state.takes==0,"inspector cancelled task discarded");}
    }
    std::cerr<<"inspector injected image input/adoption/cancel/reap pass\n";
}
}
