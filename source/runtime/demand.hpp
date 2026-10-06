#pragma once
#include "policy.hpp"
#include <limits>
#include <optional>
#include <vector>

namespace syspane::runtime {
enum class DemandCode { accepted, duplicate, denied, invalid, capacity, obsolete, clock_fault };
struct DemandField { std::string id, classification; };
struct DemandSource {
    std::string id, capability;
    std::uint64_t minimum_ms, timeout_ms;
    std::string cadence_setting;
    std::vector<DemandField> fields;
};
struct DemandSelection {
    std::string field;
    std::optional<std::string> entity;
    bool operator==(const DemandSelection& other) const { return field == other.field && entity == other.entity; }
};
struct DemandRequest {
    std::string channel;
    std::vector<DemandSelection> selections;
    std::uint64_t maximum_age_ms = 1000;
    unsigned priority = 0;
    bool recording = false;
};
struct DemandPlan {
    std::string source;
    std::vector<DemandSelection> selections;
    std::uint64_t interval_ms = 0, requested_age_ms = 0;
    unsigned priority = 0;
    bool recording = false, age_feasible = false;
    bool operator==(const DemandPlan& other) const;
    bool operator!=(const DemandPlan& other) const { return !(*this == other); }
};
struct DemandJob {
    std::uint64_t ticket, plan_revision, policy_revision, started_ms;
    DemandPlan plan;
    bool cancelled = false;
};
struct DemandAdmission { DemandCode code; std::uint64_t lease = 0; };
struct DemandLimits {
    std::size_t leases = 32, selections = 64, workers = 4;
    std::uint64_t identities = std::numeric_limits<std::uint64_t>::max();
};
// One trusted serialized controller owner. Native authentication, transport,
// source execution and actual stop proof stay with their existing adapters.
class DemandOwner {
public:
    DemandOwner(std::vector<DemandSource> catalog, configuration::Policy policy, DemandLimits limits = {});
    DemandOwner(const DemandOwner&) = delete;
    DemandOwner& operator=(const DemandOwner&) = delete;
    DemandAdmission admit(const DemandRequest&, const configuration::Authority&, std::uint64_t now);
    DemandCode renew(std::uint64_t lease, std::uint64_t sequence, std::uint64_t now);
    DemandCode release(std::uint64_t lease, std::uint64_t now);
    DemandCode policy(configuration::Policy next, std::uint64_t now);
    DemandCode tick(std::uint64_t now);
    std::optional<DemandJob> take(std::uint64_t now);
    DemandCode complete(std::uint64_t ticket, std::uint64_t now);
    // Caller supplies an actual matching native completion/stop observation.
    // Permitted after clock fault; this cannot revive demand or publish a result.
    DemandCode confirm_stopped(std::uint64_t ticket);
    std::vector<DemandJob> outstanding() const;
    std::size_t lease_count() const { return leases_.size(); }
    std::optional<DemandCode> fault() const { return fault_; }
private:
    struct Lease { DemandRequest request; std::uint64_t renewed; std::optional<std::uint64_t> sequence; };
    struct Source {
        DemandSource descriptor;
        std::optional<DemandPlan> plan;
        std::uint64_t revision = 0, job = 0, order = 0;
        std::optional<std::uint64_t> dispatched, eligible;
    };
    bool rebuild(std::uint64_t now);
    void readiness(std::uint64_t now);
    void drain();
    void fail(DemandCode code);
    std::uint64_t identity();
    bool permitted(const DemandRequest&, const configuration::Authority&) const;
    void validate_policy(const configuration::Policy&) const;
    std::size_t worker_limit() const;
    DemandLimits limits_;
    configuration::Policy policy_;
    std::optional<std::uint64_t> highest_policy_, last_;
    std::optional<DemandCode> fault_;
    std::uint64_t issued_ = 0;
    std::map<std::string, Source> sources_;
    std::map<std::string, std::pair<std::string, std::string>> fields_;
    std::map<std::uint64_t, Lease> leases_;
    std::map<std::uint64_t, DemandJob> jobs_;
};
}
