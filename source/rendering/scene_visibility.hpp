#pragma once
#include "scene_surface.hpp"
namespace syspane::rendering {
// Unpublished candidate owned by SceneSurface; no independent retained cache.
void condition_surface(const SurfaceConfig&,const std::vector<scene::BindingInput>&,std::uint64_t,
    SurfaceFrame&,std::map<std::string,SurfaceText>&,std::map<std::string,TextRaster>&,
    std::size_t display_pixels,std::size_t& leaf_pixels,TextSession* session=nullptr);
}
