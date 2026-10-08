#pragma once
#include "wire.hpp"
#include <memory>
#include <functional>

namespace syspane::platform {
class LinuxInstallation;
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
class RecoveryTask {
public:
    virtual ~RecoveryTask()=default;
    virtual std::uint64_t replace(std::string)=0;
    virtual std::uint64_t retire()=0;
    virtual RecoveryQueueStatus poll()=0;
    virtual RecoveryQueueStatus status()const=0;
    virtual std::optional<RecoveryCompletion> take()=0;
    virtual void close()=0;
};
using RecoveryFactory=std::function<std::unique_ptr<RecoveryTask>(std::string directory,RecoveryContext)>;
// Serialized parent loop. Close, poll until reaped, then destroy. No recovery
// directory I/O runs on this loop; existing Child owns each native helper.
class LinuxRecoveryQueue final:public RecoveryTask {
public:
    LinuxRecoveryQueue(std::string worker,std::string directory,RecoveryContext);
    // Construct/poll on the installation's native worker; each operation
    // revalidates the bundle before sealed launch, without a pathname fallback.
    LinuxRecoveryQueue(std::shared_ptr<LinuxInstallation>,std::string directory,RecoveryContext);
    ~LinuxRecoveryQueue() override;
    LinuxRecoveryQueue(const LinuxRecoveryQueue&)=delete;
    LinuxRecoveryQueue& operator=(const LinuxRecoveryQueue&)=delete;
    std::uint64_t replace(std::string bytes) override;
    std::uint64_t retire() override;
    RecoveryQueueStatus poll() override;
    RecoveryQueueStatus status()const override;
    std::optional<RecoveryCompletion> take() override;
    void close() override; // Also the policy/session/generation invalidation operation.
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
