#include "transaction.hpp"
#include "digest.hpp"
#include <fstream>
#include <iostream>
#include <limits>

namespace c=syspane::configuration;namespace p=syspane::protocol;using p::Json;
void content_tests(const std::string& name,const std::string& root);
void check(bool v,const char* expression,int line){if(!v)throw std::runtime_error(std::string(expression)+":"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),#x,__LINE__)
std::string fixtures;
Json read(const char* name){std::ifstream input(fixtures+"/"+name);CHECK(input.good());Json value;input>>value;return value;}
c::Authored initial(std::uint64_t revision=40){
    c::Authored value{read("settings.json"),read("scene-portable.json")};value.settings["revision"]=value.scene["revision"]=std::to_string(revision);
    value.scene["widgets"][1]["layout"]={{"base",{{"kind","fixed"},{"x",10},{"y",20},{"width",240},{"height",80}}}};return value;
}
c::Policy policy(std::uint64_t revision=7){c::Policy value;value.available=true;value.revision=revision;return value;}
c::Authority authority(){return {true,"console",{"console"}};}
Json command(const c::Authored& base,const char* intent="commit",const std::string& id="R"){
    auto scene=base.scene;scene["widgets"][1]["layout"]["base"]["x"]=20;
    return {{"schema_version","0.2.0"},{"request_id",id},{"expected_revision",base.settings["revision"]},{"policy_generation","7"},{"intent",intent},
        {"operations",Json::array({{{"op","scene.replace"},{"scene",scene}},{{"op","settings.set"},{"path","sampling.resources_ms"},{"value",1500}}})}};
}
struct MemoryStore: c::GenerationStore {
    c::Committed current{initial(),{}},previous;unsigned writes=0;int failure=0;std::function<void()> before=[]{};
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{
        std::vector<c::CommitReceipt> rows;for(const auto* r:{&current,&previous})if(r->identity)rows.push_back({*r->identity,c::authored_revision(r->documents)});return rows;
    }
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{
        for(const auto* row:{&current,&previous})if(row->identity&&row->identity->principal==principal&&row->identity->epoch==epoch&&row->identity->request==request)return *row;
        return {};
    }
    c::Publication publish(const c::Committed& next,const std::function<void()>& guard)override{
        before();guard();if(failure==1)return c::Publication::unchanged;
        previous=current;current=next;++writes;return failure==2?c::Publication::unknown:c::Publication::durable;
    }
};
Json submit(c::Transactions& tx,const Json& value,std::uint64_t now=0){return tx.submit("principal","connection",value.dump(),authority(),[]{return policy();},now);}
void rejected(const std::function<void()>& call){bool failed=false;try{call();}catch(const p::Error&){failed=true;}CHECK(failed);}
void schemas(){
    auto v=initial();c::validate_authored(v);v.scene=read("scene-portable.json");v.scene["revision"]="40";c::validate_authored(v);
    const auto saved=v;
    for(unsigned i=0;i<9;++i){
        v=saved;
        if(i==0)v.scene["widgets"].push_back(v.scene["widgets"][1]);
        if(i==1)v.scene["roots"].push_back("widget:adapters");
        if(i==2)v.scene["widgets"][0]["children"]={"missing"};
        if(i==3)v.scene["widgets"][1]["children"]=Json::array();
        if(i==4)v.scene["widgets"][1]["layout"]["base"]["width"]["preferred"]=1000;
        if(i==5)v.scene["widgets"][1]["layout"]["breakpoints"]=Json::array({{{"min_width_dip",100},{"layout",v.scene["widgets"][1]["layout"]["base"]}},{{"min_width_dip",100},{"layout",v.scene["widgets"][1]["layout"]["base"]}}});
        if(i==6)v.scene["widgets"][1]["layout"]["base"]={{"kind","grid"},{"columns",2},{"gap_dip",1},{"overflow","diagnose"}};
        if(i==7)v.scene["widgets"][1]["bindings"][0]["predicates"][0]["op"]="regex";
        if(i==8)v.scene["revision"]="18446744073709551616";
        rejected([&]{c::validate_authored(v);});
    }
    v=saved;v.scene["extensions"]={{"author.note",{{"nested",Json::array({"x",false,1})}}}};c::validate_authored(v);
    v.scene["extensions"]["bad key"]=1;rejected([&]{c::validate_authored(v);});
    v=saved;v.settings["sampling"]["max_workers"]=4.0;c::validate_authored(v);v.settings["sampling"]["max_workers"]=true;rejected([&]{c::validate_authored(v);});
    v=saved;v.scene["widgets"][1]["title"]=std::string(512,'a');c::validate_authored(v);
    v.scene["widgets"][1]["title"]=std::string(513,'a');rejected([&]{c::validate_authored(v);});
    auto q=command(saved);q["operations"].push_back(q["operations"][0]);rejected([&]{c::validate_command(q);});
    q=command(saved);q["operations"].push_back(q["operations"][1]);rejected([&]{c::validate_command(q);});
}
void mixed(){
    MemoryStore store;c::Transactions tx(store,"E1",[](const c::Authored&){});auto q=command(store.current.documents,"preview","P");
    const auto preview=submit(tx,q);CHECK(preview["outcome"]=="preview"&&!preview["stored"].get<bool>()&&store.writes==0);
    q=command(store.current.documents);const auto accepted=submit(tx,q,1);
    CHECK(accepted["outcome"]=="accepted"&&accepted["revision"]=="41"&&accepted["durable"]==true&&accepted["visible"]==false&&accepted["activation"][0]["state"]=="pending");
    CHECK(tx.authored().settings["revision"]=="41"&&tx.authored().scene["revision"]=="41"&&store.writes==1);
    CHECK(tx.authored().scene["widgets"][1]["layout"]["base"]["x"]==20&&tx.authored().settings["sampling"]["resources_ms"]==1500);
    auto invalid=command(tx.authored(),"commit","bad");invalid["operations"][1]["value"]=1;
    rejected([&]{submit(tx,invalid,2);});CHECK(store.writes==1);
}
void conflicts(){
    MemoryStore store;c::Transactions tx(store,"E1",[](const c::Authored&){});auto q=command(store.current.documents);auto current_policy=policy();
    current_policy.forced["sampling.resources_ms"]=1000;
    CHECK(tx.submit("p","c",q.dump(),authority(),[&]{return current_policy;},0)["outcome"]=="denied"&&store.writes==0);
    current_policy=policy();store.before=[&]{current_policy=policy(8);};
    CHECK(tx.submit("p","c",q.dump(),authority(),[&]{return current_policy;},1)["error"]["code"]=="policy.changed"&&store.writes==0);
    store.before=[]{};q["request_id"]="S";q["expected_revision"]="39";q["operations"][0]["scene"]["revision"]="39";
    CHECK(submit(tx,q,2)["error"]["code"]=="revision.changed"&&store.writes==0);
    q=command(store.current.documents,"commit","T");auto a=authority();a.role="saver_settings";a.role_grants.insert(a.role);
    CHECK(tx.submit("p","c",q.dump(),a,[]{return policy();},3)["outcome"]=="denied");
}
void replay(){
    MemoryStore store;c::Transactions tx(store,"E1",[](const c::Authored&){});const auto q=command(store.current.documents);const auto accepted=submit(tx,q);
    CHECK(submit(tx,q,600001)==accepted&&store.writes==1); // Selected committed identity survives ordinary cache expiry.
    CHECK(tx.submit("principal","other",q.dump(2),authority(),[]{return policy();},600002)["error"]["code"]=="request.changed");
    c::Transactions restarted(store,"E2",[](const c::Authored&){});const auto reconciled=restarted.reconcile("principal","E1","R",authority(),policy());
    CHECK(reconciled["outcome"]=="accepted"&&reconciled["revision"]=="41"&&reconciled["producer_epoch"]=="E2"&&store.writes==1);
    auto denied=policy(8);denied.denied_capabilities.insert("scene.replace");
    CHECK(restarted.reconcile("principal","E1","R",authority(),denied)["outcome"]=="denied");
    CHECK(restarted.reconcile("other","E1","R",authority(),policy())["outcome"]=="unknown");
    CHECK(submit(restarted,q)["outcome"]=="conflict"&&store.writes==1);
}
void interruption(){
    for(int failure=1;failure<=2;++failure){MemoryStore store;store.failure=failure;c::Transactions tx(store,"E1",[](const c::Authored&){});auto q=command(store.current.documents);
        auto response=submit(tx,q);CHECK(response["outcome"]==(failure==1?"invalid":"unknown"));
        CHECK(c::authored_revision(tx.authored())==40&&store.writes==(failure==1?0U:1U));
        if(failure==2){CHECK(tx.faulted()&&response["stored"].is_null());c::Transactions restarted(store,"E2",[](const c::Authored&){});
            CHECK(c::authored_revision(restarted.authored())==41&&restarted.reconcile("principal","E1","R",authority(),policy())["durable"]==true);}
    }
    MemoryStore store;c::Transactions tx(store,"E1",[](const c::Authored&){});auto q=command(store.current.documents);
    CHECK(tx.submit("p","c",q.dump(),authority(),[]{return policy();},0,[]{return true;})["outcome"]=="cancelled"&&store.writes==0);
    bool cancel=false;store.before=[&]{cancel=true;};q["request_id"]="S";
    CHECK(tx.submit("p","c",q.dump(),authority(),[]{return policy();},1,[&]{return cancel;})["outcome"]=="cancelled"&&store.writes==0);
    MemoryStore unprepared;c::Transactions denied(unprepared,"E1",[](const c::Authored&){throw p::Error("resource.unavailable");});
    CHECK(submit(denied,command(unprepared.current.documents))["error"]["code"]=="resource.unavailable"&&unprepared.writes==0);
}
void bounds(){
    MemoryStore store;store.current.documents=initial(std::numeric_limits<std::uint64_t>::max());c::Transactions tx(store,"E1",[](const c::Authored&){});
    CHECK(submit(tx,command(store.current.documents))["error"]["code"]=="revision.exhausted"&&store.writes==0);
    auto v=initial();v.scene["widgets"]=Json::array();v.scene["roots"]={"g0"};
    for(unsigned i=0;i<17;++i)v.scene["widgets"].push_back({{"id","g"+std::to_string(i)},{"kind","group"},{"title",""},{"display",{{"role","primary"}}},
        {"layout",{{"base",{{"kind","stack"},{"axis","vertical"},{"gap_dip",0},{"overflow","diagnose"}}}}},{"bindings",Json::array()},{"priority","normal"},
        {"children",i==16?Json::array():Json::array({"g"+std::to_string(i+1)})}});
    rejected([&]{c::validate_authored(v);});v.scene["widgets"].erase(16);v.scene["widgets"][15]["children"]=Json::array();c::validate_authored(v);
    v.scene["roots"]=Json::array();v.scene["widgets"][15]["children"]={"g0"};rejected([&]{c::validate_authored(v);});
}
void capacity(){
    MemoryStore store;c::Transactions tx(store,"E1",[](const c::Authored&){});
    for(unsigned i=0;i<128;++i)CHECK(submit(tx,command(store.current.documents,"preview","P"+std::to_string(i)))["outcome"]=="preview");
    const auto q=command(store.current.documents,"preview","next");CHECK(submit(tx,q,599999)["outcome"]=="busy");
    CHECK(submit(tx,q,600000)["outcome"]=="preview"&&store.writes==0);
}
void digest(){
    CHECK(c::sha256("")=="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    CHECK(c::sha256("abc")=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    CHECK(c::sha256(std::string(1000000,'a'))=="cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
}
void scene_content_tests(const std::string&,const std::string&);
int main(int argc,char** argv){try{CHECK(argc==3);fixtures=argv[2];const std::string name=argv[1];
    if(name.rfind("SCENE-CONTENT-",0)==0)scene_content_tests(name,fixtures);else if(name=="AUTH-SCHEMA")schemas();else if(name=="TX-MIXED")mixed();else if(name=="TX-CONFLICT")conflicts();else if(name=="TX-REPLAY")replay();
    else if(name=="TX-INTERRUPT")interruption();else if(name=="TX-BOUNDS")bounds();else if(name=="TX-CAPACITY")capacity();else if(name=="DIGEST")digest();
    else if(name.substr(0,8)=="CONTENT-"||name.substr(0,9)=="RESOURCE-")content_tests(name,fixtures);else CHECK(false);
    std::cout<<name<<" pass\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
