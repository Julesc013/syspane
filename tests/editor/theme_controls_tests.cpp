#include "theme_history_fixture.hpp"
#include "editor_theme.hpp"
#include <iostream>
namespace {
using namespace theme_history_fixture;
void check(bool b,int line){if(!b)throw std::runtime_error("font controls assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool caught=false;try{f();}catch(const syspane::protocol::Error&){caught=true;}CHECK(caught);}
Json candidate(const Json& source,const Json& artifact){return ui::theme_control_edit(source,ui::theme_control_input(artifact.at("theme")));}
void run(const std::string& family,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/theme-controls-cases.json");const auto source=cases.at("source");
    f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};ui::EditorDraft d(authority(),policy(),f.authored,"E1",context(f),true);
    const auto apply=[&](const Json& theme){return d.set_theme_fonts(theme.at("font"),theme.value("font_roles",Json()));};
    if(family=="INPUT"){
        const auto input=ui::theme_control_input(source);CHECK(!input.explicit_roles&&input.fonts.roles.empty());CHECK(ui::theme_control_edit(source,input).dump()==source.dump());
        for(const char* key:{"base","roles","empty"}){const auto& artifact=cases["artifacts"][key];auto expected=artifact["theme"];expected["theme_id"]=source["theme_id"];CHECK(candidate(source,artifact).dump()==expected.dump());
            auto exact=artifact["theme"];exact["font"]["size_dip"]=19;CHECK(ui::theme_control_edit(exact,ui::theme_control_input(exact)).dump()==exact.dump());}
    }else if(family=="ROLE-MAP"){
        auto input=ui::theme_control_input(source);input.explicit_roles=true;auto explicit_empty=ui::theme_control_edit(source,input);CHECK(explicit_empty["schema_version"]=="0.2.0"&&explicit_empty["font_roles"].empty()&&explicit_empty["font"]["weight"]==400);
        CHECK(ui::theme_control_edit(explicit_empty,ui::theme_control_input(explicit_empty)).dump()==explicit_empty.dump());
        input=ui::theme_control_input(cases["artifacts"]["roles"]["theme"]);input.explicit_roles=false;for(auto& role:input.fonts.roles)role.second={"","invalid","-1","wrong"};CHECK(ui::theme_control_edit(source,input)==candidate(source,cases["artifacts"]["base"]));
        input.explicit_roles=true;rejects([&]{ui::theme_control_edit(source,input);});
        const auto authoring=settings_fixture::read(root+"/tests/editor/theme-authoring-cases.json");
        for(const auto& value:authoring["invalid_size"]){auto bad=ui::theme_control_input(source);bad.fonts.font.size_dip=value;rejects([&]{ui::theme_control_edit(source,bad);});}
        auto bad=ui::theme_control_input(source);bad.explicit_roles=true;bad.fonts.roles["unknown"]=bad.fonts.font;rejects([&]{ui::theme_control_edit(source,bad);});CHECK(!d.dirty());
    }else if(family=="HISTORY"){
        CHECK(apply(candidate(source,cases["artifacts"]["roles"]))&&d.undo_count()==1);CHECK(*d.scene()==cases["scenes"]["roles"]&&d.resources()->selection()==cases["selections"]["roles"]);
        CHECK(d.undo()&&!d.dirty()&&d.redo());Store store(f);c::Transactions tx(store,"E1",store.provider());auto q=*d.begin("commit","fonts");auto command=c::parse_command(q.body);CHECK(command["schema_version"]=="0.8.0"&&command["theme_edit"]["font_roles"]==cases["artifacts"]["roles"]["theme"]["font_roles"]);
        auto result=tx.submit("p","C",q.body,authority(),[]{return policy();},0);CHECK(result["outcome"]=="accepted"&&d.complete(q.ticket,result)&&d.undo_count()==0);
        CHECK(d.execute({ui::SceneThemeEdit{std::nullopt}}));q=*d.begin("commit","reset");command=c::parse_command(q.body);CHECK(command["theme_edit"].is_null()&&command["content"]==cases["base_selection"]);
        result=tx.submit("p","C",q.body,authority(),[]{return policy();},1);CHECK(result["outcome"]=="accepted"&&d.complete(q.ticket,result)&&d.revision()==42);
    }else if(family=="POLICY"){
        auto missing=context(f);missing.capabilities.erase("theme.typography");ui::EditorDraft old(authority(),policy(),f.authored,"E1",missing,true);CHECK(!old.theme_fonts_available());
        CHECK(apply(candidate(source,cases["artifacts"]["base"])));const auto request=*d.begin("commit","pending");CHECK(!d.theme_fonts_available());rejects([&]{apply(candidate(source,cases["artifacts"]["roles"]));});CHECK(d.active_request()->body==request.body);
        auto revoked=policy(8);revoked.denied_capabilities.insert("configuration.theme-overrides");d.policy(revoked);CHECK(!d.available()&&!d.resources()&&d.active_request()->body.empty()&&d.history_bytes()==0);
    }else throw std::runtime_error("unknown font controls family");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
