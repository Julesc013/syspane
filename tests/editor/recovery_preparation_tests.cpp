#include "theme_history_fixture.hpp"
#include <iostream>
#include <thread>

namespace {
using namespace theme_history_fixture;
void check(bool ok,int line){if(!ok)throw std::runtime_error("preparation assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f,const char* code=nullptr){bool caught=false;try{f();}catch(const syspane::protocol::Error& e){caught=true;if(code)CHECK(std::string(e.what())==code);}CHECK(caught);}
c::Policy grant(std::uint64_t revision=7){auto p=policy(revision);p.disclosure[{"desktop","history"}]={"sensitive"};return p;}
ui::SettingsResources admitted(const settings_fixture::Fixture& f){auto r=context(f);r.capabilities.insert("editor.recovery");return r;}
std::string wrap(const Json& cases,const Json& command){auto value=cases["envelope"];value["command"]=command.dump();return value.dump();}
void stage(ui::EditorDraft& d,const Json& scene){
    std::vector<ui::SceneEdit> edits{ui::RemoveWidgets{d.scene()->at("roots").get<std::vector<std::string>>()}};
    std::size_t index=0;for(const auto& w:scene["widgets"])edits.push_back(ui::InsertWidget{w,std::nullopt,index++});
    CHECK(d.execute(edits)&&*d.scene()==scene);
}
#include "recovery_submission.hpp"
void run(const std::string& family,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/recovery-draft-cases.json");
    const ui::RecoveryIdentity id{cases["identity"]["profile"],cases["identity"]["generation"]};const auto bytes=cases["wire"].get<std::string>();
    auto fresh=[&]{return ui::EditorDraft(authority(),grant(),f.authored,"E1",admitted(f),true);};auto d=fresh();
    if(family=="SUBMISSION"){
        recovery_submission(f,cases,id);
    }else if(family=="CAPTURE"){
        auto clean=d.recovery_capture_work(id);CHECK(!d.recovery_capture(clean->run(),id));rejects([&]{clean->run();},"recovery.work_consumed");
        stage(d,cases["scene"]);const auto scene=*d.scene();const auto selection=d.selection();const auto resources=d.resources();const auto history=d.history_bytes();
        auto work=d.recovery_capture_work(id);std::unique_ptr<ui::RecoveryPrepared> result;std::exception_ptr failure;
        std::thread worker([&]{try{result=work->run();}catch(...){failure=std::current_exception();}});worker.join();if(failure)std::rethrow_exception(failure);
        CHECK(*d.scene()==scene&&d.selection()==selection&&d.resources()==resources&&d.history_bytes()==history);
        CHECK(d.recovery_capture(std::move(result),id)==std::optional<std::string>{bytes});
        auto prepared=d.recovery_capture_work(id)->run();d.select({});CHECK(d.recovery_capture(std::move(prepared),id)==std::optional<std::string>{bytes});
    }else if(family=="RESTORE"){
        auto prepared=d.recovery_restore_work(bytes,id)->run();CHECK(!d.dirty()&&d.undo_count()==0&&*d.scene()==f.authored.scene);
        const auto info=d.inspect_recovery(*prepared,id);CHECK(info.scene_id==f.authored.scene["scene_id"]&&info.revision==40&&info.widgets==cases["scene"]["widgets"].size()&&!info.theme_changed);
        d.select({"widget:text"});CHECK(d.restore_recovery(std::move(prepared),id));CHECK(*d.scene()==cases["scene"]&&d.selection().empty()&&d.undo_count()==1&&d.revision()==40&&!d.active_request());
        CHECK(d.recovery_capture(d.recovery_capture_work(id)->run(),id)==std::optional<std::string>{bytes});
        CHECK(d.undo()&&*d.scene()==f.authored.scene&&d.selection()==std::vector<std::string>{"widget:text"});CHECK(d.redo()&&*d.scene()==cases["scene"]);
        d.discard();d.select({"widget:text"});auto noop=cases["command"];noop["operations"][0]["scene"]=f.authored.scene;
        CHECK(!d.restore_recovery(d.recovery_restore_work(wrap(cases,noop),id)->run(),id));CHECK(!d.dirty()&&d.undo_count()==0&&d.selection()==std::vector<std::string>{"widget:text"});
    }else if(family=="THEME"){
        for(const char* name:{"first","second"}){
            CHECK(fonts(d,cases["theme_artifacts"][name]));const auto expected=wrap(cases,cases["theme_commands"][name]);
            CHECK(d.recovery_capture(d.recovery_capture_work(id)->run(),id)==std::optional<std::string>{expected});
            auto restored=fresh();auto result=restored.recovery_restore_work(expected,id)->run();CHECK(restored.inspect_recovery(*result,id).theme_changed);
            CHECK(restored.restore_recovery(std::move(result),id));CHECK(*restored.scene()==cases["theme_scenes"][name]&&restored.resources()->selection()==cases["theme_selections"][name]);
            CHECK(restored.resources()->theme()==cases["theme_artifacts"][name]["theme"]&&restored.resources()->base_packages()==d.resources()->base_packages());
            bool exact=false;for(const auto& p:restored.resources()->packages())if(p->manifest==cases["theme_artifacts"][name]["manifest"]){CHECK(p->assets.at("theme.json")==cases["theme_artifacts"][name]["asset"]);exact=true;}CHECK(exact);
            CHECK(restored.undo()&&*restored.scene()==f.authored.scene);CHECK(restored.redo()&&restored.resources()->theme()==cases["theme_artifacts"][name]["theme"]);
        }
    }else if(family=="INVALID"){
        for(const auto& raw:std::vector<std::string>{"","{","[]","null","{\"format\":0,\"format\":1}",std::string("\xef\xbb\xbf")+bytes}){
            auto work=d.recovery_restore_work(raw,id);rejects([&]{work->run();});rejects([&]{work->run();},"recovery.work_consumed");
        }
        for(unsigned n=0;n<9;++n){auto q=cases["command"];
            if(n==0)q["operations"][0]["scene"]["scene_id"]="scene:other";
            if(n==1)q["operations"][0]["scene"]["extensions"]["unexpected"]=true;
            if(n==2)q["expected_revision"]="41";
            if(n==3)q["operations"][0]["scene"]["roots"].push_back("widget:missing");
            if(n==4)q["content"]["package"]["sha256"]=std::string(64,'0');
            if(n==5)q["intent"]="commit";
            if(n==6)q["request_id"]="other";
            if(n==7){q=cases["theme_commands"]["first"];q["theme_edit"]["font"]["size_dip"]=31;}
            if(n==8){q=cases["theme_commands"]["first"];q["theme_edit"]["source"]["sha256"]=std::string(64,'0');}
            rejects([&]{d.recovery_restore_work(wrap(cases,q),id)->run();});CHECK(!d.dirty()&&d.undo_count()==0&&*d.scene()==f.authored.scene);
        }
        auto padded=bytes;padded.append(ui::recovery_record_limit-padded.size(),' ');CHECK(d.inspect_recovery(*d.recovery_restore_work(padded,id)->run(),id).revision==40);
        rejects([&]{d.recovery_restore_work(padded+" ",id);});
        auto capture=d.recovery_capture_work(id)->run();rejects([&]{d.inspect_recovery(*capture,id);},"recovery.prepared_kind");
        auto restore=d.recovery_restore_work(bytes,id)->run();rejects([&]{d.recovery_capture(std::move(restore),id);},"recovery.prepared_kind");
    }else if(family=="POLICY"){
        for(const char* cap:{"editor.recovery","scene.replace","settings.preview","scene.content","content.select"}){
            auto subject=fresh();auto result=subject.recovery_restore_work(bytes,id)->run();auto revoked=grant(8);revoked.denied_capabilities.insert(cap);subject.policy(revoked);
            CHECK(!subject.recovery_available());rejects([&]{subject.inspect_recovery(*result,id);});subject.policy(grant(9));rejects([&]{subject.inspect_recovery(*result,id);},"recovery.prepared_stale");
            CHECK(subject.restore_recovery(subject.recovery_restore_work(bytes,id)->run(),id));
        }
        auto missing=admitted(f);missing.capabilities.erase("editor.recovery");ui::EditorDraft disabled(authority(),grant(),f.authored,"E1",missing,true);rejects([&]{disabled.recovery_capture_work(id);});
        auto denied=grant(8);denied.disclosure[{"desktop","history"}]={"operational"};auto work=d.recovery_restore_work(bytes,id);d.policy(denied);auto result=work->run();rejects([&]{d.restore_recovery(std::move(result),id);});
    }else if(family=="INVALIDATION"){
        for(unsigned n=0;n<19;++n)for(bool completed:{false,true}){
            auto subject=fresh();auto work=subject.recovery_restore_work(bytes,id);auto capture=subject.recovery_capture_work(id);auto result=completed?work->run():nullptr;
            try{
                if(n==0)subject.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,subject.scene()->at("widgets")[0]["title"]}});
                if(n==1)subject.execute({});
                if(n==2)subject.undo();
                if(n==3)subject.redo();
                if(n==4)subject.discard();
                if(n==5)subject.policy(grant(8));
                if(n==6)subject.reload(f.authored,"E2",admitted(f));
                if(n==7)subject.begin("preview","no:change");
                if(n==8)subject.cancel_request();
                if(n==9)subject.disconnected();
                if(n==10)subject.complete(123,Json());
                if(n==11)subject.reconciled(123,"Q","E2",Json());
                if(n==12)subject.set_theme_fonts(Json(),Json());
                if(n==13)subject.restore_recovery("{",id);
                if(n==14)subject.restore_recovery(std::unique_ptr<ui::RecoveryPrepared>{},id);
                if(n==15){auto wrong=fresh();subject.restore_recovery(wrong.recovery_restore_work(bytes,id)->run(),id);}
                if(n==16){auto noop=cases["command"];noop["operations"][0]["scene"]=f.authored.scene;subject.restore_recovery(subject.recovery_restore_work(wrap(cases,noop),id)->run(),id);}
                if(n==17)subject.execute({ui::MoveWidgets{{"widget:text"},1,0}});
                if(n==18)subject.close();
            }catch(const syspane::protocol::Error&){}
            if(!completed)result=work->run();
            rejects([&]{subject.inspect_recovery(*result,id);});rejects([&]{subject.recovery_capture(capture->run(),id);});
        }
    }else if(family=="IDENTITY"){
        for(const auto& wrong:std::vector<ui::RecoveryIdentity>{{"profile:other",id.generation},{id.profile,std::string(64,'5')}}){
            rejects([&]{d.recovery_restore_work(bytes,wrong)->run();});auto result=d.recovery_restore_work(bytes,id)->run();rejects([&]{d.inspect_recovery(*result,wrong);},"recovery.prepared_stale");
            CHECK(d.inspect_recovery(*result,id).revision==40);
        }
        auto result=d.recovery_restore_work(bytes,id)->run();auto copy=d;rejects([&]{copy.inspect_recovery(*result,id);},"recovery.prepared_stale");
        auto assigned=fresh();assigned=d;rejects([&]{assigned.inspect_recovery(*result,id);},"recovery.prepared_stale");
        auto moved=std::move(copy);rejects([&]{moved.inspect_recovery(*result,id);},"recovery.prepared_stale");CHECK(d.inspect_recovery(*result,id).revision==40);
        auto prior=d.recovery_restore_work(bytes,id)->run();d=assigned;rejects([&]{d.inspect_recovery(*prior,id);},"recovery.prepared_stale");
    }else if(family=="LIFETIME"){
        std::unique_ptr<ui::RecoveryWork> work;{auto origin=fresh();stage(origin,cases["scene"]);work=origin.recovery_capture_work(id);}
        auto captured=work->run();rejects([&]{d.recovery_capture(std::move(captured),id);},"recovery.prepared_stale");
        {auto origin=fresh();work=origin.recovery_restore_work(bytes,id);}auto orphan=work->run();rejects([&]{d.inspect_recovery(*orphan,id);},"recovery.prepared_stale");
        auto old=d.recovery_restore_work(bytes,id)->run();CHECK(d.restore_recovery(d.recovery_restore_work(bytes,id)->run(),id));auto request=*d.begin("commit","prepared:apply");
        Store store(f);c::Transactions tx(store,"E1",store.provider());auto accepted=tx.submit("p","C",request.body,authority(),[]{return grant();},0);CHECK(accepted["outcome"]=="accepted");
        CHECK(d.complete(request.ticket,accepted)&&d.revision()==41&&store.writes==1);rejects([&]{d.inspect_recovery(*old,id);});
        auto expected=cases["scene"];expected["revision"]="41";CHECK(store.current.documents.scene==expected);
    }else throw std::runtime_error("unknown preparation family");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
