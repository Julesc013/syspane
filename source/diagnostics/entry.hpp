#pragma once
#include "policy.hpp"
#include <optional>
#include <string>

namespace syspane::diagnostics {
std::optional<protocol::Json> report(const configuration::Policy& policy, const std::string& profile);
std::string inspector_text(const configuration::Policy& policy, const std::string& profile);
}
