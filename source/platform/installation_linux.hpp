#pragma once
#include <cstddef>
#include <memory>
#include <string>

namespace syspane::platform {
struct HelperExpectation {
    std::string record_sha256,helper_sha256;
    std::size_t helper_bytes;
};
// Expectation is compiled into the trusted consumer, never read from its adjacent
// manifest, environment, preferences or command arguments. Serialized worker only.
class LinuxInstallation {
public:
    explicit LinuxInstallation(const HelperExpectation&);
    ~LinuxInstallation();
    LinuxInstallation(const LinuxInstallation&)=delete;
    LinuxInstallation& operator=(const LinuxInstallation&)=delete;
    // Revalidates the current installation. Descriptor is borrowed and immutable;
    // retain this owner through launch. No pathname is reopened for execution.
    int verified_helper()const;
    const std::string& root()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
