#pragma once

#include <array>
#include <cstdint>
#include <optional>
#include <string>

namespace syspane::recovery {

enum class Code {
    accepted, duplicate, closed, stale_attachment, invalid, sequence_order,
    snapshot_required, busy, clock_fault, circuit_open, quarantined, not_due
};

// Invocation times belong to one serialized owner, not to a remote process.
class Clock {
public:
    bool observe(std::uint64_t now);
private:
    std::optional<std::uint64_t> last_;
    bool fault_ = false;
};

enum class Presentation { empty, waiting, active, retained };
enum class LeaseReason { none, disconnected, expired, resync, invalid, clock_fault };
struct AcceptedUpdate {
    std::string producer, epoch;
    std::uint64_t generation, accepted_ms;
};
struct LeaseView {
    bool alive, snapshot_required;
    Presentation presentation;
    LeaseReason reason;
    std::optional<AcceptedUpdate> last;
};
struct Attachment { Code code; std::uint64_t token; };

// No payload is owned here. Notify only after full data validation; the data owner
// enforces current policy on retention/presentation. This token grants no authority.
class ProducerLease {
public:
    ProducerLease() = default;
    ProducerLease(const ProducerLease&) = delete;
    ProducerLease& operator=(const ProducerLease&) = delete;
    Attachment attach(const std::string& producer, const std::string& epoch, std::uint64_t now);
    Code heartbeat(std::uint64_t token, std::uint64_t sequence, std::uint64_t now);
    Code snapshot(std::uint64_t token, const std::string& producer, const std::string& epoch,
                  std::uint64_t generation, std::uint64_t now);
    Code delta(std::uint64_t token, std::uint64_t base, std::uint64_t next, std::uint64_t now);
    Code gap(std::uint64_t token, std::uint64_t now);
    Code disconnect(std::uint64_t token, std::uint64_t now);
    Code forget(std::uint64_t now);
    Code tick(std::uint64_t now);
    LeaseView view() const;
private:
    Code check(std::uint64_t token, std::uint64_t now);
    void close(LeaseReason reason);
    Clock clock_;
    std::uint64_t token_ = 0, renewed_ = 0;
    std::string producer_, epoch_;
    std::optional<std::uint64_t> sequence_, generation_;
    std::optional<AcceptedUpdate> last_;
    bool alive_ = false, needs_snapshot_ = true;
    LeaseReason reason_ = LeaseReason::none;
};

enum class RenderState { idle, awaiting, stalled, clock_fault };
struct RenderView {
    RenderState state;
    std::optional<std::uint64_t> pending, completed;
};
// One render-path challenge, separate from IPC health and external pixel evidence.
class RenderWatch {
public:
    RenderWatch() = default;
    RenderWatch(const RenderWatch&) = delete;
    RenderWatch& operator=(const RenderWatch&) = delete;
    Code issue(std::uint64_t generation, std::uint64_t now);
    Code complete(std::uint64_t generation, std::uint64_t now);
    Code tick(std::uint64_t now);
    RenderView view() const;
private:
    Clock clock_;
    RenderState state_ = RenderState::idle;
    std::uint64_t issued_ms_ = 0;
    std::optional<std::uint64_t> pending_, completed_;
};

enum class ChildState { idle, running, waiting, quarantined, circuit_open, stopped, clock_fault };
// One independent absolute deadline per controller transaction. A failed watch
// cannot be renewed; replace it only with a new, independently owned child.
class TransactionWatch {
public:
    TransactionWatch()=default;
    TransactionWatch(const TransactionWatch&)=delete;
    TransactionWatch& operator=(const TransactionWatch&)=delete;
    Code started(std::uint64_t ticket,std::uint64_t now);
    Code finished(std::uint64_t ticket,std::uint64_t now);
    Code tick(std::uint64_t now);
    std::optional<std::uint64_t> pending()const{return pending_;}
private:
    Clock clock_;
    std::optional<std::uint64_t> pending_,completed_;
    std::uint64_t started_ms_=0;
    bool failed_=false;
};
enum class Failure { launch_failed, crashed, producer_expired, render_stalled, operation_timeout };
enum class StopProof { unconfirmed, confirmed };
struct FailureRecord { Failure reason; std::uint64_t observed_ms; };
struct RestartView {
    ChildState state;
    std::uint32_t restarts_in_window, backoff_ms;
    std::optional<FailureRecord> last_failure;
};

// Manages decisions for exactly one owned child. Native code must hold its exact
// process identity and independently confirm termination before supplying proof.
class RestartGate {
public:
    explicit RestartGate(std::uint32_t jitter_ms);
    RestartGate(const RestartGate&) = delete;
    RestartGate& operator=(const RestartGate&) = delete;
    Code start(std::uint64_t now);
    Code failed(Failure reason, StopProof proof, std::uint64_t now);
    Code stopped(StopProof proof, std::uint64_t now);
    Code confirm_stopped(std::uint64_t now);
    Code reset(std::uint64_t now);
    Code tick(std::uint64_t now);
    RestartView view() const;
private:
    void after_stop();
    Code unavailable() const;
    Clock clock_;
    ChildState state_ = ChildState::idle;
    std::array<std::uint64_t, 3> restarts_{};
    std::uint32_t count_ = 0, streak_ = 0, delay_ = 0, jitter_;
    std::uint64_t started_ = 0;
    bool graceful_ = false;
    std::optional<FailureRecord> failure_;
};

} // namespace syspane::recovery
