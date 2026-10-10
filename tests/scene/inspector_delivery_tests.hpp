#pragma once
#include "surface_fixture.hpp"
#include "scene_inspector.hpp"
#include <gtk/gtk.h>
namespace inspector_delivery_test {
using namespace fixture;
namespace ui=syspane::interfaces;
inline GtkWidget* tree(GtkWidget* widget){
    if(GTK_IS_TREE_VIEW(widget))return widget;
    if(!GTK_IS_CONTAINER(widget))return nullptr;
    auto* children=gtk_container_get_children(GTK_CONTAINER(widget));GtkWidget* found=nullptr;
    for(auto* p=children;p&&!found;p=p->next)found=tree(GTK_WIDGET(p->data));
    g_list_free(children);return found;
}
inline std::string information(ui::SceneInspector& inspector){
    auto* view=tree(inspector.widget());need(view!=nullptr,"delivery native tree");
    auto* model=gtk_tree_view_get_model(GTK_TREE_VIEW(view));GtkTreeIter first;
    if(!gtk_tree_model_get_iter_first(model,&first))return {};
    gchar* text=nullptr;gtk_tree_model_get(model,&first,2,&text,-1);std::string out=text?text:"";g_free(text);return out;
}
inline void shows(ui::SceneInspector& inspector,const char* value,const char* lease,const char* age){
    const auto text=information(inspector);
    need(text.find(value)!=std::string::npos&&text.find(lease)!=std::string::npos&&text.find(age)!=std::string::npos,"delivery native information");
}
inline void run(const std::string& root){
    c::Policy policy;policy.available=true;policy.revision=7;
    for(const char* channel:{"inspector","accessibility"})policy.disclosure[{"console",channel}]={"operational"};
    auto binding=link();binding.channel="inspector";const r::DeliveryScope scope{11,4};
    r::TelemetryReceiver receiver(scope,policy,n::network_metrics(),binding,1000);
    ui::SceneInspector inspector({true,"console",{"console"}},policy,config(root),{provider()});
    need(receiver.receive(wire(document(123,1),binding),1001,tick(100)).code==r::DataCode::accepted,"delivery initial validation");
    inspector.deliver(receiver.view(1001),scope,1001);shows(inspector,"123 byte","lease=active","age=0 ns");
    need(receiver.receive(wire(document(987,2),binding),1002,tick(101)).code==r::DataCode::accepted,"delivery queued replacement");
    inspector.deliver(receiver.view(1002),scope,1300);shows(inspector,"123 byte","lease=retained","age=unknown");
    need(information(inspector).find("987 byte")==std::string::npos,"stale clock cannot display queued value");
    need(receiver.sample(tick(200),1301)==r::DataCode::accepted,"delivery clock refresh");
    inspector.deliver(receiver.view(1301),scope,1310);shows(inspector,"987 byte","lease=active","age=100 ns");
    need(receiver.heartbeat(0,2000)==r::DataCode::accepted&&receiver.sample(tick(300),2000)==r::DataCode::accepted,"delivery native heartbeat");
    inspector.deliver(receiver.view(2000),scope,2000);
    need(receiver.receive(wire(document(777,3),binding),2001,tick(301)).code==r::DataCode::accepted,"delivery unpublished value");
    const auto delayed=receiver.view(2001);inspector.deliver(delayed,scope,5000);
    shows(inspector,"987 byte","lease=retained","age=unknown");need(information(inspector).find("777 byte")==std::string::npos,"expired native deadline drops unseen value");
    need(receiver.heartbeat(1,4999)==r::DataCode::accepted&&receiver.sample(tick(400),4999)==r::DataCode::accepted,"independent worker stays live");
    const auto live=receiver.view(4999);inspector.deliver(live,scope,5001);shows(inspector,"777 byte","lease=active","age=300 ns");
    receiver.disconnect(5002);inspector.deliver(receiver.view(5002),scope,5002);shows(inspector,"777 byte","lease=retained","age=unknown");
    inspector.policy({},5003);need(information(inspector).empty(),"policy erases native information and saved delivery");
    ui::SceneInspector replacement({true,"console",{"console"}},policy,config(root),{provider()});
    replacement.deliver(live,scope,5010);shows(replacement,"777 byte","lease=active","age=300 ns");
    replacement.deliver(live,{12,4},5011);need(information(replacement).empty()&&replacement.status().code==v::SurfaceCode::closed,"different profile cannot retain old data");
}
}
