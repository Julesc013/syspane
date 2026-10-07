#pragma once
#include "scene_surface.hpp"
namespace syspane::interfaces {
struct InspectorRow {std::string key,item,information;std::vector<InspectorRow> children;};
std::vector<InspectorRow> inspector_rows(const rendering::SurfaceFrame&);
}
