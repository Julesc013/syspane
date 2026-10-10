#pragma once
#include "policy.hpp"
#include "network_watch.hpp"
#include <functional>

namespace syspane::application {
// Trusted native composition; production uses only the protected machine policy.
// The optional acquisition callable is supplied only by compiled test composition.
int run_network_controller(std::uint64_t parent,std::function<configuration::Policy()> policy={},
                           std::function<void()> before_read={},
                           std::function<platform::WatchedNetworkResult(const platform::NetworkRequest&)> read={});
}
