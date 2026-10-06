#pragma once
#include "scene_surface.hpp"
namespace syspane::rendering {
// Internal helpers; SceneSurface owns history, current policy and all output lifetimes.
scene::ChartPlot compose_chart(const configuration::Json& widget,SurfaceText& text,const scene::ChartView&,
    const std::string& unit,unsigned width,unsigned height,std::size_t work_limit);
TextRaster raster_chart(const TextRequest&,SurfaceText&,const scene::ChartPlot&,std::size_t construction_pixels);
}
