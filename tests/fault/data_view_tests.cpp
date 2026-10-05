#include "data_view.hpp"
#include <iostream>
#include <stdexcept>

namespace m = syspane::model;
namespace r = syspane::recovery;
namespace c = syspane::configuration;
using D = r::DataCode;
void check(bool condition, const char* expression, int line) {
    if (!condition) throw std::runtime_error(std::string(expression)+" at "+std::to_string(line));
}
#define CHECK(expression) check(static_cast<bool>(expression), #expression, __LINE__)
c::Authority authority() { return {true, "desktop", {"desktop"}}; }
c::Policy policy(std::uint64_t revision = 7) {
    c::Policy result; result.available = true; result.revision = revision;
    result.disclosure[{"desktop", "desktop"}] = {"operational"};
    result.disclosure[{"desktop", "accessibility"}] = {"operational"};
    return result;
}
std::vector<m::Metric> metrics() { return {{"network.throughput", "B/s", m::ValueKind::uint64}}; }
m::Publication full(std::string record = "full:40", std::uint64_t generation = 40, std::uint64_t value = 10, std::string epoch = "epoch:1") {
    m::Observation o;
    o.entity_id = "nic:1"; o.field = "network.throughput"; o.source_id = "source:1";
    o.value = value; o.unit = "B/s"; o.support = m::Support::supported; o.acquisition = m::Acquisition::success;
    o.freshness = m::Freshness::current; o.presence = m::Presence::present;
    o.observed_at = m::UtcTime{1791158400, 0}; o.attempted_at = *o.observed_at; o.measured_at = m::Tick{epoch, 1000000000};
    return {std::move(record), {}, {"producer:1", epoch, generation, {{"nic:1", "network.interface", "Fixture", generation}},
        {{"source:1", "fixture", "host:1"}}, {}, {o}}};
}
m::Publication delta(std::string record = "delta:41", std::uint64_t base = 40, std::uint64_t next = 41, std::uint64_t value = 20) {
    auto result = full(std::move(record), next, value); result.expected_base = base; return result;
}
std::uint64_t attach(r::DataView& view, std::uint64_t now = 0, const std::string& epoch = "epoch:1") {
    const auto result = view.attach("producer:1", epoch, now);
    CHECK(result.code == D::accepted && result.token); return result.token;
}
void expect(r::DataView& view, std::uint64_t now, std::uint64_t generation, std::uint64_t value, r::Presentation presentation,
            const std::string& epoch = "epoch:1", std::optional<std::uint64_t> accepted = {}) {
    unsigned calls = 0;
    CHECK(view.project(now, [&](const m::Snapshot& snapshot, const r::LeaseView& lease) {
        ++calls; CHECK(snapshot.generation == generation && snapshot.epoch == epoch && snapshot.producer == "producer:1");
        CHECK(std::get<std::uint64_t>(snapshot.observations.at(0).value) == value);
        CHECK(lease.presentation == presentation && lease.last && lease.last->generation == generation && lease.last->epoch == epoch);
        if (accepted) CHECK(lease.last->accepted_ms == *accepted);
    }));
    CHECK(calls == 1);
}
void atomic() {
    r::DataView view(authority(), policy(), "desktop", "operational", metrics());
    const auto token = attach(view);
    CHECK(view.status(0).presentation == r::Presentation::waiting && !view.status(0).payload_available);
    CHECK(view.delta(token, 7, delta(), 0).code == D::snapshot_required);
    CHECK(view.full(token, 7, full(), 10).code == D::accepted);
    expect(view, 11, 40, 10, r::Presentation::active, "epoch:1", 10);
    auto bad = full("invalid", 41, 99); bad.next.entities.push_back(bad.next.entities[0]);
    auto result = view.full(token, 7, bad, 12);
    CHECK(result.code == D::invalid && result.validation == m::Code::duplicate_entity);
    expect(view, 13, 40, 10, r::Presentation::retained);
    CHECK(view.delta(token, 7, delta(), 14).code == D::snapshot_required);
    CHECK(view.full(token, 7, full("recovered", 41, 30), 15).code == D::accepted);
    auto missing = delta("missing", 40, 42);
    CHECK(view.delta(token, 7, missing, 16).code == D::snapshot_required);
    expect(view, 17, 41, 30, r::Presentation::retained);
    CHECK(view.full(token, 7, full("recovered", 41, 30), 18).code == D::accepted);
    auto invalid_observation = delta("invalid-observation", 41, 42); invalid_observation.next.observations[0].unit = "wrong";
    CHECK(view.delta(token, 7, invalid_observation, 19).validation == m::Code::invalid_observation);
    expect(view, 20, 41, 30, r::Presentation::retained);
    auto wrong_shape = delta();
    CHECK(view.full(token, 7, wrong_shape, 21).code == D::invalid);
    auto wrong_epoch = full("wrong", 42, 55, "epoch:2");
    CHECK(view.full(token, 7, wrong_epoch, 22).validation == m::Code::wrong_epoch);
    CHECK(!view.status(23).alive);
    expect(view, 23, 41, 30, r::Presentation::retained);
}
void replay() {
    r::DataView view(authority(), policy(), "desktop", "operational", metrics());
    const auto token = attach(view);
    CHECK(view.full(token, 7, full(), 10).code == D::accepted);
    CHECK(view.full(token, 7, full(), 11).code == D::duplicate);
    expect(view, 12, 40, 10, r::Presentation::active, "epoch:1", 10);
    CHECK(view.delta(token, 7, delta(), 20).code == D::accepted);
    CHECK(view.delta(token, 7, delta(), 21).code == D::duplicate);
    expect(view, 22, 41, 20, r::Presentation::active, "epoch:1", 20);
    CHECK(view.full(token, 7, full(), 23).code == D::duplicate);
    expect(view, 24, 41, 20, r::Presentation::active, "epoch:1", 20);
    CHECK(view.gap(token, 7, 25) == D::accepted);
    CHECK(view.full(token, 7, full("resync-after-delta", 41, 20), 26).code == D::accepted);
    expect(view, 27, 41, 20, r::Presentation::active, "epoch:1", 26);
    CHECK(view.full(token, 7, full("full:42", 42, 30), 30).code == D::accepted);
    auto changed = delta(); changed.next.observations[0].value = std::uint64_t{999};
    CHECK(view.delta(token, 7, changed, 31).validation == m::Code::conflict);
    expect(view, 32, 42, 30, r::Presentation::retained, "epoch:1", 30);
    CHECK(view.full(token, 7, full(), 33).code == D::duplicate);
    CHECK(view.status(33).snapshot_required);
    CHECK(view.full(token, 7, full("changed", 42, 999), 34).validation == m::Code::conflict);
    CHECK(view.full(token, 7, full("confirming", 42, 30), 35).code == D::accepted);
    expect(view, 36, 42, 30, r::Presentation::active, "epoch:1", 35);
    CHECK(view.gap(token, 7, 37) == D::accepted);
    CHECK(view.full(token, 7, full("full:42", 42, 30), 38).code == D::accepted);
    CHECK(view.full(token, 7, full("lower", 41, 30), 39).validation == m::Code::generation_order);
    expect(view, 40, 42, 30, r::Presentation::retained, "epoch:1", 38);
}
void reconnect() {
    r::DataView view(authority(), policy(), "desktop", "operational", metrics());
    const auto old = attach(view);
    CHECK(view.full(old, 7, full(), 10).code == D::accepted);
    auto removed = full("removed", 41); removed.next.entities.clear(); removed.next.observations.clear();
    CHECK(view.full(old, 7, removed, 20).code == D::accepted);
    CHECK(view.disconnect(old, 7, 21) == D::accepted);
    const auto token = attach(view, 30);
    CHECK(token > old && view.status(30).snapshot_required);
    CHECK(view.full(token, 7, removed, 31).code == D::accepted);
    CHECK(view.full(token, 7, full("reuse", 42), 32).validation == m::Code::retired_identity);
    CHECK(view.full(token, 7, removed, 33).code == D::accepted);
    const auto next = attach(view, 40, "epoch:2");
    CHECK(view.heartbeat(token, 7, 9, 0) == D::stale_attachment);
    CHECK(view.gap(token, 7, 0) == D::stale_attachment);
    CHECK(view.full(token, 7, full(), 0).code == D::stale_attachment);
    CHECK(view.disconnect(token, 7, 0) == D::stale_attachment);
    CHECK(view.project(40, [&](const m::Snapshot& data, const r::LeaseView& state) {
        CHECK(data.epoch == "epoch:1" && data.generation == 41 && state.presentation == r::Presentation::retained);
    }));
    CHECK(view.heartbeat(next, 7, 0, 41) == D::accepted);
    CHECK(view.full(next, 7, full("new", 0, 77, "epoch:2"), 42).code == D::accepted);
    expect(view, 43, 0, 77, r::Presentation::active, "epoch:2");
}
void lease() {
    r::DataView view(authority(), policy(), "desktop", "operational", metrics());
    const auto token = attach(view);
    CHECK(view.full(token, 7, full(), 10).code == D::accepted);
    CHECK(view.heartbeat(token, 7, 0, 1000) == D::accepted);
    CHECK(view.heartbeat(token, 7, 0, 3999) == D::duplicate);
    auto failed = delta(); auto& o = failed.next.observations[0];
    o.value = std::monostate{}; o.observed_at.reset(); o.measured_at.reset(); o.acquisition = m::Acquisition::failed;
    o.error = m::Error{"source.unavailable", "Unavailable", true}; o.attempted_at.seconds = 1791158401;
    CHECK(view.delta(token, 7, failed, 3999).code == D::accepted);
    CHECK(view.project(3999, [&](const m::Snapshot& data, const r::LeaseView& state) {
        const auto& observation = data.observations[0];
        CHECK(state.presentation == r::Presentation::active && observation.acquisition == m::Acquisition::failed);
        CHECK(std::get<std::uint64_t>(observation.value) == 10 && observation.observed_at->seconds == 1791158400);
        CHECK(observation.attempted_at.seconds == 1791158401 && observation.freshness == m::Freshness::stale);
    }));
    CHECK(view.status(4000).reason == r::LeaseReason::expired);
    expect(view, 4000, 41, 10, r::Presentation::retained);
    CHECK(view.heartbeat(token, 7, 1, 4000) == D::closed);
    const auto next = attach(view, 5000);
    CHECK(view.full(next, 7, full("fresh", 42, 20), 5001).code == D::accepted);
    CHECK(view.heartbeat(next, 7, 0, 6000) == D::accepted);
    CHECK(view.project(6001, [&](const m::Snapshot& data, const r::LeaseView& state) {
        CHECK(state.presentation == r::Presentation::active);
        CHECK(m::freshness_at(data.observations[0], {"epoch:1", 2000000000}, 1000000000) == m::Freshness::stale);
        CHECK(data.observations[0].measured_at->nanoseconds == 1000000000);
    }));
}
void policy_cases() {
    auto denied = policy(); denied.available = false;
    r::DataView unavailable(authority(), denied, "desktop", "public", metrics());
    CHECK(unavailable.attach("producer:1", "epoch:1", 0).code == D::denied);
    unsigned calls = 0;
    CHECK(!unavailable.project(0, [&](const m::Snapshot&, const r::LeaseView&) { ++calls; })); CHECK(calls == 0);
    for (unsigned variant = 0; variant < 5; ++variant) {
        auto auth = authority(); auto p = policy(); std::string channel = "desktop", classification = "operational";
        if (variant == 0) auth.authenticated = false;
        if (variant == 1) auth.role_grants.clear();
        if (variant == 2) channel = "preview";
        if (variant == 3) classification = "sensitive";
        if (variant == 4) p.disclosure[{"desktop", "accessibility"}] = {};
        r::DataView view(auth, p, channel, classification, metrics());
        CHECK(view.attach("producer:1", "epoch:1", 0).code == D::denied);
    }
    r::DataView view(authority(), policy(), "desktop", "operational", metrics());
    const auto old = attach(view);
    CHECK(view.full(old, 7, full(), 10).code == D::accepted);
    const auto lifetime = view.status(10).lifetime;
    auto revoked = policy(8); revoked.denied_capabilities.insert("telemetry.subscribe");
    CHECK(view.policy(revoked, 20) == D::denied);
    CHECK(!view.status(20).payload_available && view.status(20).presentation == r::Presentation::empty);
    CHECK(view.status(20).lifetime > lifetime);
    CHECK(!view.project(20, [&](const m::Snapshot&, const r::LeaseView&) { ++calls; })); CHECK(calls == 0);
    CHECK(view.policy(policy(9), 30) == D::accepted);
    CHECK(!view.project(30, [&](const m::Snapshot&, const r::LeaseView&) { ++calls; }));
    const auto token = attach(view, 30);
    CHECK(view.full(old, 7, full(), 999999).code == D::stale_attachment);
    CHECK(view.full(token, 7, full(), 0).code == D::policy_changed);
    CHECK(view.heartbeat(token, 9, 0, 31) == D::accepted);
    CHECK(view.full(token, 9, full(), 32).code == D::accepted);
    expect(view, 33, 40, 10, r::Presentation::active);
    CHECK(view.policy(policy(9), 34) == D::policy_changed); // Same-revision replacement fails closed.
    CHECK(!view.status(34).permitted && !view.status(34).payload_available);
    CHECK(view.policy(policy(8), 35) == D::policy_changed);
    CHECK(view.policy(policy(10), 36) == D::accepted);
    CHECK(!view.status(36).payload_available && !view.status(36).alive);
    const auto third = attach(view, 36);
    CHECK(view.full(third, 10, full(), 37).code == D::accepted);
    c::Policy missing;
    CHECK(view.policy(missing, 38) == D::denied); // Unavailable revision zero still revokes.
    CHECK(!view.status(38).payload_available);
    CHECK(view.policy(policy(10), 39) == D::policy_changed); // Unavailable snapshot cannot roll back the high-water mark.
}
void faults() {
    m::Limits limits; limits.replay_records = 1;
    r::DataView bounded(authority(), policy(), "desktop", "operational", metrics(), limits);
    const auto token = attach(bounded);
    CHECK(bounded.full(token, 7, full(), 10).code == D::accepted);
    CHECK(bounded.delta(token, 7, delta(), 11).code == D::capacity);
    expect(bounded, 12, 40, 10, r::Presentation::retained);
    const auto same = attach(bounded, 13);
    CHECK(bounded.full(same, 7, full(), 14).code == D::accepted);
    CHECK(bounded.full(same, 7, full("cannot-reset-same-generation", 40), 15).code == D::capacity);
    CHECK(bounded.full(same, 7, full("cannot-reset", 41), 15).code == D::capacity);
    expect(bounded, 16, 40, 10, r::Presentation::retained);
    CHECK(bounded.project(17, [&](const m::Snapshot&, const r::LeaseView&) {
        bool rejected = false;
        try { (void)bounded.policy(policy(8), 18); } catch (const std::logic_error&) { rejected = true; }
        CHECK(rejected);
    }));
    bool thrown = false;
    try { bounded.project(18, [](const m::Snapshot&, const r::LeaseView&) { throw std::runtime_error("fixture"); }); }
    catch (const std::runtime_error&) { thrown = true; }
    CHECK(thrown); expect(bounded, 19, 40, 10, r::Presentation::retained);
    CHECK(bounded.status(18).reason == r::LeaseReason::clock_fault);
    CHECK(bounded.heartbeat(same, 7, 1, 20) == D::clock_fault);
    auto revoked = policy(8); revoked.available = false;
    CHECK(bounded.policy(revoked, 0) == D::denied); // Removal survives broken clock.
    CHECK(!bounded.status(21).payload_available);
    CHECK(bounded.policy(policy(9), 22) == D::accepted);
    CHECK(bounded.attach("producer:1", "epoch:2", 23).code == D::clock_fault);
    auto too_large = limits; too_large.replay_records = 129;
    bool rejected = false;
    try { r::DataView invalid(authority(), policy(), "desktop", "operational", metrics(), too_large); }
    catch (const std::invalid_argument&) { rejected = true; }
    CHECK(rejected);
}
int main(int argc, char** argv) {
    try {
        if (argc != 2) return 2;
        const std::string name = argv[1];
        if (name == "VIEW-ATOMIC") atomic(); else if (name == "VIEW-REPLAY") replay();
        else if (name == "VIEW-RECONNECT") reconnect(); else if (name == "VIEW-LEASE") lease();
        else if (name == "VIEW-POLICY") policy_cases(); else if (name == "VIEW-FAULT") faults(); else return 2;
        std::cout << name << ": pass\n"; return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
