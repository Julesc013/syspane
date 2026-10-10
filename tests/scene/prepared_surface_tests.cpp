#include "surface_fixture.hpp"
#include <iostream>
namespace {
using namespace fixture;
template<class F>void rejects(F f,const char* expected){bool caught=false;try{f();}catch(const p::Error& e){caught=true;need(std::string(e.what())==expected,"prepared surface rejection");}need(caught,"missing prepared surface rejection");}
v::SurfaceConfig prepared(v::SurfaceConfig cfg){cfg.authored_snapshot.emplace(cfg.authored);cfg.authored={};return cfg;}
std::unique_ptr<v::SceneSurface> make(v::SurfaceConfig cfg){return std::make_unique<v::SceneSurface>(c::Authority{true,"desktop",{"desktop"}},policy(),std::move(cfg),std::vector<v::SurfaceProvider>{provider()},[]{return true;});}
// Waiting for telemetry does not degrade this fully readable layout.
v::SurfaceFrame frame(v::SceneSurface& surface,std::uint64_t now=1){v::SurfaceFrame out;unsigned calls=0;surface.paint(now,{},[&](auto code,const auto* value){++calls;if(!value||code!=v::SurfaceCode::ready)throw std::runtime_error("prepared surface state: code="+std::to_string(static_cast<int>(code))+", payload="+(value?"present":"absent"));out=*value;});need(calls==1,"one native frame");return out;}
}
int prepared_surface_tests(const std::string& root){
    auto cfg=config(root);const auto original=cfg.authored;
    auto raw=make(cfg);auto expected=frame(*raw);need(expected.widgets.size()==1&&expected.widgets[0].text=="Receive\nWaiting","literal pending text");
    auto typed=prepared(cfg);cfg.authored.scene["widgets"][0]["title"]="Mutated caller";
    auto surface=make(typed);const auto actual=frame(*surface);
    need(actual.widgets[0].text=="Receive\nWaiting"&&actual.displays.size()==expected.displays.size(),"prepared native text");
    for(std::size_t i=0;i<actual.displays.size();++i)need(actual.displays[i].rgba==expected.displays[i].rgba,"identical native pixels");
    auto mixed=typed;mixed.authored=original;rejects([&]{make(mixed);},"surface.authored_source");
    auto invalid=typed;invalid.topology.displays[0].scale_denominator=0;rejects([&]{make(invalid);},"layout.topology");
    invalid=typed;auto wrong=original;wrong.scene["theme_id"]="wrong";invalid.authored_snapshot.emplace(wrong);
    rejects([&]{surface->replace(invalid,2);},"content.theme");need(frame(*surface,2).widgets[0].text=="Receive\nWaiting","failed replacement retains authored state");
    auto moved=std::move(*typed.authored_snapshot);rejects([&]{make(typed);},"authored.snapshot");
    (void)moved;surface->policy(policy(8,false),3);bool cleared=false;surface->paint(3,{},[&](auto code,const auto* value){cleared=!value&&code==v::SurfaceCode::restricted;});need(cleared,"current policy erasure");
    auto changed=config(root);changed.authored.scene["widgets"][0]["title"]="Replacement";surface=make(prepared(changed));
    need(frame(*surface).widgets[0].text=="Replacement\nWaiting","fresh authored source");
    std::cout<<"PREPARED-SURFACE: native equality, ownership, refusal and policy passed\n";return 0;
}
