#include "editor_content.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <algorithm>
#include <limits>
#include <locale>
namespace {
namespace ui=syspane::interfaces;namespace c=syspane::configuration;namespace p=syspane::protocol;using c::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("content properties assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Policy policy(std::uint64_t revision=7){c::Policy p;p.available=true;p.revision=revision;p.disclosure[{"desktop","inspector"}]={"operational"};p.disclosure[{"desktop","accessibility"}]={"operational"};return p;}
ui::ContentInput proposed(const Json& widget,const std::string& name,const Json& cases){auto in=ui::content_input(widget);
    if(name=="table"||name=="order"){in.columns[0].label="Received\nbytes";in.columns[1].label="Sent bytes";if(name=="order")std::reverse(in.columns.begin(),in.columns.end());}
    if(name=="chart"){in.fields["window_ms"]="2000";in.fields["max_points"]="32";in.fields["interpolation"]="step";in.fields["axis"]="fixed";in.fields["minimum"]="-5.5";in.fields["maximum"]="1e2";in.fields["include_zero"]="invalid inactive";}
    if(name=="chart-auto"){in.fields["window_ms"]="1000";in.fields["max_points"]="2";in.fields["include_zero"]="false";in.fields["minimum"]="invalid inactive";in.fields["maximum"]="invalid inactive";}
    if(name=="image"){in.asset=cases["gray_asset"];in.fields["alt"]="Gray replacement";in.fields["width_dip"]="9.6e1";in.fields["height_dip"]="80";in.fields["fit"]="stretch";}
    return in;
}
}
void run_content_properties(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root,"tests/editor/content-properties-fixture.json");const auto cases=settings_fixture::read(root+"/tests/editor/content-properties-cases.json");
    const c::Authority authority{true,"desktop",{"desktop"}};const auto snapshot=f.catalog->resources(f.document["selection"],f.authored);const auto choices=ui::content_choices(*snapshot);
    ui::EditorDraft draft(authority,policy(),f.authored,"E1",f.resources());const auto& widgets=f.authored.scene["widgets"];
    if(name=="MAPPING"||name=="HISTORY"){
        for(const std::string mode:{"table","order","chart","chart-auto","image","theme","inherit"}){
            std::size_t index=mode=="table"||mode=="order"?1:mode=="chart"||mode=="chart-auto"?2:3;
            const auto& w=widgets[index];draft.select({w["id"]});std::vector<ui::SceneEdit> edits;
            if(mode=="theme"||mode=="inherit")edits.push_back(ui::content_theme(mode=="theme"?Json("theme:contrast"):Json(),choices));
            else {edits.push_back(ui::content_edit(w,proposed(w,mode,cases),choices));edits.push_back(ui::content_theme(nullptr,choices));}
            const bool changed=draft.execute(edits);CHECK(*draft.scene()==cases["expected"][mode]);CHECK(changed==(mode!="inherit"));CHECK(draft.undo_count()==(changed?1u:0u));
            CHECK(!draft.execute(edits));if(changed){CHECK(draft.undo()&&*draft.scene()==f.authored.scene);CHECK(draft.selection()==std::vector<std::string>{w["id"]});CHECK(draft.redo()&&*draft.scene()==cases["expected"][mode]);}
            if(name=="HISTORY"&&changed){ui::EditorDraft submitted(authority,policy(),f.authored,"E1",f.resources());submitted.execute(edits);const auto q=submitted.begin("commit","properties:"+mode);CHECK(q&&c::parse_command(q->body)["operations"][0]["scene"]==cases["expected"][mode]);rejects([&]{submitted.execute(edits);});draft.discard();}
            else draft.discard();
        }
    }else if(name=="NUMBERS"){
        for(const std::string v:{""," 2","2 ","02","+2","-2","2.0","2e3","4294967296","99999999999"})rejects([&]{ui::content_integer(v,2,4096);});
        CHECK(ui::content_integer("2",2,4096)==2&&ui::content_integer("4096",2,4096)==4096);
        for(const std::string v:{""," 2","2 ",".5","2.","nan","NaN","inf","1,5","0x2","1e","1e9999","--2","2\n"})rejects([&]{ui::content_number(v);});
        CHECK(ui::content_number("+2.5E+2")==250&&ui::content_number("-5.5")==-5.5&&ui::content_number("1e-2")==0.01);
        rejects([&]{ui::content_number(std::string(65,'1'));});
        struct Comma:std::numpunct<char>{char do_decimal_point()const override{return ',';}};const auto previous=std::locale();std::locale::global(std::locale(previous,new Comma));
        try{for(const double n:{std::numeric_limits<double>::min(),std::numeric_limits<double>::max(),1.2345678901234567,-1.2345678901234567}){auto w=widgets[2];w["content"]["axis"]={{"mode","fixed"},{"minimum",n},{"maximum",n}};const auto in=ui::content_input(w);CHECK(ui::content_number(in.fields.at("minimum"))==n);}CHECK(ui::content_number("1.5")==1.5);}catch(...){std::locale::global(previous);throw;}std::locale::global(previous);
    }else if(name=="ATOMIC"){
        draft.select({"widget:table"});const auto before=*draft.scene();auto input=proposed(widgets[1],"table",cases);
        for(const std::string& label:{std::string(129,'x'),std::string("bad\tlabel"),std::string("bad\x01label")}){input.columns[0].label=label;rejects([&]{draft.execute({ui::content_theme("theme:contrast",choices),ui::content_edit(widgets[1],input,choices)});});CHECK(*draft.scene()==before&&!draft.dirty()&&draft.undo_count()==0&&!draft.active_request());}
        input=ui::content_input(widgets[1]);input.columns[1].original=0;rejects([&]{ui::content_edit(widgets[1],input,choices);});input.columns.pop_back();rejects([&]{ui::content_edit(widgets[1],input,choices);});
        auto image=ui::content_input(widgets[3]);image.asset["sha256"]=std::string(64,'0');rejects([&]{ui::content_edit(widgets[3],image,choices);});
        rejects([&]{ui::content_theme("theme:unadmitted",choices);});
        image=ui::content_input(widgets[3]);image.fields["alt"]=std::string(1025,'a');rejects([&]{draft.execute({ui::content_edit(widgets[3],image,choices)});});
        for(const std::string n:{"0","4097","1e9999"}){image=ui::content_input(widgets[3]);image.fields["width_dip"]=n;rejects([&]{ui::content_edit(widgets[3],image,choices);});}
        auto chart=proposed(widgets[2],"chart",cases);chart.fields["minimum"]="100";rejects([&]{ui::content_edit(widgets[2],chart,choices);});
        CHECK(*draft.scene()==before&&draft.selection()==std::vector<std::string>{"widget:table"}&&draft.undo_count()==0);
    }else if(name=="CHOICES"){
        CHECK(choices.images.size()==2&&choices.themes.size()==3);CHECK(choices.images[1].value==cases["gray_asset"]);
        for(const auto& choice:choices.images){CHECK(choice.label.find("package:properties-native / 0.1.0 / images/")==0);auto in=ui::content_input(widgets[3]);in.asset=choice.value;draft.execute({ui::content_edit(widgets[3],in,choices)});draft.discard();}
        for(const auto& w:widgets){const auto edit=ui::content_edit(w,ui::content_input(w),choices);CHECK(edit.content==w["content"]&&edit.bindings==w["bindings"]);}
        auto table=widgets[1];table["bindings"]=Json::array();table["content"]["columns"]=Json::array();for(unsigned n=0;n<256;++n){auto b=widgets[1]["bindings"][0];b["field"]="network.field"+std::to_string(n);table["bindings"].push_back(b);table["content"]["columns"].push_back({{"label",std::to_string(n)}});}auto in=ui::content_input(table);std::reverse(in.columns.begin(),in.columns.end());const auto result=ui::content_edit(table,in,choices);CHECK(result.bindings[255]==table["bindings"][0]&&result.content["columns"][0]["label"]=="255");
    }else if(name=="POLICY"){
        const auto edit=ui::content_edit(widgets[3],proposed(widgets[3],"image",cases),choices);auto next=policy(8);next.denied_capabilities.insert("scene.content");draft.policy(next);rejects([&]{draft.execute({edit});});CHECK(*draft.scene()==f.authored.scene&&draft.undo_count()==0);
        draft.policy(policy(9));draft.execute({edit});next=policy(10);next.disclosure.clear();draft.policy(next);CHECK(!draft.scene()&&draft.history_bytes()==0);draft.policy(policy(11));CHECK(!draft.available());
        draft.reload(f.authored,"E2",f.resources());CHECK(draft.available());
    }else throw std::runtime_error("unknown content properties family");
}
