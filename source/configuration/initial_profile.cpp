#include "initial_profile.hpp"
#include "initial_profile_data.hpp"
#include "settings_descriptors.hpp"
#include "digest.hpp"
#include <algorithm>

namespace syspane::configuration {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
void setting(Json& settings,const std::string& name,const Json& value){
    const auto dot=name.find('.');need(dot!=std::string::npos&&name.find('.',dot+1)==std::string::npos,"initial.setting");
    settings[name.substr(0,dot)][name.substr(dot+1)]=value;
}
struct Pins {Json package,document;};
Pins package(std::vector<ContentPackage>& packages,const char* kind,const Json& document,Json dependencies=Json::array()){
    const std::string filename=std::string(kind)+".json",id=std::string("package:syspane-default-")+kind,bytes=document.dump();
    Json manifest={{"schema_version","0.1.0"},{"package_id",id},{"version","0.1.0"},{"kind",kind},{"license","LicenseRef-SysPane-Pending"},
        {"dependencies",std::move(dependencies)},{"assets",Json::array({{{"path",filename},{"media_type","application/json"},{"sha256",sha256(bytes)},{"bytes",bytes.size()}}})},
        {"total_unpacked_bytes",bytes.size()},{"required_capabilities",std::string(kind)=="scene"?Json::array({"scene.content"}):Json::array()},{"optional_capabilities",Json::array()}};
    const auto raw=manifest.dump();packages.push_back({raw,{{filename,bytes}}});
    return {{{"id",id},{"version","0.1.0"},{"sha256",sha256(raw)}},{{"id",document[std::string(kind)+"_id"]},{"version","0.1.0"},{"sha256",sha256(bytes)}}};
}
}
Committed initial_profile(const Policy& policy,const std::set<std::string>& capabilities){
    need(policy.available,"policy.denied");
    for(const char* operation:{"profile.open","profile.create","settings.commit","scene.replace","preset.apply"})
        need(!policy.denied_capabilities.count(operation),"policy.denied");
    const auto defaults=protocol::parse(initial_profile_json);
    Authored authored{{{"schema_version","0.1.0"},{"revision","0"}},defaults.at("scene")};
    for(const auto& descriptor:descriptors)setting(authored.settings,descriptor.path,protocol::parse(descriptor.default_json));
    for(const auto& forced:policy.forced){
        need(std::any_of(descriptors.begin(),descriptors.end(),[&](const auto& d){return forced.first==d.path;}),"initial.setting");
        setting(authored.settings,forced.first,forced.second);
    }
    validate_authored(authored);
    std::vector<ContentPackage> packages;
    const auto theme=package(packages,"theme",defaults.at("theme"));const auto scene=package(packages,"scene",defaults.at("scene"));
    const Json preset={{"schema_version","0.1.0"},{"preset_id","preset:default"},{"version","0.1.0"},{"parent",nullptr},{"scene",scene.document},
        {"theme",nullptr},{"settings",Json::array()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    const auto selected=package(packages,"preset",preset,Json::array({theme.package,scene.package}));
    auto resources=ContentCatalog(std::move(packages)).resources({{"package",selected.package},{"preset",selected.document}},authored);
    authorize_resources(*resources,policy,capabilities);return {std::move(authored),std::nullopt,std::move(resources)};
}
}
