#include "telemetry.hpp"
#include <algorithm>
#include <cmath>
#include <new>
#include <set>

namespace syspane::protocol {
namespace {
void need(bool ok, const char* code = "telemetry.body") { if (!ok) throw Error(code); }
const std::string& text(const Json& v, std::size_t max) {
    need(v.is_string()); const auto& s = v.get_ref<const std::string&>(); need(s.size() <= max); return s;
}
std::string id(const Json& v) { const auto& s = text(v, 256); need(identifier(s)); return s; }
std::uint64_t number(const Json& v) {
    const auto n = decimal(text(v, 20)); need(n.has_value()); return *n;
}
bool one(const Json& v, std::initializer_list<const char*> choices) {
    if (!v.is_string()) return false;
    const auto& s = v.get_ref<const std::string&>();
    return std::any_of(choices.begin(), choices.end(), [&](const char* c) { return s == c; });
}
void object(const Json& v, std::initializer_list<const char*> required, bool extensions = false) {
    need(v.is_object() && (v.size() == required.size() || (extensions && v.size() == required.size()+1 && v.contains("extensions"))));
    for (const auto name : required) need(v.contains(name));
    if (extensions && v.contains("extensions")) {
        const auto& ext = v["extensions"]; need(ext.is_object() && ext.size() <= 64);
        for (auto it = ext.begin(); it != ext.end(); ++it) {
            const auto& key = it.key();
            need(!key.empty() && key.size() <= 128 && key[0] >= 'a' && key[0] <= 'z');
            for (const char ch : key) need((ch >= 'a' && ch <= 'z') || (ch >= '0' && ch <= '9') || ch == '_' || ch == '.' || ch == '-');
        }
    }
}
void array(const Json& v, std::size_t limit) { need(v.is_array() && v.size() <= limit); }
void timestamp(const Json& v) {
    const auto& s = text(v, 64); need(s.size() >= 20, "telemetry.time");
    auto digits = [&](std::size_t start, std::size_t count) {
        unsigned n = 0;
        need(start+count <= s.size(), "telemetry.time");
        for (auto i = start; i < start+count; ++i) { need(s[i] >= '0' && s[i] <= '9', "telemetry.time"); n = n*10+static_cast<unsigned>(s[i]-'0'); }
        return n;
    };
    need(s[4]=='-' && s[7]=='-' && (s[10]=='T' || s[10]=='t') && s[13]==':' && s[16]==':', "telemetry.time");
    const unsigned year = digits(0, 4), month = digits(5, 2), day = digits(8, 2);
    need(year >= 1 && month >= 1 && month <= 12, "telemetry.time");
    const unsigned days[] = {31,28,31,30,31,30,31,31,30,31,30,31};
    const bool leap = year%4 == 0 && (year%100 != 0 || year%400 == 0);
    need(day >= 1 && day <= days[month-1]+(month == 2 && leap ? 1U : 0U), "telemetry.time");
    need(digits(11, 2) <= 23 && digits(14, 2) <= 59 && digits(17, 2) <= 59, "telemetry.time");
    std::size_t pos = 19;
    if (s[pos] == '.') {
        const auto begin = ++pos;
        while (pos < s.size() && s[pos] >= '0' && s[pos] <= '9') ++pos;
        need(pos > begin && pos < s.size(), "telemetry.time");
    }
    if (s[pos] == 'Z' || s[pos] == 'z') need(pos+1 == s.size(), "telemetry.time");
    else {
        need((s[pos]=='+' || s[pos]=='-') && pos+6 == s.size() && s[pos+3]==':', "telemetry.time");
        need(digits(pos+1,2) <= 23 && digits(pos+4,2) <= 59, "telemetry.time");
    }
}
void value(const Json& v) {
    if (v.is_null()) return;
    object(v, {"kind", "data"}); need(v["kind"].is_string());
    const auto& kind = v["kind"].get_ref<const std::string&>(); const auto& data = v["data"];
    if (kind == "string") (void)text(data, 16384);
    else if (kind == "boolean") need(data.is_boolean());
    else if (kind == "number") need(data.is_number() && std::isfinite(data.get<double>()));
    else if (kind == "uint64") (void)number(data);
    else need(false);
}
void observation(const Json& o, const std::string& epoch, std::uint64_t generation) {
    object(o, {"schema_version","entity_id","field","value","unit","origin","support","acquisition","freshness","presence",
               "source_id","observed_at","attempted_at","producer_epoch","generation","sample_interval_ns","error"}, true);
    need(o["schema_version"] == "0.1.0");
    (void)id(o["entity_id"]); (void)id(o["field"]); (void)id(o["source_id"]);
    need(id(o["producer_epoch"]) == epoch && number(o["generation"]) <= generation, "telemetry.generation");
    value(o["value"]); need(!text(o["unit"], 64).empty());
    need(one(o["origin"], {"observed","derived","configured"}) && one(o["support"], {"supported","unsupported","unknown"}) &&
         one(o["acquisition"], {"success","pending","denied","failed","disabled"}) && one(o["freshness"], {"current","stale","unknown","not_applicable"}) &&
         one(o["presence"], {"present","absent","unknown"}));
    timestamp(o["attempted_at"]); if (!o["observed_at"].is_null()) timestamp(o["observed_at"]);
    if (!o["sample_interval_ns"].is_null()) (void)number(o["sample_interval_ns"]);
    const auto& e = o["error"];
    if (!e.is_null()) { object(e, {"code","message","retryable"}); (void)id(e["code"]); (void)text(e["message"], 2048); need(e["retryable"].is_boolean()); }
    need(!one(o["acquisition"], {"denied","failed"}) || !e.is_null());
}
void snapshot(const Json& s, const std::string& epoch) {
    object(s, {"schema_version","producer_epoch","generation","captured_at","entities","relationships","sources","observations","completeness"}, true);
    need(s["schema_version"] == "0.1.0" && id(s["producer_epoch"]) == epoch, "telemetry.binding");
    const auto generation = number(s["generation"]); timestamp(s["captured_at"]);
    need(one(s["completeness"], {"complete","partial","gap"}));
    array(s["entities"], 8192); array(s["sources"], 1024); array(s["relationships"], 16384); array(s["observations"], 65536);
    std::set<std::string> entities, sources;
    for (const auto& e : s["entities"]) {
        object(e, {"id","kind","display_name","identity","generation"}, true);
        need(entities.insert(id(e["id"])).second, "telemetry.graph"); (void)id(e["kind"]); (void)text(e["display_name"], 2048);
        need(number(e["generation"]) <= generation, "telemetry.generation");
        const auto& identity = e["identity"]; need(identity.is_object() && identity.size() <= 64);
        for (auto it = identity.begin(); it != identity.end(); ++it) { need(it.key().size() <= 256); (void)text(it.value(), 2048); }
    }
    for (const auto& src : s["sources"]) {
        object(src, {"id","kind","scope"}); need(sources.insert(id(src["id"])).second, "telemetry.graph");
        (void)id(src["kind"]); (void)id(src["scope"]);
    }
    for (const auto& edge : s["relationships"]) {
        object(edge, {"source","target","kind"}); (void)id(edge["kind"]);
        need(entities.count(id(edge["source"])) && entities.count(id(edge["target"])), "telemetry.graph");
    }
    std::set<std::pair<std::string,std::string>> observations;
    for (const auto& o : s["observations"]) {
        observation(o, epoch, generation);
        need(entities.count(id(o["entity_id"])) && sources.count(id(o["source_id"])) &&
             observations.emplace(id(o["entity_id"]), id(o["field"])).second, "telemetry.graph");
    }
}
Message checked(std::string_view payload, const TelemetryBinding& b) {
    need(b.negotiated.max_frame_bytes >= 1024 && b.negotiated.max_frame_bytes <= frame_limit &&
         !payload.empty() && payload.size() <= b.negotiated.max_frame_bytes, "telemetry.capacity");
    need(b.negotiated.features.count("telemetry.snapshot") && b.negotiated.documents.count({"telemetry","0.1.0"}) &&
         b.negotiated.documents.count({"snapshot","0.1.0"}) && b.negotiated.documents.count({"observation","0.1.0"}), "telemetry.feature");
    need(identifier(b.connection) && identifier(b.epoch) && identifier(b.producer) && identifier(b.subscription) &&
         one(Json(b.channel), {"desktop","inspector","saver","preview"}) && one(Json(b.classification), {"public","operational","sensitive"}), "telemetry.binding");
    auto message = decode(payload);
    need(message.connection_id == b.connection && message.producer_epoch == b.epoch, "telemetry.binding");
    const auto& body = message.body;
    const bool subscribe = message.type == "subscribe", unsubscribe = message.type == "unsubscribe";
    const bool full = message.type == "snapshot", delta = message.type == "delta";
    need(subscribe || unsubscribe || full || delta, "telemetry.direction");
    need((subscribe || unsubscribe) ? b.direction == TelemetryDirection::consumer_to_producer : b.direction == TelemetryDirection::producer_to_consumer, "telemetry.direction");
    if (subscribe) object(body, {"schema_version","subscription_id","producer_id","policy_revision","channel","classification"});
    else if (unsubscribe) object(body, {"schema_version","subscription_id"});
    else if (full) object(body, {"schema_version","subscription_id","producer_id","policy_revision","record_id","snapshot"});
    else object(body, {"schema_version","subscription_id","producer_id","policy_revision","record_id","snapshot","base_generation"});
    need(body["schema_version"] == "0.1.0");
    need(id(body["subscription_id"]) == b.subscription, "telemetry.binding");
    if (!unsubscribe) need(id(body["producer_id"]) == b.producer && number(body["policy_revision"]) == b.policy_revision, "telemetry.binding");
    if (subscribe) need(body["channel"] == b.channel && body["classification"] == b.classification, "telemetry.binding");
    if (full || delta) {
        (void)id(body["record_id"]); snapshot(body["snapshot"], b.epoch);
        if (delta) need(number(body["base_generation"]) < number(body["snapshot"]["generation"]), "telemetry.generation");
    }
    return message;
}
} // namespace
Message decode_telemetry(std::string_view payload, const TelemetryBinding& binding) {
    try { return checked(payload, binding); }
    catch (const Json::exception&) { throw Error("telemetry.body"); }
    catch (const std::bad_alloc&) { throw Error("telemetry.capacity"); }
}
std::string encode_telemetry(const Message& m, const TelemetryBinding& b) {
    try {
        need(b.negotiated.max_frame_bytes >= 1024 && b.negotiated.max_frame_bytes <= frame_limit &&
             m.body_bytes.size() <= b.negotiated.max_frame_bytes && identifier(m.connection_id) && identifier(m.producer_epoch), "telemetry.capacity");
        need(m.type == "subscribe" || m.type == "unsubscribe" || m.type == "snapshot" || m.type == "delta", "telemetry.direction");
        // IDs/types are restricted ASCII; original body bytes are revalidated below.
        auto payload = std::string("{\"type\":\"")+m.type+"\",\"connection_id\":\""+m.connection_id+"\",\"producer_epoch\":\""+m.producer_epoch+"\",\"body\":"+m.body_bytes+"}";
        const auto checked_message = checked(payload, b);
        need(checked_message.body == m.body, "telemetry.body");
        return payload;
    } catch (const Json::exception&) { throw Error("telemetry.body"); }
    catch (const std::bad_alloc&) { throw Error("telemetry.capacity"); }
}
} // namespace syspane::protocol
