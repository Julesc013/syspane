#include "child.hpp"
#include "health_link.hpp"
#include "recovery.hpp"
#include "failure_store.hpp"
#include <chrono>
#include <condition_variable>
#include <cstdlib>
#include <iostream>
#include <mutex>
#include <thread>

namespace p = syspane::platform;
namespace r = syspane::recovery;
namespace w = syspane::protocol;
using w::Json;
namespace {
void emit(Json value) { value["observed_ms"] = p::monotonic_ms(); std::cout << value.dump() << std::endl; }
void require(bool condition, const char* code) { if (!condition) throw w::Error(code); }
void pause(unsigned ms) { std::this_thread::sleep_for(std::chrono::milliseconds(ms)); }

class RenderWorker {
public:
    explicit RenderWorker(bool stall) : thread_([this, stall] {
        std::unique_lock<std::mutex> lock(mutex_);
        for (;;) {
            ready_.wait(lock, [&] { return stop_ || (!stall && pending_ != completed_); });
            if (stop_) return;
            completed_ = pending_; // Synthetic work only: no pixels are rendered.
        }
    }) {}
    ~RenderWorker() {
        { std::lock_guard<std::mutex> lock(mutex_); stop_ = true; }
        ready_.notify_one(); thread_.join();
    }
    void request(std::uint64_t generation) {
        { std::lock_guard<std::mutex> lock(mutex_); pending_ = generation; }
        ready_.notify_one();
    }
    std::uint64_t completed() { std::lock_guard<std::mutex> lock(mutex_); return completed_; }
private:
    std::mutex mutex_;
    std::condition_variable ready_;
    bool stop_ = false;
    std::uint64_t pending_ = 0, completed_ = 0;
    std::thread thread_;
};
void worker(const std::string& endpoint, const std::string& scenario, const std::string& role, std::uint64_t parent) {
    p::arm_parent_lifetime(parent);
    auto stream = p::Stream::connect(endpoint, parent);
    r::HealthLink link(stream, false, scenario == "role-denial" ? "maintenance" : role,
        "worker:" + std::to_string(p::current_process_id()), "");
    r::ProducerLease lease;
    std::uint64_t token = 0, sent = 0, last_sent = 0, last_progress = 0;
    RenderWorker renderer(scenario == "render-stall");
    const auto started = p::monotonic_ms();
    while (p::monotonic_ms() - started < 35000) {
        for (const auto& event : link.poll()) {
            if (event.kind == r::HealthKind::ready) {
                token = lease.attach("supervisor", link.epoch(), event.observed_ms).token;
                if (scenario == "crash") { pause(500); std::_Exit(73); }
                if (scenario == "wrong-epoch") {
                    stream.write(w::frame(Json{{"type", "heartbeat"}, {"body", {{"sequence", "0"}}},
                        {"connection_id", link.connection()}, {"producer_epoch", "old:epoch"}}.dump(), 4096), 100);
                    for (;;) pause(100);
                }
            } else if (event.kind == r::HealthKind::heartbeat) {
                const auto code = lease.heartbeat(token, event.value, event.observed_ms);
                require(code == r::Code::accepted || code == r::Code::duplicate, "worker.heartbeat");
            } else if (event.kind == r::HealthKind::challenge) {
                if (scenario == "progress-denial") {
                    stream.write(w::frame(Json{{"type", "render.progress"}, {"body", {{"generation", std::to_string(event.value + 1)}}},
                        {"connection_id", link.connection()}, {"producer_epoch", link.epoch()}}.dump(), 4096), 100);
                } else renderer.request(event.value);
            }
            else if (event.kind == r::HealthKind::shutdown) return;
        }
        const auto now = p::monotonic_ms();
        if (link.ready()) {
            lease.tick(now); require(lease.view().alive, "worker.parent_expired");
            if (!sent || now - last_sent >= 1000) {
                link.heartbeat(sent++); last_sent = now;
                if (scenario == "producer-hang" && sent == 2) for (;;) pause(100);
            }
            const auto done = renderer.completed();
            if (done > last_progress) { link.progress(done); last_progress = done; }
        }
    }
    throw w::Error("worker.deadline");
}
std::optional<p::ChildExit> wait_child(p::Child& child, r::RestartGate& gate, unsigned limit) {
    const auto start = p::monotonic_ms();
    for (;;) {
        const auto result = child.wait(0);
        gate.tick(p::monotonic_ms());
        if (result || p::monotonic_ms() - start >= limit) return result;
        pause(10);
    }
}
void stopped_event(p::Child& child, const p::ChildExit& exit, bool forced) {
    emit({{"event", "stopped"}, {"pid", child.id()}, {"code", exit.code}, {"signaled", exit.signaled},
          {"forced", forced}, {"os_confirmed", true}});
}
void supervisor(const std::string& endpoint, const std::string& scenario, const std::string& failure_path) {
    const std::set<std::string> cases{"graceful", "producer-hang", "render-stall", "crash-circuit", "quarantine", "parent-loss", "role-denial", "wrong-epoch", "progress-denial"};
    require(cases.count(scenario), "probe.scenario");
    const bool desktop = scenario == "graceful" || scenario == "render-stall" || scenario == "progress-denial";
    const std::string role = desktop ? "desktop" : "collector";
    p::Listener listener(endpoint);
    require(listener.access_controls_verified(), "probe.endpoint_controls");
    emit({{"event", "ready"}, {"unprivileged", true}, {"endpoint_controls", true}});
    r::RestartGate gate(0);
    const auto campaign_start = p::monotonic_ms();
    std::unique_ptr<p::FailureWriter> journal;
    if (!failure_path.empty()) {
        journal = std::make_unique<p::FailureWriter>(failure_path);
        emit({{"event", "failure_recording"}, {"ready", journal->ready()}});
    }
    for (unsigned attempt = 0; attempt < 4; ++attempt) {
        for (;;) {
            require(p::monotonic_ms() - campaign_start < 40000, "probe.deadline");
            const auto code = gate.start(p::monotonic_ms());
            if (code == r::Code::accepted) break;
            require(code == r::Code::not_due, "probe.restart_state"); pause(10);
        }
        const auto mode = scenario == "crash-circuit" ? "crash" : (attempt == 0 ? scenario : "healthy");
        auto child = p::Child::launch_self({"worker", endpoint, mode, role, std::to_string(p::current_process_id())});
        emit({{"event", "spawned"}, {"pid", child.id()}, {"attempt", attempt}, {"role", role}});
        pause(250); // Bounded test-observer attachment window, before welcoming the child.
        auto stream = listener.accept(child.id());
        const auto epoch = "supervisor:" + std::to_string(p::current_process_id()) + ":" + std::to_string(attempt);
        r::HealthLink link(stream, true, role, epoch, "C:" + std::to_string(attempt));
        r::ProducerLease lease; r::RenderWatch render;
        std::uint64_t token = 0, sent = 0, last_sent = 0, received = 0, completed = 0;
        std::uint64_t last_received = 0, challenge_time = 0, challenge = 0, last_challenge = 0;
        std::string failure;
        r::Failure failure_kind = r::Failure::crashed;
        const bool healthy = scenario == "graceful" || attempt > 0;
        try {
            while (failure.empty()) {
                require(p::monotonic_ms() - campaign_start < 40000, "probe.deadline");
                for (const auto& event : link.poll()) {
                    if (event.kind == r::HealthKind::ready) {
                        token = lease.attach("worker", epoch, event.observed_ms).token;
                        last_received = event.observed_ms;
                        emit({{"event", "authenticated"}, {"pid", child.id()}, {"peer_pid", stream.peer().process_id},
                              {"role", role}, {"epoch", epoch}});
                    } else if (event.kind == r::HealthKind::heartbeat) {
                        const auto code = lease.heartbeat(token, event.value, event.observed_ms);
                        if (code == r::Code::duplicate) continue;
                        require(code == r::Code::accepted, "probe.heartbeat");
                        ++received; last_received = event.observed_ms;
                        emit({{"event", "heartbeat"}, {"pid", child.id()}, {"sequence", event.value}});
                    } else if (event.kind == r::HealthKind::progress) {
                        require(render.complete(event.value, event.observed_ms) == r::Code::accepted, "probe.render_late");
                        ++completed; emit({{"event", "progress"}, {"pid", child.id()}, {"generation", event.value}});
                    } else throw w::Error("probe.unexpected_event");
                }
                const auto now = p::monotonic_ms();
                if (child.wait(0)) { failure = "child.exited"; break; }
                if (!link.ready()) continue;
                lease.tick(now); render.tick(now);
                if (!lease.view().alive) { failure = "producer.expired"; failure_kind = r::Failure::producer_expired; break; }
                if (render.view().state == r::RenderState::stalled) { failure = "render.stalled"; failure_kind = r::Failure::render_stalled; break; }
                if (!sent || now - last_sent >= 1000) { link.heartbeat(sent++); last_sent = now; }
                if (desktop && render.view().state == r::RenderState::idle && (!challenge || now - last_challenge >= 1000)) {
                    ++challenge; require(render.issue(challenge, now) == r::Code::accepted, "probe.challenge");
                    link.challenge(challenge); challenge_time = now; last_challenge = now;
                    emit({{"event", "challenge"}, {"pid", child.id()}, {"generation", challenge}});
                }
                if (scenario == "quarantine" && attempt == 0 && received >= 2) { failure = "worker.unconfirmed"; failure_kind = r::Failure::operation_timeout; break; }
                if (healthy && scenario != "crash-circuit" && received >= 3 && (!desktop || completed >= 2)) {
                    link.shutdown();
                    const auto result = wait_child(child, gate, 1000);
                    require(result.has_value() && !result->signaled && result->code == 0, "probe.graceful_exit");
                    require(gate.stopped(r::StopProof::confirmed, p::monotonic_ms()) == r::Code::accepted, "probe.graceful_gate");
                    stopped_event(child, *result, false);
                    emit({{"event", "complete"}, {"launches", attempt+1}, {"heartbeats", received}, {"completions", completed}});
                    return;
                }
            }
        } catch (const w::Error& error) { failure = error.what(); }
          catch (const p::IpcError& error) { failure = error.what(); }
        auto exit = child.wait(0);
        if (!exit && (failure == "health.eof" || failure == "io.read")) exit = wait_child(child, gate, 100);
        if (exit) failure_kind = r::Failure::crashed;
        const auto fault_time = p::monotonic_ms();
        const bool stopped_at_fault = exit.has_value();
        require(gate.failed(failure_kind, exit ? r::StopProof::confirmed : r::StopProof::unconfirmed, fault_time) == r::Code::accepted,
                "probe.failure_gate");
        emit({{"event", "fault"}, {"pid", child.id()}, {"reason", failure}, {"alive", !exit.has_value()},
              {"since_heartbeat_ms", fault_time-last_received}, {"since_challenge_ms", challenge_time ? fault_time-challenge_time : 0},
              {"heartbeats", received}, {"completions", completed}, {"backoff_ms", gate.view().backoff_ms}});
        bool forced = false;
        if (!exit) {
            require(gate.start(fault_time) == r::Code::quarantined && gate.reset(fault_time) == r::Code::quarantined,
                    "probe.quarantine_gate");
            if (scenario == "quarantine") {
                const auto held = p::monotonic_ms();
                while (p::monotonic_ms() - held < 250) { require(!child.wait(0), "probe.quarantine_child"); gate.tick(p::monotonic_ms()); pause(10); }
                emit({{"event", "quarantined"}, {"pid", child.id()}, {"child_alive", true},
                      {"elapsed_ms", p::monotonic_ms()-held}, {"start_denied", true}, {"reset_denied", true}});
            }
            try { if (link.ready()) link.shutdown(); } catch (const std::exception&) { /* Already closed link. */ }
            exit = wait_child(child, gate, 250);
            if (!exit) { child.request_stop(); forced = true; exit = wait_child(child, gate, 2000); }
            require(exit.has_value(), "probe.stop_unconfirmed");
            require(gate.confirm_stopped(p::monotonic_ms()) == r::Code::accepted, "probe.confirm_gate");
        }
        stopped_event(child, *exit, forced);
        // Optional filesystem work must not precede cleanup of a live failed child.
        // The record retains the original fault observation, not this later write time.
        if (journal) {
            const auto reason = scenario == "role-denial" || scenario == "wrong-epoch" || scenario == "progress-denial" ? "protocol_rejected" :
                failure_kind == r::Failure::producer_expired ? "producer_expired" :
                failure_kind == r::Failure::render_stalled ? "render_stalled" :
                failure_kind == r::Failure::operation_timeout ? "operation_timeout" : "crashed";
            emit({{"event", "failure_recorded"}, {"stored", journal->append(fault_time-campaign_start, role, reason, stopped_at_fault)}});
        }
        if (scenario == "role-denial" || scenario == "wrong-epoch" || scenario == "progress-denial") {
            emit({{"event", "rejected"}, {"reason", failure}, {"heartbeats", received}, {"launches", attempt+1}}); return;
        }
        if (gate.view().state == r::ChildState::circuit_open) {
            const auto opened = p::monotonic_ms();
            while (p::monotonic_ms() - opened < 500) {
                require(gate.start(p::monotonic_ms()) == r::Code::circuit_open, "probe.circuit_gate"); pause(10);
            }
            emit({{"event", "circuit_open"}, {"launches", attempt+1}, {"observed_ms_after_open", p::monotonic_ms()-opened}}); return;
        }
    }
    throw w::Error("probe.launch_limit");
}
} // namespace
int main(int argc, char** argv) {
    try {
        require(p::unprivileged_context(), "probe.privileged_context");
        const auto arguments = p::native_arguments(argc, argv);
        if ((arguments.size() == 4 || arguments.size() == 5) && arguments[1] == "supervisor")
            supervisor(arguments[2], arguments[3], arguments.size() == 5 ? arguments[4] : "");
        else if (arguments.size() == 6 && arguments[1] == "worker") {
            const auto parent = w::decimal(arguments[5]); require(parent && *parent, "worker.parent");
            worker(arguments[2], arguments[3], arguments[4], *parent);
        } else throw w::Error("probe.arguments");
        return 0;
    } catch (const std::exception& error) { emit({{"event", "error"}, {"reason", error.what()}}); return 1; }
}
