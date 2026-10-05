#pragma once
#include "wire.hpp"
#include <map>
#include <set>
#include <string>

namespace syspane::configuration {
using protocol::Json;
// Construct only from the native adapter, never from a client document.
struct Authority {
    bool authenticated = false;
    std::string role;
    std::set<std::string> role_grants;
};
// Protected policy adapter owns this immutable snapshot for a check's lifetime.
struct Policy {
    bool available = false;
    std::uint64_t revision = 0;
    std::map<std::string, Json> forced;
    std::set<std::string> denied_capabilities;
    std::map<std::pair<std::string, std::string>, std::set<std::string>> disclosure;
};
struct Decision {
    std::string outcome, code;
};
Decision preview(const Json& command, const Authority& authority, const Policy& policy,
                 std::uint64_t current_revision);
Json result(const Decision& decision, const std::string& request_id,
            const std::string& epoch, std::uint64_t current_revision);
bool permits(const Authority& authority, const Policy& policy, const std::string& channel,
             const std::string& classification);
} // namespace syspane::configuration
