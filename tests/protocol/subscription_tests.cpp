#include "session.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
namespace p=syspane::protocol;
namespace c=syspane::configuration;
using p::Json;
void check(bool ok,const char* code,int line) { if (!ok) throw std::runtime_error(std::string(code)+":"+std::to_string(line)); }
#define CHECK(x) check(static_cast<bool>(x),#x,__LINE__)
c::Policy policy(std::uint64_t rev=7) {
    c::Policy p; p.available=true; p.revision=rev;
    p.disclosure[{"desktop","desktop"}]={"operational"}; p.disclosure[{"desktop","accessibility"}]={"operational"}; return p;
}
c::InventorySource source(std::uint64_t tickets=1000) { return {"producer:1","desktop","operational",tickets}; }
Json envelope(const char* type,Json body,const std::string& id="C") {
    return {{"type",type},{"connection_id",id},{"producer_epoch","fixture:epoch-1"},{"body",std::move(body)}};
}
Json subscribe() { return {{"schema_version","0.1.0"},{"subscription_id","S"},{"producer_id","producer:1"},
    {"policy_revision","7"},{"channel","desktop"},{"classification","operational"}}; }
Json hello() { return {{"type","hello"},{"body",{{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","client"},
    {"max_frame_bytes",p::frame_limit},{"document_versions",Json::array({{{"document","telemetry"},{"version","0.1.0"}},
    {{"document","snapshot"},{"version","0.1.0"}},{{"document","observation"},{"version","0.1.0"}},{{"document","command"},{"version","0.2.0"}}})},
    {"required_features",Json::array()},{"optional_features",{"telemetry.snapshot"}}}}}; }
void open(c::Sessions& s,Json h=hello(),const std::string& id="C",std::uint64_t now=0) {
    s.open(id,"principal",{true,"desktop",{"desktop","console"}},now); s.receive(id,h.dump(),now);
}
std::uint64_t admit(c::Sessions& s,const std::string& id="C",std::uint64_t now=0) {
    open(s,hello(),id,now); CHECK(s.pop(id,now)); s.receive(id,envelope("subscribe",subscribe(),id).dump(),now);
    CHECK(s.subscription(id)); return s.subscription(id)->ticket;
}
Json snapshot(const std::string& root,std::uint64_t gen=1) {
    std::ifstream in(root+"/valid/snapshot.json",std::ios::binary); CHECK(in.good());
    const std::string bytes{std::istreambuf_iterator<char>(in),std::istreambuf_iterator<char>()};
    auto s=Json::parse(bytes); s["generation"]=std::to_string(gen); return s;
}
void admission() {
    c::Sessions disabled("fixture:epoch-1",0,policy()); open(disabled);
    CHECK(p::decode(*disabled.pop("C",0)).body["optional_features"].empty());
    disabled.receive("C",envelope("subscribe",subscribe()).dump(),0); CHECK(disabled.closed("C"));
    for (const bool required : {false,true}) {
        c::Sessions s("fixture:epoch-1",0,policy(),source()); auto h=hello(); h["body"]["document_versions"].erase(2);
        if (required) h["body"]["required_features"]={"telemetry.snapshot"};
        open(s,h);
        if (required) CHECK(s.closed("C")); else CHECK(p::decode(*s.pop("C",0)).body["optional_features"].empty());
    }
    for (unsigned variant=0;variant<5;++variant) {
        auto pol=policy(); if (variant==0) pol.available=false; if (variant==1) pol.denied_capabilities.insert("telemetry.subscribe");
        if (variant==2) pol.disclosure[{"desktop","accessibility"}].clear();
        c::Sessions s("fixture:epoch-1",0,pol,source()); auto h=hello(); if (variant==3) h["body"]["role"]="console";
        open(s,h); CHECK(s.pop("C",0)); auto body=subscribe(); if (variant==4) body["producer_id"]="other";
        s.receive("C",envelope("subscribe",body).dump(),0); CHECK(s.closed("C") && s.demand_count()==0);
    }
    for (unsigned variant=0;variant<3;++variant) {
        c::Sessions s("fixture:epoch-1",0,policy(),source()); admit(s); auto body=subscribe();
        if (variant==0) body["subscription_id"]="other";
        if (variant==1) body["policy_revision"]="8";
        const auto wire=envelope("subscribe",body); s.receive("C",variant==2 ? wire.dump(2) : wire.dump(),0);
        CHECK(s.closed("C") && s.demand_count()==0);
    }
}
void queues(const std::string& root) {
    c::Sessions s("fixture:epoch-1",0,policy(),source()); auto ticket=admit(s);
    CHECK(!s.offer("C",ticket,"delta-first",snapshot(root,2),1,0)); CHECK(p::decode(*s.pop("C",0)).type=="gap");
    CHECK(s.offer("C",ticket,"one",snapshot(root),{},0)); CHECK(s.offer("C",ticket,"two",snapshot(root,2),1,0));
    s.receive("C",envelope("heartbeat",{{"sequence","0"}}).dump(),0);
    CHECK(p::decode(*s.pop("C",0)).type=="heartbeat"); CHECK(p::decode(*s.pop("C",0)).type=="snapshot"); CHECK(p::decode(*s.pop("C",0)).type=="delta");
    CHECK(!s.offer("C",ticket,"wrong-base",snapshot(root,4),1,0)); CHECK(p::decode(*s.pop("C",0)).body["reason"]=="resync_required");
    auto partial=snapshot(root,4); partial["completeness"]="partial";
    CHECK(!s.offer("C",ticket,"partial",partial,{},0)); CHECK(p::decode(*s.pop("C",0)).type=="gap");
    for (unsigned i=0;i<16;++i) CHECK(s.offer("C",ticket,"queue"+std::to_string(i),snapshot(root,i+4),{},0));
    CHECK(!s.offer("C",ticket,"overflow",snapshot(root,20),{},0));
    CHECK(p::decode(*s.pop("C",0)).body["reason"]=="queue_overflow" && !s.pop("C",0));
    CHECK(s.offer("C",ticket,"recovery",snapshot(root,20),{},0));
    s.receive("C",envelope("subscribe",subscribe()).dump(),0); CHECK(!s.pop("C",0));
    CHECK(s.subscription("C")->ticket!=ticket && s.demand_count()==1);
    CHECK(!s.offer("C",ticket,"obsolete",Json(),{},999999)); ticket=s.subscription("C")->ticket;
    CHECK(s.offer("C",ticket,"new-full",snapshot(root,20),{},1));
    const auto cancel=envelope("unsubscribe",{{"schema_version","0.1.0"},{"subscription_id","S"}}).dump();
    s.receive("C",cancel,1); s.receive("C",cancel,1); CHECK(!s.pop("C",1) && s.demand_count()==0);
    s.receive("C",envelope("subscribe",subscribe()).dump(),1); CHECK(s.closed("C"));
}
void lifetime(const std::string& root) {
    c::Sessions s("fixture:epoch-1",0,policy(),source()); const auto first=admit(s);
    s.receive("C",envelope("heartbeat",{{"sequence","1"}}).dump(),1000); CHECK(s.pop("C",1000));
    s.receive("C",envelope("heartbeat",{{"sequence","1"}}).dump(),2000); CHECK(s.pop("C",2000));
    s.receive("C",envelope("subscribe",subscribe()).dump(),2500);
    s.tick(3999); CHECK(s.demand_count()==1); s.tick(4000); CHECK(s.closed("C") && s.demand_count()==0);
    s.disconnect("C"); const auto successor=admit(s,"C",4001); CHECK(successor>first);
    CHECK(!s.offer("C",first,"obsolete",Json(),{},0)); CHECK(s.offer("C",successor,"one",snapshot(root),{},4002));
    auto pol=policy(8); pol.available=false; s.policy(pol,4003);
    CHECK(s.demand_count()==0 && p::decode(*s.pop("C",4003)).body["reason"]=="policy_changed" && !s.pop("C",4003));
    for (const bool clock : {false,true}) {
        c::Sessions failed("fixture:epoch-1",0,policy(),source()); const auto t=admit(failed,"C",10);
        CHECK(failed.offer("C",t,"secret",snapshot(root),{},11)); bool caught=false;
        try { failed.policy(policy(clock?8:7),clock?0:12); } catch (const p::Error&) { caught=true; }
        CHECK(caught && failed.closed("C") && failed.demand_count()==0 && !failed.subscription("C"));
    }
    c::Sessions bounded("fixture:epoch-1",0,policy(),source(1)); admit(bounded);
    bounded.receive("C",envelope("subscribe",subscribe()).dump(),0); CHECK(bounded.closed("C") && bounded.demand_count()==0);
    c::Sessions control("fixture:epoch-1",0,policy(),source()); admit(control);
    for (unsigned i=0;i<17;++i) control.receive("C",envelope("heartbeat",{{"sequence",std::to_string(i)}}).dump(),0);
    CHECK(control.closed("C") && control.demand_count()==0);
}
int main(int argc,char** argv) {
    try {
        if (argc!=3) return 2;
        const std::string test=argv[1];
        if (test=="SUB-ADMIT") admission(); else if (test=="SUB-QUEUE") queues(argv[2]); else if (test=="SUB-LIFETIME") lifetime(argv[2]); else return 2;
        std::cout<<test<<": pass\n"; return 0;
    } catch (const std::exception& e) { std::cerr<<e.what()<<'\n'; return 1; }
}
