#include "editor_binding.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <algorithm>
#include <limits>
namespace {
namespace ui=syspane::interfaces;namespace c=syspane::configuration;namespace p=syspane::protocol;using c::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("binding authoring assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Policy policy(std::uint64_t revision=7){c::Policy p;p.available=true;p.revision=revision;p.disclosure[{"desktop","inspector"}]={"operational"};p.disclosure[{"desktop","accessibility"}]={"operational"};return p;}
ui::BindingInput proposed(const Json& original,const std::string& mode){auto in=ui::binding_input(original);
    if(mode=="field")in.fields["field"]="network.transmit_bytes";
    if(mode=="direct"){in.fields["kind"]="direct";in.fields["producer_id"]="P1";in.fields["producer_epoch"]="E1";in.fields["entity_id"]="nic:one";in.fields["field"]="network.transmit_bytes";in.predicates={{"invalid","invalid","invalid","ignored"}};}
    if(mode=="persistent"||mode=="local"){in.fields["kind"]="persistent_pin";in.fields["scope"]=mode=="local"?"local_host":"registered_asset";in.fields["asset_id"]="asset:remote";in.fields["namespace"]="network.adapter";in.fields["key"]="Adapter\n\xce\xb1";in.fields["entity_type"]="network.adapter";in.fields["field"]="network.transmit_bytes";in.fields["limit"]="invalid inactive";}
    if(mode=="selector"){in.fields["scope"]="current_session";in.fields["limit"]="7";in.fields["entity_type"]="network.adapter";in.fields["field"]="network.transmit_bytes";
        in.predicates={{"entity.display_name","ne","text","Ghost"},{"network.receive_bytes","eq","number","9007199254740993"}};in.sort={{"entity.display_name","descending"},{"entity.id","ascending"}};}
    if(mode=="table"){in.fields["limit"]="1";in.predicates={{"entity.id","ne","text","nic:absent"}};in.sort={{"entity.id","descending"}};}
    if(mode=="empty")in.predicates={{"entity.id","eq","text","nic:absent"}};
    return in;
}
}
void run_binding_authoring(const std::string& name,const std::string& root){
    settings_fixture::Fixture fixture(root,"tests/editor/content-properties-fixture.json");const auto cases=settings_fixture::read(root+"/tests/editor/binding-authoring-cases.json");
    const c::Authority authority{true,"desktop",{"desktop"}};ui::EditorDraft draft(authority,policy(),fixture.authored,"E1",fixture.resources());const auto& widgets=fixture.authored.scene["widgets"];
    if(name=="MAPPING"||name=="HISTORY"){
        for(const std::string mode:{"field","direct","persistent","selector","table","empty","local"}){
            const auto& w=widgets[mode=="table"?1:2];auto in=proposed(w["bindings"][0],mode);std::vector<std::string> fields;
            for(const auto& b:w["bindings"])fields.push_back(mode=="table"?b["field"].get<std::string>():in.fields.at("field"));
            const auto edit=ui::binding_edit(w,in,fields);draft.select({w["id"]});CHECK(draft.execute({edit}));CHECK(*draft.scene()==cases["expected"][mode]);CHECK(!draft.execute({edit})&&draft.undo_count()==1);
            CHECK(draft.undo()&&*draft.scene()==fixture.authored.scene);CHECK(draft.redo()&&*draft.scene()==cases["expected"][mode]);
            if(name=="HISTORY"){ui::EditorDraft submitted(authority,policy(),fixture.authored,"E1",fixture.resources());submitted.execute({edit});const auto request=*submitted.begin("commit","bindings:"+mode);CHECK(c::parse_command(request.body)["operations"][0]["scene"]==cases["expected"][mode]);rejects([&]{submitted.execute({edit});});}
            draft.discard();
        }
        for(const auto& d:cases["descriptors"]){const auto in=ui::binding_input(d);CHECK(ui::binding_descriptor(in,d,d.value("mode","singleton"))==d);}
    }else if(name=="TEXT"){
        const auto text=settings_fixture::read(root+"/tests/editor/binding-text-cases.json");
        for(const auto& row:text["text"]){CHECK(ui::binding_text(row["input"],"escaped")==row["expected"]);CHECK(ui::binding_text(row["input"],"literal")==row["input"]);}
        for(const auto& token:text["invalid"])rejects([&]{ui::binding_text(token,"escaped");});
        auto b=text["expected"]["widgets"][2]["bindings"][0];const auto in=ui::binding_input(b);CHECK(in.predicates[0].encoding=="escaped");CHECK(ui::binding_descriptor(in,b,"singleton")==b);
        CHECK(draft.execute({ui::binding_edit(widgets[2],in,{"network.receive_bytes"})}));CHECK(*draft.scene()==text["expected"]);
        b["predicates"][0]["value"]=std::string(512,'\0');auto boundary=ui::binding_input(b);CHECK(boundary.predicates[0].value.size()==3074&&ui::binding_descriptor(boundary,b,"singleton")==b);
        boundary.predicates[0].value=Json(std::string(513,'\0')).dump();rejects([&]{ui::binding_descriptor(boundary,b,"singleton");});
        auto pin=cases["descriptors"]["persistent"];pin["key"]=text["text"][0]["expected"];auto key=ui::binding_input(pin);CHECK(key.fields.at("key_encoding")=="escaped"&&ui::binding_descriptor(key,pin,"singleton")==pin);
    }else if(name=="NUMBERS"){
        const auto parse=[](const std::string& s){return ui::binding_value({"entity.id","eq","number",s});};
        for(const std::string s:{"9007199254740993","18446744073709551615","9223372036854775808"}){const auto v=parse(s);CHECK(v.is_number_unsigned()&&v.dump()==s);}
        CHECK(parse("-9223372036854775808").get<std::int64_t>()==std::numeric_limits<std::int64_t>::min());CHECK(parse("1e2")==100.0&&parse("-0.25")==-0.25);
        for(const std::string s:{""," 1","1 ","+1","01",".1","1.","NaN","Infinity","1e9999","18446744073709551616","-9223372036854775809","1\n","true"})rejects([&]{parse(s);});
        CHECK(ui::binding_value({"x","eq","text","001"})=="001");CHECK(ui::binding_value({"x","eq","boolean","false"})==false);rejects([&]{ui::binding_value({"x","eq","boolean","False"});});
        for(const double v:{std::numeric_limits<double>::min(),std::numeric_limits<double>::max(),1.2345678901234567})CHECK(parse(Json(v).dump())==Json(v));
    }else if(name=="ATOMIC"){
        draft.select({"widget:chart"});const auto& w=widgets[2];auto in=proposed(w["bindings"][0],"field");const auto edit=ui::binding_edit(w,in,{"network.transmit_bytes"});draft.execute({edit});draft.undo();const auto before=*draft.scene();
        for(const std::string& field:std::vector<std::string>{"","bad field",std::string(257,'a')}){in.fields["field"]=field;rejects([&]{draft.execute({ui::binding_edit(w,in,{field})});});CHECK(*draft.scene()==before&&draft.redo_count()==1);}
        in=ui::binding_input(w["bindings"][0]);in.predicates={{"entity.id","eq","text",std::string(513,'x')}};rejects([&]{draft.execute({ui::binding_edit(w,in,{"network.receive_bytes"})});});
        auto table=ui::binding_input(widgets[1]["bindings"][0]);rejects([&]{ui::binding_edit(widgets[1],table,{"network.receive_bytes","network.receive_bytes"});});table.fields["kind"]="direct";rejects([&]{ui::binding_edit(widgets[1],table,{"a","b"});});
        auto legacy=widgets[2];legacy["bindings"]=Json::array({cases["descriptors"]["legacy"]});auto pin=ui::binding_input(legacy["bindings"][0]);CHECK(ui::binding_edit(legacy,pin,{"network.receive_bytes"}).bindings==legacy["bindings"]);
        rejects([&]{ui::binding_edit(legacy,pin,{"network.transmit_bytes"});});rejects([&]{ui::binding_descriptor(pin,w["bindings"][0],"singleton");});
        rejects([&]{ui::binding_edit(widgets[0],pin,{});});CHECK(*draft.scene()==before&&draft.undo_count()==0&&draft.redo_count()==1&&!draft.active_request());
    }else if(name=="BOUNDS"){
        const auto& b=widgets[2]["bindings"][0];auto in=ui::binding_input(b);in.predicates.assign(16,{"entity.id","eq","text","a"});in.sort.assign(8,{"entity.id","ascending"});in.fields["limit"]="256";CHECK(ui::binding_descriptor(in,b,"singleton")["limit"]==256);
        in.predicates.push_back({"entity.id","eq","text","b"});rejects([&]{ui::binding_descriptor(in,b,"singleton");});in.predicates.pop_back();in.sort.push_back({"entity.id","ascending"});rejects([&]{ui::binding_descriptor(in,b,"singleton");});in.sort.pop_back();
        for(const std::string n:{"0","257","01","1e2","+1"}){in.fields["limit"]=n;rejects([&]{ui::binding_descriptor(in,b,"singleton");});}
        in=proposed(b,"selector");std::reverse(in.predicates.begin(),in.predicates.end());std::reverse(in.sort.begin(),in.sort.end());const auto reversed=ui::binding_descriptor(in,b,"singleton");CHECK(reversed["predicates"][0]["value"]==9007199254740993ULL&&reversed["sort"][0]["field"]=="entity.id");
    }else if(name=="POLICY"){
        const auto& w=widgets[2];const auto edit=ui::binding_edit(w,proposed(w["bindings"][0],"field"),{"network.transmit_bytes"});auto denied=policy(8);denied.denied_capabilities.insert("scene.content");draft.policy(denied);rejects([&]{draft.execute({edit});});CHECK(!draft.dirty()&&draft.undo_count()==0);
        draft.policy(policy(9));draft.execute({edit});denied=policy(10);denied.disclosure.clear();draft.policy(denied);CHECK(!draft.scene()&&draft.history_bytes()==0);draft.policy(policy(11));CHECK(!draft.available());draft.reload(fixture.authored,"E2",fixture.resources());CHECK(*draft.scene()==fixture.authored.scene);
    }else throw std::runtime_error("unknown binding authoring family");
}
