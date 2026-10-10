#include "scene_surface.hpp"
#include "scene_table.hpp"
#include "scene_chart.hpp"
#include "scene_image.hpp"
#include "scene_visibility.hpp"
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
SurfaceText text(const Json& w,const s::BindingFrame* frame,bool typography){
    SurfaceText out;out.id=w["id"];out.kind=w["kind"];const auto title=w["title"].get<std::string>();
    if(out.kind=="group"){out.accessible=title;return out;}
    if(out.kind=="text"){out.text=out.accessible=w.contains("content")?w["content"]["body"].get<std::string>():title;if(typography)out.blocks.push_back({"body",out.text});return out;}
    out.text=title+"\n";if(typography)out.blocks.push_back({"label",title});
    need(frame!=nullptr,"surface.frame");
    if(frame->code==s::BindingCode::denied)throw Error("policy.denied");
    if(frame->code!=s::BindingCode::matched){out.notices.push_back(outcome(frame->code));out.text+=out.notices.back();out.accessible=out.text;if(typography)out.blocks.push_back({"diagnostic",out.notices.back()});return out;}
    need(frame->rows.size()==1&&!frame->truncated,"surface.unsupported");
    const auto& row=frame->rows[0];
    if(row.code==s::BindingCode::denied)throw Error("policy.denied");
    if(row.code!=s::BindingCode::matched){out.notices.push_back(outcome(row.code));out.text+=out.notices.back();out.accessible=out.text;if(typography)out.blocks.push_back({"diagnostic",out.notices.back()});return out;}
    const auto& o=row.observation;out.text+=value(o.value);
    if(!o.unit.empty()&&o.unit!="1")out.text+=" "+o.unit;
    if(typography)out.blocks.push_back({"value",out.text.substr(title.size()+1)});
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
    std::string mandatory;for(const auto& state:states){if(!mandatory.empty())mandatory+=" | ";mandatory+=state;}if(!mandatory.empty())out.notices.push_back(mandatory);
    if(o.origin==m::Origin::derived)states.emplace_back("Derived");
    if(o.origin==m::Origin::configured)states.emplace_back("Configured");
    if(states.empty())states.emplace_back("Current");
    std::string state_text;for(std::size_t i=0;i<states.size();++i){if(i)state_text+=" | ";state_text+=states[i];}out.text+='\n'+state_text;
    if(typography)out.blocks.push_back({"diagnostic",state_text});
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
c::ValidatedAuthored validate(SurfaceConfig& cfg){
    need(cfg.resources!=nullptr,"surface.resources");
    auto validated=[&]{
        if(!cfg.authored_snapshot)return c::ValidatedAuthored(cfg.authored);
        need(cfg.authored.settings.is_null()&&cfg.authored.scene.is_null(),"surface.authored_source");
        return *cfg.authored_snapshot;
    }();
    c::validate_resource_binding(*cfg.resources,validated);
    std::map<std::string,s::Metrics> metrics;
    for(const auto& w:validated.documents().scene["widgets"])if(w["kind"]!="group")metrics[w["id"]]={{64,64},{64,64}};
    (void)s::resolve(validated,cfg.topology,metrics);
    TextRequest q;q.theme=cfg.resources->theme();q.language=cfg.language;q.contrast=cfg.contrast;(void)render_text(q);
    // Other composition helpers use SurfaceConfig. Detach its private copy from
    // any references into a caller's moved JSON and keep it equal to the proof.
    cfg.authored=validated.documents();cfg.authored_snapshot.reset();return validated;
}
}
struct SceneSurface::Impl {
    struct Entry {SurfaceProvider declaration;std::unique_ptr<r::DataView> view;};
    struct History {std::unique_ptr<s::ChartHistory> samples;std::optional<s::ChartCode> fault;};
    c::Authority authority;c::Policy policy;SurfaceConfig config;std::vector<Entry> entries;std::string channel;
    std::optional<c::ValidatedAuthored> validated;
    std::function<bool()> clear;std::unique_ptr<SurfaceFrame> frame;SurfaceStatus status;
    std::optional<std::uint64_t> highest,last_time;bool busy=false,closed=false;
    std::map<std::string,History> histories;std::unique_ptr<SceneImages> images;
    void owner()const{if(busy)throw std::logic_error("surface.reentrant");}
    bool erase(){
        frame.reset();status.widgets=status.pixels=0;
        if(closed)return false;
        bool ok=false;
        try{Busy guard(busy);ok=clear();}catch(...){ok=false;}
        if(!ok){closed=true;images->clear();histories.clear();entries.clear();config={};validated.reset();status={SurfaceCode::closed,0,0,"surface.clear"};}
        else status={SurfaceCode::empty,0,0,{}};
        return ok;
    }
    void shut(const char* why){images->clear();histories.clear();erase();closed=true;entries.clear();config={};validated.reset();status={SurfaceCode::closed,0,0,why};}
    bool advance(std::uint64_t now){owner();if(closed)return false;if(last_time&&now<*last_time){shut("surface.clock");return false;}last_time=now;return true;}
    bool start(std::uint64_t now){if(!advance(now)||!erase())return false;
        for(auto& e:entries){const auto state=e.view->status(now);if(state.presentation==r::Presentation::retained||state.snapshot_required)discontinuity(e.declaration.producer,false);}
        return true;}
    Entry& entry(const std::string& id){for(auto& e:entries)if(e.declaration.producer==id)return e;throw Error("surface.producer");}
    bool charted()const{for(const auto& w:config.authored.scene["widgets"])if(w["kind"]=="chart"&&w.contains("content"))return true;return false;}
    bool allowed()const{return policy.available&&!policy.denied_capabilities.count("telemetry.subscribe")&&
        c::permits(authority,policy,channel,"operational")&&c::permits(authority,policy,"accessibility","operational")&&
        (!charted()||c::permits(authority,policy,"history","operational"));}
    bool uses(const Json& w,const std::string& producer){const auto& b=w["bindings"][0];if(b["kind"]=="direct")return b["producer_id"]==producer;
        if(b["kind"]=="unresolved_pin")return false;
        const auto& d=entry(producer).declaration;
        if(!d.types.count(b["entity_type"].get<std::string>())||b["scope"]["kind"]!=d.scope.kind)return false;
        return d.scope.kind!="registered_asset"||b["scope"]["asset_id"]==d.scope.asset;}
    void discontinuity(const std::string& producer,bool reset,std::optional<s::ChartCode> fault={}){
        for(const auto& w:config.authored.scene["widgets"])if(w["kind"]=="chart"){
            const auto found=histories.find(w["id"]);if(found==histories.end()||!uses(w,producer))continue;
            if(reset){found->second.samples->clear();found->second.fault=fault;}else found->second.samples->gap();}}
    void prepare_histories(){
        need(allowed(),"policy.denied");c::authorize_resources(*config.resources,policy,config.capabilities);
        need(config.resources->theme().at("schema_version")!="0.2.0"||config.experimental_typography,"surface.typography_unavailable");
        need(config.authored.scene["schema_version"]!="0.5.0"||config.experimental_visibility,"surface.visibility_unavailable");
        std::size_t count=0,points=0;for(const auto& w:config.authored.scene["widgets"])if(w["kind"]=="chart"){
            need(w.contains("content"),"surface.unsupported");++count;points+=w["content"]["max_points"].get<std::size_t>();}
        need(count<=32&&points<=16384,"surface.capacity");
        for(const auto& w:config.authored.scene["widgets"])if(w["kind"]=="chart"&&!histories.count(w["id"])){
            histories.emplace(w["id"].get<std::string>(),History{std::make_unique<s::ChartHistory>(w["content"]["window_ms"].get<std::uint64_t>(),w["content"]["max_points"].get<std::size_t>()),{}});}
    }
    void observe_chart(const Json& w,const s::BindingFrame& f,const std::map<std::string,m::Tick>& ticks,const std::function<void(const s::ChartView&)>& sink){
        auto& h=histories.at(w["id"].get<std::string>());std::optional<m::Tick> now;
        if(f.rows.size()==1){const auto found=ticks.find(f.rows[0].producer);if(found!=ticks.end())now=found->second;}
        if(h.fault){s::BindingFrame empty;h.samples->observe(empty,{},[&](auto v){v.code=*h.fault;sink(v);});}
        else h.samples->observe(f,now,sink);
    }
    void feed(const std::string& producer,std::uint64_t now,const std::map<std::string,m::Tick>& ticks){
        if(!charted())return;
        try{prepare_histories();const auto catalog=inputs(ticks);
            for(const auto& w:config.authored.scene["widgets"])if(w["kind"]=="chart"&&uses(w,producer))s::project_binding(w["bindings"][0],catalog,now,[&](const auto& f){observe_chart(w,f,ticks,[](const auto&){});});}
        catch(const Error&){histories.clear();}catch(const std::bad_alloc&){histories.clear();}
    }
    std::vector<s::BindingInput> inputs(const std::map<std::string,m::Tick>& ticks){
        std::vector<s::BindingInput> in;
        for(auto& e:entries){const auto& d=e.declaration;s::BindingInput v;v.view=e.view.get();v.producer=d.producer;v.scope=d.scope;
            v.entity_types=d.types;v.fields=d.fields;v.pins=d.pins;const auto found=ticks.find(d.producer);if(found!=ticks.end())v.now=found->second;in.push_back(std::move(v));}
        return in;
    }
    std::unique_ptr<SurfaceFrame> compose(std::uint64_t now,const std::map<std::string,m::Tick>& ticks){
        prepare_histories();
        // Font setup lives only until this composition returns (including failures).
        // Contexts and layouts remain independent for every request.
        TextSession text_session;
        if(policy.forced.count("display.theme_id"))need(policy.forced.at("display.theme_id")==config.resources->theme()["theme_id"],"surface.theme_policy");
        images->prepare(config);
        auto next=std::make_unique<SurfaceFrame>();next->theme_pin=config.resources->theme_pin();
        std::size_t display_pixels=0,leaf_pixels=0,text_bytes=0,queries=0,plot_work=0;
        for(const auto& d:config.topology.displays){
            const auto pixels=[&](s::Unit u){return (u*d.scale_numerator+64*d.scale_denominator-1)/(64*d.scale_denominator);};
            const auto w=pixels(d.bounds.width),h=pixels(d.bounds.height);need(w<=2048&&h<=2048,"surface.capacity");
            display_pixels+=static_cast<std::size_t>(w*h);need(display_pixels<=4194304,"surface.capacity");
            SurfacePixels p;p.display=d.id;p.x=d.pixel_x;p.y=d.pixel_y;p.width=static_cast<unsigned>(w);p.height=static_cast<unsigned>(h);next->displays.push_back(std::move(p));
        }
        const bool typography=config.resources->theme().at("schema_version")=="0.2.0";
        const auto catalog=inputs(ticks);std::map<std::string,TextRaster> rasters;std::map<std::string,s::Metrics> metrics;std::map<std::string,SurfaceText> texts;
        for(const auto& w:config.authored.scene["widgets"]){
            const auto kind=w["kind"].get<std::string>();const bool chart=kind=="chart",bound=kind=="value"||kind=="status"||chart;
            const bool table=kind=="table",image=kind=="image";
            need(bound||table||image||kind=="text"||kind=="group","surface.unsupported");
            if(!table)need(w["bindings"].size()==(bound?1u:0u),"surface.unsupported");
            queries+=w["bindings"].size();need(queries<=256,"surface.capacity");
            SurfaceText out;std::optional<s::ChartPlot> plot;
            if(table){std::vector<std::string> notices;out=compose_table(w,catalog,now,[&](const s::BindingRow& row){
                    s::BindingFrame frame;frame.code=s::BindingCode::matched;frame.rows.push_back(row);
                    auto cell=text({{"id","cell"},{"kind","value"},{"title",""}},&frame,typography);
                    for(const auto& line:cell.notices)if(std::find(notices.begin(),notices.end(),line)==notices.end())notices.push_back(line);
                    if(typography)cell.blocks.erase(cell.blocks.begin());
                    return SurfaceCell{cell.text.substr(1),cell.accessible.substr(1),{},std::move(cell.blocks)};
                });out.notices=std::move(notices);if(out.table->rows.empty())out.notices.push_back(out.table->summary=="Showing 0 of 0 rows"?"Table has no rows":out.table->summary);
            }else if(bound){const auto& b=w["bindings"][0];need(b["kind"]!="selector"||b["mode"]=="singleton","surface.unsupported");
                s::project_binding(b,catalog,now,[&](const auto& f){out=text(w,&f,typography);
                    if(chart){const auto& d=display_for(w,config.topology);const auto width=(320*d.scale_numerator+d.scale_denominator-1)/d.scale_denominator;
                        const auto height=(120*d.scale_numerator+d.scale_denominator-1)/d.scale_denominator;
                        need(static_cast<std::size_t>(width)*height<8388608-display_pixels-leaf_pixels,"surface.capacity");
                        observe_chart(w,f,ticks,[&](const auto& view){plot=compose_chart(w,out,view,f.rows.size()==1?f.rows[0].observation.unit:std::string(),width,height,4194304-plot_work);});plot_work+=plot->work;}
                });
            }else if(image){out.id=w["id"];out.kind=kind;}else out=text(w,nullptr,typography);
            if(kind!="group"){
                const auto& d=display_for(w,config.topology);TextRequest q;q.text=out.text;q.theme=config.resources->theme();q.language=config.language;q.contrast=config.contrast;
                q.numerator=d.scale_numerator;q.denominator=d.scale_denominator;q.pixel_budget=std::min(std::size_t{4194304},8388608-display_pixels-leaf_pixels);
                need(q.pixel_budget>0,"surface.capacity");auto raster=image?images->raster(w,q,out):chart?raster_chart(q,out,*plot,8388608-display_pixels-leaf_pixels,&text_session):table?raster_table(q,out,8388608-display_pixels-leaf_pixels,&text_session):typography?render_blocks(q,out.blocks,8388608-display_pixels-leaf_pixels,&text_session):render_text(q,&text_session);need(!raster.missing_glyphs,"surface.glyphs");
                leaf_pixels+=static_cast<std::size_t>(raster.width)*raster.height;out.fonts=raster.fonts;
                const auto units=[&](unsigned p){return (static_cast<s::Unit>(p)*64*d.scale_denominator+d.scale_numerator-1)/d.scale_numerator;};
                const s::Size size{units(raster.width),units(raster.height)};metrics[out.id]={size,size};rasters.emplace(out.id,std::move(raster));
            }
            out.title=w["title"];text_bytes+=surface_text_bytes(out);need(text_bytes<=262144,"surface.capacity");
            texts.emplace(out.id,std::move(out));
        }
        next->layout=s::resolve(*validated,config.topology,metrics);need(next->layout.state!=s::State::alternative,"surface.layout");
        condition_surface(config,catalog,now,*next,texts,rasters,display_pixels,leaf_pixels,&text_session);
        for(auto& d:next->displays)d.rgba.resize(static_cast<std::size_t>(d.width)*d.height*4);
        for(bool diagnostic:{false,true})
        for(const auto& node:next->layout.nodes){
            if(texts.at(node.id).diagnostic!=diagnostic||!rasters.count(node.id))continue;
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
        for(const auto& node:next->layout.nodes)next->widgets.push_back(std::move(texts.at(node.id)));
        return next;
    }
};
SceneSurface::SceneSurface(c::Authority authority,c::Policy policy,SurfaceConfig config,std::vector<SurfaceProvider> providers,std::function<bool()> clear_native,std::string image_worker,SurfaceAudience audience,ImageFactory images):impl_(std::make_unique<Impl>()){
    auto validated=validate(config);need(static_cast<bool>(clear_native)&&providers.size()<=16,"surface.input");auto& i=*impl_;
    need(audience==SurfaceAudience::desktop||audience==SurfaceAudience::inspector,"surface.audience");i.channel=audience==SurfaceAudience::desktop?"desktop":"inspector";
    i.images=images?std::make_unique<SceneImages>(std::move(images)):std::make_unique<SceneImages>(std::move(image_worker));i.authority=std::move(authority);i.policy=std::move(policy);i.config=std::move(config);i.clear=std::move(clear_native);if(i.policy.available)i.highest=i.policy.revision;
    i.validated=std::move(validated);
    std::set<std::string> ids;
    for(auto& p:providers){need(protocol::identifier(p.producer)&&ids.insert(p.producer).second,"surface.producer");
        auto view=std::make_unique<r::DataView>(i.authority,i.policy,i.channel,"operational",p.metrics);i.entries.push_back({std::move(p),std::move(view)});}
    s::project_binding({{"kind","direct"},{"producer_id","validation"},{"producer_epoch","validation"},{"entity_id","validation"},{"field","entity.id"}},i.inputs({}),0,[](const auto&){});
}
SceneSurface::~SceneSurface(){try{close();}catch(...){}}
r::DataAttachment SceneSurface::attach(const std::string& producer,const protocol::TelemetryBinding& binding,std::uint64_t now){
    auto& i=*impl_;if(!i.start(now))return {r::DataCode::closed};need(producer==binding.producer,"surface.producer");const auto result=i.entry(producer).view->attach_wire(binding,now);
    if(result.code==r::DataCode::accepted)i.discontinuity(producer,true);
    return result;
}
r::DataResult SceneSurface::receive(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::string_view bytes,std::uint64_t now,const m::Tick& tick,const std::map<std::string,m::Tick>& other_ticks){
    auto& i=*impl_;if(!i.start(now))return {r::DataCode::closed};const auto result=i.entry(producer).view->receive(token,revision,bytes,now,tick);
    if(result.code==r::DataCode::accepted||result.code==r::DataCode::duplicate){auto ticks=other_ticks;ticks[producer]=tick;i.feed(producer,now,ticks);}
    else if(result.code==r::DataCode::clock_fault)i.discontinuity(producer,true,s::ChartCode::clock_fault);
    else if(result.code!=r::DataCode::stale_attachment&&result.code!=r::DataCode::policy_changed)i.discontinuity(producer,false);
    return result;
}
r::DataCode SceneSurface::heartbeat(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now){
    auto& i=*impl_;if(!i.start(now))return r::DataCode::closed;return i.entry(producer).view->heartbeat(token,revision,sequence,now);
}
r::DataCode SceneSurface::gap(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t now){auto& i=*impl_;if(!i.start(now))return r::DataCode::closed;const auto code=i.entry(producer).view->gap(token,revision,now);if(code==r::DataCode::accepted)i.discontinuity(producer,false);return code;}
r::DataCode SceneSurface::disconnect(const std::string& producer,std::uint64_t token,std::uint64_t revision,std::uint64_t now){auto& i=*impl_;if(!i.start(now))return r::DataCode::closed;const auto code=i.entry(producer).view->disconnect(token,revision,now);if(code==r::DataCode::accepted)i.discontinuity(producer,false);return code;}
void SceneSurface::policy(c::Policy next,std::uint64_t now){
    auto& i=*impl_;if(!i.start(now))return;i.images->clear();i.histories.clear();const bool valid=!next.available||!i.highest||next.revision>*i.highest;
    if(next.available&&valid)i.highest=next.revision;
    if(!valid)next.available=false;
    for(auto& e:i.entries)e.view->policy(next,now);
    i.policy=std::move(next);i.status.code=i.allowed()?SurfaceCode::empty:SurfaceCode::restricted;
}
void SceneSurface::replace(SurfaceConfig config,std::uint64_t now){auto& i=*impl_;if(!i.start(now))return;i.images->clear();i.histories.clear();auto validated=validate(config);i.config=std::move(config);i.validated=std::move(validated);}
void SceneSurface::close(){auto& i=*impl_;i.owner();if(!i.closed)i.shut("surface.closed");}
bool SceneSurface::poll_image_jobs(){auto& i=*impl_;i.owner();try{return i.images->poll();}catch(const Error&){i.images->clear("surface.capacity");if(i.erase())i.status={SurfaceCode::alternative,0,0,"surface.capacity"};return true;}}
SurfaceStatus SceneSurface::status()const{impl_->owner();return impl_->status;}
void SceneSurface::paint(std::uint64_t now,const std::map<std::string,m::Tick>& ticks,const std::function<void(SurfaceCode,const SurfaceFrame*)>& sink){
    auto& i=*impl_;i.owner();need(static_cast<bool>(sink),"surface.sink");
    if(i.start(now)){
        if(!i.allowed()){i.images->clear();i.histories.clear();i.status={SurfaceCode::restricted,0,0,"policy.denied"};}
        else if((i.config.resources->theme().at("schema_version")!="0.2.0"||i.config.experimental_typography)&&(i.config.authored.scene["schema_version"]!="0.5.0"||i.config.experimental_visibility)&&!(i.policy.forced.count("display.enabled")?i.policy.forced.at("display.enabled")==true:
                  i.config.authored.settings["display"]["enabled"].get<bool>())){
            try{if(i.config.resources->theme().at("schema_version")=="0.2.0")c::authorize_resources(*i.config.resources,i.policy,i.config.capabilities);
                i.images->clear();i.status={SurfaceCode::empty,0,0,{}};
            }catch(const Error& e){i.images->clear();i.histories.clear();i.status={std::string(e.what())=="policy.denied"?SurfaceCode::restricted:SurfaceCode::alternative,0,0,e.what()};}}
        else try{
            i.frame=i.compose(now,ticks);i.status.code=i.frame->layout.state==s::State::ready?SurfaceCode::ready:SurfaceCode::degraded;
            for(const auto& w:i.frame->widgets)if(w.image&&w.image->state!="ready"){i.status.code=SurfaceCode::degraded;i.status.reason=w.image->state=="loading"?"image.pending":"image.failed";}
            for(const auto& w:i.frame->widgets)if(w.diagnostic){i.status.code=SurfaceCode::degraded;i.status.reason="visibility.diagnostic";}
            i.status.widgets=i.frame->widgets.size();for(const auto& d:i.frame->displays)i.status.pixels+=static_cast<std::size_t>(d.width)*d.height;
        }catch(const Error& e){i.images->clear(e.what());i.histories.clear();i.frame.reset();i.status={std::string(e.what())=="policy.denied"?SurfaceCode::restricted:SurfaceCode::alternative,0,0,e.what()};}
        catch(const std::bad_alloc&){i.images->clear("surface.capacity");i.histories.clear();i.frame.reset();i.status={SurfaceCode::alternative,0,0,"surface.capacity"};}
    }
    Busy guard(i.busy);sink(i.status.code,i.frame.get());
}
}
