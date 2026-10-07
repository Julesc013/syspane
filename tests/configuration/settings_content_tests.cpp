#include "settings_content_fixture.hpp"
#include "transaction.hpp"
namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;using c::Json;
void check(bool b,int line){if(!b)throw std::runtime_error("settings resource case:"+std::to_string(line));}
#define VERIFY(x) check(static_cast<bool>(x),__LINE__)
template<class F> void rejects(F f,const char* code=nullptr){bool bad=false;try{f();}catch(const p::Error& e){bad=true;if(code)VERIFY(std::string(e.what())==code);}VERIFY(bad);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(std::uint64_t revision=7){c::Policy v;v.available=true;v.revision=revision;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
using Fixture=settings_fixture::Fixture;
struct Store:c::GenerationStore {
    c::Committed current,previous;unsigned writes=0;
    explicit Store(const Fixture& f):current{f.authored,{},f.catalog->resources(f.document["selection"],f.authored)}{}
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{std::vector<c::CommitReceipt> out;for(const auto* v:{&current,&previous})if(v->identity)out.push_back({*v->identity,c::authored_revision(v->documents)});return out;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{
        for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;
        return {};
    }
    c::Publication publish(const c::Committed& v,const std::function<void()>& guard)override{guard();previous=current;current=v;++writes;return c::Publication::durable;}
    c::ResourceProvider provider(){return c::make_resource_provider(*this,{"scene.content"},[]{throw p::Error("test.import_unavailable");return std::vector<c::ContentPackage>{};});}
};
}
void run_settings_content_case(const std::string& name,const std::string& root){
    Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/configuration/settings-content-cases.json");
    ui::SettingsDraft d(authority(),policy(),f.authored,"E1",f.resources());
    if(name=="CONTENT"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());d.set("sampling.resources_ms",cases["edited_sampling_ms"]);
        const auto q=*d.begin("preview","P");const auto command=p::parse(q.body);VERIFY(command["schema_version"]==cases["command_version"]&&command["content"]==f.document["selection"]);
        VERIFY(command["operations"]==Json::array({{{"op","settings.set"},{"path","sampling.resources_ms"},{"value",1500}}}));
        auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0);VERIFY(result["outcome"]=="preview"&&store.writes==0);d.complete(q.ticket,result);
        VERIFY(d.dirty()&&d.value("sampling.resources_ms").requested==1500);d.revert();VERIFY(!d.dirty()&&!d.begin("commit","empty"));
        VERIFY(store.current.documents.scene==f.authored.scene&&store.current.resources->selection()==f.document["selection"]);
    }else if(name=="THEME"){
        d.set("display.theme_id",cases["selected_theme"]);VERIFY(d.value("display.theme_id").requested==cases["selected_theme"]);
        rejects([&]{d.set("display.theme_id",cases["invalid_theme"]);},"content.theme");VERIFY(d.value("display.theme_id").requested==cases["selected_theme"]);
        d.use_default("display.theme_id");VERIFY(!d.dirty());d.set("display.theme_id",cases["selected_theme"]);d.revert();VERIFY(!d.dirty());
        f.authored.scene["theme_id"]="theme:native";ui::SettingsDraft overridden(authority(),policy(),f.authored,"E1",f.resources());
        overridden.set("display.theme_id",cases["invalid_theme"]);auto q=*overridden.begin("preview","P");auto candidate=c::prepare_authored(f.authored,p::parse(q.body),authority(),policy());
        VERIFY(candidate.scene==f.authored.scene&&candidate.settings["display"]["theme_id"]==cases["invalid_theme"]);
        VERIFY(f.catalog->resources(f.document["selection"],candidate)->theme_pin()==f.document["themes"]["theme:native"]);
    }else if(name=="CONTENT-POLICY"){
        for(const auto* capability:{"content.select","scene.content","settings.set"}){
            ui::SettingsDraft blocked(authority(),policy(),f.authored,"E1",f.resources());blocked.set("sampling.resources_ms",1500);
            auto next=policy(8);next.denied_capabilities.insert(capability);blocked.policy(next);
            VERIFY(blocked.available()&&!blocked.value("sampling.resources_ms").editable&&!blocked.may_submit("commit")&&!blocked.may_submit("preview"));
            rejects([&]{blocked.begin("commit","R");});VERIFY(blocked.value("sampling.resources_ms").requested==1500);
        }
        auto resources=f.resources();resources.capabilities.clear();ui::SettingsDraft unsupported(authority(),policy(),f.authored,"E1",resources);
        VERIFY(unsupported.available()&&!unsupported.value("sampling.resources_ms").editable);rejects([&]{unsupported.set("sampling.resources_ms",1500);});
    }else if(name=="CONTENT-RELOAD"){
        d.set("sampling.resources_ms",1500);auto bad=f.resources();bad.selection["package"]["sha256"]=std::string(64,'0');
        rejects([&]{d.reload(f.authored,"E2",bad);});VERIFY(d.value("sampling.resources_ms").requested==1500&&d.revision()==40);
        rejects([&]{d.reload(f.authored,"E2");},"resource.contract");auto changed=f.authored;changed.settings["revision"]=changed.scene["revision"]="41";
        d.reload(changed,"E2",f.resources());VERIFY(d.revision()==41&&!d.dirty());d.close();bad.catalog.reset();
        ui::SettingsDraft erased(authority(),policy(),f.authored,"E1",f.resources());std::weak_ptr<const c::ContentCatalog> weak=f.catalog;f.catalog.reset();VERIFY(!weak.expired());
        auto denied=policy(8);denied.disclosure.clear();erased.policy(denied);VERIFY(weak.expired()&&!erased.available());
        erased.policy(policy(9));rejects([&]{erased.reload(f.authored,"E2");},"resource.contract");VERIFY(!erased.available());
        Fixture fresh(root);erased.reload(fresh.authored,"E2",fresh.resources());VERIFY(erased.available()&&erased.value("sampling.resources_ms").requested==1000);
    }else if(name=="CONTENT-RESULT"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());d.set("display.theme_id",cases["selected_theme"]);d.set("sampling.resources_ms",1500);
        const auto q=*d.begin("commit","R");const auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0);VERIFY(result["outcome"]=="accepted"&&store.writes==1);
        auto scene=f.authored.scene;scene["revision"]="41";VERIFY(store.current.documents.scene==scene&&store.current.resources->theme_pin()==f.document["themes"]["theme:contrast"]);
        d.disconnected();rejects([&]{d.begin("commit","duplicate");});c::Transactions restarted(store,"E2",store.provider());
        Json response={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id","R"},{"result",restarted.reconcile("P","E1","R",authority(),policy())}};
        VERIFY(d.reconciled(q.ticket,"Q","E2",response)&&d.revision()==41&&!d.dirty()&&store.writes==1);
        d.set("sampling.resources_ms",1200);d.revert();VERIFY(!d.dirty()&&d.value("display.theme_id").requested==cases["selected_theme"]);
        d.set("sampling.resources_ms",1200);auto next=*d.begin("commit","S");VERIFY(p::parse(next.body)["content"]==f.document["selection"]&&next.epoch=="E2");
    }else if(name=="CONTENT-BOUNDS"){
        rejects([&]{ui::SettingsDraft bare(authority(),policy(),f.authored,"E1");},"resource.contract");auto empty=f.resources();empty.catalog.reset();
        rejects([&]{d.reload(f.authored,"E1",empty);},"resource.context");VERIFY(d.available()&&!d.dirty());
        auto context=f.resources();ui::SettingsDraft independent(authority(),policy(),f.authored,"E1",context);context.selection=f.document["alternate_selection"];context.capabilities.clear();context.catalog.reset();
        independent.set("sampling.resources_ms",1500);auto q=*independent.begin("commit","R");VERIFY(p::parse(q.body)["content"]==f.document["selection"]);
        auto old=f.authored;old.scene=settings_fixture::read(root+"/spec/fixtures/valid/scene-portable.json");old.scene["revision"]="40";
        rejects([&]{d.reload(old,"E2");},"resource.contract");
    }else throw std::runtime_error("unknown settings resource case");
}
