#pragma once
#include "inspector_delivery_tests.hpp"
namespace inspector_phase_test {
using namespace inspector_delivery_test;
inline void run(const std::string& root){
    c::Policy policy;policy.available=true;policy.revision=7;
    for(const char* channel:{"inspector","accessibility"})policy.disclosure[{"console",channel}]={"operational"};
    auto binding=link();binding.channel="inspector";const r::DeliveryScope scope{11,4};
    r::TelemetryReceiver receiver(scope,policy,n::network_metrics(),binding,1000);
    need(receiver.receive(wire(document(123,1),binding),1001,tick(100)).code==r::DataCode::accepted,"phase input");
    const auto delivery=receiver.view(1001);
    using Phase=ui::SceneInspector::Phase;
    const std::vector<Phase> expected{Phase::admission,Phase::presentation,Phase::paint};
    std::vector<Phase> seen;std::map<Phase,std::uint64_t> times;
    ui::SceneInspector inspector({true,"console",{"console"}},policy,config(root),{provider()});
    inspector.deliver(delivery,scope,1001,[&](Phase phase,std::uint64_t elapsed,bool completed){
        need(completed,"phase completed");seen.push_back(phase);times[phase]=elapsed;return true;
    });
    need(seen==expected&&times.at(Phase::paint)>=times.at(Phase::presentation),"phase ordering and containment");
    shows(inspector,"123 byte","lease=active","age=0 ns");
    inspector.refresh(1001,{{"P1",tick(100)}});
    need(seen==expected,"observer not retained");
    inspector.close();
    for(const auto fault:expected)for(bool throws:{false,true}){
        ui::SceneInspector victim({true,"console",{"console"}},policy,config(root),{provider()});
        victim.deliver(delivery,scope,1001);need(!information(victim).empty(),"phase populated native tree");
        std::vector<Phase> events;bool failed=false;
        try{victim.refresh(1001,{{"P1",tick(100)}},[&](Phase phase,std::uint64_t,bool completed){
            need(completed,"phase fault completion");events.push_back(phase);
            if(phase!=fault)return true;
            if(throws)throw std::runtime_error("phase.test_throw");
            return false;
        });}catch(const syspane::protocol::Error& e){failed=std::string(e.what())=="inspector.phase_observer";}
        const auto count=static_cast<std::size_t>(std::find(expected.begin(),expected.end(),fault)-expected.begin())+1;
        need(failed&&events==std::vector<Phase>(expected.begin(),expected.begin()+count),"phase fault stops observation");
        need(victim.status().code==v::SurfaceCode::closed&&information(victim).empty(),"phase fault erases and closes");
        victim.refresh(1002,{},[&](Phase,std::uint64_t,bool){throw std::runtime_error("closed observer invoked");return false;});
    }
    std::cerr<<"inspector phases: ordering, lifetime, six refusal/throw paths pass\n";
}
}
