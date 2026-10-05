#include "reported_state.hpp"
#include <algorithm>

namespace syspane::recovery::detail {
namespace {
using protocol::Json;
std::uint64_t integer(const Json& value) { return *protocol::decimal(value.get_ref<const std::string&>()); }
model::UtcTime utc(const Json& value) {
    const auto& s = value.get_ref<const std::string&>();
    const auto digits = [&](std::size_t begin, std::size_t count) {
        std::int64_t n = 0; for (auto i = begin; i < begin+count; ++i) n = n*10+(s[i]-'0'); return n;
    };
    const auto year = digits(0,4), month = digits(5,2), day = digits(8,2), before = year-1;
    const int month_days[] = {31,28,31,30,31,30,31,31,30,31,30,31};
    std::int64_t days = before*365+before/4-before/100+before/400;
    for (std::int64_t m=1; m<month; ++m) days += month_days[m-1];
    if (month>2 && year%4==0 && (year%100!=0 || year%400==0)) ++days;
    days += day-1-719162; // Gregorian day index of 1970-01-01.
    model::UtcTime result{days*86400+digits(11,2)*3600+digits(14,2)*60+digits(17,2),0};
    std::size_t pos=19;
    if (s[pos]=='.') {
        const auto first=++pos;
        while (pos<s.size() && s[pos]>='0' && s[pos]<='9') ++pos;
        const auto count=pos-first, nanos=std::min<std::size_t>(9,count);
        result.nanoseconds=static_cast<std::uint32_t>(digits(first,nanos));
        for (auto n=nanos; n<9; ++n) result.nanoseconds*=10;
        if (count>9) {
            result.subnanoseconds=s.substr(first+9,count-9);
            while (!result.subnanoseconds.empty() && result.subnanoseconds.back()=='0') result.subnanoseconds.pop_back();
        }
    }
    if (s[pos]=='+' || s[pos]=='-') {
        const auto offset=digits(pos+1,2)*3600+digits(pos+4,2)*60;
        result.seconds += s[pos]=='+' ? -offset : offset;
    }
    return result;
}
template<class T> T enumeration(const Json& value, std::initializer_list<const char*> names) {
    unsigned index=0;
    for (const auto* name : names) { if (value==name) return static_cast<T>(index); ++index; }
    throw protocol::Error("telemetry.body");
}
model::Value value(const Json& v) {
    if (v.is_null()) return {};
    const auto& kind=v["kind"]; const auto& data=v["data"];
    if (kind=="string") return data.get<std::string>();
    if (kind=="boolean") return data.get<bool>();
    if (kind=="number") return data.get<double>();
    return integer(data);
}
}
model::Publication reported_state(const protocol::Message& message, const protocol::TelemetryBinding& binding) {
    const auto& body=message.body; const auto& doc=body["snapshot"];
    model::Publication result;
    result.record_id=body["record_id"].get<std::string>(); result.replay_bytes=message.body_bytes;
    if (message.type=="delta") result.expected_base=integer(body["base_generation"]);
    auto& s=result.next;
    s.producer=body["producer_id"].get<std::string>(); s.epoch=message.producer_epoch; s.generation=integer(doc["generation"]);
    s.captured_at=utc(doc["captured_at"]); s.reported_document=doc.dump();
    s.reported_version=binding.document_version; s.clock_id=binding.clock_id; s.clock_scope=binding.clock_scope;
    for (const auto& e : doc["entities"]) s.entities.push_back({e["id"].get<std::string>(),e["kind"].get<std::string>(),
        e["display_name"].get<std::string>(),integer(e["generation"]),e["identity"].get<std::map<std::string,std::string>>()});
    for (const auto& src : doc["sources"]) s.sources.push_back({src["id"].get<std::string>(),src["kind"].get<std::string>(),src["scope"].get<std::string>()});
    for (const auto& edge : doc["relationships"]) s.relationships.push_back({edge["source"].get<std::string>(),edge["target"].get<std::string>(),edge["kind"].get<std::string>()});
    for (const auto& input : doc["observations"]) {
        model::Observation o;
        o.entity_id=input["entity_id"].get<std::string>(); o.field=input["field"].get<std::string>(); o.source_id=input["source_id"].get<std::string>();
        o.value=value(input["value"]); o.unit=input["unit"].get<std::string>();
        o.origin=enumeration<model::Origin>(input["origin"],{"observed","derived","configured"});
        o.support=enumeration<model::Support>(input["support"],{"supported","unsupported","unknown"});
        o.acquisition=enumeration<model::Acquisition>(input["acquisition"],{"success","pending","denied","failed","disabled"});
        o.freshness=enumeration<model::Freshness>(input["freshness"],{"current","stale","unknown","not_applicable"});
        o.presence=enumeration<model::Presence>(input["presence"],{"present","absent","unknown"});
        o.attempted_at=utc(input["attempted_at"]); if (!input["observed_at"].is_null()) o.observed_at=utc(input["observed_at"]);
        if (!input["sample_interval_ns"].is_null()) o.sample_interval_ns=integer(input["sample_interval_ns"]);
        if (!input["error"].is_null()) {
            const auto& e=input["error"]; o.error=model::Error{e["code"].get<std::string>(),e["message"].get<std::string>(),e["retryable"].get<bool>()};
        }
        o.generation=integer(input["generation"]);
        if (binding.document_version=="0.2.0" && !input["measured_at"].is_null())
            o.measured_at=model::Tick{s.epoch,integer(input["measured_at"]["nanoseconds"]),binding.clock_id,binding.clock_scope};
        s.observations.push_back(std::move(o));
    }
    return result;
}
}
