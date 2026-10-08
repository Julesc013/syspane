#include "theme_history_fixture.hpp"
#include "generation_store_linux.hpp"
#include <iostream>
#include <unistd.h>
namespace {
using namespace theme_history_fixture;
void need(bool b){if(!b)throw std::runtime_error("native recovery state");}
void output(const Json& v){std::cout<<v.dump()<<std::endl;}
template<class F>bool rejected(F fn){try{fn();return false;}catch(const syspane::protocol::Error&){return true;}}
c::Policy grant(){auto p=policy();p.disclosure[{"desktop","history"}]={"sensitive"};return p;}
ui::SettingsResources admitted(const c::ResourceSet& r){auto v=context(r);v.capabilities.insert("editor.recovery");return v;}
struct Loaded {c::Committed value;ui::RecoveryIdentity id;};
Loaded read(const std::string& path){syspane::platform::LinuxGenerationStore s(path);return {s.load(),{"profile:primary",s.generation_token()}};}
void stage(ui::EditorDraft& d,const Json& scene){
    std::vector<ui::SceneEdit> edits{ui::RemoveWidgets{d.scene()->at("roots").get<std::vector<std::string>>()}};
    std::size_t index=0;for(const auto& w:scene["widgets"])edits.push_back(ui::InsertWidget{w,std::nullopt,index++});need(d.execute(edits));
}
}
int main(int argc,char** argv){try{
    need(argc==4&&::geteuid()!=0);const std::string root=argv[1],path=argv[2],mode=argv[3];
    if(mode.substr(0,6)=="token-"){
        syspane::platform::LinuxGenerationStore s(path,[&](const char* phase){if(mode=="token-poisoned"&&std::string(phase)=="selected")throw syspane::protocol::Error("probe.cut");});
        if(mode=="token-poisoned")need(s.publish(s.load(),[]{})==c::Publication::unknown);
        if(mode=="token-read"){output({{"event","token"},{"token",s.generation_token()},{"scene",s.load().documents.scene}});return 0;}
        need(rejected([&]{(void)s.generation_token();}));const bool readable=!rejected([&]{(void)s.load();});
        output({{"event","token-unavailable"},{"readable",readable},{"fallback",s.recovered_previous()}});return 0;
    }
    auto loaded=read(path);const auto cases=settings_fixture::read(root+"/tests/editor/recovery-draft-cases.json");
    ui::EditorDraft d(authority(),grant(),loaded.value.documents,"E1",admitted(*loaded.value.resources),true);
    if(mode=="capture"||mode=="capture-theme"){
        if(mode=="capture-theme")need(fonts(d,cases["theme_artifacts"]["first"]));else stage(d,cases["scene"]);
        output({{"event","captured"},{"token",loaded.id.generation},{"record",*d.recovery_snapshot(loaded.id)}});return 0;
    }
    std::string line;need(static_cast<bool>(std::getline(std::cin,line)));const auto bytes=Json::parse(line).get<std::string>();
    if(mode=="revoked"||mode=="wrong-generation"){
        if(mode=="revoked"){auto p=grant();p.revision=8;p.disclosure.erase({"desktop","history"});d.policy(p);}
        need(rejected([&]{d.inspect_recovery(bytes,loaded.id);})&&rejected([&]{d.restore_recovery(bytes,loaded.id);}));
        need(!d.dirty()&&!d.active_request()&&d.undo_count()==0);
        output({{"event","refused"},{"scene",*d.scene()},{"token",loaded.id.generation}});return 0;
    }
    const auto info=d.inspect_recovery(bytes,loaded.id);need(info.revision==40&&!d.dirty()&&d.undo_count()==0);
    need(d.restore_recovery(bytes,loaded.id)&&d.undo_count()==1&&d.selection().empty());const auto restored=*d.scene();
    need(d.undo()&&!d.dirty()&&*d.scene()==loaded.value.documents.scene);need(d.redo()&&*d.scene()==restored);
    output({{"event","restored"},{"scene",restored},{"theme",d.resources()->theme()},{"selection",d.resources()->selection()},{"token",loaded.id.generation}});
    const auto request=*d.begin("commit","recovery:apply");output({{"event","request"},{"body",request.body}});
    const bool lost=mode=="lost"||mode=="theme-lost";
    if(lost){d.disconnected();need(d.state()==ui::DraftState::unknown&&d.active_request()->body==request.body);}
    need(static_cast<bool>(std::getline(std::cin,line)));const auto result=Json::parse(line);
    need(lost?d.reconciled(request.ticket,"Q","E2",result):d.complete(request.ticket,result));
    need(!d.dirty()&&!d.active_request()&&d.undo_count()==0&&d.revision()==41);auto scene=*d.scene();
    if(mode=="wrong-report")scene["widgets"][0]["title"]="wrong recovery oracle";
    output({{"event","accepted"},{"scene",scene},{"theme",d.resources()->theme()},{"selection",d.resources()->selection()}});
    d.close();loaded=read(path);ui::EditorDraft fresh(authority(),grant(),loaded.value.documents,"E2",admitted(*loaded.value.resources),true);
    need(rejected([&]{fresh.inspect_recovery(bytes,loaded.id);})&&rejected([&]{fresh.restore_recovery(bytes,loaded.id);}));
    need(!fresh.dirty()&&!fresh.active_request()&&fresh.undo_count()==0&&fresh.revision()==41);
    output({{"event","reloaded"},{"old_record_rejected",true},{"scene",*fresh.scene()},{"theme",fresh.resources()->theme()},{"selection",fresh.resources()->selection()},{"token",loaded.id.generation}});return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
