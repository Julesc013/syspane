#pragma once
#include "profile_owner_linux.hpp"
#include "child.hpp"
#include "recovery.hpp"
#include "installation_linux.hpp"
#include <vector>

namespace syspane::application {
enum class LocalService {configuration,network};
enum class ProfileSupervisorState {starting,ready,quarantined,waiting,circuit_open,unavailable,closing,closed};
struct ProfileSupervisorView {
    ProfileSupervisorState state=ProfileSupervisorState::starting;
    std::uint64_t generation=0,process=0;
    std::string epoch,endpoint,fault;
    recovery::RestartView restart{};
    std::optional<platform::ChildExit> last_exit;
};
struct ProfileSupervisorEvent {
    std::string kind;
    ProfileSupervisorView view;
    std::uint64_t observed_ms=0,ticket=0;
};
// Trusted native composition only. Run on an independent serialized owner, off UI
// callbacks. Admit the helper's installation identity before calling. Close, poll
// until closed, then destroy; the caller retains the empty runtime root.
class LinuxProfileSupervisor {
public:
    LinuxProfileSupervisor(std::string helper,std::string runtime,platform::ProfileLocation,
                           bool create,std::uint64_t console,LocalService service=LocalService::configuration);
    LinuxProfileSupervisor(std::shared_ptr<platform::LinuxInstallation>,std::string runtime,
                           platform::ProfileLocation,bool create,std::uint64_t console,LocalService service=LocalService::configuration);
    ~LinuxProfileSupervisor();
    LinuxProfileSupervisor(const LinuxProfileSupervisor&)=delete;
    LinuxProfileSupervisor& operator=(const LinuxProfileSupervisor&)=delete;
    ProfileSupervisorView poll();
    ProfileSupervisorView status()const;
    std::vector<ProfileSupervisorEvent> take();
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
