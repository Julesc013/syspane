#include "session.hpp"

namespace syspane::configuration {
using protocol::Error;
namespace {
protocol::Handshake server_hello(const std::string& epoch) {
    return {1, protocol::frame_limit, "console", epoch,
        {{"command", "0.2.0"}, {"command-result", "0.1.0"}}, {}, {"settings.preview", "result.get", "cancel"}};
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
Sessions::Sessions(std::string epoch, std::uint64_t revision, Policy policy)
    : epoch_(std::move(epoch)), revision_(revision), policy_(std::move(policy)) {
    if (!protocol::identifier(epoch_)) throw Error("session.epoch");
}
void Sessions::open(const std::string& id, std::string principal, Authority authority, std::uint64_t now) {
    tick(now);
    if (!authority.authenticated || authority.role_grants.empty()) throw Error("session.unauthenticated");
    if (!protocol::identifier(id) || !protocol::identifier(principal)) throw Error("session.identity");
    if (connections_.count(id)) throw Error("session.collision");
    if (connections_.size() >= 16) throw Error("session.capacity");
    connections_.emplace(id, Connection{id, std::move(principal), std::move(authority), now, false, {}, {1, protocol::frame_limit, {}, {}}, {}});
}
void Sessions::shut(Connection& c, const char* reason) { c.reason = reason; c.outbox.close(); }
void Sessions::tick(std::uint64_t now) {
    if (last_ && now < *last_) throw Error("clock.regressed");
    last_ = now;
    for (auto& entry : connections_) {
        auto& c = entry.second;
        if (!c.negotiated && !c.outbox.closed() && now - c.opened >= protocol::deadline_ms) shut(c, "handshake.timeout");
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
}
void Sessions::dispatch(Connection& c, const protocol::Message& message, std::uint64_t now) {
    if (!c.negotiated) {
        if (message.type != "hello") throw Error("session.expected_hello");
        const auto client = protocol::handshake(message.body);
        c.selection = protocol::negotiate(server_hello(epoch_), client, c.authority.role_grants);
        c.authority.role = client.role;
        const bool has_commands = c.selection.documents.count({"command", "0.2.0"}) && c.selection.documents.count({"command-result", "0.1.0"});
        if (!has_commands) {
            for (const auto& feature : {"settings.preview", "result.get", "cancel"}) {
                if (client.required.count(feature)) throw Error("handshake.document_version");
                c.selection.features.erase(feature);
            }
        }
        c.negotiated = true;
        queue(c, "welcome", welcome(epoch_, c.selection));
        return;
    }
    if (message.type == "hello" || message.connection_id != c.id || message.producer_epoch != epoch_)
        throw Error("session.identity");
    if (message.type == "shutdown") { shut(c, "peer.shutdown"); return; }
    if (message.type == "heartbeat") { queue(c, "heartbeat", message.body); return; }
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
    return connections_.at(id).outbox.pop();
}
void Sessions::disconnect(const std::string& id) { connections_.erase(id); }
void Sessions::policy(Policy next, std::uint64_t now) {
    tick(now);
    if (next.revision <= policy_.revision) throw Error("policy.revision");
    policy_ = std::move(next);
    for (auto& entry : connections_) {
        auto& c = entry.second;
        if (c.negotiated && !c.outbox.closed()) {
            c.outbox.revoke(envelope(c, "gap", {{"reason", "policy_changed"}}));
            if (c.outbox.closed()) c.reason = "queue.control_full";
        }
    }
}
bool Sessions::closed(const std::string& id) const { return connections_.at(id).outbox.closed(); }
std::string Sessions::close_reason(const std::string& id) const { return connections_.at(id).reason; }
std::size_t Sessions::frame_bound(const std::string& id) const { return connections_.at(id).selection.max_frame_bytes; }
} // namespace syspane::configuration
