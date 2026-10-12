#include "local_ipc.hpp"
#include "session.hpp"
#include "wire.hpp"
#include <array>
#include <chrono>
#include <deque>
#include <iostream>
#include <set>
#include <thread>

namespace native = syspane::platform;
namespace wire = syspane::protocol;
namespace cfg = syspane::configuration;
using wire::Json;
namespace {
void emit(Json value) { std::cout << value.dump() << std::endl; }
#if defined(_WIN32)
void polling_server(const std::string& endpoint,const std::string& scenario,std::uint64_t expected) {
    if (!native::unprivileged_context() || !expected) throw wire::Error("probe.poll_context");
    const std::set<std::string> modes={"idle","delayed","preconnected","retry","timeout","close-read","close-connect","keep-stream"};
    if (!modes.count(scenario)) throw wire::Error("probe.poll_scenario");
    auto listener=std::make_unique<native::Listener>(endpoint);
    const auto started=native::monotonic_ms();auto last_tick=started;
    Json samples=Json::array(),ticks=Json::array();unsigned errors=0,calls=0;std::optional<native::Stream> stream;
    emit({{"event","ready"},{"access_controls_verified",listener->access_controls_verified()},{"unprivileged_context",true},{"started_ms",std::to_string(started)}});
    if (scenario=="preconnected") std::this_thread::sleep_for(std::chrono::milliseconds(150));
    for (;;) {
        auto now=native::monotonic_ms();
        if (now-started>=12000) throw wire::Error("probe.poll_deadline");
        const auto before=now;std::string outcome="empty",error;
        try { auto ready=listener->accept_ready(expected);if (ready) { stream=std::move(ready);outcome="accepted"; } }
        catch (const native::IpcError& failure) { error=failure.what();outcome="error";++errors; }
        const auto after=native::monotonic_ms();
        if (samples.size()>=20000) throw wire::Error("probe.poll_sample_limit");
        samples.push_back({{"ordinal",++calls},{"start_ms",std::to_string(before)},{"end_ms",std::to_string(after)},{"result",outcome},{"error",error}});
        if (!error.empty()) emit({{"event","admission_error"},{"code",error},{"observed_ms",std::to_string(after)}});
        if (after-last_tick>=100) { last_tick=after;ticks.push_back(std::to_string(after));emit({{"event","tick"},{"observed_ms",std::to_string(after)}}); }
        if (stream) {
            const auto connected=stream->connected_ms();char first=0,second=0;
            const auto read=stream->read(&first,1,1),again=stream->read(&second,1,1);
            const auto busy_begin=native::monotonic_ms();bool busy=false;try { (void)listener->accept_ready(expected); }catch(const native::IpcError& failure) { busy=std::string(failure.what())=="endpoint.busy"; }
            samples.push_back({{"ordinal",++calls},{"start_ms",std::to_string(busy_begin)},{"end_ms",std::to_string(native::monotonic_ms())},{"result","error"},{"error",busy?"endpoint.busy":"probe.poll_busy"}});
            if (!busy) throw wire::Error("probe.poll_busy");
            const auto destroy_begin=native::monotonic_ms();
            if (scenario=="keep-stream") listener.reset();
            const auto destroy_end=native::monotonic_ms();
            if (scenario=="keep-stream") {
                stream->write("y",100);emit({{"event","retained_stream"}});char acknowledgement=0;const auto got=stream->read(&acknowledgement,1,1000);
                if (got.bytes!=1 || acknowledgement!='z') throw wire::Error("probe.poll_retained_stream");
            }
            emit({{"event","authenticated"},{"peer_pid",stream->peer().process_id},{"connected_ms",std::to_string(connected)},
                {"first_read_bytes",read.bytes},{"first_value",static_cast<unsigned char>(first)},{"first_observed_ms",std::to_string(read.observed_ms)},
                {"second_read_bytes",again.bytes},{"second_timeout",again.timeout},{"busy_rejected",busy},
                {"listener_destroy_ms",std::to_string(destroy_end-destroy_begin)},{"stream_survived_listener",scenario=="keep-stream"}});
            stream.reset();
            emit({{"event","complete"},{"samples",samples},{"call_count",calls},{"ticks",ticks},{"errors",errors},{"admitted",true},{"destroy_ms","0"}});
            return;
        }
        const auto limit=scenario=="idle"?750:scenario=="close-connect"?350:scenario=="close-read"?900:0;
        if (limit && after-started>=static_cast<unsigned>(limit)) {
            const auto destroy_begin=native::monotonic_ms();listener.reset();const auto destroy_end=native::monotonic_ms();
            emit({{"event","complete"},{"samples",samples},{"call_count",calls},{"ticks",ticks},{"errors",errors},{"admitted",false},{"destroy_ms",std::to_string(destroy_end-destroy_begin)}});
            return;
        }
        if (errors>2) throw wire::Error("probe.poll_repeated_error");
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}
#endif
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
#if defined(_WIN32)
        else if (role == "poll") polling_server(argv[2], argv[3], *expected);
#endif
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
