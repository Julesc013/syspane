#pragma once
#include <atomic>
#include <chrono>
#include <cstdint>
#include <optional>
#include <vector>

namespace syspane::platform {
enum class NetworkCode { success, cancelled, timed_out, capacity, denied, unsupported, interrupted, malformed, failed };
struct NetworkCounters { std::uint64_t receive, transmit; };
// Source-native keys/type numbers are raw acquisition facts, never model IDs.
struct NetworkRow {
    std::uint64_t native_key;
    std::uint32_t index, native_type;
    std::optional<NetworkCounters> counters;
};
struct NetworkResult {
    NetworkCode code;
    std::int64_t native_error = 0;
    std::vector<NetworkRow> rows = {};
};
struct NetworkRequest {
    std::chrono::steady_clock::time_point deadline;
    const std::atomic_bool& cancelled;
    std::size_t row_limit = 8192;
};
inline std::optional<NetworkCode> network_stopped(const NetworkRequest& request) {
    if (request.cancelled.load()) return NetworkCode::cancelled;
    if (std::chrono::steady_clock::now() >= request.deadline) return NetworkCode::timed_out;
    if (request.row_limit > 8192) return NetworkCode::capacity;
    return {};
}
NetworkResult read_network(const NetworkRequest& request);
const char* network_code_name(NetworkCode code);
} // namespace syspane::platform
