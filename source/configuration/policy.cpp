#include "policy.hpp"
#include "settings_descriptors.hpp"
#include <algorithm>
#include <cmath>
#include <regex>

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
Policy decode_policy(std::string_view bytes) {
    if (bytes.empty() || bytes.size() > 65536) throw protocol::Error("policy.size");
    const auto first = bytes.find_first_not_of(" \t\r\n"), last = bytes.find_last_not_of(" \t\r\n");
    if (first == std::string_view::npos) throw protocol::Error("policy.shape");
    auto value = protocol::parse(bytes.substr(first, last - first + 1));
    if (value.is_object() && value.contains("extensions")) {
        const auto& extensions = value["extensions"];
        if (!extensions.is_object() || extensions.size() > 64) throw protocol::Error("policy.extensions");
        for (auto it = extensions.begin(); it != extensions.end(); ++it)
            if (!std::regex_match(it.key(), std::regex("[a-z][a-z0-9_.-]{0,127}"))) throw protocol::Error("policy.extensions");
        value.erase("extensions");
    }
    if (!protocol::members(value, {"schema_version", "policy_id", "revision", "scope", "forced_settings",
            "denied_capabilities", "disclosure", "retained_data_on_revocation"}) ||
        value["schema_version"] != "0.1.0" || !value["policy_id"].is_string() ||
        !protocol::identifier(value["policy_id"].get_ref<const std::string&>()) ||
        (value["scope"] != "machine" && value["scope"] != "organization") ||
        (value["retained_data_on_revocation"] != "restrict" && value["retained_data_on_revocation"] != "purge_with_authority"))
        throw protocol::Error("policy.shape");
    const auto generation = revision(value["revision"]);
    if (!generation) throw protocol::Error("policy.revision");
    Policy result;
    result.revision = *generation;
    const auto& forced = value["forced_settings"];
    if (!forced.is_array() || forced.size() > 64) throw protocol::Error("policy.settings");
    for (const auto& row : forced) {
        if (!protocol::members(row, {"path", "value"}) || !row["path"].is_string()) throw protocol::Error("policy.setting");
        const auto path = row["path"].get<std::string>();
        const auto descriptor = std::find_if(descriptors.begin(), descriptors.end(), [&](const Descriptor& item) { return path == item.path; });
        if (descriptor == descriptors.end() || !valid_value(*descriptor, row["value"]) ||
            !result.forced.emplace(path, row["value"]).second) throw protocol::Error("policy.setting");
    }
    const auto& denied = value["denied_capabilities"];
    if (!denied.is_array() || denied.size() > 128) throw protocol::Error("policy.capabilities");
    for (const auto& item : denied)
        if (!item.is_string() || !protocol::identifier(item.get_ref<const std::string&>()) ||
            !result.denied_capabilities.insert(item.get<std::string>()).second) throw protocol::Error("policy.capability");
    const std::set<std::string> roles = {"desktop", "console", "collector", "saver", "preview", "saver_settings", "diagnostic", "maintenance"};
    const std::set<std::string> channels = {"desktop", "inspector", "saver", "preview", "accessibility", "tooltip", "clipboard", "history", "logs", "support_bundle", "extension", "export"};
    const std::set<std::string> classes = {"public", "operational", "sensitive"};
    const auto& disclosure = value["disclosure"];
    if (!disclosure.is_array() || disclosure.size() > 128) throw protocol::Error("policy.disclosure");
    for (const auto& row : disclosure) {
        if (!protocol::members(row, {"role", "channel", "allow_classifications"}) || !row["role"].is_string() || !row["channel"].is_string() ||
            !roles.count(row["role"].get<std::string>()) || !channels.count(row["channel"].get<std::string>())) throw protocol::Error("policy.disclosure");
        const auto& allowed = row["allow_classifications"];
        if (!allowed.is_array() || allowed.size() > 3) throw protocol::Error("policy.classification");
        std::set<std::string> values;
        for (const auto& item : allowed)
            if (!item.is_string() || !classes.count(item.get<std::string>()) || !values.insert(item.get<std::string>()).second)
                throw protocol::Error("policy.classification");
        if (!result.disclosure.emplace(std::make_pair(row["role"].get<std::string>(), row["channel"].get<std::string>()), values).second)
            throw protocol::Error("policy.duplicate_disclosure");
    }
    return result;
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
        {"message", decision.outcome == "unknown" ? "Request outcome requires reconciliation." : "Request did not change stored configuration."},
        {"retryable", decision.outcome == "busy"}};
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
