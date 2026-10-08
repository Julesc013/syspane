#include "theme_font.hpp"
namespace syspane::configuration {
ThemeFont theme_font(const Json& theme,const std::string& role){
    if(role!="body"&&role!="label"&&role!="value"&&role!="diagnostic")throw protocol::Error("theme.role");
    validate_content_document(theme,"theme");
    const Json* font=&theme.at("font");
    const bool modern=theme.at("schema_version")=="0.2.0";
    if(modern&&theme.contains("font_roles")&&theme.at("font_roles").contains(role))font=&theme.at("font_roles").at(role);
    return {font->at("family").get<std::string>(),font->at("size_dip").get<double>(),modern?font->at("weight").get<unsigned>():400u,modern?font->at("style").get<std::string>():"normal"};
}
}
