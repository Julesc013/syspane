#include "health_link.hpp"
#include <array>

namespace syspane::recovery {
namespace w = protocol;
HealthLink::HealthLink(platform::Stream& stream, bool server, std::string role, std::string epoch, std::string connection)
    : stream_(stream), server_(server), progress_(role == "desktop"), role_(std::move(role)),
      epoch_(std::move(epoch)), connection_(std::move(connection)) {
    if (!server_) stream_.write(w::frame(w::Json{{"type", "hello"}, {"body", greeting(role_)}}.dump(), limit_), 100);
}
w::Json HealthLink::greeting(const std::string& role) const {
    w::Json features = w::Json::array({"recovery.health"});
    if (progress_) features.push_back("recovery.progress");
    return {{"wire_major", 0}, {"wire_minor", 1}, {"role", role}, {"producer_epoch", epoch_},
        {"max_frame_bytes", limit_}, {"document_versions", w::Json::array({{{"document", "recovery-health"}, {"version", "0.1.0"}}})},
        {"required_features", features}, {"optional_features", w::Json::array()}};
}
void HealthLink::send(const std::string& type, w::Json body) try {
    if (!ready_ || closed_) throw w::Error("health.not_ready");
    stream_.write(w::frame(w::Json{{"type", type}, {"body", std::move(body)},
        {"connection_id", connection_}, {"producer_epoch", epoch_}}.dump(), limit_), 100);
} catch (...) {
    closed_ = true;
    throw;
}
std::vector<HealthEvent> HealthLink::poll() try {
    if (closed_) throw w::Error("health.closed");
    std::vector<HealthEvent> events;
    std::array<char, 4096> buffer{};
    const auto read = stream_.read(buffer.data(), buffer.size(), 100);
    if (read.eof) { closed_ = true; decoder_.eof(); throw w::Error("health.eof"); }
    if (read.bytes) decoder_.feed(std::string_view(buffer.data(), read.bytes), read.observed_ms, [&](std::string_view payload) {
        if (closed_) throw w::Error("health.closed");
        if (events.size() >= 16) throw w::Error("health.event_limit");
        const auto message = w::decode(payload);
        const auto now = platform::monotonic_ms();
        if (!ready_) {
            if (now - stream_.connected_ms() >= 5000) throw w::Error("health.handshake_timeout");
            if (message.type != (server_ ? "hello" : "welcome")) throw w::Error("health.handshake_state");
            const auto remote = w::handshake(message.body), local = w::handshake(greeting(server_ ? "console" : role_));
            const auto selection = server_ ? w::negotiate(local, remote, {role_}) : w::negotiate(remote, local, {role_});
            if (!server_ && remote.role != "console") throw w::Error("health.server_role");
            if (selection.documents != std::set<std::pair<std::string,std::string>>{{"recovery-health", "0.1.0"}} ||
                !selection.features.count("recovery.health") || (progress_ && !selection.features.count("recovery.progress")))
                throw w::Error("health.feature");
            limit_ = selection.max_frame_bytes; decoder_.restrict_limit(limit_);
            if (!server_) {
                if (remote.max_frame_bytes != limit_ || remote.minor != selection.minor || remote.epoch != message.producer_epoch)
                    throw w::Error("health.selection");
                connection_ = message.connection_id; epoch_ = message.producer_epoch;
            }
            ready_ = true;
            if (server_) send("welcome", greeting("console"));
            events.push_back({HealthKind::ready, 0, now});
            return;
        }
        if (message.connection_id != connection_ || message.producer_epoch != epoch_) throw w::Error("health.identity");
        if (message.type == "heartbeat") {
            events.push_back({HealthKind::heartbeat, *w::decimal(message.body["sequence"].get<std::string>()), now});
        } else if (message.type == "render.challenge" && progress_ && !server_) {
            const auto generation = *w::decimal(message.body["generation"].get<std::string>());
            if (pending_ || (completed_ && generation <= *completed_)) throw w::Error("health.challenge_order");
            pending_ = generation; events.push_back({HealthKind::challenge, generation, now});
        } else if (message.type == "render.progress" && progress_ && server_) {
            const auto generation = *w::decimal(message.body["generation"].get<std::string>());
            if (!pending_ || generation != *pending_) throw w::Error("health.progress_order");
            completed_ = generation; pending_.reset(); events.push_back({HealthKind::progress, generation, now});
        } else if (message.type == "shutdown") {
            closed_ = true; events.push_back({HealthKind::shutdown, 0, now});
        } else throw w::Error("health.direction_or_feature");
    });
    const auto now = platform::monotonic_ms();
    if (!ready_ && now - stream_.connected_ms() >= 5000) throw w::Error("health.handshake_timeout");
    decoder_.tick(now);
    return events;
} catch (...) {
    closed_ = true;
    throw;
}
void HealthLink::heartbeat(std::uint64_t sequence) { send("heartbeat", {{"sequence", std::to_string(sequence)}}); }
void HealthLink::challenge(std::uint64_t generation) {
    if (!server_ || !progress_ || pending_ || (completed_ && generation <= *completed_)) throw w::Error("health.challenge_order");
    send("render.challenge", {{"generation", std::to_string(generation)}}); pending_ = generation;
}
void HealthLink::progress(std::uint64_t generation) {
    if (server_ || !progress_ || !pending_ || generation != *pending_) throw w::Error("health.progress_order");
    send("render.progress", {{"generation", std::to_string(generation)}}); completed_ = generation; pending_.reset();
}
void HealthLink::shutdown() { send("shutdown", {{"reason", "normal"}}); closed_ = true; }
} // namespace syspane::recovery
