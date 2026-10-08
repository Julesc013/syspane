#include "authored_theme.hpp"
#include "digest.hpp"
namespace syspane::configuration {
namespace {
void need(bool b,const char* why){if(!b)throw protocol::Error(why);}
AuthoredTheme artifact(const Json& theme,const std::string& license){
    auto body=theme;body.erase("theme_id");
    const Json seed={{"license",license},{"theme",std::move(body)}};const auto identity=sha256("SysPane authored theme 1\n"+seed.dump()+"\n");
    AuthoredTheme out;out.theme=theme;out.theme["theme_id"]="theme:authored:"+identity;
    const auto asset=out.theme.dump()+"\n",asset_hash=sha256(asset),package_id="package:authored-theme:"+identity;
    Json manifest={{"schema_version","0.1.0"},{"package_id",package_id},{"version","0.1.0"},{"kind","theme"},{"license",license},{"dependencies",Json::array()},
        {"assets",Json::array({{{"path","theme.json"},{"media_type","application/json"},{"sha256",asset_hash},{"bytes",asset.size()}}})},
        {"total_unpacked_bytes",asset.size()},{"required_capabilities",Json::array({"theme.typography"})},{"optional_capabilities",Json::array()}};
    out.package={manifest.dump()+"\n",{{"theme.json",asset}}};out.package_pin={{"id",package_id},{"version","0.1.0"},{"sha256",sha256(out.package.manifest)}};
    out.theme_pin={{"id",out.theme.at("theme_id")},{"version","0.1.0"},{"sha256",asset_hash}};return out;
}
}
AuthoredTheme validate_authored_theme(const ContentPackage& package){
    const auto manifest=validate_content_manifest(package.manifest);
    need(manifest.at("kind")=="theme"&&package.assets.size()==1&&package.assets.count("theme.json"),"theme.artifact");
    const auto theme=parse_content_json(package.assets.at("theme.json"));validate_content_document(theme,"theme");
    need(theme.at("schema_version")=="0.2.0","theme.artifact");
    auto result=artifact(theme,manifest.at("license").get<std::string>());
    need(result.package.manifest==package.manifest&&result.package.assets==package.assets,"theme.artifact");return result;
}
std::optional<AuthoredTheme> author_theme(const ResourceSet& source,const Json& proposed,const Policy& policy,const std::set<std::string>& capabilities){
    authorize_resources(source,policy,capabilities);need(capabilities.count("theme.typography")&&!policy.denied_capabilities.count("theme.typography"),"policy.denied");
    validate_content_document(proposed,"theme");if(proposed.dump()==source.theme().dump())return {};
    auto original=source.theme(),other=proposed;for(const char* k:{"schema_version","font","font_roles"}){original.erase(k);other.erase(k);}
    need(original.dump()==other.dump()&&proposed.at("schema_version")=="0.2.0","theme.authoring_scope");
    std::optional<std::string> license;
    for(const auto& package:source.packages()){
        const auto m=parse_content_json(package->manifest,65536);if(m.at("kind")!="theme"||m.at("version")!=source.theme_pin().at("version"))continue;
        const auto& bytes=package->assets.at("theme.json");if(sha256(bytes)!=source.theme_pin().at("sha256"))continue;
        const auto doc=parse_content_json(bytes);if(doc.at("theme_id")!=source.theme_pin().at("id"))continue;
        need(!license,"content.ambiguous");license=m.at("license").get<std::string>();
    }
    need(license.has_value(),"content.theme");auto out=artifact(proposed,*license);
    (void)ContentCatalog({out.package});return out;
}
}
