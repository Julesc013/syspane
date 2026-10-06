#include "content.hpp"
#include "digest.hpp"
#include "async_commands.hpp"
#include "session.hpp"
#include <fstream>
#include <functional>
#include <iostream>
namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;using p::Json;
void need(bool b,const char* why){if(!b)throw std::runtime_error(why);}
Json read(const std::string& root,const char* name){std::ifstream f(root+"/"+name);need(f.good(),"fixture");Json j;f>>j;return j;}
void rejects(const std::function<void()>& f,const char* why=nullptr){bool rejected=false;try{f();}catch(const p::Error& e){rejected=true;if(why)need(std::string(e.what())==why,"expected rejection code");}need(rejected,"expected rejection");}
c::ContentPackage pack(const std::string& kind,const Json& doc,Json deps=Json::array(),bool image=false){
    auto bytes=doc.dump()+"\n";c::ContentPackage result;result.assets[kind+".json"]=bytes;
    Json assets=Json::array({{{"path",kind+".json"},{"media_type","application/json"},{"sha256",c::sha256(bytes)},{"bytes",bytes.size()}}});
    if(image){result.assets["images/pixel.png"]="opaque fixture";assets.push_back({{"path","images/pixel.png"},{"media_type","image/png"},{"sha256",c::sha256("opaque fixture")},{"bytes",14}});}
    result.manifest=Json{{"schema_version","0.1.0"},{"package_id","package:"+kind},{"version","0.1.0"},{"kind",kind},{"license","MIT"},{"dependencies",deps},{"assets",assets},
        {"total_unpacked_bytes",bytes.size()+(image?14:0)},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}}.dump();return result;
}
Json package_pin(const c::ContentPackage& p){auto m=Json::parse(p.manifest);return {{"id",m["package_id"]},{"version","0.1.0"},{"sha256",c::sha256(p.manifest)}};}
Json doc_pin(const c::ContentPackage& p){auto m=Json::parse(p.manifest);const auto kind=m["kind"].get<std::string>();const auto& bytes=p.assets.at(kind+".json");return {{"id",Json::parse(bytes)[kind+"_id"]},{"version","0.1.0"},{"sha256",c::sha256(bytes)}};}
struct Fixture {
    c::Authored base,draft;std::vector<c::ContentPackage> packages;Json selection,command;c::Policy policy;
    c::Authority authority{true,"console",{"console"}};
    explicit Fixture(const std::string& root){base={read(root,"settings.json"),read(root,"scene-portable.json")};base.settings["revision"]=base.scene["revision"]="40";
        draft={base.settings,read(root,"scene-content.json")};policy.available=true;policy.revision=7;
        packages.push_back(pack("theme",read(root,"theme.json"),Json::array(),true));
        auto& asset=draft.scene["widgets"][6]["content"]["asset"];asset["package"]=package_pin(packages[0]);asset["sha256"]=c::sha256("opaque fixture");
        packages.push_back(pack("scene",draft.scene));auto preset=Json{{"schema_version","0.1.0"},{"preset_id","preset:content"},{"version","0.1.0"},{"parent",nullptr},
            {"scene",doc_pin(packages[1])},{"theme",doc_pin(packages[0])},{"settings",Json::array()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
        packages.push_back(pack("preset",preset,Json::array({package_pin(packages[0]),package_pin(packages[1])})));
        selection={{"package",package_pin(packages[2])},{"preset",doc_pin(packages[2])}};
        command={{"schema_version","0.4.0"},{"request_id","R"},{"expected_revision","40"},{"policy_generation","7"},{"intent","commit"},{"content",selection},{"operations",Json::array({{{"op","scene.replace"},{"scene",draft.scene}}})}};
    }
    c::ResourceProvider provider(){return {{"scene.selector","scene.content"},[&](const c::Authored& a,const Json& s){return c::ContentCatalog(packages).resources(s,a);}};}
};
struct Store:c::GenerationStore {
    c::Committed current,previous;unsigned writes=0;explicit Store(const c::Authored& a):current{a,{}}{}
    c::Committed load()const override{return current;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{
        for(const auto* v:{&current,&previous}){if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;}
        return {};}
    std::vector<c::CommitReceipt> receipts()const override{std::vector<c::CommitReceipt> out;for(const auto* v:{&current,&previous})if(v->identity)out.push_back({*v->identity,c::authored_revision(v->documents)});return out;}
    c::Publication publish(const c::Committed& next,const std::function<void()>& guard)override{guard();previous=current;current=next;++writes;return c::Publication::durable;}
};
void schema(const std::string& root){Fixture f(root);c::validate_authored(f.draft);c::validate_command(f.command);
    auto text=f.draft;std::string unicode;for(unsigned i=0;i<1024;++i)unicode+="\xf0\x9f\x98\x80";text.scene["widgets"][0]["content"]["body"]=unicode;c::validate_authored(text);
    for(const auto& body:{std::string(64,'\n'),std::string("\x7f"),std::string("\xc2\x85")}){text.scene["widgets"][0]["content"]["body"]=body;rejects([&]{c::validate_authored(text);});}
    for(const std::string version:{"0.2.0","0.3.0"}){auto q=f.command;q["schema_version"]=version;if(version=="0.2.0")q.erase("content");rejects([&]{c::validate_command(q);});}
    auto v=f.draft;v.scene["widgets"][0]["content"]["body"]=std::string(1024,'x');c::validate_authored(v);v.scene["widgets"][0]["content"]["body"]=std::string(1025,'x');rejects([&]{c::validate_authored(v);});
    for(const char* name:{"content-kind.json","content-missing.json","content-table-count.json","content-chart-range.json","content-image-path.json","content-image-bindings.json","content-text-control.json","content-chart-collection.json"}){v.scene=read(root+"/../invalid",name);rejects([&]{c::validate_authored(v);});}
}
void migration(const std::string& root){Fixture f(root);auto old=f.base.scene;old["widgets"]=Json::array({old["widgets"][1]});old["roots"]=Json::array({old["widgets"][0]["id"]});old["widgets"][0]["kind"]="text";old["widgets"][0]["bindings"]=Json::array();const auto original=old;
    try{c::validate_scene_document(old);}catch(const std::exception& e){throw std::runtime_error(std::string("migration input: ")+e.what()+" "+old.dump());}
    auto next=c::upgrade_scene_content(old);need(old==original&&next["schema_version"]=="0.3.0"&&next["widgets"][0]["content"]["body"]==old["widgets"][0]["title"],"reversible text migration");need(c::upgrade_scene_content(next)==next,"idempotent migration");
    old["widgets"][0]["kind"]="image";rejects([&]{c::upgrade_scene_content(old);},"scene.content_required");old["widgets"][0]["kind"]="chart";rejects([&]{c::upgrade_scene_content(old);},"scene.content_required");
    need(c::upgrade_scene_content(f.draft.scene)==f.draft.scene,"extensions and content preserved");
}
void resources(const std::string& root){Fixture f(root);auto snapshot=c::ContentCatalog(f.packages).resources(f.selection,f.draft);need(snapshot->required().count("scene.content"),"implicit parser capability");
    c::authorize_resources(*snapshot,f.policy,{"scene.content"});rejects([&]{c::authorize_resources(*snapshot,f.policy,{});},"policy.denied");f.policy.denied_capabilities.insert("scene.content");rejects([&]{c::authorize_resources(*snapshot,f.policy,{"scene.content"});},"policy.denied");
    for(unsigned i=0;i<4;++i){auto a=f.draft;auto& ref=a.scene["widgets"][6]["content"]["asset"];if(i==0)ref["sha256"]=std::string(64,'0');if(i==1)ref["package"]["sha256"]=std::string(64,'0');if(i==2)ref["path"]="images/missing.png";if(i==3){ref["path"]="theme.json";ref["sha256"]=c::sha256(f.packages[0].assets.at("theme.json"));}rejects([&]{c::ContentCatalog(f.packages).resources(f.selection,a);},"content.asset");}
}
void preview(const std::string& root){Fixture f(root);auto plan=c::ContentCatalog(f.packages).preview(f.selection["package"],f.selection["preset"],f.base,"P",f.authority,f.policy,{"scene.content","scene.selector"});
    need(plan.command["schema_version"]=="0.4.0"&&plan.command["content"]==f.selection&&plan.candidate.scene==f.draft.scene,"new preset command identity");
}
void transaction(const std::string& root){Fixture f(root);Store store(f.base);c::Transactions tx(store,"E1",f.provider());const auto body=f.command.dump();auto reply=tx.submit("p","C",body,f.authority,[&]{return f.policy;},0);
    need(reply["revision"]=="41"&&reply["durable"]==true&&reply["visible"]==false&&store.writes==1,"content commit");auto expected=f.draft.scene;expected["revision"]="41";need(store.current.documents.scene==expected,"exact committed content");
    need(tx.submit("p","C",body,f.authority,[&]{return f.policy;},600001)==reply&&store.writes==1,"replay without repeated mutation");c::Transactions recovered(store,"E2",f.provider());need(recovered.reconcile("p","E1","R",f.authority,f.policy)["revision"]=="41","recovery identity");
    auto q=f.command;q["schema_version"]="0.3.0";q["request_id"]="S";q["expected_revision"]="41";q["operations"]={{{"op","settings.set"},{"path","sampling.resources_ms"},{"value",1500}}};need(recovered.submit("p","D",q.dump(),f.authority,[&]{return f.policy;},0)["revision"]=="42","old settings-only command");expected["revision"]="42";need(store.current.documents.scene==expected,"old command preserves new content");
}
void session(const std::string& root){Fixture f(root);Store store(f.base);auto owner=std::make_shared<c::AsyncCommands>(store,"E1",f.provider());c::Sessions sessions("E1",40,f.policy,{},owner);
    auto hello=[](const char* version,bool feature){return Json{{"wire_major",0},{"wire_minor",1},{"role","console"},{"producer_epoch","client"},{"max_frame_bytes",1048576},
        {"document_versions",Json::array({{{"document","command"},{"version",version}},{{"document","command-result"},{"version","0.1.0"}}})},
        {"required_features",Json::array({"configuration.transactions","configuration.content"})},{"optional_features",feature?Json::array({"configuration.scene-content"}):Json::array()}};};
    auto send=[&](const char* id,const char* type,Json body){Json envelope={{"type",type},{"body",std::move(body)}};if(std::string(type)!="hello"){envelope["connection_id"]=id;envelope["producer_epoch"]="E1";}sessions.receive(id,envelope.dump(),0);need(!sessions.closed(id),"session remains open");};
    auto pop=[&](const char* id){auto b=sessions.pop(id,0);need(b.has_value(),"reply");return p::parse(*b);};
    sessions.open("required","p",f.authority,0);auto bad=hello("0.3.0",false);bad["required_features"].push_back("configuration.scene-content");
    sessions.receive("required",Json{{"type","hello"},{"body",bad}}.dump(),0);need(sessions.closed("required"),"required feature cannot downgrade");
    for(const char* id:{"old","missing","new"}){sessions.open(id,"p",f.authority,0);send(id,"hello",hello(std::string(id)=="old"?"0.3.0":"0.4.0",std::string(id)!="missing"));need(pop(id)["type"]=="welcome","negotiated welcome");send(id,"command",f.command);
        if(std::string(id)!="new")need(pop(id)["body"]["error"]["code"]=="feature.unsupported"&&!owner->take(),"unnegotiated rejected before work");
        else{auto job=owner->take();need(job.has_value(),"admitted work");auto done=owner->run(*job);need(owner->finish(std::move(done),0,true),"finished work");need(pop(id)["body"]["outcome"]=="accepted","new feature commits");}}
}
}
void scene_content_tests(const std::string& name,const std::string& root){
    if(name=="SCENE-CONTENT-SCHEMA")schema(root);else if(name=="SCENE-CONTENT-MIGRATION")migration(root);else if(name=="SCENE-CONTENT-RESOURCES")resources(root);
    else if(name=="SCENE-CONTENT-PREVIEW")preview(root);else if(name=="SCENE-CONTENT-TX")transaction(root);else if(name=="SCENE-CONTENT-SESSION")session(root);else need(false,"unknown content case");
}
