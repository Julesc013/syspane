#pragma once
#include "installation_linux.hpp"
#include "profile_owner_linux.hpp"
#include "profile_projection.hpp"
#include "settings_draft.hpp"
#include <memory>

namespace syspane::application {
struct FrontendProfile {
    configuration::ProfileView view;
    interfaces::SettingsResources resources;
    std::string epoch;
    std::uint64_t serial=0;
};
struct FrontendReply {
    std::uint64_t ticket=0;
    std::string query,epoch;
    configuration::Json body;
};
struct FrontendView {
    std::shared_ptr<const FrontendProfile> profile;
    std::optional<FrontendReply> reply;
    std::string status;
    std::uint64_t withdrawal=0;
    bool pending=false,loading=true,closing=false,stopped=false,failed=false;
};
// UI methods only transfer bounded intent/state. Native ownership and validation
// live on separate supervisory and client workers. Close, await stopped, then join.
class LinuxFrontendBackend {
public:
    LinuxFrontendBackend(platform::HelperExpectation,std::string runtime_base,platform::ProfileLocation);
    ~LinuxFrontendBackend();
    LinuxFrontendBackend(const LinuxFrontendBackend&)=delete;
    LinuxFrontendBackend& operator=(const LinuxFrontendBackend&)=delete;
    FrontendView take();
    std::string request_id();
    void submit(const interfaces::EditRequest&);
    void cancel(const interfaces::EditRequest&);
    void reload();
    void retrieve();
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
int run_frontend(int argc,char** argv,platform::HelperExpectation);
}
