#pragma once
#include "authored.hpp"
namespace syspane::configuration {
struct ThemeFont {std::string family;double size_dip=0;unsigned weight=400;std::string style="normal";};
// Owned font value. Resolution neither changes authored bytes nor substitutes fonts.
ThemeFont theme_font(const Json& theme,const std::string& role);
// Immutable proof for an exact theme; it owns no native resources or policy.
class ValidatedTheme {
public:
    explicit ValidatedTheme(const Json&);
    ValidatedTheme(const ValidatedTheme&)=delete;ValidatedTheme& operator=(const ValidatedTheme&)=delete;
    ValidatedTheme(ValidatedTheme&&)=delete;ValidatedTheme& operator=(ValidatedTheme&&)=delete;
    bool matches(const Json&)const;
    ThemeFont font(const Json&,const std::string& role)const;
private:
    Json theme_;
};
}
