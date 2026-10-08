#pragma once
#include "profile_store_linux.hpp"
#include <cstdint>
namespace syspane::application {
// Private child-process entry. May exit the process without stack unwinding to
// stop uncooperative native work. Never call in the inspector/UI process.
// Injection is trusted, thread-safe, in-process test composition only.
int run_profile_controller(std::uint64_t parent,platform::LinuxProfileStore::PolicySource={},
                           platform::LinuxProfileOwner::Transition={});
}
