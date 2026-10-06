#include "demand.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>

namespace r = syspane::runtime;
namespace c = syspane::configuration;
using Code = r::DemandCode;
void need(bool yes) { if (!yes) throw std::runtime_error("fixed demand expectation failed"); }
c::Authority auth(std::string role = "desktop") { return {true, role, {role}}; }
c::Policy policy(std::uint64_t revision = 7) {
    c::Policy p; p.available = true; p.revision = revision;
    for (const auto& pair : {std::make_pair("desktop","desktop"),std::make_pair("console","inspector"),
            std::make_pair("console","history"),std::make_pair("saver","saver"),std::make_pair("preview","preview")})
        p.disclosure[pair] = {"public","operational"};
    return p;
}
std::vector<r::DemandSource> catalog() {
    return {{"network","collection.network",100,500,"",{{"network.rx","operational"},{"network.tx","operational"},{"network.private","sensitive"}}},
            {"resources","collection.resources",100,500,"sampling.resources_ms",{{"resources.load","public"}}},
            {"devices","collection.devices",100,500,"",{{"devices.count","public"}}}};
}
r::DemandRequest request(std::string field = "network.rx", std::uint64_t age = 1000, unsigned priority = 0) {
    r::DemandRequest value; value.channel = "desktop"; value.selections = {{std::move(field), "entity:1"}};
    value.maximum_age_ms = age; value.priority = priority; return value;
}
std::uint64_t add(r::DemandOwner& owner, const r::DemandRequest& value, std::uint64_t now = 0, c::Authority authority = auth()) {
    const auto result = owner.admit(value, authority, now); need(result.code == Code::accepted && result.lease); return result.lease;
}
r::DemandJob take(r::DemandOwner& owner, std::uint64_t now) { auto job = owner.take(now); need(job.has_value()); return *job; }
bool selected(const r::DemandJob& job, std::initializer_list<std::pair<const char*,const char*>> expected) {
    if(job.plan.selections.size()!=expected.size())return false;
    auto actual=job.plan.selections.begin();
    for(const auto& row:expected) {
        if(actual->field!=row.first || (row.second ? (!actual->entity || *actual->entity!=row.second) : actual->entity.has_value()))return false;
        ++actual;
    }
    return true;
}
void merge() {
    r::DemandOwner owner(catalog(), policy());
    for (unsigned n = 0; n < 5; ++n) add(owner, request());
    auto job = take(owner, 0); need(job.plan.source == "network" && job.plan.interval_ms == 1000 && job.plan.age_feasible &&
        selected(job,{{"network.rx","entity:1"}}) && !owner.take(0));
    // Adding indistinguishable demand cannot cancel or duplicate the running job.
    add(owner, request(), 1); need(!owner.outstanding()[0].cancelled && owner.complete(job.ticket, 2) == Code::accepted);
    auto more = request("network.tx", 500, 2); more.selections.push_back({"network.rx","entity:2"}); add(owner, more, 3);
    need(!owner.take(499)); job = take(owner, 500);
    need(job.plan.priority == 2 && job.plan.interval_ms == 500 &&
        selected(job,{{"network.rx","entity:1"},{"network.rx","entity:2"},{"network.tx","entity:1"}}));
    need(owner.complete(job.ticket,501) == Code::accepted);
    auto all = request(); all.selections[0].entity.reset(); add(owner, all, 502);
    job = take(owner,1000); need(selected(job,{{"network.rx",nullptr},{"network.tx","entity:1"}}));
}
void policy_gate() {
    r::DemandOwner owner(catalog(), policy()); auto mixed = request(); mixed.selections.push_back({"network.private",{}});
    need(owner.admit(mixed,auth(),0).code == Code::denied && owner.lease_count() == 0);
    need(owner.admit(request(),{false,"desktop",{"desktop"}},0).code == Code::denied);
    need(owner.admit(request(),auth("console"),0).code == Code::denied);
    need(owner.admit(request(),{true,"desktop",{"console"}},0).code == Code::denied);
    auto p=policy(8); p.denied_capabilities.insert("collection.network"); need(owner.policy(p,0) == Code::accepted);
    need(owner.admit(request(),auth(),0).code == Code::denied);
    p=policy(9); p.denied_capabilities.insert("telemetry.subscribe"); owner.policy(p,0);
    need(owner.admit(request("resources.load"),auth(),0).code == Code::denied);
    owner.policy(c::Policy{},0); need(owner.admit(request("resources.load"),auth(),0).code == Code::denied);
    owner.policy(policy(10),0); const auto lease=add(owner,request()); const auto job=take(owner,0);
    need(owner.policy(policy(10),1) == Code::invalid && owner.lease_count()==0 && owner.outstanding()[0].cancelled);
    need(owner.renew(lease,0,1)==Code::obsolete && !owner.take(1));
    need(owner.policy(policy(11),2)==Code::accepted && !owner.take(2)); add(owner,request(),2);
    need(!owner.take(1000)); need(owner.complete(job.ticket,1000)==Code::obsolete);
    const auto fresh=take(owner,1000); need(fresh.policy_revision==11 && fresh.ticket!=job.ticket && fresh.plan_revision!=job.plan_revision);
}
void independent_leases() {
    r::DemandOwner owner(catalog(),policy());
    auto saver=request(); saver.channel="saver"; const auto s=add(owner,saver,0,auth("saver"));
    auto record=request(); record.channel="history"; record.recording=true; const auto h=add(owner,record,0,auth("console"));
    auto job=take(owner,0); need(job.plan.recording); need(owner.complete(job.ticket,1)==Code::accepted);
    need(owner.release(s,2)==Code::accepted && owner.lease_count()==1);
    need(owner.renew(h,0,2500)==Code::accepted && owner.renew(h,0,5000)==Code::duplicate);
    job=take(owner,5000); need(job.plan.recording && owner.complete(job.ticket,5001)==Code::accepted);
    need(owner.renew(h,1,5500)==Code::obsolete && owner.lease_count()==0 && !owner.take(5500));
    auto p=policy(8); p.denied_capabilities.insert("history.record"); owner.policy(p,5500);
    need(owner.admit(record,auth("console"),5500).code==Code::denied);
    const auto a=add(owner,request(),5500); need(owner.renew(a,2,5501)==Code::accepted);
    need(owner.renew(a,1,5502)==Code::invalid && owner.lease_count()==0);
}
void stop_proof() {
    r::DemandOwner owner(catalog(),policy(),{32,64,1});
    const auto a=add(owner,request()); add(owner,request("resources.load")); const auto old=take(owner,0);
    need(old.plan.source=="network" && owner.release(a,1)==Code::accepted && owner.outstanding()[0].cancelled);
    need(!owner.take(1000) && owner.confirm_stopped(old.ticket+100)==Code::obsolete);
    need(owner.confirm_stopped(old.ticket)==Code::accepted); const auto other=take(owner,1000); need(other.plan.source=="resources");
    need(owner.complete(old.ticket,1001)==Code::obsolete && owner.outstanding().size()==1);
    need(owner.complete(other.ticket,1500)==Code::obsolete); // Equality with timeout is expired.
    add(owner,request(),1500); auto next=take(owner,1500); need(next.plan.source=="network");
    need(owner.tick(2000)==Code::accepted && owner.outstanding()[0].cancelled && !owner.take(2000));
    need(owner.complete(next.ticket,2000)==Code::obsolete); need(take(owner,2000).plan.source=="resources");
}
void caps_and_churn() {
    auto p=policy(); p.forced["sampling.resources_ms"]=2000; p.forced["sampling.max_workers"]=1;
    r::DemandOwner owner(catalog(),p,{32,64,4}); const auto a=add(owner,request("resources.load",100));
    auto job=take(owner,0); need(job.plan.interval_ms==2000 && !job.plan.age_feasible && job.plan.requested_age_ms==100);
    add(owner,request(),0); need(!owner.take(0)); need(owner.complete(job.ticket,1)==Code::accepted);
    const auto network=take(owner,1); need(network.plan.source=="network" && owner.complete(network.ticket,2)==Code::accepted);
    owner.release(a,2); add(owner,request("resources.load",100),2);
    need(!owner.take(999)); job=take(owner,1001); need(job.plan.source=="network"); owner.complete(job.ticket,1002);
    job=take(owner,2000); need(job.plan.source=="resources");
    p=policy(8);p.forced["sampling.max_workers"]="bad";
    need(owner.policy(p,2001)==Code::invalid && owner.outstanding()[0].cancelled && !owner.take(2001));
    r::DemandOwner shrinking(catalog(),policy(),{32,64,3});
    add(shrinking,request());add(shrinking,request("resources.load"));add(shrinking,request("devices.count"));
    const auto one=take(shrinking,0),two=take(shrinking,0),three=take(shrinking,0);
    p=policy(8);p.forced["sampling.max_workers"]=1;need(shrinking.policy(p,1)==Code::accepted);
    add(shrinking,request(),1);add(shrinking,request("resources.load"),1);add(shrinking,request("devices.count"),1);
    need(!shrinking.take(1000));shrinking.confirm_stopped(one.ticket);need(!shrinking.take(1000));
    shrinking.confirm_stopped(two.ticket);need(!shrinking.take(1000));
    shrinking.confirm_stopped(three.ticket);need(shrinking.take(1000).has_value());
}
void priority_fairness() {
    r::DemandOwner owner(catalog(),policy(),{32,64,1});
    const auto low=add(owner,request("devices.count",100,0)); const auto high=add(owner,request("network.rx",100,3));
    for (std::uint64_t t=0;t<3000;t+=100) {
        if (t%1000==0) { need(owner.renew(low,t,t)==Code::accepted); need(owner.renew(high,t,t)==Code::accepted); }
        auto job=take(owner,t);need(job.plan.source=="network");need(owner.complete(job.ticket,t+1)==Code::accepted);
    }
    need(take(owner,3000).plan.source=="devices"); // Aged work wins the oldest eligibility tie.
    r::DemandOwner equal(catalog(),policy(),{32,64,1});
    add(equal,request("resources.load",100));add(equal,request("network.rx",100));add(equal,request("devices.count",100));
    for(const auto& source: {"devices","network","resources"}) {
        const auto job=take(equal,0);need(job.plan.source==source);need(equal.complete(job.ticket,0)==Code::accepted);
    }
    need(!equal.take(99)); need(take(equal,100).plan.source=="devices");
}
void plans() {
    r::DemandOwner owner(catalog(),policy());const auto lease=add(owner,request());const auto first=take(owner,0);
    const auto identical=add(owner,request(),1);need(!owner.outstanding()[0].cancelled);
    owner.release(identical,2);need(!owner.outstanding()[0].cancelled);
    auto changed=request("network.tx");add(owner,changed,3);need(owner.outstanding()[0].cancelled);
    need(owner.complete(first.ticket,4)==Code::obsolete && !owner.take(999));
    const auto second=take(owner,1000);need(second.plan_revision>first.plan_revision && second.plan.selections.size()==2);
    owner.release(lease,1001);need(owner.outstanding()[0].cancelled);
    need(owner.complete(second.ticket,1002)==Code::obsolete);
    need(selected(take(owner,2000),{{"network.tx","entity:1"}}));
}
void bounds() {
    r::DemandOwner owner(catalog(),policy(),{1,1,1,3});const auto lease=add(owner,request());
    need(owner.admit(request(),auth(),0).code==Code::capacity && owner.lease_count()==1);
    const auto job=take(owner,0);need(owner.complete(job.ticket,1)==Code::accepted);owner.release(lease,2);
    add(owner,request(),2);need(!owner.take(1000) && owner.fault()==Code::capacity && owner.lease_count()==0);
    r::DemandOwner invalid(catalog(),policy());auto q=request();q.selections[0].field="unknown";
    need(invalid.admit(q,auth(),0).code==Code::invalid);q=request();q.selections.push_back(q.selections[0]);
    need(invalid.admit(q,auth(),0).code==Code::invalid);q=request();q.maximum_age_ms=99;
    need(invalid.admit(q,auth(),0).code==Code::invalid);q=request();q.selections[0].entity="";
    need(invalid.admit(q,auth(),0).code==Code::invalid && invalid.lease_count()==0);
    bool threw=false;try {auto bad=catalog();bad[1].fields[0].id="network.rx";r::DemandOwner duplicate(bad,policy());}
    catch(const std::invalid_argument&){threw=true;}need(threw);
}
void demand_clock() {
    r::DemandOwner owner(catalog(),policy());add(owner,request(),100);const auto job=take(owner,100);
    need(owner.tick(99)==Code::clock_fault && owner.lease_count()==0 && owner.outstanding()[0].cancelled);
    need(owner.policy(policy(8),101)==Code::clock_fault && !owner.take(102));
    need(owner.confirm_stopped(job.ticket)==Code::accepted && owner.outstanding().empty());
    const auto maximum=std::numeric_limits<std::uint64_t>::max();r::DemandOwner edge(catalog(),policy());
    const auto lease=add(edge,request(),maximum-3000);const auto last=take(edge,maximum-3000);
    need(edge.complete(last.ticket,maximum-2999)==Code::accepted);
    need(edge.renew(lease,0,maximum)==Code::obsolete && !edge.take(maximum));
}
int main(int argc,char** argv) {try {
    need(argc==2);const std::string name=argv[1];
    if(name=="DEMAND-MERGE")merge();else if(name=="DEMAND-POLICY")policy_gate();else if(name=="DEMAND-LEASES")independent_leases();
    else if(name=="DEMAND-STOP")stop_proof();else if(name=="DEMAND-CAPS")caps_and_churn();else if(name=="DEMAND-FAIRNESS")priority_fairness();
    else if(name=="DEMAND-PLANS")plans();else if(name=="DEMAND-BOUNDS")bounds();else if(name=="DEMAND-CLOCK")demand_clock();else need(false);
    std::cout<<name<<": pass\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
