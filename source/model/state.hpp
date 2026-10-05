#pragma once

#include <cstddef>
#include <cstdint>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <tuple>
#include <variant>
#include <vector>

namespace syspane::model {

using Value = std::variant<std::monostate, std::string, bool, double, std::uint64_t>;
enum class ValueKind { string = 1, boolean = 2, number = 3, uint64 = 4 };
enum class Origin { observed, derived, configured };
enum class Support { supported, unsupported, unknown };
enum class Acquisition { success, pending, denied, failed, disabled };
enum class Freshness { current, stale, unknown, not_applicable };
enum class Presence { present, absent, unknown };

struct UtcTime {
    std::int64_t seconds = 0;
    std::uint32_t nanoseconds = 0;
    std::string subnanoseconds = {};
    bool operator==(const UtcTime& b) const { return std::tie(seconds, nanoseconds, subnanoseconds) == std::tie(b.seconds, b.nanoseconds, b.subnanoseconds); }
};

struct Tick {
    std::string epoch;
    std::uint64_t nanoseconds = 0;
    std::string clock_id = {}, clock_scope = {};
    bool operator==(const Tick& b) const { return std::tie(epoch, nanoseconds, clock_id, clock_scope) == std::tie(b.epoch, b.nanoseconds, b.clock_id, b.clock_scope); }
};

struct Error {
    std::string code;
    std::string message;
    bool retryable = false;
    bool operator==(const Error& b) const { return std::tie(code, message, retryable) == std::tie(b.code, b.message, b.retryable); }
};

struct Entity {
    std::string id;
    std::string kind;
    std::string display_name;
    std::uint64_t generation = 0;
    std::map<std::string, std::string> identity = {};
    bool operator==(const Entity& b) const { return std::tie(id, kind, display_name, generation, identity) == std::tie(b.id, b.kind, b.display_name, b.generation, b.identity); }
};

struct Source {
    std::string id;
    std::string kind;
    std::string scope;
    bool operator==(const Source& b) const { return std::tie(id, kind, scope) == std::tie(b.id, b.kind, b.scope); }
};

struct Relationship {
    std::string source;
    std::string target;
    std::string kind;
    bool operator==(const Relationship& b) const { return std::tie(source, target, kind) == std::tie(b.source, b.target, b.kind); }
};

struct Observation {
    std::string entity_id;
    std::string field;
    std::string source_id;
    Value value;
    std::string unit;
    Origin origin = Origin::observed;
    Support support = Support::unknown;
    Acquisition acquisition = Acquisition::pending;
    Freshness freshness = Freshness::unknown;
    Presence presence = Presence::unknown;
    std::optional<UtcTime> observed_at;
    UtcTime attempted_at;
    std::optional<Tick> measured_at;
    std::optional<std::uint64_t> sample_interval_ns;
    std::optional<Error> error;
    std::optional<std::uint64_t> generation = {};
    bool operator==(const Observation& b) const;
};

struct Snapshot {
    std::string producer;
    std::string epoch;
    std::uint64_t generation = 0;
    std::vector<Entity> entities;
    std::vector<Source> sources;
    std::vector<Relationship> relationships;
    std::vector<Observation> observations;
    std::optional<UtcTime> captured_at = {};
    // Adapter-validated complete state, opaque to the JSON-independent model.
    std::string reported_document = {};
    std::string reported_version = {}, clock_id = {}, clock_scope = {};
    bool operator==(const Snapshot& b) const;
};

struct Publication {
    std::string record_id;
    std::optional<std::uint64_t> expected_base;
    Snapshot next;
    std::string replay_bytes = {};
    bool operator==(const Publication& b) const;
};

struct Metric {
    std::string field;
    std::string unit;
    ValueKind kind;
};

struct Limits {
    std::size_t entities = 8192;
    std::size_t relationships = 16384;
    std::size_t sources = 1024;
    std::size_t observations = 65536;
    std::size_t retired_entities = 8192;
    std::size_t replay_records = 128;
    std::size_t candidate_bytes = 8 * 1024 * 1024;
    std::size_t retained_bytes = 64 * 1024 * 1024;
};

enum class Code {
    accepted, duplicate, conflict, wrong_epoch, missing_base, generation_order,
    invalid_identity, duplicate_entity, duplicate_source, retired_identity,
    dangling_relationship, invalid_observation, duplicate_observation, capacity, invalid_mode
};

struct Result {
    Code code;
    bool snapshot_required = false;
    bool accepted() const { return code == Code::accepted || code == Code::duplicate; }
};

// Single writer; callers must serialize access. Reader snapshots own immutable data.
class Store {
public:
    Store(std::string producer, std::string epoch, std::vector<Metric> metrics, Limits limits = {});
    std::shared_ptr<const Snapshot> snapshot() const { return current_; }
    Result publish(const Publication& candidate);
    // Consumer-only full resynchronization: a new record may confirm the identical
    // normalized current generation. It reserves replay capacity and never resets history.
    Result resynchronize(const Publication& candidate);
    Result import_state(const Publication& candidate);
    std::vector<Observation> retired_observations(const std::string& entity_id) const;
private:
    Result publish_checked(const Publication& candidate, bool resynchronize = false, bool reported = false);
    std::string producer_;
    std::string epoch_;
    std::vector<Metric> metrics_;
    Limits limits_;
    std::shared_ptr<const Snapshot> current_;
    std::map<std::string, std::shared_ptr<const Publication>> records_;
    std::map<std::string, std::vector<Observation>> retired_;
    std::map<std::tuple<std::string, std::string, std::string>, std::uint64_t> measurement_highwater_;
    std::size_t retained_bytes_ = 0;
    std::optional<bool> reported_;
};

std::optional<std::uint64_t> interval_ns(const Tick& before, const Tick& after);
Freshness freshness_at(const Observation& observation, const Tick& now,
                       std::optional<std::uint64_t> ttl_ns);
const char* code_name(Code code);

} // namespace syspane::model
