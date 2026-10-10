#include "scene_text.hpp"
#include "theme_font.hpp"
#include <algorithm>
#include <array>
#include <set>
namespace syspane::rendering {
namespace {void need(bool b,const char* why){if(!b)throw protocol::Error(why);}}
TextRaster render_blocks(const TextRequest& request,const std::vector<TextBlock>& blocks,std::size_t capacity,TextSession* session){
    need(request.denominator>=1&&request.denominator<=16&&request.numerator>=1&&request.numerator<=16,"text.input");
    need(!blocks.empty()&&blocks.size()<=16,"surface.capacity");
    std::size_t bytes=0;for(const auto& b:blocks){bytes+=b.text.size();need(bytes<=4096,"surface.capacity");}
    if(blocks.size()==1){auto q=request;q.text=blocks[0].text;q.role=blocks[0].role;
        q.pixel_budget=std::min(q.pixel_budget,capacity);return render_text(q,session);}
    TextRequest q=request;q.theme["tokens"]["background"]="#00000000";
    if(q.contrast!="authored")q.theme["tokens"][q.token]=q.contrast=="light"?"#000000ff":"#ffffffff";
    q.contrast="authored";
    std::optional<configuration::ValidatedTheme> prepared;
    if(!q.prepared_theme||!q.prepared_theme->matches(q.theme)){prepared.emplace(q.theme);q.prepared_theme=&*prepared;}
    const auto gap=(4*q.numerator+q.denominator-1)/q.denominator;
    std::vector<TextRaster> parts;std::set<std::string> fonts;std::size_t retained=0;
    TextRaster result;
    for(const auto& b:blocks){need(retained<capacity,"surface.capacity");q.role=b.role;q.text=b.text;q.pixel_budget=std::min(request.pixel_budget,capacity-retained);
        auto part=render_text(q,session);need(!part.missing_glyphs,"surface.glyphs");
        result.lines+=part.lines;need(result.lines<=1024,"surface.capacity");
        result.width=std::max(result.width,part.width);result.height+=part.height+(parts.empty()?0:gap);
        need(result.width<=2048&&result.height<=2048,"surface.capacity");
        retained+=static_cast<std::size_t>(part.width)*part.height;fonts.insert(part.fonts.begin(),part.fonts.end());parts.push_back(std::move(part));}
    const auto pixels=static_cast<std::size_t>(result.width)*result.height;
    need(pixels<=request.pixel_budget&&retained<=capacity&&pixels<=capacity-retained,"surface.capacity");
    const std::string token=request.contrast=="light"?"#ffffffff":request.contrast=="dark"?"#000000ff":request.theme["tokens"]["background"].get<std::string>();
    std::array<unsigned,4> background{};for(unsigned c=0;c<4;++c)background[c]=static_cast<unsigned>(std::stoul(token.substr(1+2*c,2),nullptr,16));
    for(unsigned c=0;c<3;++c)background[c]=(background[c]*background[3]+127)/255;
    result.rgba.resize(pixels*4);for(std::size_t p=0;p<pixels;++p)for(unsigned c=0;c<4;++c)result.rgba[p*4+c]=static_cast<unsigned char>(background[c]);
    unsigned y0=0;for(const auto& part:parts){for(unsigned y=0;y<part.height;++y)for(unsigned x=0;x<part.width;++x){
        const auto src=(static_cast<std::size_t>(y)*part.width+x)*4,dst=(static_cast<std::size_t>(y0+y)*result.width+x)*4;
        for(unsigned c=0;c<4;++c)result.rgba[dst+c]=static_cast<unsigned char>(part.rgba[src+c]+(result.rgba[dst+c]*(255-part.rgba[src+3])+127)/255);}
        y0+=part.height+gap;}
    result.fonts.assign(fonts.begin(),fonts.end());return result;
}
}
