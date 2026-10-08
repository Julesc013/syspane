#pragma once
#include "image_fixture.hpp"
namespace fixture {
inline Json visibility_rule(std::uint64_t value=123){return {{"schema_version","0.1.0"},{"binding",binding()},{"op","eq"},{"value",value},{"unit","byte"}};}
inline void visibility_config(v::SurfaceConfig& cfg){
    content_config(cfg);cfg.authored.scene["schema_version"]="0.5.0";cfg.experimental_visibility=true;
    cfg.capabilities.insert({"scene.content","scene.edit-locks","scene.visibility"});std::vector<c::ContentPackage> packages;
    for(const auto& p:cfg.resources->packages())packages.push_back(*p);
    cfg.resources=c::ContentCatalog(std::move(packages)).resources(cfg.resources->selection(),cfg.authored);
}
inline v::SurfaceConfig visibility_text_config(const std::string& root){auto cfg=config(root);visibility_config(cfg);auto& w=cfg.authored.scene["widgets"][0];w["kind"]="text";w["bindings"]=Json::array();w["title"]="Private label";w["content"]["body"]="Secret body";w["visibility"]=visibility_rule();return cfg;}
inline v::SurfaceConfig visibility_group_config(const std::string& root,const Json& theme_changes=Json::object()){auto cfg=config(root,theme_changes);visibility_config(cfg);
    auto a=widget("a","text","First"),b=widget("b","value","Second"),g=widget("g","group","Group");
    a["content"]={{"body","Secret body"}};b["content"]=Json::object();b["layout"]["base"]["x"]=330;
    g["bindings"]=Json::array();g["content"]=Json::object();g["children"]={"a","b"};g["layout"]["base"]["width"]=800;g["layout"]["base"]["height"]=600;
    cfg.authored.scene["widgets"]={b,g,a};cfg.authored.scene["roots"]={"g"};return cfg;
}
}
