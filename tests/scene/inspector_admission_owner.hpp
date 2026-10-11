#pragma once
#include "chart_fixture.hpp"
#include "scene_inspector_admission.hpp"
#include "scene_inspector_model.hpp"
#include <algorithm>
#include <future>
#include <iostream>
#include <thread>

namespace inspector_admission_owner_test {
using namespace fixture;
namespace ui=syspane::interfaces;
inline c::Policy grant(){
    c::Policy p;p.available=true;p.revision=7;
    for(const char* channel:{"inspector","accessibility","history"})p.disclosure[{"console",channel}]={"operational"};
    return p;
}
inline p::TelemetryBinding binding(){auto b=link();b.channel="inspector";return b;}
struct Owner {
    v::SceneSurface surface;
    ui::InspectorAdmission admission;
    Owner(const std::string& root,bool chart=false):
        surface({true,"console",{"console"}},grant(),chart?chart_config(root):config(root),{provider()},[]{return true;},{},v::SurfaceAudience::inspector),admission(surface){}
    std::vector<ui::InspectorRow> show(const r::TelemetryDelivery& value,r::DeliveryScope current,std::uint64_t now){
        const auto ticks=admission.admit(value,current,now);std::vector<ui::InspectorRow> result;
        surface.paint(now,ticks,[&](auto,const auto* frame){if(frame)result=ui::inspector_rows(*frame);});return result;
    }
};
inline std::string information(const std::vector<ui::InspectorRow>& rows){need(rows.size()==1,"one admission scalar row");return rows[0].information;}
inline void shows(const std::vector<ui::InspectorRow>& rows,const char* value,const char* lease,const char* age){
    const auto text=information(rows);need(text.find(value)!=std::string::npos&&text.find(lease)!=std::string::npos&&text.find(age)!=std::string::npos,"exact admission information");
}
inline std::vector<std::string> scalar(const std::string& root){
    const r::DeliveryScope scope{11,4};const auto b=binding();r::TelemetryReceiver receiver(scope,grant(),n::network_metrics(),b,1000);Owner owner(root);
    std::vector<std::string> observed;
    const auto record=[&](const auto& delivery,std::uint64_t now,const char* value,const char* lease,const char* age){
        auto rows=owner.show(delivery,scope,now);shows(rows,value,lease,age);observed.push_back(information(rows));
    };
    need(receiver.receive(wire(document(123,1),b),1001,tick(100)).code==r::DataCode::accepted,"owner initial receipt");
    record(receiver.view(1001),1001,"123 byte","lease=active","age=0 ns");
    need(receiver.receive(wire(document(987,2),b),1002,tick(101)).code==r::DataCode::accepted,"owner pending receipt");
    record(receiver.view(1002),1300,"123 byte","lease=retained","age=unknown");
    need(observed.back().find("987 byte")==std::string::npos,"stale clock cannot import pending value");
    need(receiver.sample(tick(200),1301)==r::DataCode::accepted,"owner fresh clock");
    record(receiver.view(1301),1310,"987 byte","lease=active","age=100 ns");
    need(receiver.heartbeat(0,2000)==r::DataCode::accepted&&receiver.sample(tick(300),2000)==r::DataCode::accepted,"owner native heartbeat");
    record(receiver.view(2000),2000,"987 byte","lease=active","age=200 ns");
    need(receiver.receive(wire(document(777,3),b),2001,tick(301)).code==r::DataCode::accepted,"owner unseen value");
    record(receiver.view(2001),5000,"987 byte","lease=retained","age=unknown");
    need(observed.back().find("777 byte")==std::string::npos,"expired native lease cannot import pending value");
    need(receiver.heartbeat(1,4999)==r::DataCode::accepted&&receiver.sample(tick(400),4999)==r::DataCode::accepted,"owner independent source lease");
    const auto live=receiver.view(4999);record(live,5001,"777 byte","lease=active","age=300 ns");
    receiver.disconnect(5002);record(receiver.view(5002),5002,"777 byte","lease=retained","age=unknown");
    owner.admission.reset();owner.surface.policy({},5003);owner.surface.paint(5003,{},[&](auto code,const auto* frame){need(code==v::SurfaceCode::restricted&&!frame,"policy erases borrowed surface");});
    need(owner.admission.compatible(scope)&&!owner.admission.compatible({12,4}),"reset retains profile identity");
    Owner replacement(root);shows(replacement.show(live,scope,5010),"777 byte","lease=active","age=300 ns");
    need(replacement.show(live,{12,4},5011).empty()&&replacement.surface.status().code==v::SurfaceCode::closed,"different profile closes before presentation");
    return observed;
}
inline void invalid(const std::string& root){
    const auto b=binding();const r::DeliveryScope scope{11,4};
    for(const std::string cause:{"clock-stale","clock-future","receipt-future","clock-missing","frame-missing","binding-missing","lease-expired","disconnected","zero-ordinal","backward-ordinal","wrong-generation"}){
        r::TelemetryReceiver receiver(scope,grant(),n::network_metrics(),b,1000);Owner owner(root);
        need(receiver.receive(wire(document(123,1),b),1001,tick()).code==r::DataCode::accepted,"invalid case initial receipt");
        shows(owner.show(receiver.view(1001),scope,1001),"123 byte","lease=active","age=0 ns");
        need(receiver.receive(wire(document(987,2),b),1002,tick(101)).code==r::DataCode::accepted,"invalid case new receipt");
        auto candidate=receiver.view(1002);auto current=scope;
        if(cause=="clock-stale")candidate.clock_ms=0;
        if(cause=="clock-future")candidate.clock_ms=1003;
        if(cause=="receipt-future"){auto frame=*candidate.frame;frame.received_ms=1003;candidate.frame=std::make_shared<const r::DeliveredFrame>(std::move(frame));}
        if(cause=="clock-missing")candidate.clock.reset();
        if(cause=="frame-missing")candidate.frame.reset();
        if(cause=="binding-missing")candidate.binding.reset();
        if(cause=="lease-expired")candidate.live_until_ms=1002;
        if(cause=="disconnected")candidate.connected=false;
        if(cause=="zero-ordinal"||cause=="backward-ordinal"){auto frame=*candidate.frame;frame.ordinal=cause=="zero-ordinal"?0:1;candidate.frame=std::make_shared<const r::DeliveredFrame>(std::move(frame));}
        if(cause=="wrong-generation")++current.generation;
        const auto rows=owner.show(candidate,current,1002);shows(rows,"123 byte","lease=retained","age=unknown");
        need(information(rows).find("987 byte")==std::string::npos,"invalid candidate never imports unseen value");
        std::cerr<<"admission-owner "<<cause<<": pass\n";
    }
    Owner missing(root);need(missing.show({}, {},1000).empty()&&missing.surface.status().code==v::SurfaceCode::closed,"missing profile closes");
}
inline void charts(const std::string& root){
    const auto cases=read(root+"/../../../tests/scene","inspector-delivery-cases.json");
    for(const auto& scenario:cases["cases"]){
        const auto b=binding();const r::DeliveryScope scope{11,4};r::TelemetryReceiver receiver(scope,grant(),n::network_metrics(),b,1000);Owner owner(root,true);
        std::uint64_t now=1000,clock=0;
        for(const auto& step:scenario["steps"]){
            ++now;const auto measured=step["time"].get<std::uint64_t>();clock=std::max(clock,measured);auto doc=chart_document(step["value"],step["generation"],measured);
            if(step.value("failed",false))for(auto& observation:doc["observations"])if(observation["field"]=="network.receive_bytes"){
                observation["acquisition"]="failed";observation["freshness"]="stale";observation["error"]={{"code","fixture.failed"},{"message","Controlled failure"},{"retryable",true}};
            }
            need(receiver.receive(wire(doc,b),now,tick(clock)).code==(step.value("duplicate",false)?r::DataCode::duplicate:r::DataCode::accepted),"chart admission unchanged");
            if(!step.contains("points"))continue;
            const auto rows=owner.show(receiver.view(now),scope,now);need(rows.size()==1&&rows[0].children.size()==step["points"].size(),"exact admitted chart row count");
            for(std::size_t index=0;index<step["points"].size();++index){const auto& expected=step["points"][index];const auto& actual=rows[0].children[index];
                need(actual.item=="Point "+expected[0].dump()+" ns"&&actual.information==expected[1].dump()+" byte; generation "+expected[2].dump()+"; "+expected[3].get<std::string>(),"unchanged literal chart oracle");
            }
            need((rows[0].information.find("Gap pending")!=std::string::npos)==step.value("gap_pending",false),"unchanged pending chart break");
        }
        std::cerr<<"admission-owner chart "<<scenario["id"].get<std::string>()<<": pass\n";
    }
}
inline void confinement(const std::string& root){
    const r::DeliveryScope scope{11,4};Owner owner(root);unsigned rejected=0;std::exception_ptr failure;
    std::thread other([&]{
        try{for(unsigned op=0;op!=3;++op)try{
            if(op==0)(void)owner.admission.compatible(scope);else if(op==1)(void)owner.admission.admit({},scope,1000);else owner.admission.reset();
        }catch(const std::logic_error& e){need(std::string(e.what())=="inspector.delivery_owner","exact owner rejection");++rejected;}
        }catch(...){failure=std::current_exception();}
    });other.join();if(failure)std::rethrow_exception(failure);need(rejected==3&&owner.surface.status().code==v::SurfaceCode::empty,"wrong thread rejected before touching surface");
    ui::InspectorAdmission* active=nullptr;unsigned recursive=0;
    v::SceneSurface surface({true,"console",{"console"}},grant(),config(root),{provider()},[&]{
        if(active)try{active->reset();}catch(const std::logic_error& e){need(std::string(e.what())=="inspector.delivery_owner","recursive owner rejection");++recursive;}
        return true;
    },{},v::SurfaceAudience::inspector);
    ui::InspectorAdmission admission(surface);active=&admission;
    const auto b=binding();r::TelemetryReceiver receiver(scope,grant(),n::network_metrics(),b,1000);
    need(receiver.receive(wire(document(),b),1001,tick()).code==r::DataCode::accepted,"recursive test input");
    const auto ticks=admission.admit(receiver.view(1001),scope,1001);active=nullptr;
    need(recursive>=2&&ticks.size()==1,"recursive callback cannot reset live admission");
    surface.paint(1001,ticks,[&](auto,const auto* frame){need(frame&&frame->widgets[0].accessible.find("123 byte")!=std::string::npos,"recursive refusal preserves outer admission");});
    const auto before=recursive;active=&admission;
    need(admission.admit({}, {12,4},1002).empty(),"profile refusal supplies no tick");active=nullptr;
    need(recursive>before&&surface.status().code==v::SurfaceCode::closed,"profile closure also guards recursive clear callback");
}
inline int run(const std::string& root){
    const auto expected=scalar(root);invalid(root);charts(root);confinement(root);
    std::promise<std::vector<std::string>> completion;auto result=completion.get_future();
    std::thread worker([&]{try{const auto actual=scalar(root);invalid(root);charts(root);completion.set_value(actual);}catch(...){completion.set_exception(std::current_exception());}});
    worker.join();need(result.get()==expected,"owned semantic transfer has exact same output on fresh worker owner");
    std::cout<<"SCALAR NEGATIVE CHART THREAD REENTRANCY pass\n";return 0;
}
}
