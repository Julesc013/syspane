#pragma once
#include "chart_fixture.hpp"
#include "scene_inspector_model.hpp"
#include "scene_table.hpp"
#include <iostream>

namespace chart_frame_limits {
using namespace fixture;
namespace ui=syspane::interfaces;
inline Json rows(const std::vector<ui::InspectorRow>& input){
    auto out=Json::array();for(const auto& r:input)out.push_back({{"key",r.key},{"item",r.item},{"information",r.information},{"children",rows(r.children)}});return out;
}
inline const char* code(v::SurfaceCode value){switch(value){case v::SurfaceCode::ready:return "ready";case v::SurfaceCode::degraded:return "degraded";
    case v::SurfaceCode::empty:return "empty";case v::SurfaceCode::restricted:return "restricted";case v::SurfaceCode::alternative:return "alternative";default:return "closed";}}
inline int run(const std::string& root,bool mixed,unsigned fitting,const std::string& group){
    static_assert(sizeof(s::ChartPoint)==40,"This experiment requires the pinned Linux x86-64 ChartPoint ABI");
    need(fitting>1&&fitting<4096,"chart boundary argument");
    need(group=="boundary"||group=="maximum"||group=="eviction","chart group argument");
    auto cfg=chart_config(root,{{"font",{{"family","Noto Sans"},{"size_dip",9}}}});
    auto& chart=cfg.authored.scene["widgets"][0];chart["content"]["window_ms"]=10000;chart["content"]["max_points"]=4096;
    chart["layout"]["base"]["x"]=1280;chart["layout"]["base"]["width"]=320;
    cfg.topology.displays[0].bounds=cfg.topology.displays[0].work={0,0,1600*64,2048*64};
    std::vector<v::SurfaceProvider> providers{provider()};
    if(mixed){auto table=widget("table","table","Interfaces");table["bindings"]=Json::array();table["content"]={{"columns",Json::array()}};
        const std::vector<std::pair<std::string,std::string>> columns={{"network.receive_bytes","Rx"},{"network.transmit_bytes","Tx"},{"entity.id","Identity"},{"entity.kind","Kind"}};
        for(const auto& pair:columns){auto b=collection(pair.first,64);b["scope"]={{"kind","registered_asset"},{"asset_id","lab:table"}};table["bindings"].push_back(b);table["content"]["columns"].push_back({{"label",pair.second}});}
        table["layout"]["base"]["width"]=1280;table["layout"]["base"]["height"]=2048;
        cfg.authored.scene["widgets"].push_back(table);cfg.authored.scene["roots"].push_back("table");
        auto p=provider();p.producer="P2";p.scope.kind="registered_asset";p.scope.asset="lab:table";providers.push_back(std::move(p));}
    std::uint64_t now=0,revision=7,measured=0,table_token=0,sequence=0;unsigned clears=0;std::string last_bytes;
    v::SceneSurface owner({true,"desktop",{"desktop"}},chart_policy(),cfg,providers,[&]{++clears;return true;});
    const auto continuous=[](std::uint64_t rev){auto b=link(rev);b.negotiated.features.insert("telemetry.monotonic-replay");return b;};
    auto l=continuous(revision);auto token=owner.attach("P1",l,++now).token;need(token!=0,"chart limits attachment");
    const auto table_full=[&]{if(!mixed)return;auto t=continuous(revision);t.producer="P2";table_token=owner.attach("P2",t,++now).token;need(table_token!=0,"table limits attachment");
        n::NetworkState state("E1","clock:1","scope:1");state.demand(1);syspane::platform::NetworkResult input{syspane::platform::NetworkCode::success,0,{}};
        for(unsigned i=1;i<=64;++i)input.rows.push_back({i,i,6,syspane::platform::NetworkCounters{10,7}});
        need(state.commit(1,0,std::move(input),tick(0),tick(0))==n::NetworkStateCode::accepted,"maximum table input");
        auto doc=n::network_document(*state.sample(),1,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
        Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","P2"},{"record_id","sample:1"},{"policy_revision",std::to_string(revision)},{"clock_id","clock:1"},{"snapshot",doc}};
        const auto bytes=p::encode_telemetry({"snapshot","D","E1",body.dump(),body},t);
        need(owner.receive("P2",table_token,revision,bytes,++now,tick(0),{{"P1",tick(measured)}}).code==r::DataCode::accepted,"maximum table admission");};
    const auto full=[&](unsigned generation,std::uint64_t ns){measured=ns;auto body=p::Json{{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","P1"},{"record_id","sample:"+std::to_string(generation)},
            {"policy_revision",std::to_string(revision)},{"clock_id","clock:1"},{"snapshot",chart_document(10,generation,ns)}};
        const auto bytes=p::encode_telemetry({"snapshot","D","E1",body.dump(),body},l);
        last_bytes=bytes;
        const auto result=owner.receive("P1",token,revision,bytes,++now,tick(ns),mixed?std::map<std::string,m::Tick>{{"P2",tick(0)}}:std::map<std::string,m::Tick>{});
        if(result.code!=r::DataCode::accepted){std::cout<<Json({{"case","ADMISSION-FAILURE"},{"generation",generation},{"data_code",static_cast<int>(result.code)},
            {"model_code",result.validation?m::code_name(*result.validation):"none"}}).dump()<<'\n';
            throw std::runtime_error("chart limits admission generation="+std::to_string(generation)+" code="+std::to_string(static_cast<int>(result.code))+" validation="+(result.validation?m::code_name(*result.validation):"none"));}};
    const auto paint=[&](const char* name){Json record={{"case",name},{"point_bytes",sizeof(s::ChartPoint)}};
        auto ticks=std::map<std::string,m::Tick>{{"P1",tick(measured)}};if(mixed)ticks.emplace("P2",tick(0));
        owner.paint(++now,ticks,[&](auto status,const auto* frame){record["code"]=code(status);record["frame"]=nullptr;if(!frame)return;
            Json result={{"widgets",Json::array()},{"rows",rows(ui::inspector_rows(*frame))},{"display_pixels",0}};
            for(const auto& d:frame->displays)result["display_pixels"]=result["display_pixels"].get<std::size_t>()+static_cast<std::size_t>(d.width)*d.height;
            for(const auto& w:frame->widgets){Json item={{"id",w.id},{"kind",w.kind},{"title",w.title},{"text",w.text},{"accessible",w.accessible},{"fonts",w.fonts},{"bytes",v::surface_text_bytes(w)}};
                if(w.chart){item["summary"]=w.chart->summary;item["accessible_summary"]=w.chart->accessible_summary;item["points"]=Json::array();
                    for(const auto& point:w.chart->points)item["points"].push_back({{"measured_ns",point.measured_ns},{"generation",point.generation},{"value",std::get<std::uint64_t>(point.value)},{"joins_previous",point.joins_previous}});}
                result["widgets"].push_back(std::move(item));}
            record["frame"]=std::move(result);});record["reason"]=owner.status().reason;record["clears"]=clears;std::cout<<record.dump()<<'\n';};
    table_full();
    const auto count=group=="boundary"?fitting+1:group=="maximum"?4096U:4097U;
    for(unsigned g=1;g<=count;++g){full(g,static_cast<std::uint64_t>(g-1)*1000000);
        if(g%1000==0){++sequence;need(owner.heartbeat("P1",token,revision,sequence,++now)==r::DataCode::accepted,"chart heartbeat");
            if(mixed)need(owner.heartbeat("P2",table_token,revision,sequence,++now)==r::DataCode::accepted,"table heartbeat");}
        if(group=="boundary"&&g==fitting)paint("FIT");
        if(g==count)paint(group=="boundary"?"OVER":group=="maximum"?"MAX":"EVICT");}
    need(owner.receive("P1",token,revision,last_bytes,++now,tick(measured),mixed?std::map<std::string,m::Tick>{{"P2",tick(0)}}:std::map<std::string,m::Tick>{}).code==r::DataCode::duplicate,"blocked duplicate");
    need(owner.heartbeat("P1",token,revision,++sequence,++now)==r::DataCode::accepted,"blocked heartbeat");
    paint("RETRY-BLOCKED");full(4098,20000000000ULL);paint("RECOVER");
    auto revoked=chart_policy(8);revoked.disclosure.erase({"desktop","history"});owner.policy(revoked,++now);paint("REVOKE");
    revision=9;owner.policy(chart_policy(revision),++now);paint("REGRANT");l=continuous(revision);token=owner.attach("P1",l,++now).token;need(token!=0,"fresh chart attachment");
    table_full();full(4099,21000000000ULL);paint("FRESH");owner.close();paint("CLOSE");return 0;
}
}
