#pragma once
#include <cstddef>
#include <array>
#include <memory>
#include <string>

namespace syspane::platform {
struct HelperExpectation {
    std::string record_sha256,helper_sha256;
    std::size_t helper_bytes;
};
enum class HelperKind {configuration,image,recovery};
struct HelperImageExpectation {std::string sha256;std::size_t bytes;};
struct HelperBundleExpectation {
    std::string record_sha256;
    std::array<HelperImageExpectation,3> helpers; // Configuration, image, recovery.
};
// Expectation is compiled into the trusted consumer, never read from its adjacent
// manifest, environment, preferences or command arguments. Serialized worker only.
class LinuxInstallation {
public:
    explicit LinuxInstallation(const HelperExpectation&);
    explicit LinuxInstallation(const HelperBundleExpectation&);
    ~LinuxInstallation();
    LinuxInstallation(const LinuxInstallation&)=delete;
    LinuxInstallation& operator=(const LinuxInstallation&)=delete;
    // Revalidates the current installation. Descriptor is borrowed and immutable;
    // retain this owner through launch. No pathname is reopened for execution.
    int verified_helper()const;
    int verified_helper(HelperKind)const;
    const std::string& root()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
