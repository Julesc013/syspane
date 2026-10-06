#include "chart_history.hpp"
#include "network_publication.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace s=syspane::scene;namespace m=syspane::model;namespace r=syspane::recovery;
namespace p=syspane::protocol;namespace c=syspane::configuration;namespace n=syspane::runtime;
namespace {
constexpr std::uint64_t second=1000000000ULL;
void need(bool ok,const char* reason="chart oracle failed"){if(!ok)throw std::runtime_error(reason);}
m::Tick tick(std::uint64_t ns){return {"E1",ns,"clock:1","scope:1"};}
s::BindingFrame sample(std::uint64_t ns,std::uint64_t value=7,std::uint64_t generation=1){
    s::BindingFrame f;f.code=s::BindingCode::matched;f.total=1;s::BindingRow row;
    row.producer="P1";row.epoch="E1";row.entity="entity:1";row.generation=generation;row.code=s::BindingCode::matched;
    row.effective=m::Freshness::current;row.presentation=r::Presentation::active;row.age_ns=0;
    auto& o=row.observation;o.entity_id=row.entity;o.field="network.receive_bytes";o.source_id="source:1";o.unit="byte";
    o.value=value;o.origin=m::Origin::observed;o.support=m::Support::supported;o.acquisition=m::Acquisition::success;
    o.freshness=m::Freshness::current;o.presence=m::Presence::present;o.measured_at=tick(ns);
    f.rows.push_back(row);return f;
}
void observe(s::ChartHistory& h,const s::BindingFrame& f,const std::optional<m::Tick>& now,
             const std::function<void(const s::ChartView&)>& check=[](const auto&) {}){
    unsigned calls=0;h.observe(f,now,[&](const auto& v){++calls;check(v);});need(calls==1,"single borrow");
}
void points(const s::ChartView& v,std::initializer_list<std::uint64_t> ns,std::initializer_list<bool> joins){
    need(v.points.size()==ns.size()&&ns.size()==joins.size(),"point count");std::size_t i=0;
    auto j=joins.begin();for(auto time:ns){need(v.points[i].measured_ns==time&&v.points[i].joins_previous==*j,"point geometry");++i;++j;}
}
void no_payload(const s::ChartView& v,s::ChartCode code){need(v.code==code&&!v.identity&&v.points.empty()&&!v.window_end_ns&&!v.capacity_truncated,"erased payload");}
void limits(){
    for(auto ms:{0ULL,999ULL,3600001ULL,std::numeric_limits<unsigned long long>::max()}){
        bool rejected=false;try{s::ChartHistory h(ms,2);}catch(const p::Error& e){rejected=std::string(e.what())=="chart.settings";}need(rejected,"duration bound");}
    for(std::size_t count:{0u,1u,4097u}){bool rejected=false;try{s::ChartHistory h(1000,count);}catch(const p::Error& e){rejected=std::string(e.what())=="chart.settings";}need(rejected,"point bound");}
    s::ChartHistory h(3600000,4096);auto f=sample(0);f.rows[0].producer=std::string(8192,'p');
    observe(h,f,tick(0),[](const auto& v){no_payload(v,s::ChartCode::invalid);});
    observe(h,sample(0),tick(0),[](const auto& v){points(v,{0},{false});});
}
void window(){
    s::ChartHistory h(1000,3);observe(h,sample(100),tick(100));observe(h,sample(200,8,2),tick(200));
    observe(h,sample(200,8,2),tick(second+100),[](const auto& v){points(v,{100,200},{false,true});need(v.code==s::ChartCode::duplicate&&!v.capacity_truncated);});
    observe(h,sample(200,8,2),tick(second+101),[](const auto& v){points(v,{200},{false});});
    observe(h,sample(200,8,2),tick(second+201),[](const auto& v){points(v,{},{});need(v.code==s::ChartCode::duplicate);});
    h.clear();const auto top=std::numeric_limits<std::uint64_t>::max();observe(h,sample(top-second),tick(top-second));
    observe(h,sample(top,8,2),tick(top),[&](const auto& v){points(v,{top-second,top},{false,true});need(*v.window_end_ns==top);});
}
void capacity(){
    s::ChartHistory h(1000,2);observe(h,sample(100),tick(100));observe(h,sample(200,8,2),tick(200));
    observe(h,sample(300,9,3),tick(300),[](const auto& v){points(v,{200,300},{false,true});need(v.capacity_truncated);});
    observe(h,sample(300,9,3),tick(second+100),[](const auto& v){need(v.capacity_truncated);});
    observe(h,sample(300,9,3),tick(second+101),[](const auto& v){need(!v.capacity_truncated);points(v,{200,300},{false,true});});
    s::ChartHistory large(1000,4096);for(std::uint64_t i=0;i<5000;++i)observe(large,sample(i,i,i),tick(i),[&](const auto& v){need(v.points.size()==static_cast<std::size_t>(std::min<std::uint64_t>(i+1,4096)));});
    observe(large,sample(4999,4999,4999),tick(5000),[](const auto& v){need(v.points.front().measured_ns==904&&v.capacity_truncated&&!v.points.front().joins_previous);});
}
void replay(){
    s::ChartHistory h(1000,2);observe(h,sample(1,9),tick(1));
    observe(h,sample(1,9,2),tick(2),[](const auto& v){points(v,{1},{false});need(v.code==s::ChartCode::duplicate&&v.points[0].generation==1);});
    observe(h,sample(1,9,2),tick(second+2),[](const auto& v){points(v,{},{});});
    observe(h,sample(1,10,3),tick(second+3),[](const auto& v){no_payload(v,s::ChartCode::conflict);});
    observe(h,sample(second+4,11,4),tick(second+4),[](const auto& v){no_payload(v,s::ChartCode::conflict);});
    s::BindingFrame waiting;observe(h,waiting,{},[](const auto& v){need(v.points.empty()&&!v.identity);});
    observe(h,sample(second+5,12,5),tick(second+5),[](const auto& v){no_payload(v,s::ChartCode::conflict);});
    h.clear();observe(h,sample(5,5,9),tick(5));observe(h,sample(6,6,8),tick(6),[](const auto& v){no_payload(v,s::ChartCode::conflict);});
    h.clear();observe(h,sample(1,7),tick(1));auto stale=sample(1,8,2);stale.rows[0].effective=m::Freshness::stale;
    observe(h,stale,tick(2),[](const auto& v){no_payload(v,s::ChartCode::conflict);});
}
void gaps(){
    std::vector<std::function<void(s::BindingRow&)>> mutations{
        [](auto& r){r.observation.value=std::monostate{};},[](auto& r){r.effective=m::Freshness::stale;},
        [](auto& r){r.effective=m::Freshness::unknown;},[](auto& r){r.effective=m::Freshness::not_applicable;},
        [](auto& r){r.observation.acquisition=m::Acquisition::pending;},[](auto& r){r.observation.acquisition=m::Acquisition::failed;},
        [](auto& r){r.observation.acquisition=m::Acquisition::disabled;},[](auto& r){r.observation.presence=m::Presence::absent;},
        [](auto& r){r.observation.presence=m::Presence::unknown;},[](auto& r){r.observation.support=m::Support::unknown;},
        [](auto& r){r.observation.support=m::Support::unsupported;},[](auto& r){r.presentation=r::Presentation::retained;},
        [](auto& r){r.presentation=r::Presentation::empty;},[](auto& r){r.observation.measured_at.reset();}
    };
    for(const auto& mutate:mutations){s::ChartHistory h(1000,5);observe(h,sample(1),tick(1));auto f=sample(2,8,2);mutate(f.rows[0]);
        observe(h,f,tick(2),[](const auto& v){points(v,{1},{false});need(v.code==s::ChartCode::gap&&v.pending_break);});
        observe(h,sample(1,7,3),tick(3),[](const auto& v){need(v.pending_break&&v.code==s::ChartCode::duplicate);});
        observe(h,sample(4,10,4),tick(4),[](const auto& v){points(v,{1,4},{false,false});need(!v.pending_break);});
        observe(h,sample(5,11,5),tick(5),[](const auto& v){points(v,{1,4,5},{false,false,true});});}
    s::ChartHistory h(1000,2);observe(h,sample(1),tick(1));h.gap();observe(h,sample(1),tick(2));
    observe(h,sample(3,8,2),tick(3),[](const auto& v){points(v,{1,3},{false,false});});
}
void identity(){
    std::vector<std::function<void(s::BindingRow&)>> mutations{
        [](auto& r){r.producer="P2";},[](auto& r){r.epoch="E2";r.observation.measured_at->epoch="E2";},
        [](auto& r){r.entity="replacement";r.observation.entity_id=r.entity;},[](auto& r){r.observation.field="other.field";},
        [](auto& r){r.observation.source_id="source:2";},[](auto& r){r.observation.unit="bit";},
        [](auto& r){r.observation.value=8.0;},[](auto& r){r.observation.origin=m::Origin::derived;},
        [](auto& r){r.observation.origin=m::Origin::configured;},[](auto& r){r.observation.measured_at->clock_id="clock:2";},
        [](auto& r){r.observation.measured_at->clock_scope="scope:2";}
    };
    for(const auto& mutate:mutations){s::ChartHistory h(1000,3);observe(h,sample(10),tick(10));auto f=sample(1,8,1);mutate(f.rows[0]);
        observe(h,f,f.rows[0].observation.measured_at,[](const auto& v){points(v,{1},{false});need(v.code==s::ChartCode::ready);});}
}
void clock_cases(){
    for(unsigned fault=0;fault<5;++fault){s::ChartHistory h(1000,3);observe(h,sample(10),tick(10));auto f=sample(11,8,2);auto now=tick(11);
        if(fault==0)now.nanoseconds=9;
        if(fault==1)f.rows[0].observation.measured_at->nanoseconds=9;
        if(fault==2)now.clock_id="bad";
        if(fault==3)now.clock_scope="bad";
        if(fault==4)now.nanoseconds=10;
        observe(h,f,now,[](const auto& v){no_payload(v,s::ChartCode::clock_fault);});
        observe(h,sample(12,9,3),tick(12),[](const auto& v){no_payload(v,s::ChartCode::clock_fault);});}
    for(unsigned unavailable=0;unavailable<3;++unavailable){s::ChartHistory prior(1000,3);observe(prior,sample(10),tick(10));
        auto older=sample(9,8,2);std::optional<m::Tick> now=tick(11);
        if(unavailable==0)older.rows[0].effective=m::Freshness::stale;
        if(unavailable==1)older.rows[0].presentation=r::Presentation::retained;
        if(unavailable==2)now.reset();
        observe(prior,older,now,[](const auto& v){no_payload(v,s::ChartCode::clock_fault);});}
    s::ChartHistory h(1000,3);observe(h,sample(1),tick(1));
    observe(h,sample(2,8,2),{},[](const auto& v){points(v,{1},{false});need(v.code==s::ChartCode::clock_unknown&&v.window_end_ns==1&&v.pending_break);});
    observe(h,sample(3,9,3),tick(3),[](const auto& v){points(v,{1,3},{false,false});});
    auto retained=sample(3,9,3);retained.rows[0].presentation=r::Presentation::retained;
    observe(h,retained,tick(second+4),[](const auto& v){points(v,{},{});need(v.code==s::ChartCode::gap);});
}
void selection(){
    for(auto code:{s::BindingCode::pending,s::BindingCode::empty,s::BindingCode::denied,s::BindingCode::unsupported,
                  s::BindingCode::ambiguous,s::BindingCode::invalid,s::BindingCode::capacity}){
        s::ChartHistory h(1000,2);observe(h,sample(1),tick(1));s::BindingFrame f;f.code=code;
        observe(h,f,tick(2),[&](const auto& v){need(v.selection==code&&!v.identity&&v.points.empty());});
        observe(h,sample(3,8,2),tick(3),[](const auto& v){points(v,{3},{false});});}
    for(unsigned change=0;change<6;++change){s::ChartHistory h(1000,2);observe(h,sample(1),tick(1));auto f=sample(2,8,2);
        if(change==0)f.rows.push_back(f.rows[0]);
        if(change==1)f.total=2;
        if(change==2)f.truncated=true;
        if(change==3)f.rows[0].observation.entity_id="bad";
        if(change==4)f.rows[0].observation.field.clear();
        if(change==5)f.rows[0].code=s::BindingCode::pending;
        observe(h,f,tick(2),[](const auto& v){need(v.points.empty()&&!v.identity);});}
    for(bool row_denial:{false,true}){s::ChartHistory h(1000,2);observe(h,sample(1),tick(1));auto f=sample(2);
        if(row_denial)f.rows[0].code=s::BindingCode::denied;else f.rows[0].observation.acquisition=m::Acquisition::denied;
        observe(h,f,tick(2),[](const auto& v){no_payload(v,s::ChartCode::denied);});}
}
void numeric(){
    s::ChartHistory h(1000,4);observe(h,sample(1,9007199254740993ULL),tick(1));
    const auto maximum=std::numeric_limits<std::uint64_t>::max();observe(h,sample(2,maximum,2),tick(2),[&](const auto& v){
        need(std::get<std::uint64_t>(v.points[0].value)==9007199254740993ULL&&std::get<std::uint64_t>(v.points[1].value)==maximum);});
    for(m::Value value:{m::Value(true),m::Value(std::string("7")),m::Value(std::numeric_limits<double>::infinity()),m::Value(std::nan(""))}){
        auto f=sample(3);f.rows[0].observation.value=value;observe(h,f,tick(3),[](const auto& v){need(!v.identity&&v.points.empty());});}
    auto f=sample(4);f.rows[0].metadata=true;observe(h,f,tick(4),[](const auto& v){no_payload(v,s::ChartCode::unsupported);});
    f.rows[0].metadata=false;f.rows[0].observation.value=std::monostate{};observe(h,f,tick(4),[](const auto& v){need(v.points.empty()&&!v.identity);});
    f.rows[0].observation.value=-0.0;observe(h,f,tick(4));f.rows[0].observation.value=0.0;
    observe(h,f,tick(5),[](const auto& v){need(v.code==s::ChartCode::duplicate&&std::signbit(std::get<double>(v.points[0].value)));});
    f=sample(6,0,2);f.rows[0].observation.value=-1.25;observe(h,f,tick(6),[](const auto& v){need(std::get<double>(v.points.back().value)==-1.25);});
}
void lifetime(){
    s::ChartHistory h(1000,2);observe(h,sample(1),tick(1),[&](const auto&){
        unsigned rejected=0;for(unsigned method=0;method<3;++method)try{if(method==0)h.clear();else if(method==1)h.gap();else observe(h,sample(2),tick(2));}
        catch(const std::logic_error&){++rejected;}need(rejected==3,"reentry");});
    unsigned calls=0;try{h.observe(sample(2,8,2),tick(2),[&](const auto&){++calls;throw std::runtime_error("sink");});}
    catch(const std::runtime_error& e){need(std::string(e.what())=="sink");}need(calls==1);
    observe(h,sample(2,8,2),tick(3),[](const auto& v){points(v,{1,2},{false,true});need(v.code==s::ChartCode::duplicate);});
    h.clear();observe(h,sample(0,9,0),tick(0),[](const auto& v){points(v,{0},{false});need(!v.capacity_truncated);});
}
void wire(){
    c::Policy policy;policy.available=true;policy.revision=7;policy.disclosure[{"desktop","desktop"}]={"operational"};
    policy.disclosure[{"desktop","accessibility"}]={"operational"};
    policy.disclosure[{"desktop","history"}]={"operational"};
    r::DataView view({true,"desktop",{"desktop"}},policy,"desktop","operational",n::network_metrics());
    p::TelemetryBinding link={{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},
        {"telemetry.snapshot","telemetry.measured-time"}},"D","E1","P1","S","desktop","operational",7,
        p::TelemetryDirection::producer_to_consumer,"0.2.0","clock:1","scope:1"};
    const auto token=view.attach_wire(link,0).token;need(token!=0,"wire attach");
    n::NetworkState state("E1","clock:1","scope:1");state.demand(1);s::ChartHistory history(1000,8);
    s::BindingInput input;input.view=&view;input.producer="P1";input.entity_types={"network.interface"};
    for(const auto& metric:n::network_metrics())input.fields.emplace(metric.field,3*second);
    for(std::uint64_t i=1;i<=3;++i){need(state.commit(1,0,{syspane::platform::NetworkCode::success,0,{{9,9,6,syspane::platform::NetworkCounters{i*10,0}}}},tick(i*100),tick(i*100))==n::NetworkStateCode::accepted,"sample commit");
        auto doc=n::network_document(*state.sample(),i,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
        p::Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","P1"},{"record_id","R"+std::to_string(i)},
            {"policy_revision","7"},{"clock_id","clock:1"},{"snapshot",doc}};
        const auto bytes=p::encode_telemetry({"snapshot","D","E1",body.dump(),body},link);
        need(view.receive(token,7,bytes,i,tick(i*100)).code==r::DataCode::accepted,"wire receive");input.now=tick(i*100);
        p::Json binding={{"kind","direct"},{"producer_id","P1"},{"producer_epoch","E1"},{"entity_id",doc["entities"][0]["id"]},{"field","network.receive_bytes"}};
        s::project_binding(binding,{input},i,[&](const auto& frame){observe(history,frame,input.now,[&](const auto& v){need(v.points.size()==i,"every admitted sample");
            if(i==3){points(v,{100,200,300},{false,true,true});need(std::get<std::uint64_t>(v.points[0].value)==10&&std::get<std::uint64_t>(v.points[2].value)==30);}});});}
}
}
int chart_history_test(const std::string& name){
    if(name=="CHART-LIMITS")limits();else if(name=="CHART-WINDOW")window();else if(name=="CHART-CAPACITY")capacity();
    else if(name=="CHART-REPLAY")replay();else if(name=="CHART-GAPS")gaps();else if(name=="CHART-IDENTITY")identity();
    else if(name=="CHART-CLOCK")clock_cases();else if(name=="CHART-SELECTION")selection();else if(name=="CHART-NUMERIC")numeric();
    else if(name=="CHART-LIFETIME")lifetime();else if(name=="CHART-WIRE")wire();else throw std::runtime_error("unknown chart case");
    std::cout<<name<<" pass\n";return 0;
}
