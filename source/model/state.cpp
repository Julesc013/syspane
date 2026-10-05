#include "state.hpp"

#include <algorithm>
#include <cmath>
#include <new>
#include <set>
#include <stdexcept>

namespace syspane::model {
namespace {
bool identifier(const std::string& value) {
    const auto alnum = [](char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9'); };
    return !value.empty() && value.size() <= 256 && alnum(value.front()) &&
        std::all_of(value.begin(), value.end(), [&](char c) { return alnum(c) || c == ':' || c == '.' || c == '_' || c == '/' || c == '-'; });
}
bool safe_text(const std::string& value, std::size_t max) {
    // UI adapters still own escaping. Reject controls, including terminal escape.
    return value.size() <= max && std::none_of(value.begin(), value.end(), [](unsigned char c) { return c < 32 || c == 127; });
}
bool valid_time(const UtcTime& time) {
    return time.nanoseconds < 1000000000 && time.subnanoseconds.size() <= 34 &&
        (time.subnanoseconds.empty() || (time.subnanoseconds.back() != '0' &&
         std::all_of(time.subnanoseconds.begin(), time.subnanoseconds.end(), [](char c) { return c >= '0' && c <= '9'; })));
}
auto key(const Observation& o) { return std::tie(o.entity_id, o.source_id, o.field); }
std::size_t observation_bytes(const Observation& o) {
    return sizeof(o) + o.entity_id.size() + o.field.size() + o.source_id.size() + o.unit.size() +
        (std::holds_alternative<std::string>(o.value) ? std::get<std::string>(o.value).size() : 0) +
        (o.measured_at ? o.measured_at->epoch.size() + o.measured_at->clock_id.size() + o.measured_at->clock_scope.size() : 0) +
        (o.error ? o.error->code.size() + o.error->message.size() : 0) + o.attempted_at.subnanoseconds.size() +
        (o.observed_at ? o.observed_at->subnanoseconds.size() : 0);
}
std::optional<std::size_t> accounted_bytes(const Publication& p, std::size_t limit) {
    std::size_t size = 0;
    const auto add = [&](std::size_t n) { if (n > limit - size) return false; size += n; return true; };
    if (!add(sizeof(p)) || !add(p.record_id.size()) || !add(p.next.producer.size()) || !add(p.next.epoch.size())) return {};
    if (!add(p.replay_bytes.size()) || !add(p.next.reported_document.size()) ||
        !add(p.next.reported_version.size()) || !add(p.next.clock_id.size()) || !add(p.next.clock_scope.size()) ||
        (p.next.captured_at && !add(p.next.captured_at->subnanoseconds.size()))) return {};
    for (const auto& e : p.next.entities) if (!add(sizeof(e)) || !add(e.id.size()) || !add(e.kind.size()) || !add(e.display_name.size())) return {};
    for (const auto& e : p.next.entities) for (const auto& item : e.identity)
        if (!add(sizeof(item)) || !add(item.first.size()) || !add(item.second.size())) return {};
    for (const auto& s : p.next.sources) if (!add(sizeof(s)) || !add(s.id.size()) || !add(s.kind.size()) || !add(s.scope.size())) return {};
    for (const auto& r : p.next.relationships) if (!add(sizeof(r)) || !add(r.source.size()) || !add(r.target.size()) || !add(r.kind.size())) return {};
    for (const auto& o : p.next.observations) if (!add(observation_bytes(o))) return {};
    return size;
}
} // namespace

bool Observation::operator==(const Observation& b) const {
    return std::tie(entity_id, field, source_id, value, unit, origin, support, acquisition, freshness, presence, observed_at, attempted_at, measured_at, sample_interval_ns, error, generation) ==
        std::tie(b.entity_id, b.field, b.source_id, b.value, b.unit, b.origin, b.support, b.acquisition, b.freshness, b.presence, b.observed_at, b.attempted_at, b.measured_at, b.sample_interval_ns, b.error, b.generation);
}
bool Snapshot::operator==(const Snapshot& b) const {
    return std::tie(producer, epoch, generation, entities, sources, relationships, observations, captured_at, reported_document, reported_version, clock_id, clock_scope) == std::tie(b.producer, b.epoch, b.generation, b.entities, b.sources, b.relationships, b.observations, b.captured_at, b.reported_document, b.reported_version, b.clock_id, b.clock_scope);
}
bool Publication::operator==(const Publication& b) const {
    return std::tie(record_id, expected_base, next, replay_bytes) == std::tie(b.record_id, b.expected_base, b.next, b.replay_bytes);
}

Store::Store(std::string producer, std::string epoch, std::vector<Metric> metrics, Limits limits)
    : producer_(std::move(producer)), epoch_(std::move(epoch)), metrics_(std::move(metrics)), limits_(limits) {
    if (!identifier(producer_) || !identifier(epoch_)) throw std::invalid_argument("invalid store identity");
    std::set<std::string> fields;
    for (const auto& metric : metrics_) {
        if (!identifier(metric.field) || metric.unit.empty() || !safe_text(metric.unit, 64) ||
            static_cast<int>(metric.kind) < 1 || static_cast<int>(metric.kind) > 4 || !fields.insert(metric.field).second)
            throw std::invalid_argument("invalid metric descriptor");
    }
}

Result Store::publish(const Publication& candidate) {
    try { return publish_checked(candidate); }
    catch (const std::bad_alloc&) { return {Code::capacity}; }
}

Result Store::resynchronize(const Publication& candidate) {
    if (candidate.expected_base) return {Code::missing_base, true};
    try { return publish_checked(candidate, true); }
    catch (const std::bad_alloc&) { return {Code::capacity}; }
}
Result Store::import_state(const Publication& candidate) {
    try { return publish_checked(candidate, !candidate.expected_base, true); }
    catch (const std::bad_alloc&) { return {Code::capacity}; }
}
Result Store::publish_checked(const Publication& candidate, bool resynchronize, bool reported) {
    const auto& next = candidate.next;
    if ((reported_ && *reported_ != reported) ||
        (reported && (next.reported_document.empty() || candidate.replay_bytes.empty() || !next.captured_at)) ||
        (!reported && (!next.reported_document.empty() || !candidate.replay_bytes.empty() ||
                      !next.reported_version.empty() || !next.clock_id.empty() || !next.clock_scope.empty()))) return {Code::invalid_mode};
    if (next.reported_document.size() > 1048576 || candidate.replay_bytes.size() > 1048576) return {Code::capacity};
    if (next.captured_at && !valid_time(*next.captured_at)) return {Code::invalid_observation};
    if (!identifier(candidate.record_id)) return {Code::invalid_identity};
    if (next.producer != producer_ || next.epoch != epoch_) return {Code::wrong_epoch, true};
    if (next.reported_version.size() > 32 || (!next.clock_id.empty() && !identifier(next.clock_id)) ||
        (!next.clock_scope.empty() && !identifier(next.clock_scope))) return {Code::invalid_identity};
    if (reported && current_ && std::tie(next.reported_version,next.clock_id,next.clock_scope) !=
        std::tie(current_->reported_version,current_->clock_id,current_->clock_scope)) return {Code::invalid_mode};
    // Bound before comparing or copying potentially large input containers.
    if (next.entities.size() > limits_.entities || next.sources.size() > limits_.sources ||
        next.relationships.size() > limits_.relationships || next.observations.size() > limits_.observations)
        return {Code::capacity};
    const auto bytes = accounted_bytes(candidate, limits_.candidate_bytes);
    if (!bytes) return {Code::capacity};
    const auto replay = records_.find(candidate.record_id);
    if (replay != records_.end()) return {(*replay->second == candidate) ? Code::duplicate : Code::conflict};
    if (candidate.expected_base && (!current_ || *candidate.expected_base != current_->generation)) return {Code::missing_base, true};
    if (current_ && (next.generation < current_->generation || (next.generation == current_->generation && !resynchronize))) return {Code::generation_order};
    if (records_.size() >= limits_.replay_records || *bytes > limits_.retained_bytes - retained_bytes_) return {Code::capacity};

    std::set<std::string> entities, sources;
    for (const auto& e : next.entities) {
        if (!identifier(e.id) || !identifier(e.kind) || !safe_text(e.display_name, 2048) || e.generation > next.generation) return {Code::invalid_identity};
        if (e.identity.size() > 64) return {Code::capacity};
        for (const auto& item : e.identity) if (item.first.size() > 256 || item.second.size() > 2048) return {Code::invalid_identity};
        if (!entities.insert(e.id).second) return {Code::duplicate_entity};
        if (retired_.count(e.id)) return {Code::retired_identity};
    }
    for (const auto& s : next.sources) {
        if (!identifier(s.id) || !identifier(s.kind) || !identifier(s.scope)) return {Code::invalid_identity};
        if (!sources.insert(s.id).second) return {Code::duplicate_source};
    }
    for (const auto& r : next.relationships)
        if (!entities.count(r.source) || !entities.count(r.target) || !identifier(r.kind)) return {Code::dangling_relationship};

    Snapshot normalized = next;
    auto measurement_highwater = measurement_highwater_;
    std::size_t clock_added = 0;
    std::set<std::tuple<std::string, std::string, std::string>> observation_keys;
    for (auto& o : normalized.observations) {
        if (o.origin < Origin::observed || o.origin > Origin::configured ||
            o.support < Support::supported || o.support > Support::unknown ||
            o.acquisition < Acquisition::success || o.acquisition > Acquisition::disabled ||
            o.freshness < Freshness::current || o.freshness > Freshness::not_applicable ||
            o.presence < Presence::present || o.presence > Presence::unknown) return {Code::invalid_observation};
        if (retired_.count(o.entity_id)) return {Code::retired_identity};
        if (!entities.count(o.entity_id) || !sources.count(o.source_id) || !identifier(o.field) ||
            !valid_time(o.attempted_at) || (o.observed_at && !valid_time(*o.observed_at)) ||
            (o.measured_at && o.measured_at->epoch != epoch_)) return {Code::invalid_observation};
        if ((o.generation && *o.generation > next.generation) || (reported && !o.generation)) return {Code::invalid_observation};
        if (o.measured_at && ((!o.measured_at->clock_id.empty() && !identifier(o.measured_at->clock_id)) ||
            (!o.measured_at->clock_scope.empty() && !identifier(o.measured_at->clock_scope)) ||
            (reported && (!identifier(o.measured_at->clock_id) || !identifier(o.measured_at->clock_scope) ||
                          o.measured_at->clock_id != next.clock_id || o.measured_at->clock_scope != next.clock_scope))))
            return {Code::invalid_observation};
        if (!observation_keys.insert(key(o)).second) return {Code::duplicate_observation};
        const auto metric = std::find_if(metrics_.begin(), metrics_.end(), [&](const Metric& m) { return m.field == o.field; });
        if (metric == metrics_.end() || metric->unit != o.unit ||
            (o.value.index() != 0 && o.value.index() != static_cast<std::size_t>(metric->kind))) return {Code::invalid_observation};
        if ((std::holds_alternative<double>(o.value) && !std::isfinite(std::get<double>(o.value))) ||
            (std::holds_alternative<std::string>(o.value) && std::get<std::string>(o.value).size() > 16384)) return {Code::invalid_observation};
        if (o.error && (!identifier(o.error->code) || !safe_text(o.error->message, 2048))) return {Code::invalid_observation};
        if ((o.acquisition == Acquisition::failed || o.acquisition == Acquisition::denied) && !o.error) return {Code::invalid_observation};
        if (reported) {
            if (o.measured_at) {
                const auto previous = measurement_highwater.find(key(o));
                if (previous != measurement_highwater.end() && o.measured_at->nanoseconds < previous->second) return {Code::invalid_observation};
                if (previous == measurement_highwater.end()) {
                    const auto cost = sizeof(decltype(measurement_highwater)::value_type) + o.entity_id.size() + o.source_id.size() + o.field.size();
                    if (measurement_highwater.size() >= limits_.observations || cost > limits_.retained_bytes-retained_bytes_-*bytes-clock_added)
                        return {Code::capacity};
                    clock_added += cost;
                }
                measurement_highwater[key(o)] = o.measured_at->nanoseconds;
            }
            // A full remote state reports its own retained measurement. It is not
            // a local acquisition attempt and cannot inherit older local values.
            if (o.value.index() == 0 && (o.observed_at || o.measured_at)) return {Code::invalid_observation};
            if (o.support == Support::unsupported) {
                if (o.value.index() != 0 || o.acquisition == Acquisition::success || o.freshness != Freshness::not_applicable) return {Code::invalid_observation};
            } else if (o.acquisition == Acquisition::success) {
                if (o.support != Support::supported || o.value.index() == 0 || !o.observed_at || o.error) return {Code::invalid_observation};
            } else if (o.value.index() != 0) {
                if (o.support != Support::supported || !o.observed_at || o.freshness != Freshness::stale) return {Code::invalid_observation};
            } else if (o.freshness != Freshness::unknown) return {Code::invalid_observation};
            if (o.presence == Presence::absent && o.value.index() != 0 && o.freshness != Freshness::stale) return {Code::invalid_observation};
            continue;
        }
        if (o.support == Support::unsupported) {
            if (o.value.index() != 0 || o.acquisition == Acquisition::success) return {Code::invalid_observation};
            o.freshness = Freshness::not_applicable;
        } else if (o.acquisition == Acquisition::success) {
            if (o.support != Support::supported || o.value.index() == 0 || !o.observed_at || o.error) return {Code::invalid_observation};
        } else {
            // Acquisition attempts never get to replace a retained measurement.
            if (current_) {
                const auto previous = std::find_if(current_->observations.begin(), current_->observations.end(), [&](const Observation& old) { return key(old) == key(o); });
                if (previous != current_->observations.end() && previous->value.index() != 0) {
                    o.value = previous->value;
                    o.observed_at = previous->observed_at;
                    o.measured_at = previous->measured_at;
                    o.sample_interval_ns = previous->sample_interval_ns;
                    o.origin = previous->origin;
                } else if (o.value.index() != 0) return {Code::invalid_observation};
            } else if (o.value.index() != 0) return {Code::invalid_observation};
            o.freshness = o.value.index() != 0 ? Freshness::stale : Freshness::unknown;
        }
        if (o.presence == Presence::absent && o.value.index() != 0) o.freshness = Freshness::stale;
    }
    // Retained values can make normalized state larger than the incoming attempt.
    if (current_ && next.generation == current_->generation && !(normalized == *current_)) return {Code::conflict};
    Publication normalized_size{candidate.record_id, candidate.expected_base, normalized, candidate.replay_bytes};
    if (!accounted_bytes(normalized_size, limits_.candidate_bytes)) return {Code::capacity};

    auto retired = retired_;
    std::size_t retained_bytes = retained_bytes_ + *bytes + clock_added;
    if (current_) for (const auto& e : current_->entities) {
        if (entities.count(e.id)) continue;
        if (retired.size() >= limits_.retired_entities) return {Code::capacity};
        std::vector<Observation> observations;
        std::size_t size = sizeof(e) + e.id.size();
        for (auto o : current_->observations) if (o.entity_id == e.id) {
            o.presence = Presence::absent;
            if (o.value.index() != 0) o.freshness = Freshness::stale;
            const auto cost = observation_bytes(o);
            if (cost > limits_.retained_bytes - retained_bytes || size > limits_.retained_bytes - retained_bytes - cost) return {Code::capacity};
            size += cost;
            observations.push_back(std::move(o));
        }
        if (size > limits_.retained_bytes - retained_bytes) return {Code::capacity};
        retained_bytes += size;
        retired.emplace(e.id, std::move(observations));
    }
    auto records = records_;
    records.emplace(candidate.record_id, std::make_shared<const Publication>(candidate));
    auto published = std::make_shared<const Snapshot>(std::move(normalized));
    // All throwing work completed. Publish snapshot, replay and tombstones together.
    current_.swap(published);
    records_.swap(records);
    retired_.swap(retired);
    measurement_highwater_.swap(measurement_highwater);
    retained_bytes_ = retained_bytes;
    reported_ = reported;
    return {Code::accepted};
}

std::vector<Observation> Store::retired_observations(const std::string& entity_id) const {
    const auto found = retired_.find(entity_id);
    return found == retired_.end() ? std::vector<Observation>{} : found->second;
}

std::optional<std::uint64_t> interval_ns(const Tick& before, const Tick& after) {
    if (before.epoch.empty() || before.epoch != after.epoch || before.clock_id != after.clock_id ||
        before.clock_scope != after.clock_scope || after.nanoseconds <= before.nanoseconds) return {};
    return after.nanoseconds - before.nanoseconds;
}

Freshness freshness_at(const Observation& o, const Tick& now, std::optional<std::uint64_t> ttl_ns) {
    if (o.support == Support::unsupported) return Freshness::not_applicable;
    if (o.value.index() == 0) return Freshness::unknown;
    if (o.acquisition != Acquisition::success || o.presence == Presence::absent || o.freshness != Freshness::current) return Freshness::stale;
    if (!ttl_ns) return o.freshness;
    if (!o.measured_at || o.measured_at->epoch != now.epoch || o.measured_at->clock_id != now.clock_id ||
        o.measured_at->clock_scope != now.clock_scope || now.nanoseconds < o.measured_at->nanoseconds) return Freshness::stale;
    return now.nanoseconds - o.measured_at->nanoseconds >= *ttl_ns ? Freshness::stale : Freshness::current;
}

const char* code_name(Code code) {
    switch (code) {
    case Code::accepted: return "accepted";
    case Code::duplicate: return "duplicate";
    case Code::conflict: return "conflict";
    case Code::wrong_epoch: return "wrong_epoch";
    case Code::missing_base: return "missing_base";
    case Code::generation_order: return "generation_order";
    case Code::invalid_identity: return "invalid_identity";
    case Code::duplicate_entity: return "duplicate_entity";
    case Code::duplicate_source: return "duplicate_source";
    case Code::retired_identity: return "retired_identity";
    case Code::dangling_relationship: return "dangling_relationship";
    case Code::invalid_observation: return "invalid_observation";
    case Code::duplicate_observation: return "duplicate_observation";
    case Code::capacity: return "capacity";
    case Code::invalid_mode: return "invalid_mode";
    }
    return "unknown";
}
} // namespace syspane::model
