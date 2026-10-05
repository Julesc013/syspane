#pragma once
#include "state.hpp"
#include "recovery.hpp"
#include "policy.hpp"
#include <functional>
#include <memory>

namespace syspane::recovery {
enum class DataCode { accepted, duplicate, denied, stale_attachment, policy_changed, snapshot_required, invalid, capacity, clock_fault, closed };
struct DataResult { DataCode code; std::optional<model::Code> validation = {}; };
struct DataAttachment { DataCode code; std::uint64_t token = 0; };
struct DataStatus {
    bool permitted, alive, snapshot_required, payload_available;
    Presentation presentation;
    LeaseReason reason;
    std::uint64_t lifetime;
};

// One serialized trusted event-loop owner. No model pointer escapes this component.
// Projection callbacks are synchronous borrows: no retaining, caching, exporting or reentry.
class DataView {
public:
    DataView(configuration::Authority authority, configuration::Policy policy,
             std::string channel, std::string classification, std::vector<model::Metric> metrics, model::Limits limits = {});
    DataView(const DataView&) = delete;
    DataView& operator=(const DataView&) = delete;
    DataAttachment attach(const std::string& producer, const std::string& epoch, std::uint64_t now);
    DataResult full(std::uint64_t token, std::uint64_t policy_revision, const model::Publication& publication, std::uint64_t now);
    DataResult delta(std::uint64_t token, std::uint64_t policy_revision, const model::Publication& publication, std::uint64_t now);
    DataCode heartbeat(std::uint64_t token, std::uint64_t revision, std::uint64_t sequence, std::uint64_t now);
    DataCode gap(std::uint64_t token, std::uint64_t revision, std::uint64_t now);
    DataCode disconnect(std::uint64_t token, std::uint64_t revision, std::uint64_t now);
    DataCode policy(configuration::Policy next, std::uint64_t now);
    DataStatus status(std::uint64_t now);
    bool project(std::uint64_t now, const std::function<void(const model::Snapshot&, const LeaseView&)>& borrow);
private:
    void require_owner() const;
    bool permitted() const;
    bool advance_lifetime();
    void drop(std::uint64_t now);
    DataCode check(std::uint64_t token, std::uint64_t revision, std::uint64_t now);
    DataResult publish(bool full, std::uint64_t token, std::uint64_t revision, const model::Publication&, std::uint64_t now);
    configuration::Authority authority_;
    configuration::Policy policy_;
    std::string channel_, classification_, producer_, epoch_;
    std::vector<model::Metric> metrics_;
    model::Limits limits_;
    std::optional<std::uint64_t> highest_policy_;
    std::uint64_t token_ = 0, lifetime_ = 1;
    bool borrowed_ = false, lifetime_fault_ = false;
    ProducerLease lease_;
    std::unique_ptr<model::Store> store_;
};
}
