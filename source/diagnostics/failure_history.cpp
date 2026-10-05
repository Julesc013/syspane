#include "failure_history.hpp"
#include <set>

namespace syspane::diagnostics {
namespace {
std::uint64_t number(const protocol::Json& value) {
    const auto parsed = value.is_string() ? protocol::decimal(value.get_ref<const std::string&>()) : std::nullopt;
    if (!parsed) throw protocol::Error("failure.number");
    return *parsed;
}
void validate(const protocol::Json& value, std::uint64_t expected, std::uint64_t previous) {
    const std::set<std::string> roles{"collector", "desktop"};
    const std::set<std::string> reasons{"launch_failed", "crashed", "producer_expired", "render_stalled", "operation_timeout", "protocol_rejected"};
    if (!protocol::members(value, {"sequence", "elapsed_ms", "role", "reason", "stop_confirmed"}) ||
        !value["role"].is_string() || !roles.count(value["role"].get<std::string>()) ||
        !value["reason"].is_string() || !reasons.count(value["reason"].get<std::string>()) ||
        !value["stop_confirmed"].is_boolean() || number(value["sequence"]) != expected ||
        expected == 0 || expected > 16 || number(value["elapsed_ms"]) < previous)
        throw protocol::Error("failure.record");
}
}
FailureHistory decode_failures(std::string_view bytes) {
    const std::string_view header(failure_header);
    if (bytes.size() > 8192) return {"invalid", {}};
    if (bytes.size() < header.size())
        return {header.substr(0, bytes.size()) == bytes ? "incomplete" : "invalid", {}};
    if (bytes.substr(0, header.size()) != header) return {"invalid", {}};
    FailureHistory result{"empty", {}};
    bytes.remove_prefix(header.size());
    std::uint64_t previous = 0;
    try {
        while (!bytes.empty()) {
            const auto end = bytes.find('\n');
            if (result.records.size() >= 16 || (end == std::string_view::npos ? bytes.size() >= 512 : end >= 512))
                return {"invalid", {}};
            if (end == std::string_view::npos) { result.status = "incomplete"; return result; }
            auto value = protocol::parse(bytes.substr(0, end));
            validate(value, result.records.size()+1, previous);
            previous = number(value["elapsed_ms"]);
            result.records.push_back(std::move(value));
            bytes.remove_prefix(end+1);
        }
    } catch (const std::exception&) { return {"invalid", {}}; }
    result.status = result.records.empty() ? "empty" : "complete";
    return result;
}
std::string failure_line(std::uint64_t sequence, std::uint64_t elapsed_ms,
                         const std::string& role, const std::string& reason, bool stopped) {
    protocol::Json value{{"sequence", std::to_string(sequence)}, {"elapsed_ms", std::to_string(elapsed_ms)},
        {"role", role}, {"reason", reason}, {"stop_confirmed", stopped}};
    validate(value, sequence, 0);
    const auto line = value.dump() + '\n';
    if (line.size() > 512) throw protocol::Error("failure.line");
    return line;
}
protocol::Json failure_projection(const FailureHistory& history) {
    const std::set<std::string> statuses{"absent", "unavailable", "empty", "complete", "incomplete", "invalid", "restricted"};
    if (!statuses.count(history.status) || history.records.size() > 16) throw protocol::Error("failure.projection");
    if ((history.status != "complete" && history.status != "incomplete") && !history.records.empty())
        throw protocol::Error("failure.projection");
    std::uint64_t previous = 0, sequence = 0;
    for (const auto& row : history.records) {
        validate(row, ++sequence, previous); previous = number(row["elapsed_ms"]);
    }
    return {{"status", history.status}, {"trust", "unverified_local_metadata"},
            {"live_health", false}, {"records", history.records}};
}
}
