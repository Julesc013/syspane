#include "session.hpp"

namespace syspane::configuration {
using protocol::Error;
namespace {
protocol::Handshake server_hello(const std::string& epoch, const std::optional<InventorySource>& source) {
    protocol::Handshake hello{1, protocol::frame_limit, "console", epoch,
        {{"command", "0.2.0"}, {"command-result", "0.1.0"}}, {}, {"settings.preview", "result.get", "cancel"}};
    if (source) {
        const auto& version = source->document_version;
        hello.documents.insert({{"telemetry",version},{"snapshot",version},{"observation",version}});
        hello.optional.insert("telemetry.snapshot");
        if (version=="0.2.0") hello.optional.insert("telemetry.measured-time");
    }
    return hello;
}
Json welcome(const std::string& epoch, const protocol::Negotiated& selected) {
    Json docs = Json::array();
    for (const auto& doc : selected.documents) docs.push_back({{"document", doc.first}, {"version", doc.second}});
    return {{"wire_major", 0}, {"wire_minor", selected.minor}, {"role", "console"}, {"producer_epoch", epoch},
        {"max_frame_bytes", selected.max_frame_bytes}, {"document_versions", std::move(docs)},
        {"required_features", Json::array()}, {"optional_features", selected.features}};
}
bool may_request(const Authority& authority, const Policy& policy) {
    const std::set<std::string> roles = {"console", "desktop", "saver_settings"};
    return authority.authenticated && authority.role_grants.count(authority.role) && roles.count(authority.role) &&
        policy.available && !policy.denied_capabilities.count("settings.preview") && !policy.denied_capabilities.count("settings.set");
}
}
Sessions::Sessions(std::string epoch, std::uint64_t revision, Policy policy, std::optional<InventorySource> source)
    : epoch_(std::move(epoch)), revision_(revision), policy_(std::move(policy)), source_(std::move(source)) {
    if (!protocol::identifier(epoch_)) throw Error("session.epoch");
    if (source_) {
        const auto hello=server_hello(epoch_,source_);
        protocol::validate_telemetry_binding({{1,protocol::frame_limit,hello.documents,hello.optional},
            "validation",epoch_,source_->producer,"validation",source_->channel,source_->classification,
            policy_.revision,protocol::TelemetryDirection::consumer_to_producer,source_->document_version,source_->clock_id,source_->clock_scope});
    }
}
void Sessions::open(const std::string& id, std::string principal, Authority authority, std::uint64_t now) {
    tick(now);
    if (!authority.authenticated || authority.role_grants.empty()) throw Error("session.unauthenticated");
    if (!protocol::identifier(id) || !protocol::identifier(principal)) throw Error("session.identity");
    if (connections_.count(id)) throw Error("session.collision");
    if (connections_.size() >= 16) throw Error("session.capacity");
    connections_.emplace(id, Connection{id, std::move(principal), std::move(authority), now, false, {}, {1, protocol::frame_limit, {}, {}}, {}});
}
void Sessions::shut(Connection& c, const char* reason) { c.ticket = 0; c.generation.reset(); c.reason = reason; c.outbox.close(); }
void Sessions::tick(std::uint64_t now) {
    if (clock_fault_ || (last_ && now < *last_)) {
        clock_fault_ = true;
        for (auto& entry : connections_) shut(entry.second,"clock.regressed");
        throw Error("clock.regressed");
    }
    last_ = now;
    for (auto& entry : connections_) {
        auto& c = entry.second;
        if (!c.negotiated && !c.outbox.closed() && now - c.opened >= protocol::deadline_ms) shut(c, "handshake.timeout");
        if (c.ticket && now - c.renewed >= 3000) shut(c,"subscription.expired");
    }
}
std::string Sessions::envelope(const Connection& c, const std::string& type, Json body) const {
    return Json{{"type", type}, {"body", std::move(body)}, {"connection_id", c.id}, {"producer_epoch", epoch_}}.dump();
}
bool Sessions::queue(Connection& c, const std::string& type, Json body) {
    auto payload = envelope(c, type, std::move(body));
    if (payload.size() > c.selection.max_frame_bytes || !c.outbox.control(std::move(payload))) {
        shut(c, "queue.control_full"); return false;
    }
    return true;
}
void Sessions::receive(const std::string& id, std::string_view payload, std::uint64_t now) {
    tick(now);
    auto& c = connections_.at(id);
    if (c.outbox.closed()) throw Error("session.closed");
    try {
        if (payload.size() > c.selection.max_frame_bytes) throw Error("frame.length");
        dispatch(c, protocol::decode(payload), now);
    } catch (const Error& error) { shut(c, error.what()); }
      catch (const Json::exception&) { shut(c,"telemetry.body"); }
      catch (const std::bad_alloc&) { shut(c,"session.capacity"); }
}
void Sessions::dispatch(Connection& c, const protocol::Message& message, std::uint64_t now) {
    if (!c.negotiated) {
        if (message.type != "hello") throw Error("session.expected_hello");
        const auto client = protocol::handshake(message.body);
        c.selection = protocol::negotiate(server_hello(epoch_,source_), client, c.authority.role_grants);
        c.authority.role = client.role;
        const bool has_commands = c.selection.documents.count({"command", "0.2.0"}) && c.selection.documents.count({"command-result", "0.1.0"});
        if (!has_commands) {
            for (const auto& feature : {"settings.preview", "result.get", "cancel"}) {
                if (client.required.count(feature)) throw Error("handshake.document_version");
                c.selection.features.erase(feature);
            }
        }
        const auto version = source_ ? source_->document_version : "0.1.0";
        if (!c.selection.documents.count({"telemetry",version}) || !c.selection.documents.count({"snapshot",version}) ||
            !c.selection.documents.count({"observation",version}) ||
            (version=="0.2.0" && !c.selection.features.count("telemetry.measured-time"))) {
            if (client.required.count("telemetry.snapshot") || client.required.count("telemetry.measured-time")) throw Error("handshake.document_version");
            c.selection.features.erase("telemetry.snapshot"); c.selection.features.erase("telemetry.measured-time");
        }
        c.negotiated = true;
        queue(c, "welcome", welcome(epoch_, c.selection));
        return;
    }
    if (message.type == "hello" || message.connection_id != c.id || message.producer_epoch != epoch_)
        throw Error("session.identity");
    if (message.type == "shutdown") { shut(c, "peer.shutdown"); return; }
    if (message.type == "heartbeat") {
        const auto sequence = *protocol::decimal(message.body["sequence"].get_ref<const std::string&>());
        if (!c.heartbeat || sequence > *c.heartbeat) {
            c.heartbeat = sequence;
            if (c.ticket) c.renewed = now;
        }
        queue(c, "heartbeat", message.body); return;
    }
    if (message.type == "subscribe" || message.type == "unsubscribe") { subscribe(c,message,now); return; }
    if (message.type == "command") {
        if (!c.selection.features.count("settings.preview")) throw Error("feature.unsupported");
        const auto& body = message.body;
        if (!body.contains("request_id") || !body["request_id"].is_string() ||
            !protocol::identifier(body["request_id"].get_ref<const std::string&>())) throw Error("command.identity");
        const auto request = body["request_id"].get<std::string>();
        auto decision = message.body_bytes.size() > 16384 ? Decision{"invalid", "command.size"} : preview(body, c.authority, policy_, revision_);
        const auto prior = may_request(c.authority, policy_) ? ledger_.get(c.principal, request, now) : std::nullopt;
        if (prior && prior->body != message.body_bytes) decision = {"conflict", "request.changed"};
        auto reply = result(decision, request, epoch_, revision_);
        // Reserve bounded reply capacity before any request-ledger admission.
        auto required = envelope(c, "result", reply).size();
        for (const auto& alternative : {Decision{"conflict", "request.changed"}, Decision{"busy", "request.capacity"}, Decision{"busy", "request.pending"}})
            required = std::max(required, envelope(c, "result", result(alternative, request, epoch_, revision_)).size());
        if (required > c.selection.max_frame_bytes || !c.outbox.can_control(required)) {
            shut(c, "queue.control_full"); return;
        }
        if (decision.outcome == "preview") {
            const auto admission = ledger_.admit(c.principal, c.id, request, message.body_bytes, now);
            switch (admission) {
            case protocol::Admission::admitted:
                ledger_.finish(c.principal, request, reply.dump(), false, now); break;
            case protocol::Admission::replay:
                reply = protocol::parse(ledger_.get(c.principal, request, now)->result); break;
            case protocol::Admission::conflict:
                reply = result({"conflict", "request.changed"}, request, epoch_, revision_); break;
            case protocol::Admission::busy:
                reply = result({"busy", "request.capacity"}, request, epoch_, revision_); break;
            case protocol::Admission::pending:
                reply = result({"busy", "request.pending"}, request, epoch_, revision_); break;
            }
        }
        queue(c, "result", std::move(reply));
        return;
    }
    if (message.type == "result.get" || message.type == "cancel") {
        if (!c.selection.features.count(message.type)) throw Error("feature.unsupported");
        const auto request = message.body["request_id"].get<std::string>();
        if (!may_request(c.authority, policy_)) {
            queue(c, "result", result({"denied", "policy.denied"}, request, epoch_, revision_)); return;
        }
        auto record = ledger_.get(c.principal, request, now);
        if (message.type == "cancel" && record && !record->finished_ms) {
            // Present previews finish synchronously. W-08 must recheck here before
            // admitting any asynchronous durable-command integration.
            record = ledger_.cancel(c.principal, request, result({"cancelled", "request.cancelled"}, request, epoch_, revision_).dump(), now);
        }
        queue(c, "result", record && record->finished_ms ? protocol::parse(record->result) :
            result({"unknown", "request.reconcile"}, request, epoch_, revision_));
        return;
    }
    throw Error("session.direction_or_feature");
}
std::optional<std::string> Sessions::pop(const std::string& id, std::uint64_t now) {
    tick(now);
    auto& c = connections_.at(id);
    if (c.ticket && !may_subscribe(c)) shut(c,"policy.denied");
    return c.outbox.pop();
}
void Sessions::disconnect(const std::string& id) { connections_.erase(id); }
void Sessions::policy(Policy next, std::uint64_t now) {
    // Invalidate before any fallible revision/time check. Never retain old data
    // because the caller's clock or policy adapter failed.
    for (auto& entry : connections_) {
        auto& c = entry.second; c.ticket = 0; c.generation.reset();
        if (!c.outbox.closed()) c.outbox = protocol::Outbox{};
    }
    if (next.revision <= policy_.revision) {
        policy_.available = false;
        for (auto& entry : connections_) shut(entry.second,"policy.revision");
        throw Error("policy.revision");
    }
    policy_ = std::move(next);
    tick(now);
    for (auto& entry : connections_) {
        auto& c = entry.second;
        if (c.negotiated && !c.outbox.closed()) {
            c.outbox.revoke(envelope(c, "gap", {{"reason", "policy_changed"}}));
            if (c.outbox.closed()) c.reason = "queue.control_full";
        }
    }
}
bool Sessions::may_subscribe(const Connection& c) const {
    if (!source_ || !policy_.available || policy_.denied_capabilities.count("telemetry.subscribe")) return false;
    const std::map<std::string,std::string> channels{{"desktop","desktop"},{"console","inspector"},{"saver","saver"},{"preview","preview"}};
    const auto role = channels.find(c.authority.role);
    return role != channels.end() && role->second == source_->channel &&
        permits(c.authority,policy_,source_->channel,source_->classification) && permits(c.authority,policy_,"accessibility",source_->classification);
}
protocol::TelemetryBinding Sessions::binding(const Connection& c, const std::string& subscription, protocol::TelemetryDirection direction) const {
    return {c.selection,c.id,epoch_,source_->producer,subscription,source_->channel,source_->classification,policy_.revision,direction,
            source_->document_version,source_->clock_id,source_->clock_scope};
}
void Sessions::subscribe(Connection& c, const protocol::Message& message, std::uint64_t now) {
    if (!source_ || !c.selection.features.count("telemetry.snapshot")) throw Error("feature.unsupported");
    if (!may_subscribe(c)) throw Error("policy.denied");
    if (!message.body.contains("subscription_id") || !message.body["subscription_id"].is_string()) throw Error("telemetry.body");
    const auto id = message.body["subscription_id"].get<std::string>();
    protocol::encode_telemetry(message,binding(c,id,protocol::TelemetryDirection::consumer_to_producer));
    if (message.type == "unsubscribe") {
        if (c.subscription_id != id) throw Error("subscription.identity");
        c.ticket = 0; c.generation.reset(); c.outbox.discard_data(); return;
    }
    if (!c.subscription_id.empty() && (!c.ticket || c.subscription_id != id || c.subscription_body != message.body_bytes))
        throw Error("subscription.conflict");
    if (tickets_ >= source_->ticket_limit) throw Error("subscription.capacity");
    if (c.subscription_id.empty()) {
        c.subscription_id = id; c.subscription_body = message.body_bytes; c.renewed = now;
    }
    c.ticket = ++tickets_; c.generation.reset(); c.outbox.discard_data();
}
std::optional<Subscription> Sessions::subscription(const std::string& id) const {
    const auto found = connections_.find(id);
    if (found == connections_.end() || !found->second.ticket) return {};
    const auto& c = found->second;
    return Subscription{binding(c,c.subscription_id,protocol::TelemetryDirection::producer_to_consumer),c.ticket};
}
std::size_t Sessions::demand_count() const {
    std::size_t count = 0; for (const auto& entry : connections_) if (entry.second.ticket) ++count; return count;
}
void Sessions::resync(Connection& c, const char* reason) {
    c.generation.reset(); c.outbox.revoke(envelope(c,"gap",{{"reason",reason}}));
    if (c.outbox.closed()) shut(c,"queue.control_full");
}
bool Sessions::offer(const std::string& id, std::uint64_t ticket, const std::string& record,
                     const Json& snapshot, std::optional<std::uint64_t> base, std::uint64_t now) {
    auto found = connections_.find(id);
    if (!ticket || found == connections_.end() || found->second.ticket != ticket) return false;
    tick(now);
    auto& c = found->second;
    if (!c.ticket) return false;
    if (!may_subscribe(c)) { shut(c,"policy.denied"); return false; }
    try {
        Json body{{"schema_version",source_->document_version},{"subscription_id",c.subscription_id},{"producer_id",source_->producer},
            {"policy_revision",std::to_string(policy_.revision)},{"record_id",record},{"snapshot",snapshot}};
        if (source_->document_version=="0.2.0") body["clock_id"]=source_->clock_id;
        if (base) body["base_generation"] = std::to_string(*base);
        const std::string type = base ? "delta" : "snapshot";
        protocol::Message message{type,id,epoch_,body.dump(),body};
        const auto payload = protocol::encode_telemetry(message,binding(c,c.subscription_id,protocol::TelemetryDirection::producer_to_consumer));
        const auto generation = *protocol::decimal(snapshot["generation"].get_ref<const std::string&>());
        if (snapshot["completeness"] != "complete" || (base && (!c.generation || *base != *c.generation)) ||
            (c.generation && generation < *c.generation)) { resync(c,"resync_required"); return false; }
        if (!c.outbox.data(payload,envelope(c,"gap",{{"reason","queue_overflow"}}))) {
            c.generation.reset(); if (c.outbox.closed()) shut(c,"queue.control_full"); return false;
        }
        c.generation = generation; return true;
    } catch (const Error& error) { shut(c,error.what()); }
      catch (const Json::exception&) { shut(c,"telemetry.body"); }
      catch (const std::bad_alloc&) { shut(c,"session.capacity"); }
    return false;
}
bool Sessions::closed(const std::string& id) const { return connections_.at(id).outbox.closed(); }
std::string Sessions::close_reason(const std::string& id) const { return connections_.at(id).reason; }
std::size_t Sessions::frame_bound(const std::string& id) const { return connections_.at(id).selection.max_frame_bytes; }
} // namespace syspane::configuration
