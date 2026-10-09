#include "scene_chart.hpp"
#include <algorithm>
#include <array>
namespace syspane::rendering {
namespace {
using configuration::Json;namespace s=scene;
void need(bool b,const char* why){if(!b)throw protocol::Error(why);}
std::string number(const s::ChartNumber& n){return n.index()==1?std::to_string(std::get<std::uint64_t>(n)):Json(std::get<double>(n)).dump();}
const char* fault(s::ChartCode code){switch(code){case s::ChartCode::conflict:return "Chart conflict";case s::ChartCode::clock_fault:return "Chart clock fault";
    case s::ChartCode::invalid:return "Chart invalid";case s::ChartCode::unsupported:return "Chart unsupported";case s::ChartCode::clock_unknown:return "Chart clock unknown";default:return "";}}
std::array<unsigned,4> color(const std::string& token){std::array<unsigned,4> c{};for(unsigned i=0;i<4;++i)c[i]=static_cast<unsigned>(std::stoul(token.substr(1+i*2,2),nullptr,16));
    for(unsigned i=0;i<3;++i)c[i]=(c[i]*c[3]+127)/255;
    return c;}
}
scene::ChartPlot compose_chart(const Json& widget,SurfaceText& text,const s::ChartView& view,
    const std::string& unit,unsigned width,unsigned height,std::size_t work_limit){
    need(view.code!=s::ChartCode::denied,"policy.denied");const auto& content=widget["content"];s::ChartAxis axis;axis.automatic=content["axis"]["mode"]=="auto";
    if(axis.automatic)axis.include_zero=content["axis"]["include_zero"];
    else{axis.minimum=content["axis"]["minimum"].get<double>();axis.maximum=content["axis"]["maximum"].get<double>();}
    const std::string interpolation=content["interpolation"];
    auto plot=s::plot_chart(view.points,view.window_end_ns,content["window_ms"],axis,interpolation=="linear"?s::ChartInterpolation::linear:s::ChartInterpolation::step,width,height,work_limit);
    text.chart.emplace();auto& chart=*text.chart;chart.samples=view.points.size();chart.segments=plot.segments;
    chart.summary="Samples "+std::to_string(chart.samples)+" | Segments "+std::to_string(chart.segments);
    if(view.capacity_truncated)chart.summary+=" | Capacity truncated";
    if(view.pending_break)chart.summary+=" | Gap pending";
    const auto why=fault(view.code);if(*why)chart.summary+=" | "+std::string(why);
    if(*why)text.notices.push_back(why);
    if(view.capacity_truncated)text.notices.push_back("Chart capacity truncated");
    if(view.pending_break)text.notices.push_back("Chart gap pending");
    if(plot.clipped)text.notices.push_back("Chart clipped");
    if(!text.blocks.empty())text.blocks.push_back({view.capacity_truncated||view.pending_break||*why?"diagnostic":"label",chart.summary});
    const auto range_start=chart.summary.size()+1;
    chart.summary+='\n';chart.summary+=plot.minimum?"Range "+number(*plot.minimum)+" .. "+number(*plot.maximum):"Range unavailable";
    if(!unit.empty()&&unit!="1")chart.summary+=" "+unit;
    if(plot.clipped)chart.summary+=" | Clipped "+std::to_string(plot.clipped);
    if(!text.blocks.empty())text.blocks.push_back({!plot.minimum||plot.clipped?"diagnostic":"value",chart.summary.substr(range_start)});
    const auto window_start=chart.summary.size()+1;
    chart.summary+="\nWindow "+std::to_string(content["window_ms"].get<unsigned>())+" ms | "+interpolation;
    if(!text.blocks.empty())text.blocks.push_back({"label",chart.summary.substr(window_start)});
    text.text+='\n'+chart.summary;text.accessible+='\n'+chart.summary;
    chart.accessible_summary=text.accessible;chart.identity=view.identity;chart.points=view.points;
    for(const auto& point:view.points){text.accessible+="\nPoint "+std::to_string(point.measured_ns)+": "+number(point.value)+"; generation "+std::to_string(point.generation)+(point.joins_previous?"; join":"; start");
        need(text.accessible.size()+text.text.size()+chart.summary.size()<=262144,"surface.capacity");}
    return plot;
}
TextRaster raster_chart(const TextRequest& request,SurfaceText& widget,const s::ChartPlot& plot,std::size_t capacity,TextSession* session){
    need(widget.chart.has_value(),"surface.chart");const auto mask_pixels=static_cast<std::size_t>(plot.width)*plot.height;
    need(mask_pixels<capacity,"surface.capacity");TextRequest q=request;q.wrap_units.reset();q.pixel_budget=std::min(std::size_t{4194304},capacity-mask_pixels);
    const auto bg=color(request.contrast=="light"?"#ffffffff":request.contrast=="dark"?"#000000ff":request.theme["tokens"]["background"].get<std::string>());
    const auto fg=color(request.contrast=="light"?"#000000ff":request.contrast=="dark"?"#ffffffff":request.theme["tokens"]["foreground"].get<std::string>());
    const auto border=request.contrast=="authored"?color(request.theme["tokens"]["muted"]):fg;
    q.theme["tokens"]["foreground"]=request.contrast=="light"?"#000000ff":request.contrast=="dark"?"#ffffffff":request.theme["tokens"]["foreground"].get<std::string>();
    q.theme["tokens"]["background"]="#00000000";q.contrast="authored";auto text=request.theme["schema_version"]=="0.2.0"?render_blocks(q,widget.blocks,capacity-mask_pixels,session):render_text(q,session);need(!text.missing_glyphs,"surface.glyphs");
    const auto gap=(4*q.numerator+q.denominator-1)/q.denominator,graph_y=text.height+gap;
    TextRaster result;result.width=std::max(text.width,plot.width);result.height=graph_y+plot.height;result.fonts=text.fonts;
    const auto pixels=static_cast<std::size_t>(result.width)*result.height,text_pixels=static_cast<std::size_t>(text.width)*text.height;
    need(result.width<=2048&&result.height<=2048&&pixels<=4194304&&text_pixels<=capacity-mask_pixels&&pixels<=capacity-mask_pixels-text_pixels,"surface.capacity");
    result.rgba.resize(pixels*4);for(std::size_t i=0;i<pixels;++i)for(unsigned c=0;c<4;++c)result.rgba[i*4+c]=static_cast<unsigned char>(bg[c]);
    const auto over=[&](unsigned x,unsigned y,const auto& rgba){const auto dst=(static_cast<std::size_t>(y)*result.width+x)*4;
        for(unsigned c=0;c<4;++c)result.rgba[dst+c]=static_cast<unsigned char>(rgba[c]+(result.rgba[dst+c]*(255-rgba[3])+127)/255);};
    for(unsigned y=0;y<text.height;++y)for(unsigned x=0;x<text.width;++x)over(x,y,&text.rgba[(static_cast<std::size_t>(y)*text.width+x)*4]);
    for(unsigned y=0;y<plot.height;++y)for(unsigned x=0;x<plot.width;++x){
        if(!x||!y||x+1==plot.width||y+1==plot.height)over(x,graph_y+y,border);
        if(plot.mask[static_cast<std::size_t>(y)*plot.width+x])over(x,graph_y+y,fg);}
    widget.chart->pixels={0,graph_y,plot.width,plot.height};return result;
}
}
