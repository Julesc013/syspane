#pragma once
#include "scene_surface.hpp"
namespace syspane::rendering {
// Internal helpers. Only SceneSurface admits inputs and owns their lifetimes.
SurfaceText compose_table(const configuration::Json&,const std::vector<scene::BindingInput>&,
    std::uint64_t,const std::function<SurfaceCell(const scene::BindingRow&)>&);
TextRaster raster_table(const TextRequest&,SurfaceText&,std::size_t construction_pixels,TextSession* session=nullptr);
std::size_t surface_text_bytes(const SurfaceText&);
}
