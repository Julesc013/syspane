#pragma once
#include "data_view.hpp"

namespace syspane::recovery {
struct DeliveryScope {std::uint64_t profile=0,generation=0;};
struct DeliveredFrame {
    std::string bytes;
    std::uint64_t received_ms;
    model::Tick received_tick;
    // Receiver-local admission order, independent of snapshot generation.
    // Zero is invalid; duplicate wire frames never advance this ordinal.
    std::uint64_t ordinal=0;
};
// A bounded, immutable transfer from a serialized native receiver to the UI.
// The UI must supply its CURRENT scope at every use, including refresh without
// new data. Holding a prior view is not authority to retain a withdrawn profile.
struct TelemetryDelivery {
    DeliveryScope scope;
    std::shared_ptr<const protocol::TelemetryBinding> binding;
    std::shared_ptr<const DeliveredFrame> frame;
    std::optional<model::Tick> clock;
    std::optional<std::uint64_t> heartbeat;
    std::uint64_t clock_ms=0,live_until_ms=0;
    bool connected=false;
    bool live(DeliveryScope current,std::uint64_t now)const;
    bool deliverable(DeliveryScope current,std::uint64_t now)const;
};
// Native I/O, policy ownership and the scope guard belong to the caller. This
// owner validates at ORIGINAL receipt, coalesces only complete accepted states,
// and never grants more lease time because delivery to a GUI was delayed.
class TelemetryReceiver {
public:
    TelemetryReceiver(DeliveryScope,configuration::Policy,std::vector<model::Metric>,
                      protocol::TelemetryBinding,std::uint64_t now);
    DataResult receive(std::string_view,std::uint64_t received_ms,const model::Tick&);
    DataCode heartbeat(std::uint64_t sequence,std::uint64_t received_ms);
    DataCode sample(const model::Tick&,std::uint64_t observed_ms);
    TelemetryDelivery view(std::uint64_t now);
    void disconnect(std::uint64_t now);
    void withdraw(std::uint64_t now);
private:
    DataView model_;
    TelemetryDelivery delivery_;
    std::uint64_t token_=0,last_ms_=0,ordinal_=0;
    DataCode advance(std::uint64_t now);
    bool deadline(std::uint64_t now);
};
}
