#include "recovery.hpp"
#include "state.hpp"

#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <type_traits>

using namespace syspane::recovery;
static_assert(!std::is_copy_constructible_v<ProducerLease> && !std::is_move_constructible_v<ProducerLease>);
static_assert(!std::is_copy_constructible_v<RenderWatch> && !std::is_move_constructible_v<RenderWatch>);
static_assert(!std::is_copy_constructible_v<RestartGate> && !std::is_move_constructible_v<RestartGate>);

namespace {
void require(bool condition, const char* expression, int line) {
    if (!condition) throw std::runtime_error(std::string(expression) + " at line " + std::to_string(line));
}
#define CHECK(expression) require(static_cast<bool>(expression), #expression, __LINE__)

std::uint64_t attach(ProducerLease& lease, std::uint64_t now = 100, const std::string& epoch = "E1") {
    const auto result = lease.attach("P1", epoch, now);
    CHECK(result.code == Code::accepted); CHECK(result.token != 0);
    return result.token;
}
void lease01() {
    ProducerLease lease;
    CHECK(lease.view().presentation == Presentation::empty);
    const auto token = attach(lease);
    CHECK(lease.view().presentation == Presentation::waiting);
    CHECK(lease.snapshot(token, "P1", "E1", 40, 101) == Code::accepted);
    CHECK(lease.heartbeat(token, 7, 1100) == Code::accepted);
    CHECK(lease.heartbeat(token, 7, 3000) == Code::duplicate);
    CHECK(lease.tick(4099) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::active);
    CHECK(lease.view().last->generation == 40); CHECK(lease.view().last->accepted_ms == 101);
    CHECK(lease.tick(4100) == Code::accepted);
    CHECK(!lease.view().alive); CHECK(lease.view().snapshot_required);
    CHECK(lease.view().presentation == Presentation::retained);
    CHECK(lease.view().reason == LeaseReason::expired);
    CHECK(lease.heartbeat(token, 8, 4100) == Code::closed);
    CHECK(lease.snapshot(token, "P1", "E1", 41, 4100) == Code::closed);
    CHECK(lease.view().last->generation == 40);

    ProducerLease traffic;
    const auto t = attach(traffic, 0);
    CHECK(traffic.snapshot(t, "P1", "E1", 1, 0) == Code::accepted);
    CHECK(traffic.delta(t, 1, 2, 2999) == Code::accepted);
    CHECK(traffic.heartbeat(t, 0, 3000) == Code::closed); // Data did not renew lease.
    CHECK(traffic.view().last->generation == 2);
}
void lease02() {
    ProducerLease lease;
    const auto old = attach(lease);
    CHECK(lease.snapshot(old, "P1", "E1", 40, 100) == Code::accepted);
    CHECK(lease.disconnect(old, 101) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::retained);
    CHECK(lease.view().reason == LeaseReason::disconnected);
    const auto next = attach(lease, 200, "E2");
    CHECK(next > old); CHECK(lease.view().alive); CHECK(lease.view().snapshot_required);
    CHECK(lease.view().last->epoch == "E1"); CHECK(lease.view().last->producer == "P1");
    CHECK(lease.heartbeat(old, 100, 1) == Code::stale_attachment);
    CHECK(lease.disconnect(old, 1) == Code::stale_attachment);
    CHECK(lease.gap(old, 1) == Code::stale_attachment);
    CHECK(lease.snapshot(old, "P1", "E1", 41, 1) == Code::stale_attachment);
    CHECK(lease.delta(old, 40, 41, 1) == Code::stale_attachment);
    CHECK(lease.delta(next, 40, 41, 200) == Code::snapshot_required);
    CHECK(lease.heartbeat(next, 0, 200) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::retained);
    CHECK(lease.snapshot(next, "P1", "E2", 0, 201) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::active);
    CHECK(lease.view().last->epoch == "E2"); CHECK(lease.view().last->generation == 0);
    const auto same_epoch = attach(lease, 300, "E2");
    CHECK(lease.delta(same_epoch, 0, 1, 300) == Code::snapshot_required);
    CHECK(lease.snapshot(same_epoch, "P1", "E2", 0, 301) == Code::accepted);
    const auto different = lease.attach("P2", "E3", 302);
    CHECK(different.code == Code::accepted);
    CHECK(lease.view().last->producer == "P1"); // No relabelling retained data.
    CHECK(lease.snapshot(different.token, "P2", "E3", 0, 303) == Code::accepted);
    CHECK(lease.view().last->producer == "P2");
}
void lease03() {
    ProducerLease lease;
    const auto token = attach(lease);
    CHECK(lease.snapshot(token, "P1", "E1", 40, 100) == Code::accepted);
    CHECK(lease.snapshot(token, "P1", "E1", 40, 101) == Code::duplicate);
    CHECK(lease.view().last->accepted_ms == 100);
    CHECK(lease.delta(token, 39, 41, 102) == Code::snapshot_required);
    CHECK(lease.view().last->generation == 40);
    CHECK(lease.delta(token, 40, 41, 103) == Code::snapshot_required);
    CHECK(lease.heartbeat(token, 1, 104) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::retained);
    CHECK(lease.snapshot(token, "P1", "E1", 40, 105) == Code::accepted);
    CHECK(lease.delta(token, 40, 41, 106) == Code::accepted);
    CHECK(lease.delta(token, 41, 41, 107) == Code::snapshot_required);
    CHECK(lease.snapshot(token, "P1", "E1", 40, 108) == Code::sequence_order);
    CHECK(lease.view().last->generation == 41); CHECK(lease.view().last->accepted_ms == 106);
    CHECK(lease.snapshot(token, "P1", "E1", 41, 109) == Code::accepted);
    CHECK(lease.gap(token, 110) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::retained);
    CHECK(lease.snapshot(token, "P1", "E2", 42, 111) == Code::invalid);
    CHECK(!lease.view().alive); CHECK(lease.view().last->epoch == "E1");
    CHECK(lease.view().last->generation == 41);
    const auto next = attach(lease, 112);
    CHECK(lease.snapshot(next, "P2", "E1", 42, 112) == Code::invalid);
    CHECK(!lease.view().alive);
}
void lease04() {
    namespace m = syspane::model;
    m::Observation observation;
    observation.entity_id = "A1"; observation.field = "throughput"; observation.source_id = "S1";
    observation.value = std::uint64_t{10}; observation.unit = "B/s";
    observation.support = m::Support::supported; observation.acquisition = m::Acquisition::success;
    observation.freshness = m::Freshness::current; observation.presence = m::Presence::present;
    observation.observed_at = m::UtcTime{1791158400, 0}; observation.attempted_at = *observation.observed_at;
    observation.measured_at = m::Tick{"E1", 1000000000};
    m::Snapshot data{"P1", "E1", 40, {{"A1", "network_interface", "Test", 1}},
        {{"S1", "fixture", "local"}}, {}, {observation}};
    m::Store store("P1", "E1", {{"throughput", "B/s", m::ValueKind::uint64}});
    CHECK(store.publish({"snapshot", {}, data}).code == m::Code::accepted);
    const auto held = store.snapshot();
    ProducerLease lease;
    const auto token = attach(lease, 1000);
    CHECK(lease.snapshot(token, "P1", "E1", 40, 1000) == Code::accepted);
    CHECK(lease.heartbeat(token, 1, 2000) == Code::accepted);
    CHECK(lease.heartbeat(token, 2, 3000) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::active);
    CHECK(m::freshness_at(held->observations[0], {"E1", 3000000000}, 1000000000) == m::Freshness::stale);
    CHECK(*store.snapshot() == data); CHECK(store.snapshot() == held);
    CHECK(lease.view().last->accepted_ms == 1000);
    CHECK(lease.forget(3001) == Code::accepted);
    CHECK(!lease.view().last); CHECK(lease.view().presentation == Presentation::waiting);
    CHECK(lease.delta(token, 40, 41, 3002) == Code::snapshot_required);
    CHECK(lease.snapshot(token, "P1", "E1", 40, 3003) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::active);
    CHECK(lease.tick(6000) == Code::accepted); CHECK(!lease.view().alive);
    CHECK(lease.forget(6000) == Code::accepted);
    CHECK(lease.view().presentation == Presentation::empty);
    // This helper does not own/purge the model; the policy composition must do so.
    CHECK(*held == data);
}
void lease05() {
    ProducerLease lease;
    for (const auto& bad : {std::string{}, std::string(257, 'a'), std::string("_bad"), std::string("P space"), std::string("P\x80")}) {
        CHECK(lease.attach(bad, "E", 0).code == Code::invalid);
        CHECK(lease.attach("P", bad, 0).code == Code::invalid);
        CHECK(lease.view().presentation == Presentation::empty);
    }
    auto good = lease.attach(std::string(256, 'a'), "E:1._/-", 0);
    CHECK(good.code == Code::accepted);
    CHECK(lease.heartbeat(good.token, 9, 0) == Code::accepted);
    CHECK(lease.heartbeat(good.token, 8, 1) == Code::sequence_order);
    CHECK(!lease.view().alive); CHECK(lease.view().reason == LeaseReason::invalid);
    // Reattachment stores only the current and last accepted identities.
    for (std::uint64_t i = 0; i < 10000; ++i) {
        auto next = lease.attach("P", "E" + std::to_string(i), i + 1);
        CHECK(next.code == Code::accepted); CHECK(next.token == i + 2);
    }
    ProducerLease boundary;
    const auto max = std::numeric_limits<std::uint64_t>::max();
    const auto token = attach(boundary, max - 3000);
    CHECK(boundary.snapshot(token, "P1", "E1", max, max - 3000) == Code::accepted);
    CHECK(boundary.tick(max - 1) == Code::accepted); CHECK(boundary.view().alive);
    CHECK(boundary.heartbeat(token, max, max) == Code::closed); CHECK(!boundary.view().alive);
    ProducerLease near;
    const auto t = attach(near, max - 1);
    CHECK(near.heartbeat(t, max, max) == Code::accepted); CHECK(near.view().alive);
    CHECK(near.heartbeat(t, 0, max) == Code::sequence_order); // No sequence wrap.
}
void render01() {
    RenderWatch render;
    CHECK(render.view().state == RenderState::idle);
    CHECK(render.issue(41, 100) == Code::accepted);
    CHECK(render.issue(42, 1000) == Code::busy);
    CHECK(render.complete(40, 2000) == Code::invalid);
    CHECK(render.complete(42, 3099) == Code::invalid);
    CHECK(render.view().state == RenderState::awaiting); CHECK(render.view().pending == 41);
    CHECK(render.complete(41, 3100) == Code::closed);
    CHECK(render.view().state == RenderState::stalled);
    CHECK(!render.view().completed); CHECK(render.view().pending == 41);
    CHECK(render.issue(42, 6000) == Code::closed);
    CHECK(render.complete(41, 9000) == Code::closed);
}
void render02() {
    RenderWatch render;
    CHECK(render.complete(0, 0) == Code::invalid);
    CHECK(render.issue(0, 0) == Code::accepted);
    CHECK(render.complete(0, 2999) == Code::accepted);
    CHECK(render.complete(0, 2999) == Code::duplicate);
    CHECK(render.issue(0, 2999) == Code::sequence_order);
    CHECK(render.issue(1, 3000) == Code::accepted);
    CHECK(render.complete(0, 3001) == Code::duplicate);
    ProducerLease producer;
    const auto token = attach(producer, 3000);
    CHECK(producer.snapshot(token, "P1", "E1", 1, 3000) == Code::accepted);
    for (const auto time : {4000U, 5000U, 6000U}) {
        CHECK(producer.heartbeat(token, time, time) == Code::accepted);
        render.tick(time);
    }
    CHECK(producer.view().alive); CHECK(producer.view().presentation == Presentation::active);
    CHECK(render.view().state == RenderState::stalled); CHECK(render.view().completed == 0);
    const auto max = std::numeric_limits<std::uint64_t>::max();
    RenderWatch edge;
    CHECK(edge.issue(max, max - 3000) == Code::accepted);
    CHECK(edge.complete(max, max - 1) == Code::accepted);
    CHECK(edge.issue(0, max) == Code::sequence_order);
}
void retry01() {
    RestartGate gate(0);
    CHECK(gate.start(0) == Code::accepted);
    CHECK(gate.view().restarts_in_window == 0);
    CHECK(gate.failed(Failure::crashed, StopProof::confirmed, 0) == Code::accepted);
    CHECK(gate.view().backoff_ms == 1000);
    CHECK(gate.start(999) == Code::not_due); CHECK(gate.start(1000) == Code::accepted);
    CHECK(gate.view().restarts_in_window == 1);
    CHECK(gate.failed(Failure::crashed, StopProof::confirmed, 1000) == Code::accepted);
    CHECK(gate.view().backoff_ms == 2000);
    CHECK(gate.start(2999) == Code::not_due); CHECK(gate.start(3000) == Code::accepted);
    CHECK(gate.view().restarts_in_window == 2);
    CHECK(gate.failed(Failure::crashed, StopProof::confirmed, 3000) == Code::accepted);
    CHECK(gate.view().backoff_ms == 4000);
    CHECK(gate.start(6999) == Code::not_due); CHECK(gate.start(7000) == Code::accepted);
    CHECK(gate.view().restarts_in_window == 3);
    CHECK(gate.failed(Failure::render_stalled, StopProof::confirmed, 7000) == Code::accepted);
    CHECK(gate.view().state == ChildState::circuit_open);
    CHECK(gate.start(61000) == Code::circuit_open);
    CHECK(gate.start(67000) == Code::circuit_open); CHECK(gate.view().restarts_in_window == 0);
    CHECK(gate.reset(67000) == Code::accepted);
    CHECK(gate.view().last_failure->reason == Failure::render_stalled);
    CHECK(gate.view().last_failure->observed_ms == 7000);
    CHECK(gate.start(67000) == Code::accepted); CHECK(gate.view().restarts_in_window == 0);
}
void retry02() {
    RestartGate gate(0);
    CHECK(gate.start(0) == Code::accepted); CHECK(gate.start(0) == Code::busy);
    CHECK(gate.reset(0) == Code::busy);
    CHECK(gate.failed(Failure::operation_timeout, StopProof::unconfirmed, 0) == Code::accepted);
    CHECK(gate.view().state == ChildState::quarantined);
    CHECK(gate.start(100000) == Code::quarantined); CHECK(gate.reset(100000) == Code::quarantined);
    CHECK(gate.failed(Failure::crashed, StopProof::confirmed, 100000) == Code::quarantined);
    CHECK(gate.view().last_failure->reason == Failure::operation_timeout);
    CHECK(gate.confirm_stopped(100000) == Code::accepted);
    CHECK(gate.confirm_stopped(100000) == Code::closed);
    CHECK(gate.view().state == ChildState::waiting);
    CHECK(gate.start(100000) == Code::accepted); CHECK(gate.view().restarts_in_window == 1);
    CHECK(gate.stopped(StopProof::unconfirmed, 100001) == Code::accepted);
    CHECK(gate.start(100001) == Code::quarantined);
    CHECK(gate.confirm_stopped(100002) == Code::accepted); CHECK(gate.view().state == ChildState::stopped);
    CHECK(gate.start(100003) == Code::closed);
    CHECK(gate.reset(100003) == Code::accepted); CHECK(gate.start(100003) == Code::accepted);
    CHECK(gate.stopped(StopProof::confirmed, 100004) == Code::accepted);
    CHECK(gate.view().state == ChildState::stopped);
}
void retry03() {
    bool rejected = false;
    try { RestartGate invalid(251); } catch (const std::invalid_argument&) { rejected = true; }
    CHECK(rejected);
    RestartGate jitter(250);
    CHECK(jitter.start(0) == Code::accepted);
    CHECK(jitter.failed(Failure::launch_failed, StopProof::confirmed, 0) == Code::accepted);
    CHECK(jitter.view().backoff_ms == 1250);
    CHECK(jitter.start(1249) == Code::not_due); CHECK(jitter.start(1250) == Code::accepted);
    CHECK(jitter.failed(Failure::crashed, StopProof::confirmed, 1250) == Code::accepted);
    CHECK(jitter.view().backoff_ms == 2250);
    CHECK(jitter.start(3500) == Code::accepted);
    CHECK(jitter.failed(Failure::crashed, StopProof::confirmed, 63500) == Code::accepted);
    CHECK(jitter.view().backoff_ms == 1250); CHECK(jitter.view().restarts_in_window == 0);

    RestartGate rolling(0);
    CHECK(rolling.start(0) == Code::accepted);
    CHECK(rolling.failed(Failure::crashed, StopProof::confirmed, 0) == Code::accepted);
    CHECK(rolling.start(1000) == Code::accepted);
    CHECK(rolling.failed(Failure::crashed, StopProof::confirmed, 1000) == Code::accepted);
    CHECK(rolling.start(3000) == Code::accepted);
    CHECK(rolling.failed(Failure::crashed, StopProof::confirmed, 3000) == Code::accepted);
    CHECK(rolling.start(7000) == Code::accepted);
    CHECK(rolling.tick(60999) == Code::accepted); CHECK(rolling.view().restarts_in_window == 3);
    CHECK(rolling.failed(Failure::crashed, StopProof::confirmed, 61000) == Code::accepted);
    CHECK(rolling.view().state == ChildState::waiting); CHECK(rolling.view().restarts_in_window == 2);
    CHECK(rolling.view().backoff_ms == 4000);
    CHECK(rolling.start(65000) == Code::accepted); CHECK(rolling.view().restarts_in_window == 2);
    const auto max = std::numeric_limits<std::uint64_t>::max();
    RestartGate edge(0);
    CHECK(edge.start(max - 1000) == Code::accepted);
    CHECK(edge.failed(Failure::crashed, StopProof::confirmed, max - 1000) == Code::accepted);
    CHECK(edge.start(max - 1) == Code::not_due); CHECK(edge.start(max) == Code::accepted);
    CHECK(edge.view().restarts_in_window == 1);
}
void clock_fault() {
    ProducerLease lease;
    const auto token = attach(lease);
    CHECK(lease.snapshot(token, "P1", "E1", 40, 100) == Code::accepted);
    CHECK(lease.tick(99) == Code::clock_fault); CHECK(!lease.view().alive);
    CHECK(lease.view().reason == LeaseReason::clock_fault);
    CHECK(lease.attach("P1", "E2", 1000).code == Code::clock_fault);
    CHECK(lease.heartbeat(token, 1, 1000) == Code::clock_fault);
    CHECK(lease.forget(1000) == Code::clock_fault); CHECK(!lease.view().last);
    RenderWatch render;
    CHECK(render.issue(40, 100) == Code::accepted);
    CHECK(render.complete(40, 99) == Code::clock_fault);
    CHECK(render.issue(41, 1000) == Code::clock_fault); CHECK(!render.view().completed);
    RestartGate gate(0);
    CHECK(gate.start(100) == Code::accepted);
    CHECK(gate.failed(Failure::crashed, StopProof::confirmed, 99) == Code::clock_fault);
    CHECK(gate.reset(1000) == Code::clock_fault); CHECK(gate.start(1000) == Code::clock_fault);
    CHECK(!gate.view().last_failure); CHECK(gate.view().state == ChildState::clock_fault);
}
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("one case ID required");
        const std::string id = argv[1];
        if (id == "LEASE-01") lease01(); else if (id == "LEASE-02") lease02();
        else if (id == "LEASE-03") lease03(); else if (id == "LEASE-04") lease04();
        else if (id == "LEASE-05") lease05(); else if (id == "RENDER-01") render01();
        else if (id == "RENDER-02") render02(); else if (id == "RETRY-01") retry01();
        else if (id == "RETRY-02") retry02(); else if (id == "RETRY-03") retry03();
        else if (id == "RECOVERY-CLOCK") clock_fault();
        else if(id=="TRANSACTION-DEADLINE"){
            TransactionWatch watch;CHECK(watch.started(1,100)==Code::accepted);CHECK(watch.tick(5099)==Code::accepted);
            CHECK(watch.finished(1,5100)==Code::closed);CHECK(watch.pending()==1);CHECK(watch.started(2,6000)==Code::closed);
            TransactionWatch good;CHECK(good.started(1,100)==Code::accepted);CHECK(good.finished(1,5099)==Code::accepted);
            CHECK(!good.pending());CHECK(good.started(2,5099)==Code::accepted);CHECK(good.finished(2,5100)==Code::accepted);
            const auto max=std::numeric_limits<std::uint64_t>::max();TransactionWatch edge;CHECK(edge.started(1,max-5000)==Code::accepted);CHECK(edge.tick(max)==Code::closed);
        }else if(id=="TRANSACTION-ORDER"){
            for(unsigned mode=0;mode<4;++mode){TransactionWatch watch;
                if(mode==0)CHECK(watch.started(0,100)==Code::invalid);
                if(mode==1){CHECK(watch.started(1,100)==Code::accepted);CHECK(watch.started(2,101)==Code::invalid);}
                if(mode==2){CHECK(watch.started(1,100)==Code::accepted);CHECK(watch.finished(2,101)==Code::invalid);}
                if(mode==3){CHECK(watch.started(1,100)==Code::accepted);CHECK(watch.finished(1,101)==Code::accepted);CHECK(watch.started(1,102)==Code::invalid);}
                CHECK(watch.tick(10000)==Code::closed);
            }
            TransactionWatch clock;CHECK(clock.started(1,100)==Code::accepted);CHECK(clock.tick(99)==Code::clock_fault);CHECK(clock.finished(1,101)==Code::clock_fault);
        }else throw std::runtime_error("unknown case ID");
        std::cout << id << ": pass\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
