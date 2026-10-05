#include "data_view.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
namespace m=syspane::model;
namespace r=syspane::recovery;
namespace c=syspane::configuration;
namespace p=syspane::protocol;
using D=r::DataCode;
using p::Json;
void check(bool value,const char* code,int line) { if (!value) throw std::runtime_error(std::string(code)+":"+std::to_string(line)); }
#define CHECK(x) check(static_cast<bool>(x),#x,__LINE__)
Json fixture(const std::string& root,const std::string& name) {
    std::ifstream input(root+"/valid/"+name+".json",std::ios::binary); CHECK(input.good());
    const std::string data{std::istreambuf_iterator<char>(input),std::istreambuf_iterator<char>()}; return Json::parse(data);
}
c::Authority authority() { return {true,"desktop",{"desktop"}}; }
c::Policy policy(std::uint64_t revision=7) {
    c::Policy result; result.available=true; result.revision=revision;
    result.disclosure[{"desktop","desktop"}]={"operational"}; result.disclosure[{"desktop","accessibility"}]={"operational"}; return result;
}
std::vector<m::Metric> metrics() { return {{"network.media","none",m::ValueKind::string},{"network.rx_total","byte",m::ValueKind::uint64}}; }
p::TelemetryBinding binding(std::uint64_t revision=7) {
    return {{1,p::frame_limit,{{"telemetry","0.1.0"},{"snapshot","0.1.0"},{"observation","0.1.0"}},{"telemetry.snapshot"}},
        "connection:1","fixture:epoch-1","producer:1","subscription:1","desktop","operational",revision,p::TelemetryDirection::producer_to_consumer};
}
std::uint64_t attach(r::DataView& view,std::uint64_t now=0,const p::TelemetryBinding& b=binding()) {
    const auto result=view.attach_wire(b,now); CHECK(result.code==D::accepted && result.token); return result.token;
}
Json full(const std::string& root,std::string record="publication:1",std::uint64_t generation=1) {
    auto wire=fixture(root,"telemetry-snapshot"); wire["body"]["record_id"]=std::move(record);
    wire["body"]["snapshot"]["generation"]=std::to_string(generation); return wire;
}
void expect(r::DataView& view,std::uint64_t now,std::uint64_t generation,const std::string& value,r::Presentation presentation) {
    CHECK(view.project(now,[&](const m::Snapshot& s,const r::LeaseView& lease) {
        CHECK(s.generation==generation && std::get<std::string>(s.observations.at(0).value)==value);
        CHECK(lease.presentation==presentation && lease.last->generation==generation);
    }));
}
void state(const std::string& root) {
    r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(view);
    auto wire=full(root); auto& doc=wire["body"]["snapshot"];
    doc["extensions"]={{"inert",{{"approval",true},{"future",Json::array({1,2})}}}};
    doc["entities"][0]["extensions"]={{"future","kept"}};
    CHECK(view.receive(token,7,wire.dump(),10).code==D::accepted);
    CHECK(view.project(11,[&](const m::Snapshot& s,const r::LeaseView& lease) {
        CHECK(s.entities[0].identity.at("fixture")=="true" && s.observations[0].generation==1);
        CHECK(s.captured_at.has_value() && s.captured_at->seconds==s.observations[0].observed_at->seconds);
        CHECK(Json::parse(s.reported_document)==doc && lease.presentation==r::Presentation::active);
        CHECK(!s.observations[0].measured_at && s.observations[0].acquisition==m::Acquisition::success);
    }));
    expect(view,12,1,"connected",r::Presentation::active);
}
void retain(const std::string& root) {
    auto remote=full(root,"remote:2",2);
    remote["body"]["snapshot"]["observations"]=Json::array({fixture(root,"observation-retained-denied")});
    remote["body"]["snapshot"]["observations"][0]["value"]["data"]="remote-new";
    remote["body"]["snapshot"]["observations"][0]["generation"]="2";
    for (const bool existing : {false,true}) {
        r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(view);
        if (existing) { auto old=full(root); old["body"]["snapshot"]["observations"][0]["value"]["data"]="local-old"; CHECK(view.receive(token,7,old.dump(),10).code==D::accepted); }
        CHECK(view.receive(token,7,remote.dump(),20).code==D::accepted);
        expect(view,21,2,"remote-new",r::Presentation::active);
        CHECK(view.project(22,[](const m::Snapshot& s,const r::LeaseView&) {
            const auto& o=s.observations[0]; CHECK(o.acquisition==m::Acquisition::denied && o.freshness==m::Freshness::stale);
            CHECK(o.error && o.error->code=="permission.denied" && o.generation==2);
        }));
    }
    for (unsigned variant=0;variant<7;++variant) {
        r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(view);
        CHECK(view.receive(token,7,full(root).dump(),10).code==D::accepted);
        auto bad=remote; auto& o=bad["body"]["snapshot"]["observations"][0];
        if (variant==0) o["freshness"]="current";
        if (variant==1) o["observed_at"]=nullptr;
        if (variant==2) o["support"]="unsupported";
        if (variant==3) o["unit"]="wrong";
        if (variant==4) o["value"]={{"kind","boolean"},{"data",true}};
        if (variant==5) { o["value"]=nullptr; o["freshness"]="unknown"; }
        if (variant==6) { o["value"]=nullptr; o["observed_at"]=nullptr; o["freshness"]="stale"; }
        CHECK(view.receive(token,7,bad.dump(),20).validation==m::Code::invalid_observation);
        expect(view,21,1,"connected",r::Presentation::retained);
    }
    r::DataView absent(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(absent);
    auto unsupported=full(root); unsupported["body"]["snapshot"]["observations"]=Json::array({fixture(root,"observation-unsupported")});
    CHECK(absent.receive(token,7,unsupported.dump(),10).code==D::accepted);
    CHECK(absent.project(11,[](const m::Snapshot& s,const r::LeaseView&) { CHECK(s.observations[0].value.index()==0 && s.observations[0].freshness==m::Freshness::not_applicable); }));
}
void coverage(const std::string& root) {
    r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(view);
    CHECK(view.receive(token,7,full(root).dump(),10).code==D::accepted);
    for (const auto kind : {"partial","gap"}) {
        auto incomplete=full(root,"incomplete:2",2); auto& doc=incomplete["body"]["snapshot"];
        doc["completeness"]=kind; doc["entities"]=Json::array(); doc["observations"]=Json::array();
        CHECK(view.receive(token,7,incomplete.dump(),20).code==D::snapshot_required);
        expect(view,20,1,"connected",r::Presentation::retained);
    }
    auto delta=full(root,"delta:2",2); delta["type"]="delta"; delta["body"]["base_generation"]="1";
    CHECK(view.receive(token,7,delta.dump(),21).code==D::snapshot_required);
    CHECK(view.receive(token,7,full(root,"incomplete:2",2).dump(),22).code==D::accepted); // Incomplete ID was not reserved.
    auto removed=full(root,"removed:3",3); removed["body"]["snapshot"]["entities"]=Json::array(); removed["body"]["snapshot"]["observations"]=Json::array();
    CHECK(view.receive(token,7,removed.dump(),23).code==D::accepted);
    auto b=binding(); b.connection="connection:2"; b.subscription="subscription:2"; const auto successor=attach(view,24,b);
    removed["connection_id"]=b.connection; removed["body"]["subscription_id"]=b.subscription; removed["body"]["record_id"]="confirm:3";
    CHECK(view.receive(successor,7,removed.dump(),25).code==D::accepted);
    auto reused=full(root,"reuse:4",4); reused["connection_id"]=b.connection; reused["body"]["subscription_id"]=b.subscription;
    CHECK(view.receive(successor,7,reused.dump(),26).validation==m::Code::retired_identity);
    CHECK(view.project(27,[](const m::Snapshot& s,const r::LeaseView& lease) { CHECK(s.entities.empty() && s.generation==3 && lease.presentation==r::Presentation::retained); }));
}
void replay(const std::string& root) {
    r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(view);
    auto first=full(root); CHECK(view.receive(token,7,first.dump(),10).code==D::accepted);
    CHECK(view.receive(token,7,first.dump(),11).code==D::duplicate);
    CHECK(view.project(12,[](const m::Snapshot&,const r::LeaseView& lease) { CHECK(lease.last->accepted_ms==10); }));
    CHECK(view.receive(token,7,first.dump(2),13).validation==m::Code::conflict);
    CHECK(view.receive(token,7,full(root,"confirm:1").dump(),14).code==D::accepted);
    auto changed=full(root,"changed:1"); changed["body"]["snapshot"]["entities"][0]["identity"]["fixture"]="changed";
    CHECK(view.receive(token,7,changed.dump(),15).validation==m::Code::conflict);
    CHECK(view.receive(token,7,full(root,"confirm:1").dump(),16).code==D::accepted);
    auto delta=full(root,"delta:2",2); delta["type"]="delta"; delta["body"]["base_generation"]="1";
    CHECK(view.receive(token,7,delta.dump(),17).code==D::accepted);
    CHECK(view.receive(token,7,delta.dump(),18).code==D::duplicate);
    CHECK(view.receive(token,7,first.dump(),19).code==D::duplicate);
    expect(view,20,2,"connected",r::Presentation::active);
    CHECK(view.gap(token,7,21)==D::accepted);
    CHECK(view.receive(token,7,first.dump(),22).code==D::duplicate && view.status(22).snapshot_required);
    CHECK(view.receive(token,7,full(root,"confirm:2",2).dump(),23).code==D::accepted);
    m::Limits limits; limits.replay_records=1;
    r::DataView bounded(authority(),policy(),"desktop","operational",metrics(),limits); const auto one=attach(bounded);
    CHECK(bounded.receive(one,7,first.dump(),10).code==D::accepted);
    const auto again=attach(bounded,11); CHECK(bounded.receive(again,7,first.dump(),12).code==D::accepted);
    CHECK(bounded.receive(again,7,full(root,"new-id").dump(),13).code==D::capacity);
    expect(bounded,14,1,"connected",r::Presentation::retained);
}
void times(const std::string& root) {
    struct Oracle { const char* source; std::int64_t seconds; std::uint32_t nanos; const char* suffix; };
    const Oracle cases[]={{"1970-01-01T01:30:00+01:30",0,0,""},{"1969-12-31T23:59:59.123456789012300Z",-1,123456789,"0123"},
        {"2000-02-29T00:00:00Z",951782400,0,""},{"1999-12-31T23:00:00-01:00",946684800,0,""},
        {"1970-01-01T00:00:00.000000000001Z",0,0,"001"},{"1970-01-01T00:00:00.100000000000Z",0,100000000,""}};
    for (const auto& expected : cases) {
        r::DataView view(authority(),policy(),"desktop","operational",metrics()); const auto token=attach(view);
        auto wire=full(root); auto& s=wire["body"]["snapshot"]; s["captured_at"]=expected.source;
        auto& o=s["observations"][0]; o["observed_at"]=expected.source; o["attempted_at"]=expected.source; o["sample_interval_ns"]="1000000000";
        CHECK(view.receive(token,7,wire.dump(),10).code==D::accepted);
        CHECK(view.heartbeat(token,7,0,1000)==D::accepted);
        CHECK(view.project(1001,[&](const m::Snapshot& snapshot,const r::LeaseView&) {
            const auto& observation=snapshot.observations[0]; const auto& time=*observation.observed_at;
            CHECK(time.seconds==expected.seconds && time.nanoseconds==expected.nanos && time.subnanoseconds==expected.suffix);
            CHECK(*snapshot.captured_at==time && observation.attempted_at==time && !observation.measured_at);
            CHECK(Json::parse(snapshot.reported_document)["observations"][0]["observed_at"]==expected.source);
            CHECK(observation.sample_interval_ns==1000000000 && m::freshness_at(observation,{"fixture:epoch-1",1},1000000000)==m::Freshness::stale);
        }));
    }
}
void lifetime(const std::string& root) {
    r::DataView view(authority(),policy(),"desktop","operational",metrics());
    auto bad=binding(); bad.policy_revision=6; CHECK(view.attach_wire(bad,0).code==D::policy_changed);
    bad=binding(); bad.channel="preview"; CHECK(view.attach_wire(bad,0).code==D::invalid);
    bad=binding(); bad.negotiated.documents.clear(); CHECK(view.attach_wire(bad,0).code==D::invalid);
    const auto token=attach(view); CHECK(view.receive(token,7,full(root).dump(),10).code==D::accepted);
    auto wrong=full(root); wrong["connection_id"]="other"; CHECK(view.receive(token,7,wrong.dump(),11).code==D::invalid);
    CHECK(!view.status(12).alive); expect(view,12,1,"connected",r::Presentation::retained);
    const auto successor=attach(view,13);
    CHECK(view.receive(token,7,"invalid",999999).code==D::stale_attachment);
    CHECK(view.receive(successor,6,"invalid",0).code==D::policy_changed);
    CHECK(view.receive(successor,7,full(root).dump(),14).code==D::accepted);
    c::Policy missing; CHECK(view.policy(missing,15)==D::denied);
    CHECK(!view.status(15).payload_available && !view.project(15,[](const m::Snapshot&,const r::LeaseView&) { CHECK(false); }));
    CHECK(view.policy(policy(9),16)==D::accepted); const auto renewed=attach(view,16,binding(9));
    CHECK(view.receive(successor,7,full(root).dump(),999999).code==D::stale_attachment);
    auto fresh=full(root); fresh["body"]["policy_revision"]="9";
    CHECK(view.receive(renewed,9,fresh.dump(),17).code==D::accepted);
    CHECK(view.status(16).reason==r::LeaseReason::clock_fault);
    CHECK(view.policy(missing,0)==D::denied && !view.status(18).payload_available);
    r::DataView modes(authority(),policy(),"desktop","operational",metrics()); const auto imported=attach(modes);
    CHECK(modes.receive(imported,7,full(root).dump(),10).code==D::accepted);
    m::Publication candidate{"local:2",{}, {"producer:1","fixture:epoch-1",2,{},{},{},{}}};
    CHECK(modes.full(imported,7,candidate,11).validation==m::Code::invalid_mode);
    const auto typed=modes.attach("producer:1","fixture:epoch-1",12).token;
    CHECK(modes.full(typed,7,candidate,13).validation==m::Code::invalid_mode);
    expect(modes,14,1,"connected",r::Presentation::retained);
    m::Limits tiny; tiny.candidate_bytes=1;
    r::DataView bounded(authority(),policy(),"desktop","operational",metrics(),tiny); const auto bt=attach(bounded);
    CHECK(bounded.receive(bt,7,full(root).dump(),10).code==D::capacity && !bounded.status(11).payload_available);
}
int main(int argc,char** argv) {
    try {
        if (argc!=3) return 2;
        const std::string name=argv[1],root=argv[2];
        if (name=="IMPORT-STATE") state(root); else if (name=="IMPORT-RETAIN") retain(root); else if (name=="IMPORT-COVERAGE") coverage(root);
        else if (name=="IMPORT-REPLAY") replay(root); else if (name=="IMPORT-TIME") times(root); else if (name=="IMPORT-LIFETIME") lifetime(root); else return 2;
        std::cout<<name<<": pass\n"; return 0;
    } catch (const std::exception& e) { std::cerr<<e.what()<<'\n'; return 1; }
}
