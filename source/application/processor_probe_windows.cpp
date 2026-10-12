#if defined(_WIN64)
#include "processor_windows.hpp"
#include "processor_state.hpp"
#include "wire.hpp"
#include "processor_publication.hpp"
#include "data_view.hpp"
#include <array>
#include <ctime>
#include <iostream>
#include <thread>

namespace os=syspane::platform;namespace r=syspane::runtime;using J=syspane::protocol::Json;
std::uint64_t now(){return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());}
syspane::model::Tick tick(std::uint64_t n){return {"probe:windows",n,"clock:steady","host:current"};}
J topology(const os::WindowsTopology& value){
    J out{{"maximum_groups",value.maximum_groups},{"groups",J::array()},{"cores",J::array()},{"packages",J::array()}};
    for(const auto& group:value.groups)out["groups"].push_back({{"number",group.number},{"active",group.active},{"maximum",group.maximum},{"mask",std::to_string(group.mask)}});
    const auto serialize=[](const std::vector<os::WindowsRelation>& records){J result=J::array();for(const auto& relation:records){J row{{"flags",relation.flags},{"efficiency",relation.efficiency},{"masks",J::array()}};for(const auto& mask:relation.masks)row["masks"].push_back({{"group",mask.group},{"mask",std::to_string(mask.mask)}});result.push_back(std::move(row));}return result;};
    out["cores"]=serialize(value.cores);out["packages"]=serialize(value.packages);return out;
}
J capture(const os::WindowsProcessorCapture& value,std::uint64_t start,std::uint64_t end){
    J out{{"code",static_cast<int>(value.code)},{"native_error",value.native_error},{"start",std::to_string(start)},{"end",std::to_string(end)},{"topology",topology(value.topology)},{"rows",J::array()}};
    for(const auto& row:value.rows){J item{{"group",row.group},{"number",row.number},{"accounting",J::array()}};for(const auto& part:row.accounting)item["accounting"].push_back({{"api_status",part.api_status},{"counter_status",part.counter_status},{"type",part.counter_type},{"multi",part.multi_count},{"first",std::to_string(part.first)},{"second",std::to_string(part.second)},{"timestamp",std::to_string(part.timestamp)}});out["rows"].push_back(std::move(item));}
    return out;
}
J ratio(const r::ProcessorUsage& value){return {{"busy",std::to_string(value.busy)},{"total",std::to_string(value.total)},{"interval_ns",std::to_string(value.interval_ns)},{"percent",value.percent()}};}
std::string utc(){
    const auto value=std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());const auto* calendar=std::gmtime(&value);std::array<char,32> text{};
    if(!calendar||!std::strftime(text.data(),text.size(),"%Y-%m-%dT%H:%M:%SZ",calendar))throw std::runtime_error("UTC unavailable");
    return text.data();
}
void import_publications(const J& first,const J& second,std::uint64_t second_start,J& result){
    namespace p=syspane::protocol;namespace c=syspane::configuration;namespace recovery=syspane::recovery;
    c::Policy policy;policy.available=true;policy.revision=7;policy.disclosure[{"console","inspector"}]={"operational"};policy.disclosure[{"console","accessibility"}]={"operational"};
    p::TelemetryBinding binding{{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},{"telemetry.snapshot","telemetry.measured-time","telemetry.processor"}},"C","probe:windows","producer:network","S","inspector","operational",7,p::TelemetryDirection::producer_to_consumer,"0.2.0","clock:steady","host:current"};
    recovery::DataView view({true,"console",{"console"}},policy,"inspector","operational",r::windows_processor_metrics());
    const auto attachment=view.attach_wire(binding,0);if(attachment.code!=recovery::DataCode::accepted)throw std::runtime_error("measured attachment");
    const auto envelope=[&](const J& snapshot,const std::string& id){J body{{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","producer:network"},{"record_id",id},{"policy_revision","7"},{"clock_id","clock:steady"},{"snapshot",snapshot}};return p::encode_telemetry({"snapshot","C","probe:windows",body.dump(),body},binding);};
    const auto before=envelope(first,"before"),after=envelope(second,"after");
    if(view.receive(attachment.token,7,before,1,tick(now())).code!=recovery::DataCode::accepted||view.receive(attachment.token,7,after,2,tick(now())).code!=recovery::DataCode::accepted||view.receive(attachment.token,7,after,3,tick(now())).code!=recovery::DataCode::duplicate)throw std::runtime_error("measured publication import/replay");
    bool projected=false;
    if(!view.project_measured(3,tick(now()),[&](const auto& snapshot,const auto&,const auto&){
        if(snapshot.entities.size()!=second["entities"].size()||snapshot.observations.size()!=second["observations"].size())throw std::runtime_error("complete measured projection");
        for(const auto& observation:snapshot.observations){
            const auto found=std::find_if(second["observations"].begin(),second["observations"].end(),[&](const auto& row){return row["entity_id"]==observation.entity_id&&row["field"]==observation.field;});
            if(found==second["observations"].end()||observation.unit!=(*found)["unit"]||observation.source_id!="provider:windows-processor"||observation.acquisition!=syspane::model::Acquisition::success||observation.freshness!=syspane::model::Freshness::current||!observation.measured_at||!(*observation.measured_at==tick(second_start))||!observation.sample_interval_ns||std::to_string(*observation.sample_interval_ns)!=(*found)["sample_interval_ns"])throw std::runtime_error("model measurement metadata");
            if((*found)["value"]["kind"]=="number"){if(!std::holds_alternative<double>(observation.value)||std::get<double>(observation.value)!=(*found)["value"]["data"].template get<double>())throw std::runtime_error("model percentage value");}
            else if(!std::holds_alternative<std::uint64_t>(observation.value)||std::to_string(std::get<std::uint64_t>(observation.value))!=(*found)["value"]["data"])throw std::runtime_error("model exact integer value");
        }
        projected=true;
    })||!projected)throw std::runtime_error("measured projection");
    policy.available=false;policy.revision=8;view.policy(policy,4);
    if(view.status(4).payload_available||view.project(4,[](const auto&,const auto&){}))throw std::runtime_error("current policy erasure");
    result["typed_import"]=true;result["model_replay_rejected_as_duplicate"]=true;result["model_policy_erased"]=true;
}
int main(){try{
    std::atomic_bool cancelled{true};os::ProcessorRequest request{std::chrono::steady_clock::now()+std::chrono::seconds(5),cancelled};
    if(os::read_windows_processors(request).code!=os::ProcessorReadCode::cancelled)throw std::runtime_error("actual cancellation");
    cancelled=false;request.deadline=std::chrono::steady_clock::now()-std::chrono::seconds(1);
    if(os::read_windows_processors(request).code!=os::ProcessorReadCode::timed_out)throw std::runtime_error("actual timeout");
    request.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(5);const auto first_utc=utc();const auto first_start=now();auto first=os::read_windows_processors(request);const auto first_end=now();
    std::this_thread::sleep_for(std::chrono::seconds(1));request.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(5);const auto second_utc=utc();const auto second_start=now();auto second=os::read_windows_processors(request);const auto second_end=now();
    J result{{"definition","windows:pdh-accounted-time-v1"},{"cancelled",true},{"timed_out",true},{"first",capture(first,first_start,first_end)},{"second",capture(second,second_start,second_end)}};
    if(first.code!=os::ProcessorReadCode::success||second.code!=os::ProcessorReadCode::success){std::cout<<result.dump()<<'\n';return 3;}
    r::ProcessorState state("probe:windows","clock:steady","host:current","windows:pdh-accounted-time-v1");state.demand(1);
    if(state.commit(1,0,first.counters(),tick(first_start),tick(first_end))!=r::ProcessorStateCode::accepted)throw std::runtime_error("first commit");
    r::WindowsProcessorPublisher publisher("probe:windows","clock:steady","host:current");const auto first_document=publisher.document(state,&first,1,first_utc,first_utc);
    if(!(first.topology==second.topology))state.topology_changed();
    const auto committed=state.commit(1,state.revision(),second.counters(),tick(second_start),tick(second_end));result["commit"]=static_cast<int>(committed);
    const auto sample=state.sample();result["pending"]=static_cast<int>(sample->pending);result["ratios"]=J::array();result["domains"]=J::object();result["aggregate"]=nullptr;
    for(const auto& row:sample->processors)result["ratios"].push_back({{"id",row.counters.id},{"domain",row.counters.domain},{"ratio",row.utilization?ratio(*row.utilization):J(nullptr)}});
    for(const auto& domain:sample->domains)result["domains"][domain.first]=ratio(domain.second);
    if(sample->aggregate)result["aggregate"]=ratio(*sample->aggregate);
    if(committed==r::ProcessorStateCode::accepted&&sample->aggregate){const auto second_document=publisher.document(state,&second,2,second_utc,second_utc);result["first_document"]=first_document;result["second_document"]=second_document;import_publications(first_document,second_document,second_start,result);}
    std::cout<<result.dump()<<'\n';return committed==r::ProcessorStateCode::accepted&&sample->aggregate?0:4;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
#endif
