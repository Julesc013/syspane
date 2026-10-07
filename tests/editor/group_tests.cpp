#include "editor_draft.hpp"
#include "layout.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <algorithm>
#include <limits>
namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;namespace s=syspane::scene;using c::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("group assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F> void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(std::uint64_t n=7){c::Policy v;v.available=true;v.revision=n;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
std::vector<s::Node> plan(const Json& scene,int width){
    s::Display d;d.id="D1";d.bounds=d.work={-100*64,-100*64,width*64,600*64};std::map<std::string,s::Metrics> metrics;
    for(const auto& w:scene["widgets"])if(w["kind"]!="group")metrics[w["id"]]={{32*64,16*64},{32*64,16*64}};
    return s::resolve(scene,{{d},{},"D1"},metrics).nodes;
}
}
void run_group(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/group-cases.json");f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};
    auto make=[&]{return ui::EditorDraft(authority(),policy(),f.authored,"E1",f.resources());};auto d=make();
    const std::vector<std::string> ids={"widget:third","widget:text","widget:second"};const ui::SceneEdit group=ui::GroupWidgets{ids,"widget:new1","Group"};
    if(name=="SCENES"){
        d.select({"widget:second"});CHECK(d.execute({group}));CHECK(*d.scene()==cases["grouped"]&&d.selection()==std::vector<std::string>{"widget:new1"});
        CHECK(d.undo()&&*d.scene()==f.authored.scene&&d.selection()==std::vector<std::string>{"widget:second"});CHECK(d.redo()&&d.selection()==std::vector<std::string>{"widget:new1"});
        d.execute({ui::MoveWidgets{{"widget:new1"},30,20}});CHECK(*d.scene()==cases["moved"]);d.execute({ui::UngroupWidget{"widget:new1"}});CHECK(*d.scene()==cases["ungrouped"]&&d.selection()==f.authored.scene["roots"].get<std::vector<std::string>>());
        CHECK(d.undo()&&*d.scene()==cases["moved"]&&d.selection()==std::vector<std::string>{"widget:new1"});CHECK(d.redo()&&*d.scene()==cases["ungrouped"]);d.discard();CHECK(*d.scene()==f.authored.scene);
        d.execute({ui::GroupWidgets{{"widget:second","widget:text"},"widget:new1","Group"}});CHECK(*d.scene()==cases["partial"]);
        d.execute({ui::GroupWidgets{{"widget:third","widget:new1"},"widget:new2","Group"}});CHECK(*d.scene()==cases["nested"]);
        d.execute({ui::UngroupWidget{"widget:new2"}});CHECK(*d.scene()==cases["partial"]&&d.selection()==std::vector<std::string>({"widget:third","widget:new1"}));
        d.execute({ui::UngroupWidget{"widget:new1"}});CHECK(*d.scene()==f.authored.scene);
    }else if(name=="VARIANTS"){
        for(const auto* key:{"fractional","responsive"}){auto value=f.authored;value.scene=cases[key];auto e=make();e.reload(value,"E1",f.resources());e.execute({group});CHECK(*e.scene()==cases[std::string(key)+"_grouped"]);
            for(const int width:{500,900}){const auto before=plan(value.scene,width),after=plan(*e.scene(),width);
                for(const auto& n:before){const auto found=std::find_if(after.begin(),after.end(),[&](const auto& row){return row.id==n.id;});CHECK(found!=after.end());
                    CHECK(n.box.x==found->box.x&&n.box.y==found->box.y&&n.box.width==found->box.width&&n.box.height==found->box.height&&n.pixels.x==found->pixels.x&&n.pixels.y==found->pixels.y&&n.variant==found->variant);}}
            CHECK(e.undo()&&*e.scene()==value.scene);e.redo();e.execute({ui::UngroupWidget{"widget:new1"}});auto expected=value.scene;
            if(std::string(key)=="fractional")expected["widgets"][0]["layout"]["base"]["x"]=expected["widgets"][0]["layout"]["base"]["y"]=-0.015625;
            CHECK(*e.scene()==expected);
        }
    }else if(name=="ORDER"){
        d.execute({ui::GroupWidgets{{"widget:third","widget:text"},"widget:new1","Group"}});CHECK(*d.scene()==cases["nonadjacent"]);
        std::vector<std::string> order;for(const auto& n:plan(*d.scene(),500))order.push_back(n.id);CHECK(order==std::vector<std::string>({"widget:new1","widget:text","widget:third","widget:second"}));
        d.execute({ui::UngroupWidget{"widget:new1"}});CHECK((*d.scene())["roots"]==Json::array({"widget:text","widget:third","widget:second"}));
        auto value=f.authored;std::reverse(value.scene["widgets"].begin(),value.scene["widgets"].end());d.reload(value,"E1",f.resources());d.execute({group});auto expected=cases["grouped"];std::reverse(expected["widgets"].begin(),expected["widgets"].begin()+3);CHECK(*d.scene()==expected);
        value=f.authored;value.scene["widgets"][1]["layout"]["base"]["x"]=400;value.scene["widgets"][1]["layout"]["base"]["y"]=320;
        d.reload(value,"E1",f.resources());d.execute({ui::GroupWidgets{{"widget:text","widget:third"},"widget:new1","Group"}});CHECK(*d.scene()==cases["overlap"]);
    }else if(name=="ATOMIC"){
        d.select({"widget:second"});d.execute({group});d.undo();const auto before=*d.scene();const auto selected=d.selection();const auto bytes=d.history_bytes();
        const std::vector<ui::SceneEdit> invalid={ui::GroupWidgets{{},"widget:new1","Group"},ui::GroupWidgets{{"widget:text"},"widget:new1","Group"},ui::GroupWidgets{ids,"widget:text","Group"},ui::GroupWidgets{ids,"widget:new1",std::string(1025,'x')},ui::GroupWidgets{{"widget:text","widget:text"},"widget:new1","Group"},ui::GroupWidgets{{"widget:text","missing"},"widget:new1","Group"},ui::UngroupWidget{"widget:text"}};
        for(const auto& edit:invalid){rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"rollback"},edit});});CHECK(*d.scene()==before&&d.selection()==selected&&d.history_bytes()==bytes&&d.redo_count()==1);}
        rejects([&]{d.execute({group,ui::RemoveWidgets{{"missing"}}});});CHECK(*d.scene()==before&&d.selection()==selected&&d.redo_count()==1);
        for(double n:{std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN(),1e300}){auto layout=before["widgets"][0]["layout"];layout["base"]["x"]=n;rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::layout,layout},group});});CHECK(*d.scene()==before);}
        auto layout=before["widgets"][0]["layout"];layout["base"]["x"]=-100000;rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::layout,layout},group});});CHECK(*d.scene()==before);
        rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:third",ui::WidgetProperty::display,{{"local_id","D2"}}},group});});CHECK(*d.scene()==before);
        layout=settings_fixture::read(root+"/tests/scene/cases/ROOT-FLOW.json")["scene"]["widgets"][0]["layout"];rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::layout,layout},group});});CHECK(*d.scene()==before);
        CHECK(!d.execute({group,ui::UngroupWidget{"widget:new1"}})&&d.selection()==selected&&d.redo_count()==1);
    }else if(name=="CONTAINMENT"){
        d.execute({group});const auto before=*d.scene();auto layout=before["widgets"][0]["layout"];layout["base"]["x"]=-1;
        rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::layout,layout},ui::UngroupWidget{"widget:new1"}});});CHECK(*d.scene()==before);
        layout=before["widgets"][3]["layout"];layout["breakpoints"]=Json::array({{{"min_width_dip",800},{"layout",layout["base"]}}});
        rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:new1",ui::WidgetProperty::layout,layout},ui::UngroupWidget{"widget:new1"}});});CHECK(*d.scene()==before);
        rejects([&]{d.execute({ui::GroupWidgets{{"widget:new1","widget:text"},"widget:new2","Group"}});});CHECK(*d.scene()==before);
        d.execute({ui::RemoveWidgets{ids}});d.select({"widget:new1"});d.execute({ui::UngroupWidget{"widget:new1"}});CHECK(d.scene()->at("widgets").empty()&&d.selection().empty());d.undo();CHECK(d.selection()==std::vector<std::string>{"widget:new1"});
        auto value=f.authored;for(unsigned n=3;n<256;++n){auto w=value.scene["widgets"][0];w["id"]="widget:capacity"+std::to_string(n);value.scene["roots"].push_back(w["id"]);value.scene["widgets"].push_back(std::move(w));}
        d.reload(value,"E1",f.resources());rejects([&]{d.execute({group});});CHECK(*d.scene()==value.scene&&d.undo_count()==0);
        value=f.authored;for(unsigned n=0;n<15;++n){auto w=cases["grouped"]["widgets"][3];w["id"]="widget:depth"+std::to_string(n);w["children"]=value.scene["roots"];value.scene["roots"]=Json::array({w["id"]});value.scene["widgets"].push_back(std::move(w));}
        d.reload(value,"E1",f.resources());rejects([&]{d.execute({group});});CHECK(*d.scene()==value.scene&&d.undo_count()==0&&d.selection().empty());
    }else if(name=="POLICY"){
        d.execute({group});const auto q=*d.begin("commit","group");const auto body=p::parse(q.body);CHECK(body["operations"]==Json::array({{{"op","scene.replace"},{"scene",cases["grouped"]}}})&&body["content"]==f.document["selection"]);
        rejects([&]{d.execute({ui::UngroupWidget{"widget:new1"}});});d.disconnected();rejects([&]{d.undo();});CHECK(d.active_request()->body==q.body);
        auto e=make();e.execute({group});auto next=policy(8);next.denied_capabilities.insert("scene.replace");e.policy(next);rejects([&]{e.undo();});rejects([&]{e.execute({ui::UngroupWidget{"widget:new1"}});});CHECK(*e.scene()==cases["grouped"]&&e.undo_count()==1);
        next=policy(9);next.disclosure.clear();e.policy(next);CHECK(!e.scene()&&e.selection().empty()&&e.history_bytes()==0);e.policy(policy(10));CHECK(!e.available());e.reload(f.authored,"E2",f.resources());CHECK(*e.scene()==f.authored.scene);
    }else if(name=="COMPAT"){
        auto value=f.authored;value.scene["schema_version"]="0.2.0";for(auto& w:value.scene["widgets"])w.erase("content");ui::EditorDraft e(authority(),policy(),value,"E1");e.execute({group});CHECK(!e.scene()->at("widgets")[3].contains("content"));
        CHECK(p::parse(e.begin("preview","P")->body)["schema_version"]=="0.2.0");
    }else throw std::runtime_error("unknown group family");
}
