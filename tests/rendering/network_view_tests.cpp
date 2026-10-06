#include "network_view.hpp"
#include "network_publication.hpp"
#include <cstring>
#include <fstream>
#include <iostream>
#include <limits>
#include <locale>
#include <stdexcept>

namespace v = syspane::rendering; namespace n = syspane::runtime;
namespace r = syspane::recovery; namespace p = syspane::protocol;
namespace m = syspane::model; namespace c = syspane::configuration;
using p::Json;
void need(bool value, const char* why = "fixed presentation expectation failed") { if (!value) throw std::runtime_error(why); }
c::Policy policy(std::uint64_t revision = 7, bool allow = true) {
    c::Policy result; result.available = allow; result.revision = revision;
    result.disclosure[{"desktop", "desktop"}] = {"operational"}; result.disclosure[{"desktop", "accessibility"}] = {"operational"}; return result;
}
m::Tick tick(std::uint64_t value, const std::string& epoch = "epoch:1") { return {epoch, value, "clock:1", "scope:1"}; }
p::TelemetryBinding binding(const std::string& epoch = "epoch:1", std::uint64_t revision = 7) {
    return {{1, p::frame_limit, {{"telemetry", "0.2.0"}, {"snapshot", "0.2.0"}, {"observation", "0.2.0"}},
        {"telemetry.snapshot", "telemetry.measured-time"}}, "D", epoch, "producer:network", "S", "desktop", "operational", revision,
        p::TelemetryDirection::producer_to_consumer, "0.2.0", "clock:1", "scope:1"};
}
Json document(bool rates = true) {
    n::NetworkState state("epoch:1", "clock:1", "scope:1"); state.demand(1);
    need(state.commit(1, 0, {syspane::platform::NetworkCode::success, 0, {{9, 9, 6, syspane::platform::NetworkCounters{100, 200}}}}, tick(100), tick(100)) == n::NetworkStateCode::accepted);
    if (rates) need(state.commit(1, 0, {syspane::platform::NetworkCode::success, 0, {{9, 9, 6, syspane::platform::NetworkCounters{130, 260}}}}, tick(110), tick(110)) == n::NetworkStateCode::accepted);
    return n::network_document(*state.sample(), rates ? 2 : 1, "2026-10-06T00:00:00Z", "2026-10-06T00:00:01Z", true);
}
struct Fixture {
    r::DataView view{{true, "desktop", {"desktop"}}, policy(), "desktop", "operational", n::network_metrics()};
    p::TelemetryBinding link = binding();
    std::uint64_t token = view.attach_wire(link, 0).token;
    v::NetworkSelection selection{"producer:network", "epoch:1", "network:interface:1"};
    void receive(Json doc, std::uint64_t now = 1, std::uint64_t measured = 110) {
        const auto record = doc["generation"].get<std::string>();
        Json body{{"schema_version", "0.2.0"}, {"subscription_id", "S"}, {"producer_id", "producer:network"},
            {"record_id", "record:" + record}, {"policy_revision", std::to_string(link.policy_revision)}, {"clock_id", "clock:1"}, {"snapshot", std::move(doc)}};
        const auto bytes = p::encode_telemetry({"snapshot", "D", link.epoch, body.dump(), body}, link);
        need(view.receive(token, link.policy_revision, bytes, now, tick(measured, link.epoch)).code == r::DataCode::accepted, "fixture import");
    }
    void check(const std::function<void(const v::NetworkFrame&)>& expected, std::uint64_t now = 2, std::uint64_t measured = 111, std::size_t limit = 4096) {
        unsigned calls = 0;
        v::project_network(view, selection, now, tick(measured, link.epoch), [&](const auto& frame) { ++calls; expected(frame); }, limit);
        need(calls == 1, "exactly one callback");
    }
};
void empty(const v::NetworkFrame& frame, v::NetworkViewCode code) {
    need(frame.code == code && frame.selected.producer.empty() && frame.selected.epoch.empty() && frame.selected.entity.empty() && frame.generation.empty());
    need(frame.presentation == r::Presentation::empty && frame.reason == r::LeaseReason::none && frame.accounted_bytes == 0);
    for (const auto& field : frame.fields) need(!field.value && field.unit.empty() && field.error_code.empty() && !field.measured_at && !field.observed_at && !field.age_ns && !field.interval_ns);
}
void values() {
    Fixture f; auto doc = document(false);
    doc["observations"][0]["value"]["data"] = "18446744073709551615";
    doc["observations"][1]["value"]["data"] = "0";
    f.receive(doc, 1, 100);
    f.check([](const auto& frame) {
        need(frame.code == v::NetworkViewCode::ready && frame.generation == "1" && frame.selected.entity == "network:interface:1");
        need(frame.presentation == r::Presentation::active && frame.reason == r::LeaseReason::none);
        need(frame.fields[0].value == "18446744073709551615" && frame.fields[1].value == "0");
        need(frame.fields[0].unit == "byte" && frame.fields[0].age_ns == 0);
        for (unsigned i = 2; i < 4; ++i) need(!frame.fields[i].value && !frame.fields[i].age_ns && !frame.fields[i].interval_ns && frame.fields[i].acquisition == m::Acquisition::pending);
    }, 2, 100);
    Fixture rates; rates.receive(document()); rates.check([](const auto& frame) {
        need(frame.fields[2].value == "3000000000.000" && frame.fields[3].value == "6000000000.000");
        need(frame.fields[2].unit == "byte/second" && frame.fields[2].interval_ns == 10 && frame.fields[2].origin == m::Origin::derived);
        need(frame.fields[0].observed_at->seconds == 1791244800 && frame.fields[0].attempted_at.seconds == 1791244801);
    });
}
struct OddLocale : std::numpunct<char> { char do_decimal_point() const override { return ','; } char do_thousands_sep() const override { return '_'; } std::string do_grouping() const override { return "\3"; } };
void format(const char* path) {
    std::ifstream file(path); Json vectors; file >> vectors;
    const auto original = std::locale(); std::locale::global(std::locale(original, new OddLocale));
    for (const auto& vector : vectors) {
        const auto bits = std::stoull(vector["binary64_hex"].get<std::string>(), nullptr, 16); double value = 0; std::memcpy(&value, &bits, sizeof(value));
        Fixture f; auto doc = document(); doc["observations"][2]["value"]["data"] = value; f.receive(doc);
        f.check([&](const auto& frame) { need(frame.code == v::NetworkViewCode::ready && frame.fields[2].value == vector["expected"].get<std::string>(), "independent exact rational formatting vector"); });
    }
    std::locale::global(original);
}
void states() {
    Fixture f; f.receive(document());
    f.check([](const auto& frame) { need(frame.fields[0].effective == m::Freshness::current && frame.fields[0].age_ns == 2999999999ULL); }, 2, 3000000109ULL);
    need(f.view.heartbeat(f.token, 7, 0, 3) == r::DataCode::accepted);
    f.check([](const auto& frame) { need(frame.presentation == r::Presentation::active && frame.fields[0].reported == m::Freshness::current && frame.fields[0].effective == m::Freshness::stale && frame.fields[0].measured_at->nanoseconds == 110); }, 4, 3000000110ULL);
    Fixture loss; loss.receive(document()); loss.view.disconnect(loss.token, 7, 2);
    loss.check([](const auto& frame) { need(frame.presentation == r::Presentation::retained && frame.reason == r::LeaseReason::disconnected && frame.fields[0].effective == m::Freshness::current && frame.fields[0].value == "130"); }, 3);
    v::project_network_retained(loss.view, loss.selection, 4, [](const auto& frame) { need(frame.code == v::NetworkViewCode::ready && frame.presentation == r::Presentation::retained && frame.fields[0].value == "130" && !frame.fields[0].age_ns && frame.fields[0].effective == m::Freshness::stale); });
    v::project_network_retained(f.view, f.selection, 5, [](const auto& frame) { empty(frame, v::NetworkViewCode::unavailable); });
    Fixture failed; auto doc = document();
    for (auto& field : doc["observations"]) { field["acquisition"] = "failed"; field["freshness"] = "stale"; field["error"] = {{"code", "network.acquisition_failed"}, {"message", "must not enter projection"}, {"retryable", true}}; }
    failed.receive(doc); failed.check([](const auto& frame) { need(frame.fields[0].value == "130" && frame.fields[0].acquisition == m::Acquisition::failed && frame.fields[0].effective == m::Freshness::stale && frame.fields[0].error_code == "network.acquisition_failed" && frame.fields[0].measured_at->nanoseconds == 110); });
}
void selection() {
    Fixture f; f.receive(document());
    const auto original = f.selection;
    for (unsigned i = 0; i < 3; ++i) { f.selection = original; (i == 0 ? f.selection.producer : i == 1 ? f.selection.epoch : f.selection.entity) = "different";
        f.check([](const auto& frame) { empty(frame, v::NetworkViewCode::selection_missing); }); }
    f.selection = original; f.view.disconnect(f.token, 7, 3); f.link = binding("epoch:2"); f.token = f.view.attach_wire(f.link, 4).token;
    f.check([](const auto& frame) { need(frame.code == v::NetworkViewCode::ready && frame.selected.epoch == "epoch:1" && frame.presentation == r::Presentation::retained && !frame.fields[0].age_ns && frame.fields[0].effective == m::Freshness::stale); }, 5, 120);
    auto doc = document(); doc["producer_epoch"] = "epoch:2"; for (auto& field : doc["observations"]) field["producer_epoch"] = "epoch:2"; f.receive(doc, 6, 120);
    f.check([](const auto& frame) { empty(frame, v::NetworkViewCode::selection_missing); }, 7, 121);
    f.selection.epoch = "epoch:2"; f.check([](const auto& frame) { need(frame.code == v::NetworkViewCode::ready && frame.selected.epoch == "epoch:2"); }, 8, 122);
    doc["generation"] = "3"; doc["entities"] = Json::array(); doc["observations"] = Json::array(); f.receive(doc, 9, 123);
    f.check([](const auto& frame) { empty(frame, v::NetworkViewCode::selection_missing); }, 10, 124);
}
void bounds() {
    Fixture f; f.receive(document()); std::size_t exact = 0;
    f.check([&](const auto& frame) { need(frame.code == v::NetworkViewCode::ready); exact = frame.accounted_bytes; });
    f.check([](const auto& frame) { need(frame.code == v::NetworkViewCode::ready); }, 2, 111, exact);
    f.check([](const auto& frame) { empty(frame, v::NetworkViewCode::capacity); }, 2, 111, exact - 1);
    for (unsigned mode = 0; mode < 4; ++mode) {
        Fixture bad; auto doc = document();
        if (mode == 0) doc["observations"].erase(3);
        if (mode == 1) doc["entities"][0]["kind"] = "different";
        if (mode == 2) doc["sources"][0]["kind"] = "different";
        if (mode == 3) { doc["sources"].push_back({{"id", "provider:other"}, {"kind", "native.network.counters"}, {"scope", "host:local"}}); doc["observations"][3]["source_id"] = "provider:other"; }
        bad.receive(doc); bad.check([](const auto& frame) { empty(frame, v::NetworkViewCode::invalid); });
    }
}
void lifetime() {
    Fixture f; f.check([](const auto& frame) { empty(frame, v::NetworkViewCode::waiting); }); f.receive(document(), 3);
    f.view.policy(policy(8, false), 4); f.selection.entity = "missing";
    f.check([](const auto& frame) { empty(frame, v::NetworkViewCode::restricted); }, 5, 111, 0);
    v::project_network_retained(f.view, f.selection, 5, [](const auto& frame) { empty(frame, v::NetworkViewCode::restricted); });
    f.view.policy(policy(9), 6); f.check([](const auto& frame) { empty(frame, v::NetworkViewCode::waiting); }, 7);
    Fixture clock; clock.receive(document());
    v::project_network(clock.view, clock.selection, 2, {"epoch:1", 111, "wrong", "scope:1"}, [](const auto& frame) { empty(frame, v::NetworkViewCode::unavailable); });
    clock.check([](const auto& frame) { empty(frame, v::NetworkViewCode::unavailable); }, 3);
    v::project_network_retained(clock.view, clock.selection, 4, [](const auto& frame) { need(frame.code == v::NetworkViewCode::ready && frame.presentation == r::Presentation::retained && !frame.fields[0].age_ns && frame.fields[0].effective == m::Freshness::stale); });
    Fixture borrow; borrow.receive(document());
    borrow.check([&](const auto&) { bool rejected = false; try { borrow.view.status(2); } catch (const std::logic_error&) { rejected = true; } need(rejected, "DataView reentry must fail"); });
    unsigned calls = 0; bool propagated = false;
    try { v::project_network(borrow.view, borrow.selection, 3, tick(112), [&](const auto&) { ++calls; throw std::bad_alloc(); }); }
    catch (const std::bad_alloc&) { propagated = true; }
    need(propagated && calls == 1, "consumer exception delivered twice");
    borrow.check([](const auto& frame) { need(frame.code == v::NetworkViewCode::ready); }, 4, 113);
}
int main(int argc, char** argv) {
    try {
        need(argc == 3); const std::string name = argv[1];
        if (name == "NVIEW-VALUES") values(); else if (name == "NVIEW-FORMAT") format(argv[2]);
        else if (name == "NVIEW-STATES") states(); else if (name == "NVIEW-SELECTION") selection();
        else if (name == "NVIEW-BOUNDS") bounds(); else if (name == "NVIEW-LIFETIME") lifetime(); else return 2;
        std::cout << name << ": pass\n"; return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
