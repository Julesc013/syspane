#pragma once
#include <functional>
#include <string>

namespace syspane::platform {
enum class PreservePhase { before_read, reading, after_read, before_create, writing, verifying, before_publish };
enum class PreserveCheck { permit, deny, cancel };
using PreserveGuard = std::function<PreserveCheck(PreservePhase)>;
struct PreserveResult {
    std::string outcome = "io_error";
    bool partial = false;
};
// Opaque private copy only. Guard must recheck current authority; absent/throwing guards deny.
// No cleanup deletes a partial or source; paths' existing parents are caller-selected and trusted.
PreserveResult preserve_file(const std::string& source, const std::string& destination, const PreserveGuard& guard);
}
