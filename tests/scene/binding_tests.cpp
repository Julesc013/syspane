#include "bindings.hpp"
#include "network_publication.hpp"
#include <algorithm>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace s=syspane::scene;namespace m=syspane::model;namespace r=syspane::recovery;
namespace p=syspane::protocol;namespace c=syspane::configuration;namespace n=syspane::runtime;
using p::Json;using Code=s::BindingCode;
namespace {
void need(bool ok,const char* why="binding oracle failed"){if(!ok)throw std::runtime_error(why);}
c::Policy policy(unsigned revision=7,bool allow=true){c::Policy v;v.available=allow;v.revision=revision;v.disclosure[{"desktop","desktop"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
m::Tick tick(std::string epoch="E1",std::uint64_t now=100){return {std::move(epoch),now,"clock:1","scope:1"};}
Json selector(std::string mode="collection",unsigned limit=256){return {{"kind","selector"},{"scope",{{"kind","local_host"}}},{"entity_type","network.interface"},
    {"mode",mode},{"predicates",Json::array()},{"sort",Json::array()},{"limit",limit},{"field","network.receive_bytes"}};}
Json direct(std::string epoch="E1",std::string entity="a"){return {{"kind","direct"},{"producer_id","P1"},{"producer_epoch",epoch},{"entity_id",entity},{"field","network.receive_bytes"}};}
struct Fixture {
    std::string producer; r::DataView view{{true,"desktop",{"desktop"}},policy(),"desktop","operational",n::network_metrics()};
    p::TelemetryBinding link;std::uint64_t token=0;Json doc;
    explicit Fixture(std::string id="P1"):producer(std::move(id)){
        link={{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},
            {"telemetry.snapshot","telemetry.measured-time"}},"D","E1",producer,"S","desktop","operational",7,
            p::TelemetryDirection::producer_to_consumer,"0.2.0","clock:1","scope:1"};
        token=view.attach_wire(link,0).token;need(token!=0,"fixture attachment");
        n::NetworkState state("E1","clock:1","scope:1");state.demand(1);
        need(state.commit(1,0,{syspane::platform::NetworkCode::success,0,{{9,9,6,syspane::platform::NetworkCounters{3,0}}}},tick(),tick())==n::NetworkStateCode::accepted);
        doc=n::network_document(*state.sample(),1,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
        const auto entity=doc["entities"][0],observations=doc["observations"];
        doc["entities"]=Json::array();doc["observations"]=Json::array();
        for(const std::string name:{"c","a","b"}){auto e=entity;e["id"]=name;e["display_name"]=name=="c"?"Beta":"Alpha";doc["entities"].push_back(e);
            for(auto o:observations){o["entity_id"]=name;if(o["field"]=="network.receive_bytes")o["value"]["data"]=name=="c"?"9":"3";doc["observations"].push_back(o);}}
    }
    void receive(unsigned now=1){Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id",producer},{"record_id","R"+doc["generation"].get<std::string>()},
        {"policy_revision",std::to_string(link.policy_revision)},{"clock_id","clock:1"},{"snapshot",doc}};
        const auto bytes=p::encode_telemetry({"snapshot","D",link.epoch,body.dump(),body},link);
        const auto result=view.receive(token,link.policy_revision,bytes,now,tick(link.epoch));need(result.code==r::DataCode::accepted,"wire admission failed");}
    s::BindingInput input(){s::BindingInput v;v.view=&view;v.producer=producer;v.entity_types={"network.interface"};v.now=tick(link.epoch);
        for(const auto& metric:n::network_metrics())v.fields.emplace(metric.field,3000000000ULL);
        return v;}
};
void check(const Json& binding,const std::vector<s::BindingInput>& inputs,const std::function<void(const s::BindingFrame&)>& expected,s::BindingLimits limits={},unsigned now=2){
    unsigned calls=0;s::project_binding(binding,inputs,now,[&](const auto& frame){++calls;expected(frame);},limits);need(calls==1,"one sink invocation");}
void empty(const s::BindingFrame& f,Code code){need(f.code==code&&f.rows.empty()&&f.total==0&&!f.truncated&&f.accounted_bytes==0,"no-payload frame");}
std::vector<std::string> ids(const s::BindingFrame& f){std::vector<std::string> v;for(const auto& row:f.rows)v.push_back(row.producer+":"+row.epoch+":"+row.entity);return v;}
void order(){Fixture a,b("P2");a.receive();std::reverse(b.doc["entities"].begin(),b.doc["entities"].end());std::reverse(b.doc["observations"].begin(),b.doc["observations"].end());b.receive();
    auto q=selector("collection",4);q["sort"]={{{"field","network.receive_bytes"},{"direction","descending"}}};
    for(bool reverse:{false,true}){auto in=std::vector<s::BindingInput>{a.input(),b.input()};if(reverse)std::reverse(in.begin(),in.end());
        check(q,in,[](const auto& f){need(f.code==Code::matched&&f.total==6&&f.truncated);need(ids(f)==std::vector<std::string>{"P1:E1:c","P2:E1:c","P1:E1:a","P1:E1:b"});});}
    q=selector("singleton",1);check(q,{a.input()},[](const auto& f){empty(f,Code::ambiguous);});
    q["predicates"]={{{"field","entity.id"},{"op","eq"},{"value","a"}}};check(q,{a.input()},[](const auto& f){need(f.code==Code::matched&&f.total==1&&!f.truncated&&f.rows[0].entity=="a");});
}
void scope(){Fixture a,b("P2");a.receive();b.receive();auto ai=a.input(),bi=b.input();bi.scope={"registered_asset","asset:2"};
    check(selector(),{ai,bi},[](const auto& f){need(f.total==3&&f.rows[0].producer=="P1");});auto q=selector();q["scope"]={{"kind","registered_asset"},{"asset_id","asset:2"}};
    check(q,{ai,bi},[](const auto& f){need(f.total==3&&f.rows[0].producer=="P2");});q["scope"]={{"kind","current_session"}};check(q,{ai,bi},[](const auto& f){empty(f,Code::unsupported);});
    bi.scope={"current_session",""};check(q,{ai,bi},[](const auto& f){need(f.total==3&&f.rows[0].producer=="P2");});
}
void direct_pin(){Fixture a;a.receive();check(direct(),{a.input()},[](const auto& f){need(f.code==Code::matched&&f.rows[0].entity=="a"&&std::get<std::uint64_t>(f.rows[0].observation.value)==3);});
    check(direct("E2"),{a.input()},[](const auto& f){empty(f,Code::empty);});
    a.doc["generation"]="2";a.doc["entities"][1]["id"]="replacement";for(auto& o:a.doc["observations"])if(o["entity_id"]=="a")o["entity_id"]="replacement";a.receive(3);
    check(direct(),{a.input()},[](const auto& f){empty(f,Code::empty);},{},4);
    auto q=selector();q["predicates"]={{{"field","entity.display_name"},{"op","eq"},{"value","Alpha"}}};
    check(q,{a.input()},[](const auto& f){need(ids(f)==std::vector<std::string>{"P1:E1:b","P1:E1:replacement"});},{},4);
}
void pins(){Fixture a;a.receive();auto in=a.input();Json q={{"kind","persistent_pin"},{"scope",{{"kind","local_host"}}},{"namespace","provider:mac"},{"key","AA"},{"entity_type","network.interface"},{"field","network.receive_bytes"}};
    check(q,{in},[](const auto& f){empty(f,Code::pending);});in.pins.push_back({"provider:mac","AA","network.interface","E0","a"});check(q,{in},[](const auto& f){empty(f,Code::empty);});
    in.pins.push_back({"provider:mac","AA","network.interface","E1","a"});check(q,{in},[](const auto& f){need(f.code==Code::matched&&f.rows[0].entity=="a");});
    in.pins.push_back({"provider:mac","AA","network.interface","E1","b"});check(q,{in},[](const auto& f){empty(f,Code::ambiguous);});
    Json legacy={{"kind","unresolved_pin"},{"source_schema_version","0.1.0"},{"entity_id","a"},{"field","network.receive_bytes"},{"reason","producer_context_required"}};
    check(legacy,{},[](const auto& f){empty(f,Code::pending);});
}
void numeric(){Fixture a;for(auto& o:a.doc["observations"])if(o["field"]=="network.receive_bytes")o["value"]["data"]=o["entity_id"]=="a"?"9007199254740993":(o["entity_id"]=="b"?"9007199254740992":"18446744073709551615");a.receive();
    auto q=selector();q["predicates"]={{{"field","network.receive_bytes"},{"op","eq"},{"value",std::uint64_t{9007199254740993ULL}}}};
    check(q,{a.input()},[](const auto& f){need(ids(f)==std::vector<std::string>{"P1:E1:a"});});q["predicates"][0]["value"]=9007199254740992.0;
    check(q,{a.input()},[](const auto& f){need(ids(f)==std::vector<std::string>{"P1:E1:b"});});q["predicates"][0]["value"]=18446744073709551616.0;
    check(q,{a.input()},[](const auto& f){empty(f,Code::empty);});q["predicates"][0]["value"]=std::numeric_limits<std::uint64_t>::max();
    check(q,{a.input()},[](const auto& f){need(ids(f)==std::vector<std::string>{"P1:E1:c"});});q["predicates"][0]["value"]="9007199254740993";
    check(q,{a.input()},[](const auto& f){empty(f,Code::empty);});q["predicates"][0]["value"]=-1;
    check(q,{a.input()},[](const auto& f){empty(f,Code::empty);});
}
void unknown(){Fixture a;a.receive();auto q=selector();q["predicates"]={{{"field","network.receive_bytes_per_second"},{"op","ne"},{"value",0}}};
    check(q,{a.input()},[](const auto& f){empty(f,Code::pending);});q["predicates"].push_back({{"field","entity.id"},{"op","eq"},{"value","absent"}});
    check(q,{a.input()},[](const auto& f){empty(f,Code::empty);});q=selector();q["sort"]={{{"field","network.receive_bytes_per_second"},{"direction","descending"}}};
    check(q,{a.input()},[](const auto& f){need(ids(f)==std::vector<std::string>{"P1:E1:a","P1:E1:b","P1:E1:c"});});
    auto in=a.input();in.fields.erase("network.receive_bytes");check(selector(),{in},[](const auto& f){empty(f,Code::unsupported);});
}
void missing(){Fixture a;auto& observations=a.doc["observations"];observations.erase(std::remove_if(observations.begin(),observations.end(),[](const auto& o){return o["entity_id"]=="a"&&o["field"]=="network.receive_bytes";}),observations.end());a.receive();
    check(direct(),{a.input()},[](const auto& f){need(f.code==Code::matched&&f.rows[0].code==Code::pending&&std::holds_alternative<std::monostate>(f.rows[0].observation.value));});
    Fixture b;auto source=b.doc["sources"][0];source["id"]="second";b.doc["sources"].push_back(source);auto o=b.doc["observations"][4];o["source_id"]="second";b.doc["observations"].push_back(o);
    // Existing wire grammar rejects duplicate entity/field pairs before projection.
    bool rejected=false;try{b.receive();}catch(const p::Error& e){rejected=std::string(e.what())=="telemetry.graph";}need(rejected,"duplicate source must fail wire admission");
    check(direct(),{b.input()},[](const auto& f){empty(f,Code::pending);});
}
void freshness(){Fixture a;a.receive();auto in=a.input();
    check(direct(),{in},[](const auto& f){need(f.rows[0].age_ns==0,"equal measurement tick has zero age");});
    in.now=tick("E1",3000000100ULL);
    check(direct(),{in},[](const auto& f){need(f.rows[0].effective==m::Freshness::stale&&f.rows[0].age_ns==3000000000ULL);});
    in.now=tick("E1",3000000101ULL);auto q=selector();q["predicates"]={{{"field","network.receive_bytes"},{"op","eq"},{"value",3}}};check(q,{in},[](const auto& f){empty(f,Code::pending);});
    Fixture b;b.receive();b.view.disconnect(b.token,7,2);in=b.input();in.now.reset();
    check(direct(),{in},[](const auto& f){need(f.rows[0].effective==m::Freshness::stale&&!f.rows[0].age_ns&&f.rows[0].presentation==r::Presentation::retained);},{},3);
    Fixture active;active.receive();in=active.input();in.now.reset();check(direct(),{in},[](const auto& f){empty(f,Code::pending);});
}
void multiple_sources(){
    r::DataView view{{true,"desktop",{"desktop"}},policy(),"desktop","operational",n::network_metrics()};const auto token=view.attach("P1","E1",0).token;need(token!=0);
    m::Observation o;o.entity_id="a";o.field="network.receive_bytes";o.source_id="S1";o.value=std::uint64_t{3};o.unit="byte";
    o.support=m::Support::supported;o.acquisition=m::Acquisition::success;o.presence=m::Presence::present;o.freshness=m::Freshness::current;
    o.observed_at=m::UtcTime{1791244800,0};o.attempted_at=*o.observed_at;o.measured_at=tick();
    m::Snapshot snapshot{"P1","E1",1,{{"a","network.interface","Alpha",1}},{{"S1","fixture","local"},{"S2","fixture","local"}}, {},{o}};
    o.source_id="S2";snapshot.observations.push_back(o);need(view.full(token,7,{"R",{},snapshot},1).code==r::DataCode::accepted);
    view.disconnect(token,7,2);s::BindingInput in;in.view=&view;in.producer="P1";in.entity_types={"network.interface"};in.fields["network.receive_bytes"]=3000000000ULL;
    check(direct(),{in},[](const auto& f){need(f.code==Code::matched&&f.rows[0].code==Code::ambiguous&&std::holds_alternative<std::monostate>(f.rows[0].observation.value));},{},3);
    auto q=selector();q["predicates"]={{{"field","network.receive_bytes"},{"op","eq"},{"value",3}}};check(q,{in},[](const auto& f){empty(f,Code::ambiguous);},{},3);
}
void axes(){Fixture a;for(auto& o:a.doc["observations"])if(o["field"]=="network.receive_bytes"){
    o["acquisition"]="failed";o["freshness"]="stale";o["error"]={{"code","provider.failed"},{"message","secret detail"},{"retryable",true}};}a.receive();
    check(direct(),{a.input()},[](const auto& f){const auto& v=f.rows[0];need(v.code==Code::matched&&v.observation.acquisition==m::Acquisition::failed&&v.effective==m::Freshness::stale&&std::get<std::uint64_t>(v.observation.value)==3);
        need(v.observation.error&&v.observation.error->code=="provider.failed"&&v.observation.error->message.empty());});
    auto q=direct();q["field"]="network.transmit_bytes";check(q,{a.input()},[](const auto& f){need(std::get<std::uint64_t>(f.rows[0].observation.value)==0);});
    q["field"]="entity.display_name";check(q,{a.input()},[](const auto& f){need(f.rows[0].metadata&&std::get<std::string>(f.rows[0].observation.value)=="Alpha"&&f.rows[0].observation.origin==m::Origin::configured);});
}
void permission(){Fixture a,b("P2");a.receive();b.receive();b.view.policy(policy(8,false),2);auto in=b.input();in.fields.clear();
    check(selector(),{a.input(),in},[](const auto& f){empty(f,Code::denied);},{},3);
    b.view.policy(policy(9),4);check(selector(),{a.input(),b.input()},[](const auto& f){empty(f,Code::pending);},{},5);
    check(direct(),{a.input(),b.input()},[](const auto& f){need(f.code==Code::matched);},{},5);
}
void bounds(){Fixture a;a.receive();std::size_t exact=0;check(selector(),{a.input()},[&](const auto& f){need(f.code==Code::matched);exact=f.accounted_bytes;});
    auto l=s::BindingLimits{};l.output_bytes=exact;check(selector(),{a.input()},[](const auto& f){need(f.code==Code::matched);},l);
    l.output_bytes=exact-1;check(selector(),{a.input()},[](const auto& f){empty(f,Code::capacity);},l);
    l={};l.index_bytes=0;check(selector(),{a.input()},[](const auto& f){empty(f,Code::capacity);},l);
    l={};l.work_steps=0;check(selector(),{a.input()},[](const auto& f){empty(f,Code::capacity);},l);
}
void lifetime(){Fixture a,b("P2");a.receive();b.receive();check(selector(),{a.input(),b.input()},[&](const auto& f){need(f.total==6);for(auto* v:{&a.view,&b.view}){bool denied=false;try{v->status(2);}catch(const std::logic_error&){denied=true;}need(denied,"all borrows alive");}});
    unsigned calls=0;bool threw=false;try{s::project_binding(selector(),{a.input(),b.input()},2,[&](const auto&){++calls;throw std::bad_alloc();});}catch(const std::bad_alloc&){threw=true;}need(threw&&calls==1);
    check(selector(),{b.input(),a.input()},[](const auto& f){need(f.total==6);},{},3);
}
void invalid(){Fixture a;a.receive();const auto reject=[&](Json q,std::vector<s::BindingInput> in,s::BindingLimits l={}){unsigned calls=0;bool threw=false;try{s::project_binding(q,in,2,[&](const auto&){++calls;},l);}catch(const p::Error&){threw=true;}need(threw&&calls==0);};
    auto q=selector();q["limit"]=257;reject(q,{a.input()});reject(selector(),{a.input(),a.input()});auto in=a.input();in.view=nullptr;reject(selector(),{in});
    in=a.input();in.fields["network.receive_bytes"]=0;reject(selector(),{in});in=a.input();in.scope={"registered_asset",""};reject(selector(),{in});
    auto l=s::BindingLimits{};l.work_steps++;reject(selector(),{a.input()},l);
    // All sixteen 512-scalar predicates remain admitted even above 32 KiB UTF-8.
    std::string unicode;for(unsigned i=0;i<512;++i)unicode+="\xf0\x9f\x98\x80";
    q=selector();for(unsigned i=0;i<16;++i)q["predicates"].push_back({{"field","entity.display_name"},{"op","eq"},{"value",unicode}});
    need(q.dump().size()>32768);check(q,{a.input()},[](const auto& f){empty(f,Code::empty);});
}
void restart(){Fixture a;a.receive();a.view.disconnect(a.token,7,2);a.link.epoch="E2";a.token=a.view.attach_wire(a.link,3).token;need(a.token!=0);
    check(direct(),{a.input()},[](const auto& f){need(f.code==Code::matched&&f.rows[0].epoch=="E1"&&f.rows[0].effective==m::Freshness::stale);},{},4);
    a.doc["producer_epoch"]="E2";for(auto& o:a.doc["observations"])o["producer_epoch"]="E2";a.receive(5);
    check(direct(),{a.input()},[](const auto& f){empty(f,Code::empty);},{},6);check(direct("E2"),{a.input()},[](const auto& f){need(f.code==Code::matched&&f.rows[0].epoch=="E2");},{},6);
    auto in=a.input();in.now=tick("E2",99);check(direct("E2"),{in},[](const auto& f){empty(f,Code::pending);},{},7);
    check(direct("E2"),{a.input()},[](const auto& f){empty(f,Code::pending);},{},8);
}
void real_sort(){Fixture a;for(auto& o:a.doc["observations"])if(o["field"]=="network.receive_bytes_per_second"&&o["entity_id"]!="c"){
    o["value"]={{"kind","number"},{"data",o["entity_id"]=="a"?-9007199254740992.0:1.5}};o["acquisition"]="success";o["freshness"]="current";
    o["observed_at"]="2026-10-06T00:00:00Z";o["sample_interval_ns"]="100";o["measured_at"]={{"clock_id","clock:1"},{"nanoseconds","100"}};}a.receive();
    auto q=selector();q["sort"]={{{"field","network.receive_bytes_per_second"},{"direction","descending"}}};
    check(q,{a.input()},[](const auto& f){need(ids(f)==std::vector<std::string>{"P1:E1:b","P1:E1:a","P1:E1:c"});});
    q["sort"][0]["direction"]="ascending";check(q,{a.input()},[](const auto& f){need(ids(f)==std::vector<std::string>{"P1:E1:a","P1:E1:b","P1:E1:c"});});
    q["predicates"]={{{"field","entity.id"},{"op","eq"},{"value","a"}},{{"field","network.receive_bytes_per_second"},{"op","eq"},{"value",std::int64_t{-9007199254740993LL}}}};
    check(q,{a.input()},[](const auto& f){empty(f,Code::empty);});q["predicates"][1]["value"]=-9007199254740992.0;
    check(q,{a.input()},[](const auto& f){need(ids(f)==std::vector<std::string>{"P1:E1:a"});});
}
void collection_bound(){Fixture a;const auto entity=a.doc["entities"][0],observation=a.doc["observations"][0];a.doc["entities"]=Json::array();a.doc["observations"]=Json::array();
    for(unsigned i=0;i<270;++i){const auto id="e"+std::to_string(1000+i);auto e=entity,o=observation;e["id"]=id;o["entity_id"]=id;
        a.doc["entities"].push_back(e);a.doc["observations"].push_back(o);}
    std::reverse(a.doc["entities"].begin(),a.doc["entities"].end());a.receive();check(selector(),{a.input()},[](const auto& f){need(f.total==270&&f.rows.size()==256&&f.truncated);
        for(unsigned i=0;i<256;++i)need(f.rows[i].entity=="e"+std::to_string(1000+i));});
}
}
int binding_test(const std::string& name){
    if(name=="BIND-ORDER")order();else if(name=="BIND-SCOPE")scope();else if(name=="BIND-DIRECT")direct_pin();else if(name=="BIND-PINS")pins();
    else if(name=="BIND-NUMERIC")numeric();else if(name=="BIND-UNKNOWN")unknown();else if(name=="BIND-MISSING")missing();else if(name=="BIND-FRESHNESS")freshness();
    else if(name=="BIND-RESTART")restart();else if(name=="BIND-REAL-SORT")real_sort();else if(name=="BIND-COLLECTION-BOUND")collection_bound();
    else if(name=="BIND-MULTISOURCE")multiple_sources();else if(name=="BIND-AXES")axes();else if(name=="BIND-POLICY")permission();else if(name=="BIND-BOUNDS")bounds();else if(name=="BIND-LIFETIME")lifetime();else if(name=="BIND-INVALID")invalid();else return 2;
    return 0;
}
