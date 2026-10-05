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
const std::string failure_one = "{\"sequence\":\"1\",\"elapsed_ms\":\"100\",\"role\":\"collector\",\"reason\":\"producer_expired\",\"stop_confirmed\":false}\n";
const std::string failure_two = "{\"sequence\":\"2\",\"elapsed_ms\":\"200\",\"role\":\"desktop\",\"reason\":\"render_stalled\",\"stop_confirmed\":true}\n";
void failure_codec() {
    const std::string header = "SYSPANE-FAILURES 0.1\n";
    const auto valid = diag::decode_failures(header+failure_one+failure_two);
    require(valid.status == "complete" && valid.records.size() == 2 && valid.records[0] == Json::parse(failure_one) && valid.records[1] == Json::parse(failure_two));
    require(diag::decode_failures(header).status == "empty");
    require(Json::parse(diag::failure_line(1, 100, "collector", "producer_expired", false)) == Json::parse(failure_one));
    for (const auto& mutation : std::vector<std::function<void(Json&)>>{
        [](Json& p) { p["sequence"] = "0"; }, [](Json& p) { p["sequence"] = "2"; },
        [](Json& p) { p["sequence"] = "01"; }, [](Json& p) { p["elapsed_ms"] = "18446744073709551616"; },
        [](Json& p) { p["elapsed_ms"] = "-1"; }, [](Json& p) { p["elapsed_ms"] = 100; },
        [](Json& p) { p["role"] = "maintenance"; }, [](Json& p) { p["reason"] = "private arbitrary text"; },
        [](Json& p) { p["stop_confirmed"] = 1; }, [](Json& p) { p["path"] = "private"; },
        [](Json& p) { p.erase("reason"); }
    }) {
        auto value = Json::parse(failure_one); mutation(value);
        const auto bad = diag::decode_failures(header+value.dump()+"\n");
        require(bad.status == "invalid" && bad.records.empty());
    }
    auto backward = Json::parse(failure_two); backward["elapsed_ms"] = "99";
    require(diag::decode_failures(header+failure_one+backward.dump()+"\n").status == "invalid");
    auto duplicate = failure_one; duplicate.insert(1, "\"sequence\":\"1\",");
    require(diag::decode_failures(header+duplicate).status == "invalid");
    require(diag::decode_failures("\xef\xbb\xbf"+header).status == "invalid");
    require(diag::decode_failures(header+failure_one+std::string(512, 'x')).status == "invalid");
    require(diag::decode_failures(header+std::string(8193, 'x')).status == "invalid");
    auto sixteen = header;
    for (unsigned i = 1; i <= 16; ++i) {
        auto row = Json::parse(failure_one); row["sequence"] = std::to_string(i); row["elapsed_ms"] = "18446744073709551615";
        sixteen += row.dump()+"\n";
    }
    require(diag::decode_failures(sixteen).records.size() == 16);
    require(diag::decode_failures(sixteen+"x").status == "invalid");
    auto full_line = failure_one;
    full_line.insert(full_line.size()-1, 512-full_line.size(), ' ');
    require(full_line.size() == 512 && diag::decode_failures(header+full_line).status == "complete");
    full_line.insert(full_line.size()-1, " ");
    require(diag::decode_failures(header+full_line).status == "invalid");
}
void failure_interrupt() {
    const std::string header = "SYSPANE-FAILURES 0.1\n";
    const auto bytes = header+failure_one+failure_two;
    for (std::size_t i = 0; i <= bytes.size(); ++i) {
        const auto value = diag::decode_failures(std::string_view(bytes).substr(0, i));
        const auto completed = i >= bytes.size() ? 2u : i >= header.size()+failure_one.size() ? 1u : 0u;
        require(value.records.size() == completed);
        const auto status = i == header.size() ? "empty" : i == bytes.size() || i == header.size()+failure_one.size() ? "complete" : "incomplete";
        require(value.status == status);
    }
    const auto broken = diag::decode_failures(header+failure_one+"{bad}\n");
    require(broken.status == "invalid" && broken.records.empty());
    require(diag::decode_failures(header+failure_one+"\n").status == "invalid");
}
void failure_policy() {
    unsigned reads = 0;
    diag::FailureReader loader = [&] { ++reads; return diag::decode_failures(std::string(diag::failure_header)+failure_one); };
    cfg::Policy p;
    auto value = diag::report(p, "linux-x64-gcc13", loader);
    require(reads == 0 && value->at("failure_history") == Json({{"status", "restricted"}, {"trust", "unverified_local_metadata"}, {"live_health", false}, {"records", Json::array()}}));
    require(diag::inspector_text(p, "linux-x64-gcc13", loader).find("producer_expired") == std::string::npos && reads == 0);
    p.available = true;
    p.disclosure[{"diagnostic", "export"}] = {"public", "operational"};
    value = diag::report(p, "linux-x64-gcc13", loader);
    require(reads == 1 && value->at("failure_history")["records"][0] == Json::parse(failure_one) && !value->at("failure_history")["live_health"].get<bool>());
    p.disclosure[{"diagnostic", "inspector"}] = {"public", "operational"};
    require(diag::inspector_text(p, "linux-x64-gcc13", loader).find("producer_expired") == std::string::npos && reads == 1);
    p.disclosure[{"diagnostic", "accessibility"}] = {"public", "operational"};
    const auto text = diag::inspector_text(p, "linux-x64-gcc13", loader);
    require(reads == 2 && text.find("collector/producer_expired") != std::string::npos && text.find("not live health") != std::string::npos);
    p.disclosure[{"diagnostic", "accessibility"}] = {"public"};
    require(diag::inspector_text(p, "linux-x64-gcc13", loader).find("producer_expired") == std::string::npos && reads == 2);
    p.disclosure[{"diagnostic", "export"}] = {"public"};
    require(diag::report(p, "linux-x64-gcc13", loader)->at("failure_history")["status"] == "restricted" && reads == 2);
    p.denied_capabilities.insert("projection.export");
    require(!diag::report(p, "linux-x64-gcc13", loader) && reads == 2);
}
int main(int argc, char** argv) {
    try {
        if (argc != 2) return 2;
        const std::string name = argv[1];
        if (name == "DIAG-POLICY") policy_cases();
        else if (name == "DIAG-PROJECTION") projection_cases();
        else if (name == "FAILURE-CODEC") failure_codec();
        else if (name == "FAILURE-INTERRUPT") failure_interrupt();
        else if (name == "FAILURE-PROJECTION") failure_policy();
        else return 2;
        std::cout << name << ": pass\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
