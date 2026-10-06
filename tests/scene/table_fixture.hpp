#pragma once
#include "surface_fixture.hpp"
namespace fixture {
inline Json collection(std::string field="network.receive_bytes",unsigned limit=8){return {
    {"kind","selector"},{"scope",{{"kind","local_host"}}},{"entity_type","network.interface"},{"field",field},
    {"predicates",Json::array()},{"mode","collection"},{"sort",Json::array()},{"limit",limit}};}
inline v::SurfaceConfig table_config(const std::string& root,const Json& theme_changes=Json::object()){auto cfg=config(root,theme_changes);auto& w=cfg.authored.scene["widgets"][0];
    w["kind"]="table";w["title"]="Interfaces";w["bindings"]={collection(),collection("network.transmit_bytes")};
    w["layout"]["base"]["width"]=800;w["layout"]["base"]["height"]=600;return cfg;}
inline Json table_document(std::uint64_t value=123,std::uint64_t generation=1){
    n::NetworkState state("E1","clock:1","scope:1");state.demand(1);
    need(state.commit(1,0,{syspane::platform::NetworkCode::success,0,{
        {9,9,6,syspane::platform::NetworkCounters{value,7}},
        {10,10,6,syspane::platform::NetworkCounters{124,8}}}},tick(),tick())==n::NetworkStateCode::accepted,"table fixture source");
    return n::network_document(*state.sample(),generation,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
}
inline void table_prepare(Owner& f,const std::string& root){f.cfg=table_config(root);f.surface->replace(f.cfg,0);f.attach();}
}
