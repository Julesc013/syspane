#include "demand.hpp"
#include <algorithm>
#include <cmath>
#include <new>
#include <stdexcept>
#include <tuple>

namespace syspane::runtime {
namespace {
using configuration::Policy;
void require(bool yes) { if (!yes) throw std::invalid_argument("demand.contract"); }
std::uint64_t forced(const Policy& policy, const std::string& key, std::uint64_t fallback,
                     std::uint64_t minimum, std::uint64_t maximum) {
    const auto it = policy.forced.find(key);
    if (key.empty() || it == policy.forced.end()) return fallback;
    const auto& value = it->second;
    require(value.is_number());
    const auto number = value.get<double>();
    require(std::isfinite(number) && std::floor(number) == number && number >= static_cast<double>(minimum) &&
            number <= static_cast<double>(maximum));
    return static_cast<std::uint64_t>(number);
}
}
bool DemandPlan::operator==(const DemandPlan& other) const {
    return source == other.source && selections == other.selections && interval_ms == other.interval_ms &&
        requested_age_ms == other.requested_age_ms && priority == other.priority && recording == other.recording &&
        age_feasible == other.age_feasible;
}
DemandOwner::DemandOwner(std::vector<DemandSource> catalog, Policy policy, DemandLimits limits)
    : limits_(limits), policy_(std::move(policy)) {
    require(!catalog.empty() && catalog.size() <= 16 && limits.leases > 0 && limits.leases <= 32 &&
            limits.selections > 0 && limits.selections <= 64 && limits.workers > 0 && limits.workers <= 8 && limits.identities > 0);
    for (auto& item : catalog) {
        require(protocol::identifier(item.id) && protocol::identifier(item.capability) &&
                item.minimum_ms >= 100 && item.minimum_ms <= 3600000 && item.timeout_ms > 0 && item.timeout_ms <= 60000 &&
                (item.cadence_setting.empty() || item.cadence_setting == "sampling.resources_ms" || item.cadence_setting == "sampling.reconcile_ms") &&
                !item.fields.empty() && !sources_.count(item.id));
        for (const auto& field : item.fields) {
            require(protocol::identifier(field.id) && (field.classification == "public" || field.classification == "operational" || field.classification == "sensitive") &&
                    fields_.emplace(field.id, std::make_pair(item.id, field.classification)).second && fields_.size() <= 256);
        }
        const auto id = item.id;
        sources_.emplace(id, Source{std::move(item), {}, 0, 0, 0, {}, {}});
    }
    validate_policy(policy_);
    if (policy_.available) highest_policy_ = policy_.revision;
}
void DemandOwner::validate_policy(const Policy& policy) const {
    if (!policy.available) return;
    (void)forced(policy, "sampling.max_workers", limits_.workers, 1, 32);
    for (const auto& row : sources_) {
        const auto& source = row.second.descriptor;
        (void)forced(policy, source.cadence_setting, source.minimum_ms,
                     source.cadence_setting == "sampling.reconcile_ms" ? 1000 : 100,
                     source.cadence_setting == "sampling.resources_ms" ? 60000 : 3600000);
    }
}
std::size_t DemandOwner::worker_limit() const {
    return std::min(limits_.workers, static_cast<std::size_t>(forced(policy_, "sampling.max_workers", limits_.workers, 1, 32)));
}
void DemandOwner::drain() {
    leases_.clear();
    for (auto& row : jobs_) row.second.cancelled = true;
    for (auto& row : sources_) { row.second.plan.reset(); row.second.eligible.reset(); }
}
void DemandOwner::fail(DemandCode code) { fault_ = code; policy_.available = false; drain(); }
std::uint64_t DemandOwner::identity() {
    if (issued_ == limits_.identities) { fail(DemandCode::capacity); return 0; }
    return ++issued_;
}
bool DemandOwner::permitted(const DemandRequest& request, const configuration::Authority& authority) const {
    if (!policy_.available || policy_.denied_capabilities.count("telemetry.subscribe") ||
        (request.recording && policy_.denied_capabilities.count("history.record"))) return false;
    const std::map<std::string, std::string> channels = {{"desktop","desktop"},{"console","inspector"},{"saver","saver"},{"preview","preview"}};
    const auto channel = channels.find(authority.role);
    if (request.recording ? (authority.role != "console" || request.channel != "history") :
        (channel == channels.end() || channel->second != request.channel)) return false;
    for (const auto& selected : request.selections) {
        const auto& field = fields_.at(selected.field);
        if (policy_.denied_capabilities.count(sources_.at(field.first).descriptor.capability) ||
            !configuration::permits(authority, policy_, request.channel, field.second)) return false;
    }
    return true;
}
DemandAdmission DemandOwner::admit(const DemandRequest& request, const configuration::Authority& authority, std::uint64_t now) {
    const auto advanced = tick(now);
    if (advanced != DemandCode::accepted) return {advanced, 0};
    if (request.selections.empty() || request.selections.size() > limits_.selections || request.maximum_age_ms < 100 ||
        request.maximum_age_ms > 3600000 || request.priority > 3) return {DemandCode::invalid, 0};
    std::set<std::pair<std::string, std::optional<std::string>>> unique;
    for (const auto& selection : request.selections)
        if (!fields_.count(selection.field) || (selection.entity && !protocol::identifier(*selection.entity)) ||
            !unique.emplace(selection.field, selection.entity).second) return {DemandCode::invalid, 0};
    if (!permitted(request, authority)) return {DemandCode::denied, 0};
    if (leases_.size() == limits_.leases) return {DemandCode::capacity, 0};
    Lease lease{request, now, {}};
    const auto id = identity();
    if (!id) return {*fault_, 0};
    leases_.emplace(id, std::move(lease));
    if (!rebuild(now)) return {*fault_, 0};
    return {DemandCode::accepted, id};
}
bool DemandOwner::rebuild(std::uint64_t now) try {
    std::map<std::string, DemandPlan> plans;
    for (const auto& row : sources_) {
        const auto& source = row.second.descriptor;
        DemandPlan plan; plan.source = row.first; plan.requested_age_ms = 3600000;
        std::map<std::string, std::set<std::string>> selections;
        for (const auto& entry : leases_) {
            const auto& request = entry.second.request; bool used = false;
            for (const auto& selected : request.selections) {
                if (fields_.at(selected.field).first != row.first) continue;
                selections[selected.field].insert(selected.entity.value_or("")); used = true;
            }
            if (used) {
                plan.requested_age_ms = std::min(plan.requested_age_ms, request.maximum_age_ms);
                plan.priority = std::max(plan.priority, request.priority); plan.recording |= request.recording;
            }
        }
        if (selections.empty()) continue;
        for (const auto& selected : selections) {
            if (selected.second.count("")) plan.selections.push_back({selected.first, {}});
            else for (const auto& entity : selected.second) plan.selections.push_back({selected.first, entity});
        }
        plan.interval_ms = std::max({plan.requested_age_ms, source.minimum_ms,
            forced(policy_, source.cadence_setting, source.minimum_ms, source.cadence_setting == "sampling.reconcile_ms" ? 1000 : 100,
                   source.cadence_setting == "sampling.resources_ms" ? 60000 : 3600000)});
        plan.age_feasible = plan.interval_ms <= plan.requested_age_ms;
        plans.emplace(row.first, std::move(plan));
    }
    for (auto& row : sources_) {
        auto& source = row.second; const auto found = plans.find(row.first);
        std::optional<DemandPlan> next;
        if (found != plans.end()) next = std::move(found->second);
        if (next != source.plan) {
            if (source.revision == std::numeric_limits<std::uint64_t>::max()) { fail(DemandCode::capacity); return false; }
            ++source.revision;
            if (source.job) jobs_.at(source.job).cancelled = true;
            source.plan = std::move(next);
        }
    }
    readiness(now); return true;
} catch (const std::bad_alloc&) {
    fail(DemandCode::capacity); throw;
}
void DemandOwner::readiness(std::uint64_t now) {
    for (auto& row : sources_) {
        auto& source = row.second;
        if (source.plan && !source.job && (!source.dispatched || now - *source.dispatched >= source.plan->interval_ms)) {
            if (!source.eligible) source.eligible = now;
        } else source.eligible.reset();
    }
}
DemandCode DemandOwner::tick(std::uint64_t now) {
    if (fault_) return *fault_;
    if (last_ && now < *last_) { fail(DemandCode::clock_fault); return *fault_; }
    last_ = now; bool removed = false;
    for (auto it = leases_.begin(); it != leases_.end();) {
        if (now - it->second.renewed >= 3000) { it = leases_.erase(it); removed = true; }
        else ++it;
    }
    if (removed && !rebuild(now)) return *fault_;
    for (auto& row : jobs_)
        if (now - row.second.started_ms >= sources_.at(row.second.plan.source).descriptor.timeout_ms) row.second.cancelled = true;
    readiness(now); return DemandCode::accepted;
}
DemandCode DemandOwner::renew(std::uint64_t lease, std::uint64_t sequence, std::uint64_t now) {
    const auto advanced = tick(now); if (advanced != DemandCode::accepted) return advanced;
    const auto it = leases_.find(lease); if (it == leases_.end()) return DemandCode::obsolete;
    if (it->second.sequence) {
        if (sequence == *it->second.sequence) return DemandCode::duplicate;
        if (sequence < *it->second.sequence) { leases_.erase(it); rebuild(now); return DemandCode::invalid; }
    }
    it->second.sequence = sequence; it->second.renewed = now; return DemandCode::accepted;
}
DemandCode DemandOwner::release(std::uint64_t lease, std::uint64_t now) {
    const auto advanced = tick(now); if (advanced != DemandCode::accepted) return advanced;
    if (!leases_.erase(lease)) return DemandCode::obsolete;
    return rebuild(now) ? DemandCode::accepted : *fault_;
}
DemandCode DemandOwner::policy(Policy next, std::uint64_t now) {
    const auto advanced = tick(now); drain(); policy_.available = false;
    if (advanced != DemandCode::accepted) return advanced;
    try { validate_policy(next); } catch (const std::invalid_argument&) { return DemandCode::invalid; }
    if (next.available && highest_policy_ && next.revision <= *highest_policy_) return DemandCode::invalid;
    if (next.available) highest_policy_ = next.revision;
    policy_ = std::move(next); return DemandCode::accepted;
}
std::optional<DemandJob> DemandOwner::take(std::uint64_t now) {
    if (tick(now) != DemandCode::accepted || !policy_.available || jobs_.size() >= worker_limit()) return {};
    Source* selected = nullptr;
    const auto priority = [now](const Source& source) { return std::min<std::uint64_t>(3, source.plan->priority + (now - *source.eligible) / 1000); };
    for (auto& row : sources_) {
        auto& source = row.second; if (!source.eligible) continue;
        if (!selected || priority(source) > priority(*selected) || (priority(source) == priority(*selected) &&
            std::tie(source.eligible, source.order, source.descriptor.id) < std::tie(selected->eligible, selected->order, selected->descriptor.id))) selected = &source;
    }
    if (!selected) return {};
    const auto id = identity(); if (!id) return {};
    DemandJob job{id, selected->revision, policy_.revision, now, *selected->plan, false};
    jobs_.emplace(id, job); selected->job = selected->order = id; selected->dispatched = now; selected->eligible.reset();
    return job;
}
DemandCode DemandOwner::confirm_stopped(std::uint64_t ticket) {
    const auto it = jobs_.find(ticket); if (it == jobs_.end()) return DemandCode::obsolete;
    sources_.at(it->second.plan.source).job = 0; jobs_.erase(it);
    if (!fault_ && last_) readiness(*last_);
    return DemandCode::accepted;
}
DemandCode DemandOwner::complete(std::uint64_t ticket, std::uint64_t now) {
    const auto advanced = tick(now);
    const auto it = jobs_.find(ticket); if (it == jobs_.end()) return DemandCode::obsolete;
    const auto& source = sources_.at(it->second.plan.source);
    const bool current = advanced == DemandCode::accepted && !it->second.cancelled && source.plan &&
        source.revision == it->second.plan_revision && policy_.available && policy_.revision == it->second.policy_revision;
    confirm_stopped(ticket); return current ? DemandCode::accepted : DemandCode::obsolete;
}
std::vector<DemandJob> DemandOwner::outstanding() const {
    std::vector<DemandJob> result; result.reserve(jobs_.size());
    for (const auto& row : jobs_) result.push_back(row.second);
    return result;
}
}
