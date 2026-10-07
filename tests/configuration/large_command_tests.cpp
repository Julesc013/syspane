#include "async_commands.hpp"
#include "session.hpp"
#include "editor_draft.hpp"
#include "settings_content_fixture.hpp"
#include <iostream>
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;using p::Json;
void check(bool b,int line){if(!b)throw std::runtime_error("large-command assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F> void rejects(F f){bool failed=false;try{f();}catch(const p::Error&){failed=true;}CHECK(failed);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(){c::Policy v;v.available=true;v.revision=7;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
struct Store:c::GenerationStore {
    c::Committed current,previous;unsigned writes=0;
    Store(const settings_fixture::Fixture& f):current{f.authored,{},f.catalog->resources(f.document["selection"],f.authored)}{}
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{std::vector<c::CommitReceipt> out;for(const auto* v:{&current,&previous})if(v->identity)out.push_back({*v->identity,c::authored_revision(v->documents)});return out;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{
        for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;
        return {};
    }
    c::Publication publish(const c::Committed& v,const std::function<void()>& guard)override{guard();previous=current;current=v;++writes;return c::Publication::durable;}
    c::ResourceProvider provider(){return c::make_resource_provider(*this,{"scene.content"});}
};
Json command(const settings_fixture::Fixture& f,const Json& scene,const std::string& id="R"){
    return {{"schema_version","0.5.0"},{"request_id",id},{"expected_revision","40"},{"policy_generation","7"},{"intent","commit"},
        {"content",f.document["selection"]},{"operations",Json::array({{{"op","scene.replace"},{"scene",scene}}})}};
}
std::string padded(const Json& q,std::size_t size=327680){auto text=q.dump();CHECK(text.size()<=size);text.insert(text.size()-1,size-text.size(),' ');return text;}
std::string envelope(const std::string& kind,const Json& value){Json root={{"type",kind},{"body",value}};if(kind!="hello"){root["connection_id"]="C";root["producer_epoch"]="E1";}return root.dump();}
Json hello(){return {{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","client"},{"max_frame_bytes",328704},
    {"document_versions",Json::array({{{"document","command"},{"version","0.5.0"}},{{"document","command-result"},{"version","0.1.0"}}})},
    {"required_features",Json::array({"configuration.transactions"})},
    {"optional_features",Json::array({"configuration.large-commands","configuration.content","configuration.scene-content","cancel","result.get"})}};}
std::size_t nodes(const Json& v){std::size_t n=1;if(v.is_object())for(auto it=v.begin();it!=v.end();++it)n+=1+nodes(it.value());else if(v.is_array())for(const auto& x:v)n+=nodes(x);return n;}
void run(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);auto cases=settings_fixture::read(root+"/tests/configuration/large-command-cases.json");
    f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};const auto moved=cases["moved_scene"];auto q=command(f,moved);const auto raw=padded(q);
    CHECK(f.authored.scene.dump().size()==262140&&moved.dump().size()==262144&&raw.size()==327680);
    if(name=="BOUNDS"){
        CHECK(c::parse_command(raw)==q);c::validate_command(q);rejects([&]{c::parse_command(padded(q,327681));});
        auto old=q;old["schema_version"]="0.4.0";rejects([&]{c::parse_command(old.dump());});rejects([&]{c::validate_command(old);});
        auto overflow=q;overflow["operations"][0]["scene"]["extensions"]["author.padding"].get_ref<std::string&>()+='x';rejects([&]{c::validate_command(overflow);});
        auto missing=q;missing.erase("content");rejects([&]{c::validate_command(missing);});
        auto simple=q;simple["operations"]=Json::array({{{"op","settings.set"},{"path","sampling.resources_ms"},{"value",1500}}});simple.erase("content");c::validate_command(simple);
        auto scene=f.authored.scene;scene["extensions"]={{"author.nodes",Json::array()}};const auto base=nodes(scene);
        for(std::size_t i=base;i<16384;++i)scene["extensions"]["author.nodes"].push_back(0);
        CHECK(nodes(scene)==16384);c::validate_scene_document(scene);auto wrapped=command(f,scene);CHECK(nodes(wrapped)>16384);c::validate_command(wrapped);
        CHECK(p::decode(envelope("command",wrapped),true).body==wrapped);rejects([&]{p::decode(envelope("command",wrapped));});
        scene["extensions"]["author.nodes"].push_back(0);rejects([&]{c::validate_command(command(f,scene));});
        wrapped["schema_version"]="0.4.0";rejects([&]{p::decode(envelope("command",wrapped),true);});
        auto other=wrapped;other["schema_version"]="0.5.0";rejects([&]{p::decode(envelope("heartbeat",other),true);});
        scene=f.authored.scene;Json chain=0;for(int i=0;i<30;++i)chain=Json::array({chain});scene["extensions"]={{"author.depth",chain}};
        c::validate_scene_document(scene);c::validate_command(command(f,scene));p::decode(envelope("command",command(f,scene)),true);
        scene["extensions"]["author.depth"]=Json::array({chain});rejects([&]{c::validate_command(command(f,scene));});
        auto excessive=command(f,f.authored.scene);excessive["extensions"]={{"author.nodes",Json::array()}};
        for(std::size_t n=nodes(excessive);n<=18432;++n)excessive["extensions"]["author.nodes"].push_back(0);
        rejects([&]{c::parse_command(excessive.dump());});
    }else if(name=="LEDGER"){
        p::Ledger ledger;rejects([&]{ledger.admit("p","c","legacy",raw,0);});
        for(unsigned i=0;i<50;++i)CHECK(ledger.admit("p","c",std::to_string(i),raw,0,true)==p::Admission::admitted);
        CHECK(ledger.size()==50&&ledger.reserved_bytes()==16588800);CHECK(ledger.admit("p","c","51",raw,0,true)==p::Admission::busy);
        CHECK(ledger.admit("p","other","0",raw,0,true)==p::Admission::pending);ledger.finish("p","0","{}",true,0);
        CHECK(ledger.admit("p","other","0",raw,599999,true)==p::Admission::replay);CHECK(ledger.admit("p","c","51",raw,599999,true)==p::Admission::busy);
        auto changed=raw;changed.back()=' ';CHECK(ledger.admit("p","c","0",changed,599999,true)==p::Admission::conflict);
        CHECK(ledger.admit("p","c","51",raw,600000,true)==p::Admission::admitted);CHECK(ledger.size()==50&&ledger.reserved_bytes()==16588800);
    }else if(name=="DRAFT"){
        ui::EditorDraft old(authority(),policy(),f.authored,"E1",f.resources());CHECK(old.execute({ui::MoveWidgets{{"widget:text"},30,20}}));
        rejects([&]{old.begin("commit","R");});CHECK(old.dirty()&&*old.scene()==moved&&!old.active_request());
        ui::EditorDraft draft(authority(),policy(),f.authored,"E1",f.resources(),true);CHECK(draft.execute({ui::MoveWidgets{{"widget:text"},30,20}}));CHECK(*draft.scene()==moved);
        const auto request=draft.begin("commit","R");CHECK(request&&c::parse_command(request->body)==q);draft.cancel_request();draft.disconnected();CHECK(draft.active_request()->body==request->body);
        Store store(f);c::Transactions tx(store,"E1",store.provider());auto answer=tx.submit("p","c",request->body,authority(),[]{return policy();},0);
        CHECK(answer["outcome"]=="accepted"&&store.writes==1);CHECK(draft.complete(request->ticket,answer));auto expected=moved;expected["revision"]="41";CHECK(*draft.scene()==expected);
    }else if(name=="ASYNC"){
        for(bool cancel:{false,true}){Store store(f);c::AsyncCommands owner(store,"E1",store.provider());owner.attach("E1",40,policy());
            auto admitted=owner.submit("p","c",1,authority(),raw,true,0);CHECK(admitted.ticket);
            CHECK(owner.submit("p","c",1,authority(),raw,true,0).reply["error"]["code"]=="request.pending");
            CHECK(owner.submit("p","c",1,authority(),q.dump(),true,0).reply["error"]["code"]=="request.changed");
            if(cancel)CHECK(owner.query("p",authority(),"R",true,0)["outcome"]=="unknown");
            auto ticket=owner.take();CHECK(ticket);auto done=owner.run(*ticket);CHECK(!owner.finish(std::move(done),0,false));CHECK(owner.finish(std::move(done),0,true));
            auto delivery=owner.delivery(0);CHECK(delivery&&delivery->reply["outcome"]==(cancel?"cancelled":"accepted"));CHECK(store.writes==(cancel?0U:1U));
            CHECK(owner.submit("p","other",2,authority(),raw,true,1).reply==delivery->reply);
            if(!cancel){CHECK(store.current.identity->body==raw);auto expected=moved;expected["revision"]="41";CHECK(store.current.documents.scene==expected);
                c::AsyncCommands restart(store,"E2",store.provider());restart.attach("E2",41,policy());Json lookup={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id","R"}};
                CHECK(restart.reconcile("p",authority(),lookup,600001)["result"]["revision"]=="41"&&store.writes==1);
                auto revoked=policy();revoked.revision=8;revoked.denied_capabilities.insert("scene.replace");restart.policy(revoked);
                CHECK(restart.reconcile("p",authority(),lookup,600002)["result"]["outcome"]=="unknown");
            }
        }
        Store store(f);c::AsyncCommands owner(store,"E1",store.provider());owner.attach("E1",40,policy());
        for(unsigned i=0;i<50;++i)CHECK(owner.submit("p","c",1,authority(),padded(command(f,moved,std::to_string(i))),true,0).ticket);
        CHECK(owner.submit("p","c",1,authority(),padded(command(f,moved,"51")),true,0).reply["outcome"]=="busy");CHECK(owner.request_count()==50&&store.writes==0);
        CHECK(owner.submit("p","c",1,authority(),padded(q,327681),true,0).reply["error"]["code"]=="command.size");
    }else if(name=="NEGOTIATION"){
        for(unsigned mode=0;mode<9;++mode){Store store(f);auto owner=std::make_shared<c::AsyncCommands>(store,"E1",store.provider());c::Sessions sessions("E1",40,policy(),{},owner);sessions.open("C","p",authority(),0);auto h=hello();
            if(mode==1||mode==2)h["max_frame_bytes"]=328703;
            if(mode==2)h["required_features"].push_back("configuration.large-commands");
            if(mode==3)h["optional_features"]=Json::array({"configuration.content","configuration.scene-content"});
            if(mode==4)h["optional_features"]=Json::array({"configuration.large-commands"});
            if(mode==5)h["optional_features"]=Json::array({"configuration.large-commands","configuration.content"});
            if(mode==6)h["document_versions"][0]["version"]="0.4.0";
            if(mode==7)h["required_features"]=Json::array();
            if(mode==8)h["document_versions"].erase(1);
            sessions.receive("C",envelope("hello",h),0);
            if(mode==2||mode==8){CHECK(sessions.closed("C"));continue;}
            CHECK(!sessions.closed("C"));auto welcome=sessions.pop("C",0);CHECK(welcome);auto features=p::decode(*welcome).body["optional_features"];
            CHECK((std::find(features.begin(),features.end(),"configuration.large-commands")!=features.end())==(mode==0||mode==4||mode==5));
            sessions.receive("C",envelope("command",q),0);CHECK(!sessions.closed("C"));
            if(mode==0){CHECK(owner->request_count()==1);auto t=owner->take();CHECK(t);CHECK(owner->finish(owner->run(*t),0,true));CHECK(p::decode(*sessions.pop("C",0)).body["outcome"]=="accepted");}
            else CHECK(p::decode(*sessions.pop("C",0)).body["error"]["code"]=="feature.unsupported"&&owner->request_count()==0);
        }
    }else throw std::runtime_error("unknown case");
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<"PASS "<<argv[1]<<'\n';return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
