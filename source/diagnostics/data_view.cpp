#include "data_view.hpp"
#include "reported_state.hpp"
#include <limits>
#include <stdexcept>

namespace syspane::recovery {
namespace {
DataCode translated(Code code) {
    switch (code) {
    case Code::accepted: return DataCode::accepted;
    case Code::duplicate: return DataCode::duplicate;
    case Code::clock_fault: return DataCode::clock_fault;
    case Code::stale_attachment: return DataCode::stale_attachment;
    case Code::snapshot_required: return DataCode::snapshot_required;
    case Code::closed: return DataCode::closed;
    default: return DataCode::invalid;
    }
}
}
DataView::DataView(configuration::Authority authority, configuration::Policy policy,
                   std::string channel, std::string classification, std::vector<model::Metric> metrics, model::Limits limits)
    : authority_(std::move(authority)), policy_(std::move(policy)), channel_(std::move(channel)),
      classification_(std::move(classification)), metrics_(std::move(metrics)), limits_(limits) {
    if ((channel_ != "desktop" && channel_ != "inspector" && channel_ != "saver" && channel_ != "preview") ||
        (classification_ != "public" && classification_ != "operational" && classification_ != "sensitive"))
        throw std::invalid_argument("view.scope");
    const model::Limits ceiling;
    if (metrics_.size() > 1024 || limits_.entities > ceiling.entities || limits_.relationships > ceiling.relationships ||
        limits_.sources > ceiling.sources || limits_.observations > ceiling.observations || limits_.retired_entities > ceiling.retired_entities ||
        limits_.replay_records > ceiling.replay_records || limits_.candidate_bytes > ceiling.candidate_bytes || limits_.retained_bytes > ceiling.retained_bytes)
        throw std::invalid_argument("view.limits");
    // Validate the trusted registry through its existing owner before accepting data.
    model::Store validation("view:validation", "view:validation", metrics_, limits_);
    if (policy_.available) highest_policy_ = policy_.revision;
}
void DataView::require_owner() const { if (borrowed_) throw std::logic_error("view.reentrant"); }
bool DataView::permitted() const {
    return !lifetime_fault_ && policy_.available && !policy_.denied_capabilities.count("telemetry.subscribe") &&
        configuration::permits(authority_, policy_, channel_, classification_) &&
        configuration::permits(authority_, policy_, "accessibility", classification_);
}
bool DataView::advance_lifetime() {
    if (lifetime_ == std::numeric_limits<std::uint64_t>::max()) { lifetime_fault_ = true; return false; }
    ++lifetime_; return true;
}
void DataView::drop(std::uint64_t now) {
    store_.reset(); wire_binding_.reset(); producer_.clear(); epoch_.clear();
    if (token_) lease_.disconnect(token_, now);
    lease_.forget(now); token_ = 0;
}
DataAttachment DataView::attach(const std::string& producer, const std::string& epoch, std::uint64_t now) {
    require_owner();
    if (!permitted()) return {DataCode::denied};
    // Prepare strings before changing the lease. Its own identity checks bound storage.
    if (!protocol::identifier(producer) || !protocol::identifier(epoch)) return {DataCode::invalid};
    std::string next_producer(producer), next_epoch(epoch);
    const auto attached = lease_.attach(producer, epoch, now);
    if (attached.code != Code::accepted) return {translated(attached.code)};
    if (!advance_lifetime()) { drop(now); return {DataCode::closed}; }
    producer_.swap(next_producer); epoch_.swap(next_epoch); token_ = attached.token;
    wire_binding_.reset();
    return {DataCode::accepted, token_};
}
DataAttachment DataView::attach_wire(const protocol::TelemetryBinding& binding, std::uint64_t now) {
    require_owner();
    if (!permitted()) return {DataCode::denied};
    if (binding.policy_revision != policy_.revision) return {DataCode::policy_changed};
    if (binding.channel != channel_ || binding.classification != classification_ ||
        binding.direction != protocol::TelemetryDirection::producer_to_consumer) return {DataCode::invalid};
    try {
        protocol::validate_telemetry_binding(binding);
        auto prepared = std::make_unique<protocol::TelemetryBinding>(binding);
        const auto attached = attach(binding.producer,binding.epoch,now);
        if (attached.code == DataCode::accepted) wire_binding_.swap(prepared);
        return attached;
    } catch (const protocol::Error&) { return {DataCode::invalid}; }
    catch (const std::bad_alloc&) { return {DataCode::capacity}; }
}
DataResult DataView::receive(std::uint64_t token, std::uint64_t revision, std::string_view payload, std::uint64_t now) {
    const auto checked = check(token,revision,now);
    if (checked != DataCode::accepted) return {checked};
    if (!wire_binding_) { lease_.gap(token_,now); return {DataCode::invalid,model::Code::invalid_mode}; }
    try {
        const auto message = protocol::decode_telemetry(payload,*wire_binding_);
        if (message.body["snapshot"]["completeness"] != "complete") {
            lease_.gap(token_,now); return {DataCode::snapshot_required};
        }
        const auto candidate = detail::reported_state(message);
        return publish(message.type == "snapshot",token,revision,candidate,now,true);
    } catch (const protocol::Error& error) {
        if (std::string_view(error.what()) == "telemetry.capacity") {
            lease_.gap(token_,now); return {DataCode::capacity,model::Code::capacity};
        }
        lease_.disconnect(token_,now); return {DataCode::invalid};
    } catch (const std::bad_alloc&) {
        lease_.gap(token_,now); return {DataCode::capacity,model::Code::capacity};
    }
}
DataCode DataView::check(std::uint64_t token, std::uint64_t revision, std::uint64_t now) {
    require_owner();
    if (!token || token != token_) return DataCode::stale_attachment;
    if (revision != policy_.revision) return DataCode::policy_changed;
    if (!permitted()) return DataCode::denied;
    if (lease_.tick(now) == Code::clock_fault) return DataCode::clock_fault;
    return lease_.view().alive ? DataCode::accepted : DataCode::closed;
}
DataResult DataView::full(std::uint64_t token, std::uint64_t revision, const model::Publication& candidate, std::uint64_t now) {
    return publish(true, token, revision, candidate, now);
}
DataResult DataView::delta(std::uint64_t token, std::uint64_t revision, const model::Publication& candidate, std::uint64_t now) {
    return publish(false, token, revision, candidate, now);
}
DataResult DataView::publish(bool full, std::uint64_t token, std::uint64_t revision, const model::Publication& candidate, std::uint64_t now, bool reported) {
    const auto checked = check(token, revision, now);
    if (checked != DataCode::accepted) return {checked};
    if (reported != static_cast<bool>(wire_binding_)) {
        lease_.gap(token_,now); return {DataCode::invalid,model::Code::invalid_mode};
    }
    if (!full && lease_.view().snapshot_required) return {DataCode::snapshot_required};
    if (candidate.next.producer != producer_ || candidate.next.epoch != epoch_) {
        lease_.disconnect(token_, now);
        return {DataCode::invalid, model::Code::wrong_epoch};
    }
    if (full == candidate.expected_base.has_value()) {
        lease_.gap(token_, now);
        return {DataCode::invalid, model::Code::missing_base};
    }
    try {
        const auto old = store_ ? store_->snapshot() : nullptr;
        const bool same_scope = old && old->producer == producer_ && old->epoch == epoch_;
        auto prepared = same_scope ? std::make_unique<model::Store>(*store_) :
            std::make_unique<model::Store>(producer_, epoch_, metrics_, limits_);
        const auto validated = reported ? prepared->import_state(candidate) : (full ? prepared->resynchronize(candidate) : prepared->publish(candidate));
        if (!validated.accepted()) {
            lease_.gap(token_, now);
            return {validated.code == model::Code::capacity ? DataCode::capacity :
                validated.snapshot_required ? DataCode::snapshot_required : DataCode::invalid, validated.code};
        }
        const auto next = prepared->snapshot();
        if (validated.code == model::Code::duplicate && (!full || next->generation != candidate.next.generation))
            return {DataCode::duplicate, validated.code}; // Never replay an older record into the current view.
        const auto notified = full ? lease_.snapshot(token_, producer_, epoch_, next->generation, now) :
            lease_.delta(token_, *candidate.expected_base, next->generation, now);
        if (notified != Code::accepted && notified != Code::duplicate) return {translated(notified), validated.code};
        store_.swap(prepared); // All potentially throwing validation completed; publish data after lease acceptance.
        return {translated(notified), validated.code};
    } catch (const std::bad_alloc&) {
        lease_.gap(token_, now);
        return {DataCode::capacity, model::Code::capacity};
    }
}
DataCode DataView::heartbeat(std::uint64_t token, std::uint64_t revision, std::uint64_t sequence, std::uint64_t now) {
    const auto checked = check(token, revision, now);
    return checked == DataCode::accepted ? translated(lease_.heartbeat(token, sequence, now)) : checked;
}
DataCode DataView::gap(std::uint64_t token, std::uint64_t revision, std::uint64_t now) {
    const auto checked = check(token, revision, now);
    return checked == DataCode::accepted ? translated(lease_.gap(token, now)) : checked;
}
DataCode DataView::disconnect(std::uint64_t token, std::uint64_t revision, std::uint64_t now) {
    const auto checked = check(token, revision, now);
    return checked == DataCode::accepted ? translated(lease_.disconnect(token, now)) : checked;
}
DataCode DataView::policy(configuration::Policy next, std::uint64_t now) {
    require_owner();
    const bool valid = !next.available || !highest_policy_ || next.revision > *highest_policy_;
    // Removal is independent of clock validity and never restores an old store.
    drop(now); advance_lifetime();
    if (!valid) { policy_.available = false; return DataCode::policy_changed; }
    if (next.available) highest_policy_ = next.revision;
    policy_ = std::move(next);
    return permitted() ? DataCode::accepted : DataCode::denied;
}
DataStatus DataView::status(std::uint64_t now) {
    require_owner(); lease_.tick(now);
    const auto view = lease_.view();
    const bool allowed = permitted();
    return {allowed, allowed && view.alive, !allowed || view.snapshot_required, allowed && store_ && store_->snapshot(),
        allowed ? view.presentation : Presentation::empty, allowed ? view.reason : LeaseReason::none, lifetime_};
}
bool DataView::project(std::uint64_t now, const std::function<void(const model::Snapshot&, const LeaseView&)>& borrow) {
    require_owner();
    const auto state = status(now);
    if (!state.permitted || !state.payload_available) return false;
    const auto snapshot = store_->snapshot();
    const auto lease = lease_.view();
    struct Borrow {
        bool& flag;
        explicit Borrow(bool& flag) : flag(flag) { flag = true; }
        ~Borrow() { flag = false; }
    } guard(borrowed_);
    borrow(*snapshot, lease);
    return true;
}
}
