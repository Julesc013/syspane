#pragma once
#include "authored.hpp"
namespace syspane::configuration {
struct ThemeFont {std::string family;double size_dip=0;unsigned weight=400;std::string style="normal";};
// Owned font value. Resolution neither changes authored bytes nor substitutes fonts.
ThemeFont theme_font(const Json& theme,const std::string& role);
}
