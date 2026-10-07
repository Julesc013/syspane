#include "editor_draft.hpp"
#include "layout.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <algorithm>
namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;namespace s=syspane::scene;using c::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("container assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(std::uint64_t n=7){c::Policy v;v.available=true;v.revision=n;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
}
void run_container(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/container-cases.json");f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};
    auto make=[&]{return ui::EditorDraft(authority(),policy(),f.authored,"E1",f.resources());};auto d=make();
    const std::vector<std::string> ids={"widget:second","widget:text"};const ui::WrapWidgets wrap{ids,"widget:new1","Container",cases["layouts"]["stack-horizontal"]};
    if(name=="SCENES"){
        for(auto it=cases["layouts"].begin();it!=cases["layouts"].end();++it){auto e=make();e.select({"widget:second"});auto op=wrap;op.layout=it.value();CHECK(e.execute({op}));
            CHECK(*e.scene()==cases["expected"][it.key()]&&e.selection()==std::vector<std::string>{"widget:new1"});CHECK(e.undo_count()==1);
            CHECK(e.undo()&&*e.scene()==f.authored.scene&&e.selection()==std::vector<std::string>{"widget:second"});CHECK(e.redo()&&*e.scene()==cases["expected"][it.key()]);
            CHECK(e.execute({ui::UnwrapWidget{"widget:new1"}})&&*e.scene()==f.authored.scene&&e.selection()==std::vector<std::string>({"widget:text","widget:second"}));
            CHECK(e.undo()&&*e.scene()==cases["expected"][it.key()]&&e.selection()==std::vector<std::string>{"widget:new1"});
        }
        d.execute({ui::UnwrapWidget{"widget:group"}});CHECK(*d.scene()==cases["unwrapped"]&&d.selection()==std::vector<std::string>({"widget:text","widget:second"}));d.undo();CHECK(*d.scene()==f.authored.scene);
    }else if(name=="GEOMETRY"){
        auto observe=[&](const Json& scene,const std::string& key,int width){s::Display display;display.id="D1";display.bounds=display.work={0,0,width*64,420*64};std::map<std::string,s::Metrics> metrics;
            for(const auto& w:scene["widgets"])if(w["kind"]!="group")metrics[w["id"]]={{32*64,16*64},{32*64,16*64}};
            const auto plan=s::resolve(scene,{{display},{},"D1"},metrics);
            for(unsigned i=0;i<2;++i){const auto id=i?"widget:second":"widget:text";const auto at=std::find_if(plan.nodes.begin(),plan.nodes.end(),[&](const s::Node& n){return n.id==id;});CHECK(at!=plan.nodes.end());
                const auto b=cases["geometry"][key][i];CHECK(at->box.x==b[0].get<int>()*64&&at->box.y==b[1].get<int>()*64&&at->box.width==b[2].get<int>()*64&&at->box.height==b[3].get<int>()*64);}
        };
        observe(f.authored.scene,"initial",500);
        for(auto it=cases["layouts"].begin();it!=cases["layouts"].end();++it){auto e=make();auto op=wrap;op.layout=it.value();e.execute({op});observe(*e.scene(),it.key(),500);if(it.key()=="responsive")observe(*e.scene(),"responsive-narrow",399);}
    }else if(name=="RULES"){
        auto value=f.authored;value.scene["widgets"][0]["layout"]["breakpoints"]=Json::array({{{"min_width_dip",600},{"layout",{{"kind","fixed"},{"x",-0.001},{"y",12},{"width",180},{"height",80}}}}});
        value.scene["widgets"][0]["extensions"]={{"author.opaque",Json::array({"keep",7,false})}};d.reload(value,"E1",f.resources());d.execute({wrap});
        for(unsigned i=0;i<4;++i)if(i!=3)CHECK(d.scene()->at("widgets")[i]==value.scene["widgets"][i]);
        d.execute({ui::UnwrapWidget{"widget:new1"}});CHECK(*d.scene()==value.scene);
        d.execute({ui::WrapWidgets{{"widget:group"},"widget:new2","Outer",cases["layouts"]["responsive"],"essential"}});CHECK(d.scene()->at("widgets")[3]==value.scene["widgets"][3]);
        d.execute({ui::UnwrapWidget{"widget:new2"}});CHECK(*d.scene()==value.scene);
        value=f.authored;value.scene=cases["nonadjacent"];d.reload(value,"E1",f.resources());d.execute({ui::WrapWidgets{{"widget:third","widget:text"},"widget:new1","Container",wrap.layout}});CHECK(*d.scene()==cases["nonadjacent_expected"]);
        d.execute({ui::UnwrapWidget{"widget:new1"}});CHECK(d.scene()->at("widgets")[4]["children"]==Json::array({"widget:text","widget:third","widget:second"}));d.undo();d.undo();CHECK(*d.scene()==value.scene);
        d.reload(f.authored,"E1",f.resources());d.execute({ui::RemoveWidgets{ids}});d.select({"widget:group"});d.execute({ui::UnwrapWidget{"widget:group"}});CHECK(d.selection().empty()&&d.scene()->at("widgets").size()==1);d.undo();CHECK(d.selection()==std::vector<std::string>{"widget:group"});
    }else if(name=="ATOMIC"){
        d.select({"widget:second"});d.execute({wrap});d.undo();const auto before=*d.scene();const auto selection=d.selection();const auto bytes=d.history_bytes();
        std::vector<ui::SceneEdit> invalid={ui::WrapWidgets{{},"widget:new1","Container",wrap.layout},ui::WrapWidgets{{"widget:text","widget:text"},"widget:new1","Container",wrap.layout},ui::WrapWidgets{{"widget:text","missing"},"widget:new1","Container",wrap.layout},ui::WrapWidgets{{"widget:text","widget:group"},"widget:new1","Container",wrap.layout},ui::WrapWidgets{{"widget:text","widget:image"},"widget:new1","Container",wrap.layout},ui::WrapWidgets{ids,"widget:text","Container",wrap.layout},ui::WrapWidgets{ids,"widget:new1",std::string(1025,'x'),wrap.layout},ui::WrapWidgets{ids,"widget:new1","Container",{{"base",before["widgets"][0]["layout"]["base"]}}},ui::WrapWidgets{ids,"widget:new1","Container",wrap.layout,"invalid"},ui::UnwrapWidget{"missing"},ui::UnwrapWidget{"widget:text"}};
        for(const auto& op:invalid){rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"rollback"},op});});CHECK(*d.scene()==before&&d.selection()==selection&&d.history_bytes()==bytes&&d.redo_count()==1);}
        rejects([&]{d.execute({wrap,ui::RemoveWidgets{{"missing"}}});});CHECK(*d.scene()==before&&d.selection()==selection&&d.redo_count()==1);
        rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::display,{{"local_id","D2"}}},wrap});});
        rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::display,{{"local_id","D2"}}},ui::UnwrapWidget{"widget:group"}});});CHECK(*d.scene()==before);
        CHECK(!d.execute({wrap,ui::UnwrapWidget{"widget:new1"}})&&d.selection()==selection&&d.redo_count()==1);
        auto value=f.authored;for(unsigned i=4;i<256;++i){auto w=value.scene["widgets"][2];w["id"]="widget:capacity"+std::to_string(i);value.scene["roots"].push_back(w["id"]);value.scene["widgets"].push_back(w);}d.reload(value,"E1",f.resources());rejects([&]{d.execute({wrap});});CHECK(*d.scene()==value.scene&&d.undo_count()==0);
        value=f.authored;for(unsigned i=0;i<14;++i){auto w=value.scene["widgets"][3];w["id"]="widget:depth"+std::to_string(i);w["children"]=value.scene["roots"];value.scene["roots"]=Json::array({w["id"]});value.scene["widgets"].push_back(w);}d.reload(value,"E1",f.resources());rejects([&]{d.execute({wrap});});CHECK(*d.scene()==value.scene&&d.undo_count()==0);
    }else if(name=="POLICY"){
        d.execute({wrap});const auto q=*d.begin("commit","container");CHECK(p::parse(q.body)["operations"]==Json::array({{{"op","scene.replace"},{"scene",cases["expected"]["stack-horizontal"]}}}));
        rejects([&]{d.execute({ui::UnwrapWidget{"widget:new1"}});});d.disconnected();rejects([&]{d.undo();});CHECK(d.active_request()->body==q.body);
        auto e=make();e.execute({wrap});auto next=policy(8);next.denied_capabilities.insert("scene.replace");e.policy(next);rejects([&]{e.execute({ui::UnwrapWidget{"widget:new1"}});});rejects([&]{e.undo();});CHECK(e.undo_count()==1&&*e.scene()==cases["expected"]["stack-horizontal"]);
        next=policy(9);next.disclosure.clear();e.policy(next);CHECK(!e.available()&&e.selection().empty()&&e.history_bytes()==0);e.policy(policy(10));CHECK(!e.available());e.reload(f.authored,"E2",f.resources());CHECK(*e.scene()==f.authored.scene);
    }else if(name=="COMPAT"){
        auto value=f.authored;value.scene["schema_version"]="0.2.0";for(auto& w:value.scene["widgets"])w.erase("content");ui::EditorDraft e(authority(),policy(),value,"E1");e.execute({wrap});CHECK(!e.scene()->at("widgets")[4].contains("content"));e.execute({ui::UnwrapWidget{"widget:new1"}});CHECK(*e.scene()==value.scene);
    }else throw std::runtime_error("unknown container family");
}
