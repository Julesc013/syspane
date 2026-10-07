#pragma once
#include "chart_fixture.hpp"
#include <array>
#include <unistd.h>
namespace fixture {
inline std::string image_worker_path(){std::array<char,4096> path{};const auto n=::readlink("/proc/self/exe",path.data(),path.size()-1);need(n>0,"image fixture executable");std::string value(path.data(),n);return value.substr(0,value.rfind('/'))+"/SysPane.ImageWorker";}
inline std::string image_bytes(const std::string& root){std::ifstream file(root+"/../../../tests/scene/image-cases/rgba.png",std::ios::binary);need(file.good(),"image fixture bytes");return {std::istreambuf_iterator<char>(file),{}};}
inline v::SurfaceConfig image_config(const std::string& root,std::string bytes={},std::string media="image/png",std::string fit="contain"){
    if(bytes.empty())bytes=image_bytes(root);
    auto cfg=config(root);auto theme=pack("package:theme","theme",cfg.resources->theme());
    auto manifest=Json::parse(theme.manifest);theme.assets["image.data"]=bytes;
    manifest["assets"].push_back({{"path","image.data"},{"media_type",media},{"sha256",c::content_sha256(bytes)},{"bytes",bytes.size()}});
    manifest["total_unpacked_bytes"]=manifest["total_unpacked_bytes"].get<std::size_t>()+bytes.size();theme.manifest=manifest.dump()+"\n";
    auto& w=cfg.authored.scene["widgets"][0];w["id"]="image";w["kind"]="image";w["title"]="Image title";w["bindings"]=Json::array();w["layout"]["base"]={{"kind","fixed"},{"x",0},{"y",0},{"width",32},{"height",16}};
    w["content"]={{"asset",{{"package",package_pin(theme)},{"path","image.data"},{"sha256",c::content_sha256(bytes)}}},{"alt","Public image"},{"width_dip",9},{"height_dip",5},{"fit",fit}};
    cfg.authored.scene["schema_version"]="0.3.0";cfg.authored.scene["roots"]={"image"};auto scene=pack("package:scene","scene",cfg.authored.scene);
    Json preset={{"schema_version","0.1.0"},{"preset_id","preset:image"},{"version","0.1.0"},{"parent",nullptr},{"scene",document_pin(scene)},{"theme",document_pin(theme)},
        {"settings",Json::array()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    auto pr=pack("package:preset","preset",preset,Json::array({package_pin(theme),package_pin(scene)}));
    cfg.resources=c::ContentCatalog({theme,scene,pr}).resources({{"package",package_pin(pr)},{"preset",document_pin(pr)}},cfg.authored);cfg.capabilities.insert("scene.content");return cfg;
}
inline std::string green_image(){return "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"2\" height=\"2\"><rect width=\"2\" height=\"2\" fill=\"#00ff00\"/></svg>";}
}
