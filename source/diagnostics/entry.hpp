#pragma once
#include "policy.hpp"
#include "failure_history.hpp"
#include <optional>
#include <string>

namespace syspane::diagnostics {
bool preservation_permitted(const configuration::Policy& policy, std::uint64_t revision, bool inspector);
std::optional<protocol::Json> report(const configuration::Policy& policy, const std::string& profile, const FailureReader& failures = {});
std::string inspector_text(const configuration::Policy& policy, const std::string& profile, const FailureReader& failures = {});
}
