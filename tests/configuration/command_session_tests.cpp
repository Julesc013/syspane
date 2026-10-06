#include "async_commands.hpp"
#include "session.hpp"
#include <fstream>
#include <iostream>

namespace c=syspane::configuration;namespace p=syspane::protocol;using p::Json;
void check(bool v,const char* expression,int line){if(!v)throw std::runtime_error(std::string(expression)+":"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),#x,__LINE__)
std::string fixtures;
Json read(const char* name){std::ifstream input(fixtures+"/"+name);CHECK(input.good());Json value;input>>value;return value;}
c::Authored initial(){c::Authored v{read("settings.json"),read("scene-portable.json")};v.settings["revision"]=v.scene["revision"]="40";return v;}
c::Policy policy(std::uint64_t revision=7){c::Policy v;v.available=true;v.revision=revision;return v;}
c::Authority authority(){return {true,"console",{"console"}};}
Json command(const std::string& id="R",const char* intent="commit"){
    return {{"schema_version","0.2.0"},{"request_id",id},{"expected_revision","40"},{"policy_generation","7"},{"intent",intent},
        {"operations",Json::array({{{"op","settings.set"},{"path","sampling.resources_ms"},{"value",1500}}})}};
}
struct Store:c::GenerationStore{
    c::Committed current{initial(),{}},previous;unsigned writes=0;std::function<void()> before=[]{},after=[]{ };
    c::Committed load()const override{return current;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{
        for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;
        return {};
    }
    c::Publication publish(const c::Committed& value,const std::function<void()>& guard)override{
        before();guard();after();previous=current;current=value;++writes;return c::Publication::durable;
    }
};
std::string envelope(const std::string& type,Json body,const std::string& id="C"){
    Json v{{"type",type},{"body",std::move(body)}};
    if(type!="hello"){v["connection_id"]=id;v["producer_epoch"]="E1";}return v.dump();
}
Json hello(bool transactions=true,std::size_t frame=p::frame_limit){
    Json v{{"wire_major",0},{"wire_minor",1},{"role","console"},{"producer_epoch","client"},{"max_frame_bytes",frame},
        {"document_versions",Json::array({{{"document","command"},{"version","0.2.0"}},{{"document","command-result"},{"version","0.1.0"}}})},
        {"required_features",Json::array()},{"optional_features",Json::array({"settings.preview","result.get","cancel"})}};
    if(transactions)v["required_features"].push_back("configuration.transactions");
    return v;
}
struct Harness{
    Store store;std::function<void()> prepare=[]{};
    std::shared_ptr<c::AsyncCommands> owner=std::make_shared<c::AsyncCommands>(store,"E1",[&](const c::Authored&){prepare();});
    c::Sessions sessions{"E1",40,policy(),{},owner};std::uint64_t now=0;
    void open(const std::string& id="C",const std::string& principal="principal",bool transactions=true){
        sessions.open(id,principal,authority(),now);sessions.receive(id,envelope("hello",hello(transactions)),now);CHECK(pop(id)["type"]=="welcome");
    }
    void send(const std::string& type,const Json& body,const std::string& id="C"){sessions.receive(id,envelope(type,body,id),now);CHECK(!sessions.closed(id));}
    Json pop(const std::string& id="C"){auto v=sessions.pop(id,now);CHECK(v);return p::parse(*v);}
    Json query(const char* type="result.get",const std::string& request="R",const std::string& id="C"){
        send(type,{{"request_id",request}},id);return pop(id)["body"];
    }
    void execute(){auto t=owner->take();CHECK(t);auto done=owner->run(*t);CHECK(!owner->finish(std::move(done),now,false));CHECK(!owner->take());CHECK(owner->finish(std::move(done),now,true));}
};
void committed(){
    Harness h;h.open();h.send("command",command());CHECK(!h.sessions.pop("C",0));CHECK(h.sessions.request_count()==1);
    const auto pending=h.query();CHECK(pending["outcome"]=="unknown"&&pending["stored"].is_null()&&pending["error"]["code"]=="request.pending");
    h.execute();auto accepted=h.pop()["body"];
    CHECK(accepted["outcome"]=="accepted"&&accepted["revision"]=="41"&&accepted["durable"]==true&&accepted["visible"]==false);
    CHECK(h.store.writes==1&&h.store.current.documents.settings["sampling"]["resources_ms"]==1500);
    h.send("command",command());CHECK(h.pop()["body"]==accepted&&h.store.writes==1);
    auto changed=command();changed["operations"][0]["value"]=1600;h.send("command",changed);CHECK(h.pop()["body"]["error"]["code"]=="request.changed");
    h.open("D","other");CHECK(h.query("result.get","R","D")["outcome"]=="unknown");
    h.now=600001;CHECK(h.query()["outcome"]=="unknown");h.send("command",command());h.execute();CHECK(h.pop()["body"]==accepted&&h.store.writes==1);
    Harness legacy;legacy.open("C","principal",false);legacy.send("command",command("P","preview"));legacy.execute();CHECK(legacy.pop()["body"]["outcome"]=="preview"&&legacy.store.writes==0);
    legacy.send("command",command());CHECK(legacy.pop()["body"]["error"]["code"]=="feature.unsupported"&&legacy.sessions.request_count()==1);
    Harness mixed;mixed.open();auto edit=command();auto scene=mixed.store.current.documents.scene;scene["widgets"][1]["title"]="Saved scene";
    edit["operations"].push_back({{"op","scene.replace"},{"scene",scene}});mixed.send("command",edit);mixed.execute();const auto stored=mixed.pop()["body"];
    CHECK(stored["outcome"]=="accepted"&&mixed.store.current.documents.scene["widgets"][1]["title"]=="Saved scene");
    mixed.send("command",edit);CHECK(mixed.pop()["body"]==stored&&mixed.store.writes==1);
}
void cancellation(){
    for(unsigned stage=0;stage<3;++stage){Harness h;h.open();h.send("command",command());
        const auto cancel=[&]{const auto r=h.query("cancel");CHECK(r["outcome"]=="unknown"&&r["durable"].is_null());};
        if(stage==0)h.prepare=cancel;
        if(stage==1)h.store.before=cancel;
        if(stage==2)h.store.after=cancel;
        h.execute();const auto answer=h.pop()["body"];
        CHECK(answer["outcome"]==(stage==2?"accepted":"cancelled")&&h.store.writes==(stage==2?1U:0U));
        CHECK(h.query("cancel")==answer);
    }
    Harness queued;queued.open();queued.send("command",command());CHECK(queued.query("cancel")["outcome"]=="unknown");queued.execute();CHECK(queued.pop()["body"]["outcome"]=="cancelled"&&queued.store.writes==0);
}
void policy_changes(){
    for(unsigned stage=0;stage<3;++stage){Harness h;h.open();h.send("command",command());
        const auto revoke=[&]{auto next=policy(8);next.denied_capabilities.insert("settings.commit");h.sessions.policy(next,h.now);CHECK(h.pop()["type"]=="gap");};
        if(stage==0)h.prepare=revoke;
        if(stage==1)h.store.before=revoke;
        if(stage==2)h.store.after=revoke;
        h.execute();CHECK(!h.sessions.pop("C",h.now));const auto hidden=h.query();
        CHECK(hidden["outcome"]=="unknown"&&hidden["error"]["code"]=="policy.denied"&&hidden["stored"].is_null());
        CHECK(h.store.writes==(stage==2?1U:0U));
    }
    Harness h;h.open();h.send("command",command());h.execute();h.sessions.tick(0);h.sessions.policy(policy(8),0);CHECK(h.pop()["type"]=="gap");CHECK(!h.sessions.pop("C",0));CHECK(h.query()["outcome"]=="accepted");
}
void lifetimes(){
    Harness h;h.open();h.send("command",command());h.sessions.disconnect("C");h.open();h.execute();CHECK(!h.sessions.pop("C",0));CHECK(h.query()["outcome"]=="accepted");
    Harness alive;alive.open();alive.send("command",command());alive.prepare=[&]{
        alive.send("heartbeat",{{"sequence","1"}});CHECK(alive.pop()["type"]=="heartbeat");
        CHECK(alive.query()["outcome"]=="unknown");CHECK(!alive.owner->take());
    };alive.execute();CHECK(alive.pop()["body"]["outcome"]=="accepted");
}
void capacity(){
    Harness h;h.open();for(unsigned i=0;i<8;++i)h.send("command",command("R"+std::to_string(i)));
    CHECK(h.sessions.request_count()==8);h.send("command",command("overflow"));CHECK(h.pop()["body"]["outcome"]=="busy"&&h.sessions.request_count()==8);
    h.send("heartbeat",{{"sequence","1"}});CHECK(h.pop()["type"]=="heartbeat");
    h.execute();CHECK(h.pop()["body"]["outcome"]=="accepted");h.send("command",command("next"));CHECK(h.sessions.request_count()==9);
    // Same ledger remains bounded across reconnect and terminal retention.
    Harness many;for(unsigned batch=0;batch<16;++batch){many.open();for(unsigned i=0;i<8;++i)many.send("command",command("P"+std::to_string(batch*8+i),"preview"));
        for(unsigned i=0;i<8;++i){many.execute();CHECK(many.pop()["body"]["outcome"]=="preview");}many.sessions.disconnect("C");}
    many.open();many.send("command",command("full","preview"));CHECK(many.pop()["body"]["outcome"]=="busy"&&many.sessions.request_count()==128);
    p::Outbox box;for(unsigned i=0;i<8;++i)CHECK(box.reserve_reply());CHECK(!box.reserve_reply());
    for(unsigned i=0;i<8;++i)CHECK(box.control("control"));
    CHECK(!box.can_control(1));
    box.release_reply();CHECK(box.control(std::string(p::Outbox::reply_capacity,'x')));CHECK(!box.can_control(1));
    Harness global;
    for(unsigned i=0;i<128;++i)CHECK(global.owner->submit("principal","C",1,authority(),command("R"+std::to_string(i)).dump(),true,0).ticket);
    CHECK(global.owner->submit("another","D",2,authority(),command("overflow").dump(),true,0).reply["outcome"]=="busy");
}
void faults(){
    Harness h;h.open();h.send("command",command());h.prepare=[&]{bool failed=false;try{h.sessions.policy(policy(),0);}catch(const p::Error&){failed=true;}CHECK(failed);};
    h.execute();CHECK(h.store.writes==0&&h.sessions.closed("C"));
    Harness clock;clock.now=10;clock.open();clock.send("command",command());bool failed=false;try{clock.sessions.tick(9);}catch(const p::Error&){failed=true;}CHECK(failed);
    clock.execute();CHECK(clock.store.writes==0&&clock.sessions.closed("C"));
    Harness unknown;unknown.open();unknown.send("command",command());unknown.store.after=[]{throw std::runtime_error("ambiguous native error");};unknown.execute();CHECK(unknown.pop()["body"]["outcome"]=="unknown");
    unknown.send("command",command("S"));CHECK(unknown.pop()["body"]["error"]["code"]=="storage.reconcile");
    Harness left,right;left.open();right.open();left.send("command",command());right.send("command",command());
    auto l=left.owner->run(*left.owner->take());auto r=right.owner->run(*right.owner->take());
    CHECK(!right.owner->finish(std::move(l),9999,true));CHECK(right.owner->finish(std::move(r),0,true));
    CHECK(left.owner->finish(std::move(l),0,true));CHECK(!left.owner->finish(std::move(l),9999,true));
}
void negotiation(){
    c::Sessions plain("E1",40,policy());plain.open("C","principal",authority(),0);plain.receive("C",envelope("hello",hello()),0);CHECK(plain.closed("C"));
    Harness low;low.sessions.open("C","principal",authority(),0);low.sessions.receive("C",envelope("hello",hello(true,4096)),0);CHECK(low.sessions.closed("C"));
    Harness optional;optional.sessions.open("C","principal",authority(),0);auto v=hello(false,4096);v["optional_features"].push_back("configuration.transactions");
    optional.sessions.receive("C",envelope("hello",v),0);const auto answer=optional.pop();CHECK(answer["type"]=="welcome");
    for(const auto& f:answer["body"]["optional_features"])CHECK(f!="configuration.transactions"&&f!="settings.preview");
    Harness docs;docs.sessions.open("C","principal",authority(),0);v=hello();v["document_versions"]=Json::array();docs.sessions.receive("C",envelope("hello",v),0);CHECK(docs.sessions.closed("C"));
}
int main(int argc,char** argv){try{
    if(argc!=3)return 2;
    fixtures=argv[2];const std::string name=argv[1];
    if(name=="COMMAND-COMMIT")committed();else if(name=="COMMAND-CANCEL")cancellation();else if(name=="COMMAND-POLICY")policy_changes();
    else if(name=="COMMAND-LIFETIME")lifetimes();else if(name=="COMMAND-CAPACITY")capacity();else if(name=="COMMAND-FAULT")faults();else if(name=="COMMAND-NEGOTIATE")negotiation();else return 2;
    std::cout<<name<<" passed\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
