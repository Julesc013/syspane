#include "wire.hpp"
#include "ledger.hpp"
#include "policy.hpp"
#include "session.hpp"
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <vector>

using namespace syspane::protocol;
namespace cfg = syspane::configuration;
namespace {
void check(bool condition, const char* why) { if (!condition) throw std::runtime_error(why); }
void fails(const std::function<void()>& call, const char* code) {
    try { call(); } catch (const Error& error) {
        check(std::string(error.what()) == code, error.what());
        return;
    }
    throw std::runtime_error(std::string("expected error: ") + code);
}
Json hello() {
    return {{"wire_major", 0}, {"wire_minor", 1}, {"role", "console"}, {"producer_epoch", "client:1"},
        {"max_frame_bytes", 1048576}, {"document_versions", Json::array({{{"document", "command"}, {"version", "0.2.0"}}})},
        {"required_features", Json::array()}, {"optional_features", Json::array({"settings.preview"})}};
}
Json command() {
    return {{"schema_version", "0.2.0"}, {"request_id", "R"}, {"expected_revision", "40"}, {"policy_generation", "7"},
        {"intent", "preview"}, {"operations", Json::array({{{"op", "settings.set"}, {"path", "sampling.resources_ms"}, {"value", 1000}}})}};
}
cfg::Authority authority() { return {true, "console", {"console"}}; }
cfg::Policy policy() { cfg::Policy p; p.available = true; p.revision = 7; return p; }
void decision(const Json& cmd, const cfg::Authority& a, const cfg::Policy& p, const char* outcome, const char* code) {
    const auto d = cfg::preview(cmd, a, p, 40);
    check(d.outcome == outcome && d.code == code, "incorrect preview decision");
}
void frame01() {
    const std::string first = R"({"one":1})", second = R"({"two":2})";
    const auto input = frame(first) + frame(second);
    for (std::size_t split = 0; split <= input.size(); ++split) {
        Framer decoder;
        std::vector<std::string> output;
        const auto take = [&](std::string_view value) { output.emplace_back(value); };
        decoder.feed(std::string_view(input).substr(0, split), 0, take);
        decoder.feed(std::string_view(input).substr(split), 1, take);
        decoder.eof();
        check(output == std::vector<std::string>{first, second}, "fragmented/coalesced frame differs");
    }
    Framer decoder;
    std::vector<std::string> output;
    for (const auto byte : input) decoder.feed(std::string_view(&byte, 1), 0, [&](auto value) { output.emplace_back(value); });
    check(output == std::vector<std::string>{first, second}, "byte-wise decode differs");
    const std::string maximum(frame_limit, 'x');
    Framer boundary;
    boundary.feed(frame(maximum), 0, [&](auto value) { check(value == maximum, "maximum frame altered"); });
}
void frame02() {
    const auto take = [](std::string_view) { throw std::runtime_error("unexpected accepted frame"); };
    for (const auto& prefix : {std::string(4, '\0'), std::string("\0\x10\0\1", 4)}) {
        Framer decoder;
        fails([&] { decoder.feed(prefix, 0, take); }, "frame.length");
        check(decoder.buffered() <= 4, "allocated rejected payload");
        fails([&] { decoder.feed(frame("{}"), 1, take); }, "frame.closed");
    }
    const auto complete = frame("{}");
    for (std::size_t length = 1; length < complete.size(); ++length) {
        Framer decoder;
        decoder.feed(std::string_view(complete).substr(0, length), 0, take);
        fails([&] { decoder.eof(); }, "frame.truncated");
    }
    Framer closed;
    closed.eof();
    fails([&] { closed.feed({}, 0, take); }, "frame.closed");
    Framer callback;
    fails([&] { callback.feed(frame("{}"), 0, [](auto) { throw Error("fixture.reject"); }); }, "fixture.reject");
    fails([&] { callback.tick(0); }, "frame.closed");
    Framer negotiated;
    unsigned count = 0;
    fails([&] { negotiated.feed(frame("hi") + frame("big"), 0, [&](auto) { ++count; negotiated.restrict_limit(2); }); }, "frame.length");
    check(count == 1 && negotiated.buffered() <= 4, "coalesced negotiated limit not enforced before allocation");
}
void frame03() {
    auto input = frame("{}");
    Framer decoder;
    const auto take = [](auto) { throw std::runtime_error("unexpected frame"); };
    decoder.feed(std::string_view(input).substr(0, 1), 10, take);
    decoder.feed(std::string_view(input).substr(1, 1), 5009, take);
    fails([&] { decoder.tick(5010); }, "frame.timeout");
    Framer accepted;
    unsigned count = 0;
    accepted.feed(std::string_view(input).substr(0, 1), 10, [&](auto) { ++count; });
    accepted.feed(std::string_view(input).substr(1), 5009, [&](auto) { ++count; });
    accepted.tick(5010);
    check(count == 1, "frame before deadline rejected");
    fails([&] { accepted.tick(5000); }, "clock.regressed");
}
void json01() {
    fails([] { parse(R"({"a":1,"\u0061":2})"); }, "json.duplicate_key");
    fails([] { parse(R"({"a":{"b":1,"b":2}})"); }, "json.duplicate_key");
    check(parse(R"({"a":{"b":1},"c":{"b":2}})").size() == 2, "independent keys conflated");
    for (const auto& input : {std::string("{\"a\":\"\xc0\xaf\"}"), std::string(R"({"n":NaN})"),
                             std::string(R"({"n":1e9999})"), std::string(R"({"s":"\ud800"})")})
        fails([&] { parse(input); }, "json.invalid");
    fails([] { parse("\xef\xbb\xbf{}"); }, "json.encoding");
    fails([] { parse("{}\n"); }, "json.encoding");
    std::string deep = "0";
    for (unsigned n = 0; n < 32; ++n) deep = "[" + deep + "]";
    check(parse(deep).is_array(), "valid boundary depth rejected");
    fails([&] { parse("[" + deep + "]"); }, "json.depth");
    Json wide = Json::array();
    for (unsigned n = 0; n < 16383; ++n) wide.push_back(n);
    check(parse(wide.dump()).size() == 16383, "valid node boundary rejected");
    wide.push_back(0);
    fails([&] { parse(wide.dump()); }, "json.nodes");
    check(decimal("18446744073709551615") == std::numeric_limits<std::uint64_t>::max(), "uint64 maximum changed");
    check(!decimal("18446744073709551616") && !decimal("01") && !decimal("-1"), "invalid uint64 accepted");
}
void wire01() {
    const std::string bytes = "{ \"body\":{ \"request_id\" : \"R\" }, \"producer_epoch\":\"E\",\"connection_id\":\"C\",\"type\":\"result.get\" }";
    const auto message = decode(bytes);
    check(message.body_bytes == "{ \"request_id\" : \"R\" }", "raw request identity lost");
    check(message.connection_id == "C" && message.producer_epoch == "E", "envelope identity changed");
    auto envelope = Json{{"type", "hello"}, {"body", hello()}};
    check(decode(envelope.dump()).type == "hello", "hello not parsed");
    envelope["approved"] = true;
    fails([&] { decode(envelope.dump()); }, "envelope.invalid");
    envelope.erase("approved"); envelope["type"] = "unknown";
    fails([&] { decode(envelope.dump()); }, "message.unknown");
    envelope["type"] = "command";
    fails([&] { decode(envelope.dump()); }, "envelope.invalid");
    auto control = Json{{"type", "heartbeat"}, {"connection_id", "C"}, {"producer_epoch", "E"}, {"body", {{"sequence", "18446744073709551615"}}}};
    decode(control.dump());
    control["body"]["sequence"] = "18446744073709551616";
    fails([&] { decode(control.dump()); }, "body.invalid");
    control["body"] = Json::array();
    fails([&] { decode(control.dump()); }, "body.invalid");
}
void negotiate01() {
    auto server_body = hello(), client_body = hello();
    server_body["wire_minor"] = 5; client_body["wire_minor"] = 2;
    client_body["max_frame_bytes"] = 4096;
    client_body["optional_features"].push_back("unknown.optional");
    const auto selected = negotiate(handshake(server_body), handshake(client_body), {"console"});
    check(selected.minor == 2 && selected.max_frame_bytes == 4096 && selected.features == std::set<std::string>{"settings.preview"}, "negotiation differs");
    check(selected.documents == std::set<std::pair<std::string, std::string>>{{"command", "0.2.0"}}, "document version changed");
    fails([&] { negotiate(handshake(server_body), handshake(client_body), {"saver"}); }, "handshake.role_denied");
    client_body["required_features"].push_back("unknown.required");
    fails([&] { negotiate(handshake(server_body), handshake(client_body), {"console"}); }, "handshake.required_feature");
    client_body["required_features"] = Json::array();
    server_body["required_features"].push_back("server.required");
    fails([&] { negotiate(handshake(server_body), handshake(client_body), {"console"}); }, "handshake.required_feature");
    server_body["required_features"] = Json::array();
    client_body["document_versions"][0]["version"] = "0.1.0";
    fails([&] { negotiate(handshake(server_body), handshake(client_body), {"console"}); }, "handshake.document_version");
    client_body["wire_major"] = 1;
    fails([&] { handshake(client_body); }, "handshake.invalid");
    auto duplicate = hello(); duplicate["document_versions"].push_back(duplicate["document_versions"][0]);
    fails([&] { handshake(duplicate); }, "handshake.invalid");
    auto numeric = hello(); numeric["wire_major"] = 0.0; numeric["wire_minor"] = 1.0;
    check(handshake(numeric).minor == 1, "JSON integer-valued number rejected");
    numeric["wire_minor"] = 1.5;
    fails([&] { handshake(numeric); }, "handshake.invalid");
}
void fill(Ledger& ledger, bool finish) {
    for (unsigned n = 0; n < 128; ++n) {
        const auto request = "R" + std::to_string(n);
        check(ledger.admit("P", "C", request, "{}", 0) == Admission::admitted, "early capacity exhaustion");
        if (finish) ledger.finish("P", request, "committed", true, 0);
    }
}
void budget01() {
    Ledger ledger; fill(ledger, false);
    check(ledger.admit("P", "C", "R129", "{}", 0) == Admission::busy, "129th mutation executed");
    check(ledger.size() == 128, "busy changed reservations");
    check(ledger.get("P", "R0", 0).has_value(), "control lookup blocked at capacity");
    check(ledger.cancel("P", "R0", "cancelled", 0)->result == "cancelled", "control cancellation blocked");
    check(ledger.admit("P", "C", "R129", "{}", 0) == Admission::busy, "cancel evicted retained result");
}
void budget02() {
    Ledger ledger; fill(ledger, true);
    check(ledger.admit("P", "C", "R129", "{}", 599000) == Admission::busy, "unexpired result evicted");
    check(ledger.admit("P", "C", "R129", "{}", 600000) == Admission::admitted, "expired record not reclaimed");
    check(ledger.size() == 1 && ledger.reserved_bytes() == 4098, "expiry accounting differs");
}
void budget03() {
    Ledger ledger; fill(ledger, true);
    check(ledger.admit("P", "reconnected", "R129", "{}", 599000) == Admission::busy, "reconnect reset capacity");
    check(ledger.get("P", "R0", 599000)->result == "committed", "reconnect cannot retrieve result");
    check(!ledger.get("P", "R0", 600000), "retrieval extended expiry");
}
void budget04() {
    Ledger ledger;
    check(ledger.admit("P", "C", "R", "{ }", 0) == Admission::admitted, "request not admitted");
    check(ledger.admit("P", "C2", "R", "{ }", 0) == Admission::pending, "unfinished replay executes again");
    ledger.finish("P", "R", "revision41", true, 0);
    check(ledger.admit("P", "C2", "R", "{ }", 599000) == Admission::replay, "identical replay not found");
    check(ledger.admit("P", "C2", "R", "{}", 599000) == Admission::conflict, "changed bytes not conflict");
    check(ledger.get("P", "R", 599000)->result == "revision41" && ledger.size() == 1, "replay changed result");
    check(!ledger.get("P", "R", 600000), "replay extended expiry");
}
void ledger01() {
    Ledger ledger;
    ledger.admit("P", "C", "R", "{}", 0);
    check(ledger.cancel("P", "R", "cancelled", 0)->result == "cancelled", "precommit cancel differs");
    ledger.admit("P", "C", "S", "{}", 0);
    fails([&] { ledger.finish("P", "S", std::string(4097, 'x'), true, 0); }, "result.size");
    check(!ledger.get("P", "S", 0)->finished_ms, "oversize result partially finished");
    ledger.finish("P", "S", "committed", true, 0);
    check(ledger.cancel("P", "S", "cancelled", 0)->committed, "cancel undid committed result");
    check(ledger.admit("other", "C2", "R", "{}", 0) == Admission::admitted, "principal scopes conflated");
    check(!ledger.get("other", "S", 0), "cross-principal retrieval");
    ledger.get("P", "R", 1);
    fails([&] { ledger.get("P", "R", 0); }, "clock.regressed");
    Ledger active;
    for (unsigned i = 0; i < 128; ++i) {
        const auto p = i < 64 ? "P" : "Q";
        check(active.admit(p, "sameConnection", "R" + std::to_string(i), "{}", 0) == Admission::admitted, "active bound early");
    }
    check(active.admit("Q", "sameConnection", "overflow", "{}", 0) == Admission::busy, "active connection limit ignored");
    Ledger global;
    for (unsigned i = 0; i < 1024; ++i) {
        const auto p = "P" + std::to_string(i / 128);
        check(global.admit(p, p, "R" + std::to_string(i), "{}", 0) == Admission::admitted, "global bound early");
    }
    check(global.admit("P9", "C9", "overflow", "{}", 0) == Admission::busy, "global record bound ignored");
    Ledger principals;
    for (unsigned i = 0; i < 16; ++i) {
        const auto p = "P" + std::to_string(i);
        check(principals.admit(p, p, "R", "{}", 0) == Admission::admitted, "principal bound early");
    }
    check(principals.admit("P17", "C17", "R", "{}", 0) == Admission::busy, "principal bound ignored");
    Ledger bytes;
    for (unsigned i = 0; i < 819; ++i) {
        const auto p = "P" + std::to_string(i / 128);
        check(bytes.admit(p, p, "R" + std::to_string(i), std::string(16384, 'x'), 0) == Admission::admitted, "byte reservation early");
    }
    check(bytes.admit("P7", "P7", "overflow", std::string(16384, 'x'), 0) == Admission::busy, "result capacity not reserved");
    check(bytes.reserved_bytes() == 16773120, "byte accounting differs");
}
void policy01() {
    const auto p = policy(); const auto a = authority();
    const std::vector<std::pair<std::string, std::vector<Json>>> valid = {
        {"sampling.resources_ms", {100, 60000}}, {"sampling.reconcile_ms", {1000, 3600000}},
        {"sampling.max_workers", {1, 32}}, {"history.persistent", {false, true}},
        {"history.segment_bytes", {4096, 1073741824}}, {"history.segments", {1, 100}},
        {"display.enabled", {false, true}}, {"display.theme_id", {"theme:one", std::string(256, 'x')}},
        {"display.reduced_motion", {false, true}}, {"privacy.remote_probes", {false, true}}, {"privacy.export_enabled", {false, true}}};
    for (const auto& row : valid) for (const auto& value : row.second) {
        auto c = command(); c["operations"][0]["path"] = row.first; c["operations"][0]["value"] = value;
        decision(c, a, p, "preview", "");
        c["operations"][0]["value"] = nullptr;
        decision(c, a, p, "invalid", "command.setting");
    }
    for (const auto& row : valid) {
        if (!row.second.front().is_number_integer()) continue;
        auto c = command(); c["operations"][0]["path"] = row.first;
        c["operations"][0]["value"] = row.second.front().get<std::int64_t>() - 1;
        decision(c, a, p, "invalid", "command.setting");
        c["operations"][0]["value"] = row.second.back().get<std::int64_t>() + 1;
        decision(c, a, p, "invalid", "command.setting");
    }
    auto integral = command(); integral["operations"][0]["value"] = 1000.0;
    decision(integral, a, p, "preview", "");
    auto text = command(); text["operations"][0]["path"] = "display.theme_id";
    for (const auto& value : {std::string{}, std::string(257, 'x'), std::string("bad id")}) {
        text["operations"][0]["value"] = value;
        decision(text, a, p, "invalid", "command.setting");
    }
    for (const auto& value : std::vector<Json>{99, 60001, -1, true, "1000", 1000.5}) {
        auto c = command(); c["operations"][0]["value"] = value;
        decision(c, a, p, "invalid", "command.setting");
    }
    auto c = command(); c["operations"][0]["path"] = "unknown";
    decision(c, a, p, "invalid", "command.setting");
    c = command(); c["operations"].push_back(c["operations"][0]);
    decision(c, a, p, "invalid", "command.duplicate_path");
    c = command(); c["approved"] = true;
    decision(c, a, p, "invalid", "command.shape");
    c = command(); c["operations"][0]["approved"] = true;
    decision(c, a, p, "invalid", "command.operation");
    c = command(); c["expected_revision"] = "39";
    decision(c, a, p, "conflict", "revision.changed");
    c = command(); c["policy_generation"] = "6";
    decision(c, a, p, "conflict", "policy.changed");
    c = command(); c["expected_revision"] = "18446744073709551616";
    decision(c, a, p, "invalid", "command.revision");
}
void policy02() {
    auto c = command(); auto p = policy(); auto a = authority();
    p.forced["sampling.resources_ms"] = 2000;
    decision(c, a, p, "denied", "policy.forced");
    c["operations"][0]["value"] = 2000;
    decision(c, a, p, "preview", "");
    p.denied_capabilities.insert("settings.preview");
    decision(c, a, p, "denied", "policy.denied");
    p = policy(); a.authenticated = false;
    decision(c, a, p, "denied", "policy.denied");
    a = authority(); a.role = "desktop";
    decision(c, a, p, "denied", "policy.denied");
    a = authority(); p.available = false;
    decision(c, a, p, "denied", "policy.denied");
    p = policy(); c["intent"] = "commit";
    decision(c, a, p, "invalid", "feature.unsupported");
    const auto reply = cfg::result(cfg::preview(c, a, p, 40), "R", "E", 40);
    check(reply["stored"] == false && reply["durable"] == false && reply["visible"] == false && reply["revision"] == "40" && reply["activation"].empty(), "unsupported commit claimed storage");
    c = command(); c["operations"][0] = {{"op", "scene.replace"}, {"scene", Json::object()}};
    decision(c, a, p, "invalid", "feature.unsupported");
    const auto unknown = cfg::result({"unknown", "request.reconcile"}, "R", "E", 40);
    check(unknown["revision"].is_null() && unknown["stored"].is_null() && unknown["durable"].is_null() && unknown["visible"].is_null(), "unknown facts fabricated");
}
void disclosure01() {
    auto p = policy(); auto a = authority();
    for (const auto& label : {"public", "operational", "sensitive", "secret", "unregistered"})
        check(cfg::permits(a, p, "desktop", label) == (std::string(label) == "public"), "default projection disclosed restricted field");
    p.disclosure[{"console", "desktop"}] = {"public", "operational", "sensitive", "secret"};
    check(cfg::permits(a, p, "desktop", "operational") && cfg::permits(a, p, "desktop", "unregistered"), "explicit disclosure grant ignored");
    check(!cfg::permits(a, p, "desktop", "secret"), "secret allowed by policy");
    check(!cfg::permits(a, p, "clipboard", "sensitive"), "channel grant leaked");
    a = {true, "saver", {"saver"}};
    check(cfg::permits(a, p, "desktop", "public") && !cfg::permits(a, p, "desktop", "sensitive"), "role grant leaked");
    a = authority(); p.disclosure.clear();
    check(!cfg::permits(a, p, "desktop", "sensitive"), "revoked disclosure persisted");
    p.available = false;
    check(cfg::permits(a, p, "desktop", "public") && !cfg::permits(a, p, "desktop", "operational"), "required-policy failure disclosure");
    a.role_grants.clear();
    check(!cfg::permits(a, p, "desktop", "public"), "ungranted role disclosed");
}
void queue01() {
    Outbox queue;
    for (unsigned i = 0; i < 16; ++i) check(queue.data("data", "gap"), "data capacity early");
    check(queue.control("health"), "data consumed control capacity");
    check(queue.pop() == "health", "control did not precede data");
    check(!queue.data("overflow", "gap") && queue.data_size() == 0 && queue.pop() == "gap", "data overflow did not invalidate projection");
    queue.data("restricted", "gap");
    queue.revoke("revoked");
    check(queue.pop() == "revoked" && !queue.pop(), "revocation retained pending data");
    for (unsigned i = 0; i < 16; ++i) check(queue.control("health"), "control capacity early");
    check(!queue.can_control(1) && !queue.control("overflow") && queue.closed() && !queue.pop(), "control saturation did not close");
    Outbox bytes;
    check(bytes.data(std::string(1048572, 'x'), "gap") && bytes.data(std::string(1048572, 'x'), "gap"), "data byte bound early");
    check(!bytes.data("x", "gap") && bytes.pop() == "gap", "data byte bound ignored");
    Outbox controls;
    check(controls.control(std::string(65532, 'x')), "control byte bound early");
    check(!controls.control("x") && controls.closed(), "control byte bound ignored");
}
std::string packet(const std::string& type, const Json& body, const std::string& id = "C", const std::string& epoch = "E") {
    return Json{{"type", type}, {"body", body}, {"connection_id", id}, {"producer_epoch", epoch}}.dump();
}
void connect(cfg::Sessions& sessions, const std::string& id, const std::string& principal = "P") {
    sessions.open(id, principal, authority(), 0);
    auto client = hello();
    client["document_versions"].push_back({{"document", "command-result"}, {"version", "0.1.0"}});
    client["optional_features"] = {"settings.preview", "result.get", "cancel"};
    sessions.receive(id, Json{{"type", "hello"}, {"body", client}}.dump(), 0);
    const auto reply = sessions.pop(id, 0);
    check(reply && decode(*reply).type == "welcome", "welcome missing");
}
void session01() {
    cfg::Sessions unauthenticated("E", 40, policy());
    auto denied = authority(); denied.authenticated = false;
    fails([&] { unauthenticated.open("C", "P", denied, 0); }, "session.unauthenticated");
    unauthenticated.open("C", "P", authority(), 0);
    unauthenticated.tick(4999);
    check(!unauthenticated.closed("C"), "handshake expired early");
    unauthenticated.tick(5000);
    check(unauthenticated.closed("C") && unauthenticated.close_reason("C") == "handshake.timeout", "handshake deadline ignored");
    cfg::Sessions sessions("E", 40, policy());
    connect(sessions, "C");
    sessions.receive("C", packet("command", command()), 0);
    const auto preview = decode(*sessions.pop("C", 0));
    check(preview.body["outcome"] == "preview" && preview.body["stored"] == false && sessions.request_count() == 1, "preview integration differs");
    sessions.disconnect("C");
    connect(sessions, "C2");
    sessions.receive("C2", packet("result.get", {{"request_id", "R"}}, "C2"), 0);
    check(decode(*sessions.pop("C2", 0)).body == preview.body, "reconnect result lost");
    sessions.receive("C2", packet("command", command(), "C2"), 0);
    check(decode(*sessions.pop("C2", 0)).body == preview.body && sessions.request_count() == 1, "replay executed again");
    auto changed = command(); changed["operations"][0]["value"] = -1;
    sessions.receive("C2", packet("command", changed, "C2"), 0);
    check(decode(*sessions.pop("C2", 0)).body["error"]["code"] == "request.changed", "invalid changed body did not conflict");
    connect(sessions, "C3", "other");
    sessions.receive("C3", packet("result.get", {{"request_id", "R"}}, "C3"), 0);
    check(decode(*sessions.pop("C3", 0)).body["outcome"] == "unknown", "cross-principal result disclosed");
    auto revoked = policy(); revoked.revision = 8; revoked.available = false;
    sessions.policy(revoked, 1);
    check(decode(*sessions.pop("C2", 1)).type == "gap", "revocation gap missing");
    sessions.receive("C2", packet("result.get", {{"request_id", "R"}}, "C2"), 1);
    check(decode(*sessions.pop("C2", 1)).body["outcome"] == "denied", "cached result bypassed current policy");
    sessions.receive("C2", packet("heartbeat", {{"sequence", "1"}}, "C2"), 1);
    check(decode(*sessions.pop("C2", 1)).type == "heartbeat", "public health blocked by policy");
    sessions.receive("C2", packet("heartbeat", {{"sequence", "1"}}, "C2", "oldEpoch"), 1);
    check(sessions.closed("C2") && sessions.close_reason("C2") == "session.identity", "old epoch accepted");
    cfg::Sessions direction("E", 40, policy()); connect(direction, "C");
    direction.receive("C", packet("result", Json::object()), 0);
    check(direction.closed("C") && direction.close_reason("C") == "session.direction_or_feature", "client result accepted");
    cfg::Sessions feature("E", 40, policy()); connect(feature, "C");
    feature.receive("C", packet("subscribe", Json::object()), 0);
    check(feature.closed("C"), "unadvertised feature accepted");
    for (const auto type : {"render.challenge", "render.progress"}) {
        cfg::Sessions rendering("E", 40, policy()); connect(rendering, "C");
        auto valid = packet(type, {{"generation", "18446744073709551615"}});
        check(decode(valid).type == type, "bounded render body not recognized");
        rendering.receive("C", valid, 0);
        check(rendering.closed("C") && rendering.close_reason("C") == "session.direction_or_feature", "preview inherited render feature");
        fails([&] { decode(packet(type, {{"generation", 1}})); }, "body.invalid");
        fails([&] { decode(packet(type, {{"generation", "18446744073709551616"}})); }, "body.invalid");
        fails([&] { decode(packet(type, {{"generation", "1"}, {"approved", true}})); }, "body.invalid");
    }
    cfg::Sessions spoof("E", 40, policy());
    spoof.open("C", "P", authority(), 0);
    auto claim = hello(); claim["role"] = "maintenance";
    spoof.receive("C", Json{{"type", "hello"}, {"body", claim}}.dump(), 0);
    check(spoof.closed("C") && spoof.close_reason("C") == "handshake.role_denied", "claimed role manufactured authority");
    cfg::Sessions saturated("E", 40, policy()); connect(saturated, "C");
    for (unsigned i = 0; i < 16; ++i) {
        auto c = command(); c["request_id"] = "R" + std::to_string(i);
        saturated.receive("C", packet("command", c), 0);
    }
    auto extra = command(); extra["request_id"] = "extra";
    saturated.receive("C", packet("command", extra), 0);
    check(saturated.closed("C") && saturated.request_count() == 16, "request admitted without control reply capacity");
    cfg::Sessions connections("E", 40, policy());
    for (unsigned i = 0; i < 16; ++i) connections.open("C" + std::to_string(i), "P", authority(), 0);
    fails([&] { connections.open("extra", "P", authority(), 0); }, "session.capacity");
    fails([&] { connections.open("C0", "P", authority(), 0); }, "session.collision");
}
}
int main(int argc, char** argv) {
    const std::map<std::string, std::function<void()>> cases = {
        {"FRAME-01", frame01}, {"FRAME-02", frame02}, {"FRAME-03", frame03}, {"JSON-01", json01},
        {"WIRE-01", wire01}, {"NEGOTIATE-01", negotiate01}, {"IPC-BUDGET-01", budget01}, {"IPC-BUDGET-02", budget02},
        {"IPC-BUDGET-03", budget03}, {"IPC-BUDGET-04", budget04}, {"LEDGER-01", ledger01},
        {"POLICY-01", policy01}, {"POLICY-02", policy02}, {"DISCLOSURE-01", disclosure01},
        {"QUEUE-01", queue01}, {"SESSION-01", session01}};
    if (argc != 2 || !cases.count(argv[1])) { std::cerr << "unknown or missing case\n"; return 2; }
    try { cases.at(argv[1])(); std::cout << argv[1] << ": pass\n"; return 0; }
    catch (const std::exception& error) { std::cerr << argv[1] << ": " << error.what() << '\n'; return 1; }
}
