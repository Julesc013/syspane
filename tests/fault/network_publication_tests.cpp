#include "network_publication.hpp"
#include "data_view.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>
namespace n=syspane::runtime;namespace m=syspane::model;namespace p=syspane::protocol;
namespace r=syspane::recovery;namespace c=syspane::configuration;namespace os=syspane::platform;
using p::Json;
void need(bool ok){if(!ok)throw std::runtime_error("fixed network publication expectation failed");}
const std::string utc="2026-10-05T23:00:00Z",later="2026-10-05T23:00:01Z";
m::Tick tick(std::uint64_t n){return {"epoch:1",n,"clock:1","scope:1"};}
os::NetworkRow row(std::uint64_t receive=100,std::uint64_t transmit=200){return {9,9,6,os::NetworkCounters{receive,transmit}};}
void accept(n::NetworkState& state,os::NetworkRow value,std::uint64_t now){need(state.commit(1,state.revision(),{os::NetworkCode::success,0,{value}},tick(now),tick(now))==n::NetworkStateCode::accepted);}
c::Policy policy(){c::Policy v;v.available=true;v.revision=7;v.disclosure[{"desktop","desktop"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
p::TelemetryBinding binding(){return {{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},
    {"telemetry.snapshot","telemetry.measured-time"}},"D","epoch:1","producer:network","S","desktop","operational",7,
    p::TelemetryDirection::producer_to_consumer,"0.2.0","clock:1","scope:1"};}
std::string encoded(Json doc,const char* record){Json body{{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","producer:network"},
    {"record_id",record},{"policy_revision","7"},{"clock_id","clock:1"},{"snapshot",std::move(doc)}};
    return p::encode_telemetry({"snapshot","D","epoch:1",body.dump(),body},binding());}
void values(){n::NetworkState state("epoch:1","clock:1","scope:1");state.demand(1);accept(state,row(),100);
    auto doc=n::network_document(*state.sample(),1,utc,utc,true);auto& o=doc["observations"];
    need(doc["entities"][0]["id"]=="network:interface:1"&&doc["entities"][0]["identity"]["native_index"]=="9");
    need(o[0]["value"]["data"]=="100"&&o[1]["value"]["data"]=="200"&&o[2]["value"].is_null()&&o[2]["acquisition"]=="pending");
    accept(state,row(130,260),110);doc=n::network_document(*state.sample(),2,later,later,true);
    need(doc["observations"][2]["value"]["data"]==3e9&&doc["observations"][3]["value"]["data"]==6e9&&doc["observations"][2]["sample_interval_ns"]=="10");
    accept(state,row(130,260),120);doc=n::network_document(*state.sample(),3,later,later,true);need(doc["observations"][2]["value"]["data"]==0.0);
    accept(state,row(1,2),130);doc=n::network_document(*state.sample(),4,later,later,true);need(doc["observations"][2]["value"].is_null());
    auto absent=row();absent.counters.reset();accept(state,absent,140);doc=n::network_document(*state.sample(),5,later,later,true);
    for(const auto& field:doc["observations"])need(field["value"].is_null()&&field["measured_at"].is_null());
    accept(state,row(std::numeric_limits<std::uint64_t>::max()),150);doc=n::network_document(*state.sample(),6,later,later,true);
    need(doc["observations"][0]["value"]["data"]=="18446744073709551615");(void)encoded(doc,"max");
}
void failure(){n::NetworkState state("epoch:1","clock:1","scope:1");state.demand(1);accept(state,row(),100);accept(state,row(130,260),110);
    const auto current=n::network_document(*state.sample(),2,utc,utc,true);
    need(state.commit(1,0,{os::NetworkCode::failed,5},tick(120),tick(121))==n::NetworkStateCode::source_failed);
    auto retained=n::network_document(*state.sample(),3,utc,later,state.current());
    for(unsigned i=0;i<4;++i){const auto& a=current["observations"][i];const auto& b=retained["observations"][i];
        need(a["value"]==b["value"]&&a["measured_at"]==b["measured_at"]&&a["observed_at"]==b["observed_at"]&&b["attempted_at"]==later);
        need(b["acquisition"]=="failed"&&b["freshness"]=="stale"&&!b["error"].is_null());}
    (void)encoded(retained,"failure");accept(state,row(190,380),140);auto resumed=n::network_document(*state.sample(),4,later,later,true);
    need(resumed["observations"][2]["sample_interval_ns"]=="30"&&resumed["observations"][2]["value"]["data"]==2e9);
}
void boundary(){n::NetworkState state("epoch:1","clock:1","scope:1");state.demand(1);accept(state,row(),100);
    const auto doc=n::network_document(*state.sample(),1,utc,utc,true);const auto bytes=encoded(doc,"first");
    r::DataView view({true,"desktop",{"desktop"}},policy(),"desktop","operational",n::network_metrics());
    const auto attachment=view.attach_wire(binding(),0);need(attachment.code==r::DataCode::accepted);
    need(view.receive(attachment.token,7,bytes,1,tick(101)).code==r::DataCode::accepted);
    need(view.receive(attachment.token,7,bytes,2,tick(102)).code==r::DataCode::duplicate);
    bool rejected=false;try{(void)n::network_document(*state.sample(),2,later,later,true,32);}catch(const p::Error& error){rejected=std::string(error.what())=="network.publication_capacity";}need(rejected);
    need(view.project(2,[&](const auto& s,const auto&){need(s.generation==1&&s.observations[0].measured_at->nanoseconds==100);}));
    need(state.commit(1,0,{os::NetworkCode::success,0,{}},tick(110),tick(110))==n::NetworkStateCode::accepted);
    need(view.receive(attachment.token,7,encoded(n::network_document(*state.sample(),2,later,later,true),"empty"),3,tick(111)).code==r::DataCode::accepted);
    accept(state,row(),120);const auto replacement=n::network_document(*state.sample(),3,later,later,true);
    need(replacement["entities"][0]["id"]=="network:interface:2");
    need(view.receive(attachment.token,7,encoded(replacement,"replacement"),4,tick(121)).code==r::DataCode::accepted);
    auto denied=policy();denied.available=false;denied.revision=8;view.policy(denied,5);need(!view.status(5).payload_available);
}
int main(int argc,char** argv){try{need(argc==2);const std::string name=argv[1];if(name=="PUBLICATION-VALUES")values();else if(name=="PUBLICATION-FAILURE")failure();else if(name=="PUBLICATION-BOUNDARY")boundary();else return 2;
    std::cout<<name<<": pass\n";return 0;}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
