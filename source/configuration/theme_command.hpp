#pragma once
#include "theme_resources.hpp"
namespace syspane::configuration {
// Serialized owner: current resources are the sole source; no import I/O.
ResourceSnapshot prepare_theme_command(const ResourceSet&,const Authored&,const Json&,
    const Policy&,const std::set<std::string>& capabilities);
// Recovery verifies fulfilled font intent as well as byte and selection identity.
void validate_theme_command_binding(const Json&,const ResourceSet&);
}
