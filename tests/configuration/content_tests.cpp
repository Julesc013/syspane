#include "content.hpp"
#include "digest.hpp"
#include "async_commands.hpp"
#include "session.hpp"
#include <fstream>
#include <functional>

namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;using p::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("content test:"+std::to_string(line));}
#define VERIFY(x) check(static_cast<bool>(x),__LINE__)
void rejects(const std::function<void()>& call,const char* code=nullptr){bool failed=false;try{call();}catch(const p::Error& e){failed=true;if(code)VERIFY(std::string(e.what())==code);}VERIFY(failed);}
Json read(const std::string& root,const char* name){std::ifstream stream(root+"/"+name);VERIFY(stream.good());Json value;stream>>value;return value;}
Json package_pin(const c::ContentPackage& package){auto m=c::parse_content_json(package.manifest);return {{"id",m["package_id"]},{"version",m["version"]},{"sha256",c::sha256(package.manifest)}};}
Json doc_pin(const c::ContentPackage& package){auto m=c::parse_content_json(package.manifest);const auto kind=m["kind"].get<std::string>();const auto& b=package.assets.at(kind+".json");
    return {{"id",c::parse_content_json(b)[kind+"_id"]},{"version",m["version"]},{"sha256",c::sha256(b)}};}
c::ContentPackage pack(const std::string& id,const std::string& kind,const Json& doc,Json deps=Json::array()){
    const auto bytes=doc.dump()+"\n";Json m={{"schema_version","0.1.0"},{"package_id",id},{"version","0.1.0"},{"kind",kind},{"license","MIT"},{"dependencies",deps},
        {"assets",Json::array({{{"path",kind+".json"},{"media_type","application/json"},{"sha256",c::sha256(bytes)},{"bytes",bytes.size()}}})},
        {"total_unpacked_bytes",bytes.size()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    return {m.dump()+"\n",{{kind+".json",bytes}}};
}
void manifest(c::ContentPackage& bytes,const std::function<void(Json&)>& change){auto m=c::parse_content_json(bytes.manifest);change(m);bytes.manifest=m.dump();}
struct Fixture {
    c::Authored base;std::vector<c::ContentPackage> packages;c::Policy policy;c::Authority authority{true,"console",{"console"}};
    explicit Fixture(const std::string& root):base{read(root,"settings.json"),read(root,"scene-portable.json")}{
        base.settings["revision"]=base.scene["revision"]="40";policy.available=true;policy.revision=7;
        auto theme=read(root,"theme.json");packages.push_back(pack("package:native","theme",theme));theme["theme_id"]="theme:parent";packages.push_back(pack("package:other","theme",theme));
        auto scene=base.scene;scene["revision"]="3";packages.push_back(pack("package:scene","scene",scene));
        Json parent={{"schema_version","0.1.0"},{"preset_id","preset:parent"},{"version","0.1.0"},{"parent",nullptr},{"scene",doc_pin(packages[2])},
            {"theme",doc_pin(packages[1])},{"settings",Json::array({{{"path","display.enabled"},{"value",false}},{{"path","sampling.resources_ms"},{"value",1000}}})},
            {"required_capabilities",Json::array({"scene.selector"})},{"optional_capabilities",Json::array({"optional.z","optional.a"})}};
        packages.push_back(pack("package:parent","preset",parent,Json::array({package_pin(packages[0]),package_pin(packages[1]),package_pin(packages[2])})));
        auto leaf=parent;leaf["preset_id"]="preset:leaf";leaf["parent"]=doc_pin(packages[3]);leaf["theme"]=doc_pin(packages[0]);leaf["settings"]=Json::array({{{"path","sampling.resources_ms"},{"value",1500}}});
        packages.push_back(pack("package:leaf","preset",leaf,Json::array({package_pin(packages[3])})));
    }
    void leaf(const std::function<void(Json&)>& change){auto doc=c::parse_content_json(packages[4].assets.at("preset.json"));change(doc);packages[4]=pack("package:leaf","preset",doc,Json::array({package_pin(packages[3])}));}
    c::PresetPlan preview(){return c::ContentCatalog(packages).preview(package_pin(packages[4]),doc_pin(packages[4]),base,"P",authority,policy,{"scene.selector"});}
};
void compose(const std::string& root){Fixture f(root);const auto base=f.base;auto plan=f.preview();
    VERIFY(plan.candidate.settings["sampling"]["resources_ms"]==1500&&plan.candidate.settings["display"]["enabled"]==false);
    VERIFY(plan.candidate.scene["revision"]=="40"&&plan.candidate.scene["theme_id"]=="theme:native"&&plan.theme["theme_id"]=="theme:native");
    VERIFY(plan.command["intent"]=="preview"&&plan.command["policy_generation"]=="7"&&plan.command["operations"].size()==3);
    VERIFY(plan.command["operations"][0]["path"]=="display.enabled"&&plan.command["operations"][1]["path"]=="sampling.resources_ms");
    VERIFY(plan.setting_origins["display.enabled"]==doc_pin(f.packages[3])&&plan.setting_origins["sampling.resources_ms"]==doc_pin(f.packages[4]));
    VERIFY(plan.preset_pins==Json::array({doc_pin(f.packages[3]),doc_pin(f.packages[4])})&&plan.package_pins.size()==5);
    VERIFY(plan.missing_optional==Json::array({"optional.a","optional.z"}));
    f.leaf([](Json& d){d["theme"]=nullptr;});auto inherited=f.preview();VERIFY(inherited.candidate.scene["theme_id"].is_null()&&inherited.theme["theme_id"]=="theme:native");
    VERIFY(f.base.settings==base.settings&&f.base.scene==base.scene);
    f.packages.clear();bool original=false;for(const auto& bytes:plan.packages)if(bytes->assets.count("scene.json")){VERIFY(c::parse_content_json(bytes->assets.at("scene.json"))["revision"]=="3");original=true;}VERIFY(original);
}
void pins(const std::string& root){Fixture f(root);auto bad=package_pin(f.packages[4]);bad["sha256"]=std::string(64,'0');
    rejects([&]{c::ContentCatalog(f.packages).preview(bad,doc_pin(f.packages[4]),f.base,"P",f.authority,f.policy,{"scene.selector"});},"content.reference");
    f.leaf([](Json& d){d["scene"]["sha256"]=std::string(64,'0');});rejects([&]{f.preview();},"content.reference");
    f=Fixture(root);manifest(f.packages[4],[](Json& m){m["dependencies"]=Json::array();});rejects([&]{f.preview();},"content.reference");
    f=Fixture(root);f.packages[0].assets["theme.json"]+=" ";rejects([&]{f.preview();},"content.digest");
    f=Fixture(root);manifest(f.packages[4],[](Json& m){m["dependencies"][0]["sha256"]=std::string(64,'0');});rejects([&]{f.preview();},"content.dependency");
    f=Fixture(root);f.packages.push_back(f.packages[0]);rejects([&]{f.preview();},"content.duplicate_package");
    f=Fixture(root);f.packages[0].assets["extra.json"]="{}";rejects([&]{f.preview();},"content.assets");
}
void names(const std::string& root){
    for(const char* name:{"/a","a/../b","a//b","a/.","a\\b","C:a","a.","a ","nul.png","COM1/x","manifest.json","MANIFEST.JSON","Manifest.json/child"})rejects([&]{c::validate_content_path(name);},"content.path");
    c::validate_content_path("images/space name-1.png");c::validate_content_path("com10.txt");
    Fixture f(root);for(const char* path:{"Theme.json","theme.json/child"}){auto package=f.packages[0];manifest(package,[&](Json& m){auto a=m["assets"][0];a["path"]=path;m["assets"].push_back(a);m["total_unpacked_bytes"]=2*m["total_unpacked_bytes"].get<unsigned>();});
        rejects([&]{c::validate_content_manifest(package.manifest);},"content.path_collision");}
    auto package=f.packages[0];manifest(package,[](Json& m){auto a=m["assets"][0];a["path"]="Images/a.png";m["assets"].push_back(a);a["path"]="images/b.png";m["assets"].push_back(a);m["total_unpacked_bytes"]=3*m["total_unpacked_bytes"].get<unsigned>();});
    rejects([&]{c::validate_content_manifest(package.manifest);},"content.path_collision");
    rejects([]{c::parse_content_json("{\"x\":1,\"x\":2}");},"json.duplicate_key");
    VERIFY(c::parse_content_json("{}\r\n\t ")==Json::object());
}
void bounds(const std::string& root){Fixture f(root);
    f.leaf([](Json& d){d["settings"].push_back(d["settings"][0]);});rejects([&]{f.preview();},"content.duplicate_setting");
    f=Fixture(root);f.leaf([](Json& d){d["settings"][0]["value"]=1;});rejects([&]{f.preview();},"authored.schema");
    f=Fixture(root);manifest(f.packages[0],[](Json& m){m["total_unpacked_bytes"]=1;});rejects([&]{f.preview();},"content.total");
    f=Fixture(root);auto d=read(root,"theme.json");std::vector<c::ContentPackage> chain;
    for(unsigned i=0;i<9;++i){d["theme_id"]="theme:"+std::to_string(i);chain.push_back(pack("package:"+std::to_string(i),"theme",d,i?Json::array({package_pin(chain.back())}):Json::array()));
        if(i==7)(void)c::ContentCatalog(chain);}
    rejects([&]{c::ContentCatalog catalog(chain);},"content.depth");
    rejects([]{c::ContentCatalog catalog(std::vector<c::ContentPackage>(65));},"content.capacity");
    rejects([]{c::parse_content_json(std::string(262145,' '));},"content.size");
}
void capabilities(const std::string& root){Fixture f(root);f.policy.denied_capabilities.insert("scene.selector");rejects([&]{f.preview();},"content.capability");
    f=Fixture(root);rejects([&]{c::ContentCatalog(f.packages).preview(package_pin(f.packages[4]),doc_pin(f.packages[4]),f.base,"P",f.authority,f.policy,{});},"content.capability");
    f=Fixture(root);f.leaf([](Json& d){d["theme"]=nullptr;d["settings"].push_back({{"path","display.theme_id"},{"value","theme:missing"}});});rejects([&]{f.preview();},"content.theme");
}
void policy(const std::string& root){Fixture f(root);f.policy.forced["sampling.resources_ms"]=1000;rejects([&]{f.preview();},"policy.forced");
    f=Fixture(root);f.policy.available=false;rejects([&]{f.preview();},"policy.denied");
    f=Fixture(root);f.policy.denied_capabilities.insert("settings.preview");rejects([&]{f.preview();},"policy.denied");
    f=Fixture(root);f.authority={true,"saver_settings",{"saver_settings"}};rejects([&]{f.preview();},"policy.denied");
}
struct ResourceStore:c::GenerationStore{
    c::Committed current,previous;unsigned writes=0;std::function<void()> before=[]{};
    explicit ResourceStore(const c::Authored& base):current{base,{}}{}
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{std::vector<c::CommitReceipt> result;
        for(const auto* v:{&current,&previous})if(v->identity)result.push_back({*v->identity,c::authored_revision(v->documents)});
        return result;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{
        for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;
        return {};}
    c::Publication publish(const c::Committed& next,const std::function<void()>& guard)override{before();guard();previous=current;current=next;++writes;return c::Publication::durable;}
};
Json resource_command(Fixture& f){auto q=f.preview().command;q["schema_version"]="0.3.0";q["intent"]="commit";
    q["content"]={{"package",package_pin(f.packages[4])},{"preset",doc_pin(f.packages[4])}};return q;}
c::ResourceProvider provider(const Fixture& f,unsigned& calls){auto catalog=std::make_shared<c::ContentCatalog>(f.packages);
    return {{"scene.selector"},[catalog,&calls](const c::Authored& candidate,const Json& selection){++calls;return catalog->resources(selection,candidate);}};}
void resource_commit(const std::string& root){Fixture f(root);ResourceStore store(f.base);unsigned calls=0;c::Transactions tx(store,"E1",provider(f,calls));auto q=resource_command(f);
    auto submit=[&](Json v){return tx.submit("principal","connection",v.dump(),f.authority,[&]{return f.policy;},0);};
    auto preview=q;preview["request_id"]="preview";preview["intent"]="preview";VERIFY(submit(preview)["outcome"]=="preview"&&store.writes==0);
    const auto accepted=submit(q);VERIFY(accepted["revision"]=="41"&&accepted["durable"]==true&&accepted["visible"]==false&&store.writes==1);
    VERIFY(store.current.resources&&store.current.resources->selection()==q["content"]&&store.current.resources->packages().size()==5);
    VERIFY(submit(q)==accepted&&calls==2&&store.writes==1);q["content"]["package"]["sha256"]=std::string(64,'0');VERIFY(submit(q)["error"]["code"]=="request.changed");
    auto legacy=resource_command(f);legacy["schema_version"]="0.2.0";legacy.erase("content");legacy["request_id"]="legacy";
    legacy["expected_revision"]=legacy["operations"].back()["scene"]["revision"]="41";VERIFY(submit(legacy)["error"]["code"]=="resource.contract"&&store.writes==1);
    c::Transactions restarted(store,"E2",[](const c::Authored&){throw p::Error("should.not.prepare");});
    VERIFY(restarted.reconcile("principal","E1","P",f.authority,f.policy)["revision"]=="41");
    f.policy.denied_capabilities.insert("content.select");VERIFY(restarted.reconcile("principal","E1","P",f.authority,f.policy)["outcome"]=="denied");
}
void resource_guards(const std::string& root){Fixture f(root);ResourceStore store(f.base);unsigned calls=0;const auto q=resource_command(f);
    c::Transactions old(store,"old",[](const c::Authored&){});VERIFY(old.submit("p","c",q.dump(),f.authority,[&]{return f.policy;},0)["error"]["code"]=="resource.contract");
    c::Transactions tx(store,"E1",provider(f,calls));auto submit=[&](const std::string& id){auto v=q;v["request_id"]=id;return tx.submit("p","c",v.dump(),f.authority,[&]{return f.policy;},0);};
    f.policy.denied_capabilities.insert("scene.selector");VERIFY(submit("denied")["outcome"]=="denied"&&store.writes==0);
    f.policy.denied_capabilities.clear();store.before=[&]{f.policy.revision=8;};VERIFY(submit("late")["error"]["code"]=="policy.changed"&&store.writes==0);
    const auto snapshot=c::ContentCatalog(f.packages).resources(q["content"],f.preview().candidate);
    auto wrong=f.base;wrong.scene["theme_id"]="theme:parent";rejects([&]{c::validate_resource_binding(*snapshot,wrong);},"content.theme");
    c::ResourceProvider mismatch{{"scene.selector"},[snapshot](const c::Authored&,const Json&){return snapshot;}};ResourceStore other(f.base);c::Transactions invalid(other,"E1",std::move(mismatch));
    auto changed=q;changed["content"]["package"]["sha256"]=std::string(64,'0');f.policy.revision=7;
    VERIFY(invalid.submit("p","c",changed.dump(),f.authority,[&]{return f.policy;},0)["error"]["code"]=="resource.selection"&&other.writes==0);
}
void resource_session(const std::string& root){Fixture f(root);ResourceStore store(f.base);unsigned calls=0;auto owner=std::make_shared<c::AsyncCommands>(store,"E1",provider(f,calls));
    c::Sessions sessions("E1",40,f.policy,{},owner);auto q=resource_command(f);
    auto hello=[](const std::string& version,bool content){return Json{{"wire_major",0},{"wire_minor",1},{"role","console"},{"producer_epoch","client"},{"max_frame_bytes",1048576},
        {"document_versions",Json::array({{{"document","command"},{"version",version}},{{"document","command-result"},{"version","0.1.0"}}})},
        {"required_features",Json::array({"configuration.transactions"})},{"optional_features",content?Json::array({"configuration.content"}):Json::array()}};};
    auto send=[&](const char* id,const char* type,Json body){Json envelope={{"type",type},{"body",std::move(body)}};if(std::string(type)!="hello"){envelope["connection_id"]=id;envelope["producer_epoch"]="E1";}
        sessions.receive(id,envelope.dump(),0);VERIFY(!sessions.closed(id));};
    auto pop=[&](const char* id){const auto bytes=sessions.pop(id,0);VERIFY(bytes);return p::parse(*bytes);};
    sessions.open("C","p",f.authority,0);send("C","hello",hello("0.3.0",true));VERIFY(pop("C")["type"]=="welcome");
    send("C","command",q);const auto ticket=owner->take();VERIFY(ticket);auto completion=owner->run(*ticket);VERIFY(owner->finish(std::move(completion),0,true));
    VERIFY(pop("C")["body"]["outcome"]=="accepted"&&store.current.resources&&calls==1);
    sessions.open("D","p",f.authority,0);send("D","hello",hello("0.2.0",false));VERIFY(pop("D")["type"]=="welcome");
    send("D","command",q);VERIFY(pop("D")["body"]["error"]["code"]=="feature.unsupported"&&calls==1);
    sessions.open("F","p",f.authority,0);send("F","hello",hello("0.3.0",false));VERIFY(pop("F")["type"]=="welcome");
    send("F","command",q);VERIFY(pop("F")["body"]["error"]["code"]=="feature.unsupported"&&calls==1);
    q["schema_version"]="0.2.0";q.erase("content");send("C","command",q);VERIFY(pop("C")["body"]["error"]["code"]=="feature.unsupported");
}
}
void content_tests(const std::string& name,const std::string& root){
    if(name=="CONTENT-COMPOSE")compose(root);else if(name=="CONTENT-PINS")pins(root);else if(name=="CONTENT-PATHS")names(root);
    else if(name=="CONTENT-BOUNDS")bounds(root);else if(name=="CONTENT-CAPABILITIES")capabilities(root);else if(name=="CONTENT-POLICY")policy(root);
    else if(name=="RESOURCE-COMMIT")resource_commit(root);else if(name=="RESOURCE-GUARDS")resource_guards(root);else if(name=="RESOURCE-SESSION")resource_session(root);else VERIFY(false);
}
