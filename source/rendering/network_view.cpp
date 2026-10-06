#include "network_view.hpp"
#include <cmath>
#include <limits>
#include <new>

namespace syspane::rendering {
namespace {
// Nonnegative decimal integer arithmetic, bounded by binary64's exponent range.
void multiply(std::string& digits, unsigned factor) {
    unsigned carry = 0;
    for (auto i = digits.size(); i-- > 0;) {
        const auto n = unsigned(digits[i] - '0') * factor + carry;
        digits[i] = char('0' + n % 10); carry = n / 10;
    }
    while (carry) { digits.insert(digits.begin(), char('0' + carry % 10)); carry /= 10; }
}
unsigned halve(std::string& digits) {
    unsigned carry = 0;
    for (auto& digit : digits) {
        const auto n = carry * 10 + unsigned(digit - '0');
        digit = char('0' + n / 2); carry = n % 2;
    }
    const auto nonzero = digits.find_first_not_of('0');
    if (nonzero == std::string::npos) digits = "0";
    else if (nonzero) digits.erase(0, nonzero);
    return carry;
}
void increment(std::string& digits) {
    for (auto i = digits.size(); i-- > 0;) {
        if (digits[i] != '9') { ++digits[i]; return; }
        digits[i] = '0';
    }
    digits.insert(digits.begin(), '1');
}
std::string rate_text(double value) {
    static_assert(std::numeric_limits<double>::is_iec559 && std::numeric_limits<double>::digits == 53,
                  "The presentation contract requires IEEE binary64");
    int exponent = 0;
    const auto fraction = std::frexp(value, &exponent);
    std::string digits = std::to_string(static_cast<std::uint64_t>(std::ldexp(fraction, 53)));
    multiply(digits, 125); // value * 1000 = significand * 125 * 2^(exponent-50).
    exponent -= 50;
    if (exponent >= 0) { for (int n = 0; n < exponent; ++n) multiply(digits, 2); }
    else {
        unsigned rounding = 0;
        for (int n = 0; n < -exponent; ++n) rounding = halve(digits);
        if (rounding) increment(digits); // Highest discarded bit: ties round upward.
    }
    if (digits.size() < 4) digits.insert(0, 4 - digits.size(), '0');
    digits.insert(digits.size() - 3, ".");
    return digits;
}
NetworkFrame empty(NetworkViewCode code) { NetworkFrame frame; frame.code = code; return frame; }
NetworkFrame prepare(const model::Snapshot& snapshot, const recovery::LeaseView& lease,
                     const std::optional<model::Tick>& now, const NetworkSelection& selection, std::size_t limit) {
    if (snapshot.reported_version != "0.2.0") return empty(NetworkViewCode::invalid);
    if (snapshot.producer != selection.producer || snapshot.epoch != selection.epoch)
        return empty(NetworkViewCode::selection_missing);
    const model::Entity* entity = nullptr;
    for (const auto& candidate : snapshot.entities) if (candidate.id == selection.entity) entity = &candidate;
    if (!entity) return empty(NetworkViewCode::selection_missing);
    if (entity->kind != "network.interface") return empty(NetworkViewCode::invalid);
    bool source_valid = false;
    for (const auto& source : snapshot.sources)
        if (source.id == "provider:native-network" && source.kind == "native.network.counters" && source.scope == "host:local") source_valid = true;
    if (!source_valid) return empty(NetworkViewCode::invalid);
    const std::array<const char*, 4> keys{{"network.receive_bytes", "network.transmit_bytes",
        "network.receive_bytes_per_second", "network.transmit_bytes_per_second"}};
    NetworkFrame frame;
    frame.code = NetworkViewCode::ready; frame.selected = selection;
    frame.generation = std::to_string(snapshot.generation); frame.presentation = lease.presentation; frame.reason = lease.reason;
    frame.accounted_bytes = 1024 + selection.producer.size() + selection.epoch.size() + selection.entity.size() + frame.generation.size();
    for (std::size_t index = 0; index < keys.size(); ++index) {
        const model::Observation* selected = nullptr;
        for (const auto& observation : snapshot.observations) {
            if (observation.entity_id != selection.entity || observation.field != keys[index]) continue;
            if (selected || observation.source_id != "provider:native-network") return empty(NetworkViewCode::invalid);
            selected = &observation;
        }
        if (!selected || selected->unit != (index < 2 ? "byte" : "byte/second")) return empty(NetworkViewCode::invalid);
        const auto& observation = *selected; auto& field = frame.fields[index];
        if (!std::holds_alternative<std::monostate>(observation.value)) {
            if (index < 2) {
                const auto* counter = std::get_if<std::uint64_t>(&observation.value);
                if (!counter) return empty(NetworkViewCode::invalid);
                field.value = std::to_string(*counter);
            } else {
                const auto* rate = std::get_if<double>(&observation.value);
                if (!rate || !std::isfinite(*rate) || *rate < 0) return empty(NetworkViewCode::invalid);
                field.value = rate_text(*rate);
            }
        }
        field.unit = observation.unit; field.support = observation.support;
        field.acquisition = observation.acquisition; field.presence = observation.presence; field.origin = observation.origin;
        field.reported = observation.freshness; field.effective = model::freshness_at(observation, now.value_or(model::Tick{}), 3000000000ULL);
        field.observed_at = observation.observed_at; field.attempted_at = observation.attempted_at;
        field.measured_at = observation.measured_at; field.interval_ns = observation.sample_interval_ns;
        if (observation.measured_at && now) {
            const auto& measured = *observation.measured_at;
            if (!measured.epoch.empty() && measured.epoch == now->epoch && measured.clock_id == now->clock_id &&
                measured.clock_scope == now->clock_scope && measured.nanoseconds <= now->nanoseconds)
                field.age_ns = now->nanoseconds - measured.nanoseconds;
        }
        if (observation.error) field.error_code = observation.error->code;
        frame.accounted_bytes += (field.value ? field.value->size() : 0) + field.unit.size() + field.error_code.size() + field.attempted_at.subnanoseconds.size();
        if (field.observed_at) frame.accounted_bytes += field.observed_at->subnanoseconds.size();
        if (field.measured_at) frame.accounted_bytes += field.measured_at->epoch.size() + field.measured_at->clock_id.size() + field.measured_at->clock_scope.size();
    }
    if (frame.accounted_bytes > limit) return empty(NetworkViewCode::capacity);
    return frame;
}
}
static void project_impl(recovery::DataView& view, const NetworkSelection& selection, std::uint64_t now_ms,
                         const std::optional<model::Tick>& measured_now, const std::function<void(const NetworkFrame&)>& sink, std::size_t limit) {
    const auto status = view.status(now_ms);
    if (!status.permitted) { sink(empty(NetworkViewCode::restricted)); return; }
    if (!status.payload_available) { sink(empty(NetworkViewCode::waiting)); return; }
    if (!measured_now && status.presentation != recovery::Presentation::retained) { sink(empty(NetworkViewCode::unavailable)); return; }
    bool delivered = false;
    try {
        const auto deliver = [&](const auto& snapshot, const auto& lease) {
            NetworkFrame frame = prepare(snapshot, lease, measured_now, selection, limit);
            delivered = true;
            sink(frame); // Consumer exceptions must never cause a second callback.
        };
        const bool borrowed = measured_now ? view.project_measured(now_ms, *measured_now,
            [&](const auto& snapshot, const auto& lease, const auto&) { deliver(snapshot, lease); }) : view.project(now_ms, deliver);
        if (!borrowed) { delivered = true; sink(empty(NetworkViewCode::unavailable)); }
    } catch (const std::bad_alloc&) {
        if (delivered) throw;
        sink(empty(NetworkViewCode::capacity));
    }
}
void project_network(recovery::DataView& view, const NetworkSelection& selection, std::uint64_t now_ms,
                     const model::Tick& measured_now, const std::function<void(const NetworkFrame&)>& sink, std::size_t limit) {
    project_impl(view, selection, now_ms, measured_now, sink, limit);
}
void project_network_retained(recovery::DataView& view, const NetworkSelection& selection, std::uint64_t now_ms,
                              const std::function<void(const NetworkFrame&)>& sink, std::size_t limit) {
    project_impl(view, selection, now_ms, {}, sink, limit);
}
}
