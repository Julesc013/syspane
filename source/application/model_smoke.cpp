#include "state.hpp"

#include <iostream>

using namespace syspane::model;

int main() {
    Store store("fixture", "E1", {{"throughput", "B/s", ValueKind::uint64}, {"serial", "1", ValueKind::string}});
    Observation rate;
    rate.entity_id = "A1"; rate.field = "throughput"; rate.source_id = "S1";
    rate.value = std::uint64_t{42}; rate.unit = "B/s"; rate.support = Support::supported;
    rate.acquisition = Acquisition::success; rate.freshness = Freshness::current;
    rate.presence = Presence::present; rate.observed_at = UtcTime{1791158400, 0};
    rate.attempted_at = *rate.observed_at; rate.measured_at = Tick{"E1", 1000000000};
    Observation unsupported;
    unsupported.entity_id = "A1"; unsupported.field = "serial"; unsupported.source_id = "S1";
    unsupported.unit = "1"; unsupported.support = Support::unsupported;
    unsupported.acquisition = Acquisition::disabled; unsupported.presence = Presence::present;
    Snapshot first{"fixture", "E1", 7, {{"A1", "network_interface", "Ethernet", 7}},
                   {{"S1", "fixture", "local"}}, {}, {rate, unsupported}};
    if (!store.publish({"initial", {}, first}).accepted()) return 1;
    auto failed = first;
    failed.generation = 8;
    failed.observations[0].value = std::monostate{};
    failed.observations[0].acquisition = Acquisition::failed;
    failed.observations[0].attempted_at = {1791158401, 0};
    failed.observations[0].error = Error{"fixture.unavailable", "source unavailable", true};
    if (!store.publish({"failed-attempt", 7, failed}).accepted()) return 1;
    const auto state = store.snapshot();
    const auto& observed = state->observations[0];
    if (observed.freshness != Freshness::stale || observed.acquisition != Acquisition::failed ||
        state->observations[1].value.index() != 0 || state->observations[1].support != Support::unsupported)
        return 1;
    std::cout << "{\"epoch\":\"" << state->epoch << "\",\"generation\":\"" << state->generation
              << "\",\"throughput\":{\"value\":\"" << std::get<std::uint64_t>(observed.value)
              << "\",\"unit\":\"B/s\",\"acquisition\":\"failed\",\"freshness\":\"stale\"},"
                 "\"serial\":{\"value\":null,\"support\":\"unsupported\"}}\n";
    return 0;
}
