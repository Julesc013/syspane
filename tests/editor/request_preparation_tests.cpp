#include "theme_history_fixture.hpp"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <thread>

namespace {
using namespace theme_history_fixture;
void check(bool ok,int line){if(!ok)throw std::runtime_error("request preparation assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f,const char* code=nullptr){bool caught=false;try{f();}catch(const syspane::protocol::Error& e){caught=true;if(code)CHECK(std::string(e.what())==code);}CHECK(caught);}
ui::SceneEdit title(const std::string& value){return ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,value};}
using Clock=std::chrono::steady_clock;
auto us(Clock::time_point a,Clock::time_point b){return std::chrono::duration_cast<std::chrono::microseconds>(b-a).count();}
std::optional<ui::EditRequest> submit(ui::EditorDraft& d,const std::string& intent,const std::string& id,bool measure=false){
#ifdef SYSPANE_TEST_REQUEST_PREPARATION
    const auto scene=d.scene()?*d.scene():Json();const auto selection=d.selection();const auto history=d.history_bytes();
    const auto begin=Clock::now();auto work=d.request_work(intent,id);const auto captured=Clock::now();if(!work)return {};
    std::unique_ptr<ui::RequestPrepared> result;std::exception_ptr error;
    std::thread worker([&]{try{result=work->run();}catch(...){error=std::current_exception();}});worker.join();const auto computed=Clock::now();if(error)std::rethrow_exception(error);
    CHECK(!d.active_request()&&*d.scene()==scene&&d.selection()==selection&&d.history_bytes()==history);
    rejects([&]{work->run();},"editor.request_consumed");
    const auto adopting=Clock::now();auto q=d.adopt_request(std::move(result));const auto adopted=Clock::now();
    if(measure)std::cout<<"request-cost prepared capture_us="<<us(begin,captured)<<" run_and_join_us="<<us(captured,computed)<<" adopt_us="<<us(adopting,adopted)<<'\n';
    return q;
#else
    const auto begin=Clock::now();auto q=d.begin(intent,id);const auto done=Clock::now();
    if(measure)std::cout<<"request-cost synchronous begin_us="<<us(begin,done)<<'\n';
    return q;
#endif
}
Json expected(const settings_fixture::Fixture& f,const Json& scene,const std::string& intent,const std::string& id){
    return {{"schema_version","0.5.0"},{"request_id",id},{"expected_revision","40"},{"policy_generation","7"},{"intent",intent},
        {"operations",Json::array({{{"op","scene.replace"},{"scene",scene}}})},{"content",f.document["selection"]}};
}
}
void run_request_preparation(const std::string& name,const std::string& root){
    using namespace theme_history_fixture;
    settings_fixture::Fixture f(root);auto fresh=[&]{return ui::EditorDraft(authority(),policy(),f.authored,"E1",context(f),true);};auto d=fresh();
    const auto original=f.authored.scene;auto changed=original;changed["widgets"][0]["title"]="Prepared";
    if(name=="REQUEST-PREPARATION-TRACE"){
        CHECK(!submit(d,"commit","clean"));rejects([&]{submit(d,"bad","clean");},"settings.intent");rejects([&]{submit(d,"commit","");},"settings.request");
        d.select({"widget:text"});CHECK(d.execute({title("Prepared")}));const auto bytes=d.history_bytes();
        auto q=*submit(d,"commit","request:one");CHECK(q.ticket==1&&q.epoch=="E1"&&q.request=="request:one");
        CHECK(c::parse_command(q.body)==expected(f,changed,"commit","request:one"));
        CHECK(*d.scene()==changed&&d.selection()==std::vector<std::string>{"widget:text"}&&d.undo_count()==1&&d.history_bytes()==bytes&&d.state()==ui::DraftState::pending);
        rejects([&]{submit(d,"commit","again");},"settings.pending");auto active=*d.active_request();CHECK(active.ticket==q.ticket&&active.body==q.body);
        CHECK(d.cancel_request()->body==q.body&&!d.cancel_request());d.disconnected();CHECK(d.state()==ui::DraftState::unknown&&d.active_request()->body==q.body);
    }else if(name=="REQUEST-PREPARATION-THEME"){
        const auto cases=settings_fixture::read(root+"/tests/editor/theme-history-cases.json");CHECK(fonts(d,cases["artifacts"]["first"])&&fonts(d,cases["artifacts"]["second"]));
        const auto pin=d.resources()->theme_pin();auto q=*submit(d,"commit","request:theme");auto want=cases["commands"]["second"];want["request_id"]="request:theme";
        CHECK(c::parse_command(q.body)==want&&q.ticket==1&&q.epoch=="E1"&&d.resources()->theme_pin()==pin&&d.undo_count()==2);
    }else if(name=="REQUEST-PREPARATION-TRANSACTION"){
        d.execute({title("Prepared")});Store store(f);c::Transactions tx(store,"E1",store.provider());
        auto preview=*submit(d,"preview","request:preview");CHECK(c::parse_command(preview.body)==expected(f,changed,"preview","request:preview"));
        auto reply=tx.submit("p","C",preview.body,authority(),[]{return policy();},0);CHECK(reply["outcome"]=="preview"&&d.complete(preview.ticket,reply)&&d.revision()==40&&store.writes==0);
        auto q=*submit(d,"commit","request:commit");CHECK(q.ticket==preview.ticket+1&&c::parse_command(q.body)==expected(f,changed,"commit","request:commit"));
        reply=tx.submit("p","C",q.body,authority(),[]{return policy();},1);CHECK(reply["outcome"]=="accepted"&&store.writes==1);
        d.disconnected();CHECK(d.state()==ui::DraftState::unknown&&d.active_request()->body==q.body);
        CHECK(tx.submit("p","C",q.body,authority(),[]{return policy();},2)==reply&&store.writes==1);
        Json recovered={{"schema_version","0.1.0"},{"query_id","query:one"},{"original_producer_epoch","E1"},{"request_id",q.request},{"result",reply}};
        CHECK(d.reconciled(q.ticket,"query:one","E1",recovered)&&!d.active_request()&&d.revision()==41&&d.undo_count()==0);
        changed["revision"]="41";CHECK(*d.scene()==changed&&store.current.documents.scene==changed);
    }else if(name=="REQUEST-PREPARATION-LEGACY"){
        ui::EditorDraft old(authority(),policy(),f.authored,"E1",context(f),false);std::vector<ui::SceneEdit> additions;
        for(unsigned n=0;n<70;++n){auto w=original["widgets"][0];w["id"]="large:"+std::to_string(n);w["content"]["body"]=std::string(1024,'x');additions.push_back(ui::InsertWidget{w,std::nullopt,original["roots"].size()+n});}
        CHECK(old.execute(additions));const auto scene=*old.scene();rejects([&]{submit(old,"commit","oversize");});CHECK(!old.active_request()&&*old.scene()==scene&&old.undo_count()==1);
        old.discard();old.execute({title("Prepared")});CHECK(submit(old,"commit","small")->ticket==1);
    }else if(name=="REQUEST-PREPARATION-COST"){
        auto authored=f.authored;auto& scene=authored.scene;
        while(scene["widgets"].size()<256){auto w=original["widgets"][0];w["id"]="large:"+std::to_string(scene["widgets"].size());w["content"]["body"]="L";scene["roots"].push_back(w["id"]);scene["widgets"].push_back(w);}
        const auto bytes=scene.dump().size();CHECK(bytes<262144);std::size_t remaining=262144-bytes;
        for(std::size_t n=original["widgets"].size();n<256&&remaining;++n){auto& body=scene["widgets"][n]["content"]["body"];const auto count=std::min<std::size_t>(remaining,1023);body=std::string(1+count,'L');remaining-=count;}
        CHECK(!remaining&&scene.dump().size()==262144);ui::EditorDraft large(authority(),policy(),authored,"E1",context(f),true);
        auto name_value=scene["widgets"][0]["title"].get<std::string>();CHECK(!name_value.empty());name_value[0]=name_value[0]=='X'?'Y':'X';
        large.execute({title(name_value)});auto want=scene;want["widgets"][0]["title"]=name_value;
        const auto q=*submit(large,"commit","request:maximum",true);CHECK(c::parse_command(q.body)==expected(f,want,"commit","request:maximum")&&q.ticket==1&&q.body.size()<=327680);
#ifdef SYSPANE_TEST_REQUEST_PREPARATION
    }else if(name=="REQUEST-PREPARATION-INVALIDATION"){
        for(unsigned n=0;n<19;++n)for(bool finished:{false,true}){
            auto s=fresh();s.execute({title("Prepared")});auto work=s.request_work("commit","stale");auto result=finished?work->run():nullptr;
            try{
                if(n==0)s.select({});
                if(n==1)s.select({"missing"});
                if(n==2)s.execute({title("Prepared")});
                if(n==3)s.execute({});
                if(n==4)s.undo();
                if(n==5)s.redo();
                if(n==6)s.discard();
                if(n==7)s.policy(policy(8));
                if(n==8)s.reload(f.authored,"E2",context(f));
                if(n==9)s.begin("preview","pending");
                if(n==10)s.cancel_request();
                if(n==11)s.disconnected();
                if(n==12)s.complete(99,Json());
                if(n==13)s.reconciled(99,"Q","E2",Json());
                if(n==14)s.set_theme_fonts(Json(),Json());
                if(n==15)s.close();
                if(n==16)s.history_work(false);
                if(n==17)s.request_work("bad","new");
                if(n==18)s.adopt_request({});
            }catch(const syspane::protocol::Error&){}
            if(!finished){result=work->run();}
            const auto before=s.scene()?*s.scene():Json();const auto selection=s.selection();const auto count=s.undo_count();const auto active=s.active_request();
            rejects([&]{s.adopt_request(std::move(result));});CHECK((s.scene()?*s.scene():Json())==before&&s.selection()==selection&&s.undo_count()==count&&s.active_request().has_value()==active.has_value());
            if(active)CHECK(s.active_request()->ticket==active->ticket&&s.active_request()->body==active->body);
        }
    }else if(name=="REQUEST-PREPARATION-IDENTITY"){
        d.execute({title("Prepared")});auto result=d.request_work("commit","copied")->run();auto copy=d;rejects([&]{copy.adopt_request(std::move(result));});
        result=d.request_work("commit","moved")->run();auto moved=std::move(d);rejects([&]{moved.adopt_request(std::move(result));});
        auto s=fresh();s.execute({title("Prepared")});result=s.request_work("commit","assigned")->run();auto assigned=fresh();assigned=s;rejects([&]{assigned.adopt_request(std::move(result));});
        result=s.request_work("commit","replaced")->run();s=copy;rejects([&]{s.adopt_request(std::move(result));});
        std::unique_ptr<ui::RequestWork> work;{auto origin=fresh();origin.execute({title("Prepared")});work=origin.request_work("commit","destroyed");}
        result=work->run();rejects([&]{copy.adopt_request(std::move(result));});
        CHECK(submit(copy,"commit","fresh")->ticket==1);
    }else if(name=="REQUEST-PREPARATION-GUARDS"){
        d.execute({title("Prepared")});auto first=d.request_work("commit","old")->run();auto second=d.request_work("commit","new")->run();
        rejects([&]{d.adopt_request(std::move(first));},"editor.request_stale");rejects([&]{d.adopt_request(std::move(second));},"editor.request_stale");
        for(const char* cap:{"settings.commit","scene.replace","content.select","scene.content"}){
            auto s=fresh();s.execute({title("Prepared")});auto work=s.request_work("commit","denied");auto result=work->run();auto denied=policy(8);denied.denied_capabilities.insert(cap);s.policy(denied);s.policy(policy(9));
            rejects([&]{s.adopt_request(std::move(result));});CHECK(!s.active_request()&&s.undo_count()==1);
        }
        auto denied=policy(8);denied.denied_capabilities.insert("settings.commit");d.policy(denied);auto work=d.request_work("commit","denied");rejects([&]{work->run();},"policy.denied");rejects([&]{work->run();},"editor.request_consumed");
        d.policy(policy(9));auto ready=d.request_work("commit","good")->run();auto q=d.adopt_request(std::move(ready));CHECK(q.ticket==1);rejects([&]{d.adopt_request(std::move(ready));});CHECK(d.active_request()->body==q.body);
#endif
    }else throw std::runtime_error("unknown request preparation case");
}
