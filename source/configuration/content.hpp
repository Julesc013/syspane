#pragma once
#include "authored.hpp"
#include <memory>

namespace syspane::configuration {
struct ContentPackage { std::string manifest;std::map<std::string,std::string> assets; };
class ResourceSet {
public:
    const Json& selection()const{return selection_;}
    const Json& theme_pin()const{return theme_pin_;}
    const Json& theme()const{return theme_;}
    const std::set<std::string>& required()const{return required_;}
    const std::vector<std::shared_ptr<const ContentPackage>>& packages()const{return packages_;}
    const std::vector<std::shared_ptr<const ContentPackage>>& base_packages()const{return base_packages_;}
private:
    friend class ContentCatalog;
    ResourceSet()=default;
    Json selection_,theme_pin_,theme_;
    std::set<std::string> required_;
    std::vector<std::shared_ptr<const ContentPackage>> packages_;
    std::vector<std::shared_ptr<const ContentPackage>> base_packages_;
};
using ResourceSnapshot=std::shared_ptr<const ResourceSet>;
void authorize_resources(const ResourceSet&,const Policy&,const std::set<std::string>& capabilities);
void validate_resource_binding(const ResourceSet&,const Authored&);
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
    ResourceSnapshot resources(const Json& selection,const Authored& candidate)const;
    // Explicit experimental contract; legacy commands/stores use resources().
    ResourceSnapshot theme_resources(const Json& selection,const Authored& candidate)const;
    PresetPlan preview(const Json& package_pin,const Json& preset_pin,const Authored& baseline,const std::string& request,
                       const Authority& authority,const Policy& policy,const std::set<std::string>& capabilities)const;
private:
    ResourceSnapshot resolve_resources(const Json&,const Authored&,bool overrides)const;
    struct Selection {std::size_t leaf;std::vector<std::size_t> chain;};
    Selection select(const Json& package_pin,const Json& preset_pin)const;
    std::size_t lookup(const Json& pin,const char* kind,const std::set<std::size_t>& scope)const;
    struct Entry {std::shared_ptr<const ContentPackage> bytes;Json manifest,document,pin;std::set<std::size_t> closure;};
    std::vector<Entry> entries_;
};
}
