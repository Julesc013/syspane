#include "data_view.hpp"
#include "session.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <stdexcept>
namespace m=syspane::model;
namespace r=syspane::recovery;
namespace c=syspane::configuration;
namespace p=syspane::protocol;
using p::Json;
using D=r::DataCode;
void check(bool ok,const char* expression,int line) { if (!ok) throw std::runtime_error(std::string(expression)+":"+std::to_string(line)); }
#define CHECK(x) check(static_cast<bool>(x),#x,__LINE__)
Json fixture(const std::string& root,const std::string& name) {
    std::ifstream input(root+"/valid/"+name+".json",std::ios::binary); CHECK(input.good());
    return Json::parse(std::string{std::istreambuf_iterator<char>(input),std::istreambuf_iterator<char>()});
}
c::Authority authority() { return {true,"desktop",{"desktop"}}; }
c::Policy policy(std::uint64_t revision=7) {
    c::Policy value; value.available=true; value.revision=revision;
    value.disclosure[{"desktop","desktop"}]={"operational"}; value.disclosure[{"desktop","accessibility"}]={"operational"}; return value;
}
std::vector<m::Metric> metrics() { return {{"network.media","none",m::ValueKind::string}}; }
p::TelemetryBinding binding() {
    return {{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},
        {"telemetry.snapshot","telemetry.measured-time"}},"connection:1","fixture:epoch-1","producer:1","subscription:1",
        "desktop","operational",7,p::TelemetryDirection::producer_to_consumer,"0.2.0","fixture:clock","fixture:scope"};
}
m::Tick tick(std::uint64_t n) { return {"fixture:epoch-1",n,"fixture:clock","fixture:scope"}; }
std::uint64_t attach(r::DataView& view,std::uint64_t now=0,p::TelemetryBinding b=binding()) {
    const auto result=view.attach_wire(b,now); CHECK(result.code==D::accepted); return result.token;
}
bool good(r::DataResult result) { return result.code==D::accepted || result.code==D::duplicate; }
Json full(const std::string& root,const char* record="publication:1",unsigned generation=1,std::uint64_t measured=100) {
    auto v=fixture(root,"telemetry-snapshot-v0.2"); v["body"]["record_id"]=record;
    auto& s=v["body"]["snapshot"]; s["generation"]=std::to_string(generation);
    s["observations"][0]["measured_at"]["nanoseconds"]=std::to_string(measured); return v;
}
void codec(const std::string& root) {
    const auto b=binding(); const auto w=full(root);
    const auto bytes=w.dump(); const auto message=p::decode_telemetry(bytes,b);
    const auto encoded=p::encode_telemetry(message,b);
    CHECK(p::parse(encoded)==w);
    CHECK(p::decode_telemetry(encoded,b).body_bytes==message.body_bytes);
    const auto formatted_body=w["body"].dump(2);
    const auto formatted=std::string("{\"type\":\"snapshot\",\"connection_id\":\"connection:1\",\"producer_epoch\":\"fixture:epoch-1\",\"body\":")+formatted_body+"}";
    const auto preserved=p::decode_telemetry(p::encode_telemetry(p::decode_telemetry(formatted,b),b),b);
    CHECK(preserved.body_bytes==formatted_body && preserved.body==message.body);
    for (unsigned variant=0;variant<13;++variant) {
        auto bad=w; auto local=b; auto& o=bad["body"]["snapshot"]["observations"][0];
        if (variant==0) bad["body"].erase("clock_id");
        if (variant==1) bad["body"]["clock_id"]="other";
        if (variant==2) o["measured_at"]["clock_id"]="other";
        if (variant==3) o["measured_at"]["nanoseconds"]="18446744073709551616";
        if (variant==4) o["measured_at"]["nanoseconds"]="0100";
        if (variant==5) o["measured_at"]["nanoseconds"]=100;
        if (variant==6) o["value"]=nullptr;
        if (variant==7) o.erase("measured_at");
        if (variant==8) o["schema_version"]="0.1.0";
        if (variant==9) local.negotiated.features.erase("telemetry.measured-time");
        if (variant==10) local.negotiated.documents.erase({"observation","0.2.0"});
        if (variant==11) local.clock_scope.clear();
        if (variant==12) bad["body"]["snapshot"]["schema_version"]="0.1.0";
        bool rejected=false; try { p::decode_telemetry(bad.dump(),local); } catch (const p::Error&) { rejected=true; }
        CHECK(rejected);
    }
    auto old=b; old.document_version="0.1.0"; old.clock_id.clear(); old.clock_scope.clear();
    old.negotiated.documents={{"telemetry","0.1.0"},{"snapshot","0.1.0"},{"observation","0.1.0"}};
    old.negotiated.features={"telemetry.snapshot"};
    CHECK(p::decode_telemetry(fixture(root,"telemetry-snapshot").dump(),old).type=="snapshot");
}
void age(const std::string& root) {
    r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(view);
    CHECK(good(view.receive(token,7,full(root).dump(),1,tick(100))));
    unsigned ordinal=0;
    for (const auto count : {100ULL,109ULL,110ULL}) {
        CHECK(view.project_measured(2+ordinal,tick(count),[&](const auto& s,const auto& lease,const auto& now) {
            const auto& o=s.observations[0]; CHECK(o.measured_at==std::optional<m::Tick>(tick(100)));
            CHECK(lease.presentation==r::Presentation::active);
            CHECK(m::freshness_at(o,now,10)==(count<110?m::Freshness::current:m::Freshness::stale));
            CHECK(m::freshness_at(o,now,0)==m::Freshness::stale);
            for (unsigned variant=0;variant<4;++variant) {
                auto mismatch=now;
                if (variant==0) mismatch.epoch="other";
                if (variant==1) mismatch.clock_id="other";
                if (variant==2) mismatch.clock_scope="other";
                if (variant==3) mismatch.nanoseconds=99;
                CHECK(m::freshness_at(o,mismatch,1000)==m::Freshness::stale);
                CHECK(!m::interval_ns(*o.measured_at,mismatch));
            }
            auto missing=o; missing.measured_at.reset(); CHECK(m::freshness_at(missing,now,10)==m::Freshness::stale);
            CHECK(m::freshness_at(missing,now,{})==m::Freshness::current);
            auto retained=o; retained.acquisition=m::Acquisition::failed;
            CHECK(m::freshness_at(retained,tick(100),1000)==m::Freshness::stale);
        })); ++ordinal;
    }
    CHECK(!m::interval_ns(tick(100),tick(100))); CHECK(m::interval_ns(tick(100),tick(110))==10);
    const auto maximum=std::numeric_limits<std::uint64_t>::max();
    CHECK(m::interval_ns(tick(maximum-1),tick(maximum))==1);
    r::DataView edge(authority(),policy(),"desktop","operational",metrics()); const auto e=attach(edge);
    CHECK(good(edge.receive(e,7,full(root,"maximum",1,maximum).dump(),1,tick(maximum))));
    CHECK(edge.project_measured(2,tick(maximum),[](const auto& s,const auto&,const auto& now) {
        CHECK(m::freshness_at(s.observations[0],now,1)==m::Freshness::current);
    }));
    r::DataView future(authority(),policy(),"desktop","operational",metrics()); const auto f=attach(future);
    CHECK(future.receive(f,7,full(root,"future",1,101).dump(),1,tick(100)).code==D::invalid);
    CHECK(!future.status(2).payload_available);
    const auto next=attach(future,3); CHECK(good(future.receive(next,7,full(root).dump(),4,tick(101))));
}
void replay(const std::string& root) {
    r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto t=attach(view);
    const auto first=full(root).dump(); CHECK(good(view.receive(t,7,first,1,tick(100))));
    CHECK(view.receive(t,7,first,2,tick(110)).code==D::duplicate);
    CHECK(good(view.receive(t,7,full(root,"confirm").dump(),3,tick(110))));
    CHECK(view.project_measured(4,tick(110),[](const auto& s,const auto&,const auto& now) {
        CHECK(s.observations[0].measured_at->nanoseconds==100);
        CHECK(m::freshness_at(s.observations[0],now,10)==m::Freshness::stale);
    }));
    CHECK(view.receive(t,7,full(root,"older",2,90).dump(),5,tick(110)).code==D::invalid);
    auto absent=full(root,"temporarily-missing",2); absent["body"]["snapshot"]["observations"]=Json::array();
    CHECK(good(view.receive(t,7,absent.dump(),6,tick(110))));
    CHECK(view.receive(t,7,full(root,"older-again",3,90).dump(),7,tick(110)).code==D::invalid);
    CHECK(view.project(8,[](const auto& s,const auto&) { CHECK(s.generation==2 && s.observations.empty()); }));
    CHECK(view.receive(t,7,first,9,tick(110)).code==D::duplicate);
    CHECK(view.project(10,[](const auto& s,const auto&) { CHECK(s.generation==2); }));
    m::Limits limits; limits.observations=1;
    r::DataView bounded(authority(),policy(),"desktop","operational",metrics(),limits); const auto bt=attach(bounded);
    CHECK(good(bounded.receive(bt,7,first,1,tick(100))));
    CHECK(good(bounded.receive(bt,7,absent.dump(),2,tick(110))));
    auto another=full(root,"new-source",3,110);
    another["body"]["snapshot"]["sources"][0]["id"]="source:two";
    another["body"]["snapshot"]["observations"][0]["source_id"]="source:two";
    CHECK(bounded.receive(bt,7,another.dump(),3,tick(110)).code==D::capacity);
}
void lifetime(const std::string& root) {
    r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto first=attach(view);
    CHECK(good(view.receive(first,7,full(root).dump(),1,tick(100)))); CHECK(view.disconnect(first,7,2)==D::accepted);
    auto b=binding(); b.connection="connection:2"; const auto second=attach(view,3,b);
    CHECK(view.receive(first,7,"bad",0,tick(0)).code==D::stale_attachment);
    auto confirm=full(root,"confirm"); confirm["connection_id"]=b.connection;
    CHECK(good(view.receive(second,7,confirm.dump(),4,tick(105))));
    auto incompatible=b; incompatible.clock_scope="other";
    CHECK(view.attach_wire(incompatible,5).code==D::invalid);
    incompatible.document_version="0.1.0"; incompatible.clock_id.clear(); incompatible.clock_scope.clear();
    incompatible.negotiated.documents={{"telemetry","0.1.0"},{"snapshot","0.1.0"},{"observation","0.1.0"}};
    CHECK(view.attach_wire(incompatible,5).code==D::invalid);
    CHECK(view.heartbeat(second,7,0,5)==D::accepted);
    b.epoch="epoch:2"; b.connection="connection:3"; const auto third=attach(view,6,b);
    auto next=full(root,"next-epoch",1,106); next["connection_id"]=b.connection; next["producer_epoch"]=b.epoch;
    next["body"]["snapshot"]["producer_epoch"]=b.epoch; next["body"]["snapshot"]["observations"][0]["producer_epoch"]=b.epoch;
    auto now=tick(107); now.epoch=b.epoch;
    CHECK(good(view.receive(third,7,next.dump(),7,now)));
    now.nanoseconds=106; CHECK(view.receive(third,7,next.dump(),8,now).code==D::clock_fault);
    CHECK(view.status(9).payload_available && !view.status(9).alive);
    CHECK(view.attach_wire(b,10).code==D::clock_fault);
    auto denied=policy(8); denied.available=false; CHECK(view.policy(denied,0)==D::denied);
    CHECK(!view.status(10).payload_available);
    view.policy(policy(9),11); b.policy_revision=9; CHECK(view.attach_wire(b,12).code==D::clock_fault);
    for (unsigned variant=0;variant<4;++variant) {
        r::DataView faulty(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(faulty);
        std::optional<m::Tick> wrong=tick(100);
        if (variant==0) wrong.reset();
        if (variant==1) wrong->clock_id="wrong";
        if (variant==2) wrong->clock_scope="wrong";
        if (variant==3) wrong->epoch="wrong";
        CHECK(faulty.receive(token,7,full(root).dump(),1,wrong).code==D::clock_fault);
    }
}
void session(const std::string& root) {
    const auto b=binding();
    for (unsigned variant=0;variant<6;++variant) {
        c::TelemetrySource source{"producer:1","desktop","operational"};
        source.document_version="0.2.0"; source.clock_id=b.clock_id; source.clock_scope=b.clock_scope;
        c::Sessions sessions(b.epoch,0,policy(),source); sessions.open(b.connection,"principal",authority(),0);
        Json docs=Json::array(); for (const auto& pair : b.negotiated.documents) docs.push_back({{"document",pair.first},{"version",pair.second}});
        Json hello{{"type","hello"},{"body",{{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","client"},
            {"max_frame_bytes",p::frame_limit},{"document_versions",docs},{"required_features",{"telemetry.snapshot","telemetry.measured-time"}},
            {"optional_features",Json::array()}}}};
        if (variant==1) hello["body"]["document_versions"].erase(0);
        if (variant==2 || variant==4) hello["body"]["required_features"]={"telemetry.snapshot"};
        if (variant==4) for (auto& doc : hello["body"]["document_versions"]) doc["version"]="0.1.0";
        if (variant==5) hello["body"]["required_features"]=Json::array();
        sessions.receive(b.connection,hello.dump(),1);
        if (variant==1 || variant==2 || variant==4) { CHECK(sessions.closed(b.connection)); CHECK(!sessions.pop(b.connection,2)); continue; }
        CHECK(p::decode(*sessions.pop(b.connection,2)).type=="welcome");
        auto subscribe=fixture(root,"telemetry-subscribe-v0.2");
        if (variant==3) subscribe["body"]["clock_id"]="wrong";
        sessions.receive(b.connection,subscribe.dump(),3);
        if (variant==3 || variant==5) { CHECK(sessions.closed(b.connection) && !sessions.subscription(b.connection)); continue; }
        const auto sub=sessions.subscription(b.connection); CHECK(sub && sub->binding.document_version=="0.2.0");
        CHECK(sessions.offer(b.connection,sub->ticket,"offered",full(root)["body"]["snapshot"],{},4));
        const auto payload=sessions.pop(b.connection,5); CHECK(payload);
        CHECK(p::decode_telemetry(*payload,b).body["schema_version"]=="0.2.0");
    }
}
int main(int argc,char** argv) {
    try {
        CHECK(argc==3); const std::string name=argv[1],root=argv[2];
        if (name=="MEASURED-CODEC") codec(root); else if (name=="MEASURED-AGE") age(root);
        else if (name=="MEASURED-REPLAY") replay(root); else if (name=="MEASURED-LIFETIME") lifetime(root);
        else if (name=="MEASURED-SESSION") session(root); else CHECK(false);
        std::cout<<name<<": pass\n"; return 0;
    } catch (const std::exception& error) { std::cerr<<error.what()<<'\n'; return 1; }
}
