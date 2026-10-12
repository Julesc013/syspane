#pragma once
#include "processor_state.hpp"
#include "processor_linux.hpp"
#include "telemetry.hpp"

namespace syspane::runtime {
std::vector<model::Metric> processor_metrics();
std::vector<model::Metric> host_metrics();
bool processor_requested(const protocol::Json& validated_scene);
// Serialized publication identity bookkeeping; no demand scheduler or worker.
class LinuxProcessorPublisher {
public:
    LinuxProcessorPublisher(std::string epoch,std::string clock,std::string scope);
    protocol::Json document(const ProcessorState&,const platform::LinuxProcessorCapture*,
        std::uint64_t publication,const std::string& sampled_utc,const std::string& attempted_utc,
        bool disabled=false,std::size_t limit=protocol::frame_limit-8192);
private:
    std::string epoch_,clock_,scope_;
    std::map<std::string,std::uint64_t> live_;
    std::uint64_t issued_=0,last_sample_=0,hz_=0;
};
protocol::Json host_document(const std::optional<protocol::Json>& network,
    const std::optional<protocol::Json>& processor,std::uint64_t generation,
    const std::string& epoch,const std::string& attempted_utc,
    std::size_t limit=protocol::frame_limit-8192);
}
