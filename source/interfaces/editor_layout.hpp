#pragma once
#include "editor_content.hpp"
namespace syspane::interfaces {
struct LayoutVariantInput {
    std::string kind;
    std::map<std::string,std::map<std::string,std::string>> by_kind;
};
struct LayoutInput {
    std::vector<LayoutVariantInput> variants;
    std::vector<std::string> thresholds;
    std::string display_kind,display_value,priority,sibling;
    bool breakpoints_present=false;
};
LayoutInput layout_input(const Json& scene,const std::string& id);
std::vector<SceneEdit> layout_edits(const Json& scene,const std::string& id,const LayoutInput&);
}
