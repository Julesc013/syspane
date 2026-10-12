#if defined(_WIN64)
#include "processor_windows.hpp"
#include "processor_state.hpp"
#include "wire.hpp"
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
int main(){try{
    std::atomic_bool cancelled{true};os::ProcessorRequest request{std::chrono::steady_clock::now()+std::chrono::seconds(5),cancelled};
    if(os::read_windows_processors(request).code!=os::ProcessorReadCode::cancelled)throw std::runtime_error("actual cancellation");
    cancelled=false;request.deadline=std::chrono::steady_clock::now()-std::chrono::seconds(1);
    if(os::read_windows_processors(request).code!=os::ProcessorReadCode::timed_out)throw std::runtime_error("actual timeout");
    request.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(5);const auto first_start=now();auto first=os::read_windows_processors(request);const auto first_end=now();
    std::this_thread::sleep_for(std::chrono::seconds(1));request.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(5);const auto second_start=now();auto second=os::read_windows_processors(request);const auto second_end=now();
    J result{{"definition","windows:pdh-accounted-time-v1"},{"cancelled",true},{"timed_out",true},{"first",capture(first,first_start,first_end)},{"second",capture(second,second_start,second_end)}};
    if(first.code!=os::ProcessorReadCode::success||second.code!=os::ProcessorReadCode::success){std::cout<<result.dump()<<'\n';return 3;}
    r::ProcessorState state("probe:windows","clock:steady","host:current","windows:pdh-accounted-time-v1");state.demand(1);
    if(state.commit(1,0,first.counters(),tick(first_start),tick(first_end))!=r::ProcessorStateCode::accepted)throw std::runtime_error("first commit");
    if(!(first.topology==second.topology))state.topology_changed();
    const auto committed=state.commit(1,state.revision(),second.counters(),tick(second_start),tick(second_end));result["commit"]=static_cast<int>(committed);
    const auto sample=state.sample();result["pending"]=static_cast<int>(sample->pending);result["ratios"]=J::array();result["domains"]=J::object();result["aggregate"]=nullptr;
    for(const auto& row:sample->processors)result["ratios"].push_back({{"id",row.counters.id},{"domain",row.counters.domain},{"ratio",row.utilization?ratio(*row.utilization):J(nullptr)}});
    for(const auto& domain:sample->domains)result["domains"][domain.first]=ratio(domain.second);
    if(sample->aggregate)result["aggregate"]=ratio(*sample->aggregate);
    std::cout<<result.dump()<<'\n';return committed==r::ProcessorStateCode::accepted&&sample->aggregate?0:4;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
#endif
