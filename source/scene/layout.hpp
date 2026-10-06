#pragma once
#include "authored.hpp"

namespace syspane::scene {
using Unit=std::int64_t;
inline constexpr Unit dip=64;
struct Rect { Unit x=0,y=0,width=0,height=0; };
struct Size { Unit width=0,height=0; };
struct Insets { Unit left=0,top=0,right=0,bottom=0; };
struct Metrics { Size minimum,preferred; };
struct Display {
    std::string id;
    Rect bounds,work;
    Insets safe;
    std::vector<Rect> exclusions;
    Unit pixel_x=0,pixel_y=0;
    unsigned scale_numerator=1,scale_denominator=1;
};
struct Topology {
    std::vector<Display> displays;
    std::map<std::string,std::vector<std::string>> roles;
    std::string fallback;
};
struct Diagnostic { std::string widget,code,related; };
struct Node {
    std::string id,parent,display,kind;
    int variant=-1;
    Rect box,visible,content;
    Rect pixels; // Device pixels, all other Rect members are 1/64 DIP.
    std::string overflow="none";
    bool clipped=false;
};
enum class State { ready,degraded,alternative };
struct Plan {
    std::string scene_id,revision;
    State state=State::ready;
    std::vector<Node> nodes;
    std::vector<Diagnostic> diagnostics;
};
// Pure, bounded projection. Inputs are immutable; native measurement precedes it.
// Throws protocol::Error on invalid input, without a partial result or side effect.
Plan resolve(const configuration::Json& scene,const Topology& topology,
             const std::map<std::string,Metrics>& metrics);
}
