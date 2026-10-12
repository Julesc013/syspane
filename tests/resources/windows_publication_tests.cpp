#include "processor_publication.hpp"
#include "network_publication.hpp"
#include "data_view.hpp"
#include "demand.hpp"
#include <iostream>
#include <stdexcept>

namespace n=syspane::runtime;namespace os=syspane::platform;
namespace p=syspane::protocol;namespace c=syspane::configuration;namespace r=syspane::recovery;
using J=p::Json;using R=os::ProcessorReadCode;using S=n::ProcessorStateCode;
const std::string utc="2026-10-12T07:00:00Z",later="2026-10-12T07:00:01Z";
void need(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
void admitted(const r::DataResult& result,const char* message){if(result.code!=r::DataCode::accepted){std::cerr<<message<<" data="<<static_cast<int>(result.code)<<" validation="<<(result.validation?static_cast<int>(*result.validation):-1)<<'\n';throw std::runtime_error(message);}}
syspane::model::Tick tick(std::uint64_t ns){return {"epoch:1",ns,"clock:1","scope:1"};}
os::WindowsProcessorCapture capture(std::uint64_t a=40,std::uint64_t ai=60,std::uint64_t b=150,std::uint64_t bi=50){
    os::WindowsTopology topology{2,{{0,1,1,1},{1,1,4,4}},{{1,7,{{0,1}}},{0,2,{{1,4}}}},{{0,0,{{0,1}}},{0,0,{{1,4}}}}};
    const auto row=[](std::uint16_t group,std::uint8_t number,std::uint64_t busy,std::uint64_t idle){
        os::WindowsProcessorRow value{group,number,{}};
        for(std::size_t i=0;i<3;++i)value.accounting[i]={0,0,0x20510500,1,static_cast<std::int64_t>(i==0?busy:i==2?idle:0),100000,42};
        return value;
    };
    return {R::success,0,topology,{row(0,0,a,ai),row(1,2,b,bi)}};
}
n::ProcessorState owner(){return n::ProcessorState("epoch:1","clock:1","scope:1","windows:pdh-accounted-time-v1");}
void commit(n::ProcessorState& state,const os::WindowsProcessorCapture& raw,std::uint64_t ns){
    const auto result=raw.counters();const auto start=tick(ns);
    need(state.commit(1,state.revision(),result,start,start)==S::accepted,"source accepted");
}
c::Policy policy(){c::Policy v;v.available=true;v.revision=7;v.disclosure[{"console","inspector"}]={"operational"};v.disclosure[{"console","accessibility"}]={"operational"};return v;}
p::TelemetryBinding binding(){return {{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},{"telemetry.snapshot","telemetry.measured-time","telemetry.processor"}},"C","epoch:1","producer:network","S","inspector","operational",7,p::TelemetryDirection::producer_to_consumer,"0.2.0","clock:1","scope:1"};}
std::string encoded(const J& doc,const std::string& record){
    J body{{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","producer:network"},{"record_id",record},{"policy_revision","7"},{"clock_id","clock:1"},{"snapshot",doc}};
    return p::encode_telemetry({"snapshot","C","epoch:1",body.dump(),body},binding());
}
const J& field(const J& doc,std::string_view entity,std::string_view name){
    for(const auto& row:doc["observations"])if(row["entity_id"].get_ref<const std::string&>()==entity&&row["field"].get_ref<const std::string&>()==name)return row;
    throw std::runtime_error("missing expected field");
}
template<class F> void contract(F call){bool rejected=false;try{call();}catch(const p::Error&){rejected=true;}need(rejected,"invalid publication rejected");}
void values(){
    auto state=owner();state.demand(1);auto raw=capture();n::WindowsProcessorPublisher pub("epoch:1","clock:1","scope:1");
    commit(state,raw,100);const auto first=pub.document(state,&raw,1,utc,utc);
    need(first["entities"].size()==5&&first["observations"].size()==15&&first["relationships"].size()==2,"every CPU/group plus aggregate");
    for(const auto& row:first["observations"])need(row["value"].is_null()&&row["acquisition"]=="pending"&&row["error"]["code"]=="processor.first","first is pending");
    raw=capture(80,80,230,70);commit(state,raw,200);const auto doc=pub.document(state,&raw,2,later,later);
    need(field(doc,"processor:aggregate","windows.cpu.accounted_busy_percent")["value"]["data"]==75,"literal weighted 120/160");
    need(field(doc,"processor:aggregate","windows.cpu.interval_busy_100ns")["value"]["data"]=="120"&&field(doc,"processor:aggregate","windows.cpu.interval_total_100ns")["value"]["data"]=="160","exact aggregate integers");
    need(field(doc,"processor:domain:1","windows.cpu.interval_busy_100ns")["value"]["data"]=="40"&&field(doc,"processor:domain:2","windows.cpu.interval_total_100ns")["value"]["data"]=="100","per-group denominators");
    need(field(doc,"processor:logical:3","windows.cpu.interval_busy_100ns")["value"]["data"]=="40"&&field(doc,"processor:logical:4","windows.cpu.interval_total_100ns")["value"]["data"]=="100","per-CPU denominators");
    for(const auto& row:doc["observations"])need(row["sample_interval_ns"]=="100"&&row["measured_at"]["clock_id"]=="clock:1"&&row["measured_at"]["nanoseconds"]=="200"&&row["observed_at"]==later,"actual separate measurement metadata");
    need(doc["entities"][3]["identity"]["native_efficiency_class"]=="7"&&doc["entities"][4]["identity"]["native_core_masks"]=="1:4","reported topology metadata");
    need(first["observations"][0]["value"].is_null()&&first["generation"]=="1","retained document immutable");
    (void)encoded(doc,"values");
    const J scene{{"widgets",J::array({{{"bindings",J::array({{{"field","windows.cpu.accounted_busy_percent"}}})}}})}};
    need(n::windows_processor_requested(scene)&&!n::processor_requested(scene),"OS-specific field selection");
    need(n::windows_host_metrics().size()==7&&n::host_metrics().size()==7,"complete explicit catalogs");
}
void states(){
    auto state=owner();state.demand(1);auto raw=capture(0,100,0,100);n::WindowsProcessorPublisher pub("epoch:1","clock:1","scope:1");
    commit(state,raw,100);pub.document(state,&raw,1,utc,utc);raw=capture(0,200,0,200);commit(state,raw,200);
    auto doc=pub.document(state,&raw,2,later,later);need(field(doc,"processor:aggregate","windows.cpu.accounted_busy_percent")["value"]["data"]==0,"genuine zero");
    raw=capture(100,200,100,200);commit(state,raw,300);doc=pub.document(state,&raw,3,later,later);
    need(doc["observations"][0]["value"]["data"]==100,"full accounted busy");
    commit(state,raw,400);doc=pub.document(state,&raw,4,later,later);need(doc["observations"][0]["value"].is_null()&&doc["observations"][0]["error"]["code"]=="processor.no_progress","no progress not zero");
    raw=capture(1,1,1,1);commit(state,raw,500);doc=pub.document(state,&raw,5,later,later);need(doc["observations"][0]["error"]["code"]=="processor.counter_reset","decrease rebases");
}
void failure(){
    auto state=owner();state.demand(1);auto raw=capture();n::WindowsProcessorPublisher pub("epoch:1","clock:1","scope:1");commit(state,raw,100);pub.document(state,&raw,1,utc,utc);
    raw=capture(80,80,230,70);commit(state,raw,200);const auto prior=pub.document(state,&raw,2,utc,utc);
    const os::ProcessorResult failed{R::failed,5};const auto t300=tick(300);need(state.commit(1,0,failed,t300,t300)==S::source_failed,"source failure");
    auto doc=pub.document(state,&raw,3,utc,later);
    for(std::size_t i=0;i<doc["observations"].size();++i){for(const auto* key:{"value","observed_at","measured_at","sample_interval_ns"})need(doc["observations"][i][key]==prior["observations"][i][key],"old measurement retained");need(doc["observations"][i]["freshness"]=="stale"&&doc["observations"][i]["attempted_at"]==later,"stale attempt advances");}
    const os::ProcessorResult denied{R::denied,5};const auto t400=tick(400);state.commit(1,0,denied,t400,t400);doc=pub.document(state,&raw,4,utc,later);need(doc["observations"][0]["acquisition"]=="denied","denied distinct");
    const os::ProcessorResult unsupported{R::unsupported,50};const auto t500=tick(500);state.commit(1,0,unsupported,t500,t500);doc=pub.document(state,&raw,5,utc,later);
    for(const auto& row:doc["observations"])need(row["value"].is_null()&&row["support"]=="unsupported"&&row["freshness"]=="not_applicable","unsupported never old healthy values");
    raw=capture(180,180,330,170);commit(state,raw,600);doc=pub.document(state,&raw,6,later,later);need(doc["observations"][0]["error"]["code"]=="processor.acquisition_gap","gap rebase");
    const auto disabled=pub.document(state,&raw,7,later,later,true);need(disabled["entities"].size()==1&&disabled["relationships"].empty(),"disabled retires groups and CPUs");
    for(const auto& row:disabled["observations"])need(row["value"].is_null()&&row["acquisition"]=="disabled"&&row["measured_at"].is_null(),"disabled no raw values");
}
void lifetimes(){
    auto state=owner();state.demand(1);auto raw=capture();n::WindowsProcessorPublisher pub("epoch:1","clock:1","scope:1");commit(state,raw,100);
    contract([&]{pub.document(state,&raw,1,utc,utc,false,32);});const auto doc=pub.document(state,&raw,1,utc,utc);
    need(doc["entities"][1]["id"]=="processor:domain:1"&&doc["entities"][4]["id"]=="processor:logical:4","failed capacity allocates no identities");
    auto removed_raw=raw;removed_raw.rows.pop_back();removed_raw.topology.groups.pop_back();removed_raw.topology.cores.pop_back();removed_raw.topology.packages.pop_back();
    state.topology_changed();commit(state,removed_raw,200);const auto removed=pub.document(state,&removed_raw,2,later,later);
    state.topology_changed();commit(state,raw,300);const auto returned=pub.document(state,&raw,3,later,later);
    need(returned["entities"][2]["id"]=="processor:domain:5"&&returned["entities"][4]["id"]=="processor:logical:6","reused group and CPU addresses are fresh wire lifetimes");
    r::DataView view({true,"console",{"console"}},policy(),"inspector","operational",n::windows_processor_metrics());const auto attachment=view.attach_wire(binding(),0);
    need(attachment.code==r::DataCode::accepted,"authorized inspector/accessibility attachment");
    for(const auto& item:{std::make_pair(doc,1),std::make_pair(removed,2),std::make_pair(returned,3)})admitted(view.receive(attachment.token,7,encoded(item.first,"lifetime:"+std::to_string(item.second)),static_cast<std::uint64_t>(item.second),tick(300)),"actual retirement/import");
    const auto disabled=pub.document(state,&raw,4,later,later,true);const auto regrant=pub.document(state,&raw,5,later,later);
    need(regrant["entities"][1]["id"]=="processor:domain:7"&&regrant["entities"][3]["id"]=="processor:logical:9","disable/regrant never revives old IDs");
    need(view.receive(attachment.token,7,encoded(disabled,"disabled"),4,tick(300)).code==r::DataCode::accepted&&view.receive(attachment.token,7,encoded(regrant,"regrant"),5,tick(300)).code==r::DataCode::accepted,"disabled/regrant typed import");
}
void boundary(){
    auto state=owner();state.demand(1);auto raw=capture();n::WindowsProcessorPublisher pub("epoch:1","clock:1","scope:1");commit(state,raw,100);
    auto undisclosed=policy();undisclosed.disclosure.erase({"console","accessibility"});r::DataView blocked({true,"console",{"console"}},undisclosed,"inspector","operational",n::windows_processor_metrics());need(blocked.attach_wire(binding(),0).code==r::DataCode::denied,"accessibility disclosure is required, not inferred from inspector");
    r::DataView view({true,"console",{"console"}},policy(),"inspector","operational",n::windows_processor_metrics());const auto attachment=view.attach_wire(binding(),0);need(attachment.code==r::DataCode::accepted,"authorized model attachment");
    auto bytes=encoded(pub.document(state,&raw,1,utc,utc),"first");admitted(view.receive(attachment.token,7,bytes,1,tick(100)),"pending actual measured import");
    raw=capture(80,80,230,70);commit(state,raw,200);bytes=encoded(pub.document(state,&raw,2,later,later),"second");
    need(view.receive(attachment.token,7,bytes,2,tick(200)).code==r::DataCode::accepted&&view.receive(attachment.token,7,bytes,3,tick(201)).code==r::DataCode::duplicate,"measured import/replay");
    auto denied=policy();denied.available=false;denied.revision=8;view.policy(denied,4);need(!view.status(4).payload_available&&!view.project(4,[](const auto&,const auto&){}),"current-policy erasure");
}
void merge(){
    auto state=owner();state.demand(1);auto raw=capture();n::WindowsProcessorPublisher pub("epoch:1","clock:1","scope:1");commit(state,raw,100);pub.document(state,&raw,1,utc,utc);raw=capture(80,80,230,70);commit(state,raw,200);
    n::NetworkState network("epoch:1","clock:1","scope:1");network.demand(1);const os::NetworkResult net{os::NetworkCode::success,0,{{9,9,6,os::NetworkCounters{100,200}}}};const auto at=tick(90);
    need(network.commit(1,0,net,at,at)==n::NetworkStateCode::accepted,"network fixture");const auto network_doc=n::network_document(*network.sample(),1,utc,utc,true);
    const auto doc=n::host_document(network_doc,pub.document(state,&raw,2,later,later),2,"epoch:1",later);
    need(doc["entities"].size()==6&&doc["sources"].size()==2&&doc["observations"].size()==19,"complete independent sources");
    const auto& row=field(doc,"network:interface:1","network.receive_bytes");need(row["measured_at"]["nanoseconds"]=="90"&&row["attempted_at"]==utc,"CPU cannot rewrite network measurement");
    (void)encoded(doc,"merge");
}
void demand(){
    n::DemandSource source{"processor","collection.processor",1000,2500,"sampling.resources_ms",{}};
    n::DemandRequest request;request.channel="inspector";
    for(const auto& metric:n::windows_processor_metrics()){source.fields.push_back({metric.field,"operational"});request.selections.push_back({metric.field,{}});}
    n::DemandOwner scheduler({source},policy());const auto lease=scheduler.admit(request,{true,"console",{"console"}},0);need(lease.code==n::DemandCode::accepted,"Windows fields admitted");
    const auto first=scheduler.take(0);need(first.has_value(),"first job");scheduler.complete(first->ticket,0);scheduler.renew(lease.lease,1,1000);const auto next=scheduler.take(1000);
    need(next&&next->ticket!=first->ticket&&next->plan_revision==first->plan_revision,"continuous admitted plan across jobs");
    auto denied=policy();denied.denied_capabilities.insert("collection.processor");n::DemandOwner blocked({source},denied);
    need(blocked.admit(request,{true,"console",{"console"}},0).code==n::DemandCode::denied&&!blocked.take(0),"field names never grant denied collection");
}
void contracts(){
    auto state=owner();state.demand(1);auto raw=capture();commit(state,raw,100);n::WindowsProcessorPublisher pub("epoch:1","clock:1","scope:1");
    contract([&]{pub.document(state,nullptr,1,utc,utc);});auto changed=raw;changed.rows[0].accounting[0].first++;
    contract([&]{pub.document(state,&changed,1,utc,utc);});changed=raw;changed.topology.cores.clear();contract([&]{pub.document(state,&changed,1,utc,utc);});
    n::ProcessorState wrong("epoch:1","clock:1","scope:1","linux:execution-ticks-v1");wrong.demand(1);commit(wrong,raw,100);contract([&]{pub.document(wrong,&raw,1,utc,utc);});
    const auto doc=pub.document(state,&raw,1,utc,utc);need(doc["entities"][1]["id"]=="processor:domain:1","contract rejection rolls back ownership");
    auto empty_state=owner();n::WindowsProcessorPublisher waiting("epoch:1","clock:1","scope:1");const auto pending=waiting.document(empty_state,nullptr,1,utc,utc);
    need(pending["entities"].size()==1&&pending["observations"][0]["value"].is_null(),"before first sample no invented inventory");
    auto many=raw;many.topology={1,{{0,12,12,4095}},{{1,0,{{0,4095}}}},{{0,0,{{0,4095}}}}};many.rows.clear();
    for(unsigned number=0;number<12;++number){auto row=raw.rows[0];row.number=static_cast<std::uint8_t>(number);many.rows.push_back(row);}
    auto complete=owner();complete.demand(1);commit(complete,many,100);n::WindowsProcessorPublisher ordered("epoch:1","clock:1","scope:1");const auto numerical=ordered.document(complete,&many,1,utc,utc);
    need(numerical["entities"][4]["identity"]["native_processor_number"]=="2"&&numerical["entities"][4]["id"]=="processor:logical:4","numeric native order: CPU 2 precedes CPU 10");
}
int main(int argc,char** argv){try{
    need(argc==2,"case required");const std::string name=argv[1];
    if(name=="VALUES")values();else if(name=="STATES")states();else if(name=="FAILURE")failure();else if(name=="LIFETIMES")lifetimes();else if(name=="BOUNDARY")boundary();else if(name=="MERGE")merge();else if(name=="DEMAND")demand();else if(name=="CONTRACTS")contracts();else throw std::runtime_error("unknown case");
    std::cout<<name<<": pass\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
