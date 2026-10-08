#pragma once
#include "wire.hpp"
#include <memory>

namespace syspane::platform {
struct RecoveryContext {
    std::string session,profile,generation;
    std::uint64_t policy_revision=0;
    bool read=false,retain=false,erase=false;
};
enum class RecoveryQueueState {loading,ready,busy,retiring,retired,unavailable,closing,closed};
struct RecoveryQueueStatus {
    RecoveryQueueState state=RecoveryQueueState::loading;
    std::uint64_t active=0,pending=0,process=0;
    std::size_t retained_bytes=0;
    bool reaped=true;
    std::string error;
};
struct RecoveryCompletion {
    RecoveryContext context;
    std::uint64_t ticket=0;
    std::string operation,outcome,error;
    std::optional<std::string> digest,bytes;
    bool pending=false;
};
// Serialized parent loop. Close, poll until reaped, then destroy. No recovery
// directory I/O runs on this loop; existing Child owns each native helper.
class LinuxRecoveryQueue {
public:
    LinuxRecoveryQueue(std::string worker,std::string directory,RecoveryContext);
    ~LinuxRecoveryQueue();
    LinuxRecoveryQueue(const LinuxRecoveryQueue&)=delete;
    LinuxRecoveryQueue& operator=(const LinuxRecoveryQueue&)=delete;
    std::uint64_t replace(std::string bytes);
    std::uint64_t retire();
    RecoveryQueueStatus poll();
    RecoveryQueueStatus status()const;
    std::optional<RecoveryCompletion> take();
    void close(); // Also the policy/session/generation invalidation operation.
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
