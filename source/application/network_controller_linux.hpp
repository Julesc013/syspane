#pragma once
#include "policy.hpp"
#include <functional>

namespace syspane::application {
// Trusted native composition; production uses only the protected machine policy.
int run_network_controller(std::uint64_t parent,std::function<configuration::Policy()> policy={},
                           std::function<void()> before_read={});
}
