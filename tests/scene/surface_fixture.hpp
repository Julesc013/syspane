#pragma once
#include "scene_surface.hpp"
#include "network_publication.hpp"
#include "digest.hpp"
#include <fstream>
#include <stdexcept>
namespace fixture {
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace m=syspane::model;
namespace s=syspane::scene;namespace v=syspane::rendering;namespace r=syspane::recovery;namespace n=syspane::runtime;
using p::Json;
inline void need(bool b,const char* why){if(!b)throw std::runtime_error(why);}
inline Json read(const std::string& root,const char* name){std::ifstream f(root+"/"+name);need(f.good(),"fixture file");Json j;f>>j;return j;}
inline c::Policy policy(std::uint64_t revision=7,bool permit=true){c::Policy p;p.available=true;p.revision=revision;if(permit){p.disclosure[{"desktop","desktop"}]={"operational"};p.disclosure[{"desktop","accessibility"}]={"operational"};}return p;}
inline c::ContentPackage pack(const std::string& id,const std::string& kind,const Json& doc,Json deps=Json::array()){
    const auto b=doc.dump()+"\n";Json manifest={{"schema_version","0.1.0"},{"package_id",id},{"version","0.1.0"},{"kind",kind},{"license","MIT"},{"dependencies",deps},
        {"assets",Json::array({{{"path",kind+".json"},{"media_type","application/json"},{"sha256",c::sha256(b)},{"bytes",b.size()}}})},
        {"total_unpacked_bytes",b.size()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    return {manifest.dump()+"\n",{{kind+".json",b}}};
}
inline Json package_pin(const c::ContentPackage& p){auto j=Json::parse(p.manifest);return {{"id",j["package_id"]},{"version","0.1.0"},{"sha256",c::sha256(p.manifest)}};}
inline Json document_pin(const c::ContentPackage& p){auto j=Json::parse(p.manifest);auto kind=j["kind"].get<std::string>();const auto& b=p.assets.at(kind+".json");return {{"id",Json::parse(b)[kind+"_id"]},{"version","0.1.0"},{"sha256",c::sha256(b)}};}
inline Json binding(){return {{"kind","direct"},{"producer_id","P1"},{"producer_epoch","E1"},{"entity_id","network:interface:1"},{"field","network.receive_bytes"}};}
inline Json widget(std::string id="value",std::string kind="value",std::string title="Receive"){
    return {{"id",id},{"kind",kind},{"title",title},{"display",{{"local_id","D1"}}},
        {"layout",{{"base",{{"kind","fixed"},{"x",0},{"y",0},{"width",320},{"height",180}}}}},
        {"bindings",kind=="text"?Json::array():Json::array({binding()})},{"priority","normal"}};
}
inline v::SurfaceConfig config(const std::string& root,const Json& theme_changes=Json::object()){
    v::SurfaceConfig c;c.authored.settings=read(root,"settings.json");c.authored.settings["revision"]="40";
    c.authored.scene={{"schema_version","0.2.0"},{"revision","40"},{"scene_id","scene:surface"},{"theme_id","theme:native"},{"roots",Json::array({"value"})},{"widgets",Json::array({widget()})}};
    auto theme=read(root,"theme.json");theme["font"]={{"family","Noto Sans"},{"size_dip",24}};
    theme["tokens"]={{"foreground","#ffffffff"},{"background","#00000000"},{"warning","#ffcf4aff"},{"error","#ff8080ff"},{"muted","#d0d0d0ff"}};
    for(auto it=theme_changes.begin();it!=theme_changes.end();++it)theme[it.key()]=it.value();
    auto t=pack("package:theme","theme",theme),sc=pack("package:scene","scene",c.authored.scene);
    Json preset={{"schema_version","0.1.0"},{"preset_id","preset:surface"},{"version","0.1.0"},{"parent",nullptr},{"scene",document_pin(sc)},{"theme",document_pin(t)},
        {"settings",Json::array()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    auto pr=pack("package:preset","preset",preset,Json::array({package_pin(t),package_pin(sc)}));
    c.resources=c::ContentCatalog({t,sc,pr}).resources({{"package",package_pin(pr)},{"preset",document_pin(pr)}},c.authored);
    s::Display d;d.id="D1";d.bounds=d.work={0,0,800*64,600*64};c.topology={{d},{},"D1"};c.capabilities={"scene.selector"};return c;
}
inline v::SurfaceProvider provider(){v::SurfaceProvider p;p.producer="P1";p.types={"network.interface"};p.metrics=n::network_metrics();for(const auto& f:p.metrics)p.fields[f.field]=3000000000ULL;return p;}
inline m::Tick tick(std::uint64_t now=100,std::string epoch="E1"){return {epoch,now,"clock:1","scope:1"};}
inline p::TelemetryBinding link(std::uint64_t revision=7,std::string epoch="E1"){
    return {{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},
        {"telemetry.snapshot","telemetry.measured-time"}},"D",epoch,"P1","S","desktop","operational",revision,p::TelemetryDirection::producer_to_consumer,"0.2.0","clock:1","scope:1"};
}
inline Json document(std::uint64_t value=123,std::uint64_t generation=1){
    n::NetworkState state("E1","clock:1","scope:1");state.demand(1);
    need(state.commit(1,0,{syspane::platform::NetworkCode::success,0,{{9,9,6,syspane::platform::NetworkCounters{value,0}}}},tick(),tick())==n::NetworkStateCode::accepted,"fixture source");
    auto doc=n::network_document(*state.sample(),generation,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);return doc;
}
inline std::string wire(Json doc,const p::TelemetryBinding& l){Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","P1"},{"record_id","R"+doc["generation"].get<std::string>()},
    {"policy_revision",std::to_string(l.policy_revision)},{"clock_id","clock:1"},{"snapshot",std::move(doc)}};
    return p::encode_telemetry({"snapshot","D",l.epoch,body.dump(),body},l);
}
struct Owner {
    unsigned clears=0;bool clear_ok=true;v::SurfaceConfig cfg;std::unique_ptr<v::SceneSurface> surface;std::uint64_t token=0;std::uint64_t revision=7;
    explicit Owner(const std::string& root,std::optional<m::ValueKind> custom={}):cfg(config(root)){
        auto declaration=provider();
        if(custom){declaration.metrics.push_back({"probe.value","1",*custom});declaration.fields["probe.value"]=3000000000ULL;cfg.authored.scene["widgets"][0]["bindings"][0]["field"]="probe.value";}
        surface=std::make_unique<v::SceneSurface>(c::Authority{true,"desktop",{"desktop"}},policy(),cfg,std::vector<v::SurfaceProvider>{declaration},[&]{++clears;return clear_ok;});
    }
    void attach(std::uint64_t now=0){token=surface->attach("P1",link(revision),now).token;need(token!=0,"fixture attach");}
    void receive(Json d=document(),std::uint64_t now=1){need(surface->receive("P1",token,revision,wire(std::move(d),link(revision)),now,tick()).code==r::DataCode::accepted,"fixture receive");}
    v::SurfaceFrame paint(std::uint64_t now=2,std::uint64_t measured=100){v::SurfaceFrame frame;unsigned calls=0;surface->paint(now,{{"P1",tick(measured)}},[&](auto code,const auto* f){++calls;need(code==v::SurfaceCode::ready||code==v::SurfaceCode::degraded,"fixture paint");need(f,"fixture payload");frame=*f;});need(calls==1,"one callback");return frame;}
};
}
