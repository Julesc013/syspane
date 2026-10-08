#pragma once
#include "authored_theme.hpp"
namespace syspane::configuration {
// Pure immutable replacement. Null resets to the original preset closure.
// Does not authorize a command, mutate a draft or publish a generation.
ResourceSnapshot replace_theme_resources(const ResourceSet&,const Authored&,
    const std::optional<AuthoredTheme>&,const Policy&,const std::set<std::string>& capabilities);
}
