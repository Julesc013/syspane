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
std::optional<protocol::Json> report(const configuration::Policy& policy, const std::string& profile, const FailureReader& failures) {
    if (!configuration::permits(authority, policy, "export", "public")) return {};
    auto value = facts(policy, profile);
    if (failures) value["failure_history"] = failure_projection(configuration::permits(authority, policy, "export", "operational") ?
        failures() : FailureHistory{"restricted", {}});
    return value;
}
std::string inspector_text(const configuration::Policy& policy, const std::string& profile, const FailureReader& failures) {
    if (!configuration::permits(authority, policy, "inspector", "public") ||
        !configuration::permits(authority, policy, "accessibility", "public")) return "Diagnostic details are restricted by policy.";
    const auto value = facts(policy, profile);
    auto text = "SysPane diagnostic 0.0.1\nDevelopment profile: " + profile +
        "\nMandatory policy: " + value["policy_state"].get<std::string>() +
        "\nRecovery controls are not implemented.\nApplication configuration is not opened.";
    if (failures) {
        const auto history = failure_projection(configuration::permits(authority, policy, "inspector", "operational") &&
            configuration::permits(authority, policy, "accessibility", "operational") ? failures() : FailureHistory{"restricted", {}});
        text += "\nRecorded failures (unverified, not live health): " + history["status"].get<std::string>();
        const auto& records = history["records"];
        if (!records.empty()) {
            const auto& last = records.back();
            text += "\n" + std::to_string(records.size()) + " records; last: " + last["role"].get<std::string>() + "/" + last["reason"].get<std::string>() +
                "\nElapsed in recorded run: " + last["elapsed_ms"].get<std::string>() + " ms; stop confirmed then: " +
                (last["stop_confirmed"].get<bool>() ? "yes" : "no");
        }
    }
    return text;
}
}
