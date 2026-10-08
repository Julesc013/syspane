#include "editor_visibility.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <limits>
namespace {
namespace ui=syspane::interfaces;namespace c=syspane::configuration;namespace p=syspane::protocol;using p::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("visibility controls assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Policy policy(std::uint64_t revision=7){c::Policy v;v.available=true;v.revision=revision;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
}
void run_visibility_controls(const std::string& name,const std::string& root){
    const auto cases=settings_fixture::read(root+"/tests/editor/visibility-controls-cases.json");settings_fixture::Fixture fixture(root);fixture.authored={cases["authored"]["settings"],cases["authored"]["scene"]};
    auto resources=fixture.resources();resources.capabilities.insert({"scene.edit-locks","scene.visibility","configuration.edit-locks","configuration.visibility"});const c::Authority authority{true,"desktop",{"desktop"}};
    auto make=[&]{return ui::EditorDraft(authority,policy(),fixture.authored,"E1",resources,true);};auto draft=make();const std::vector<std::string> ids{"widget:text"},both{"widget:text","widget:second"};
    auto input=ui::visibility_input(*draft.scene(),ids);input.mode="conditional";
    if(name=="INPUT"){
        const auto numbers=settings_fixture::read(root+"/tests/editor/visibility-number-cases.json");
        for(const auto& pair:numbers["pairs"]){auto scene=cases["multi"];scene["widgets"][0]["visibility"]["value"]=pair["left"];scene["widgets"][1]["visibility"]["value"]=pair["right"];CHECK(ui::visibility_input(scene,both).mode==(pair["equal"].get<bool>()?"conditional":"keep"));}
        CHECK(ui::visibility_input(*draft.scene(),ids).mode=="always");CHECK(ui::visibility_edit(ids,input)->rule==cases["rule"]);
        CHECK(draft.execute({*ui::visibility_edit(ids,input)}));CHECK(*draft.scene()==cases["conditional"]);
        auto mixed=ui::visibility_input(*draft.scene(),both);CHECK(mixed.mode=="keep"&&!ui::visibility_edit(both,mixed));mixed.binding=nullptr;mixed.unit="invalid";mixed.comparison.type="invalid";CHECK(!ui::visibility_edit(both,mixed));mixed.mode="always";CHECK(!ui::visibility_edit(both,mixed)->rule);
        for(const auto& key:{"conditional","hidden","multi","source","exact","mismatch"}){const auto in=ui::visibility_input(cases[key],ids);CHECK(in.mode=="conditional"&&ui::visibility_edit(ids,in)->rule==cases[key]["widgets"][0]["visibility"]);}
        CHECK(ui::visibility_input(cases["multi"],both).mode=="conditional");rejects([&]{ui::visibility_input(*draft.scene(),{});});rejects([&]{ui::visibility_input(*draft.scene(),{"absent"});});rejects([&]{ui::visibility_edit({"widget:text","widget:text"},input);});
    }else if(name=="VALUES"){
        for(const std::string token:{"18446744073709551615","9007199254740993","-9223372036854775808"}){input.comparison.value=token;const auto rule=*ui::visibility_edit(ids,input)->rule;CHECK(rule["value"].is_number_integer()&&rule["value"].dump()==token);}
        for(const std::string token:{"18446744073709551616","-9223372036854775809","NaN","1e9999","+1","01","1 "}){input.comparison.value=token;rejects([&]{ui::visibility_edit(ids,input);});}
        input.comparison.value="1.25";for(const char* op:{"eq","ne","lt","le","gt","ge"}){input.comparison.op=op;CHECK((*ui::visibility_edit(ids,input)->rule)["value"]==1.25);}
        input.comparison={"","eq","boolean","false"};input.unit="1";CHECK((*ui::visibility_edit(ids,input)->rule)["value"]==false);input.comparison.value="False";rejects([&]{ui::visibility_edit(ids,input);});input.comparison.value="true";input.comparison.op="gt";rejects([&]{ui::visibility_edit(ids,input);});
        input.comparison={"","ne","text","001"};CHECK((*ui::visibility_edit(ids,input)->rule)["value"]=="001");input.unit="byte";rejects([&]{ui::visibility_edit(ids,input);});input.unit="1";
        input.comparison.value="\"a\\u0000\\t\\n\"";input.comparison.encoding="escaped";auto rule=*ui::visibility_edit(ids,input)->rule;CHECK(rule["value"]==std::string("a\0\t\n",4));auto scene=cases["conditional"];scene["widgets"][0]["visibility"]=rule;const auto restored=ui::visibility_input(scene,ids);CHECK(restored.comparison.encoding=="escaped"&&ui::visibility_edit(ids,restored)->rule==rule);
        input.comparison.value=Json(std::string(512,'\0')).dump();CHECK((*ui::visibility_edit(ids,input)->rule)["value"].get<std::string>().size()==512);input.comparison.value=Json(std::string(513,'\0')).dump();rejects([&]{ui::visibility_edit(ids,input);});
    }else if(name=="SOURCE"){
        auto binding=cases["rule"]["binding"];ui::visibility_source(binding);binding["limit"]=2;rejects([&]{ui::visibility_source(binding);});binding["limit"]=1;binding["mode"]="collection";rejects([&]{ui::visibility_source(binding);});
        input.binding=cases["source"]["widgets"][0]["visibility"]["binding"];CHECK(draft.execute({*ui::visibility_edit(ids,input)})&&*draft.scene()==cases["source"]);draft.discard();
        const auto bindings=settings_fixture::read(root+"/tests/editor/binding-authoring-cases.json")["descriptors"];
        for(const char* kind:{"direct","persistent","legacy"}){input.binding=bindings.at(kind);ui::visibility_source(input.binding);auto scene=cases["conditional"];scene["widgets"][0]["visibility"]=*ui::visibility_edit(ids,input)->rule;const auto restored=ui::visibility_input(scene,ids);CHECK(restored.binding==input.binding);}
        input.binding=nullptr;rejects([&]{ui::visibility_edit(ids,input);});
    }else if(name=="ATOMIC"){
        const auto numbers=settings_fixture::read(root+"/tests/editor/visibility-number-cases.json");
        for(const auto& pair:numbers["pairs"]){
            auto initial=fixture.authored;initial.scene=cases["conditional"];initial.scene["widgets"][0]["visibility"]["value"]=pair["left"];
            ui::EditorDraft exact(authority,policy(),initial,"E1",resources,true);auto next=ui::visibility_input(*exact.scene(),ids);next.comparison.value=pair["right"].dump();const bool different=!pair["equal"].get<bool>();
            CHECK(exact.execute({*ui::visibility_edit(ids,next)})==different);CHECK(exact.dirty()==different);
            if(different){CHECK(exact.undo()&&!exact.dirty());CHECK(exact.redo()&&exact.dirty());const auto request=exact.begin("commit","numeric.change");CHECK(request);const auto command=c::parse_command(request->body);CHECK(command["operations"].size()==1&&command["operations"][0]["scene"]["widgets"][0]["visibility"]["value"].dump()==pair["right"].dump());}
            else CHECK(exact.undo_count()==0&&!exact.begin("commit","numeric.noop"));
        }
        input.comparison.op="eq";draft.select(both);auto edit=*ui::visibility_edit(both,input);CHECK(draft.execute({edit})&&*draft.scene()==cases["multi"]);CHECK(!draft.execute({edit})&&draft.undo_count()==1&&draft.selection()==both);
        CHECK(draft.undo()&&*draft.scene()==fixture.authored.scene);CHECK(draft.redo()&&*draft.scene()==cases["multi"]);input.mode="always";CHECK(draft.execute({*ui::visibility_edit(both,input)})&&*draft.scene()==cases["cleared"]);CHECK(!draft.execute({*ui::visibility_edit(both,input)}));
        draft.undo();CHECK(*draft.scene()==cases["multi"]);input.mode="conditional";input.comparison.value="invalid";rejects([&]{draft.execute({*ui::visibility_edit(both,input)});});CHECK(*draft.scene()==cases["multi"]&&draft.redo_count()==1&&draft.undo_count()==1);
        const auto request=*draft.begin("commit","visibility:controls");const auto command=c::parse_command(request.body);CHECK(command["schema_version"]=="0.7.0"&&command["operations"][0]["scene"]==cases["multi"]);input.mode="always";rejects([&]{draft.execute({*ui::visibility_edit(both,input)});});CHECK(*draft.scene()==cases["multi"]);
    }else if(name=="POLICY"){
        draft.execute({ui::SetWidgetLocks{ids,true}});const auto locked=*draft.scene();rejects([&]{draft.execute({*ui::visibility_edit(ids,input)});});CHECK(*draft.scene()==locked&&draft.undo_count()==1);draft.undo();
        auto denied=policy(8);denied.denied_capabilities.insert("configuration.visibility");draft.policy(denied);CHECK(!draft.visibility_available());rejects([&]{draft.execute({*ui::visibility_edit(ids,input)});});CHECK(*draft.scene()==fixture.authored.scene);
        draft.policy(policy(9));draft.execute({*ui::visibility_edit(ids,input)});denied=policy(10);denied.disclosure.clear();draft.policy(denied);CHECK(!draft.scene()&&draft.history_bytes()==0);draft.policy(policy(11));CHECK(!draft.available());draft.reload(fixture.authored,"E2",resources);CHECK(draft.visibility_available()&&*draft.scene()==fixture.authored.scene);
    }else throw std::runtime_error("unknown visibility controls family");
}
