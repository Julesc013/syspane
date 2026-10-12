#pragma once
#include <atomic>
#include <chrono>
#include <cstdint>
#include <string>
#include <vector>

namespace syspane::platform {
enum class ProcessorReadCode {success,cancelled,timed_out,denied,unsupported,malformed,failed,capacity,interrupted};
struct ProcessorCounters {
    std::string id,domain;
    std::uint64_t total,idle;
    // Fixed category order for this source definition; empty remains valid.
    std::vector<std::uint64_t> accounting={};
};
struct ProcessorResult {ProcessorReadCode code;std::int64_t native_error=0;std::vector<ProcessorCounters> rows={};};
struct ProcessorRequest {
    std::chrono::steady_clock::time_point deadline;
    const std::atomic_bool& cancelled;
    std::size_t row_limit=8192;
};
inline ProcessorReadCode processor_stopped(const ProcessorRequest& request){
    if(request.cancelled.load())return ProcessorReadCode::cancelled;
    if(std::chrono::steady_clock::now()>=request.deadline)return ProcessorReadCode::timed_out;
    if(!request.row_limit||request.row_limit>8192)return ProcessorReadCode::capacity;
    return ProcessorReadCode::success;
}
}
