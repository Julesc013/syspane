#pragma once
#include "inspector_delivery_tests.hpp"
#include "chart_fixture.hpp"
#include <iostream>
namespace inspector_delivery_chart_test {
using namespace fixture;
inline std::string cell(GtkTreeModel* model,GtkTreeIter* row,int column){
    gchar* value=nullptr;gtk_tree_model_get(model,row,column,&value,-1);
    std::string out=value?value:"";g_free(value);return out;
}
inline void run(const std::string& root){
    const auto cases=read(root+"/../../../tests/scene","inspector-delivery-cases.json");
    for(const auto& scenario:cases["cases"]){
        const auto name=scenario["id"].get<std::string>();
        try{
            c::Policy policy;policy.available=true;policy.revision=7;
            for(const char* channel:{"inspector","accessibility","history"})policy.disclosure[{"console",channel}]={"operational"};
            auto binding=link();binding.channel="inspector";const r::DeliveryScope scope{11,4};
            r::TelemetryReceiver receiver(scope,policy,n::network_metrics(),binding,1000);
            syspane::interfaces::SceneInspector inspector({true,"console",{"console"}},policy,chart_config(root),{provider()});
            std::uint64_t now=1000,clock=0;
            for(const auto& step:scenario["steps"]){
                ++now;const auto measured=step["time"].get<std::uint64_t>();clock=std::max(clock,measured);
                auto doc=chart_document(step["value"],step["generation"],measured);
                if(step.value("failed",false))for(auto& observation:doc["observations"])if(observation["field"]=="network.receive_bytes"){
                    observation["acquisition"]="failed";observation["freshness"]="stale";
                    observation["error"]={{"code","fixture.failed"},{"message","Controlled failure"},{"retryable",true}};
                }
                const auto accepted=receiver.receive(wire(doc,binding),now,tick(clock));
                if(accepted.code!=(step.value("duplicate",false)?r::DataCode::duplicate:r::DataCode::accepted))
                    throw std::runtime_error("chart receiver admission at generation "+step["generation"].dump()+"; code "+std::to_string(static_cast<int>(accepted.code)));
                if(!step.contains("points"))continue;
                inspector.deliver(receiver.view(now),scope,now);
                auto* native=inspector_delivery_test::tree(inspector.widget());need(native,"native chart tree");
                auto* model=gtk_tree_view_get_model(GTK_TREE_VIEW(native));GtkTreeIter parent,row;
                need(gtk_tree_model_iter_n_children(model,nullptr)==1&&gtk_tree_model_get_iter_first(model,&parent),"one chart root");
                need(gtk_tree_model_iter_n_children(model,&parent)==static_cast<int>(step["points"].size()),"exact chart point count");
                std::size_t index=0;
                if(gtk_tree_model_iter_children(model,&row,&parent))do{
                    const auto& expected=step["points"][index++];
                    const auto item="Point "+expected[0].dump()+" ns";
                    const auto information=expected[1].dump()+" byte; generation "+expected[2].dump()+"; "+expected[3].get<std::string>();
                    if(cell(model,&row,1)!=item||cell(model,&row,2)!=information)
                        throw std::runtime_error("expected "+item+" | "+information+"; actual "+cell(model,&row,1)+" | "+cell(model,&row,2));
                }while(gtk_tree_model_iter_next(model,&row));
                need((cell(model,&parent,2).find("Gap pending")!=std::string::npos)==step.value("gap_pending",false),"exact pending-break state");
            }
            std::cerr<<"delivery-chart "<<name<<": pass\n";
        }catch(const std::exception& error){throw std::runtime_error(name+": "+error.what());}
    }
}
}
