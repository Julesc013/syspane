#pragma once
#include "local_ipc.hpp"
#include "wire.hpp"
#include <vector>

namespace syspane::recovery {
enum class HealthKind { ready, heartbeat, challenge, progress, shutdown };
struct HealthEvent { HealthKind kind; std::uint64_t value, observed_ms; };
// Serialized owner; the authenticated stream must outlive this link. No commands,
// snapshot/delta, launch instructions or disclosure authority are exposed here.
class HealthLink {
public:
    HealthLink(platform::Stream& stream, bool server, std::string role, std::string epoch, std::string connection);
    HealthLink(const HealthLink&) = delete;
    HealthLink& operator=(const HealthLink&) = delete;
    std::vector<HealthEvent> poll();
    void heartbeat(std::uint64_t sequence);
    void challenge(std::uint64_t generation);
    void progress(std::uint64_t generation);
    void shutdown();
    bool ready() const { return ready_; }
    const std::string& connection() const { return connection_; }
    const std::string& epoch() const { return epoch_; }
private:
    void send(const std::string& type, protocol::Json body);
    protocol::Json greeting(const std::string& role) const;
    platform::Stream& stream_;
    bool server_, progress_, ready_ = false, closed_ = false;
    std::string role_, epoch_, connection_;
    std::size_t limit_ = 4096;
    protocol::Framer decoder_{4096};
    std::optional<std::uint64_t> pending_, completed_;
};
} // namespace syspane::recovery
