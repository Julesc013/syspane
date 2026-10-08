#pragma once
#include "editor_binding.hpp"
namespace syspane::interfaces {
struct VisibilityInput {
    std::string mode="always";
    Json binding;
    PredicateInput comparison{"","gt","number","0"};
    std::string unit="byte";
};
VisibilityInput visibility_input(const Json& scene,const std::vector<std::string>& ids);
void visibility_source(const Json& binding);
std::optional<SetWidgetVisibility> visibility_edit(const std::vector<std::string>& ids,const VisibilityInput&);
}
