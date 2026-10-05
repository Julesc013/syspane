#include "local_ipc.hpp"
#include "session.hpp"
#include "wire.hpp"
#include <array>
#include <chrono>
#include <deque>
#include <iostream>
#include <thread>

namespace native = syspane::platform;
namespace wire = syspane::protocol;
namespace cfg = syspane::configuration;
using wire::Json;
namespace {
void emit(Json value) { std::cout << value.dump() << std::endl; }
std::string envelope(const std::string& type, Json body, const std::string& connection, const std::string& epoch = "probe:epoch-1") {
    return Json{{"type", type}, {"body", std::move(body)}, {"connection_id", connection}, {"producer_epoch", epoch}}.dump();
}
Json hello(const std::string& role = "console", unsigned maximum = 1048576) {
    return {{"type", "hello"}, {"body", {{"wire_major", 0}, {"wire_minor", 1}, {"role", role}, {"producer_epoch", "probe:client"},
        {"max_frame_bytes", maximum}, {"document_versions", Json::array({{{"document", "command"}, {"version", "0.2.0"}},
            {{"document", "command-result"}, {"version", "0.1.0"}}})},
        {"required_features", Json::array()}, {"optional_features", {"settings.preview", "result.get", "cancel"}}}}};
}
Json command(const std::string& request, int value = 1000, const std::string& intent = "preview") {
    return {{"schema_version", "0.2.0"}, {"request_id", request}, {"expected_revision", "40"}, {"policy_generation", "7"},
        {"intent", intent}, {"operations", Json::array({{{"op", "settings.set"}, {"path", "sampling.resources_ms"}, {"value", value}}})}};
}
class Client {
public:
    native::Stream stream;
    explicit Client(native::Stream connection) : stream(std::move(connection)) {}
    Json next() {
        const auto deadline = native::monotonic_ms() + 5000;
        std::array<char, 4096> buffer{};
        while (messages.empty()) {
            if (native::monotonic_ms() >= deadline) throw wire::Error("probe.reply_timeout");
            const auto read = stream.read(buffer.data(), buffer.size());
            if (read.eof) { decoder.eof(); throw wire::Error("probe.eof"); }
            if (read.timeout) { decoder.tick(read.observed_ms); continue; }
            decoder.feed(std::string_view(buffer.data(), read.bytes), read.observed_ms, [&](auto bytes) {
                wire::decode(bytes);
                messages.push_back(wire::parse(bytes));
                if (messages.size() > 16) throw wire::Error("probe.reply_limit");
            });
        }
        auto result = std::move(messages.front()); messages.pop_front();
        emit({{"event", "reply"}, {"message", result}});
        return result;
    }
    void send(const std::string& type, Json body, const std::string& connection) {
        stream.write(wire::frame(envelope(type, std::move(body), connection)));
    }
private:
    wire::Framer decoder;
    std::deque<Json> messages;
};
void server(const std::string& endpoint, const std::string& scenario, std::uint64_t expected) {
    if (!native::unprivileged_context()) throw wire::Error("probe.privileged_context");
    native::Listener listener(endpoint);
    emit({{"event", "ready"}, {"access_controls_verified", listener.access_controls_verified()}, {"unprivileged_context", true}});
    cfg::Policy policy; policy.available = true; policy.revision = 7;
    cfg::Sessions sessions("probe:epoch-1", 40, policy);
    const unsigned connections = scenario == "journey" ? 2 : 1;
    for (unsigned ordinal = 0; ordinal < connections; ++ordinal) {
        emit({{"event", "listening"}, {"ordinal", ordinal}});
        auto stream = listener.accept(expected);
        emit({{"event", "authenticated"}, {"peer_pid", stream.peer().process_id}, {"user_session_verified", true}});
        if (scenario == "write-stall") {
            const auto started = native::monotonic_ms();
            try { stream.write(std::string(1048580, 'x')); throw wire::Error("probe.write_did_not_stall"); }
            catch (const native::IpcError& error) {
                emit({{"event", "closed"}, {"reason", error.what()}, {"elapsed_ms", native::monotonic_ms() - started}, {"requests", 0}});
                return;
            }
        }
        const auto id = "C" + std::to_string(ordinal);
        sessions.open(id, stream.peer().principal, {true, "console", {"console"}}, stream.connected_ms());
        wire::Framer decoder;
        std::array<char, 4096> buffer{};
        unsigned reads = 0, frames = 0;
        std::string reason;
        const auto started = native::monotonic_ms();
        try {
            while (!sessions.closed(id)) {
                if (native::monotonic_ms() - started > 15000) throw wire::Error("probe.process_deadline");
                const auto read = stream.read(buffer.data(), buffer.size());
                if (read.eof) { decoder.eof(); reason = "peer.eof"; break; }
                if (read.bytes) {
                    ++reads;
                    decoder.feed(std::string_view(buffer.data(), read.bytes), read.observed_ms, [&](auto payload) {
                        ++frames;
                        sessions.receive(id, payload, native::monotonic_ms());
                        decoder.restrict_limit(sessions.frame_bound(id));
                        if (sessions.closed(id)) reason = sessions.close_reason(id);
                    });
                }
                const auto now = native::monotonic_ms();
                sessions.tick(now);
                if (sessions.closed(id)) { reason = sessions.close_reason(id); break; }
                decoder.tick(now);
                while (auto payload = sessions.pop(id, native::monotonic_ms())) stream.write(wire::frame(*payload, sessions.frame_bound(id)));
            }
        } catch (const wire::Error& error) { reason = error.what(); }
          catch (const native::IpcError& error) { reason = error.what(); }
        emit({{"event", "closed"}, {"reason", reason}, {"reads", reads}, {"frames", frames},
              {"buffered", decoder.buffered()}, {"requests", sessions.request_count()}, {"elapsed_ms", native::monotonic_ms() - started}});
        sessions.disconnect(id);
    }
}
void client(const std::string& endpoint, const std::string& scenario, std::uint64_t expected) {
    if (!native::unprivileged_context()) throw wire::Error("probe.privileged_context");
    Client client(native::Stream::connect(endpoint, expected));
    emit({{"event", "authenticated"}, {"peer_pid", client.stream.peer().process_id}, {"user_session_verified", true}});
    if (scenario == "write-stall" || scenario == "hello-timeout") {
        client.stream.write(std::string(1, '\0'));
        std::this_thread::sleep_for(std::chrono::milliseconds(6500));
        return;
    }
    if (scenario == "partial-eof") { client.stream.write(std::string("\0\0\0\x14{", 5)); return; }
    if (scenario == "malformed") { client.stream.write(std::string(4, '\0')); client.next(); return; }
    auto greeting = wire::frame(hello(scenario == "role-spoof" ? "maintenance" : "console", scenario == "over-limit" ? 1024 : 1048576).dump());
    client.stream.write(std::string_view(greeting).substr(0, 1));
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    client.stream.write(std::string_view(greeting).substr(1));
    const auto welcome = client.next();
    if (welcome["type"] != "welcome") throw wire::Error("probe.expected_welcome");
    const auto id = welcome["connection_id"].get<std::string>();
    if (scenario == "frame-timeout") {
        client.stream.write(std::string(1, '\0'));
        std::this_thread::sleep_for(std::chrono::milliseconds(6500));
        return;
    }
    if (scenario == "over-limit") { client.stream.write(std::string("\0\0\x08\0", 4)); client.next(); return; }
    if (scenario == "old-epoch") {
        client.stream.write(wire::frame(envelope("heartbeat", {{"sequence", "1"}}, id, "old:epoch"))); client.next(); return;
    }
    if (scenario == "saturation") {
        for (unsigned i = 0; i < 129; ++i) {
            client.send("command", command("R" + std::to_string(i)), id); client.next();
        }
        client.send("result.get", {{"request_id", "R0"}}, id); client.next();
        client.send("cancel", {{"request_id", "R0"}}, id); client.next();
        client.send("heartbeat", {{"sequence", "9"}}, id); client.next();
    } else if (scenario == "drop-reply") {
        client.send("command", command("R"), id);
        return; // Deliberately close before reading any command result.
    } else if (scenario == "journey") {
        const auto bytes = wire::frame(envelope("command", command("R"), id));
        client.stream.write(bytes + bytes);
        client.next(); client.next();
    } else if (scenario == "retrieve") {
        client.send("result.get", {{"request_id", "R"}}, id); client.next();
        client.send("command", command("commit", 1000, "commit"), id); client.next();
        client.send("command", command("R", 2000), id); client.next();
        client.send("result.get", {{"request_id", "missing"}}, id); client.next();
    } else if (scenario == "forged") {
        auto forged = command("forged"); forged["approved"] = true;
        client.send("command", forged, id); client.next();
    } else if (scenario != "normal") throw wire::Error("probe.unknown_scenario");
    client.send("shutdown", {{"reason", "normal"}}, id);
}
}
int main(int argc, char** argv) {
    if (argc != 5) { std::cerr << "usage: SysPane.IpcProbe server|client|collision endpoint scenario expected-pid\n"; return 2; }
    try {
        const auto expected = wire::decimal(argv[4]);
        if (!expected) throw wire::Error("probe.expected_pid");
        const std::string role = argv[1];
        if (role == "server") server(argv[2], argv[3], *expected);
        else if (role == "client") client(argv[2], argv[3], *expected);
        else if (role == "collision") {
            try { native::Listener collision(argv[2]); throw wire::Error("probe.collision_not_rejected"); }
            catch (const native::IpcError& error) {
                if (std::string(error.what()) != "endpoint.collision") throw;
                emit({{"event", "collision_rejected"}});
            }
        } else throw wire::Error("probe.role");
        if (role == "client") std::this_thread::sleep_for(std::chrono::milliseconds(500));
        return 0;
    } catch (const std::exception& error) {
        emit({{"event", "error"}, {"code", error.what()}});
        // Keep a denied client's OS process identity alive long enough for the
        // listening peer's independent credential query; no retry or authority.
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        return 3;
    }
}
