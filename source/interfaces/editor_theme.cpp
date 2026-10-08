#include "editor_theme.hpp"
#include "editor_content.hpp"
#include "authored_equal.hpp"
#include <iomanip>
#include <limits>
#include <locale>
#include <sstream>
namespace syspane::interfaces {
namespace {
namespace c=configuration;using c::Json;
FontInput hydrate(const Json& f){std::ostringstream s;s.imbue(std::locale::classic());s<<std::setprecision(std::numeric_limits<double>::max_digits10)<<f.at("size_dip").get<double>();
    return {f.at("family"),s.str(),std::to_string(f.value("weight",400u)),f.value("style",std::string("normal"))};}
Json parse(const FontInput& f){return {{"family",f.family},{"size_dip",content_number(f.size_dip)},{"weight",content_integer(f.weight,100,900)},{"style",f.style}};}
Json normalized(Json f){if(!f.contains("weight"))f["weight"]=400;if(!f.contains("style"))f["style"]="normal";return f;}
}
ThemeInput theme_input(const Json& theme){c::validate_content_document(theme,"theme");ThemeInput out;out.font=hydrate(theme.at("font"));
    if(theme.contains("font_roles"))for(auto i=theme.at("font_roles").begin();i!=theme.at("font_roles").end();++i)out.roles.emplace(i.key(),hydrate(i.value()));
    return out;
}
Json theme_edit(const Json& theme,const ThemeInput& input){
    c::validate_content_document(theme,"theme");if(input.roles.size()>4)throw protocol::Error("theme.role");
    Json roles=Json::object();for(const auto& r:input.roles){if(r.first!="body"&&r.first!="label"&&r.first!="value"&&r.first!="diagnostic")throw protocol::Error("theme.role");roles[r.first]=parse(r.second);}
    auto out=theme;out["schema_version"]="0.2.0";out["font"]=parse(input.font);if(roles.empty())out.erase("font_roles");else out["font_roles"]=roles;
    c::validate_content_document(out,"theme");
    if(c::authored_equal(out.at("font"),normalized(theme.at("font")))&&c::authored_equal(roles,theme.value("font_roles",Json::object())))return theme;
    return out;
}
}
