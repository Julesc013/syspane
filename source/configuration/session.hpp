#pragma once
#include "policy.hpp"
#include "ledger.hpp"
#include "outbox.hpp"
#include "telemetry.hpp"
#include <limits>

namespace syspane::configuration {
// Local composition selects a fixed inventory source; received documents cannot.
struct InventorySource {
    std::string producer, channel, classification;
    std::uint64_t ticket_limit = std::numeric_limits<std::uint64_t>::max();
};
struct Subscription {
    protocol::TelemetryBinding binding;
    std::uint64_t ticket;
};
// Portable controller-side state machine. Native streams own I/O deadlines and
// supply authenticated context; this class cannot authenticate a process itself.
class Sessions {
public:
    Sessions(std::string epoch, std::uint64_t revision, Policy policy, std::optional<InventorySource> source = {});
    void open(const std::string& connection, std::string principal, Authority authority, std::uint64_t now);
    void receive(const std::string& connection, std::string_view payload, std::uint64_t now);
    std::optional<std::string> pop(const std::string& connection, std::uint64_t now);
    void tick(std::uint64_t now);
    void disconnect(const std::string& connection);
    void policy(Policy next, std::uint64_t now);
    bool closed(const std::string& connection) const;
    std::string close_reason(const std::string& connection) const;
    std::size_t frame_bound(const std::string& connection) const;
    std::size_t request_count() const { return ledger_.size(); }
    std::optional<Subscription> subscription(const std::string& connection) const;
    std::size_t demand_count() const;
    bool offer(const std::string& connection, std::uint64_t ticket, const std::string& record,
               const Json& snapshot, std::optional<std::uint64_t> base, std::uint64_t now);
private:
    struct Connection {
        std::string id, principal;
        Authority authority;
        std::uint64_t opened;
        bool negotiated = false;
        std::string reason;
        protocol::Negotiated selection{1, protocol::frame_limit, {}, {}};
        protocol::Outbox outbox;
        std::string subscription_id = {}, subscription_body = {};
        std::uint64_t ticket = 0, renewed = 0;
        std::optional<std::uint64_t> heartbeat = {}, generation = {};
    };
    std::string envelope(const Connection& connection, const std::string& type, Json body) const;
    bool queue(Connection& connection, const std::string& type, Json body);
    void dispatch(Connection& connection, const protocol::Message& message, std::uint64_t now);
    void shut(Connection& connection, const char* reason);
    bool may_subscribe(const Connection& connection) const;
    protocol::TelemetryBinding binding(const Connection& connection, const std::string& subscription,
                                       protocol::TelemetryDirection direction) const;
    void subscribe(Connection& connection, const protocol::Message& message, std::uint64_t now);
    void resync(Connection& connection, const char* reason);
    std::string epoch_;
    std::uint64_t revision_;
    Policy policy_;
    std::optional<std::uint64_t> last_;
    protocol::Ledger ledger_;
    std::map<std::string, Connection> connections_;
    std::optional<InventorySource> source_;
    std::uint64_t tickets_ = 0;
    bool clock_fault_ = false;
};
} // namespace syspane::configuration
