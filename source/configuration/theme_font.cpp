#include "theme_font.hpp"
namespace syspane::configuration {
namespace {
void valid_role(const std::string& role){
    if(role!="body"&&role!="label"&&role!="value"&&role!="diagnostic")throw protocol::Error("theme.role");
}
bool exact(const Json& a,const Json& b,unsigned depth=0){
    if(depth>=64||a.type()!=b.type())return false;
    if(!a.is_structured())return a==b;
    if(a.size()!=b.size())return false;
    auto other=b.begin();
    for(auto current=a.begin();current!=a.end();++current,++other){
        if(a.is_object()&&current.key()!=other.key())return false;
        if(!exact(current.value(),other.value(),depth+1))return false;
    }
    return true;
}
ThemeFont resolve(const Json& theme,const std::string& role){
    const Json* font=&theme.at("font");
    const bool modern=theme.at("schema_version")=="0.2.0";
    if(modern&&theme.contains("font_roles")&&theme.at("font_roles").contains(role))font=&theme.at("font_roles").at(role);
    return {font->at("family").get<std::string>(),font->at("size_dip").get<double>(),modern?font->at("weight").get<unsigned>():400u,modern?font->at("style").get<std::string>():"normal"};
}
}
ThemeFont theme_font(const Json& theme,const std::string& role){valid_role(role);validate_content_document(theme,"theme");return resolve(theme,role);}
ValidatedTheme::ValidatedTheme(const Json& theme){validate_content_document(theme,"theme");theme_=theme;}
bool ValidatedTheme::matches(const Json& theme)const{return exact(theme_,theme);}
ThemeFont ValidatedTheme::font(const Json& theme,const std::string& role)const{
    valid_role(role);return matches(theme)?resolve(theme_,role):theme_font(theme,role);
}
}
