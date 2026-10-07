#include "editor_draft.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <algorithm>
#include <limits>
namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;using c::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("arrange assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F> void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(std::uint64_t n=7){c::Policy v;v.available=true;v.revision=n;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
ui::SceneEdit operation(const std::string& name,const std::vector<std::string>& ids){
    if(name=="horizontal"||name=="vertical")return ui::DistributeWidgets{ids,name=="horizontal"?ui::Spacing::horizontal:ui::Spacing::vertical};
    const std::map<std::string,ui::Alignment> kinds={{"left",ui::Alignment::left},{"hcenter",ui::Alignment::hcenter},{"right",ui::Alignment::right},{"top",ui::Alignment::top},{"vcenter",ui::Alignment::vcenter},{"bottom",ui::Alignment::bottom}};
    return ui::AlignWidgets{ids,kinds.at(name)};
}
}
void run_arrange(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/arrange-cases.json");f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};
    auto make=[&]{return ui::EditorDraft(authority(),policy(),f.authored,"E1",f.resources());};auto d=make();
    const std::vector<std::string> ids={"widget:third","widget:text","widget:second"};const auto edit=operation("horizontal",ids);
    if(name=="FIXED"){
        for(const auto& row:cases["cases"]){auto e=make();e.select(ids);const auto selected=e.selection();CHECK(e.execute({operation(row["action"],row["ids"].get<std::vector<std::string>>())}));
            CHECK(*e.scene()==row["expected"]&&e.selection()==selected&&e.undo_count()==1&&e.revision()==40);CHECK(e.undo()&&*e.scene()==f.authored.scene);CHECK(e.redo()&&*e.scene()==row["expected"]);}
    }else if(name=="ROUNDING"){
        for(const auto& row:cases["fractional"]){auto e=make();auto scene=f.authored.scene;
            for(std::size_t i=0;i<3;++i){scene["widgets"][i]["layout"]["base"]["x"]=row["positions"][i];scene["widgets"][i]["layout"]["base"]["width"]=row["extents"][i];}
            auto value=f.authored;value.scene=scene;e.reload(value,"E1",f.resources());e.execute({operation(row["action"],ids)});
            for(std::size_t i=0;i<3;++i)scene["widgets"][i]["layout"]["base"]["x"]=row["expected"][i];
            CHECK(*e.scene()==scene);
        }
    }else if(name=="ATOMIC"){
        d.select(ids);d.execute({edit});d.undo();const auto before=*d.scene();const auto selected=d.selection();const auto history=d.history_bytes();
        const std::vector<ui::SceneEdit> invalid={operation("left",{}),operation("left",{"widget:text"}),operation("horizontal",{"widget:text","widget:second"}),
            operation("left",{"widget:text","widget:text"}),operation("left",{"widget:text","missing"}),ui::AlignWidgets{ids,static_cast<ui::Alignment>(99)},ui::DistributeWidgets{ids,static_cast<ui::Spacing>(99)}};
        const ui::SceneEdit title=ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"should roll back"};
        for(const auto& bad:invalid){rejects([&]{d.execute({title,bad});});CHECK(*d.scene()==before&&d.selection()==selected&&d.undo_count()==0&&d.redo_count()==1&&d.history_bytes()==history&&!d.active_request());}
        for(const auto n:{std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),1e300,-100001.}){
            auto layout=before["widgets"][0]["layout"];layout["base"]["x"]=n;rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::layout,layout},edit});});CHECK(*d.scene()==before&&d.redo_count()==1);}
        for(const auto* key:{"width","height"}){auto layout=before["widgets"][0]["layout"];layout["base"][key]=0;
            rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::layout,layout},edit});});CHECK(*d.scene()==before);}
        auto layout=before["widgets"][2]["layout"];layout["base"]["x"]=50;
        rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:third",ui::WidgetProperty::layout,layout},edit});});CHECK(*d.scene()==before&&d.redo_count()==1);
        layout["base"]["x"]=100000;layout["base"]["width"]=32768;
        rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:third",ui::WidgetProperty::layout,layout},operation("right",ids)});});CHECK(*d.scene()==before&&d.redo_count()==1);
        rejects([&]{d.execute({operation("left",std::vector<std::string>(257,"widget:text"))});});CHECK(*d.scene()==before);
    }else if(name=="SCOPE"){
        auto scene=f.authored.scene;auto group=scene["widgets"][0];group["id"]="widget:group";group["kind"]="group";group["content"]=Json::object();group["children"]=scene["roots"];
        group["layout"]["base"]={{"kind","fixed"},{"x",20},{"y",30},{"width",480},{"height",400}};
        scene["roots"]=Json::array({"widget:group"});scene["widgets"].push_back(group);auto value=f.authored;value.scene=scene;d.reload(value,"E1",f.resources());
        CHECK(d.execute({edit}));scene["widgets"][1]["layout"]["base"]["x"]=217;CHECK(*d.scene()==scene);d.undo();
        rejects([&]{d.execute({operation("left",{"widget:group","widget:text"})});});
        d.execute({ui::ReparentWidgets{{"widget:third"},std::nullopt,1}});const auto mixed=*d.scene();rejects([&]{d.execute({edit});});CHECK(*d.scene()==mixed);
        d.reload(f.authored,"E1",f.resources());d.execute({ui::WidgetPropertyEdit{"widget:third",ui::WidgetProperty::display,{{"local_id","D2"}}}});
        const auto different=*d.scene();rejects([&]{d.execute({edit});});CHECK(*d.scene()==different);
        // Reverse widget storage and caller order independently of ownership.
        value=f.authored;std::reverse(value.scene["widgets"].begin(),value.scene["widgets"].end());d.reload(value,"E1",f.resources());d.execute({edit});value.scene["widgets"][1]["layout"]["base"]["x"]=217;CHECK(*d.scene()==value.scene);
        auto layout=value.scene["widgets"][0]["layout"];layout["breakpoints"]=Json::array({{{"min_width_dip",800},{"layout",layout["base"]}}});
        d.execute({ui::WidgetPropertyEdit{"widget:third",ui::WidgetProperty::layout,layout},operation("left",ids)});CHECK((*d.scene())["widgets"][0]["layout"]["breakpoints"]==layout["breakpoints"]);
        value=f.authored;value.scene["widgets"][0]["layout"]["base"]["x"]=0;value.scene["widgets"][1]["layout"]["base"]["x"]=0;value.scene["widgets"][2]["layout"]["base"]["x"]=400;
        d.reload(value,"E1",f.resources());d.execute({edit});CHECK((*d.scene())["widgets"][1]["layout"]["base"]["x"]==212);
        value.scene["roots"]=Json::array({"widget:second","widget:text","widget:third"});d.reload(value,"E1",f.resources());d.execute({edit});CHECK((*d.scene())["widgets"][0]["layout"]["base"]["x"]==188&&(*d.scene())["widgets"][1]["layout"]["base"]["x"]==0);
        value=f.authored;value.scene["widgets"][0]["layout"]=settings_fixture::read(root+"/tests/scene/cases/ROOT-FLOW.json")["scene"]["widgets"][0]["layout"];
        d.reload(value,"E1",f.resources());rejects([&]{d.execute({edit});});CHECK(*d.scene()==value.scene&&!d.dirty());
    }else if(name=="HISTORY"){
        d.select(ids);d.execute({edit,operation("top",ids)});CHECK(d.undo_count()==1);const auto combined=*d.scene();
        CHECK(d.undo()&&*d.scene()==f.authored.scene);CHECK(d.redo()&&*d.scene()==combined);CHECK(!d.execute({edit,operation("top",ids)})&&d.undo_count()==1);
        d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"later"}});d.undo();CHECK(!d.execute({edit,operation("top",ids)})&&d.redo_count()==1);
        d.discard();CHECK(!d.dirty()&&*d.scene()==f.authored.scene&&d.history_bytes()==0);
    }else if(name=="POLICY"){
        d.execute({edit});const auto arranged=*d.scene();const auto q=*d.begin("commit","arrange");const auto body=p::parse(q.body);CHECK(body["operations"]==Json::array({{{"op","scene.replace"},{"scene",arranged}}}));CHECK(body["content"]==f.document["selection"]);
        rejects([&]{d.execute({operation("left",ids)});});d.disconnected();rejects([&]{d.undo();});CHECK(d.active_request()->body==q.body);
        auto e=make();e.execute({edit});auto next=policy(8);next.denied_capabilities.insert("scene.replace");e.policy(next);rejects([&]{e.undo();});rejects([&]{e.execute({operation("left",ids)});});CHECK(*e.scene()==arranged&&e.undo_count()==1);
        next=policy(9);next.disclosure.clear();e.policy(next);CHECK(!e.scene()&&e.selection().empty()&&e.history_bytes()==0);e.policy(policy(10));CHECK(!e.available());e.reload(f.authored,"E2",f.resources());CHECK(*e.scene()==f.authored.scene);
    }else throw std::runtime_error("unknown arrange family");
}
