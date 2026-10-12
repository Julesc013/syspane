#include "processor_publication.hpp"
#include "network_publication.hpp"
#include <algorithm>
#include <limits>
#include <set>

namespace syspane::runtime {
namespace p=protocol;
namespace {
void need(bool ok){if(!ok)throw p::Error("processor.publication_contract");}
p::Json empty(const std::string& epoch,std::uint64_t generation,const std::string& utc){
    need(generation&&p::identifier(epoch)&&utc.size()>=20&&utc.size()<=64);
    return {{"schema_version","0.2.0"},{"producer_epoch",epoch},{"generation",std::to_string(generation)},{"captured_at",utc},
        {"entities",p::Json::array()},{"relationships",p::Json::array()},{"sources",p::Json::array()},{"observations",p::Json::array()},{"completeness","complete"}};
}
const char* reason(ProcessorPending code){switch(code){case ProcessorPending::none:return "none";case ProcessorPending::first:return "first";case ProcessorPending::demand_changed:return "demand_changed";case ProcessorPending::topology_changed:return "topology_changed";case ProcessorPending::counter_reset:return "counter_reset";case ProcessorPending::interval_zero:return "interval_zero";case ProcessorPending::no_progress:return "no_progress";case ProcessorPending::acquisition_gap:return "acquisition_gap";}throw p::Error("processor.pending");}
const char* failure(ProcessorReadCode code){switch(code){case ProcessorReadCode::success:return "awaiting_sample";case ProcessorReadCode::cancelled:return "cancelled";case ProcessorReadCode::timed_out:return "timed_out";case ProcessorReadCode::denied:return "denied";case ProcessorReadCode::unsupported:return "unsupported";case ProcessorReadCode::malformed:return "malformed";case ProcessorReadCode::failed:return "failed";case ProcessorReadCode::capacity:return "capacity";case ProcessorReadCode::interrupted:return "interrupted";}throw p::Error("processor.acquisition");}
void bounded(const p::Json& value,std::size_t limit){if(limit>p::frame_limit-8192)throw p::Error("processor.publication_contract");if(value.dump().size()>limit||value.at("entities").size()>8192||value.at("observations").size()>65536||value.at("relationships").size()>16384||value.at("sources").size()>1024)throw p::Error("processor.publication_capacity");}
void append(p::Json& doc,const char* key,p::Json row,std::size_t& bytes,std::size_t limit){
    need(limit<=p::frame_limit-8192);
    const auto size=row.dump().size()+1;
    const auto count_limit=std::string(key)=="entities"?8192:std::string(key)=="observations"?65536:std::string(key)=="relationships"?16384:1024;
    if(bytes>limit||size>limit-bytes||doc[key].size()>=static_cast<std::size_t>(count_limit))throw p::Error("processor.publication_capacity");
    bytes+=size;doc[key].push_back(std::move(row));
}
}
std::vector<model::Metric> processor_metrics(){return {{"linux.cpu.execution_percent","percent",model::ValueKind::number},{"linux.cpu.interval_busy_ticks","USER_HZ tick",model::ValueKind::uint64},{"linux.cpu.interval_total_ticks","USER_HZ tick",model::ValueKind::uint64}};}
std::vector<model::Metric> host_metrics(){auto result=network_metrics();const auto cpu=processor_metrics();result.insert(result.end(),cpu.begin(),cpu.end());return result;}
bool processor_requested(const p::Json& scene){
    if(!scene.is_object()||!scene.contains("widgets")||!scene["widgets"].is_array())return false;
    for(const auto& widget:scene["widgets"])if(widget.contains("bindings")&&widget["bindings"].is_array())for(const auto& binding:widget["bindings"]){
        if(!binding.contains("field")||!binding["field"].is_string())continue;
        for(const auto& metric:processor_metrics())if(binding["field"]==metric.field)return true;
    }return false;
}
LinuxProcessorPublisher::LinuxProcessorPublisher(std::string epoch,std::string clock,std::string scope):epoch_(std::move(epoch)),clock_(std::move(clock)),scope_(std::move(scope)){need(p::identifier(epoch_)&&p::identifier(clock_)&&p::identifier(scope_));}
p::Json LinuxProcessorPublisher::document(const ProcessorState& state,const platform::LinuxProcessorCapture* topology,std::uint64_t publication,const std::string& sampled,const std::string& attempted,bool disabled,std::size_t limit){
    auto doc=empty(epoch_,publication,attempted);std::size_t bytes=doc.dump().size();const auto sample=state.sample();const auto status=state.status();
    std::map<std::string,const platform::LinuxProcessorRow*> native;
    auto live=live_;auto issued=issued_;const bool supported=sample&&!disabled&&status.acquisition!=ProcessorReadCode::unsupported;
    if(sample){
        need(sample->generation>=last_sample_&&sample->counter_definition=="linux:execution-ticks-v1"&&sample->measured_at.epoch==epoch_&&sample->measured_at.clock_id==clock_&&sample->measured_at.clock_scope==scope_);
        need(topology&&topology->code==ProcessorReadCode::success&&topology->ticks_per_second&&topology->rows.size()==sample->processors.size());
        need(!hz_||topology->ticks_per_second==hz_);
        for(const auto& row:topology->rows)need(native.emplace("linux:cpu:"+std::to_string(row.index),&row).second);
        const auto raw=topology->counters();need(raw.code==ProcessorReadCode::success);
        std::map<std::string,const platform::ProcessorCounters*> counters;for(const auto& row:raw.rows)counters.emplace(row.id,&row);
        for(const auto& row:sample->processors){const auto found=counters.find(row.counters.id);need(found!=counters.end()&&row.counters.domain=="linux:online"&&row.counters.total==found->second->total&&row.counters.idle==found->second->idle&&row.counters.accounting==found->second->accounting);}
        if(!disabled&&sample->generation!=last_sample_){
            std::set<std::string> present;for(const auto& row:sample->processors)present.insert(row.counters.id);
            for(auto it=live.begin();it!=live.end();)if(!present.count(it->first))it=live.erase(it);else ++it;
            for(const auto& row:sample->processors)if(!live.count(row.counters.id)){if(issued>=8190)throw p::Error("processor.publication_capacity");live.emplace(row.counters.id,++issued);}
        }
    }
    append(doc,"sources",{{"id","provider:linux-processor"},{"kind","native.linux.processor"},{"scope","kernel:visible-online-cpus"}},bytes,limit);
    const auto metrics=processor_metrics();
    const auto emit=[&](const std::string& id,const std::string& kind,const std::string& name,p::Json identity,const std::optional<ProcessorUsage>& ratio){
        identity["counter_definition"]="linux:execution-ticks-v1";
        if(topology&&!disabled)identity["ticks_per_second"]=std::to_string(topology->ticks_per_second);
        append(doc,"entities",{{"id",id},{"kind",kind},{"display_name",name},{"identity",identity},{"generation",std::to_string(publication)}},bytes,limit);
        for(unsigned i=0;i<3;++i){
            const bool available=ratio.has_value()&&supported;
            p::Json value=nullptr,error=nullptr;
            const bool current=state.current()&&!disabled;
            const std::string acquisition=disabled?"disabled":status.acquisition==ProcessorReadCode::denied?"denied":current?(available?"success":"pending"):sample?"failed":status.code==ProcessorStateCode::closed?"pending":"failed";
            if(available){need(ratio->total&&ratio->busy<=ratio->total&&ratio->interval_ns);value=i==0?p::Json{{"kind","number"},{"data",ratio->percent()}}:p::Json{{"kind","uint64"},{"data",std::to_string(i==1?ratio->busy:ratio->total)}};}
            if(acquisition!="success"){
                const auto why=disabled?std::string("policy_disabled"):current&&sample?std::string(reason(sample->pending)):status.code==ProcessorStateCode::invalid?std::string("invalid_sample"):status.code==ProcessorStateCode::capacity?std::string("capacity"):status.code==ProcessorStateCode::clock_fault?std::string("clock_fault"):std::string(failure(status.acquisition));
                error={{"code","processor."+why},{"message","Linux processor "+why+"; native error "+std::to_string(status.native_error)},{"retryable",!disabled}};
            }
            append(doc,"observations",{{"schema_version","0.2.0"},{"entity_id",id},{"field",metrics[i].field},{"value",value},{"unit",metrics[i].unit},{"origin","derived"},
                {"support",disabled?"unknown":status.acquisition==ProcessorReadCode::unsupported?"unsupported":sample?"supported":"unknown"},{"acquisition",acquisition},
                {"freshness",status.acquisition==ProcessorReadCode::unsupported&&!disabled?"not_applicable":available?(current?"current":"stale"):"unknown"},
                {"presence",sample&&!disabled?"present":"unknown"},{"source_id","provider:linux-processor"},{"observed_at",available?p::Json(sampled):p::Json(nullptr)},
                {"attempted_at",attempted},{"producer_epoch",epoch_},{"generation",std::to_string(publication)},
                {"sample_interval_ns",available?p::Json(std::to_string(ratio->interval_ns)):p::Json(nullptr)},{"error",error},
                {"measured_at",available?p::Json{{"clock_id",clock_},{"nanoseconds",std::to_string(sample->measured_at.nanoseconds)}}:p::Json(nullptr)}},bytes,limit);
        }
    };
    const auto count=sample&&!disabled?sample->processors.size():0;
    const auto aggregate=sample&&!disabled?sample->aggregate:std::optional<ProcessorUsage>{};
    emit("processor:aggregate","processor.aggregate","Linux online CPU execution",{{"kernel_cpu_count",std::to_string(count)}},aggregate);
    emit("processor:domain:linux-online","processor.domain","Linux online scheduling domain",{{"kernel_cpu_count",std::to_string(count)}},aggregate);
    if(sample&&!disabled)for(const auto& value:sample->processors){
        const auto found=native.find(value.counters.id);need(found!=native.end());const auto& row=*found->second;
        std::string peers;for(auto peer:row.peers){if(!peers.empty())peers+=',';peers+=std::to_string(peer);}if(peers.size()>2048)throw p::Error("processor.publication_capacity");
        const auto id="processor:logical:"+std::to_string(live.at(value.counters.id));
        emit(id,"processor.logical","Linux logical CPU "+std::to_string(row.index),{{"kernel_cpu_index",std::to_string(row.index)},{"kernel_package_id",std::to_string(row.package)},{"kernel_core_id",std::to_string(row.core)},{"kernel_core_peers",peers}},value.utilization);
        append(doc,"relationships",{{"source",id},{"target","processor:domain:linux-online"},{"kind","member_of"}},bytes,limit);
    }
    bounded(doc,limit);if(disabled){live.clear();last_sample_=0;}else if(sample){last_sample_=sample->generation;hz_=topology->ticks_per_second;}
    live_=std::move(live);issued_=issued;return doc;
}
p::Json host_document(const std::optional<p::Json>& network,const std::optional<p::Json>& processor,std::uint64_t generation,const std::string& epoch,const std::string& utc,std::size_t limit){
    auto doc=empty(epoch,generation,utc);std::size_t bytes=doc.dump().size();need(network||processor);
    for(const auto* source:{&network,&processor})if(*source){need(source->value().at("producer_epoch")==epoch&&source->value().at("schema_version")=="0.2.0");for(const char* key:{"entities","relationships","sources","observations"})for(auto row:source->value().at(key)){
        if(std::string(key)=="entities"||std::string(key)=="observations")row["generation"]=std::to_string(generation);
        append(doc,key,std::move(row),bytes,limit);
    }}bounded(doc,limit);return doc;
}
}
