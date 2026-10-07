#include "editor_create.hpp"
#include "../configuration/settings_content_fixture.hpp"
namespace {
namespace ui=syspane::interfaces;namespace c=syspane::configuration;namespace p=syspane::protocol;using c::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("widget creation assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Policy policy(std::uint64_t revision=7){c::Policy p;p.available=true;p.revision=revision;p.disclosure[{"desktop","inspector"}]={"operational"};p.disclosure[{"desktop","accessibility"}]={"operational"};return p;}
}
void run_widget_creation(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root,"tests/editor/content-properties-fixture.json");const auto cases=settings_fixture::read(root+"/tests/editor/widget-creation-cases.json");
    const c::Authority authority{true,"desktop",{"desktop"}};const auto snapshot=f.catalog->resources(f.document["selection"],f.authored);const auto choices=ui::content_choices(*snapshot);const Json display={{"local_id","D1"}};
    ui::EditorDraft draft(authority,policy(),f.authored,"E1",f.resources());
    const auto input=[&](const std::string& kind){auto in=ui::create_input(kind);if(kind=="image")in.asset=cases["objects"]["image"]["content"]["asset"];return in;};
    const auto create=[&](const ui::CreateInput& in,const std::string& id="widget:new1"){return ui::create_widget(*draft.scene(),in,id,display,choices);};
    if(name=="KINDS"||name=="HISTORY"){
        for(const std::string kind:{"text","value","status","table","chart","image","group"}){
            const auto edit=create(input(kind));CHECK(edit.widget==cases["objects"][kind]);CHECK(edit.select_inserted&&edit.index==4&&!edit.parent);
            const std::vector<std::string> before={f.authored.scene["widgets"][0]["id"]};draft.select(before);CHECK(draft.execute({edit}));CHECK(*draft.scene()==cases["expected"][kind]);CHECK(draft.selection()==std::vector<std::string>{"widget:new1"});CHECK(draft.undo_count()==1);
            CHECK(draft.undo()&&*draft.scene()==f.authored.scene&&draft.selection()==before);CHECK(draft.redo()&&*draft.scene()==cases["expected"][kind]&&draft.selection()==std::vector<std::string>{"widget:new1"});
            if(name=="HISTORY"){ui::EditorDraft submitted(authority,policy(),f.authored,"E1",f.resources());submitted.execute({edit});const auto q=submitted.begin("commit","creation:"+kind);CHECK(q&&c::parse_command(q->body)["operations"][0]["scene"]==cases["expected"][kind]);rejects([&]{submitted.execute({edit});});CHECK(submitted.active_request()->request==q->request);}
            draft.discard();draft.select(before);auto compatible=edit;compatible.select_inserted=false;draft.execute({compatible});CHECK(draft.selection()==before);draft.discard();
        }
    }else if(name=="PARENTS"){
        draft.execute({create(input("group"))});auto in=input("text");in.parent="widget:new1";in.fields["title"]="Nested";in.fields["body"]="Nested body";const auto edit=create(in,"widget:new2");CHECK(edit.index==0&&edit.parent==in.parent);draft.execute({edit});CHECK(*draft.scene()==cases["expected"]["nested"]);
        CHECK(draft.undo()&&draft.selection()==std::vector<std::string>{"widget:new1"});CHECK(draft.redo()&&draft.selection()==std::vector<std::string>{"widget:new2"});
        auto scene=*draft.scene();scene["widgets"][4]["display"]={{"role","primary"}};const auto role=ui::create_widget(scene,in,"widget:new3",display,choices);CHECK(role.widget["display"]==scene["widgets"][4]["display"]&&role.index==1);CHECK(role.widget["layout"]["base"]["x"]==20);
        for(const std::string& id:{std::string("missing"),f.authored.scene["widgets"][0]["id"].get<std::string>()}){in.parent=id;rejects([&]{create(in);});}
    }else if(name=="ATOMIC"){
        const auto edit=create(input("text"));draft.execute({edit});draft.undo();const auto before=*draft.scene();const auto selection=draft.selection();const auto bytes=draft.history_bytes();
        const auto unchanged=[&]{CHECK(*draft.scene()==before&&draft.selection()==selection&&draft.undo_count()==0&&draft.redo_count()==1&&draft.history_bytes()==bytes&&!draft.active_request());};
        rejects([&]{draft.execute({edit,edit});});unchanged();auto bad=edit;bad.widget["id"]=before["widgets"][0]["id"];rejects([&]{draft.execute({bad});});unchanged();
        bad=edit;bad.widget["title"]=std::string(513,'x');rejects([&]{draft.execute({bad});});unchanged();
        auto in=input("table");in.fields["second_field"]=in.fields["field"];rejects([&]{create(in);});unchanged();
        in=input("image");in.asset["path"]="images/absent.png";rejects([&]{create(in);});unchanged();
        CHECK(draft.redo()&&*draft.scene()==cases["expected"]["text"]);
    }else if(name=="BOUNDS"){
        rejects([&]{ui::create_input("unknown");});rejects([&]{create(input("text"),"invalid id");});
        auto in=input("text");for(const std::string value:{"","NaN","inf"," 20","20 ","1e9999","0x20","-100001","100001"}){in.fields["x"]=value;rejects([&]{create(in);});}
        in.fields["x"]="-1e5";in.fields["y"]="+1e5";in.fields["width"]="3.2e1";in.fields["height"]="16";auto edit=create(in);CHECK(edit.widget["layout"]["base"]["x"]==-100000&&edit.widget["layout"]["base"]["width"]==32);draft.execute({edit});draft.discard();
        for(const char* key:{"width","height"})for(const char* value:{"0","-1","32769"}){auto bad=input("text");bad.fields[key]=value;rejects([&]{create(bad);});}
        in=input("text");in.fields["x"]=std::string(65,'1');rejects([&]{create(in);});in=input("image");in.asset=nullptr;rejects([&]{create(in);});
        in=input("value");in.fields["field"]="bad field";rejects([&]{create(in);});in=input("text");in.fields["field"]="bad field";in.asset="ignored";CHECK(create(in).widget==cases["objects"]["text"]);
        auto old=f.authored.scene;old["schema_version"]="0.2.0";rejects([&]{ui::create_widget(old,input("text"),"widget:new1",display,choices);});
        std::vector<ui::SceneEdit> many;for(unsigned n=0;n<252;++n){auto w=create(input("text"),"widget:many"+std::to_string(n));w.index=4+n;many.push_back(w);if(many.size()==126){draft.execute(many);many.clear();}}const auto full=*draft.scene();const auto selected=draft.selection();const auto bytes=draft.history_bytes();rejects([&]{draft.execute({create(input("text"))});});CHECK(*draft.scene()==full&&draft.selection()==selected&&draft.history_bytes()==bytes);draft.discard();
        auto nested=f.authored;auto& scene=nested.scene;scene["widgets"]=Json::array();scene["roots"]=Json::array({"group:0"});for(unsigned n=0;n<16;++n){auto w=cases["objects"]["group"];w["id"]="group:"+std::to_string(n);if(n<15)w["children"]=Json::array({"group:"+std::to_string(n+1)});scene["widgets"].push_back(w);}ui::EditorDraft deep(authority,policy(),nested,"E1",f.resources());in=input("text");in.parent="group:15";const auto too_deep=ui::create_widget(scene,in,"widget:deep",display,choices);rejects([&]{deep.execute({too_deep});});CHECK(*deep.scene()==scene&&deep.undo_count()==0);
    }else if(name=="POLICY"){
        const auto edit=create(input("image"));auto denied=policy(8);denied.denied_capabilities.insert("scene.content");draft.policy(denied);rejects([&]{draft.execute({edit});});CHECK(*draft.scene()==f.authored.scene&&draft.undo_count()==0);
        draft.policy(policy(9));draft.execute({edit});denied=policy(10);denied.disclosure.clear();draft.policy(denied);CHECK(!draft.scene()&&draft.history_bytes()==0&&draft.selection().empty());draft.policy(policy(11));CHECK(!draft.available());draft.reload(f.authored,"E2",f.resources());CHECK(draft.available()&&*draft.scene()==f.authored.scene);
        auto missing=f.resources();missing.capabilities.clear();ui::EditorDraft unavailable(authority,policy(),f.authored,"E1",missing);rejects([&]{unavailable.execute({edit});});
    }else throw std::runtime_error("unknown widget creation family");
}
