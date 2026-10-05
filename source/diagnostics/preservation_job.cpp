#include "preservation_job.hpp"
#include <atomic>
#include <mutex>

namespace syspane::diagnostics {
struct PreservationJob::State {
    std::atomic<bool> cancel{false}, done{false};
    std::mutex mutex;
    platform::PreserveResult result;
};
PreservationJob::PreservationJob(PolicyReader policy) : policy_(std::move(policy)) {}
PreservationJob::~PreservationJob() {
    cancel();
    if (worker_.joinable()) {
        if (busy()) worker_.detach(); // Entry lifetime ends immediately; never block native Close on storage.
        else worker_.join();
    }
}
bool PreservationJob::permitted() const {
    try { const auto policy = policy_(); return preservation_permitted(policy, policy.revision, true); }
    catch (...) { return false; }
}
bool PreservationJob::busy() const { return state_ && !state_->done.load(); }
bool PreservationJob::start(std::string source, std::string destination) {
    if (busy()) return false;
    if (worker_.joinable()) worker_.join();
    auto next = std::make_shared<State>();
    try {
        const auto initial = policy_();
        if (!preservation_permitted(initial, initial.revision, true)) return false;
        worker_ = std::thread([state = next, policy = policy_, revision = initial.revision,
                               source = std::move(source), destination = std::move(destination)] {
            const auto result = platform::preserve_file(source, destination, [&](platform::PreservePhase) {
                if (state->cancel.load()) return platform::PreserveCheck::cancel;
                return preservation_permitted(policy(), revision, true) ? platform::PreserveCheck::permit : platform::PreserveCheck::deny;
            });
            { std::lock_guard<std::mutex> lock(state->mutex); state->result = result; }
            state->done.store(true);
        });
        state_ = std::move(next);
        return true;
    } catch (...) { return false; }
}
void PreservationJob::cancel() { if (state_) state_->cancel.store(true); }
std::string PreservationJob::status() const {
    if (!state_) return "Choose a source and a new destination. Copies may contain private data.";
    if (busy()) return "Copy in progress. Close or Cancel requests cancellation.";
    std::lock_guard<std::mutex> lock(state_->mutex);
    const auto& result = state_->result;
    if (result.outcome == "preserved") return "Private copy preserved. No configuration was activated; power-loss durability is unqualified.";
    return "Copy outcome: " + result.outcome + (result.partial ? ". Private partial retained; choose a new destination." : ". No copy published.");
}
}
