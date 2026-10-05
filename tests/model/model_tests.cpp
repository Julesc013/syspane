#include "state.hpp"

#include <algorithm>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

using namespace syspane::model;

namespace {
void require(bool condition, const char* expression, int line) {
    if (!condition) throw std::runtime_error(std::string(expression) + " at line " + std::to_string(line));
}
#define CHECK(expression) require(static_cast<bool>(expression), #expression, __LINE__)

Store store(Limits limits = {}) {
    return Store("P", "E1", {{"throughput", "B/s", ValueKind::uint64},
        {"serial", "1", ValueKind::string}, {"load", "1", ValueKind::number}}, limits);
}
Snapshot sample(std::uint64_t generation = 7, std::uint64_t value = 10) {
    Observation o;
    o.entity_id = "A1"; o.field = "throughput"; o.source_id = "S1";
    o.value = value; o.unit = "B/s"; o.support = Support::supported;
    o.acquisition = Acquisition::success; o.freshness = Freshness::current;
    o.presence = Presence::present; o.observed_at = UtcTime{1791158400, 0};
    o.attempted_at = *o.observed_at; o.measured_at = Tick{"E1", 1000000000};
    return {"P", "E1", generation, {{"A1", "network_interface", "Ethernet", generation}},
            {{"S1", "fixture", "local"}}, {}, {o}};
}
std::uint64_t value(const std::shared_ptr<const Snapshot>& s) { return std::get<std::uint64_t>(s->observations.at(0).value); }
void initial(Store& s, std::uint64_t v = 10) { CHECK(s.publish({"initial", {}, sample(7, v)}).code == Code::accepted); }

void state01() {
    auto s = store(); initial(s);
    auto next = sample(8, 20); next.entities.push_back(next.entities[0]);
    CHECK(s.publish({"duplicate", {}, next}).code == Code::duplicate_entity);
    CHECK(s.snapshot()->generation == 7); CHECK(value(s.snapshot()) == 10);
}
void state02() {
    auto s = store(); initial(s);
    auto gone = sample(8); gone.entities.clear(); gone.observations.clear();
    CHECK(s.publish({"removed", 7, gone}).code == Code::accepted);
    auto replaced = sample(9, 20); replaced.entities[0].id = "A2"; replaced.observations[0].entity_id = "A2";
    CHECK(s.publish({"replacement", 8, replaced}).code == Code::accepted);
    auto late = replaced; late.generation = 10; late.observations.push_back(sample(10, 99).observations[0]);
    CHECK(s.publish({"late", 9, late}).code == Code::retired_identity);
    CHECK(s.snapshot()->generation == 9); CHECK(value(s.snapshot()) == 20);
    CHECK(s.snapshot()->entities[0].id == "A2");
    CHECK(s.publish({"reuse", 9, sample(10, 99)}).code == Code::retired_identity);
}
void state03() {
    auto s = store(); initial(s);
    const auto result = s.publish({"delta", 6, sample(8, 20)});
    CHECK(result.code == Code::missing_base); CHECK(result.snapshot_required);
    CHECK(s.snapshot()->generation == 7); CHECK(value(s.snapshot()) == 10);
}
void state04() {
    auto s = store(); initial(s);
    Publication request{"R", 7, sample(8, 10)};
    CHECK(s.publish(request).code == Code::accepted);
    CHECK(s.publish(request).code == Code::duplicate);
    request.next.observations[0].value = std::uint64_t{11};
    CHECK(s.publish(request).code == Code::conflict);
    CHECK(s.snapshot()->generation == 8); CHECK(value(s.snapshot()) == 10);
}
void state05() {
    auto s = store(); initial(s);
    const auto old_reader = s.snapshot();
    CHECK(s.publish({"new", 7, sample(8, 20)}).code == Code::accepted);
    auto broken = sample(9, 30); broken.relationships.push_back({"A1", "A2", "lower_layer"});
    CHECK(s.publish({"broken", 8, broken}).code == Code::dangling_relationship);
    CHECK(old_reader->generation == 7); CHECK(value(old_reader) == 10);
    CHECK(s.snapshot()->generation == 8); CHECK(value(s.snapshot()) == 20);
}
void validity01() {
    auto s = store(); initial(s, 42);
    auto failed = sample(8); auto& attempt = failed.observations[0];
    attempt.value = std::monostate{}; attempt.observed_at.reset(); attempt.measured_at.reset();
    attempt.acquisition = Acquisition::failed; attempt.attempted_at = {1791158401, 0};
    attempt.error = Error{"fixture.unavailable", "source unavailable", true};
    CHECK(s.publish({"failed", 7, failed}).code == Code::accepted);
    const auto& o = s.snapshot()->observations[0];
    CHECK(std::get<std::uint64_t>(o.value) == 42); CHECK(o.observed_at->seconds == 1791158400);
    CHECK(o.attempted_at.seconds == 1791158401); CHECK(o.acquisition == Acquisition::failed);
    CHECK(o.freshness == Freshness::stale); CHECK(o.presence == Presence::present);
    CHECK(o.error->code == "fixture.unavailable");
    CHECK(s.publish({"failed", 7, failed}).code == Code::duplicate);
}
void validity02() {
    auto zero = store(); initial(zero, 0);
    CHECK(value(zero.snapshot()) == 0); CHECK(zero.snapshot()->observations[0].acquisition == Acquisition::success);
    auto s = store(); auto next = sample(); auto& o = next.observations[0];
    o.value = std::monostate{}; o.observed_at.reset(); o.measured_at.reset();
    o.support = Support::unsupported; o.acquisition = Acquisition::disabled;
    CHECK(s.publish({"unsupported", {}, next}).code == Code::accepted);
    CHECK(s.snapshot()->observations[0].value.index() == 0);
    CHECK(s.snapshot()->observations[0].freshness == Freshness::not_applicable);
    next.generation = 8; o.support = Support::supported; o.acquisition = Acquisition::pending;
    CHECK(s.publish({"pending", 7, next}).code == Code::accepted);
    CHECK(s.snapshot()->observations[0].value.index() == 0);
    CHECK(s.snapshot()->observations[0].acquisition == Acquisition::pending);
    auto retained = store(); initial(retained, 42);
    auto gone = sample(8); gone.entities.clear(); gone.observations.clear();
    CHECK(retained.publish({"removed", 7, gone}).code == Code::accepted);
    const auto history = retained.retired_observations("A1");
    CHECK(history.size() == 1); CHECK(std::get<std::uint64_t>(history[0].value) == 42);
    CHECK(history[0].presence == Presence::absent); CHECK(history[0].freshness == Freshness::stale);
    CHECK(retained.snapshot()->observations.empty());
}
void clock01() {
    auto before = sample().observations[0]; auto after = before;
    before.value = std::uint64_t{100}; after.value = std::uint64_t{300};
    after.observed_at->seconds -= 3600; after.measured_at->nanoseconds = 3000000000;
    const auto elapsed = interval_ns(*before.measured_at, *after.measured_at);
    CHECK(elapsed && *elapsed == 2000000000);
    CHECK((std::get<std::uint64_t>(after.value) - std::get<std::uint64_t>(before.value)) * 1000000000 / *elapsed == 100);
}
void clock02() {
    CHECK(!interval_ns({"E1", 3000000000}, {"E2", 1000000000}));
    CHECK(!interval_ns({"E1", 3000000000}, {"E1", 1000000000}));
    CHECK(!interval_ns({"E1", 3}, {"E1", 3}));
    CHECK(interval_ns({"E2", 1000000000}, {"E2", 3000000000}) == 2000000000);
}
void bounds01() {
    Limits limits; limits.entities = 1; auto s = store(limits); initial(s);
    auto too_many = sample(8); too_many.entities.push_back({"A2", "network_interface", "second", 8});
    CHECK(s.publish({"full", 7, too_many}).code == Code::capacity);
    CHECK(s.snapshot()->generation == 7);
    const auto maximum = std::numeric_limits<std::uint64_t>::max();
    CHECK(s.publish({"maximum", 7, sample(maximum, maximum)}).code == Code::accepted);
    CHECK(s.snapshot()->generation == maximum); CHECK(value(s.snapshot()) == maximum);
    CHECK(s.publish({"wrapped", maximum, sample(0, 0)}).code == Code::generation_order);
    CHECK(value(s.snapshot()) == maximum);
}
void bounds02() {
    Limits limits; limits.replay_records = 2; auto s = store(limits); initial(s);
    const Publication request{"R", 7, sample(8, 20)};
    CHECK(s.publish(request).code == Code::accepted);
    CHECK(s.publish({"full", 8, sample(9, 30)}).code == Code::capacity);
    CHECK(s.publish(request).code == Code::duplicate);
    auto changed = request; changed.next.generation = 9;
    CHECK(s.publish(changed).code == Code::conflict); CHECK(s.snapshot()->generation == 8);
}
void bounds03() {
    Limits limits; limits.retired_entities = 0; auto s = store(limits); initial(s);
    auto removed = sample(8); removed.entities.clear(); removed.observations.clear();
    CHECK(s.publish({"full", 7, removed}).code == Code::capacity);
    CHECK(s.snapshot()->generation == 7); CHECK(s.retired_observations("A1").empty());
    limits = Limits{}; limits.candidate_bytes = 1; auto too_small = store(limits);
    CHECK(too_small.publish({"initial", {}, sample()}).code == Code::capacity); CHECK(!too_small.snapshot());
    limits = Limits{}; limits.retained_bytes = 1; auto no_retention = store(limits);
    CHECK(no_retention.publish({"initial", {}, sample()}).code == Code::capacity); CHECK(!no_retention.snapshot());
}
void observation01() {
    auto s = store(); initial(s);
    auto bad = sample(8); bad.observations[0].source_id = "missing";
    CHECK(s.publish({"bad", 7, bad}).code == Code::invalid_observation);
    bad = sample(8); bad.observations[0].unit = "wrong";
    CHECK(s.publish({"bad", 7, bad}).code == Code::invalid_observation);
    bad = sample(8); bad.observations[0].field = "load"; bad.observations[0].unit = "1";
    bad.observations[0].value = std::numeric_limits<double>::quiet_NaN();
    CHECK(s.publish({"bad", 7, bad}).code == Code::invalid_observation);
    bad = sample(8); bad.observations.push_back(bad.observations[0]);
    CHECK(s.publish({"bad", 7, bad}).code == Code::duplicate_observation);
    bad = sample(8); bad.observations[0].acquisition = Acquisition::denied;
    CHECK(s.publish({"bad", 7, bad}).code == Code::invalid_observation);
    bad.observations[0].error = Error{"denied", "\x1b[31munsafe", false};
    CHECK(s.publish({"bad", 7, bad}).code == Code::invalid_observation);
    CHECK(s.snapshot()->generation == 7); CHECK(value(s.snapshot()) == 10);
    CHECK(s.publish({"bad", 7, sample(8, 20)}).code == Code::accepted);
}
void epoch01() {
    auto s = store(); initial(s);
    auto next = sample(8); next.epoch = "E2";
    const auto wrong = s.publish({"new-epoch", 7, next});
    CHECK(wrong.code == Code::wrong_epoch); CHECK(wrong.snapshot_required);
    CHECK(s.snapshot()->epoch == "E1"); CHECK(s.snapshot()->generation == 7);
    Store restarted("P", "E2", {{"throughput", "B/s", ValueKind::uint64}});
    next.observations[0].measured_at->epoch = "E2";
    CHECK(restarted.publish({"initial", 7, next}).code == Code::missing_base);
    CHECK(restarted.publish({"initial", {}, next}).code == Code::accepted);
    CHECK(restarted.snapshot()->epoch == "E2");
}
void freshness01() {
    auto o = sample().observations[0];
    CHECK(freshness_at(o, {"E1", 1999999999}, 1000000000) == Freshness::current);
    CHECK(freshness_at(o, {"E1", 2000000000}, 1000000000) == Freshness::stale);
    CHECK(freshness_at(o, {"E2", 1999999999}, 1000000000) == Freshness::stale);
    CHECK(freshness_at(o, {"E1", 999999999}, 1000000000) == Freshness::stale);
    CHECK(freshness_at(o, {"E1", 9000000000}, {}) == Freshness::current);
    o.acquisition = Acquisition::failed;
    CHECK(freshness_at(o, {"E1", 1000000000}, {}) == Freshness::stale);
}
} // namespace

int main(int argc, char** argv) {
    const std::pair<const char*, void(*)()> cases[] = {
        {"STATE-01", state01}, {"STATE-02", state02}, {"STATE-03", state03}, {"STATE-04", state04}, {"STATE-05", state05},
        {"VALIDITY-01", validity01}, {"VALIDITY-02", validity02}, {"CLOCK-01", clock01}, {"CLOCK-02", clock02},
        {"BOUNDS-01", bounds01}, {"BOUNDS-02", bounds02}, {"BOUNDS-03", bounds03},
        {"OBSERVATION-01", observation01}, {"EPOCH-01", epoch01}, {"FRESHNESS-01", freshness01}
    };
    if (argc != 2) { std::cerr << "one case ID required\n"; return 2; }
    for (const auto& test : cases) if (test.first == std::string(argv[1])) {
        try { test.second(); std::cout << test.first << ": pass\n"; return 0; }
        catch (const std::exception& e) { std::cerr << test.first << ": " << e.what() << '\n'; return 1; }
    }
    std::cerr << "unknown case\n";
    return 2;
}
