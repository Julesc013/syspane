#include "theme_command.hpp"
#include "async_commands.hpp"
#include "session.hpp"
#include "settings_content_fixture.hpp"
#include "digest.hpp"
#include <iostream>
namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;using p::Json;
void check(bool b,int line){if(!b)throw std::runtime_error("theme command assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool failed=false;try{f();}catch(const p::Error&){failed=true;}CHECK(failed);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(){c::Policy out;out.available=true;out.revision=7;return out;}
const std::set<std::string> caps={"scene.content","scene.edit-locks","scene.visibility","theme.typography","configuration.theme-overrides"};
struct Store:c::GenerationStore {
    c::Committed current,previous;unsigned writes=0,imports=0;std::function<void()> before_guard;
    explicit Store(const settings_fixture::Fixture& f):current{f.authored,{},f.catalog->resources(f.document["selection"],f.authored)}{}
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{std::vector<c::CommitReceipt> out;for(const auto* v:{&current,&previous})if(v->identity)out.push_back({*v->identity,c::authored_revision(v->documents)});return out;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;return {};}
    c::Publication publish(const c::Committed& next,const std::function<void()>& guard)override{if(before_guard)before_guard();guard();previous=current;current=next;++writes;return c::Publication::durable;}
    c::ResourceProvider provider(std::set<std::string> supported=caps){return c::make_resource_provider(*this,std::move(supported),[this]()->std::vector<c::ContentPackage>{++imports;throw p::Error("test.unexpected_import");});}
};
std::string padded(const Json& q){auto body=q.dump();CHECK(body.size()<=327680);body.insert(body.size()-1,327680-body.size(),' ');return body;}
std::string envelope(const std::string& kind,const Json& value){Json out={{"type",kind},{"body",value}};if(kind!="hello"){out["connection_id"]="C";out["producer_epoch"]="E1";}return out.dump();}
Json manifest_hashes(const c::ResourceSet& resources){std::set<std::string> sorted;for(const auto& p:resources.packages())sorted.insert(c::sha256(p->manifest));return sorted;}
void run(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/configuration/theme-command-cases.json");const auto q=cases["command"];
    if(name=="SCHEMA"){
        c::validate_command(q);auto body=padded(q);CHECK(c::parse_command(body)==q);rejects([&]{c::parse_command(body+" ");});
        for(const char* suffix:{"missing","source","color","roles","selection"})rejects([&]{c::validate_command(settings_fixture::read(root+"/spec/fixtures/invalid/command-theme-"+suffix+".json"));});
        auto invalid=q;invalid["theme_edit"]["font"]["family"]=std::string("Bad\xc2\x85");rejects([&]{c::validate_command(invalid);});
        for(const char* version:{"0.2.0","0.3.0","0.4.0","0.5.0","0.6.0","0.7.0"}){invalid=q;invalid["schema_version"]=version;rejects([&]{c::validate_command(invalid);});}
        auto large=q;large["operations"][0]["scene"]["extensions"]["author.padding"]="";auto& scene=large["operations"][0]["scene"];const auto size=scene.dump().size();CHECK(size<262144);scene["extensions"]["author.padding"]=std::string(262144-size,'x');CHECK(scene.dump().size()==262144);c::validate_command(large);CHECK(c::parse_command(padded(large))==large);
    }else if(name=="TRANSACTION"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());auto submit=[&](const Json& command){return tx.submit("p","C",command.dump(),authority(),[]{return policy();},0);};
        auto preview=q;preview["request_id"]="preview";preview["intent"]="preview";CHECK(submit(preview)["outcome"]=="preview"&&store.writes==0);
        const auto bytes=padded(q);auto answer=tx.submit("p","C",bytes,authority(),[]{return policy();},1);CHECK(answer["outcome"]=="accepted"&&answer["revision"]=="41"&&answer["durable"]&&!answer["visible"]&&store.writes==1&&store.imports==0);
        CHECK(store.current.identity->body==bytes&&store.current.resources->selection()==cases["selection"]&&store.current.resources->theme()==cases["artifact"]["theme"]&&manifest_hashes(*store.current.resources)==cases["selected_manifests"]);
        auto expected=cases["expected"];expected["settings"]["revision"]=expected["scene"]["revision"]="41";CHECK(store.current.documents.scene==expected["scene"]&&store.current.documents.settings==expected["settings"]);
        CHECK(tx.submit("p","C",bytes,authority(),[]{return policy();},2)==answer&&store.writes==1);CHECK(submit(q)["error"]["code"]=="request.changed"&&store.writes==1);
        c::Transactions restarted(store,"E2",store.provider());CHECK(restarted.reconcile("p","E1","theme:edit",authority(),policy())["revision"]=="41"&&store.writes==1);
        auto noop=q;noop["expected_revision"]="41";noop["operations"][0]["scene"]["revision"]="41";noop["request_id"]="no-change";noop["theme_edit"]["source"]=store.current.resources->theme_pin();CHECK(restarted.submit("p","C",noop.dump(),authority(),[]{return policy();},0)["error"]["code"]=="theme.no_change");
        CHECK(restarted.submit("p","C",cases["keep"].dump(),authority(),[]{return policy();},1)["revision"]=="42");CHECK(store.current.resources->selection()==cases["selection"]&&store.current.documents.settings["display"]["reduced_motion"]);
        CHECK(restarted.submit("p","C",cases["reset"].dump(),authority(),[]{return policy();},2)["revision"]=="43");CHECK(store.current.resources->selection()==cases["base_selection"]&&manifest_hashes(*store.current.resources)==cases["base_manifests"]);
        for(unsigned n=0;n<10;++n){auto edit=q;const auto revision=43+n*2;edit["request_id"]="edit:"+std::to_string(n);edit["expected_revision"]=edit["operations"][0]["scene"]["revision"]=std::to_string(revision);
            CHECK(restarted.submit("p","C",edit.dump(),authority(),[]{return policy();},3+n*2)["revision"]==std::to_string(revision+1));CHECK(manifest_hashes(*store.current.resources)==cases["selected_manifests"]);
            auto reset=cases["reset"];reset["request_id"]="reset:"+std::to_string(n);reset["expected_revision"]=reset["operations"][0]["scene"]["revision"]=std::to_string(revision+1);
            CHECK(restarted.submit("p","C",reset.dump(),authority(),[]{return policy();},4+n*2)["revision"]==std::to_string(revision+2));CHECK(manifest_hashes(*store.current.resources)==cases["base_manifests"]);}
        CHECK(store.imports==0);
    }else if(name=="GUARDS"){
        for(const char* cap:{"configuration.theme-overrides","theme.typography","theme.edit","scene.content","content.select","scene.replace"}){Store store(f);auto current=policy();c::Transactions tx(store,"E1",store.provider());current.denied_capabilities.insert(cap);CHECK(tx.submit("p","C",q.dump(),authority(),[&]{return current;},0)["outcome"]=="denied"&&store.writes==0);}
        for(const auto& cap:caps){Store store(f);auto reduced=caps;reduced.erase(cap);c::Transactions tx(store,"E1",store.provider(reduced));CHECK(!tx.supports_theme_overrides());CHECK(tx.submit("p","C",q.dump(),authority(),[]{return policy();},0)["outcome"]=="invalid"&&store.writes==0);}
        for(unsigned mode=0;mode<5;++mode){Store store(f);auto bad=q;if(mode==0)bad["theme_edit"]["source"]["sha256"]=std::string(64,'0');if(mode==1)bad["content"]["package"]["sha256"]=std::string(64,'0');if(mode==2)bad["content"]["theme_override"]["theme"]["sha256"]=std::string(64,'0');if(mode==3)bad["theme_edit"]=nullptr;if(mode==4)bad["operations"][0]["scene"]["theme_id"]="missing";c::Transactions tx(store,"E1",store.provider());CHECK(tx.submit("p","C",bad.dump(),authority(),[]{return policy();},0)["outcome"]=="invalid"&&store.writes==0&&store.imports==0);}
        Store store(f);auto current=policy();store.before_guard=[&]{current.denied_capabilities.insert("theme.edit");};c::Transactions tx(store,"E1",store.provider());CHECK(tx.submit("p","C",q.dump(),authority(),[&]{return current;},0)["outcome"]=="denied"&&store.writes==0);
        auto saver=q;saver["operations"]=Json::array({{{"op","settings.set"},{"path","display.theme_id"},{"value",cases["artifact"]["theme"]["theme_id"]}}});CHECK(tx.submit("p","C",saver.dump(),{true,"saver_settings",{"saver_settings"}},[]{return policy();},1)["outcome"]=="denied");
        Store stopped(f);bool cancel=false;auto provider=stopped.provider();provider.after_prepare=[&]{cancel=true;};c::Transactions cancelled(stopped,"E1",provider);CHECK(cancelled.submit("p","C",q.dump(),authority(),[]{return policy();},0,[&]{return cancel;})["outcome"]=="cancelled"&&stopped.writes==0);
        Store saved(f);c::Transactions committed(saved,"E1",saved.provider());CHECK(committed.submit("p","C",q.dump(),authority(),[]{return policy();},0)["outcome"]=="accepted");auto denied=policy();denied.denied_capabilities.insert("theme.typography");CHECK(committed.submit("p","C",q.dump(),authority(),[&]{return denied;},1)["outcome"]=="denied");CHECK(committed.reconcile("p","E1","theme:edit",authority(),denied)["outcome"]=="denied");auto wrong=q;wrong["theme_edit"]["font"]["weight"]=900;rejects([&]{c::validate_theme_command_binding(wrong,*saved.current.resources);});
    }else if(name=="ASYNC"){
        Store store(f);c::AsyncCommands owner(store,"E1",store.provider());owner.attach("E1",40,policy());auto admission=owner.submit("p","C",1,authority(),padded(q),true,0);CHECK(admission.ticket);auto ticket=owner.take();CHECK(ticket&&*ticket==admission.ticket);CHECK(owner.finish(owner.run(*ticket),1,true));auto delivery=owner.delivery(1);CHECK(delivery&&delivery->reply["outcome"]=="accepted"&&store.writes==1);
        auto denied=policy();denied.revision=8;denied.denied_capabilities.insert("configuration.theme-overrides");owner.policy(denied);CHECK(owner.query("p",authority(),"theme:edit",false,2)["outcome"]=="unknown");
        Store pending(f);c::AsyncCommands queued(pending,"E1",pending.provider());queued.attach("E1",40,policy());auto a=queued.submit("p","C",1,authority(),q.dump(),true,0);CHECK(a.ticket);queued.query("p",authority(),"theme:edit",true,1);auto t=queued.take();CHECK(t&&queued.finish(queued.run(*t),2,true));CHECK(queued.delivery(2)->reply["outcome"]=="cancelled"&&pending.writes==0);
    }else if(name=="NEGOTIATE"){
        for(unsigned mode=0;mode<13;++mode){Store store(f);auto supported=caps;if(mode==9)supported.erase("theme.typography");auto owner=std::make_shared<c::AsyncCommands>(store,"E1",store.provider(supported));c::Sessions sessions("E1",40,policy(),{},owner);sessions.open("C","p",authority(),0);
            Json h={{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","client"},{"max_frame_bytes",328704},{"document_versions",Json::array({{{"document","command"},{"version","0.8.0"}},{{"document","command-result"},{"version","0.1.0"}}})},{"required_features",Json::array()},{"optional_features",cases["features"]}};
            if(mode>=1&&mode<=7)h["optional_features"].erase(mode-1);
            if(mode==8)h["max_frame_bytes"]=328703;
            if(mode==9)h["document_versions"].push_back({{"document","command"},{"version","0.7.0"}});
            if(mode==10)h["document_versions"].erase(1);
            if(mode==11)h["document_versions"][0]["version"]="0.7.0";
            if(mode==12){h["optional_features"].erase(3);h["required_features"].push_back("configuration.theme-overrides");}
            sessions.receive("C",envelope("hello",h),0);if(mode==12){CHECK(sessions.closed("C"));continue;}CHECK(!sessions.closed("C"));auto welcome=sessions.pop("C",0);CHECK(welcome);auto features=p::decode(*welcome).body["optional_features"];bool admitted=false;for(const auto& feature:features)if(feature=="configuration.theme-overrides")admitted=true;CHECK(admitted==(mode==0));
            sessions.receive("C",envelope("command",q),0);CHECK(!sessions.closed("C"));if(mode==0){auto ticket=owner->take();CHECK(ticket&&owner->finish(owner->run(*ticket),1,true));CHECK(p::decode(*sessions.pop("C",1)).body["outcome"]=="accepted"&&store.writes==1);}else CHECK(p::decode(*sessions.pop("C",1)).body["error"]["code"]=="feature.unsupported"&&store.writes==0);
        }
    }else throw std::runtime_error("unknown theme command test");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
