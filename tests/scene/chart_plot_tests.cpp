#include "chart_plot.hpp"
#include <cstring>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
namespace s=syspane::scene;using syspane::configuration::Json;
namespace {
void need(bool ok,const char* why="plot oracle"){if(!ok)throw std::runtime_error(why);}
s::ChartNumber number(const Json& j){if(j.contains("u"))return static_cast<std::uint64_t>(std::stoull(j["u"].get<std::string>()));
    const auto bits=static_cast<std::uint64_t>(std::stoull(j["f"].get<std::string>(),nullptr,16));double d;std::memcpy(&d,&bits,sizeof d);return d;}
void masks(const s::ChartPlot& p,const std::vector<std::string>& lines){need(lines.size()==p.height,"mask height");
    for(unsigned y=0;y<p.height;++y){need(lines[y].size()==p.width,"mask width");for(unsigned x=0;x<p.width;++x)need((p.mask[y*p.width+x]!=0)==(lines[y][x]=='#'),"mask pixel");}}
template<class F> void reject(F f,const char* why){bool rejected=false;try{f();}catch(const syspane::protocol::Error& e){rejected=std::string(e.what())==why;}need(rejected,why);}
std::vector<s::ChartPoint> points(){return {{0,1,std::uint64_t{0},false},{500000000,2,std::uint64_t{4},true},{1000000000,3,std::uint64_t{0},true}};}
void numeric(const std::string& root){std::ifstream f(root+"/../chart-cases/numeric.json");need(f.good(),"numeric oracle absent");Json cases;f>>cases;
    for(const auto& c:cases){s::ChartAxis a;a.automatic=false;a.minimum=number(c["low"]);a.maximum=number(c["high"]);
        const auto p=s::plot_chart({{1000000000,1,number(c["value"]),false}},1000000000,1000,a,s::ChartInterpolation::linear,2,c["height"]);
        need(p.clipped==c["clipped"].get<unsigned>()&&p.segments==1,"clip/segment count");
        for(unsigned y=0;y<p.height;++y){need(!p.mask[y*2],"unexpected x");need((p.mask[y*2+1]!=0)==(y==c["y"].get<unsigned>()),"exact rational y");}}
}
void geometry(){auto v=points();auto p=s::plot_chart(v,1000000000,1000,{},s::ChartInterpolation::linear,5,5);
    masks(p,{"..#..","..##.",".#.#.",".#..#","#...#"});need(p.segments==1&&p.clipped==0);
    p=s::plot_chart(v,1000000000,1000,{},s::ChartInterpolation::step,5,5);masks(p,{"..###","..#.#","..#.#","..#.#","###.#"});
    v[2].joins_previous=false;p=s::plot_chart(v,1000000000,1000,{},s::ChartInterpolation::linear,5,5);
    masks(p,{"..#..","..#..",".#...",".#...","#...#"});need(p.segments==2);
    v=points();v[1].measured_ns=1;v[2].measured_ns=2;p=s::plot_chart(v,1000000000,1000,{},s::ChartInterpolation::linear,2,5);
    masks(p,{"#.","#.","#.","#.","#."});
}
void ranges(){auto p=s::plot_chart({{0,1,std::uint64_t{7},false}},0,1000,{},s::ChartInterpolation::linear,5,5);
    masks(p,{".....",".....","....#",".....","....."});need(std::get<std::uint64_t>(*p.minimum)==7&&*p.minimum==*p.maximum);
    s::ChartAxis a;a.include_zero=true;p=s::plot_chart({{0,1,std::uint64_t{7},false}},0,1000,a,s::ChartInterpolation::linear,5,5);
    masks(p,{"....#",".....",".....",".....","....."});need(std::get<std::uint64_t>(*p.minimum)==0);
    p=s::plot_chart({},std::nullopt,1000,a,s::ChartInterpolation::linear,2,2);masks(p,{"..",".."});need(!p.minimum&&!p.maximum&&!p.segments);
    const auto max=std::numeric_limits<std::uint64_t>::max();p=s::plot_chart({{max-1000000000,1,max-2,false},{max,2,max,true}},max,1000,{},s::ChartInterpolation::linear,3,3);
    masks(p,{"..#",".#.","#.."});need(std::get<std::uint64_t>(*p.minimum)==max-2);
}
void limits(){auto v=points();const auto call=[&]{return s::plot_chart(v,1000000000,1000,{},s::ChartInterpolation::linear,5,5);};
    v[0].joins_previous=true;reject(call,"chart.input");v=points();v[1].measured_ns=0;reject(call,"chart.input");
    v=points();v[2].value=0.0;reject(call,"chart.input");v=points();v[2].value=std::numeric_limits<double>::infinity();reject(call,"chart.input");
    v=points();reject([&]{s::plot_chart(v,{},1000,{},s::ChartInterpolation::linear,5,5);},"chart.input");
    reject([&]{s::plot_chart(v,1000000000,999,{},s::ChartInterpolation::linear,5,5);},"chart.input");
    reject([&]{s::plot_chart(v,1000000000,1000,{},s::ChartInterpolation::linear,1,5);},"chart.input");
    reject([&]{s::plot_chart(v,1000000000,1000,{},s::ChartInterpolation::step,5,5,5);},"chart.capacity");
    s::ChartAxis a;a.automatic=false;a.minimum=4.0;a.maximum=4.0;reject([&]{s::plot_chart(v,1000000000,1000,a,s::ChartInterpolation::linear,5,5);},"chart.input");
}
}
int chart_plot_test(const std::string& name,const std::string& root){
    if(name=="PLOT-NUMERIC")numeric(root);else if(name=="PLOT-GEOMETRY")geometry();else if(name=="PLOT-RANGES")ranges();else if(name=="PLOT-LIMITS")limits();else throw std::runtime_error("unknown plot case");
    std::cout<<name<<" pass\n";return 0;
}
