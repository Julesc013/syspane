#pragma once
#include <memory>
#include <string>

namespace syspane::platform {
// Serialized off-GUI owner of one fresh directory under an explicitly admitted
// native runtime base. Destruction closes descriptors, never removes paths.
class LinuxRuntimeDirectory {
public:
    explicit LinuxRuntimeDirectory(std::string base);
    ~LinuxRuntimeDirectory();
    LinuxRuntimeDirectory(const LinuxRuntimeDirectory&)=delete;
    LinuxRuntimeDirectory& operator=(const LinuxRuntimeDirectory&)=delete;
    std::string path()const;
    // Destroy the closed supervisor first: its independent flock blocks removal.
    // Busy is retryable; observed substitution or unexpected contents are not.
    void cleanup();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
