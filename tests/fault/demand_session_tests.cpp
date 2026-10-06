#include "demand_sessions.hpp"
#include <iostream>
#include <stdexcept>

namespace n=syspane::runtime;namespace c=syspane::configuration;namespace p=syspane::protocol;
using Code=n::DemandCode;using p::Json;
void check(bool value,const char* text,int line){if(!value)throw std::runtime_error(std::string(text)+":"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),#x,__LINE__)
c::Policy policy(std::uint64_t revision=7){c::Policy v;v.available=true;v.revision=revision;
    v.disclosure[{"desktop","desktop"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
std::vector<n::DemandSource> catalog(){return {{"source:1","collection.test",100,5000,"",{{"field.a","operational"},{"field.b","operational"}}}};}
n::DemandRequest request(const std::string& field="field.a"){n::DemandRequest r;r.channel="desktop";r.selections={{field,"entity:1"}};return r;}
Json hello(){return {{"type","hello"},{"body",{{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","client"},
    {"max_frame_bytes",p::frame_limit},{"document_versions",Json::array({{{"document","telemetry"},{"version","0.1.0"}},
    {{"document","snapshot"},{"version","0.1.0"}},{{"document","observation"},{"version","0.1.0"}}})},
    {"required_features",{"telemetry.snapshot"}},{"optional_features",Json::array()}}}};}
Json body(std::uint64_t revision=7){return {{"schema_version","0.1.0"},{"subscription_id","S"},{"producer_id","producer:1"},
    {"policy_revision",std::to_string(revision)},{"channel","desktop"},{"classification","operational"}};}
std::string wire(const std::string& id,const char* type,Json value){return Json{{"type",type},{"connection_id",id},{"producer_epoch","fixture:epoch-1"},{"body",std::move(value)}}.dump();}
void open(n::DemandSessions& s,const std::string& id,n::DemandRequest req=request(),std::uint64_t now=0,
          c::Authority authority={true,"console",{"desktop","console"}},std::uint64_t revision=7){
    const auto before=s.lease_count();s.open(id,"principal",std::move(authority),std::move(req),now);CHECK(s.lease_count()==before);
    s.receive(id,hello().dump(),now);CHECK(s.pop(id,now)&&s.lease_count()==before);s.receive(id,wire(id,"subscribe",body(revision)),now);
}
void heartbeat(n::DemandSessions& s,const std::string& id,std::uint64_t sequence,std::uint64_t now){
    s.receive(id,wire(id,"heartbeat",{{"sequence",std::to_string(sequence)}}),now);
    if(!s.closed(id))CHECK(s.pop(id,now));
}
void admission(){
    n::DemandSessions s("fixture:epoch-1",0,policy(),{"producer:1","desktop","operational"},catalog());
    open(s,"C");CHECK(!s.closed("C")&&s.lease_count()==1); // Negotiated desktop, not caller's initial console role.
    open(s,"D",request("field.b"));const auto job=s.take(0);CHECK(job&&job->plan.selections.size()==2&&job->plan.selections[0].field=="field.a"&&job->plan.selections[1].field=="field.b");
    CHECK(s.complete(job->ticket,1)==Code::accepted);s.disconnect("D",2);CHECK(s.lease_count()==1&&!s.take(999));
    const auto single=s.take(1000);CHECK(single&&single->plan.selections.size()==1&&single->plan.selections[0].field=="field.a");
    for(unsigned variant=0;variant<3;++variant){
        auto q=request();if(variant==0)q.selections[0].field="unknown";if(variant==1)q.channel="saver";if(variant==2)q.selections.push_back(q.selections[0]);
        const auto id="rejected:"+std::to_string(variant);open(s,id,q,1000);CHECK(s.closed(id)&&s.lease_count()==1);
        bool rejected=false;try{s.receive(id,"not a document",1000);}catch(const p::Error&){rejected=true;}
        CHECK(rejected&&!s.closed("C")&&s.lease_count()==1);
    }
    auto denied=policy();denied.denied_capabilities.insert("collection.test");
    n::DemandSessions blocked("fixture:epoch-1",0,denied,{"producer:1","desktop","operational"},catalog());open(blocked,"C");
    CHECK(blocked.closed("C")&&blocked.lease_count()==0&&!blocked.take(0));
}
void lifetimes(){
    n::DemandSessions s("fixture:epoch-1",0,policy(),{"producer:1","desktop","operational"},catalog());open(s,"C");
    auto job=s.take(0);CHECK(job);heartbeat(s,"C",0,1000);heartbeat(s,"C",0,3999);
    s.tick(4000);CHECK(s.closed("C")&&s.lease_count()==0&&s.outstanding().size()==1&&s.outstanding()[0].cancelled);
    CHECK(s.complete(job->ticket,4000)==Code::obsolete);
    n::DemandSessions regressed("fixture:epoch-1",0,policy(),{"producer:1","desktop","operational"},catalog());open(regressed,"C");
    open(regressed,"D");const auto shared=regressed.take(0);CHECK(shared);
    heartbeat(regressed,"C",2,1);heartbeat(regressed,"C",1,2);
    CHECK(regressed.closed("C")&&regressed.close_reason("C")=="heartbeat.regressed"&&!regressed.closed("D")&&regressed.lease_count()==1);
    CHECK(regressed.outstanding().size()==1&&!regressed.outstanding()[0].cancelled&&regressed.complete(shared->ticket,3)==Code::accepted);
}
void replay(){
    n::DemandSessions s("fixture:epoch-1",0,policy(),{"producer:1","desktop","operational"},catalog());open(s,"C");
    auto first=s.subscription("C")->ticket;auto job=s.take(0);CHECK(job);
    s.receive("C",wire("C","subscribe",body()),2000);
    CHECK(s.subscription("C")->ticket!=first&&s.lease_count()==1&&!s.outstanding()[0].cancelled);
    CHECK(!s.offer("C",first,"old",Json(),{},1)&&!s.closed("C")); // Obsolete callback cannot regress owner time.
    CHECK(s.complete(job->ticket,2001)==Code::accepted);s.tick(3000);CHECK(s.closed("C")); // Resubscribe did not renew.
    s.disconnect("C",3000);open(s,"C",request(),3001);CHECK(s.subscription("C")->ticket>first);
    job=s.take(3001);CHECK(job);CHECK(!s.offer("C",first,"old",Json(),{},0)&&!s.closed("C"));
    CHECK(s.complete(job->ticket,3002)==Code::accepted);
}
void policies(){
    n::DemandSessions s("fixture:epoch-1",0,policy(),{"producer:1","desktop","operational"},catalog());open(s,"C");const auto job=s.take(0);CHECK(job);
    bool rejected=false;try{s.policy(policy(),1);}catch(const p::Error&){rejected=true;}
    CHECK(rejected&&s.closed("C")&&s.lease_count()==0&&s.outstanding()[0].cancelled);
    CHECK(s.confirm_stopped(job->ticket)==Code::accepted);s.policy(policy(8),2);CHECK(!s.take(2));
    s.disconnect("C",3);open(s,"C",request(),4,{true,"desktop",{"desktop"}},8);
    const auto next=s.take(1000);CHECK(next&&next->policy_revision==8&&next->ticket!=job->ticket);
    auto bad=policy(9);bad.forced["sampling.max_workers"]="bad";rejected=false;try{s.policy(bad,1001);}catch(const p::Error&){rejected=true;}
    CHECK(rejected&&s.closed("C")&&s.lease_count()==0&&s.outstanding()[0].cancelled);
    CHECK(s.confirm_stopped(next->ticket)==Code::accepted);
}
void faults(){
    n::DemandSessions s("fixture:epoch-1",0,policy(),{"producer:1","desktop","operational"},catalog());open(s,"C",request(),100);const auto job=s.take(100);CHECK(job);
    bool rejected=false;try{s.tick(99);}catch(const p::Error&){rejected=true;}
    CHECK(rejected&&s.closed("C")&&s.outstanding()[0].cancelled&&s.lease_count()==0);
    CHECK(s.confirm_stopped(job->ticket)==Code::accepted&&s.outstanding().empty());
    rejected=false;try{s.policy(policy(8),101);}catch(const p::Error&){rejected=true;}CHECK(rejected);
    n::DemandSessions capped("fixture:epoch-1",0,policy(),{"producer:1","desktop","operational"},catalog(),{1,64,1});
    open(capped,"C");open(capped,"D");CHECK(!capped.closed("C")&&capped.closed("D")&&capped.lease_count()==1);
}
int main(int argc,char** argv){try{CHECK(argc==2);const std::string name=argv[1];
    if(name=="DS-ADMIT")admission();else if(name=="DS-LIFETIME")lifetimes();else if(name=="DS-REPLAY")replay();
    else if(name=="DS-POLICY")policies();else if(name=="DS-FAULT")faults();else throw std::runtime_error("case");
    std::cout<<name<<" pass\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
