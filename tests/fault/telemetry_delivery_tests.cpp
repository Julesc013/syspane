#include "telemetry_delivery.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <stdexcept>
namespace r=syspane::recovery;namespace p=syspane::protocol;namespace m=syspane::model;namespace c=syspane::configuration;
using D=r::DataCode;
void check(bool value,const char* expression,int line){if(!value)throw std::runtime_error(std::string(expression)+":"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),#x,__LINE__)
c::Policy policy(){c::Policy v;v.available=true;v.revision=7;v.disclosure[{"console","inspector"}]={"operational"};v.disclosure[{"console","accessibility"}]={"operational"};return v;}
p::TelemetryBinding binding(){return {{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},
    {"telemetry.snapshot","telemetry.measured-time"}},"connection:1","fixture:epoch-1","producer:1","subscription:1",
    "inspector","operational",7,p::TelemetryDirection::producer_to_consumer,"0.2.0","fixture:clock","fixture:scope"};}
m::Tick tick(std::uint64_t ns){return {"fixture:epoch-1",ns,"fixture:clock","fixture:scope"};}
std::vector<m::Metric> metrics(){return {{"network.media","none",m::ValueKind::string}};}
p::Json full(const std::string& root,unsigned generation=1,std::uint64_t measured=100){
    std::ifstream f(root+"/valid/telemetry-snapshot-v0.2.json",std::ios::binary);CHECK(f.good());
    auto v=p::Json::parse(std::string{std::istreambuf_iterator<char>(f),{}});
    v["body"]["record_id"]="record:"+std::to_string(generation);v["body"]["snapshot"]["generation"]=std::to_string(generation);
    v["body"]["snapshot"]["observations"][0]["measured_at"]["nanoseconds"]=std::to_string(measured);return v;
}
r::TelemetryReceiver receiver(){return {{11,4},policy(),metrics(),binding(),1000};}
void run(const std::string& name,const std::string& root){
    auto receiver=::receiver();const r::DeliveryScope current{11,4};const auto first=full(root).dump(2);
    if(name=="FUTURE"){
        CHECK(receiver.receive(full(root,1,101).dump(),1001,tick(100)).code==D::invalid);
        CHECK(!receiver.view(1002).frame);CHECK(!receiver.view(1002).live(current,1002));return;
    }
    if(name=="CAPACITY"){
        CHECK(receiver.receive(std::string(p::frame_limit+1,' '),1001,tick(100)).code==D::capacity);
        CHECK(!receiver.view(1002).frame);return;
    }
    CHECK(receiver.receive(first,1001,tick(100)).code==D::accepted);
    if(name=="COALESCE"){
        const auto saved=receiver.view(1001).frame;CHECK(saved&&saved->bytes==first&&saved->received_ms==1001&&saved->received_tick==tick(100));
        const auto second=full(root,2,110).dump();CHECK(receiver.receive(second,1002,tick(110)).code==D::accepted);
        CHECK(receiver.view(1002).frame->bytes==second);CHECK(saved->bytes==first);
        CHECK(receiver.receive(first,1003,tick(120)).code==D::duplicate);
        CHECK(receiver.view(1003).frame->bytes==second);CHECK(receiver.view(1003).frame->received_tick==tick(110));
    }else if(name=="LEASE"){
        CHECK(receiver.receive(full(root,2,110).dump(),3999,tick(110)).code==D::accepted);
        const auto queued=receiver.view(3999);CHECK(queued.live(current,3999));CHECK(!queued.live(current,4000));
        CHECK(receiver.heartbeat(0,4000)==D::closed);CHECK(!receiver.view(4000).frame);
        CHECK(receiver.heartbeat(1,4001)==D::closed);
    }else if(name=="HEARTBEAT"){
        CHECK(receiver.heartbeat(0,1100)==D::accepted);CHECK(receiver.heartbeat(0,2000)==D::duplicate);
        CHECK(receiver.view(2000).live_until_ms==4100);CHECK(receiver.heartbeat(1,4099)==D::accepted);
        CHECK(receiver.view(4099).live_until_ms==7099);CHECK(!receiver.view(7099).frame);
    }else if(name=="CLOCK"){
        auto queued=receiver.view(1001);CHECK(queued.deliverable(current,1251));CHECK(!queued.deliverable(current,1252));
        CHECK(!queued.deliverable(current,1000));CHECK(queued.clock==std::optional<m::Tick>(tick(100)));
        CHECK(receiver.sample(tick(1234567),1300)==D::accepted);queued=receiver.view(1300);
        CHECK(queued.deliverable(current,1300));CHECK(queued.clock->nanoseconds==1234567);
        CHECK(queued.frame->received_tick.nanoseconds==100);CHECK(queued.frame->received_ms==1001);
        CHECK(receiver.sample(tick(1234566),1301)==D::clock_fault);CHECK(!receiver.view(1301).clock);
    }else if(name=="CLOCK-SCOPE"){
        auto bad=tick(101);bad.clock_scope="other";CHECK(receiver.sample(bad,1002)==D::clock_fault);
        CHECK(!receiver.view(1002).frame);CHECK(!receiver.view(1002).clock);
    }else if(name=="SCOPE"){
        const auto queued=receiver.view(1001);CHECK(queued.deliverable(current,1001));
        CHECK(!queued.deliverable({12,4},1001));CHECK(!queued.deliverable({11,5},1001));CHECK(!queued.deliverable({},1001));
        receiver.disconnect(1002);CHECK(!receiver.view(1002).frame);CHECK(!receiver.view(1002).clock);
        CHECK(queued.frame->bytes==first); // A UI may retain only its own already displayed state.
    }else if(name=="POLICY"){
        receiver.withdraw(1000);CHECK(!receiver.view(1002).frame);CHECK(!receiver.view(1002).clock);
        CHECK(receiver.receive(first,1003,tick(110)).code==D::closed);
        auto denied=policy();denied.denied_capabilities.insert("collection.network");bool refused=false;
        try{r::TelemetryReceiver bad(current,denied,metrics(),binding(),1000);}catch(const p::Error&){refused=true;}CHECK(refused);
    }else if(name=="EPOCH"){
        auto next=binding();next.epoch="replacement";next.connection="connection:2";
        r::TelemetryReceiver replacement({11,5},policy(),metrics(),next,1002);
        CHECK(!replacement.view(1002).frame);CHECK(!replacement.view(1002).deliverable({11,5},1002));
        auto now=tick(110);now.epoch=next.epoch;
        CHECK(replacement.receive(first,1003,now).code==D::invalid);CHECK(!replacement.view(1003).frame);
    }else if(name=="TIME-REGRESSION"){
        CHECK(receiver.sample(tick(101),1000)==D::clock_fault);CHECK(!receiver.view(1002).frame);
    }else throw std::runtime_error("unknown case");
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<": pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
