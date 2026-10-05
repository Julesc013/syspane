#include "entry.hpp"
#include <functional>
#include <iostream>
#include <limits>

using syspane::protocol::Json;
namespace cfg = syspane::configuration;
namespace diag = syspane::diagnostics;
void require(bool condition) { if (!condition) throw std::runtime_error("fixed diagnostic oracle failed"); }
Json policy() {
    return {{"schema_version", "0.1.0"}, {"policy_id", "policy:fixture"}, {"revision", "0"}, {"scope", "machine"},
        {"forced_settings", Json::array()}, {"denied_capabilities", Json::array()}, {"disclosure", Json::array()}, {"retained_data_on_revocation", "restrict"}};
}
void rejected(const std::string& bytes) {
    try { (void)cfg::decode_policy(bytes); } catch (const syspane::protocol::Error&) { return; }
    throw std::runtime_error("invalid policy accepted");
}
void policy_cases() {
    auto good = policy();
    good["forced_settings"] = {{{"path", "privacy.remote_probes"}, {"value", false}}};
    auto decoded = cfg::decode_policy(" \r\n" + good.dump() + "\r\n");
    require(!decoded.available && decoded.revision == 0 && decoded.forced.at("privacy.remote_probes") == false);
    good["revision"] = "18446744073709551615";
    require(cfg::decode_policy(good.dump()).revision == std::numeric_limits<std::uint64_t>::max());
    for (const auto& mutation : std::vector<std::function<void(Json&)>>{
        [](Json& p) { p["revision"] = "18446744073709551616"; },
        [](Json& p) { p["revision"] = "01"; },
        [](Json& p) { p["available"] = true; },
        [](Json& p) { p["schema_version"] = "1.0.0"; },
        [](Json& p) { p["scope"] = "user"; },
        [](Json& p) { p["policy_id"] = "invalid id"; },
        [](Json& p) { p["forced_settings"].push_back(p["forced_settings"][0]); },
        [](Json& p) { p["forced_settings"][0]["value"] = 1; },
        [](Json& p) { p["forced_settings"][0]["path"] = "invented.setting"; },
        [](Json& p) { p["denied_capabilities"] = {"export", "export"}; },
        [](Json& p) { p["denied_capabilities"] = {"bad value"}; },
        [](Json& p) { p["disclosure"] = {{{"role", "invented"}, {"channel", "export"}, {"allow_classifications", {"public"}}}}; },
        [](Json& p) { p["disclosure"] = {{{"role", "diagnostic"}, {"channel", "invented"}, {"allow_classifications", {"public"}}}}; },
        [](Json& p) { p["disclosure"] = {{{"role", "diagnostic"}, {"channel", "export"}, {"allow_classifications", {"secret"}}}}; },
        [](Json& p) { p["disclosure"] = {{{"role", "diagnostic"}, {"channel", "export"}, {"allow_classifications", {"public", "public"}}}}; },
        [](Json& p) { p["disclosure"] = {{{"role", "diagnostic"}, {"channel", "export"}, {"allow_classifications", {"public"}}}}; p["disclosure"].push_back(p["disclosure"][0]); },
        [](Json& p) { p["extensions"] = {{"INVALID", 1}}; },
        [](Json& p) { p["retained_data_on_revocation"] = "ignore"; }
    }) { auto invalid = good; mutation(invalid); rejected(invalid.dump()); }
    rejected("\xef\xbb\xbf" + good.dump());
    rejected("{\"revision\":\"0\",\"revision\":\"1\"}");
    rejected(std::string(65537, ' '));
    rejected(std::string(33, '[') + "0" + std::string(33, ']'));
    auto many = policy();
    many["extensions"] = {{"nodes", std::vector<int>(17000, 0)}};
    rejected(many.dump());
    auto number = policy();
    number["forced_settings"] = {{{"path", "sampling.resources_ms"}, {"value", 1000.0}}};
    // The registry ID below is selected independently from the contract registry.
    require(cfg::decode_policy(number.dump()).forced.at("sampling.resources_ms") == 1000);
    for (const auto& invalid : {Json(1000.5), Json(true), Json(0), Json(1000000000)}) {
        number["forced_settings"][0]["value"] = invalid;
        rejected(number.dump());
    }
}
void projection_cases() {
    cfg::Policy unavailable;
    const auto report = diag::report(unavailable, "windows-x64-gcc15");
    require(report && report->size() == 7 && (*report)["policy_state"] == "unavailable" && (*report)["recovery_controls"] == "not_implemented");
    require(!cfg::permits({true, "diagnostic", {"diagnostic"}}, unavailable, "export", "sensitive"));
    auto trusted = cfg::decode_policy(policy().dump());
    trusted.available = true; // Typed fixture, not native-source evidence.
    require(diag::report(trusted, "linux-x64-gcc13")->at("policy_state") == "available");
    require(diag::inspector_text(trusted, "linux-x64-gcc13").find("linux-x64-gcc13") != std::string::npos);
    trusted.denied_capabilities.insert("projection.export");
    require(!diag::report(trusted, "linux-x64-gcc13"));
    trusted.denied_capabilities.insert("projection.inspector");
    require(diag::inspector_text(trusted, "linux-x64-gcc13") == "Diagnostic details are restricted by policy.");
    trusted.denied_capabilities.erase("projection.inspector");
    trusted.disclosure[{"diagnostic", "accessibility"}] = {};
    require(diag::inspector_text(trusted, "linux-x64-gcc13") == "Diagnostic details are restricted by policy.");
    trusted.disclosure[{"diagnostic", "accessibility"}] = {"public"};
    require(diag::inspector_text(trusted, "linux-x64-gcc13").find("linux-x64-gcc13") != std::string::npos);
}
int main(int argc, char** argv) {
    try {
        if (argc != 2) return 2;
        const std::string name = argv[1];
        if (name == "DIAG-POLICY") policy_cases();
        else if (name == "DIAG-PROJECTION") projection_cases();
        else return 2;
        std::cout << name << ": pass\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
