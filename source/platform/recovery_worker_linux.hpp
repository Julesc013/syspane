#pragma once
#include "wire.hpp"
namespace syspane::platform {
// Hooks are used only by the separately built native fault probe.
int run_recovery_worker(std::uint64_t parent,
    const std::function<void(const char*)>& transition={},
    const std::function<void(protocol::Json&)>& outgoing={});
}
