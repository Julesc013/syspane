#include "async_commands.hpp"
#include "session.hpp"
#include "reconciliation.hpp"
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
    mutable unsigned reads=0;
    c::Committed load()const override{++reads;return current;}
    std::vector<c::CommitReceipt> receipts()const override{
        ++reads;
        std::vector<c::CommitReceipt> rows;for(const auto* r:{&current,&previous})if(r->identity)rows.push_back({*r->identity,c::authored_revision(r->documents)});return rows;
    }
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{
        ++reads;
        for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;
        return {};
    }
    c::Publication publish(const c::Committed& value,const std::function<void()>& guard)override{
        before();guard();after();previous=current;current=value;++writes;return c::Publication::durable;
    }
};
std::string envelope(const std::string& type,Json body,const std::string& id="C",const std::string& epoch="E1"){
    Json v{{"type",type},{"body",std::move(body)}};
    if(type!="hello"){v["connection_id"]=id;v["producer_epoch"]=epoch;}return v.dump();
}
Json hello(bool transactions=true,std::size_t frame=p::frame_limit){
    Json v{{"wire_major",0},{"wire_minor",1},{"role","console"},{"producer_epoch","client"},{"max_frame_bytes",frame},
        {"document_versions",Json::array({{{"document","command"},{"version","0.2.0"}},{{"document","command-result"},{"version","0.1.0"}}})},
        {"required_features",Json::array()},{"optional_features",Json::array({"settings.preview","result.get","cancel"})}};
    if(transactions)v["required_features"].push_back("configuration.transactions");
    return v;
}
Json reconciliation_hello(){auto v=hello();v["optional_features"].push_back("result.reconcile");
    for(const auto& name:{"reconciliation-request","reconciliation-result"})v["document_versions"].push_back({{"document",name},{"version","0.1.0"}});
    return v;
}
Json lookup(const std::string& original="E1",const std::string& id="R",const std::string& query="Q"){
    return {{"schema_version","0.1.0"},{"query_id",query},{"original_producer_epoch",original},{"request_id",id}};
}
struct Harness{
    Store store;std::string epoch;std::function<void()> prepare=[]{};
    std::shared_ptr<c::AsyncCommands> owner=std::make_shared<c::AsyncCommands>(store,epoch,[&](const c::Authored&){prepare();});
    c::Sessions sessions{epoch,c::authored_revision(store.current.documents),policy(),{},owner};std::uint64_t now=0;
    explicit Harness(std::string e="E1",Store prior={}):store(std::move(prior)),epoch(std::move(e)){}
    void open(const std::string& id="C",const std::string& principal="principal",bool transactions=true,bool reconciliation=false){
        sessions.open(id,principal,authority(),now);sessions.receive(id,envelope("hello",reconciliation?reconciliation_hello():hello(transactions)),now);CHECK(pop(id)["type"]=="welcome");
    }
    void send(const std::string& type,const Json& body,const std::string& id="C"){sessions.receive(id,envelope(type,body,id,epoch),now);CHECK(!sessions.closed(id));}
    Json pop(const std::string& id="C"){auto v=sessions.pop(id,now);CHECK(v);return p::parse(*v);}
    Json query(const char* type="result.get",const std::string& request="R",const std::string& id="C"){
        send(type,{{"request_id",request}},id);return pop(id)["body"];
    }
    void execute(){auto t=owner->take();CHECK(t);auto done=owner->run(*t);CHECK(!owner->finish(std::move(done),now,false));CHECK(!owner->take());CHECK(owner->finish(std::move(done),now,true));}
    Json reconcile(const Json& query=lookup(),const std::string& id="C"){
        const auto reads=store.reads,writes=store.writes;const auto count=sessions.request_count();send("result.reconcile",query,id);auto answer=pop(id);
        CHECK(store.reads==reads&&store.writes==writes&&sessions.request_count()==count);
        CHECK(answer["type"]=="result.reconciled"&&answer["body"]["query_id"]==query["query_id"]&&answer["body"]["original_producer_epoch"]==query["original_producer_epoch"]);
        return answer["body"]["result"];
    }
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
void receipts(){
    Harness first;first.open("C","principal",true,true);CHECK(first.reconcile()["outcome"]=="unknown");
    first.send("command",command());first.prepare=[&]{CHECK(first.reconcile()["error"]["code"]=="request.pending");};first.execute();first.pop();
    CHECK(first.reconcile()["revision"]=="41");first.now=600001;CHECK(first.query()["outcome"]=="unknown");CHECK(first.reconcile()["durable"]==true);
    auto saved=first.store;saved.before=[]{};saved.after=[]{};Harness second("E2",saved);second.open("C","principal",true,true);
    auto recovered=second.reconcile();CHECK(recovered["outcome"]=="accepted"&&recovered["revision"]=="41"&&recovered["producer_epoch"]=="E2"&&recovered["visible"]==false);
    CHECK(second.reconcile(lookup("E2"))["outcome"]=="unknown");
    auto edit=command();edit["expected_revision"]="41";second.send("command",edit);second.execute();second.pop();
    CHECK(second.reconcile(lookup("E1"))["revision"]=="41"&&second.reconcile(lookup("E2"))["revision"]=="42");
    edit["request_id"]="S";edit["expected_revision"]="42";second.send("command",edit);second.execute();second.pop();
    CHECK(second.reconcile(lookup("E1"))["outcome"]=="unknown"&&second.reconcile(lookup("E2"))["revision"]=="42"&&second.store.writes==3);
}
void reconciliation_policy(){
    Harness h;h.open("C","principal",true,true);h.send("command",command());h.execute();h.pop();
    h.open("D","foreign",true,true);CHECK(h.reconcile(lookup(),"D")["outcome"]=="unknown");
    auto next=policy(8);next.forced["sampling.resources_ms"]=2000;h.sessions.policy(next,0);h.pop();h.pop("D");
    auto answer=h.reconcile();CHECK(answer["outcome"]=="unknown"&&answer["error"]["code"]=="policy.forced"&&answer["stored"].is_null());
    next=policy(9);next.denied_capabilities.insert("result.reconcile");h.sessions.policy(next,0);h.pop();h.pop("D");
    CHECK(h.reconcile()["error"]["code"]=="policy.denied");
    h.sessions.policy(policy(10),0);h.pop();h.pop("D");CHECK(h.reconcile()["outcome"]=="accepted");
    CHECK(h.owner->reconcile("principal",{true,"collector",{"collector"}},lookup(),0)["result"]["error"]["code"]=="policy.denied");
    h.send("result.reconcile",lookup());h.sessions.policy(policy(11),0);CHECK(h.pop()["type"]=="gap"&&!h.sessions.pop("C",0));
    Harness pending;pending.open("C","principal",true,true);pending.send("command",command());
    next=policy(8);next.denied_capabilities.insert("settings.commit");pending.sessions.policy(next,0);pending.pop();
    CHECK(pending.reconcile()["error"]["code"]=="policy.denied");
}
void reconciliation_codec(){
    const auto q=lookup();auto body=q;body["result"]=c::committed_result("R","E2",41);
    auto selected=p::negotiate(p::handshake(reconciliation_hello()),p::handshake(reconciliation_hello()),{"console"});
    auto message=p::decode(envelope("result.reconciled",body,"C","E2"));CHECK(p::consume_reconciliation(message,selected,q,"C","E2")["revision"]=="41");
    for(unsigned i=0;i<10;++i){auto bad=body;auto m=message;auto selection=selected;auto query=q;
        if(i==0)m.connection_id="other";
        if(i==1)m.producer_epoch="E1";
        if(i==2)query["query_id"]="other";
        if(i==3)query["original_producer_epoch"]="E2";
        if(i==4)bad["result"]["request_id"]="other";
        if(i==5)bad["result"]["producer_epoch"]="E1";
        if(i==6)bad["result"]["durable"]=false;
        if(i==7)bad["result"]["visible"]=true;
        if(i==8)selection.features.erase("result.reconcile");
        if(i==9)selection.documents.erase({"reconciliation-result","0.1.0"});
        m.body=bad;bool failed=false;try{p::consume_reconciliation(m,selection,query,"C","E2");}catch(const p::Error&){failed=true;}CHECK(failed);
    }
    auto unknown=q;unknown["result"]=c::result({"unknown","request.reconcile"},"R","E2",41);p::validate_reconciliation_result(unknown,"E2");
    unknown["result"]["stored"]=false;bool failed=false;try{p::validate_reconciliation_result(unknown,"E2");}catch(const p::Error&){failed=true;}CHECK(failed);
}
void reconciliation_bounds(){
    Harness h;h.open("C","principal",true,true);for(unsigned i=0;i<8;++i)h.send("command",command("R"+std::to_string(i)));
    CHECK(h.reconcile()["outcome"]=="unknown"&&h.sessions.request_count()==8);
    auto missing=reconciliation_hello();missing["required_features"].push_back("result.reconcile");missing["document_versions"].erase(3);
    Harness bad;bad.sessions.open("C","principal",authority(),0);bad.sessions.receive("C",envelope("hello",missing),0);CHECK(bad.sessions.closed("C"));
    auto stored=h.store;auto invalid=command();stored.current.identity=c::CommitIdentity{"principal","E0","R",invalid.dump()};
    bool failed=false;try{Harness invalid_receipt("E1",stored);}catch(const p::Error&){failed=true;}CHECK(failed); // Revision 40 cannot prove expected 40 + one.
    Harness plain;plain.open();plain.sessions.receive("C",envelope("result.reconcile",lookup()),0);CHECK(plain.sessions.closed("C"));
    auto q=lookup();q["principal"]="forged";failed=false;try{p::decode(envelope("result.reconcile",q));}catch(const p::Error&){failed=true;}CHECK(failed);
    Harness committed;committed.open("C","principal",true,true);committed.send("command",command());
    auto done=committed.owner->run(*committed.owner->take());CHECK(committed.reconcile()["error"]["code"]=="request.pending");
    CHECK(committed.owner->finish(std::move(done),0,true));committed.pop();CHECK(committed.reconcile()["revision"]=="41");
    auto same=committed.store;same.previous=same.current;Harness deduplicated("E2",same);deduplicated.open("C","principal",true,true);CHECK(deduplicated.reconcile()["revision"]=="41");
    same.previous.identity->body=command().dump()+" ";failed=false;try{Harness conflict("E2",same);}catch(const p::Error&){failed=true;}CHECK(failed);
    committed.store.after=[]{throw std::runtime_error("ambiguous native error");};
    auto edit=command("T");edit["expected_revision"]="41";committed.send("command",edit);committed.execute();committed.pop();
    CHECK(committed.reconcile()["error"]["code"]=="storage.reconcile");
    Harness readonly;auto only=reconciliation_hello();only["required_features"]=Json::array({"result.reconcile"});only["optional_features"]=Json::array();
    readonly.sessions.open("C","principal",authority(),0);readonly.sessions.receive("C",envelope("hello",only),0);CHECK(readonly.pop()["type"]=="welcome");
    CHECK(readonly.reconcile()["outcome"]=="unknown");
}
int main(int argc,char** argv){try{
    if(argc!=3)return 2;
    fixtures=argv[2];const std::string name=argv[1];
    if(name=="COMMAND-COMMIT")committed();else if(name=="COMMAND-CANCEL")cancellation();else if(name=="COMMAND-POLICY")policy_changes();
    else if(name=="COMMAND-LIFETIME")lifetimes();else if(name=="COMMAND-CAPACITY")capacity();else if(name=="COMMAND-FAULT")faults();else if(name=="COMMAND-NEGOTIATE")negotiation();
    else if(name=="RECON-RECEIPTS")receipts();else if(name=="RECON-POLICY")reconciliation_policy();else if(name=="RECON-CODEC")reconciliation_codec();else if(name=="RECON-BOUNDS")reconciliation_bounds();else return 2;
    std::cout<<name<<" passed\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
