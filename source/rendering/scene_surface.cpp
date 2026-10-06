#include "scene_surface.hpp"
#include "scene_table.hpp"
#include <algorithm>
#include <cmath>
#include <limits>

namespace syspane::rendering {
namespace {
namespace c=configuration;namespace s=scene;namespace r=recovery;namespace m=model;
using protocol::Json;using protocol::Error;
void need(bool b,const char* code){if(!b)throw Error(code);}
struct Busy {bool& flag;explicit Busy(bool& f):flag(f){flag=true;}~Busy(){flag=false;}};
const char* support(m::Support v){return v==m::Support::supported?"supported":v==m::Support::unsupported?"unsupported":"unknown";}
const char* acquisition(m::Acquisition v){switch(v){case m::Acquisition::success:return "success";case m::Acquisition::pending:return "pending";case m::Acquisition::failed:return "failed";case m::Acquisition::denied:return "denied";default:return "disabled";}}
const char* freshness(m::Freshness v){switch(v){case m::Freshness::current:return "current";case m::Freshness::stale:return "stale";case m::Freshness::unknown:return "unknown";default:return "not_applicable";}}
const char* presence(m::Presence v){return v==m::Presence::present?"present":v==m::Presence::absent?"absent":"unknown";}
const char* origin(m::Origin v){return v==m::Origin::observed?"observed":v==m::Origin::derived?"derived":"configured";}
const char* lease(r::Presentation v){switch(v){case r::Presentation::active:return "active";case r::Presentation::retained:return "retained";case r::Presentation::waiting:return "waiting";default:return "empty";}}
std::string value(const m::Value& v){
    if(const auto* p=std::get_if<std::string>(&v))return *p;
    if(const auto* p=std::get_if<bool>(&v))return *p?"true":"false";
    if(const auto* p=std::get_if<std::uint64_t>(&v))return std::to_string(*p);
    if(const auto* p=std::get_if<double>(&v)){need(std::isfinite(*p),"surface.value");return Json(*p).dump();}
    return "—";
}
const char* outcome(s::BindingCode code){switch(code){
    case s::BindingCode::pending:return "Waiting";case s::BindingCode::empty:return "No matching entity";
    case s::BindingCode::denied:return "Restricted";case s::BindingCode::unsupported:return "Unsupported field";
    case s::BindingCode::ambiguous:return "Ambiguous selection";case s::BindingCode::capacity:return "Capacity exceeded";
    default:return "Invalid source";
}}
SurfaceText text(const Json& w,const s::BindingFrame* frame){
    SurfaceText out;out.id=w["id"];out.kind=w["kind"];const auto title=w["title"].get<std::string>();
    if(out.kind=="group"){out.accessible=title;return out;}
    if(out.kind=="text"){out.text=out.accessible=w.contains("content")?w["content"]["body"].get<std::string>():title;return out;}
    out.text=title+"\n";
    need(frame!=nullptr,"surface.frame");
    if(frame->code==s::BindingCode::denied)throw Error("policy.denied");
    if(frame->code!=s::BindingCode::matched){out.text+=outcome(frame->code);out.accessible=out.text;return out;}
    need(frame->rows.size()==1&&!frame->truncated,"surface.unsupported");
    const auto& row=frame->rows[0];
    if(row.code==s::BindingCode::denied)throw Error("policy.denied");
    if(row.code!=s::BindingCode::matched){out.text+=outcome(row.code);out.accessible=out.text;return out;}
    const auto& o=row.observation;out.text+=value(o.value);
    if(!o.unit.empty()&&o.unit!="1")out.text+=" "+o.unit;
    std::vector<std::string> states;
    if(row.presentation==r::Presentation::retained)states.emplace_back("Retained");
    if(row.effective==m::Freshness::stale)states.emplace_back("Stale");
    if(row.effective==m::Freshness::unknown)states.emplace_back("Freshness unknown");
    if(o.acquisition==m::Acquisition::pending)states.emplace_back("Pending");
    if(o.acquisition==m::Acquisition::denied)states.emplace_back("Access denied");
    if(o.acquisition==m::Acquisition::failed)states.emplace_back("Source failed"+(o.error?" ("+o.error->code+")":""));
    if(o.acquisition==m::Acquisition::disabled)states.emplace_back("Disabled");
    if(o.presence==m::Presence::absent)states.emplace_back("Absent");
    if(o.presence==m::Presence::unknown)states.emplace_back("Presence unknown");
    if(o.support==m::Support::unsupported)states.emplace_back("Unsupported");
    if(o.support==m::Support::unknown)states.emplace_back("Support unknown");
    if(o.origin==m::Origin::derived)states.emplace_back("Derived");
    if(o.origin==m::Origin::configured)states.emplace_back("Configured");
    if(states.empty())states.emplace_back("Current");
    out.text+='\n';for(std::size_t i=0;i<states.size();++i){if(i)out.text+=" | ";out.text+=states[i];}
    out.accessible=out.text+"\nsupport="+support(o.support)+"; acquisition="+acquisition(o.acquisition)+"; presence="+presence(o.presence)+
        "; freshness="+freshness(row.effective)+"; origin="+origin(o.origin)+"; lease="+lease(row.presentation)+
        "; age="+(row.age_ns?std::to_string(*row.age_ns)+" ns":"unknown");
    return out;
}
const s::Display& display_for(const Json& widget,const s::Topology& topology){
    std::string id=topology.fallback;const auto& assignment=widget["display"];
    if(assignment.contains("local_id"))id=assignment["local_id"];
    else{
        const auto found=topology.roles.find(assignment["role"].get<std::string>());std::set<std::string> present;
        if(found!=topology.roles.end())for(const auto& candidate:found->second)
            for(const auto& d:topology.displays)if(d.id==candidate)present.insert(candidate);
        if(present.size()==1)id=*present.begin();
    }
    for(const auto& d:topology.displays)if(d.id==id)return d;
    for(const auto& d:topology.displays)if(d.id==topology.fallback)return d;
    throw Error("surface.display");
}
void validate(const SurfaceConfig& cfg){
    need(cfg.resources!=nullptr,"surface.resources");c::validate_resource_binding(*cfg.resources,cfg.authored);
    std::map<std::string,s::Metrics> metrics;
    for(const auto& w:cfg.authored.scene["widgets"])if(w["kind"]!="group")metrics[w["id"]]={{64,64},{64,64}};
    (void)s::resolve(cfg.authored.scene,cfg.topology,metrics);
    TextRequest q;q.theme=cfg.resources->theme();q.language=cfg.language;q.contrast=cfg.contrast;(void)render_text(q);
}
}
struct SceneSurface::Impl {
    struct Entry {SurfaceProvider declaration;std::unique_ptr<r::DataView> view;};
    c::Authority authority;c::Policy policy;SurfaceConfig config;std::vector<Entry> entries;
    std::function<bool()> clear;std::unique_ptr<SurfaceFrame> frame;SurfaceStatus status;
    std::optional<std::uint64_t> highest,last_time;bool busy=false,closed=false;
    void owner()const{if(busy)throw std::logic_error("surface.reentrant");}
    bool erase(){
        frame.reset();status.widgets=status.pixels=0;
        if(closed)return false;
        bool ok=false;
        try{Busy guard(busy);ok=clear();}catch(...){ok=false;}
        if(!ok){closed=true;entries.clear();status={SurfaceCode::closed,0,0,"surface.clear"};}
        else status={SurfaceCode::empty,0,0,{}};
        return ok;
    }
    void shut(const char* why){erase();closed=true;entries.clear();status={SurfaceCode::closed,0,0,why};}
    bool advance(std::uint64_t now){owner();if(closed)return false;if(last_time&&now<*last_time){shut("surface.clock");return false;}last_time=now;return true;}
    bool start(std::uint64_t now){return advance(now)&&erase();}
    Entry& entry(const std::string& id){for(auto& e:entries)if(e.declaration.producer==id)return e;throw Error("surface.producer");}
    bool allowed()const{return policy.available&&!policy.denied_capabilities.count("telemetry.subscribe")&&
        c::permits(authority,policy,"desktop","operational")&&c::permits(authority,policy,"accessibility","operational");}
    std::vector<s::BindingInput> inputs(const std::map<std::string,m::Tick>& ticks){
        std::vector<s::BindingInput> in;
        for(auto& e:entries){const auto& d=e.declaration;s::BindingInput v;v.view=e.view.get();v.producer=d.producer;v.scope=d.scope;
            v.entity_types=d.types;v.fields=d.fields;v.pins=d.pins;const auto found=ticks.find(d.producer);if(found!=ticks.end())v.now=found->second;in.push_back(std::move(v));}
        return in;
    }
    std::unique_ptr<SurfaceFrame> compose(std::uint64_t now,const std::map<std::string,m::Tick>& ticks){
        c::authorize_resources(*config.resources,policy,config.capabilities);
        if(policy.forced.count("display.theme_id"))need(policy.forced.at("display.theme_id")==config.resources->theme()["theme_id"],"surface.theme_policy");
        auto next=std::make_unique<SurfaceFrame>();next->theme_pin=config.resources->theme_pin();
        std::size_t display_pixels=0,leaf_pixels=0,text_bytes=0,queries=0;
        for(const auto& d:config.topology.displays){
            const auto pixels=[&](s::Unit u){return (u*d.scale_numerator+64*d.scale_denominator-1)/(64*d.scale_denominator);};
            const auto w=pixels(d.bounds.width),h=pixels(d.bounds.height);need(w<=2048&&h<=2048,"surface.capacity");
            display_pixels+=static_cast<std::size_t>(w*h);need(display_pixels<=4194304,"surface.capacity");
            SurfacePixels p;p.display=d.id;p.x=d.pixel_x;p.y=d.pixel_y;p.width=static_cast<unsigned>(w);p.height=static_cast<unsigned>(h);next->displays.push_back(std::move(p));
        }
        const auto catalog=inputs(ticks);std::map<std::string,TextRaster> rasters;std::map<std::string,s::Metrics> metrics;std::map<std::string,SurfaceText> texts;
        for(const auto& w:config.authored.scene["widgets"]){
            const auto kind=w["kind"].get<std::string>();const bool bound=kind=="value"||kind=="status";
            const bool table=kind=="table";
            need(bound||table||kind=="text"||kind=="group","surface.unsupported");
            if(!table)need(w["bindings"].size()==(bound?1u:0u),"surface.unsupported");
            queries+=w["bindings"].size();need(queries<=256,"surface.capacity");
            SurfaceText out;
            if(table){out=compose_table(w,catalog,now,[](const s::BindingRow& row){
                    s::BindingFrame frame;frame.code=s::BindingCode::matched;frame.rows.push_back(row);
                    const auto cell=text({{"id","cell"},{"kind","value"},{"title",""}},&frame);
                    return SurfaceCell{cell.text.substr(1),cell.accessible.substr(1),{}};
                });
            }else if(bound){const auto& b=w["bindings"][0];need(b["kind"]!="selector"||b["mode"]=="singleton","surface.unsupported");
                s::project_binding(b,catalog,now,[&](const auto& f){out=text(w,&f);});
            }else out=text(w,nullptr);
            text_bytes+=surface_text_bytes(out);need(text_bytes<=262144,"surface.capacity");
            if(kind!="group"){
                const auto& d=display_for(w,config.topology);TextRequest q;q.text=out.text;q.theme=config.resources->theme();q.language=config.language;q.contrast=config.contrast;
                q.numerator=d.scale_numerator;q.denominator=d.scale_denominator;q.pixel_budget=std::min(std::size_t{4194304},8388608-display_pixels-leaf_pixels);
                need(q.pixel_budget>0,"surface.capacity");auto raster=table?raster_table(q,out,8388608-display_pixels-leaf_pixels):render_text(q);need(!raster.missing_glyphs,"surface.glyphs");
                leaf_pixels+=static_cast<std::size_t>(raster.width)*raster.height;out.fonts=raster.fonts;
                for(const auto& family:out.fonts){text_bytes+=family.size();}
                need(text_bytes<=262144,"surface.capacity");
                const auto units=[&](unsigned p){return (static_cast<s::Unit>(p)*64*d.scale_denominator+d.scale_numerator-1)/d.scale_numerator;};
                const s::Size size{units(raster.width),units(raster.height)};metrics[out.id]={size,size};rasters.emplace(out.id,std::move(raster));
            }
            texts.emplace(out.id,std::move(out));
        }
        next->layout=s::resolve(config.authored.scene,config.topology,metrics);need(next->layout.state!=s::State::alternative,"surface.layout");
        for(auto& d:next->displays)d.rgba.resize(static_cast<std::size_t>(d.width)*d.height*4);
        for(const auto& node:next->layout.nodes){
            next->widgets.push_back(std::move(texts.at(node.id)));if(node.kind=="group")continue;
            auto& raster=rasters.at(node.id);auto found=std::find_if(next->displays.begin(),next->displays.end(),[&](const auto& d){return d.display==node.display;});
            need(found!=next->displays.end(),"surface.display");auto& d=*found;const auto x=node.pixels.x-d.x,y=node.pixels.y-d.y;
            need(x>=0&&y>=0&&x+raster.width<=d.width&&y+raster.height<=d.height,"surface.layout");
            for(unsigned row=0;row<raster.height;++row)for(unsigned col=0;col<raster.width;++col){
                const auto src=(static_cast<std::size_t>(row)*raster.width+col)*4;
                const auto dst=(static_cast<std::size_t>(y+row)*d.width+static_cast<std::size_t>(x+col))*4;
                const auto inverse=255-raster.rgba[src+3];
                for(unsigned channel=0;channel<4;++channel)d.rgba[dst+channel]=static_cast<unsigned char>(raster.rgba[src+channel]+(d.rgba[dst+channel]*inverse+127)/255);
            }
        }
        return next;
    }
};
SceneSurface::SceneSurface(c::Authority authority,c::Policy policy,SurfaceConfig config,std::vector<SurfaceProvider> providers,std::function<bool()> clear_native):impl_(std::make_unique<Impl>()){
    validate(config);need(static_cast<bool>(clear_native)&&providers.size()<=16,"surface.input");auto& i=*impl_;
    i.authority=std::move(authority);i.policy=std::move(policy);i.config=std::move(config);i.clear=std::move(clear_native);if(i.policy.available)i.highest=i.policy.revision;
    std::set<std::string> ids;
    for(auto& p:providers){need(protocol::identifier(p.producer)&&ids.insert(p.producer).second,"surface.producer");
        auto view=std::make_unique<r::DataView>(i.authority,i.policy,"desktop","operational",p.metrics);i.entries.push_back({std::move(p),std::move(view)});}
    s::project_binding({{"kind","direct"},{"producer_id","validation"},{"producer_epoch","validation"},{"entity_id","validation"},{"field","entity.id"}},i.inputs({}),0,[](const auto&){});
}
SceneSurface::~SceneSurface(){try{close();}catch(...){}}
r::DataAttachment SceneSurface::attach(const std::string& producer,const protocol::TelemetryBinding& binding,std::uint64_t now){
    auto& i=*impl_;if(!i.start(now))return {r::DataCode::closed};need(producer==binding.producer,"surface.producer");return i.entry(producer).view->attach_wire(binding,now);
}
r::DataResult SceneSurface::receive(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::string_view bytes,std::uint64_t now,const m::Tick& tick){
    auto& i=*impl_;if(!i.start(now))return {r::DataCode::closed};return i.entry(producer).view->receive(token,revision,bytes,now,tick);
}
r::DataCode SceneSurface::heartbeat(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now){
    auto& i=*impl_;if(!i.start(now))return r::DataCode::closed;return i.entry(producer).view->heartbeat(token,revision,sequence,now);
}
r::DataCode SceneSurface::gap(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t now){auto& i=*impl_;if(!i.start(now))return r::DataCode::closed;return i.entry(producer).view->gap(token,revision,now);}
r::DataCode SceneSurface::disconnect(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t now){auto& i=*impl_;if(!i.start(now))return r::DataCode::closed;return i.entry(producer).view->disconnect(token,revision,now);}
void SceneSurface::policy(c::Policy next,std::uint64_t now){
    auto& i=*impl_;if(!i.start(now))return;const bool valid=!next.available||!i.highest||next.revision>*i.highest;
    if(next.available&&valid)i.highest=next.revision;
    if(!valid)next.available=false;
    for(auto& e:i.entries)e.view->policy(next,now);
    i.policy=std::move(next);i.status.code=i.allowed()?SurfaceCode::empty:SurfaceCode::restricted;
}
void SceneSurface::replace(SurfaceConfig config,std::uint64_t now){auto& i=*impl_;if(!i.start(now))return;validate(config);i.config=std::move(config);}
void SceneSurface::close(){auto& i=*impl_;i.owner();if(!i.closed)i.shut("surface.closed");}
SurfaceStatus SceneSurface::status()const{impl_->owner();return impl_->status;}
void SceneSurface::paint(std::uint64_t now,const std::map<std::string,m::Tick>& ticks,const std::function<void(SurfaceCode,const SurfaceFrame*)>& sink){
    auto& i=*impl_;i.owner();need(static_cast<bool>(sink),"surface.sink");
    if(i.start(now)){
        if(!i.allowed())i.status={SurfaceCode::restricted,0,0,"policy.denied"};
        else if(!(i.policy.forced.count("display.enabled")?i.policy.forced.at("display.enabled")==true:
                  i.config.authored.settings["display"]["enabled"].get<bool>()))i.status={SurfaceCode::empty,0,0,{}};
        else try{
            i.frame=i.compose(now,ticks);i.status.code=i.frame->layout.state==s::State::ready?SurfaceCode::ready:SurfaceCode::degraded;
            i.status.widgets=i.frame->widgets.size();for(const auto& d:i.frame->displays)i.status.pixels+=static_cast<std::size_t>(d.width)*d.height;
        }catch(const Error& e){i.frame.reset();i.status={std::string(e.what())=="policy.denied"?SurfaceCode::restricted:SurfaceCode::alternative,0,0,e.what()};}
        catch(const std::bad_alloc&){i.frame.reset();i.status={SurfaceCode::alternative,0,0,"surface.capacity"};}
    }
    Busy guard(i.busy);sink(i.status.code,i.frame.get());
}
}
