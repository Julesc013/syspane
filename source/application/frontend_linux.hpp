#pragma once
#include "installation_linux.hpp"
#include "profile_owner_linux.hpp"
#include "profile_projection.hpp"
#include "settings_draft.hpp"
#include "editor_draft.hpp"
#include "image_job.hpp"
#include "editor_recovery.hpp"
#include "editor_history_task.hpp"
#include "recovery_queue_linux.hpp"
#include <memory>
#include <functional>

namespace syspane::application {
struct FrontendProfile {
    configuration::ProfileView view;
    interfaces::SettingsResources resources;
    std::string epoch;
    std::uint64_t serial=0;
    // Accepted original-request metadata, not permission to delete. A fresh
    // admitted load must match this digest before conditional retirement.
    std::optional<std::string> recovery_retirement;
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
    LinuxFrontendBackend(platform::HelperBundleExpectation,std::string runtime_base,platform::ProfileLocation,bool recovery_admitted=false);
    ~LinuxFrontendBackend();
    LinuxFrontendBackend(const LinuxFrontendBackend&)=delete;
    LinuxFrontendBackend& operator=(const LinuxFrontendBackend&)=delete;
    FrontendView take();
    // Consumes only the exact current profile's initial editor, once. Empty means
    // unavailable/stale/already consumed; it never falls back to GTK preparation.
    std::unique_ptr<interfaces::PreparedEditor> take_editor(const std::shared_ptr<const FrontendProfile>&);
    std::string request_id();
    rendering::ImageFactory images()const;
    std::shared_ptr<const platform::RecoveryFactory> recovery()const;
    std::shared_ptr<const interfaces::RecoveryPreparationFactory> preparations()const;
    std::shared_ptr<const interfaces::HistoryPreparationFactory> history_preparations()const;
    void submit(const interfaces::EditRequest&,std::optional<std::string> captured_digest={});
    void acknowledge_retirement(std::uint64_t profile_serial);
    void cancel(const interfaces::EditRequest&);
    void reload();
    void retrieve();
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
// Optional experiment observer: tick work and excess interval delay, in microseconds.
// Returning false fails the host and initiates ordinary supervised shutdown.
using FrontendTimingObserver=std::function<bool(std::uint64_t,std::uint64_t)>;
enum class FrontendPhase : unsigned {take=1,withdrawal,reply,reply_reload,populate,editor,settings,recovery,attach,topology,controls};
struct FrontendPhaseObservation {std::uint64_t tick;FrontendPhase phase;std::uint64_t microseconds;bool completed;};
// Optional synchronous diagnosis only. Nested durations overlap. Refusal fails
// the host and disables observation so ordinary shutdown can still finish.
using FrontendPhaseObserver=std::function<bool(const FrontendPhaseObservation&)>;
int run_frontend(int argc,char** argv,platform::HelperBundleExpectation,bool recovery_admitted=false,FrontendTimingObserver={},FrontendPhaseObserver={});
}
