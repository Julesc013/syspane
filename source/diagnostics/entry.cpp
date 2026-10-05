#include "entry.hpp"

namespace syspane::diagnostics {
namespace {
const configuration::Authority authority{true, "diagnostic", {"diagnostic"}};
protocol::Json facts(const configuration::Policy& policy, const std::string& profile) {
    if (profile != "windows-x64-gcc15" && profile != "linux-x64-gcc13") throw protocol::Error("diagnostic.profile");
    return {{"schema_version", "0.1.0"}, {"product", "SysPane"}, {"component", "diagnostic"},
        {"build_version", "0.0.1"}, {"profile", profile}, {"policy_state", policy.available ? "available" : "unavailable"},
        {"recovery_controls", "not_implemented"}};
}
}
std::optional<protocol::Json> report(const configuration::Policy& policy, const std::string& profile) {
    if (!configuration::permits(authority, policy, "export", "public")) return {};
    return facts(policy, profile);
}
std::string inspector_text(const configuration::Policy& policy, const std::string& profile) {
    if (!configuration::permits(authority, policy, "inspector", "public") ||
        !configuration::permits(authority, policy, "accessibility", "public")) return "Diagnostic details are restricted by policy.";
    const auto value = facts(policy, profile);
    return "SysPane diagnostic 0.0.1\nDevelopment profile: " + profile +
        "\nMandatory policy: " + value["policy_state"].get<std::string>() +
        "\nRecovery controls are not implemented.\nApplication configuration is not opened.";
}
}
