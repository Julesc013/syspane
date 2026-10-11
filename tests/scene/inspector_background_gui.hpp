#pragma once
#include "inspector_render_tests.hpp"
#include "scene_inspector.hpp"
#include <gtk/gtk.h>

namespace inspector_background_gui {
using namespace fixture;namespace ui=syspane::interfaces;
inline GtkTreeModel* model(GtkWidget* widget){
    if(GTK_IS_TREE_VIEW(widget))return gtk_tree_view_get_model(GTK_TREE_VIEW(widget));
    if(!GTK_IS_CONTAINER(widget))return nullptr;
    auto* children=gtk_container_get_children(GTK_CONTAINER(widget));GtkTreeModel* result=nullptr;
    for(auto* item=children;item&&!result;item=item->next)result=model(GTK_WIDGET(item->data));
    g_list_free(children);return result;
}
inline void run(const std::string& root){
    namespace test=inspector_render_test;
    auto gate=std::make_shared<test::Gate>();auto held=std::make_shared<std::atomic<bool>>(false);
    auto factory=ui::threaded_inspector_renderer({},[gate,held](std::uint64_t ticket){if(ticket==3&&!held->exchange(true))gate->hold();});
    unsigned starts=0;ui::InspectorRenderTask* original=nullptr;
    auto counted=std::make_shared<const ui::InspectorRenderFactory>([&](auto setup){++starts;auto task=factory(std::move(setup));if(starts==1)original=task.get();return task;});
    auto grant=inspector_admission_owner_test::grant();auto b=inspector_admission_owner_test::binding();
    auto receiver=std::make_unique<r::TelemetryReceiver>(r::DeliveryScope{11,4},grant,n::network_metrics(),b,test::now());
    ui::SceneInspector view({true,"console",{"console"}},grant,config(root),{provider()},"",{}, {},counted,11);
    test::ReleaseGate release{gate};
    need(receiver->receive(wire(document(),b),test::now(),tick()).code==r::DataCode::accepted,"GUI barrier initial receipt");
    std::uint64_t clock=100;
    const auto pulse=[&]{receiver->sample(tick(clock),test::now());view.deliver(receiver->view(test::now()),{11,4},test::now());};
    const auto end=test::now()+2500;
    while(!gtk_tree_model_iter_n_children(model(view.widget()),nullptr)){need(test::now()<end,"GUI background initial row deadline");pulse();g_usleep(1000);}
    clock=200;
    while(gate->arrived.wait_for(std::chrono::milliseconds(0))!=std::future_status::ready){need(test::now()<end,"GUI claimed barrier deadline");pulse();g_usleep(1000);}
    gate->arrived.get();need(original&&original->status().running,"GUI worker is held in claimed work");
    GtkTreeIter stable;need(gtk_tree_model_get_iter_first(model(view.widget()),&stable),"stable original qualified native row");gchar* stable_text=nullptr;
    gtk_tree_model_get(model(view.widget()),&stable,2,&stable_text,-1);const std::string qualified=stable_text?stable_text:"";g_free(stable_text);
    need(qualified.find("age=0 ns")!=std::string::npos&&qualified.find("age=100 ns")==std::string::npos,"duplicate native frame keeps its original qualified GTK projection despite fresh clock-only jobs");
    auto denied=grant;denied.revision=8;denied.disclosure.erase({"console","inspector"});
    const auto begin=g_get_monotonic_time();view.policy(denied,test::now());
    need(gtk_tree_model_iter_n_children(model(view.widget()),nullptr)==0&&g_get_monotonic_time()-begin<200000,"held worker cannot delay immediate native policy erasure");
    view.replace(config(root),test::now());grant.revision=9;view.policy(grant,test::now());receiver->withdraw(test::now());
    view.deliver(receiver->view(test::now()),{11,4},test::now());
    need(starts==1&&original->status().closing&&!original->status().stopped&&gtk_tree_model_iter_n_children(model(view.widget()),nullptr)==0,"latest topology/grant waits for old claimed owner; old rows stay erased");
    gate->open();const auto drained=test::now()+2500;
    while(!original->status().stopped){need(test::now()<drained,"retired GUI renderer deadline");g_usleep(1000);}
    b.policy_revision=9;receiver=std::make_unique<r::TelemetryReceiver>(r::DeliveryScope{11,4},grant,n::network_metrics(),b,test::now());
    need(receiver->receive(wire(document(456,1),b),test::now(),tick()).code==r::DataCode::accepted,"new policy fresh attachment receipt");
    const auto fresh=test::now()+2500;
    while(!gtk_tree_model_iter_n_children(model(view.widget()),nullptr)){need(test::now()<fresh,"new background GUI attachment deadline");pulse();g_usleep(1000);}
    need(starts==2,"one latest replacement task follows old destruction");
    GtkTreeIter row;need(gtk_tree_model_get_iter_first(model(view.widget()),&row),"new current native row");gchar* text=nullptr;
    gtk_tree_model_get(model(view.widget()),&row,2,&text,-1);const std::string value=text?text:"";g_free(text);
    need(value.find("456 byte")!=std::string::npos&&value.find("123 byte")==std::string::npos,"fresh grant cannot resurrect old held result");
    view.deliver(receiver->view(test::now()),{12,4},test::now());need(view.status().code==v::SurfaceCode::closed&&gtk_tree_model_iter_n_children(model(view.widget()),nullptr)==0,"background profile closure erases native cells");
    const auto stopped=test::now()+2500;while(!view.poll_image_jobs()){need(test::now()<stopped,"background GUI owner shutdown deadline");g_usleep(1000);}
    bool refused=false;std::thread foreign([&]{try{view.refresh(test::now());}catch(const std::logic_error& e){refused=std::string(e.what())=="inspector.owner";}});foreign.join();
    need(refused,"closed background refresh still rejects a foreign GUI owner before reading mutable state");
    std::cerr<<"background GTK held-work/policy/topology/fresh-grant/profile/shutdown pass\n";
}
}
