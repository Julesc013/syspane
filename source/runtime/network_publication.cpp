#include "network_publication.hpp"
#include <cmath>
#include <set>

namespace syspane::runtime {
namespace p=protocol;
std::vector<model::Metric> network_metrics() {
    return {{"network.receive_bytes","byte",model::ValueKind::uint64},
        {"network.transmit_bytes","byte",model::ValueKind::uint64},
        {"network.receive_bytes_per_second","byte/second",model::ValueKind::number},
        {"network.transmit_bytes_per_second","byte/second",model::ValueKind::number}};
}
p::Json network_document(const NetworkSample& sample,std::uint64_t generation,
    const std::string& sampled_utc,const std::string& attempted_utc,bool current,std::size_t limit) {
    const auto need=[](bool ok){if(!ok)throw p::Error("network.publication_contract");};
    need(generation && sample.generation && p::identifier(sample.measured_at.epoch) && p::identifier(sample.measured_at.clock_id) &&
        p::identifier(sample.measured_at.clock_scope) && sample.values.size()<=8192 && sampled_utc.size()>=20 && sampled_utc.size()<=64 &&
        attempted_utc.size()>=20 && attempted_utc.size()<=64 && limit<=p::frame_limit-8192);
    p::Json result{{"schema_version","0.2.0"},{"producer_epoch",sample.measured_at.epoch},{"generation",std::to_string(generation)},
        {"captured_at",attempted_utc},{"entities",p::Json::array()},{"relationships",p::Json::array()},
        {"sources",p::Json::array({{{"id","provider:native-network"},{"kind","native.network.counters"},{"scope","host:local"}}})},
        {"observations",p::Json::array()},{"completeness","complete"}};
    std::size_t bytes=result.dump().size();
    const auto append=[&](const char* collection,p::Json value){
        const auto size=value.dump().size()+1; // Includes a conservative first-element comma reservation.
        if(bytes>limit || size>limit-bytes)throw p::Error("network.publication_capacity");
        bytes+=size;result[collection].push_back(std::move(value));
    };
    std::set<std::uint64_t> lifetimes;std::uint64_t previous=0;
    const auto metrics=network_metrics();
    for(const auto& item:sample.values) {
        need(item.native.native_key>previous && item.native.index && item.lifetime && item.lifetime<=8192 && lifetimes.insert(item.lifetime).second);
        previous=item.native.native_key;
        const auto entity="network:interface:"+std::to_string(item.lifetime);
        append("entities",{{"id",entity},{"kind","network.interface"},{"display_name","Network interface "+std::to_string(item.lifetime)},
            {"identity",{{"native_index",std::to_string(item.native.index)},{"native_type",std::to_string(item.native.native_type)}}},
            {"generation",std::to_string(generation)}});
        for(unsigned i=0;i<4;++i) {
            const bool rate=i>=2,available=rate?item.delta.has_value():item.native.counters.has_value();
            p::Json value=nullptr,interval=nullptr;
            if(available) {
                if(rate) {
                    need(item.native.counters.has_value() && item.delta->interval_ns>0);
                    const auto delta=i==2?item.delta->receive:item.delta->transmit;
                    const auto number=static_cast<double>(delta)/static_cast<double>(item.delta->interval_ns)*1e9;
                    need(std::isfinite(number) && number>=0);
                    value={{"kind","number"},{"data",number}};interval=std::to_string(item.delta->interval_ns);
                } else value={{"kind","uint64"},{"data",std::to_string(i==0?item.native.counters->receive:item.native.counters->transmit)}};
            }
            append("observations",{{"schema_version","0.2.0"},{"entity_id",entity},{"field",metrics[i].field},{"value",value},
                {"unit",metrics[i].unit},{"origin",rate?"derived":"observed"},{"support",item.native.counters?"supported":"unknown"},
                {"acquisition",current?(available?"success":"pending"):"failed"},{"freshness",available?(current?"current":"stale"):"unknown"},
                {"presence","present"},{"source_id","provider:native-network"},{"observed_at",available?p::Json(sampled_utc):p::Json(nullptr)},
                {"attempted_at",attempted_utc},{"producer_epoch",sample.measured_at.epoch},{"generation",std::to_string(generation)},
                {"sample_interval_ns",interval},{"error",current?p::Json(nullptr):p::Json{{"code","network.acquisition_failed"},{"message","Network acquisition failed"},{"retryable",true}}},
                {"measured_at",available?p::Json{{"clock_id",sample.measured_at.clock_id},{"nanoseconds",std::to_string(sample.measured_at.nanoseconds)}}:p::Json(nullptr)}});
        }
    }
    if(bytes>limit)throw p::Error("network.publication_capacity");
    return result;
}
}
