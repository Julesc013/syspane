#include "editor_content.hpp"
#include "digest.hpp"
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <limits>
#include <locale>
#include <regex>
#include <sstream>
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
bool admitted(const Json& value,const std::vector<ContentChoice>& choices){return std::any_of(choices.begin(),choices.end(),[&](const ContentChoice& c){return c.value==value;});}
std::string number_text(const Json& value){std::ostringstream s;s.imbue(std::locale::classic());s<<std::setprecision(std::numeric_limits<double>::max_digits10)<<value.get<double>();return s.str();}
const std::string& field(const ContentInput& in,const char* key){const auto it=in.fields.find(key);need(it!=in.fields.end(),"editor.content_field");return it->second;}
std::string choice(const ContentInput& in,const char* key,std::initializer_list<const char*> allowed){const auto& v=field(in,key);need(std::find(allowed.begin(),allowed.end(),v)!=allowed.end(),"editor.content_choice");return v;}
}
double content_number(const std::string& value){
    static const std::regex grammar("^[+-]?[0-9]+([.][0-9]+)?([eE][+-]?[0-9]+)?$");
    need(value.size()<=64&&std::regex_match(value,grammar),"editor.content_number");
    std::istringstream stream(value);stream.imbue(std::locale::classic());double n=0;stream>>n;
    need(stream&&stream.eof()&&std::isfinite(n),"editor.content_number");return n;
}
unsigned content_integer(const std::string& value,unsigned minimum,unsigned maximum){
    need(!value.empty()&&value.size()<=10&&(value.size()==1||value[0]!='0'),"editor.content_integer");
    std::uint64_t n=0;for(const char c:value){need(c>='0'&&c<='9',"editor.content_integer");n=n*10+static_cast<unsigned>(c-'0');need(n<=maximum,"editor.content_integer");}
    need(n>=minimum,"editor.content_integer");return static_cast<unsigned>(n);
}
ContentChoices content_choices(const configuration::ResourceSet& resources){
    ContentChoices out;out.themes.push_back({"Inherit settings",nullptr});std::set<std::string> themes;
    need(resources.packages().size()<=64,"editor.content_budget");std::size_t count=0;
    for(const auto& package:resources.packages()){
        const auto manifest=configuration::parse_content_json(package->manifest,65536);
        const auto id=manifest.at("package_id").get<std::string>(),version=manifest.at("version").get<std::string>();
        const Json pin={{"id",id},{"version",version},{"sha256",configuration::sha256(package->manifest)}};
        for(const auto& asset:manifest.at("assets")){
            need(++count<=1024,"editor.content_budget");const auto& media=asset.at("media_type");
            if(media=="image/png"||media=="image/jpeg"||media=="image/svg+xml")out.images.push_back({id+" / "+version+" / "+asset.at("path").get<std::string>(),{{"package",pin},{"path",asset.at("path")},{"sha256",asset.at("sha256")}}});
        }
        if(manifest.at("kind")=="theme"){
            const auto theme=configuration::parse_content_json(package->assets.at("theme.json"));const auto theme_id=theme.at("theme_id").get<std::string>();
            if(themes.insert(theme_id).second)out.themes.push_back({theme.at("name").get<std::string>()+" ("+theme_id+")",theme_id});
        }
    }
    const auto less=[](const ContentChoice& a,const ContentChoice& b){return a.value.dump()<b.value.dump();};
    std::sort(out.images.begin(),out.images.end(),less);std::sort(out.themes.begin()+1,out.themes.end(),less);return out;
}
ContentInput content_input(const Json& widget){
    ContentInput out;const auto& kind=widget.at("kind");const auto& c=widget.at("content");
    if(kind=="table")for(std::size_t n=0;n<c.at("columns").size();++n)out.columns.push_back({n,c.at("columns")[n].at("label")});
    else if(kind=="chart"){
        for(const char* k:{"window_ms","max_points"})out.fields[k]=c.at(k).dump();
        out.fields["interpolation"]=c.at("interpolation");
        const auto& axis=c.at("axis");out.fields["axis"]=axis.at("mode");out.fields["include_zero"]=axis.value("include_zero",true)?"true":"false";
        out.fields["minimum"]=axis.contains("minimum")?number_text(axis.at("minimum")):"0";out.fields["maximum"]=axis.contains("maximum")?number_text(axis.at("maximum")):"100";
    }else if(kind=="image"){
        out.asset=c.at("asset");out.fields["alt"]=c.at("alt");out.fields["fit"]=c.at("fit");
        for(const char* k:{"width_dip","height_dip"})out.fields[k]=number_text(c.at(k));
    }return out;
}
WidgetContentEdit content_edit(const Json& widget,const ContentInput& input,const ContentChoices& choices){
    WidgetContentEdit out{widget.at("id"),widget.at("bindings"),widget.at("content")};const auto& kind=widget.at("kind");
    if(kind=="table"){
        need(input.columns.size()==out.bindings.size()&&!input.columns.empty()&&input.columns.size()<=256,"editor.content_columns");
        std::set<std::size_t> seen;Json bindings=Json::array(),columns=Json::array();
        for(const auto& c:input.columns){need(c.original<out.bindings.size()&&seen.insert(c.original).second,"editor.content_columns");bindings.push_back(out.bindings[c.original]);columns.push_back({{"label",c.label}});}
        out.bindings=std::move(bindings);out.content={{"columns",std::move(columns)}};
    }else if(kind=="chart"){
        const auto mode=choice(input,"axis",{"auto","fixed"});Json axis={{"mode",mode}};
        if(mode=="auto")axis["include_zero"]=choice(input,"include_zero",{"true","false"})=="true";
        else {const auto minimum=content_number(field(input,"minimum")),maximum=content_number(field(input,"maximum"));need(minimum<maximum,"editor.content_axis");axis["minimum"]=minimum;axis["maximum"]=maximum;}
        out.content={{"window_ms",content_integer(field(input,"window_ms"),1000,3600000)},{"max_points",content_integer(field(input,"max_points"),2,4096)},
            {"interpolation",choice(input,"interpolation",{"linear","step"})},{"axis",std::move(axis)}};
    }else if(kind=="image"){
        need(admitted(input.asset,choices.images),"editor.content_asset");const auto width=content_number(field(input,"width_dip")),height=content_number(field(input,"height_dip"));
        need(width>=1&&width<=4096&&height>=1&&height<=4096,"editor.content_dimensions");
        out.content={{"asset",input.asset},{"alt",field(input,"alt")},{"width_dip",width},{"height_dip",height},{"fit",choice(input,"fit",{"contain","cover","stretch"})}};
    }return out;
}
SceneThemeEdit content_theme(const Json& id,const ContentChoices& choices){need(admitted(id,choices.themes),"editor.content_theme");return {id.is_null()?std::nullopt:std::optional<std::string>(id.get<std::string>())};}
}
