#pragma once
#include "layout.hpp"
#include <optional>
namespace syspane::interfaces {
enum class GuideSource {sibling,area,grid};
struct SnapTarget {std::string id;scene::Rect box;};
struct SnapGuide {scene::Unit position;GuideSource source;std::string target;unsigned moving,anchor;};
struct SnapInput {
    scene::Rect selection,area;
    std::vector<SnapTarget> siblings;
    scene::Unit origin_x=0,origin_y=0,spacing=8*scene::dip,threshold=6*scene::dip,dx=0,dy=0;
    bool grid=false,guides=false,resize=false,bypass=false;
};
struct SnapResult {scene::Unit dx,dy;std::optional<SnapGuide> x,y;};
// Pure projection of a captured geometry snapshot. Never changes authored state.
SnapResult snap(const SnapInput&);
}
