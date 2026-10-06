#include "health_link.hpp"
#include <array>

namespace syspane::recovery {
namespace w = protocol;
HealthLink::HealthLink(platform::Stream& stream, bool server, std::string role, std::string epoch, std::string connection,bool transactions)
    : HealthLink(server, std::move(role), std::move(epoch), std::move(connection), stream.connected_ms(),transactions) {
    stream_ = &stream;
    const auto initial = take_output();
    if (!initial.empty()) stream_->write(initial, 100);
}
HealthLink::HealthLink(bool server, std::string role, std::string epoch, std::string connection, std::uint64_t connected_ms,bool transactions)
    : connected_ms_(connected_ms), server_(server), progress_(role == "desktop"), role_(std::move(role)),
      epoch_(std::move(epoch)), connection_(std::move(connection)),transactions_(transactions) {
    if(transactions_&&role_!="console")throw w::Error("health.transaction_role");
    if (!server_) write(w::frame(w::Json{{"type", "hello"}, {"body", greeting(role_)}}.dump(), limit_));
}
void HealthLink::write(std::string bytes) {
    if (stream_) { stream_->write(bytes, 100); return; }
    if (output_frames_ >= 16 || bytes.size() > 65536 - output_.size()) throw w::Error("health.outbox_capacity");
    output_ += bytes; ++output_frames_;
}
std::string HealthLink::take_output() {
    std::string result; result.swap(output_); output_frames_ = 0; return result;
}
w::Json HealthLink::greeting(const std::string& role) const {
    w::Json features = w::Json::array({"recovery.health"});
    if (progress_) features.push_back("recovery.progress");
    if(transactions_)features.push_back("recovery.transaction");
    auto documents=w::Json::array({{{"document","recovery-health"},{"version","0.1.0"}}});
    if(transactions_)documents.push_back({{"document","transaction-watch"},{"version","0.1.0"}});
    return {{"wire_major", 0}, {"wire_minor", 1}, {"role", role}, {"producer_epoch", epoch_},
        {"max_frame_bytes", limit_}, {"document_versions", documents},
        {"required_features", features}, {"optional_features", w::Json::array()}};
}
void HealthLink::send(const std::string& type, w::Json body) try {
    if (!ready_ || closed_) throw w::Error("health.not_ready");
    write(w::frame(w::Json{{"type", type}, {"body", std::move(body)},
        {"connection_id", connection_}, {"producer_epoch", epoch_}}.dump(), limit_));
} catch (...) {
    closed_ = true;
    output_.clear(); output_frames_ = 0;
    throw;
}
std::vector<HealthEvent> HealthLink::poll(unsigned wait_ms) try {
    if (wait_ms > 100) throw w::Error("health.poll_bound");
    if (closed_) throw w::Error("health.closed");
    if (!stream_) throw w::Error("health.no_stream");
    std::array<char, 4096> buffer{};
    const auto read = stream_->read(buffer.data(), buffer.size(), wait_ms);
    if (read.eof) { closed_ = true; decoder_.eof(); throw w::Error("health.eof"); }
    return feed(std::string_view(buffer.data(), read.bytes), read.observed_ms);
} catch (...) { closed_ = true; output_.clear(); output_frames_ = 0; throw; }
std::vector<HealthEvent> HealthLink::feed(std::string_view bytes, std::uint64_t observed_ms) try {
    if (closed_) throw w::Error("health.closed");
    if (bytes.size() > 4096) throw w::Error("health.read_capacity");
    std::vector<HealthEvent> events;
    if (!bytes.empty()) decoder_.feed(bytes, observed_ms, [&](std::string_view payload) {
        if (closed_) throw w::Error("health.closed");
        if (events.size() >= 16) throw w::Error("health.event_limit");
        const auto message = w::decode(payload);
        const auto now = observed_ms;
        if (!ready_) {
            if (now - connected_ms_ >= 5000) throw w::Error("health.handshake_timeout");
            if (message.type != (server_ ? "hello" : "welcome")) throw w::Error("health.handshake_state");
            const auto remote = w::handshake(message.body), local = w::handshake(greeting(server_ ? "console" : role_));
            const auto selection = server_ ? w::negotiate(local, remote, {role_}) : w::negotiate(remote, local, {role_});
            if (!server_ && remote.role != "console") throw w::Error("health.server_role");
            auto documents=std::set<std::pair<std::string,std::string>>{{"recovery-health","0.1.0"}};
            if(transactions_)documents.insert({"transaction-watch","0.1.0"});
            if (selection.documents != documents || (transactions_&&!selection.features.count("recovery.transaction")) ||
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
        } else if(transactions_&&message.type=="transaction.started"&&server_){
            const auto ticket=*w::decimal(message.body["ticket"].get<std::string>());
            if(work_pending_||(work_completed_&&ticket<=*work_completed_))throw w::Error("health.transaction_order");
            work_pending_=ticket;work_armed_=false;events.push_back({HealthKind::transaction_started,ticket,now});
        } else if(transactions_&&message.type=="transaction.armed"&&!server_){
            const auto ticket=*w::decimal(message.body["ticket"].get<std::string>());
            if(!work_pending_||*work_pending_!=ticket||work_armed_)throw w::Error("health.transaction_order");
            work_armed_=true;events.push_back({HealthKind::transaction_armed,ticket,now});
        } else if(transactions_&&message.type=="transaction.finished"&&server_){
            const auto ticket=*w::decimal(message.body["ticket"].get<std::string>());
            if(!work_pending_||*work_pending_!=ticket||!work_armed_)throw w::Error("health.transaction_order");
            work_completed_=ticket;work_pending_.reset();work_armed_=false;events.push_back({HealthKind::transaction_finished,ticket,now});
        } else if (message.type == "shutdown") {
            closed_ = true; events.push_back({HealthKind::shutdown, 0, now});
        } else throw w::Error("health.direction_or_feature");
    });
    if (!closed_) tick(observed_ms);
    return events;
} catch (...) {
    closed_ = true;
    output_.clear(); output_frames_ = 0;
    throw;
}
void HealthLink::tick(std::uint64_t now) try {
    if (closed_) throw w::Error("health.closed");
    if (!ready_ && now - connected_ms_ >= 5000) throw w::Error("health.handshake_timeout");
    decoder_.tick(now);
} catch (...) { closed_ = true; output_.clear(); output_frames_ = 0; throw; }
void HealthLink::heartbeat(std::uint64_t sequence) { send("heartbeat", {{"sequence", std::to_string(sequence)}}); }
void HealthLink::challenge(std::uint64_t generation) try {
    if (!server_ || !progress_ || pending_ || (completed_ && generation <= *completed_)) throw w::Error("health.challenge_order");
    send("render.challenge", {{"generation", std::to_string(generation)}}); pending_ = generation;
} catch (...) { closed_ = true; output_.clear(); output_frames_ = 0; throw; }
void HealthLink::progress(std::uint64_t generation) try {
    if (server_ || !progress_ || !pending_ || generation != *pending_) throw w::Error("health.progress_order");
    send("render.progress", {{"generation", std::to_string(generation)}}); completed_ = generation; pending_.reset();
} catch (...) { closed_ = true; output_.clear(); output_frames_ = 0; throw; }
void HealthLink::shutdown() { send("shutdown", {{"reason", "normal"}}); closed_ = true; }
void HealthLink::transaction_started(std::uint64_t ticket)try{
    if(!transactions_||server_||!ticket||work_pending_||(work_completed_&&ticket<=*work_completed_))throw w::Error("health.transaction_order");
    send("transaction.started",{{"ticket",std::to_string(ticket)}});work_pending_=ticket;work_armed_=false;
}catch(...){closed_=true;output_.clear();output_frames_=0;throw;}
void HealthLink::transaction_armed(std::uint64_t ticket)try{
    if(!transactions_||!server_||!work_pending_||*work_pending_!=ticket||work_armed_)throw w::Error("health.transaction_order");
    send("transaction.armed",{{"ticket",std::to_string(ticket)}});work_armed_=true;
}catch(...){closed_=true;output_.clear();output_frames_=0;throw;}
void HealthLink::transaction_finished(std::uint64_t ticket)try{
    if(!transactions_||server_||!work_pending_||*work_pending_!=ticket||!work_armed_)throw w::Error("health.transaction_order");
    send("transaction.finished",{{"ticket",std::to_string(ticket)}});work_completed_=ticket;work_pending_.reset();work_armed_=false;
}catch(...){closed_=true;output_.clear();output_frames_=0;throw;}
} // namespace syspane::recovery
