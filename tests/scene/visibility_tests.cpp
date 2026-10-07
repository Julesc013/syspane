#include "visibility.hpp"
#include "network_publication.hpp"
#include <fstream>
#include <limits>
#include <stdexcept>

namespace {
namespace s=syspane::scene;namespace m=syspane::model;namespace r=syspane::recovery;
namespace p=syspane::protocol;namespace c=syspane::configuration;namespace n=syspane::runtime;
using p::Json;using Code=s::VisibilityCode;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
c::Policy policy(unsigned revision=7,bool allow=true){c::Policy v;v.available=allow;v.revision=revision;v.disclosure[{"desktop","desktop"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
m::Tick tick(std::string epoch="E1",std::uint64_t now=100){return {std::move(epoch),now,"clock:1","scope:1"};}
m::ValueKind kind(const std::string& name){return name=="uint64"?m::ValueKind::uint64:name=="number"?m::ValueKind::number:name=="boolean"?m::ValueKind::boolean:m::ValueKind::string;}
Json direct(std::string epoch="E1"){return {{"kind","direct"},{"producer_id","P1"},{"producer_epoch",epoch},{"entity_id","a"},{"field","test.value"}};}
Json rule(){return {{"schema_version","0.1.0"},{"binding",direct()},{"op","eq"},{"value",3},{"unit","byte"}};}
Json selector(){return {{"kind","selector"},{"scope",{{"kind","local_host"}}},{"entity_type","fixture.entity"},{"mode","singleton"},{"predicates",Json::array()},{"sort",Json::array()},{"limit",1},{"field","test.value"}};}
struct Fixture {
    r::DataView view; p::TelemetryBinding link;std::uint64_t token=0;Json doc;
    Fixture(std::string type="uint64",Json value="3",std::string unit="byte"):
      view({true,"desktop",{"desktop"}},policy(),"desktop","operational",{{"test.value",unit,kind(type)}}){
        link={{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},
            {"telemetry.snapshot","telemetry.measured-time"}},"D","E1","P1","S","desktop","operational",7,
            p::TelemetryDirection::producer_to_consumer,"0.2.0","clock:1","scope:1"};
        token=view.attach_wire(link,0).token;need(token!=0,"fixture attachment");
        n::NetworkState state("E1","clock:1","scope:1");state.demand(1);
        need(state.commit(1,0,{syspane::platform::NetworkCode::success,0,{{9,9,6,syspane::platform::NetworkCounters{3,0}}}},tick(),tick())==n::NetworkStateCode::accepted,"fixture sample");
        doc=n::network_document(*state.sample(),1,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
        doc["entities"]=Json::array();doc["entities"].push_back({{"id","a"},{"kind","fixture.entity"},{"display_name","Alpha"},{"generation","1"},{"identity",Json::object()}});
        auto o=doc["observations"][0];o["entity_id"]="a";o["field"]="test.value";o["unit"]=unit;o["value"]={{"kind",type},{"data",value}};
        doc["observations"]=Json::array();doc["observations"].push_back(o);
    }
    void receive(unsigned now=1){Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","P1"},{"record_id","R"+doc["generation"].get<std::string>()},
        {"policy_revision",std::to_string(link.policy_revision)},{"clock_id","clock:1"},{"snapshot",doc}};
        const auto bytes=p::encode_telemetry({"snapshot","D",link.epoch,body.dump(),body},link);
        need(view.receive(token,link.policy_revision,bytes,now,tick(link.epoch)).code==r::DataCode::accepted,"visibility wire admission");}
    s::BindingInput input(){s::BindingInput v;v.view=&view;v.producer="P1";v.entity_types={"fixture.entity"};v.now=tick(link.epoch);v.fields["test.value"]=1000;return v;}
};
std::string code(Code v){
    switch(v){
    case Code::shown:return "shown";case Code::hidden:return "hidden";case Code::pending:return "pending";case Code::empty:return "empty";
    case Code::denied:return "denied";case Code::unsupported:return "unsupported";case Code::ambiguous:return "ambiguous";case Code::invalid:return "invalid";
    case Code::capacity:return "capacity";case Code::lease_lost:return "lease_lost";case Code::unavailable:return "unavailable";case Code::stale:return "stale";
    case Code::unit_mismatch:return "unit_mismatch";case Code::type_mismatch:return "type_mismatch";
    }throw std::runtime_error("unknown visibility outcome");
}
void check(const Json& q,const std::vector<s::BindingInput>& inputs,const std::string& expected,const std::string& id,unsigned now=2,s::BindingLimits limits={}){
    const auto original=q;unsigned calls=0;
    s::project_visibility(q,inputs,now,[&](const s::VisibilityResult& v){++calls;need(code(v.code)==expected,id+": expected "+expected+", got "+code(v.code));},limits);
    need(calls==1&&q==original,id+": callback/input lifetime");
}
void comparisons(const Json& cases){for(const auto& test:cases){
    Fixture f(test["kind"],test["observed"],test["unit"]);f.receive();auto q=rule();q["op"]=test["op"];q["value"]=test["literal"];q["unit"]=test["literal_unit"];
    check(q,{f.input()},test["expected"],test["id"]);
}}
void states(const Json& cases){for(const auto& test:cases){
    Fixture f;auto q=rule();auto& o=f.doc["observations"][0];const std::string id=test["id"];
    if(id=="denied"||id=="failed-retained"||id=="pending-retained"){
        o["acquisition"]=id=="denied"?"denied":id=="failed-retained"?"failed":"pending";o["freshness"]="stale";
        if(id!="pending-retained")o["error"]={{"code","fixture.failed"},{"message","private explanation"},{"retryable",true}};
    }
    if(id=="unsupported"||id=="disabled"||id=="support-unknown"||id=="no-value"){
        o["value"]=nullptr;o["observed_at"]=nullptr;o["measured_at"]=nullptr;o["acquisition"]=id=="disabled"?"disabled":"pending";
        o["freshness"]=id=="unsupported"?"not_applicable":"unknown";o["support"]=id=="unsupported"?"unsupported":id=="support-unknown"?"unknown":"supported";
    }
    if(id=="absent"){o["presence"]="absent";o["freshness"]="stale";}
    if(id=="missing-field")f.doc["observations"]=Json::array();
    if(id=="ambiguous"){auto e=f.doc["entities"][0],v=o;e["id"]="b";v["entity_id"]="b";f.doc["entities"].push_back(e);f.doc["observations"].push_back(v);q["binding"]=selector();}
    if(id!="no-snapshot")f.receive();
    auto in=f.input();unsigned now=2;
    if(id=="stale")in.now=tick("E1",1100);
    if(id=="clock-missing"||id=="clock-missing-retained")in.now.reset();
    if(id=="expired")now=3001;
    if(id=="disconnected"||id=="clock-missing-retained"){f.view.disconnect(f.token,7,2);now=3;}
    if(id=="missing-entity")q["binding"]["entity_id"]="missing";
    if(id=="unsupported-field")q["binding"]["field"]="unknown.value";
    if(id=="revoked"||id=="regranted"){f.view.policy(policy(8,false),2);now=3;}
    if(id=="regranted"){f.view.policy(policy(9),3);now=4;}
    check(q,{in},test["expected"],id,now);
}}
void lifecycle(){
    Fixture f;f.receive();auto q=rule();check(q,{f.input()},"shown","initial");
    f.view.disconnect(f.token,7,2);f.link.epoch="E2";f.token=f.view.attach_wire(f.link,3).token;need(f.token!=0,"restart attach");
    check(q,{f.input()},"lease_lost","restart retained",4);
    f.doc["producer_epoch"]="E2";for(auto& o:f.doc["observations"])o["producer_epoch"]="E2";f.receive(5);
    check(q,{f.input()},"empty","old epoch pin",6);q["binding"]=direct("E2");check(q,{f.input()},"shown","new epoch pin",6);
    f.view.policy(policy(8,false),7);check(q,{f.input()},"denied","revoked",8);
    f.view.policy(policy(9),9);check(q,{f.input()},"pending","fresh grant cannot restore",10);
    f.link.policy_revision=9;f.token=f.view.attach_wire(f.link,11).token;need(f.token!=0,"regrant attach");
    check(q,{f.input()},"pending","attachment without full",12);f.receive(13);check(q,{f.input()},"shown","new full",14);
    q["binding"]["field"]="entity.display_name";q["value"]="Alpha";q["unit"]="1";check(q,{f.input()},"shown","metadata",14);
    f.view.disconnect(f.token,9,15);check(q,{f.input()},"lease_lost","metadata after disconnect",16);
}
void limits(){
    Fixture f;f.receive();auto q=rule();
    for(unsigned i=0;i<3;++i){s::BindingLimits limit;if(i==0)limit.work_steps=0;if(i==1)limit.output_bytes=0;if(i==2)limit.index_bytes=0;check(q,{f.input()},"capacity","budget",2,limit);}
    unsigned calls=0;bool reentry=false;
    s::project_visibility(q,{f.input()},2,[&](const auto& v){++calls;need(v.code==Code::shown,"inside borrow");try{f.view.status(2);}catch(const std::logic_error&){reentry=true;}});
    need(calls==1&&reentry,"view must remain borrowed during decision");
    calls=0;bool raised=false;try{s::project_visibility(q,{f.input()},2,[&](const auto&){++calls;throw std::bad_alloc();});}catch(const std::bad_alloc&){raised=true;}
    need(raised&&calls==1,"throw once");check(q,{f.input()},"shown","owner released after exception",3);
    auto in=f.input();in.view=nullptr;calls=0;raised=false;try{s::project_visibility(q,{in},4,[&](const auto&){++calls;});}catch(const p::Error&){raised=true;}need(raised&&!calls,"bad context before callback");
    raised=false;try{s::project_visibility(q,{f.input()},4,{});}catch(const p::Error&){raised=true;}need(raised,"missing callback");
}
void grammar(){
    Fixture f;f.receive();const auto reject=[&](Json q){unsigned calls=0;bool threw=false;try{s::project_visibility(q,{f.input()},2,[&](const auto&){++calls;});}catch(const p::Error&){threw=true;}need(threw&&calls==0,"invalid rule before projection");};
    for(const char* field:{"schema_version","binding","op","value","unit"}){auto q=rule();q.erase(field);reject(q);}
    auto q=rule();q["schema_version"]="0.2.0";reject(q);q=rule();q["extra"]=true;reject(q);q=rule();q["op"]="eval";reject(q);
    q=rule();q["value"]=nullptr;reject(q);q["value"]=std::numeric_limits<double>::infinity();reject(q);q["value"]=std::numeric_limits<double>::quiet_NaN();reject(q);
    q=rule();q["unit"]="";reject(q);q["unit"]="byte per second";reject(q);q["unit"]=std::string(65,'a');reject(q);
    q=rule();q["value"]="text";reject(q);q["unit"]="1";q["op"]="gt";reject(q);q["op"]="eq";q["value"]=std::string(513,'a');reject(q);
    q=rule();q["binding"]=selector();q["binding"]["mode"]="collection";reject(q);q["binding"]["mode"]="singleton";q["binding"]["limit"]=2;reject(q);
    q=rule();q["binding"]={{"kind","unresolved_pin"},{"source_schema_version","0.1.0"},{"entity_id","a"},{"field","test.value"},{"reason","producer_context_required"}};check(q,{f.input()},"pending","legacy unresolved");
    q=rule();q["binding"]=selector();check(q,{f.input()},"shown","singleton selector");
    std::string unicode;for(unsigned i=0;i<512;++i)unicode+="\xf0\x9f\x98\x80";
    q["value"]=unicode;q["unit"]="1";c::validate_visibility_document(q);
    for(unsigned i=0;i<16;++i)q["binding"]["predicates"].push_back({{"field","entity.display_name"},{"op","eq"},{"value",unicode}});
    need(q.dump().size()>32768&&q.dump().size()<65536,"large valid rule");c::validate_visibility_document(q);
    q["value"]=std::string(65536,'a');reject(q);
}
}
int visibility_test(const std::string& name,const std::string& root){
    std::ifstream input(root+"/../visibility-cases.json");Json cases;input>>cases;
    if(name=="VISIBILITY-COMPARE")comparisons(cases.at("comparisons"));
    else if(name=="VISIBILITY-STATES")states(cases.at("states"));
    else if(name=="VISIBILITY-LIFECYCLE")lifecycle();else if(name=="VISIBILITY-LIMITS")limits();else if(name=="VISIBILITY-GRAMMAR")grammar();else return 2;
    return 0;
}
