#include "theme_resources.hpp"
namespace syspane::configuration {
namespace {void need(bool b,const char* code){if(!b)throw protocol::Error(code);}}
ResourceSnapshot replace_theme_resources(const ResourceSet& source,const Authored& candidate,
    const std::optional<AuthoredTheme>& override,const Policy& policy,const std::set<std::string>& capabilities){
    authorize_resources(source,policy,capabilities);
    need(capabilities.count("configuration.theme-overrides")&&!policy.denied_capabilities.count("configuration.theme-overrides"),"policy.denied");
    Json selection={{"schema_version","0.2.0"},{"package",source.selection().at("package")},{"preset",source.selection().at("preset")},{"theme_override",nullptr}};
    std::vector<ContentPackage> packages;
    for(const auto& package:source.base_packages())packages.push_back(*package);
    if(override){
        const auto checked=validate_authored_theme(override->package);
        need(checked.theme.dump()==override->theme.dump()&&checked.package_pin==override->package_pin&&checked.theme_pin==override->theme_pin,"theme.artifact");
        bool present=false;
        for(const auto& package:packages){const auto manifest=parse_content_json(package.manifest,65536);
            if(manifest.at("package_id")==checked.package_pin.at("id")&&manifest.at("version")==checked.package_pin.at("version")){
                need(package.manifest==checked.package.manifest&&package.assets==checked.package.assets,"content.duplicate_package");present=true;}}
        if(!present){need(packages.size()<64,"content.capacity");packages.push_back(checked.package);}
        selection["theme_override"]={{"package",checked.package_pin},{"theme",checked.theme_pin}};
    }
    auto result=ContentCatalog(std::move(packages)).theme_resources(selection,candidate);
    authorize_resources(*result,policy,capabilities);return result;
}
}
