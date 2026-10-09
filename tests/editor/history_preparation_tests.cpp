#include "theme_history_fixture.hpp"
#include <iostream>
#include <thread>

namespace {
using namespace theme_history_fixture;
void check(bool ok,int line){if(!ok)throw std::runtime_error("history preparation assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f,const char* code=nullptr){bool caught=false;try{f();}catch(const syspane::protocol::Error& e){caught=true;if(code)CHECK(std::string(e.what())==code);}CHECK(caught);}
ui::SceneEdit title(const std::string& value){return ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,value};}
bool travel(ui::EditorDraft& draft,bool forward){
#ifdef SYSPANE_TEST_HISTORY_PREPARATION
    const auto scene=*draft.scene(),selection=Json(draft.selection());const auto history=draft.history_bytes();const auto resources=draft.resources();
    auto work=draft.history_work(forward);if(!work)return false;
    std::unique_ptr<ui::HistoryPrepared> result;std::exception_ptr error;
    std::thread worker([&]{try{result=work->run();}catch(...){error=std::current_exception();}});worker.join();if(error)std::rethrow_exception(error);
    CHECK(*draft.scene()==scene&&Json(draft.selection())==selection&&draft.history_bytes()==history&&draft.resources()==resources);
    rejects([&]{work->run();},"editor.history_consumed");return draft.adopt_history(std::move(result));
#else
    return forward?draft.redo():draft.undo();
#endif
}
void run(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);auto fresh=[&]{return ui::EditorDraft(authority(),policy(),f.authored,"E1",context(f),true);};auto d=fresh();
    auto original=f.authored.scene,one=original,two=original;one["widgets"][0]["title"]="First";two["widgets"][0]["title"]="Second";
    auto changed=[&]{CHECK(d.execute({title("First")}));};
    if(name=="TRACE"){
        CHECK(!travel(d,false)&&!travel(d,true));d.select({"widget:text"});changed();d.select({});CHECK(d.execute({title("Second")}));
        const auto bytes=d.history_bytes();CHECK(*d.scene()==two&&d.undo_count()==2&&d.redo_count()==0);
        CHECK(travel(d,false)&&*d.scene()==one&&d.selection().empty()&&d.undo_count()==1&&d.redo_count()==1&&d.history_bytes()==bytes&&d.may_submit("commit"));
        CHECK(travel(d,false)&&*d.scene()==original&&d.selection()==std::vector<std::string>{"widget:text"}&&!d.dirty()&&!d.may_submit("commit")&&d.undo_count()==0&&d.redo_count()==2);
        CHECK(!travel(d,false)&&travel(d,true)&&*d.scene()==one&&d.selection()==std::vector<std::string>{"widget:text"});
        CHECK(travel(d,true)&&*d.scene()==two&&d.selection().empty()&&!travel(d,true)&&d.history_bytes()==bytes);
        CHECK(travel(d,false));CHECK(d.execute({title("Branch")}));CHECK(d.undo_count()==2&&d.redo_count()==0&&!travel(d,true));
    }else if(name=="THEME"){
        const auto cases=settings_fixture::read(root+"/tests/editor/theme-history-cases.json");
        CHECK(fonts(d,cases["artifacts"]["first"])&&fonts(d,cases["artifacts"]["second"]));
        CHECK(travel(d,false)&&*d.scene()==cases["scenes"]["first"]&&d.resources()->selection()==cases["selections"]["first"]&&d.resources()->theme()==cases["artifacts"]["first"]["theme"]);
        CHECK(travel(d,false)&&*d.scene()==original&&!d.may_submit("preview"));
        CHECK(travel(d,true)&&travel(d,true)&&*d.scene()==cases["scenes"]["second"]&&d.resources()->selection()==cases["selections"]["second"]);
        auto q=*d.begin("commit","history:apply");auto expected=cases["commands"]["second"];expected["request_id"]="history:apply";CHECK(c::parse_command(q.body)==expected);
    }else if(name=="LIMITS"){
        for(unsigned n=0;n<66;++n)CHECK(d.execute({title("History "+std::to_string(n))}));
        CHECK(d.undo_count()==64&&d.history_bytes()<=8*1024*1024);const auto bytes=d.history_bytes();
        for(unsigned n=0;n<64;++n){CHECK(travel(d,false));}
        auto expected=original;expected["widgets"][0]["title"]="History 1";
        CHECK(*d.scene()==expected&&d.undo_count()==0&&d.redo_count()==64&&!travel(d,false)&&d.history_bytes()==bytes);
        for(unsigned n=0;n<64;++n){CHECK(travel(d,true));}
        expected["widgets"][0]["title"]="History 65";
        CHECK(*d.scene()==expected&&d.undo_count()==64&&!travel(d,true)&&d.history_bytes()==bytes);
    }else if(name=="LEGACY"){
        ui::EditorDraft legacy(authority(),policy(),f.authored,"E1",context(f),false);
        auto large=original;std::vector<ui::SceneEdit> additions;
        for(unsigned n=0;n<70;++n){auto w=original["widgets"][0];w["id"]="large:"+std::to_string(n);w["content"]["body"]=std::string(1024,'x');
            additions.push_back(ui::InsertWidget{w,std::nullopt,original["roots"].size()+n});large["widgets"].push_back(w);large["roots"].push_back(w["id"]);}
        CHECK(legacy.execute(additions)&&*legacy.scene()==large);
        CHECK(!legacy.may_submit("commit")&&!legacy.may_submit("preview"));
        CHECK(travel(legacy,false)&&*legacy.scene()==original&&!legacy.dirty());
        CHECK(travel(legacy,true)&&*legacy.scene()==large&&!legacy.may_submit("commit"));
    }else if(name=="TRANSACTION"){
        changed();CHECK(d.execute({title("Second")}));CHECK(travel(d,false));auto first=*d.begin("preview","history:preview");
        Store store(f);c::Transactions tx(store,"E1",store.provider());auto reply=tx.submit("p","C",first.body,authority(),[]{return policy();},0);
        CHECK(reply["outcome"]=="preview"&&d.complete(first.ticket,reply));CHECK(travel(d,true));auto q=*d.begin("commit","history:commit");
        CHECK(q.ticket==first.ticket+1&&q.epoch=="E1");const auto command=c::parse_command(q.body);CHECK(command["operations"]==Json::array({{{"op","scene.replace"},{"scene",two}}}));
        reply=tx.submit("p","C",q.body,authority(),[]{return policy();},0);CHECK(reply["outcome"]=="accepted"&&d.complete(q.ticket,reply)&&d.revision()==41&&d.undo_count()==0&&d.redo_count()==0);
        two["revision"]="41";CHECK(store.current.documents.scene==two&&store.writes==1);
#ifdef SYSPANE_TEST_HISTORY_PREPARATION
    }else if(name=="INVALIDATION"){
        for(unsigned n=0;n<18;++n)for(bool finished:{false,true}){
            auto subject=fresh();CHECK(subject.execute({title("First")}));auto work=subject.history_work(false);auto result=finished?work->run():nullptr;
            try{
                if(n==0)subject.select({});
                if(n==1)subject.select({"missing"});
                if(n==2)subject.execute({title("First")});
                if(n==3)subject.execute({});
                if(n==4)subject.undo();
                if(n==5)subject.redo();
                if(n==6)subject.discard();
                if(n==7)subject.policy(policy(8));
                if(n==8)subject.reload(f.authored,"E2",context(f));
                if(n==9)subject.begin("preview","pending");
                if(n==10)subject.cancel_request();
                if(n==11)subject.disconnected();
                if(n==12)subject.complete(99,Json());
                if(n==13)subject.reconciled(99,"Q","E2",Json());
                if(n==14)subject.set_theme_fonts(Json(),Json());
                if(n==15)subject.close();
                if(n==16)subject.history_work(true);
                if(n==17)subject.adopt_history({});
            }catch(const syspane::protocol::Error&){}
            if(!finished){result=work->run();}
            const auto scene=subject.scene()?*subject.scene():Json();const auto selection=subject.selection();const auto undo=subject.undo_count(),redo=subject.redo_count();
            rejects([&]{subject.adopt_history(std::move(result));});CHECK((subject.scene()?*subject.scene():Json())==scene&&subject.selection()==selection&&subject.undo_count()==undo&&subject.redo_count()==redo);
        }
    }else if(name=="IDENTITY"){
        changed();auto result=d.history_work(false)->run();auto copied=d;rejects([&]{copied.adopt_history(std::move(result));},"editor.history_stale");
        result=d.history_work(false)->run();auto assigned=fresh();assigned=d;rejects([&]{assigned.adopt_history(std::move(result));},"editor.history_stale");
        result=d.history_work(false)->run();auto moved=std::move(d);rejects([&]{moved.adopt_history(std::move(result));},"editor.history_stale");
        d=fresh();changed();result=d.history_work(false)->run();d=assigned;rejects([&]{d.adopt_history(std::move(result));},"editor.history_stale");
        std::unique_ptr<ui::HistoryWork> work;{auto origin=fresh();origin.execute({title("First")});work=origin.history_work(false);}
        result=work->run();rejects([&]{assigned.adopt_history(std::move(result));},"editor.history_stale");
    }else if(name=="POLICY"){
        for(const char* cap:{"scene.replace","settings.preview","content.select","scene.content"}){
            auto subject=fresh();subject.execute({title("First")});auto result=subject.history_work(false)->run();auto denied=policy(8);denied.denied_capabilities.insert(cap);subject.policy(denied);
            rejects([&]{subject.adopt_history(std::move(result));});subject.policy(policy(9));CHECK(travel(subject,false)&&*subject.scene()==original);
        }
        changed();auto denied=policy(8);denied.denied_capabilities.insert("settings.commit");d.policy(denied);CHECK(travel(d,false)&&travel(d,true));CHECK(d.may_submit("preview")&&!d.may_submit("commit"));
    }else if(name=="GUARDS"){
        changed();auto denied=policy(8);denied.denied_capabilities.insert("settings.preview");d.policy(denied);
        auto work=d.history_work(false);rejects([&]{work->run();},"policy.denied");rejects([&]{work->run();},"editor.history_consumed");
        CHECK(*d.scene()==one&&d.undo_count()==1&&d.redo_count()==0);
        d.policy(policy(9));auto result=d.history_work(false)->run();denied.revision=10;d.policy(denied);d.policy(policy(11));
        rejects([&]{d.adopt_history(std::move(result));});
        // A newer request and any refused adoption fence all older results.
        auto first=d.history_work(false)->run();auto second=d.history_work(false)->run();
        rejects([&]{d.adopt_history(std::move(first));},"editor.history_stale");
        rejects([&]{d.adopt_history(std::move(second));},"editor.history_stale");
        CHECK(travel(d,false)&&*d.scene()==original&&travel(d,true)&&*d.scene()==one);
        result=d.history_work(false)->run();CHECK(d.adopt_history(std::move(result)));
        rejects([&]{d.adopt_history(std::move(result));},"editor.history_prepared");
#endif
    }else throw std::runtime_error("unknown history preparation family");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
