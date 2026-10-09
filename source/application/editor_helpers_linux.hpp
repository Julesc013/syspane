#pragma once
#include "image_job.hpp"
#include "recovery_queue_linux.hpp"
#include "installation_linux.hpp"
#include "profile_projection.hpp"
#include "editor_recovery.hpp"
#include "editor_history_task.hpp"

namespace syspane::application {
struct RecoverySessionAuthority {
    std::string connection,epoch,profile,session;
    std::uint64_t revision=0,policy_revision=0;
    bool retain=false,erase=false;
};
// Native worker only. Current authority comes from the host's authenticated
// connection owner, independently of the received observation and GUI request.
class LinuxRecoveryAdmission {
public:
    using Current=std::function<std::optional<RecoverySessionAuthority>()>;
    LinuxRecoveryAdmission(const platform::ProfileLocation&,configuration::ProfileRecoveryView,Current);
    ~LinuxRecoveryAdmission();
    bool permitted(const std::string& operation);
    const platform::ProfileRecoveryDirectory& directory()const;
    platform::RecoveryContext context()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
using RecoveryAdmissionFactory=std::function<std::shared_ptr<LinuxRecoveryAdmission>()>;
struct EditorHelperStatus {
    bool attached=false,closing=false,stopped=false;
    std::size_t image_handles=0,recovery_handles=0,retained_bytes=0;
    // Preparation owns bounded authored snapshots, not encoded helper payloads.
    std::size_t preparation_handles=0;
    std::size_t history_handles=0;
    std::vector<std::uint64_t> processes;
};
struct EditorHelperChannel;
// GUI owner. Factories and task methods perform bounded memory/state work only.
// Close, continue pumping the native owner until stopped, then destroy the host.
class EditorHelperClient {
public:
    EditorHelperClient();
    ~EditorHelperClient();
    EditorHelperClient(const EditorHelperClient&)=delete;
    EditorHelperClient& operator=(const EditorHelperClient&)=delete;
    rendering::ImageFactory images()const;
    std::shared_ptr<const platform::RecoveryFactory> recovery()const;
    std::shared_ptr<const interfaces::RecoveryPreparationFactory> preparations()const;
    std::shared_ptr<const interfaces::HistoryPreparationFactory> history_preparations()const;
    EditorHelperStatus status()const;
    void close();
private:
    friend class LinuxEditorHelperOwner;
    std::shared_ptr<EditorHelperChannel> channel_;
    std::shared_ptr<const platform::RecoveryFactory> recovery_;
    std::shared_ptr<const interfaces::RecoveryPreparationFactory> preparations_;
    std::shared_ptr<const interfaces::HistoryPreparationFactory> history_preparations_;
};
// Existing host native worker pumps this object; it creates no additional thread.
// Installation and all concrete native tasks remain on this same worker.
class LinuxEditorHelperOwner {
public:
    LinuxEditorHelperOwner(EditorHelperClient&,std::shared_ptr<platform::LinuxInstallation>,RecoveryAdmissionFactory={});
    ~LinuxEditorHelperOwner();
    LinuxEditorHelperOwner(const LinuxEditorHelperOwner&)=delete;
    LinuxEditorHelperOwner& operator=(const LinuxEditorHelperOwner&)=delete;
    bool poll(); // True only after channel closure and native work has drained.
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
