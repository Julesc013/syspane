#include "recovery.hpp"

#include <limits>
#include <stdexcept>

namespace syspane::recovery {
namespace {
bool alnum(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9');
}
bool identity(const std::string& id) {
    if (id.empty() || id.size() > 256 || !alnum(id.front())) return false;
    for (char c : id) if (!alnum(c) && c != ':' && c != '.' && c != '_' && c != '/' && c != '-') return false;
    return true;
}
} // namespace

bool Clock::observe(std::uint64_t now) {
    if (last_ && now < *last_) fault_ = true;
    if (fault_) return false;
    last_ = now;
    return true;
}

void ProducerLease::close(LeaseReason reason) {
    alive_ = false;
    needs_snapshot_ = true;
    reason_ = reason;
}
Code ProducerLease::tick(std::uint64_t now) {
    if (!clock_.observe(now)) { close(LeaseReason::clock_fault); return Code::clock_fault; }
    if (alive_ && now - renewed_ >= 3000) close(LeaseReason::expired);
    return Code::accepted;
}
Attachment ProducerLease::attach(const std::string& producer, const std::string& epoch, std::uint64_t now) {
    if (tick(now) == Code::clock_fault) return {Code::clock_fault, 0};
    if (!identity(producer) || !identity(epoch)) return {Code::invalid, 0};
    if (token_ == std::numeric_limits<std::uint64_t>::max()) {
        close(LeaseReason::invalid);
        return {Code::closed, 0};
    }
    // Copy only after bounds validation; rejected IDs allocate no guard-owned copy.
    // Prepare both first so allocation failure cannot partly replace an attachment.
    std::string next_producer(producer), next_epoch(epoch);
    producer_.swap(next_producer);
    epoch_.swap(next_epoch);
    ++token_;
    renewed_ = now;
    sequence_.reset(); generation_.reset();
    alive_ = true; needs_snapshot_ = true; reason_ = LeaseReason::none;
    return {Code::accepted, token_};
}
Code ProducerLease::check(std::uint64_t token, std::uint64_t now) {
    // Late callbacks from a replaced connection cannot poison its successor clock.
    if (!token || token != token_) return Code::stale_attachment;
    if (tick(now) == Code::clock_fault) return Code::clock_fault;
    return alive_ ? Code::accepted : Code::closed;
}
Code ProducerLease::heartbeat(std::uint64_t token, std::uint64_t sequence, std::uint64_t now) {
    const auto checked = check(token, now);
    if (checked != Code::accepted) return checked;
    if (sequence_ && sequence == *sequence_) return Code::duplicate;
    if (sequence_ && sequence < *sequence_) { close(LeaseReason::invalid); return Code::sequence_order; }
    sequence_ = sequence; renewed_ = now;
    return Code::accepted;
}
Code ProducerLease::snapshot(std::uint64_t token, const std::string& producer, const std::string& epoch,
                             std::uint64_t generation, std::uint64_t now) {
    const auto checked = check(token, now);
    if (checked != Code::accepted) return checked;
    if (producer != producer_ || epoch != epoch_) { close(LeaseReason::invalid); return Code::invalid; }
    if (generation_ && generation < *generation_) {
        needs_snapshot_ = true; reason_ = LeaseReason::resync;
        return Code::sequence_order;
    }
    if (!needs_snapshot_ && generation_ && generation == *generation_) return Code::duplicate;
    last_ = AcceptedUpdate{producer_, epoch_, generation, now};
    generation_ = generation; needs_snapshot_ = false; reason_ = LeaseReason::none;
    return Code::accepted;
}
Code ProducerLease::delta(std::uint64_t token, std::uint64_t base, std::uint64_t next, std::uint64_t now) {
    const auto checked = check(token, now);
    if (checked != Code::accepted) return checked;
    if (needs_snapshot_ || !generation_ || base != *generation_ || next <= base) {
        needs_snapshot_ = true; reason_ = LeaseReason::resync;
        return Code::snapshot_required;
    }
    last_ = AcceptedUpdate{producer_, epoch_, next, now};
    generation_ = next;
    return Code::accepted;
}
Code ProducerLease::gap(std::uint64_t token, std::uint64_t now) {
    const auto checked = check(token, now);
    if (checked != Code::accepted) return checked;
    needs_snapshot_ = true; reason_ = LeaseReason::resync;
    return Code::accepted;
}
Code ProducerLease::disconnect(std::uint64_t token, std::uint64_t now) {
    const auto checked = check(token, now);
    if (checked != Code::accepted) return checked;
    close(LeaseReason::disconnected);
    return Code::accepted;
}
Code ProducerLease::forget(std::uint64_t now) {
    const auto result = tick(now);
    // Even a broken clock must not prevent removal of no-longer-permitted data.
    last_.reset(); needs_snapshot_ = true;
    if (alive_) reason_ = LeaseReason::resync;
    return result;
}
LeaseView ProducerLease::view() const {
    const auto presentation = last_ ? (alive_ && !needs_snapshot_ ? Presentation::active : Presentation::retained)
                                    : (alive_ ? Presentation::waiting : Presentation::empty);
    return {alive_, needs_snapshot_, presentation, reason_, last_};
}

Code RenderWatch::tick(std::uint64_t now) {
    if (!clock_.observe(now)) { state_ = RenderState::clock_fault; return Code::clock_fault; }
    if (state_ == RenderState::awaiting && now - issued_ms_ >= 3000) state_ = RenderState::stalled;
    return state_ == RenderState::stalled ? Code::closed : Code::accepted;
}
Code RenderWatch::issue(std::uint64_t generation, std::uint64_t now) {
    const auto result = tick(now);
    if (result != Code::accepted) return result;
    if (state_ == RenderState::awaiting) return Code::busy;
    if (completed_ && generation <= *completed_) return Code::sequence_order;
    pending_ = generation; issued_ms_ = now; state_ = RenderState::awaiting;
    return Code::accepted;
}
Code RenderWatch::complete(std::uint64_t generation, std::uint64_t now) {
    const auto result = tick(now);
    if (result != Code::accepted) return result;
    if (completed_ && generation == *completed_) return Code::duplicate;
    if (!pending_ || generation != *pending_) return Code::invalid;
    completed_ = generation; pending_.reset(); state_ = RenderState::idle;
    return Code::accepted;
}
RenderView RenderWatch::view() const { return {state_, pending_, completed_}; }

RestartGate::RestartGate(std::uint32_t jitter_ms) : jitter_(jitter_ms) {
    if (jitter_ms > 250) throw std::invalid_argument("recovery.jitter");
}
Code TransactionWatch::tick(std::uint64_t now){
    if(!clock_.observe(now)){failed_=true;return Code::clock_fault;}
    if(pending_&&now-started_ms_>=5000)failed_=true;
    return failed_?Code::closed:Code::accepted;
}
Code TransactionWatch::started(std::uint64_t ticket,std::uint64_t now){
    const auto checked=tick(now);if(checked!=Code::accepted)return checked;
    if(!ticket||pending_||(completed_&&ticket<=*completed_)){failed_=true;return Code::invalid;}
    pending_=ticket;started_ms_=now;return Code::accepted;
}
Code TransactionWatch::finished(std::uint64_t ticket,std::uint64_t now){
    const auto checked=tick(now);if(checked!=Code::accepted)return checked;
    if(!pending_||*pending_!=ticket){failed_=true;return Code::invalid;}
    completed_=ticket;pending_.reset();return Code::accepted;
}
Code RestartGate::tick(std::uint64_t now) {
    if (!clock_.observe(now)) { state_ = ChildState::clock_fault; return Code::clock_fault; }
    while (count_ && now - restarts_[0] >= 60000) {
        for (std::uint32_t i = 1; i < count_; ++i) restarts_[i-1] = restarts_[i];
        --count_;
    }
    return Code::accepted;
}
Code RestartGate::unavailable() const {
    if (state_ == ChildState::circuit_open) return Code::circuit_open;
    if (state_ == ChildState::quarantined) return Code::quarantined;
    if (state_ == ChildState::running) return Code::busy;
    return Code::closed;
}
Code RestartGate::start(std::uint64_t now) {
    if (tick(now) == Code::clock_fault) return Code::clock_fault;
    if (state_ == ChildState::waiting) {
        if (count_ == restarts_.size()) { state_ = ChildState::circuit_open; return Code::circuit_open; }
        if (now - failure_->observed_ms < delay_) return Code::not_due;
        restarts_[count_++] = now;
    } else if (state_ != ChildState::idle) return unavailable();
    started_ = now; state_ = ChildState::running; graceful_ = false;
    return Code::accepted;
}
void RestartGate::after_stop() {
    state_ = graceful_ ? ChildState::stopped : (count_ == restarts_.size() ? ChildState::circuit_open : ChildState::waiting);
}
Code RestartGate::failed(Failure reason, StopProof proof, std::uint64_t now) {
    if (tick(now) == Code::clock_fault) return Code::clock_fault;
    if (state_ != ChildState::running) return unavailable();
    if (now - started_ >= 60000) streak_ = 0;
    if (streak_ < 3) ++streak_;
    delay_ = (1000U << (streak_ - 1)) + jitter_;
    failure_ = FailureRecord{reason, now}; graceful_ = false;
    if (proof == StopProof::confirmed) after_stop(); else state_ = ChildState::quarantined;
    return Code::accepted;
}
Code RestartGate::stopped(StopProof proof, std::uint64_t now) {
    if (tick(now) == Code::clock_fault) return Code::clock_fault;
    if (state_ != ChildState::running) return unavailable();
    graceful_ = true;
    if (proof == StopProof::confirmed) after_stop(); else state_ = ChildState::quarantined;
    return Code::accepted;
}
Code RestartGate::confirm_stopped(std::uint64_t now) {
    if (tick(now) == Code::clock_fault) return Code::clock_fault;
    if (state_ != ChildState::quarantined) return Code::closed;
    after_stop();
    return Code::accepted;
}
Code RestartGate::reset(std::uint64_t now) {
    if (tick(now) == Code::clock_fault) return Code::clock_fault;
    if (state_ == ChildState::running || state_ == ChildState::quarantined) return unavailable();
    count_ = 0; streak_ = 0; delay_ = 0; graceful_ = false; state_ = ChildState::idle;
    return Code::accepted;
}
RestartView RestartGate::view() const { return {state_, count_, delay_, failure_}; }

} // namespace syspane::recovery
