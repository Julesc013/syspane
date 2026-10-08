#include "theme_history_fixture.hpp"
#include "authored_equal.hpp"
#include <iostream>

namespace {
using namespace theme_history_fixture;
void check(bool ok,int line){if(!ok)throw std::runtime_error("recovery assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool rejected=false;try{f();}catch(const syspane::protocol::Error&){rejected=true;}CHECK(rejected);}
c::Policy grant(std::uint64_t revision=7){auto p=policy(revision);p.disclosure[{"desktop","history"}]={"sensitive"};return p;}
ui::SettingsResources admitted(const settings_fixture::Fixture& f){auto r=context(f);r.capabilities.insert("editor.recovery");return r;}
ui::SettingsResources admitted(const c::ResourceSet& r){auto value=context(r);value.capabilities.insert("editor.recovery");return value;}
ui::RecoveryIdentity identity(const Json& cases){return {cases["identity"]["profile"],cases["identity"]["generation"]};}
std::string wrap(const Json& cases,const Json& command){auto v=cases["envelope"];v["command"]=command.dump();return v.dump();}
void stage(ui::EditorDraft& d,const Json& scene){
    std::vector<ui::SceneEdit> edits{ui::RemoveWidgets{d.scene()->at("roots").get<std::vector<std::string>>()}};
    std::size_t position=0;for(const auto& widget:scene["widgets"])edits.push_back(ui::InsertWidget{widget,std::nullopt,position++});
    CHECK(d.execute(edits));CHECK(*d.scene()==scene);
}
struct Snapshot {
    Json scene,result;std::vector<std::string> selection;const c::ResourceSet* resources;std::size_t undo,redo,bytes;std::optional<ui::EditRequest> request;ui::DraftState state;
    explicit Snapshot(ui::EditorDraft& d):scene(d.scene()?*d.scene():Json()),result(d.last_result()),selection(d.selection()),resources(d.resources()),undo(d.undo_count()),redo(d.redo_count()),bytes(d.history_bytes()),request(d.active_request()),state(d.state()){}
    void same(ui::EditorDraft& d)const{
        CHECK((d.scene()?*d.scene():Json())==scene&&d.last_result()==result&&d.selection()==selection&&d.resources()==resources&&d.undo_count()==undo&&d.redo_count()==redo&&d.history_bytes()==bytes&&d.state()==state);
        CHECK(d.active_request().has_value()==request.has_value());if(request)CHECK(d.active_request()->ticket==request->ticket&&d.active_request()->body==request->body);
    }
};
void reject(ui::EditorDraft& d,std::string_view bytes,const ui::RecoveryIdentity& id){
    Snapshot before(d);rejects([&]{d.inspect_recovery(bytes,id);});before.same(d);rejects([&]{d.restore_recovery(bytes,id);});before.same(d);
}
void run(const std::string& family,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/recovery-draft-cases.json");
    CHECK(f.authored.settings==cases["authored"]["settings"]&&f.authored.scene==cases["authored"]["scene"]);
    const auto id=identity(cases);const auto bytes=cases["wire"].get<std::string>();
    ui::EditorDraft d(authority(),grant(),f.authored,"E1",admitted(f),true);
    if(family=="CAPTURE"){
        CHECK(d.recovery_available()&&!d.recovery_snapshot(id));d.select({"widget:text"});CHECK(!d.recovery_snapshot(id));
        stage(d,cases["scene"]);const Snapshot before(d);const auto record=d.recovery_snapshot(id);CHECK(record&&*record==bytes);before.same(d);
        d.select({});CHECK(*d.recovery_snapshot(id)==bytes);d.discard();CHECK(!d.recovery_snapshot(id));
        auto wrong=cases["scene"];wrong["widgets"][0]["title"]="wrong oracle";CHECK(wrong!=cases["scene"]);
        for(const auto& bad:std::vector<ui::RecoveryIdentity>{{"bad profile",id.generation},{id.profile,"x"},{id.profile,std::string(64,'A')}})rejects([&]{d.recovery_snapshot(bad);});
    }else if(family=="RESTORE"){
        d.select({"widget:text"});const Snapshot before(d);const auto info=d.inspect_recovery(bytes,id);before.same(d);
        CHECK(info.scene_id==f.authored.scene["scene_id"]&&info.revision==40&&info.widgets==cases["scene"]["widgets"].size()&&!info.theme_changed);
        const auto base=d.resources()->packages();CHECK(d.restore_recovery(bytes,id));CHECK(*d.scene()==cases["scene"]&&d.selection().empty()&&d.undo_count()==1&&d.dirty()&&d.revision()==40&&!d.active_request());
        CHECK(d.resources()->packages()==base&&*d.recovery_snapshot(id)==bytes);
        CHECK(d.undo()&&*d.scene()==f.authored.scene&&d.selection()==std::vector<std::string>{"widget:text"}&&!d.dirty());
        reject(d,bytes,id);CHECK(d.redo()&&*d.scene()==cases["scene"]&&d.selection().empty());d.discard();
        auto noop=cases["command"];noop["operations"][0]["scene"]=f.authored.scene;d.select({"widget:text"});const Snapshot clean(d);
        CHECK(!d.restore_recovery(wrap(cases,noop),id));clean.same(d);
    }else if(family=="THEME"){
        for(const char* name:{"first","second"}){
            CHECK(fonts(d,cases["theme_artifacts"][name]));const auto record=d.recovery_snapshot(id);CHECK(record&&Json::parse(*record)["command"]==cases["theme_commands"][name].dump());
            ui::EditorDraft restored(authority(),grant(),f.authored,"E2",admitted(f),true);CHECK(restored.inspect_recovery(*record,id).theme_changed);CHECK(restored.restore_recovery(*record,id));
            CHECK(*restored.scene()==cases["theme_scenes"][name]&&restored.resources()->selection()==cases["theme_selections"][name]&&restored.resources()->theme()==cases["theme_artifacts"][name]["theme"]);
            const auto base=restored.resources()->base_packages();CHECK(base==d.resources()->base_packages());
            bool exact=false;for(const auto& p:restored.resources()->packages())if(p->manifest==cases["theme_artifacts"][name]["manifest"]){CHECK(p->assets.at("theme.json")==cases["theme_artifacts"][name]["asset"]);exact=true;}CHECK(exact);
            CHECK(restored.undo()&&*restored.scene()==f.authored.scene);CHECK(restored.redo()&&restored.resources()->theme()==cases["theme_artifacts"][name]["theme"]);
        }
        auto current=f.authored;current.scene=cases["theme_scenes"]["second"];const auto retained=admitted(*d.resources());
        ui::EditorDraft versioned(authority(),grant(),current,"E2",retained,true);versioned.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"after committed font"}});
        const auto saved=*versioned.recovery_snapshot(id);auto expected=current.scene;expected["widgets"][0]["title"]="after committed font";
        ui::EditorDraft reopened(authority(),grant(),current,"E3",retained,true);CHECK(!reopened.inspect_recovery(saved,id).theme_changed&&reopened.restore_recovery(saved,id));CHECK(*reopened.scene()==expected&&reopened.resources()->theme()==cases["theme_artifacts"]["second"]["theme"]);
        auto q=cases["theme_commands"]["first"];d.discard();q["theme_edit"]["source"]["sha256"]=std::string(64,'0');reject(d,wrap(cases,q),id);
        q=cases["theme_commands"]["first"];q["theme_edit"]["font"]["size_dip"]=31;reject(d,wrap(cases,q),id);
        q=cases["theme_commands"]["first"];q["theme_edit"]=nullptr;reject(d,wrap(cases,q),id);
        auto denied=grant(8);denied.denied_capabilities.insert("theme.edit");d.policy(denied);reject(d,wrap(cases,cases["theme_commands"]["first"]),id);CHECK(d.restore_recovery(bytes,id));
    }else if(family=="IDENTITY"){
        reject(d,bytes,{"profile:other",id.generation});reject(d,bytes,{id.profile,std::string(64,'5')});
        auto v=cases["envelope"];v["identity"]["generation"]=std::string(64,'G');reject(d,v.dump(),id);
        auto current=f.authored;current.settings["revision"]=current.scene["revision"]="41";ui::EditorDraft newer(authority(),grant(),current,"E2",admitted(f),true);
        reject(newer,bytes,id);reject(newer,bytes,{id.profile,std::string(64,'5')});CHECK(newer.revision()==41&&!newer.dirty());
        // Native identity, not revision alone, binds a same-revision replacement.
        current=f.authored;current.scene["widgets"][0]["title"]="other accepted bytes";ui::EditorDraft replaced(authority(),grant(),current,"E2",admitted(f),true);
        reject(replaced,bytes,{id.profile,std::string(64,'6')});
    }else if(family=="INVALID"){
        for(const auto& raw:std::vector<std::string>{"","{","[]","null","{\"format\":0,\"format\":1}",std::string("\xef\xbb\xbf")+bytes})reject(d,raw,id);
        for(unsigned n=0;n<18;++n){auto envelope=cases["envelope"];auto q=cases["command"];
            if(n==0)envelope["unknown"]=true;
            if(n==1)envelope["identity"]["authorized"]=true;
            if(n==2)envelope["format"]="other";
            if(n==3)envelope["schema_version"]="0.2.0";
            if(n==4)q["intent"]="commit";
            if(n==5)q["request_id"]="stolen:request";
            if(n==6)q["operations"].push_back({{"op","settings.set"},{"path","display.reduced_motion"},{"value",false}});
            if(n==7)q["operations"][0]["scene"]["scene_id"]="scene:other";
            if(n==8)q["operations"][0]["scene"]["extensions"]["unknown.change"]=true;
            if(n==9)q["expected_revision"]="41";
            if(n==10)q["content"]["package"]["sha256"]=std::string(64,'0');
            if(n==11)q["policy_generation"]="18446744073709551616";
            if(n==12)q["operations"][0]["scene"]["roots"].push_back("widget:missing");
            if(n==13){for(auto& w:q["operations"][0]["scene"]["widgets"])if(w["kind"]=="image")w["content"]["asset"]["sha256"]=std::string(64,'0');}
            if(n==14)q["operations"][0]["scene"]["widgets"][0]["kind"]="unknown";
            envelope["command"]=q.dump();
            if(n==15)envelope["command"]=q;
            if(n==16)envelope["command"]="{\"schema_version\":0,\"schema_version\":1}";
            if(n==17)envelope.erase("identity");
            reject(d,envelope.dump(),id);
        }
    }else if(family=="BOUNDS"){
        auto padded=bytes;padded.append(ui::recovery_record_limit-padded.size(),' ');CHECK(d.inspect_recovery(padded,id).revision==40);reject(d,padded+" ",id);
        auto v=cases["envelope"];v["command"]=std::string(syspane::protocol::large_command_limit+1,' ');reject(d,v.dump(),id);
        auto q=cases["command"];Json nested=0;for(unsigned n=0;n<42;++n)nested=Json::array({nested});q["operations"][0]["scene"]["widgets"][0]["extensions"]["deep"]=nested;reject(d,wrap(cases,q),id);
        q=cases["command"];q["operations"][0]["scene"]["widgets"][0]["extensions"]["nodes"]=Json::array();for(unsigned n=0;n<18500;++n)q["operations"][0]["scene"]["widgets"][0]["extensions"]["nodes"].push_back(0);reject(d,wrap(cases,q),id);
        auto large=cases["scene"];large["widgets"][0]["extensions"]["quoted"]=std::string(110000,'"');stage(d,large);const auto captured=d.recovery_snapshot(id);CHECK(captured&&captured->size()>400000&&captured->size()<=ui::recovery_record_limit);
        d.discard();CHECK(d.restore_recovery(*captured,id)&&*d.scene()==large);
    }else if(family=="POLICY"){
        auto missing=admitted(f);missing.capabilities.erase("editor.recovery");ui::EditorDraft disabled(authority(),grant(),f.authored,"E1",missing,true);CHECK(!disabled.recovery_available());reject(disabled,bytes,id);
        ui::EditorDraft small(authority(),grant(),f.authored,"E1",admitted(f),false);CHECK(!small.recovery_available());reject(small,bytes,id);
        for(const char* capability:{"editor.recovery","scene.replace","settings.preview","scene.content"}){
            auto denied=grant();denied.denied_capabilities.insert(capability);ui::EditorDraft denied_draft(authority(),denied,f.authored,"E1",admitted(f),true);CHECK(!denied_draft.recovery_available());reject(denied_draft,bytes,id);
        }
        for(auto bad:std::vector<c::Authority>{{false,"desktop",{"desktop"}},{true,"desktop",{}},{true,"saver_settings",{"saver_settings"}}}){ui::EditorDraft denied(bad,grant(),f.authored,"E1",admitted(f),true);CHECK(!denied.recovery_available());reject(denied,bytes,id);}
        auto denied=grant(8);denied.disclosure[{"desktop","history"}]={"operational"};d.policy(denied);CHECK(!d.recovery_available());reject(d,bytes,id);d.policy(grant(9));CHECK(!d.dirty()&&d.restore_recovery(bytes,id));
        auto q=*d.begin("preview","current:policy");CHECK(c::parse_command(q.body)["policy_generation"]=="9");
    }else if(family=="LIFETIME"){
        stage(d,cases["scene"]);reject(d,bytes,id);const auto record=*d.recovery_snapshot(id);auto q=*d.begin("commit","pending");
        CHECK(!d.recovery_available());rejects([&]{d.recovery_snapshot(id);});reject(d,bytes,id);d.disconnected();CHECK(d.state()==ui::DraftState::unknown);reject(d,bytes,id);
        d.close();reject(d,bytes,id);CHECK(!d.recovery_available());
        ui::EditorDraft erased(authority(),grant(),f.authored,"E2",admitted(f),true);stage(erased,cases["scene"]);auto revoked=grant(8);revoked.disclosure.clear();erased.policy(revoked);CHECK(!erased.available());reject(erased,record,id);erased.policy(grant(9));CHECK(!erased.available());erased.reload(f.authored,"E2",admitted(f));CHECK(erased.restore_recovery(record,id));
        Store store(f);c::Transactions tx(store,"E1",store.provider());ui::EditorDraft conflict(authority(),grant(),f.authored,"E1",admitted(f),true);conflict.restore_recovery(bytes,id);auto request=*conflict.begin("commit","mine");auto other=c::parse_command(request.body);other["request_id"]="other";CHECK(tx.submit("p","C",other.dump(),authority(),[]{return grant();},0)["outcome"]=="accepted");auto result=tx.submit("p","C",request.body,authority(),[]{return grant();},1);CHECK(conflict.complete(request.ticket,result)&&conflict.state()==ui::DraftState::conflict);reject(conflict,bytes,id);
        (void)q;
    }else if(family=="VERSIONS"){
        CHECK(d.execute({ui::SetWidgetLocks{{"widget:text"},true}}));const auto locked=*d.recovery_snapshot(id);CHECK(Json::parse(Json::parse(locked)["command"].get<std::string>())["schema_version"]=="0.6.0");
        d.discard();CHECK(d.restore_recovery(locked,id)&&d.scene()->at("schema_version")=="0.4.0");CHECK(ui::edit_locked(*d.scene(),"widget:text"));
        d.discard();auto limited=admitted(f);limited.capabilities.erase("configuration.edit-locks");ui::EditorDraft unsupported(authority(),grant(),f.authored,"E1",limited,true);reject(unsupported,locked,id);
        auto newer=f.authored;newer.scene["schema_version"]="0.5.0";ui::EditorDraft advanced(authority(),grant(),newer,"E1",admitted(f),true);reject(advanced,bytes,id);
        auto scene=cases["scene"];scene["schema_version"]="0.5.0";auto q=cases["command"];q["schema_version"]="0.7.0";q["operations"][0]["scene"]=scene;CHECK(d.restore_recovery(wrap(cases,q),id)&&*d.scene()==scene);
    }else if(family=="COMMIT"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());CHECK(d.restore_recovery(bytes,id));CHECK(store.writes==0&&d.revision()==40);auto request=*d.begin("commit","recovery:apply");auto expected=cases["command"];expected["intent"]="commit";expected["request_id"]="recovery:apply";CHECK(c::parse_command(request.body)==expected);
        auto result=tx.submit("p","C",request.body,authority(),[]{return grant();},0);CHECK(result["outcome"]=="accepted"&&store.writes==1);d.disconnected();c::Transactions restarted(store,"E2",store.provider());auto response=Json{{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id",request.request},{"result",restarted.reconcile("p","E1",request.request,authority(),grant())}};
        CHECK(d.reconciled(request.ticket,"Q","E2",response)&&d.revision()==41&&!d.dirty()&&d.undo_count()==0&&!d.recovery_snapshot({id.profile,std::string(64,'5')}));
        reject(d,bytes,{id.profile,std::string(64,'5')});reject(d,bytes,id);CHECK(store.writes==1);
        auto saved=cases["scene"];saved["revision"]="41";CHECK(store.current.documents.scene==saved);
    }else throw std::runtime_error("unknown recovery family");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
