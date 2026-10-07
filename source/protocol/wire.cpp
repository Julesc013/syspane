#include "wire.hpp"
#include "reconciliation.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <regex>
#include <vector>

namespace syspane::protocol {
namespace {
bool alpha_numeric(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9');
}
bool id_value(const Json& value) {
    return value.is_string() && identifier(value.get_ref<const std::string&>());
}
std::uint64_t bounded_number(const Json& value, std::uint64_t low, std::uint64_t high) {
    // JSON Schema's integer type includes numbers such as 1.0 and 1e0.
    if (value.is_number_float()) {
        const auto number = value.get<double>();
        if (std::isfinite(number) && std::floor(number) == number && number >= static_cast<double>(low) &&
            number <= static_cast<double>(high)) return static_cast<std::uint64_t>(number);
        throw Error("handshake.invalid");
    }
    if (!value.is_number_integer() || (!value.is_number_unsigned() && value.get<std::int64_t>() < 0))
        throw Error("handshake.invalid");
    const auto number = value.get<std::uint64_t>();
    if (number < low || number > high) throw Error("handshake.invalid");
    return number;
}
std::set<std::string> features(const Json& value) {
    if (!value.is_array() || value.size() > 64) throw Error("handshake.invalid");
    std::set<std::string> result;
    for (const auto& item : value) {
        if (!id_value(item) || !result.insert(item.get<std::string>()).second)
            throw Error("handshake.invalid");
    }
    return result;
}
}
bool identifier(std::string_view value) {
    if (value.empty() || value.size() > 256 || !alpha_numeric(value.front())) return false;
    return std::all_of(value.begin(), value.end(), [](char c) {
        return alpha_numeric(c) || c == ':' || c == '.' || c == '_' || c == '/' || c == '-';
    });
}
std::optional<std::uint64_t> decimal(std::string_view value) {
    if (value.empty() || value.size() > 20 || (value.size() > 1 && value.front() == '0')) return {};
    std::uint64_t result = 0;
    for (const auto c : value) {
        if (c < '0' || c > '9') return {};
        const auto digit = static_cast<unsigned>(c - '0');
        if (result > (std::numeric_limits<std::uint64_t>::max() - digit) / 10) return {};
        result = result * 10 + digit;
    }
    return result;
}
bool members(const Json& value, std::initializer_list<const char*> names) {
    if (!value.is_object() || value.size() != names.size()) return false;
    return std::all_of(names.begin(), names.end(), [&](const char* name) { return value.contains(name); });
}
Json parse(std::string_view bytes,ParseProfile profile) {
    if (bytes.empty() || bytes.size() > frame_limit) throw Error("json.size");
    if (bytes.back() == '\n' || bytes.substr(0, 3) == "\xef\xbb\xbf") throw Error("json.encoding");
    std::vector<std::set<std::string>> object_keys;
    std::size_t nodes = 0;
    try {
        return Json::parse(bytes.begin(), bytes.end(), [&](int depth, Json::parse_event_t event, Json& value) {
            using E = Json::parse_event_t;
            const bool container = event == E::object_start || event == E::array_start;
            if (container && depth >= (profile==ParseProfile::large_command?40:32)) throw Error("json.depth");
            if (container || event == E::key || (event == E::value && !value.is_structured())) {
                if (++nodes > (profile==ParseProfile::large_command?18432U:16384U)) throw Error("json.nodes");
            }
            if (event == E::object_start) object_keys.emplace_back();
            if (event == E::key && !object_keys.back().insert(value.get<std::string>()).second)
                throw Error("json.duplicate_key");
            if (event == E::object_end) object_keys.pop_back();
            return true;
        });
    } catch (const Json::exception&) {
        throw Error("json.invalid");
    }
}
std::string frame(std::string_view payload, std::size_t limit) {
    if (limit == 0 || limit > frame_limit || payload.empty() || payload.size() > limit)
        throw Error("frame.length");
    const auto n = static_cast<std::uint32_t>(payload.size());
    std::string result;
    result.reserve(n + 4);
    for (int shift = 24; shift >= 0; shift -= 8) result.push_back(static_cast<char>((n >> shift) & 255));
    result.append(payload);
    return result;
}
Framer::Framer(std::size_t limit) : limit_(limit) {
    if (limit == 0 || limit > frame_limit) throw Error("frame.length");
}
[[noreturn]] void Framer::fail(const char* code) {
    closed_ = true;
    payload_.clear();
    throw Error(code);
}
void Framer::tick(std::uint64_t now) {
    if (closed_) throw Error("frame.closed");
    if (last_ && now < *last_) fail("clock.regressed");
    last_ = now;
    if (started_ && now - *started_ >= deadline_ms) fail("frame.timeout");
}
void Framer::feed(std::string_view bytes, std::uint64_t now,
                  const std::function<void(std::string_view)>& consume) {
    tick(now);
    while (!bytes.empty()) {
        if (!started_) started_ = now;
        if (prefix_size_ < 4) {
            prefix_[prefix_size_++] = static_cast<unsigned char>(bytes.front());
            bytes.remove_prefix(1);
            if (prefix_size_ != 4) continue;
            expected_ = (static_cast<std::uint32_t>(prefix_[0]) << 24) |
                        (static_cast<std::uint32_t>(prefix_[1]) << 16) |
                        (static_cast<std::uint32_t>(prefix_[2]) << 8) | prefix_[3];
            if (expected_ == 0 || expected_ > limit_) fail("frame.length");
            payload_.reserve(expected_);
        }
        const auto amount = std::min(bytes.size(), expected_ - payload_.size());
        payload_.append(bytes.substr(0, amount));
        bytes.remove_prefix(amount);
        if (payload_.size() == expected_) {
            try { consume(payload_); } catch (...) { closed_ = true; throw; }
            payload_.clear();
            prefix_size_ = expected_ = 0;
            started_.reset();
        }
    }
}
void Framer::eof() {
    if (closed_) throw Error("frame.closed");
    if (prefix_size_ || !payload_.empty()) fail("frame.truncated");
    closed_ = true;
}
void Framer::restrict_limit(std::size_t limit) {
    if (closed_) throw Error("frame.closed");
    if (limit == 0 || limit > limit_) fail("frame.length");
    // May be called by the completed-hello callback before coalesced next input.
    if (prefix_size_ && (prefix_size_ != 4 || payload_.size() != expected_)) fail("frame.state");
    limit_ = limit;
}
Message decode(std::string_view payload,bool large_commands) {
    auto root = parse(payload,large_commands?ParseProfile::large_command:ParseProfile::ordinary);
    // Negotiated headroom belongs exclusively to command 0.5, including its envelope.
    if(large_commands&&!(root.is_object()&&root.value("type",Json())=="command"&&root.contains("body")&&
        root["body"].is_object()&&root["body"].value("schema_version",Json())=="0.5.0"))root=parse(payload);
    if (!root.is_object() || !root.contains("type") || !root["type"].is_string())
        throw Error("envelope.invalid");
    Message message;
    message.type = root["type"].get<std::string>();
    const std::set<std::string> types = {"hello", "welcome", "command", "result", "subscribe", "unsubscribe",
        "snapshot", "delta", "gap", "heartbeat", "cancel", "result.get", "result.reconcile", "result.reconciled", "shutdown", "render.challenge", "render.progress",
        "transaction.started","transaction.armed","transaction.finished"};
    if (!types.count(message.type)) throw Error("message.unknown");
    if (message.type == "hello") {
        if (!members(root, {"type", "body"})) throw Error("envelope.invalid");
    } else {
        if (!members(root, {"type", "body", "connection_id", "producer_epoch"}) ||
            !id_value(root["connection_id"]) || !id_value(root["producer_epoch"])) throw Error("envelope.invalid");
        message.connection_id = root["connection_id"].get<std::string>();
        message.producer_epoch = root["producer_epoch"].get<std::string>();
    }
    const auto& body = root.at("body");
    if (!body.is_object()) throw Error("body.invalid");
    const auto first = body.start_pos(), end = body.end_pos();
    if (first >= end || end > payload.size()) throw Error("body.position");
    message.body_bytes = std::string(payload.substr(first, end - first));
    message.body = body;
    if (message.type == "hello" || message.type == "welcome") handshake(body);
    if(message.type=="result.reconcile"){
        if(message.body_bytes.size()>2048)throw Error("reconciliation.size");
        validate_reconciliation_request(body);
    }
    if(message.type=="result.reconciled"){
        if(message.body_bytes.size()>5632)throw Error("reconciliation.size");
        validate_reconciliation_result(body,message.producer_epoch);
    }
    if (message.type == "cancel" || message.type == "result.get") {
        if (!members(body, {"request_id"}) || !id_value(body["request_id"])) throw Error("body.invalid");
    }
    if (message.type == "heartbeat") {
        if (!members(body, {"sequence"}) || !body["sequence"].is_string() ||
            !decimal(body["sequence"].get_ref<const std::string&>())) throw Error("body.invalid");
    }
    if (message.type == "render.challenge" || message.type == "render.progress") {
        if (!members(body, {"generation"}) || !body["generation"].is_string() ||
            !decimal(body["generation"].get_ref<const std::string&>())) throw Error("body.invalid");
    }
    if(message.type=="transaction.started"||message.type=="transaction.armed"||message.type=="transaction.finished"){
        if(!members(body,{"ticket"})||!body["ticket"].is_string())throw Error("body.invalid");
        const auto ticket=decimal(body["ticket"].get_ref<const std::string&>());
        if(!ticket||!*ticket)throw Error("body.invalid");
    }
    if (message.type == "gap" || message.type == "shutdown") {
        if (!members(body, {"reason"}) || !body["reason"].is_string()) throw Error("body.invalid");
        const auto reason = body["reason"].get<std::string>();
        const std::set<std::string> allowed = message.type == "gap"
            ? std::set<std::string>{"policy_changed", "queue_overflow", "resync_required"}
            : std::set<std::string>{"normal", "policy_changed", "protocol_error", "resource_limit"};
        if (!allowed.count(reason)) throw Error("body.invalid");
    }
    return message;
}
void validate_reconciliation_request(const Json& value){
    if(!members(value,{"schema_version","query_id","original_producer_epoch","request_id"})||value["schema_version"]!="0.1.0"||
       !id_value(value["query_id"])||!id_value(value["original_producer_epoch"])||!id_value(value["request_id"])||value.dump().size()>2048)
        throw Error("reconciliation.request");
}
void validate_reconciliation_result(const Json& value,const std::string& epoch){
    if(!members(value,{"schema_version","query_id","original_producer_epoch","request_id","result"})||value.dump().size()>5632)
        throw Error("reconciliation.result");
    auto query=value;query.erase("result");validate_reconciliation_request(query);
    const auto& r=value["result"];
    if(!members(r,{"schema_version","request_id","producer_epoch","outcome","revision","stored","durable","visible","activation","error"})||
       r["schema_version"]!="0.1.0"||r["request_id"]!=value["request_id"]||r["producer_epoch"]!=epoch||!identifier(epoch)||r.dump().size()>4096)
        throw Error("reconciliation.result");
    if(r["outcome"]=="accepted"){
        if(!r["revision"].is_string()||!decimal(r["revision"].get_ref<const std::string&>())||r["stored"]!=true||r["durable"]!=true||r["visible"]!=false||
           !r["error"].is_null()||!r["activation"].is_array()||r["activation"].size()!=1)throw Error("reconciliation.facts");
        const auto& a=r["activation"][0];
        if(!members(a,{"component","state","reason"})||a["component"]!="presentation"||a["state"]!="pending"||!a["reason"].is_string()||a["reason"].get_ref<const std::string&>().size()>2048)
            throw Error("reconciliation.activation");
    }else if(r["outcome"]=="unknown"){
        if(!r["revision"].is_null()||!r["stored"].is_null()||!r["durable"].is_null()||!r["visible"].is_null()||
           !r["activation"].is_array()||!r["activation"].empty())throw Error("reconciliation.facts");
        const auto& e=r["error"];
        if(!members(e,{"code","message","retryable"})||!id_value(e["code"])||!e["message"].is_string()||e["message"].get_ref<const std::string&>().empty()||
           e["message"].get_ref<const std::string&>().size()>2048||!e["retryable"].is_boolean())throw Error("reconciliation.error");
    }else throw Error("reconciliation.outcome");
}
Json consume_reconciliation(const Message& message,const Negotiated& selected,const Json& query,const std::string& connection,const std::string& epoch){
    validate_reconciliation_request(query);
    if(!selected.features.count("result.reconcile")||selected.max_frame_bytes<8192||
       !selected.documents.count({"reconciliation-request","0.1.0"})||!selected.documents.count({"reconciliation-result","0.1.0"})||
       !selected.documents.count({"command-result","0.1.0"}))throw Error("reconciliation.negotiation");
    if(message.type!="result.reconciled"||message.connection_id!=connection||message.producer_epoch!=epoch)throw Error("reconciliation.scope");
    validate_reconciliation_result(message.body,epoch);
    auto echoed=message.body;echoed.erase("result");if(echoed!=query)throw Error("reconciliation.scope");
    return message.body["result"];
}
Handshake handshake(const Json& body) {
    if (!members(body, {"wire_major", "wire_minor", "role", "producer_epoch", "max_frame_bytes",
                       "document_versions", "required_features", "optional_features"})) throw Error("handshake.invalid");
    bounded_number(body["wire_major"], 0, 0);
    Handshake result;
    result.minor = static_cast<unsigned>(bounded_number(body["wire_minor"], 1, 65535));
    result.max_frame_bytes = static_cast<std::size_t>(bounded_number(body["max_frame_bytes"], 1024, frame_limit));
    const std::set<std::string> roles = {"desktop", "console", "collector", "saver", "preview", "saver_settings", "diagnostic", "maintenance"};
    if (!body["role"].is_string() || !roles.count(body["role"].get<std::string>()) || !id_value(body["producer_epoch"]))
        throw Error("handshake.invalid");
    result.role = body["role"].get<std::string>();
    result.epoch = body["producer_epoch"].get<std::string>();
    const auto& docs = body["document_versions"];
    if (!docs.is_array() || docs.empty() || docs.size() > 32) throw Error("handshake.invalid");
    const std::regex version("^[0-9]+\\.[0-9]+\\.[0-9]+(-[A-Za-z0-9.-]+)?$");
    for (const auto& doc : docs) {
        if (!members(doc, {"document", "version"}) || !id_value(doc["document"]) || !doc["version"].is_string())
            throw Error("handshake.invalid");
        const auto v = doc["version"].get<std::string>();
        if (v.size() > 64 || !std::regex_match(v, version) ||
            !result.documents.emplace(doc["document"].get<std::string>(), v).second) throw Error("handshake.invalid");
    }
    result.required = features(body["required_features"]);
    result.optional = features(body["optional_features"]);
    return result;
}
Negotiated negotiate(const Handshake& server, const Handshake& client, const std::set<std::string>& grants) {
    if (!grants.count(client.role)) throw Error("handshake.role_denied");
    auto server_features = server.required, client_features = client.required;
    server_features.insert(server.optional.begin(), server.optional.end());
    client_features.insert(client.optional.begin(), client.optional.end());
    for (const auto& feature : client.required)
        if (!server_features.count(feature)) throw Error("handshake.required_feature");
    for (const auto& feature : server.required)
        if (!client_features.count(feature)) throw Error("handshake.required_feature");
    Negotiated result{std::min(server.minor, client.minor), std::min(server.max_frame_bytes, client.max_frame_bytes), {}, {}};
    std::set_intersection(server.documents.begin(), server.documents.end(), client.documents.begin(), client.documents.end(),
                          std::inserter(result.documents, result.documents.end()));
    if (result.documents.empty()) throw Error("handshake.document_version");
    std::set_intersection(server_features.begin(), server_features.end(), client_features.begin(), client_features.end(),
                          std::inserter(result.features, result.features.end()));
    return result;
}
} // namespace syspane::protocol
