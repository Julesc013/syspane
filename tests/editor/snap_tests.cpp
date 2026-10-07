#include "editor_snap.hpp"
#include "editor_draft.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <algorithm>
#include <limits>
namespace {
namespace ui=syspane::interfaces;namespace s=syspane::scene;namespace p=syspane::protocol;namespace c=syspane::configuration;using p::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("snap assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
s::Unit unit(const Json& v){return static_cast<s::Unit>(v.get<double>()*64);}
s::Rect rect(const Json& v){return {unit(v[0]),unit(v[1]),unit(v[2]),unit(v[3])};}
ui::SnapInput input(const Json& v){ui::SnapInput in;in.selection=rect(v["selection"]);in.area=rect(v["area"]);in.origin_x=unit(v["origin"][0]);in.origin_y=unit(v["origin"][1]);in.spacing=unit(v["spacing"]);in.threshold=unit(v["threshold"]);in.dx=unit(v["delta"][0]);in.dy=unit(v["delta"][1]);in.grid=v["grid"];in.guides=v["guides"];in.resize=v["resize"];in.bypass=v["bypass"];
    for(const auto& row:v["siblings"])in.siblings.push_back({row["id"],rect(row["box"])});
    return in;}
void guide(const std::optional<ui::SnapGuide>& actual,const Json& expected){
    CHECK(actual.has_value()!=expected.is_null());if(!actual)return;
    const auto source=expected["source"]=="grid"?ui::GuideSource::grid:expected["source"]=="area"?ui::GuideSource::area:ui::GuideSource::sibling;
    CHECK(actual->position==unit(expected["position"])&&actual->source==source&&actual->target==expected["target"]&&actual->moving==expected["moving"]&&actual->anchor==expected["anchor"]);
}
void verify(const ui::SnapInput& in,const Json& expected){const auto result=ui::snap(in);CHECK(result.dx==unit(expected["delta"][0])&&result.dy==unit(expected["delta"][1]));guide(result.x,expected["x"]);guide(result.y,expected["y"]);}
template<class F> void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
}
void run_snap(const std::string& name,const std::string& root){
    const auto cases=settings_fixture::read(root+"/tests/editor/snap-cases.json");
    if(name=="FIXED"||name=="ORDER")for(const auto& row:cases["cases"]){auto in=input(row["input"]);verify(in,row["expected"]);
        if(name=="ORDER"){std::reverse(in.siblings.begin(),in.siblings.end());verify(in,row["expected"]);}}
    else if(name=="BOUNDS"){
        const auto base=input(cases["cases"][0]["input"]);
        for(const auto n:{std::numeric_limits<s::Unit>::min(),std::numeric_limits<s::Unit>::max(),s::Unit(134217729)}){
            auto in=base;in.dx=n;rejects([&]{ui::snap(in);});in=base;in.selection.width=n;rejects([&]{ui::snap(in);});in=base;in.origin_y=n;rejects([&]{ui::snap(in);});}
        auto in=base;in.siblings.push_back(in.siblings[0]);rejects([&]{ui::snap(in);});in=base;in.siblings[0].id="invalid id";rejects([&]{ui::snap(in);});
        for(const auto n:{s::Unit(0),s::Unit(63),s::Unit(16385)}){in=base;in.spacing=n;rejects([&]{ui::snap(in);});}
        for(const auto n:{s::Unit(-1),s::Unit(1025)}){in=base;in.threshold=n;rejects([&]{ui::snap(in);});}
        in=base;in.area.width=0;rejects([&]{ui::snap(in);});in=base;in.selection.x=134217728;rejects([&]{ui::snap(in);});
        in=base;in.siblings.clear();for(unsigned n=0;n<256;++n)in.siblings.push_back({"target:"+std::to_string(n),{0,0,64,64}});(void)ui::snap(in);in.siblings.push_back({"extra",{0,0,64,64}});rejects([&]{ui::snap(in);});
    }else if(name=="HISTORY"){
        settings_fixture::Fixture f(root);f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};c::Authority a{true,"desktop",{"desktop"}};c::Policy p;p.available=true;p.revision=7;p.disclosure[{"desktop","inspector"}]={"operational"};p.disclosure[{"desktop","accessibility"}]={"operational"};
        ui::EditorDraft d(a,p,f.authored,"E1",f.resources());d.select({"widget:text"});const auto result=ui::snap(input(cases["cases"][0]["input"]));CHECK(!d.dirty()&&d.undo_count()==0);
        d.execute({ui::MoveWidgets{d.selection(),result.dx/64.0,result.dy/64.0}});CHECK(*d.scene()==cases["expected"]["grid"]&&d.undo_count()==1);CHECK(d.undo()&&*d.scene()==f.authored.scene);CHECK(d.redo()&&*d.scene()==cases["expected"]["grid"]);
        const auto q=d.begin("commit","snap");CHECK(c::parse_command(q->body)["operations"][0]["scene"]==cases["expected"]["grid"]);rejects([&]{d.execute({ui::MoveWidgets{d.selection(),1,0}});});p.disclosure.clear();p.revision=8;d.policy(p);CHECK(!d.scene()&&d.history_bytes()==0);
    }else throw std::runtime_error("unknown snap family");
}
