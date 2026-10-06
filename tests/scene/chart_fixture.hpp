#pragma once
#include "table_fixture.hpp"
namespace fixture {
inline c::Policy chart_policy(std::uint64_t revision=7,bool permit=true){auto p=policy(revision,permit);if(permit)p.disclosure[{"desktop","history"}]={"operational"};return p;}
inline v::SurfaceConfig chart_config(const std::string& root,const Json& theme_changes=Json::object()){auto cfg=config(root,theme_changes);content_config(cfg);auto& w=cfg.authored.scene["widgets"][0];
    w["kind"]="chart";w["content"]={{"window_ms",1000},{"max_points",16},{"interpolation","linear"},{"axis",{{"mode","fixed"},{"minimum",0},{"maximum",100}}}};
    w["layout"]["base"]["width"]=800;w["layout"]["base"]["height"]=600;return cfg;}
inline Json chart_document(std::uint64_t value,std::uint64_t generation,std::uint64_t measured){auto d=document(value,generation);
    for(auto& o:d["observations"])if(!o["measured_at"].is_null())o["measured_at"]["nanoseconds"]=std::to_string(measured);
    return d;}
struct ChartOwner {
    v::SurfaceConfig cfg;std::unique_ptr<v::SceneSurface> surface;std::uint64_t token=0,revision=7,now=0,measured=0,generation=0;unsigned clears=0;bool clear_ok=true;
    explicit ChartOwner(const std::string& root):cfg(chart_config(root)){surface=std::make_unique<v::SceneSurface>(c::Authority{true,"desktop",{"desktop"}},chart_policy(),cfg,std::vector<v::SurfaceProvider>{provider()},[&]{++clears;return clear_ok;});attach();}
    void attach(){token=surface->attach("P1",link(revision),++now).token;need(token!=0,"chart attachment");}
    void full(std::uint64_t value,std::uint64_t time){measured=time;auto d=chart_document(value,++generation,time);
        need(surface->receive("P1",token,revision,wire(d,link(revision)),++now,tick(time)).code==r::DataCode::accepted,"chart receive");}
    v::SurfaceFrame paint(){v::SurfaceFrame out;surface->paint(++now,{{"P1",tick(measured)}},[&](auto code,const auto* frame){need(code==v::SurfaceCode::ready||code==v::SurfaceCode::degraded,"chart paint");need(frame,"chart frame");out=*frame;});return out;}
    void empty(v::SurfaceCode expected){surface->paint(++now,{{"P1",tick(measured)}},[&](auto code,const auto* frame){need(code==expected&&!frame,"chart whole-scene outcome");});}
};
}
