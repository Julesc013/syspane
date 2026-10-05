#include "policy.hpp"
#include "settings_descriptors.hpp"
#include <algorithm>
#include <cmath>

namespace syspane::configuration {
namespace {
bool granted(const Authority& authority) {
    const std::set<std::string> roles = {"desktop", "console", "collector", "saver", "preview", "saver_settings", "diagnostic", "maintenance"};
    return authority.authenticated && roles.count(authority.role) && authority.role_grants.count(authority.role);
}
bool valid_value(const Descriptor& descriptor, const Json& value) {
    if (descriptor.kind == Kind::boolean) return value.is_boolean();
    if (descriptor.kind == Kind::identifier)
        return value.is_string() && protocol::identifier(value.get_ref<const std::string&>());
    if (value.is_number_float()) {
        const auto n = value.get<double>();
        return std::isfinite(n) && std::floor(n) == n && n >= static_cast<double>(descriptor.minimum) &&
               n <= static_cast<double>(descriptor.maximum);
    }
    if (!value.is_number_integer() || (!value.is_number_unsigned() && value.get<std::int64_t>() < 0)) return false;
    const auto n = value.get<std::uint64_t>();
    return n >= descriptor.minimum && n <= descriptor.maximum;
}
std::optional<std::uint64_t> revision(const Json& value) {
    return value.is_string() ? protocol::decimal(value.get_ref<const std::string&>()) : std::nullopt;
}
}
Decision preview(const Json& command, const Authority& authority, const Policy& policy, std::uint64_t current_revision) {
    if (!protocol::members(command, {"schema_version", "request_id", "expected_revision", "policy_generation", "intent", "operations"}) ||
        command["schema_version"] != "0.2.0" || !command["request_id"].is_string() ||
        !protocol::identifier(command["request_id"].get_ref<const std::string&>()) ||
        (command["intent"] != "preview" && command["intent"] != "commit")) return {"invalid", "command.shape"};
    const auto expected = revision(command["expected_revision"]), generation = revision(command["policy_generation"]);
    if (!expected || !generation) return {"invalid", "command.revision"};
    const auto& operations = command["operations"];
    if (!operations.is_array() || operations.empty() || operations.size() > 128) return {"invalid", "command.operations"};
    bool unsupported = false;
    std::set<std::string> paths;
    for (const auto& operation : operations) {
        if (!operation.is_object() || !operation.contains("op") || !operation["op"].is_string()) return {"invalid", "command.operation"};
        if (operation["op"] != "settings.set") { unsupported = true; continue; }
        if (!protocol::members(operation, {"op", "path", "value"}) || !operation["path"].is_string()) return {"invalid", "command.operation"};
        const auto path = operation["path"].get<std::string>();
        if (!paths.insert(path).second) return {"invalid", "command.duplicate_path"};
        const auto descriptor = std::find_if(descriptors.begin(), descriptors.end(), [&](const Descriptor& item) { return path == item.path; });
        if (descriptor == descriptors.end() || !valid_value(*descriptor, operation["value"])) return {"invalid", "command.setting"};
    }
    const std::set<std::string> writers = {"console", "desktop", "saver_settings"};
    if (!granted(authority) || !writers.count(authority.role) || !policy.available) return {"denied", "policy.denied"};
    if (*generation != policy.revision) return {"conflict", "policy.changed"};
    if (*expected != current_revision) return {"conflict", "revision.changed"};
    if (unsupported || command["intent"] == "commit") return {"invalid", "feature.unsupported"};
    if (policy.denied_capabilities.count("settings.preview") || policy.denied_capabilities.count("settings.set")) return {"denied", "policy.denied"};
    for (const auto& operation : operations) {
        const auto it = policy.forced.find(operation["path"].get<std::string>());
        if (it != policy.forced.end() && it->second != operation["value"]) return {"denied", "policy.forced"};
    }
    return {"preview", {}};
}
Json result(const Decision& decision, const std::string& request_id, const std::string& epoch, std::uint64_t current_revision) {
    const std::set<std::string> outcomes = {"preview", "conflict", "denied", "invalid", "busy", "cancelled", "unknown"};
    if (!protocol::identifier(request_id) || !protocol::identifier(epoch) || !outcomes.count(decision.outcome) ||
        (!decision.code.empty() && !protocol::identifier(decision.code))) throw protocol::Error("result.invalid");
    Json reply = {{"schema_version", "0.1.0"}, {"request_id", request_id}, {"producer_epoch", epoch},
        {"outcome", decision.outcome}, {"revision", std::to_string(current_revision)}, {"stored", false},
        {"durable", false}, {"visible", false}, {"activation", Json::array()}, {"error", nullptr}};
    if (decision.outcome == "unknown") {
        reply["revision"] = reply["stored"] = reply["durable"] = reply["visible"] = nullptr;
    }
    if (!decision.code.empty()) reply["error"] = {{"code", decision.code},
        {"message", "Request did not change stored configuration."}, {"retryable", decision.outcome == "busy"}};
    return reply;
}
bool permits(const Authority& authority, const Policy& policy, const std::string& channel, const std::string& classification) {
    const std::set<std::string> channels = {"desktop", "inspector", "saver", "preview", "accessibility", "tooltip",
        "clipboard", "history", "logs", "support_bundle", "extension", "export"};
    if (!granted(authority) || !channels.count(channel) || classification == "secret") return false;
    if (policy.denied_capabilities.count("projection." + channel)) return false;
    const auto effective = classification == "public" || classification == "operational" ? classification : "sensitive";
    if (!policy.available) return effective == "public";
    const auto rule = policy.disclosure.find({authority.role, channel});
    if (rule == policy.disclosure.end()) return effective == "public";
    return rule->second.count(effective) != 0;
}
} // namespace syspane::configuration
