#pragma once
#include <cstdint>
#include <map>
#include <optional>
#include <string>
#include <utility>

namespace syspane::protocol {
enum class Admission { admitted, pending, replay, conflict, busy };
struct Record {
    std::string connection, body, result;
    std::optional<std::uint64_t> finished_ms;
    bool committed = false;
};
// One instance per installation/session/server epoch; never keyed from JSON authority.
class Ledger {
public:
    Admission admit(const std::string& principal, const std::string& connection,
                    const std::string& request, std::string body, std::uint64_t now);
    void finish(const std::string& principal, const std::string& request,
                std::string result, bool committed, std::uint64_t now);
    std::optional<Record> get(const std::string& principal, const std::string& request, std::uint64_t now);
    std::optional<Record> cancel(const std::string& principal, const std::string& request,
                                 std::string cancelled_result, std::uint64_t now);
    std::size_t size() const { return records_.size(); }
    std::size_t reserved_bytes() const { return bytes_; }
private:
    void advance(std::uint64_t now);
    std::map<std::pair<std::string, std::string>, Record> records_;
    std::optional<std::uint64_t> last_;
    std::size_t bytes_ = 0;
};
} // namespace syspane::protocol
