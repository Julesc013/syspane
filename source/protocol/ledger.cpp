#include "ledger.hpp"
#include "wire.hpp"
#include <set>

namespace syspane::protocol {
namespace {
constexpr std::size_t result_bytes = 4096, body_bytes = 16384, total_bytes = 16 * 1024 * 1024;
}
void Ledger::advance(std::uint64_t now) {
    if (last_ && now < *last_) throw Error("clock.regressed");
    last_ = now;
    for (auto it = records_.begin(); it != records_.end();) {
        if (it->second.finished_ms && now - *it->second.finished_ms >= 600000) {
            bytes_ -= it->second.body.size() + result_bytes;
            it = records_.erase(it);
        } else ++it;
    }
}
Admission Ledger::admit(const std::string& principal, const std::string& connection,
                         const std::string& request, std::string body, std::uint64_t now) {
    advance(now);
    if (!identifier(principal) || !identifier(connection) || !identifier(request) || body.empty() || body.size() > body_bytes)
        throw Error("request.invalid");
    const auto key = std::make_pair(principal, request);
    if (const auto it = records_.find(key); it != records_.end()) {
        if (it->second.body != body) return Admission::conflict;
        return it->second.finished_ms ? Admission::replay : Admission::pending;
    }
    std::size_t principal_count = 0, active = 0;
    std::set<std::string> principals;
    for (const auto& item : records_) {
        principals.insert(item.first.first);
        if (item.first.first == principal) ++principal_count;
        if (item.second.connection == connection && !item.second.finished_ms) ++active;
    }
    if (principal_count >= 128 || active >= 128 || records_.size() >= 1024 ||
        (principals.size() >= 16 && !principals.count(principal)) ||
        body.size() + result_bytes > total_bytes - bytes_) return Admission::busy;
    const auto reservation = body.size() + result_bytes;
    records_.emplace(key, Record{connection, std::move(body), {}, {}, false});
    bytes_ += reservation;
    return Admission::admitted;
}
void Ledger::finish(const std::string& principal, const std::string& request,
                    std::string result, bool committed, std::uint64_t now) {
    advance(now);
    const auto it = records_.find({principal, request});
    if (it == records_.end() || it->second.finished_ms) throw Error("request.state");
    if (result.empty() || result.size() > result_bytes) throw Error("result.size");
    it->second.result = std::move(result);
    it->second.committed = committed;
    it->second.finished_ms = now;
}
std::optional<Record> Ledger::get(const std::string& principal, const std::string& request, std::uint64_t now) {
    advance(now);
    const auto it = records_.find({principal, request});
    if (it == records_.end()) return {};
    return it->second;
}
std::optional<Record> Ledger::cancel(const std::string& principal, const std::string& request,
                                     std::string cancelled_result, std::uint64_t now) {
    auto record = get(principal, request, now);
    if (record && !record->finished_ms) {
        finish(principal, request, std::move(cancelled_result), false, now);
        record = get(principal, request, now);
    }
    return record;
}
} // namespace syspane::protocol
