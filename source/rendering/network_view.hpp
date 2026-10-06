#pragma once
#include "data_view.hpp"
#include <array>

namespace syspane::rendering {
enum class NetworkViewCode { ready, restricted, waiting, unavailable, selection_missing, invalid, capacity };
struct NetworkSelection { std::string producer, epoch, entity; };
struct NetworkField {
    std::optional<std::string> value;
    std::string unit, error_code;
    model::Support support = model::Support::unknown;
    model::Acquisition acquisition = model::Acquisition::pending;
    model::Presence presence = model::Presence::unknown;
    model::Origin origin = model::Origin::observed;
    model::Freshness reported = model::Freshness::unknown, effective = model::Freshness::unknown;
    std::optional<model::UtcTime> observed_at;
    model::UtcTime attempted_at;
    std::optional<model::Tick> measured_at;
    std::optional<std::uint64_t> age_ns, interval_ns;
};
struct NetworkFrame {
    NetworkViewCode code = NetworkViewCode::unavailable;
    NetworkSelection selected;
    std::string generation;
    recovery::Presentation presentation = recovery::Presentation::empty;
    recovery::LeaseReason reason = recovery::LeaseReason::none;
    std::array<NetworkField, 4> fields;
    std::size_t accounted_bytes = 0;
};
// One synchronous borrow. The sink may not retain/copy/export payload or reenter
// DataView. A native cache requires a separately admitted policy-erasure owner.
void project_network(recovery::DataView& view, const NetworkSelection& selection,
    std::uint64_t now_ms, const model::Tick& measured_now,
    const std::function<void(const NetworkFrame&)>& sink, std::size_t byte_limit = 4096);
// Explicitly retained, policy-permitted drawing when no qualified current clock
// exists. It never projects active state: non-null values are stale, age is null.
void project_network_retained(recovery::DataView& view, const NetworkSelection& selection,
    std::uint64_t now_ms, const std::function<void(const NetworkFrame&)>& sink, std::size_t byte_limit = 4096);
}
