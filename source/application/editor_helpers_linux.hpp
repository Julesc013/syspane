#pragma once
#include "image_job.hpp"
#include "recovery_queue_linux.hpp"
#include "installation_linux.hpp"

namespace syspane::application {
struct EditorHelperStatus {
    bool attached=false,closing=false,stopped=false;
    std::size_t image_handles=0,recovery_handles=0,retained_bytes=0;
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
    EditorHelperStatus status()const;
    void close();
private:
    friend class LinuxEditorHelperOwner;
    std::shared_ptr<EditorHelperChannel> channel_;
    std::shared_ptr<const platform::RecoveryFactory> recovery_;
};
// Existing host native worker pumps this object; it creates no additional thread.
// Installation and all concrete native tasks remain on this same worker.
class LinuxEditorHelperOwner {
public:
    LinuxEditorHelperOwner(EditorHelperClient&,std::shared_ptr<platform::LinuxInstallation>);
    ~LinuxEditorHelperOwner();
    LinuxEditorHelperOwner(const LinuxEditorHelperOwner&)=delete;
    LinuxEditorHelperOwner& operator=(const LinuxEditorHelperOwner&)=delete;
    bool poll(); // True only after channel closure and native work has drained.
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
