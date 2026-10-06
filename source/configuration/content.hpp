#pragma once
#include "authored.hpp"
#include <memory>

namespace syspane::configuration {
struct ContentPackage { std::string manifest;std::map<std::string,std::string> assets; };
// Both reader and resolver validate names before using them as filesystem paths.
void validate_content_path(const std::string& path);
Json parse_content_json(std::string_view bytes,std::size_t maximum=262144);
Json validate_content_manifest(std::string_view bytes);
struct PresetPlan {
    Json command,theme,package_pins,preset_pins,setting_origins,missing_optional;
    Authored candidate;
    std::vector<std::shared_ptr<const ContentPackage>> packages;
};
class ContentCatalog {
public:
    explicit ContentCatalog(std::vector<ContentPackage> packages);
    PresetPlan preview(const Json& package_pin,const Json& preset_pin,const Authored& baseline,const std::string& request,
                       const Authority& authority,const Policy& policy,const std::set<std::string>& capabilities)const;
private:
    struct Entry {std::shared_ptr<const ContentPackage> bytes;Json manifest,document,pin;std::set<std::size_t> closure;};
    std::vector<Entry> entries_;
};
}
