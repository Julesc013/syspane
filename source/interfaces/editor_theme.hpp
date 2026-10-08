#pragma once
#include "authored.hpp"
namespace syspane::interfaces {
struct FontInput {std::string family,size_dip,weight,style;};
struct ThemeInput {FontInput font;std::map<std::string,FontInput> roles;};
ThemeInput theme_input(const configuration::Json&);
// Pure candidate construction. Does not stage, publish or grant resource authority.
configuration::Json theme_edit(const configuration::Json&,const ThemeInput&);
}
