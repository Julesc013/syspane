#include "editor_layout.hpp"
#include "layout.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <algorithm>
namespace {
namespace ui=syspane::interfaces;namespace c=syspane::configuration;namespace p=syspane::protocol;namespace s=syspane::scene;using c::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("layout authoring assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Policy policy(std::uint64_t revision=7){c::Policy p;p.available=true;p.revision=revision;p.disclosure[{"desktop","inspector"}]={"operational"};p.disclosure[{"desktop","accessibility"}]={"operational"};return p;}
void set(ui::LayoutVariantInput& in,const Json& layout){in.kind=layout.at("kind");for(auto i=layout.begin();i!=layout.end();++i){if(i.key()=="kind")continue;if(i.value().is_object())for(auto j=i.value().begin();j!=i.value().end();++j)in.by_kind[in.kind][i.key()+"_"+j.key()]=j.value().dump();else in.by_kind[in.kind][i.key()]=i.value().is_string()?i.value().get<std::string>():i.value().dump();}}
}
void run_layout_authoring(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/layout-authoring-cases.json");f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};
    const c::Authority authority{true,"desktop",{"desktop"}};ui::EditorDraft draft(authority,policy(),f.authored,"E1",f.resources());const std::string id="widget:text",group="widget:group";
    const auto edit=[&](const std::string& target,const Json& layout){auto in=ui::layout_input(*draft.scene(),target);set(in.variants[0],layout);return ui::layout_edits(*draft.scene(),target,in);};
    const auto responsive=[&]{auto in=ui::layout_input(*draft.scene(),id);for(const auto& row:cases["responsive"]["breakpoints"]){in.thresholds.push_back(row["min_width_dip"].dump());auto v=in.variants[0];set(v,row["layout"]);in.variants.push_back(v);}return ui::layout_edits(*draft.scene(),id,in);};
    if(name=="KINDS"){
        for(auto row=cases["layouts"].begin();row!=cases["layouts"].end();++row){const bool container=row.value()["kind"]=="canvas"||row.value()["kind"]=="stack"||row.value()["kind"]=="grid";const auto target=container?group:id;
            if(row.value()["kind"]=="stack"||row.value()["kind"]=="grid")for(const auto& child:std::vector<std::string>{id,"widget:second"})draft.execute(edit(child,cases["layouts"][row.value()["kind"]=="grid"?"flow-stretch":"flow-start"]));
            draft.select({target});draft.execute(edit(target,row.value()));CHECK(*draft.scene()==cases["expected"][row.key()]);const auto before=*draft.scene();const auto history=draft.history_bytes();CHECK(!draft.execute(ui::layout_edits(*draft.scene(),target,ui::layout_input(*draft.scene(),target))));CHECK(*draft.scene()==before&&draft.history_bytes()==history);
            // Inspect submission on an isolated snapshot; the editing owner has no pending request.
            auto submitted=draft;const auto q=submitted.begin("commit","layout:"+row.key());CHECK(q&&c::parse_command(q->body)["operations"][0]["scene"]==before);draft.discard();
        }
        auto in=ui::layout_input(*draft.scene(),id);in.variants[0].kind="flow";draft.execute(ui::layout_edits(*draft.scene(),id,in));CHECK(*draft.scene()==cases["expected"]["flow-start"]);
    }else if(name=="VARIANTS"){
        draft.select({id});draft.execute(responsive());CHECK(*draft.scene()==cases["expected"]["breakpoints"]);CHECK(draft.undo()&&*draft.scene()==f.authored.scene);CHECK(draft.redo()&&*draft.scene()==cases["expected"]["breakpoints"]);
        draft.execute({ui::MoveWidgets{{id},30,20,{0}}});CHECK(*draft.scene()==cases["expected"]["variant-move"]);draft.undo();draft.execute({ui::ResizeWidget{id,240,100,0}});CHECK(*draft.scene()==cases["expected"]["variant-resize"]);draft.undo();
        draft.execute({ui::AlignWidgets{{id,"widget:second"},ui::Alignment::left,{0,-1}}});CHECK(*draft.scene()==cases["expected"]["variant-align"]);draft.undo();
        const auto old=*draft.scene();draft.execute({ui::MoveWidgets{{id},1,2}});CHECK((*draft.scene())["widgets"][0]["layout"]["base"]["x"]==21&&(*draft.scene())["widgets"][0]["layout"]["breakpoints"]==old["widgets"][0]["layout"]["breakpoints"]);draft.undo();
        auto in=ui::layout_input(*draft.scene(),id);in.thresholds.clear();in.variants.resize(1);draft.execute(ui::layout_edits(*draft.scene(),id,in));CHECK((*draft.scene())["widgets"][0]["layout"]["breakpoints"].empty());
    }else if(name=="ORDER"){
        auto in=ui::layout_input(*draft.scene(),id);in.priority="essential";in.sibling="1";draft.select({id});draft.execute(ui::layout_edits(*draft.scene(),id,in));CHECK(*draft.scene()==cases["expected"]["order-priority"]&&draft.undo_count()==1&&draft.selection()==std::vector<std::string>{id});CHECK(draft.undo()&&*draft.scene()==f.authored.scene);CHECK(draft.redo()&&*draft.scene()==cases["expected"]["order-priority"]);
    }else if(name=="DISPLAY"){
        auto in=ui::layout_input(*draft.scene(),id);in.display_kind="role";in.display_value="work";draft.execute(ui::layout_edits(*draft.scene(),id,in));CHECK(*draft.scene()==cases["expected"]["display"]);draft.discard();
        rejects([&]{draft.execute({ui::RootDisplayEdit{id,{{"local_id","D2"}}}});});CHECK(*draft.scene()==f.authored.scene);
        auto large=f.authored;large.scene["widgets"]=Json::array({f.authored.scene["widgets"][3]});large.scene["roots"]=Json::array({group});large.scene["widgets"][0]["children"]=Json::array();
        for(unsigned n=0;n<255;++n){auto w=f.authored.scene["widgets"][0];w["id"]="widget:many"+std::to_string(n);large.scene["widgets"][0]["children"].push_back(w["id"]);large.scene["widgets"].push_back(w);}
        ui::EditorDraft many(authority,policy(),large,"E1",f.resources());auto input=ui::layout_input(*many.scene(),"widget:many254");input.display_value="missing:display";const auto edits=ui::layout_edits(*many.scene(),"widget:many254",input);CHECK(edits.size()==3);many.execute(edits);CHECK(many.scene()->at("widgets").size()==256&&many.undo_count()==1);for(const auto& w:many.scene()->at("widgets"))CHECK(w["display"]==Json({{"local_id","missing:display"}}));CHECK(many.undo()&&*many.scene()==large.scene);
    }else if(name=="ATOMIC"){
        draft.select({id});draft.execute(responsive());draft.undo();const auto before=*draft.scene();const auto bytes=draft.history_bytes();auto edits=edit(id,cases["layouts"]["fixed"]);
        edits.push_back(ui::RootDisplayEdit{id,{{"local_id","D2"}}});rejects([&]{draft.execute(edits);});CHECK(*draft.scene()==before&&draft.history_bytes()==bytes&&draft.redo_count()==1&&draft.selection()==std::vector<std::string>{id});
        CHECK(draft.redo()&&*draft.scene()==cases["expected"]["breakpoints"]);const auto active=*draft.scene();const auto count=draft.undo_count();
        rejects([&]{draft.execute({ui::MoveWidgets{{id},1,2,{0}},ui::ResizeWidget{id,0,80,0}});});CHECK(*draft.scene()==active&&draft.undo_count()==count);
        rejects([&]{draft.execute({ui::MoveWidgets{{id},1,2,{1}}});});CHECK(*draft.scene()==active);draft.discard();CHECK(*draft.scene()==f.authored.scene);
    }else if(name=="BOUNDS"){
        draft.execute(responsive());draft.undo();const auto before=*draft.scene();const auto bytes=draft.history_bytes();const auto unchanged=[&]{CHECK(*draft.scene()==before&&draft.history_bytes()==bytes&&draft.redo_count()==1&&!draft.active_request());};
        for(const char* value:{"", "NaN", "1e9999", " 20", "32769", "-1"}){auto in=ui::layout_input(before,id);in.variants[0].by_kind["fixed"]["width"]=value;rejects([&]{draft.execute(ui::layout_edits(before,id,in));});unchanged();}
        auto in=ui::layout_input(before,id);in.variants[0].kind="flow";in.variants[0].by_kind["flow"]["width_min"]="200";rejects([&]{draft.execute(ui::layout_edits(before,id,in));});unchanged();
        in=ui::layout_input(before,id);in.variants[0].kind="grid";rejects([&]{draft.execute(ui::layout_edits(before,id,in));});unchanged();
        in=ui::layout_input(before,id);in.thresholds={"400","400"};in.variants={in.variants[0],in.variants[0],in.variants[0]};rejects([&]{ui::layout_edits(before,id,in);});unchanged();
        in.thresholds[1]="399";rejects([&]{ui::layout_edits(before,id,in);});in.thresholds.resize(9,"1000");in.variants.resize(10,in.variants[0]);rejects([&]{ui::layout_edits(before,id,in);});unchanged();
        in=ui::layout_input(before,id);in.display_value="bad id";rejects([&]{ui::layout_edits(before,id,in);});in=ui::layout_input(before,id);in.sibling="2";rejects([&]{ui::layout_edits(before,id,in);});unchanged();
        rejects([&]{draft.execute({ui::MoveWidgets{{id},1,2,{0}}});});rejects([&]{draft.execute({ui::MoveWidgets{{id},1,2,{-1,-1}}});});rejects([&]{draft.execute({ui::ResizeWidget{id,180,80,8}});});unchanged();
        in=ui::layout_input(before,id);in.variants[0].by_kind["fixed"]["x"]="+7e1";in.variants[0].by_kind["fixed"]["y"]="60";in.variants[0].by_kind["fixed"]["width"]="210";in.variants[0].by_kind["fixed"]["height"]="90";in.variants[0].by_kind["flow"]["width_min"]="invalid inactive";
        draft.execute(ui::layout_edits(before,id,in));CHECK(*draft.scene()==cases["expected"]["fixed"]&&draft.redo_count()==0);draft.undo();CHECK(*draft.scene()==before);
    }else if(name=="POLICY"){
        const auto edits=edit(id,cases["layouts"]["fixed"]);auto denied=policy(8);denied.denied_capabilities.insert("scene.replace");draft.policy(denied);rejects([&]{draft.execute(edits);});CHECK(*draft.scene()==f.authored.scene);draft.policy(policy(9));draft.execute(edits);
        denied=policy(10);denied.disclosure.clear();draft.policy(denied);CHECK(!draft.scene()&&draft.history_bytes()==0);draft.policy(policy(11));CHECK(!draft.available());draft.reload(f.authored,"E2",f.resources());CHECK(draft.available());
    }else if(name=="GEOMETRY"){
        s::Display display;display.id="D1";display.bounds=display.work={0,0,500*64,420*64};s::Topology topology{{display},{},"D1"};std::map<std::string,s::Metrics> metrics;for(const auto& w:f.authored.scene["widgets"])if(w["kind"]!="group")metrics[w["id"]]={{32*64,16*64},{32*64,16*64}};
        for(auto row=cases["geometry"].begin();row!=cases["geometry"].end();++row){const auto original=cases["expected"][row.key()];const auto plan=s::resolve(original,topology,metrics);
            for(auto box=row.value().begin();box!=row.value().end();++box){const auto at=std::find_if(plan.nodes.begin(),plan.nodes.end(),[&](const auto& n){return n.id==box.key();});CHECK(at!=plan.nodes.end());CHECK(at->box.x==box.value()[0].get<int>()*64&&at->box.y==box.value()[1].get<int>()*64&&at->box.width==box.value()[2].get<int>()*64&&at->box.height==box.value()[3].get<int>()*64);}
            CHECK(original==cases["expected"][row.key()]);}
        for(const auto width:{399,400,799,800}){topology.displays[0].bounds.width=topology.displays[0].work.width=width*64;const auto plan=s::resolve(cases["expected"]["breakpoints"],topology,metrics);const auto at=std::find_if(plan.nodes.begin(),plan.nodes.end(),[&](const auto& n){return n.id==id;});CHECK(at->variant==(width<400?-1:width<800?0:1));}
    }else throw std::runtime_error("unknown layout authoring family");
}
