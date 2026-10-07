#include "settings_draft.hpp"
#include "transaction.hpp"
#include <fstream>
#include <iostream>
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;using p::Json;
void run_settings_content_case(const std::string&,const std::string&);
void check(bool value,const char* expression,int line){if(!value)throw std::runtime_error(std::string(expression)+":"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),#x,__LINE__)
std::string root;Json settings_cases;
Json read(const std::string& name){std::ifstream input(root+"/"+name);CHECK(input.good());Json v;input>>v;return v;}
c::Authored initial(){c::Authored v{read("spec/fixtures/valid/settings.json"),read("spec/fixtures/valid/scene-portable.json")};v.settings["revision"]=v.scene["revision"]=settings_cases["base_revision"];v.settings["extensions"]={{"author.note","Retain this"}};return v;}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(std::uint64_t revision=7){c::Policy v;v.available=true;v.revision=revision;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
ui::SettingsDraft draft(){return {authority(),policy(),initial(),"E1"};}
template<class F> void rejected(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
struct Store:c::GenerationStore {
    c::Committed current{initial(),{}},previous;unsigned writes=0;std::function<void()> before=[]{};
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{return {};}
    std::optional<c::Committed> reconcile(const std::string&,const std::string&,const std::string&)const override{return {};}
    c::Publication publish(const c::Committed& value,const std::function<void()>& guard)override{before();guard();previous=current;current=value;++writes;return c::Publication::durable;}
};
void edit(ui::SettingsDraft& d){d.set("sampling.resources_ms",1500);}
void run(const std::string& name){
    if(name=="DRAFT"){
        auto d=draft();CHECK(!d.dirty()&&d.revision()==40&&!d.begin("commit","empty"));edit(d);CHECK(d.dirty());d.revert();CHECK(!d.dirty()&&d.value("sampling.resources_ms").requested==1000);
        Store store;c::Transactions tx(store,"E1",[](const auto&){});edit(d);auto q=*d.begin("commit","R");auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0);CHECK(d.complete(q.ticket,result));
        CHECK(!d.dirty()&&d.revision()==41&&store.writes==1);auto scene=initial().scene;scene["revision"]="41";CHECK(tx.authored().scene==scene&&tx.authored().settings["extensions"]==initial().settings["extensions"]);CHECK(!d.begin("commit","empty-again"));
    }else if(name=="VALUES"){
        auto d=draft();const auto& descriptions=ui::setting_descriptions();CHECK(descriptions.size()==settings_cases["settings"].size());
        for(std::size_t i=0;i<descriptions.size();++i){const auto& e=settings_cases["settings"][i];const auto id=e["id"].get<std::string>();CHECK(descriptions[i].id==id&&descriptions[i].label==e["label"]&&descriptions[i].default_value==e["initial"]);CHECK(d.value(id).requested==e["initial"]);d.set(id,e["edit"]);CHECK(d.value(id).requested==e["edit"]);if(e.contains("invalid"))rejected([&]{d.set_text(id,e["invalid"].get<std::string>());});}
        const auto q=*d.begin("commit","all");const auto command=p::parse(q.body);CHECK(command["operations"].size()==10);std::size_t n=0;
        for(const auto& e:settings_cases["settings"])if(e["edit"]!=e["initial"]){CHECK(command["operations"][n]["path"]==e["id"]&&command["operations"][n]["value"]==e["edit"]);++n;}
        CHECK(command["schema_version"]=="0.2.0"&&command["expected_revision"]=="40"&&command["policy_generation"]=="7");
    }else if(name=="DEFAULT"){
        auto d=draft();edit(d);d.use_default("sampling.resources_ms");CHECK(!d.dirty());d.set("history.persistent",true);d.use_default("history.persistent");CHECK(!d.dirty());
        auto pol=policy();pol.forced["sampling.resources_ms"]=500;ui::SettingsDraft locked(authority(),pol,initial(),"E1");rejected([&]{locked.use_default("sampling.resources_ms");});
    }else if(name=="PREVIEW"||name=="COMMIT"){
        const auto intent=name=="PREVIEW"?"preview":"commit";auto d=draft();edit(d);Store store;c::Transactions tx(store,"E1",[](const auto&){});auto q=*d.begin(intent,"R");CHECK(d.state()==ui::DraftState::pending&&!d.value("sampling.resources_ms").editable);rejected([&]{d.revert();});rejected([&]{d.begin(intent,"S");});
        auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0);CHECK(d.complete(q.ticket,result));CHECK(store.writes==(name=="COMMIT"?1U:0U));CHECK(d.dirty()==(name=="PREVIEW"));
        if(name=="COMMIT"){CHECK(result["stored"]==true&&result["durable"]==true&&result["visible"]==false&&result["activation"][0]["state"]=="pending");CHECK(d.revision()==41);}else CHECK(d.revision()==40&&result["outcome"]=="preview");
    }else if(name=="CANCEL"){
        auto d=draft();edit(d);Store store;c::Transactions tx(store,"E1",[](const auto&){});auto q=*d.begin("commit","R");CHECK(d.cancel_request()->request=="R"&&!d.cancel_request());CHECK(d.state()==ui::DraftState::pending);
        auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0,[]{return true;});d.complete(q.ticket,result);CHECK(store.writes==0&&d.revision()==40&&d.dirty()&&d.last_result()["outcome"]=="cancelled");
    }else if(name=="CONFLICT"){
        auto d=draft();edit(d);Store store;store.current.documents.settings["revision"]=store.current.documents.scene["revision"]="41";c::Transactions tx(store,"E1",[](const auto&){});auto q=*d.begin("commit","R");d.complete(q.ticket,tx.submit("P","C",q.body,authority(),[]{return policy();},0));
        CHECK(store.writes==0&&d.state()==ui::DraftState::conflict&&d.dirty()&&d.value("sampling.resources_ms").requested==1500);rejected([&]{d.begin("commit","S");});d.reload(store.current.documents,"E1");CHECK(!d.dirty()&&d.revision()==41);
    }else if(name=="POLICY"){
        for(const auto* channel:{"inspector","accessibility"}){auto pol=policy();pol.disclosure.erase({"desktop",channel});ui::SettingsDraft d(authority(),pol,initial(),"E1");CHECK(!d.available()&&d.value("sampling.resources_ms").requested.is_null());}
        auto d=draft();auto pol=policy(8);pol.forced["sampling.max_workers"]=2;d.policy(pol);CHECK(d.value("sampling.max_workers").requested==4&&d.value("sampling.max_workers").effective==2&&!d.value("sampling.max_workers").editable);
        edit(d);auto q=*d.begin("commit","R");pol=policy(9);pol.disclosure.clear();d.policy(pol);CHECK(!d.available()&&d.last_result().is_null()&&d.active_request()->body.empty());
        d.complete(q.ticket,c::committed_result("R","E1",41));CHECK(!d.available()&&!d.active_request());d.policy(policy(10));CHECK(!d.available());d.reload(initial(),"E2");CHECK(d.available());d.policy(policy(10));CHECK(!d.available());
        auto denied=draft();edit(denied);pol=policy(8);pol.denied_capabilities.insert("settings.commit");denied.policy(pol);CHECK(!denied.may_submit("commit")&&denied.may_submit("preview"));
    }else if(name=="RESULT-SCOPE"){
        for(unsigned fault=0;fault<8;++fault){auto d=draft();edit(d);auto q=*d.begin("commit","R");auto result=c::committed_result("R","E1",41);
            CHECK(!d.complete(q.ticket+1,result)&&d.state()==ui::DraftState::pending);
            if(fault==0)result["request_id"]="wrong";
            if(fault==1)result["producer_epoch"]="E2";
            if(fault==2)result["revision"]="42";
            if(fault==3)result["visible"]=true;
            if(fault==4)result["durable"]=false;
            if(fault==5)result["activation"][0]["state"]="active";
            if(fault==6)result["unknown"]=true;
            if(fault==7)result["error"]={{"code","bad"},{"message","bad"},{"retryable",false}};
            rejected([&]{d.complete(q.ticket,result);});CHECK(d.state()==ui::DraftState::unknown&&d.revision()==40&&d.active_request()->body==q.body);}
    }else if(name=="UNKNOWN"){
        auto d=draft();edit(d);auto q=*d.begin("commit","R");d.disconnected();CHECK(d.state()==ui::DraftState::unknown);rejected([&]{d.reload(initial(),"E2");});
        d.complete(q.ticket,c::result({"unknown","request.pending"},"R","E1",40));CHECK(d.active_request()->body==q.body);
        Json response={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id","R"},{"result",c::committed_result("R","E2",41)}};
        rejected([&]{d.reconciled(q.ticket,"wrong-query","E2",response);});CHECK(d.reconciled(q.ticket,"Q","E2",response)&&d.last_result()["producer_epoch"]=="E2");CHECK(d.revision()==41&&!d.active_request());
        CHECK(!d.complete(q.ticket,c::committed_result("R","E1",41)));d.close();CHECK(!d.available()&&d.state()==ui::DraftState::closed);
    }else if(name=="BOUNDS"){
        auto d=draft();for(const auto* text:{"-1","01","+1","1e3","18446744073709551616"," 1000"})rejected([&]{d.set_text("sampling.resources_ms",text);});
        rejected([&]{d.set_text("display.theme_id",std::string(257,'x'));});rejected([&]{d.set("unknown.path",true);});rejected([&]{d.set("display.enabled",1);});CHECK(!d.dirty());
        auto v=initial();v.settings["revision"]=v.scene["revision"]="18446744073709551615";ui::SettingsDraft maximum(authority(),policy(),v,"E1");edit(maximum);auto q=*maximum.begin("commit","R");CHECK(p::parse(q.body)["expected_revision"]=="18446744073709551615");rejected([&]{maximum.complete(q.ticket,c::committed_result("R","E1",0));});
    }else throw std::runtime_error("unknown case");
}
int main(int argc,char** argv){try{CHECK(argc==3);root=argv[2];settings_cases=read("tests/configuration/settings-cases.json");const std::string name=argv[1];if(name=="THEME"||name.find("CONTENT")==0)run_settings_content_case(name,root);else run(name);std::cout<<name<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
