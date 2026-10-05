#pragma once
#include "wire.hpp"
#include <functional>
#include <vector>

namespace syspane::diagnostics {
inline constexpr const char* failure_header = "SYSPANE-FAILURES 0.1\n";
struct FailureHistory {
    std::string status = "unavailable";
    std::vector<protocol::Json> records;
};
using FailureReader = std::function<FailureHistory()>;
// Advisory, untrusted metadata. It cannot grant process-control or policy authority.
FailureHistory decode_failures(std::string_view bytes);
std::string failure_line(std::uint64_t sequence, std::uint64_t elapsed_ms,
                         const std::string& role, const std::string& reason, bool stopped);
protocol::Json failure_projection(const FailureHistory& history);
}
