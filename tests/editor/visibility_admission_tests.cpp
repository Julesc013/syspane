#include "editor_draft.hpp"
#include "async_commands.hpp"
#include "session.hpp"
#include "layout.hpp"
#include "digest.hpp"
#include "../configuration/settings_content_fixture.hpp"
namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;using p::Json;
void check(bool b,int line){if(!b)throw std::runtime_error("visibility admission assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f,const std::string& code={}){bool bad=false;try{f();}catch(const p::Error& e){bad=code.empty()||code==e.what();}CHECK(bad);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(){c::Policy v;v.available=true;v.revision=7;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
struct Store:c::GenerationStore {
    c::Committed current,previous;unsigned writes=0;
    Store(const settings_fixture::Fixture& f):current{f.authored,{},f.catalog->resources(f.document["selection"],f.authored)}{}
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{std::vector<c::CommitReceipt> out;for(const auto* v:{&current,&previous})if(v->identity)out.push_back({*v->identity,c::authored_revision(v->documents)});return out;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;return {};}
    c::Publication publish(const c::Committed& v,const std::function<void()>& guard)override{guard();previous=current;current=v;++writes;return c::Publication::durable;}
    c::ResourceProvider provider(bool visibility=true){return c::make_resource_provider(*this,visibility?std::set<std::string>{"scene.content","scene.edit-locks","scene.visibility"}:std::set<std::string>{"scene.content","scene.edit-locks"});}
};
std::string envelope(const std::string& type,const Json& body){Json v={{"type",type},{"body",body}};if(type!="hello"){v["connection_id"]="C";v["producer_epoch"]="E1";}return v.dump();}
Json pin(const c::ContentPackage& package,bool document=false){auto m=Json::parse(package.manifest);const auto kind=m["kind"].get<std::string>();const auto& bytes=package.assets.at(kind+".json");return {{"id",document?Json::parse(bytes)[kind+"_id"]:m["package_id"]},{"version","0.1.0"},{"sha256",c::sha256(document?bytes:package.manifest)}};}
c::ContentPackage pack(const std::string& id,const std::string& kind,const Json& doc,Json deps=Json::array()){
    const auto bytes=doc.dump()+"\n";Json m={{"schema_version","0.1.0"},{"package_id",id},{"version","0.1.0"},{"kind",kind},{"license","MIT"},{"dependencies",deps},
        {"assets",Json::array({{{"path",kind+".json"},{"media_type","application/json"},{"sha256",c::sha256(bytes)},{"bytes",bytes.size()}}})},
        {"total_unpacked_bytes",bytes.size()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    return {m.dump()+"\n",{{kind+".json",bytes}}};
}
}
void run_visibility_admission(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);auto cases=settings_fixture::read(root+"/tests/editor/visibility-admission-cases.json");f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};
    auto resources=f.resources();resources.capabilities.insert({"scene.edit-locks","scene.visibility","configuration.edit-locks","configuration.visibility","configuration.large-commands"});
    auto make=[&]{return ui::EditorDraft(authority(),policy(),f.authored,"E1",resources,true);};auto d=make();
    const ui::SetWidgetVisibility set{{"widget:text"},cases["rule"]},clear{{"widget:text"},std::nullopt};
    auto q=settings_fixture::read(root+"/spec/fixtures/valid/command-visibility.json");
    if(name=="SCHEMAS"){
        for(const char* key:{"conditional","cleared","locked","multi","grouped"})c::validate_scene_document(cases[key]);
        c::validate_command(q);
        for(const char* file:{"scene-visibility-null","scene-visibility-collection","scene-visibility-coercion","scene-old-visibility"})rejects([&]{c::validate_scene_document(settings_fixture::read(root+"/spec/fixtures/invalid/"+file+".json"));});
        for(const char* file:{"command-old-visibility","command-visibility-no-content"})rejects([&]{c::validate_command(settings_fixture::read(root+"/spec/fixtures/invalid/"+file+".json"));});
        auto raw=q.dump();raw.insert(raw.size()-1,327680-raw.size(),' ');CHECK(c::parse_command(raw)==q);raw+=' ';rejects([&]{c::parse_command(raw);},"command.size");CHECK(p::decode(envelope("command",q),true).body==q);
        auto large=cases["conditional"];large["extensions"]={{"padding",std::string(262144,'x')}};rejects([&]{c::validate_scene_document(large);},"authored.size");
        auto bound=f.authored;bound.scene=cases["cleared"];auto snapshot=f.catalog->resources(f.document["selection"],bound);CHECK(snapshot->required().count("scene.edit-locks")&&snapshot->required().count("scene.visibility")&&snapshot->required().count("scene.content"));
        rejects([&]{c::authorize_resources(*snapshot,policy(),{"scene.content","scene.edit-locks"});});rejects([&]{c::validate_resource_binding(*f.catalog->resources(f.document["selection"],f.authored),bound);});CHECK(c::upgrade_scene_content(bound.scene)==bound.scene);
        auto kinds=settings_fixture::read(root+"/spec/fixtures/valid/scene-content.json");kinds["schema_version"]="0.5.0";for(auto& w:kinds["widgets"])w["visibility"]=cases["rule"];c::validate_scene_document(kinds);
        namespace s=syspane::scene;s::Display display;display.id="D1";display.bounds=display.work={0,0,800*64,600*64};const auto original=cases["conditional"];
        std::map<std::string,s::Metrics> sizes;for(const auto& w:original["widgets"])sizes.emplace(w["id"].get<std::string>(),s::Metrics{{32*64,16*64},{64*64,32*64}});
        const auto plan=s::resolve(cases["conditional"],{{display},{},"D1"},sizes);CHECK(plan.nodes.size()==3&&cases["conditional"]==original);
        auto scene=cases["conditional"];scene["widgets"].erase(2);scene["roots"].erase(2);scene["theme_id"]="theme:native";
        auto theme=pack("package:theme","theme",settings_fixture::read(root+"/spec/fixtures/valid/theme.json")),sc=pack("package:scene","scene",scene);
        Json preset={{"schema_version","0.1.0"},{"preset_id","preset:visibility"},{"version","0.1.0"},{"parent",nullptr},{"scene",pin(sc,true)},{"theme",pin(theme,true)},
            {"settings",Json::array()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
        auto pr=pack("package:preset","preset",preset,Json::array({pin(sc),pin(theme)}));c::ContentCatalog catalog({theme,sc,pr});
        auto preview=catalog.preview(pin(pr),pin(pr,true),f.authored,"P",authority(),policy(),resources.capabilities);CHECK(preview.command["schema_version"]=="0.7.0"&&preview.candidate.scene==scene);
        auto caps=resources.capabilities;caps.erase("configuration.visibility");rejects([&]{catalog.preview(pin(pr),pin(pr,true),f.authored,"P",authority(),policy(),caps);});
    }else if(name=="DRAFT"){
        d.select({"widget:text"});CHECK(d.visibility_available()&&!d.execute({clear}));CHECK(d.execute({set})&&*d.scene()==cases["conditional"]&&d.undo_count()==1);CHECK(!d.execute({set})&&d.undo_count()==1);
        CHECK(d.execute({clear})&&*d.scene()==cases["cleared"]);CHECK(d.undo()&&*d.scene()==cases["conditional"]);CHECK(d.undo()&&*d.scene()==f.authored.scene);CHECK(d.redo()&&d.redo());
        CHECK(d.selection()==std::vector<std::string>{"widget:text"});auto request=d.begin("commit","R");CHECK(request);auto body=c::parse_command(request->body);CHECK(body["schema_version"]=="0.7.0"&&body["operations"][0]["scene"]==cases["cleared"]);
        auto e=make();e.execute({ui::SetWidgetLocks{{"widget:text"},true}});e.execute({ui::SetWidgetLocks{{"widget:text"},false},set});CHECK(*e.scene()==cases["conditional"]);e.execute({ui::SetWidgetLocks{{"widget:text"},true}});CHECK(*e.scene()==cases["locked"]);
    }else if(name=="GUARDS"){
        d.execute({ui::SetWidgetLocks{{"widget:text"},true}});rejects([&]{d.execute({set});},"editor.locked");CHECK(d.execute({ui::SetWidgetLocks{{"widget:text"},false},set})&&*d.scene()==cases["conditional"]);
        auto value=f.authored;value.scene=cases["grouped"];d.reload(value,"E1",resources);
        for(const auto& e:std::vector<ui::SceneEdit>{ui::UnwrapWidget{"widget:group"},ui::UngroupWidget{"widget:group"}}){rejects([&]{d.execute({e});},"editor.visibility_container");CHECK(*d.scene()==cases["grouped"]&&d.undo_count()==0);}
        d.execute({ui::SetWidgetLocks{{"widget:group"},true}});rejects([&]{d.execute({set});},"editor.locked");d.execute({ui::SetWidgetLocks{{"widget:group"},false},ui::SetWidgetLocks{{"widget:text"},true}});
        rejects([&]{d.execute({ui::SetWidgetVisibility{{"widget:group"},std::nullopt}});},"editor.locked");d.execute({ui::SetWidgetLocks{{"widget:text"},false},ui::SetWidgetVisibility{{"widget:group"},std::nullopt},ui::UnwrapWidget{"widget:group"}});CHECK(*d.scene()==cases["cleared"]);
    }else if(name=="PRESERVE"){
        d.execute({set});d.execute({ui::DuplicateWidgets{{"widget:text"},{{"widget:text","widget:copy"}}}});CHECK(d.scene()->at("widgets")[3]["visibility"]==cases["rule"]);d.undo();
        d.execute({ui::GroupWidgets{{"widget:text","widget:second"},"widget:new","Group"}});CHECK(!d.scene()->at("widgets")[3].contains("visibility")&&d.scene()->at("widgets")[0]["visibility"]==cases["rule"]);d.undo();
        d.execute({ui::WrapWidgets{{"widget:text"},"widget:new","Wrap",{{"base",{{"kind","stack"},{"axis","vertical"},{"gap_dip",8},{"overflow","diagnose"}}}}}});CHECK(d.scene()->at("widgets")[0]["visibility"]==cases["rule"]&&!d.scene()->at("widgets")[3].contains("visibility"));d.execute({ui::UnwrapWidget{"widget:new"}});CHECK(*d.scene()==cases["conditional"]);
        d.execute({ui::ReparentWidgets{{"widget:text"},std::nullopt,1},ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"Changed"},ui::MoveWidgets{{"widget:text"},5,0}});CHECK(d.scene()->at("widgets")[0]["visibility"]==cases["rule"]);
        auto value=f.authored;value.scene=cases["conditional"];ui::SettingsDraft settings(authority(),policy(),value,"E1",resources,true);settings.set("display.enabled",false);const auto request=settings.begin("commit","S");CHECK(request);auto command=c::parse_command(request->body);CHECK(command["schema_version"]=="0.5.0");CHECK(c::prepare_authored(value,command,authority(),policy()).scene==value.scene);
    }else if(name=="ATOMIC"){
        d.select({"widget:text"});d.execute({set});d.undo();const auto before=*d.scene();const auto bytes=d.history_bytes();
        for(const auto& e:std::vector<ui::SetWidgetVisibility>{{{},cases["rule"]},{{"widget:text","widget:text"},cases["rule"]},{{"widget:text","missing"},cases["rule"]},{{"widget:text"},Json()}}){rejects([&]{d.execute({e});});CHECK(*d.scene()==before&&d.redo_count()==1&&d.history_bytes()==bytes);}
        rejects([&]{d.execute({set,ui::RemoveWidgets{{"missing"}}});});CHECK(*d.scene()==before&&d.redo_count()==1&&d.selection()==std::vector<std::string>{"widget:text"});
        CHECK(d.execute({ui::SetWidgetVisibility{{"widget:text","widget:second"},cases["rule"]}})&&*d.scene()==cases["multi"]);
    }else if(name=="POLICY"){
        for(const char* cap:{"configuration.visibility","configuration.edit-locks","scene.visibility","scene.edit-locks"}){auto denied=resources;denied.capabilities.erase(cap);ui::EditorDraft old(authority(),policy(),f.authored,"E1",denied,true);CHECK(!old.visibility_available());rejects([&]{old.execute({clear});});}
        ui::EditorDraft small(authority(),policy(),f.authored,"E1",resources);CHECK(!small.visibility_available());rejects([&]{small.execute({set});});
        for(const char* cap:{"configuration.visibility","scene.visibility","configuration.edit-locks","scene.edit-locks","scene.replace"}){auto e=make();auto next=policy();next.revision=8;next.denied_capabilities.insert(cap);e.policy(next);CHECK(!e.visibility_available());rejects([&]{e.execute({clear});});}
        d.execute({set});auto next=policy();next.revision=8;next.denied_capabilities.insert("configuration.visibility");d.policy(next);rejects([&]{d.undo();});CHECK(*d.scene()==cases["conditional"]&&d.undo_count()==1);
        auto e=make();e.execute({set});e.begin("commit","R");CHECK(!e.visibility_available());rejects([&]{e.execute({clear});});e.disconnected();rejects([&]{e.undo();});
        Store store(f);c::Transactions tx(store,"E1",store.provider());auto denied=policy();denied.denied_capabilities.insert("configuration.visibility");auto result=tx.submit("p","C",q.dump(),authority(),[&]{return denied;},0);CHECK(result["error"]["code"]=="policy.denied"&&store.writes==0);
    }else if(name=="NEGOTIATE"){
        for(unsigned mode=0;mode<11;++mode){Store store(f);auto owner=std::make_shared<c::AsyncCommands>(store,"E1",store.provider(mode!=7&&mode!=9));c::Sessions sessions("E1",40,policy(),{},owner);sessions.open("C","p",authority(),0);
            Json h={{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","client"},{"max_frame_bytes",328704},{"document_versions",Json::array({{{"document","command"},{"version","0.7.0"}},{{"document","command-result"},{"version","0.1.0"}}})},{"required_features",Json::array({"configuration.transactions"})},{"optional_features",Json::array({"configuration.large-commands","configuration.content","configuration.scene-content","configuration.edit-locks","configuration.visibility"})}};
            if(mode>=1&&mode<=5)h["optional_features"].erase(mode-1);
            if(mode==6)h["max_frame_bytes"]=328703;
            if(mode==7)h["document_versions"].push_back({{"document","command"},{"version","0.6.0"}});
            if(mode==8){h["optional_features"].erase(0);h["required_features"].push_back("configuration.visibility");}
            if(mode==10)h["document_versions"].erase(1);
            sessions.receive("C",envelope("hello",h),0);if(mode==8||mode==9||mode==10){CHECK(sessions.closed("C"));continue;}CHECK(!sessions.closed("C"));auto welcome=sessions.pop("C",0);CHECK(welcome);auto features=p::decode(*welcome).body["optional_features"];bool admitted=false;for(const auto& feature:features)if(feature=="configuration.visibility")admitted=true;CHECK(admitted==(mode==0));
            sessions.receive("C",envelope("command",q),0);CHECK(!sessions.closed("C"));if(mode==0){auto ticket=owner->take();CHECK(ticket&&owner->finish(owner->run(*ticket),0,true));CHECK(p::decode(*sessions.pop("C",0)).body["outcome"]=="accepted"&&store.writes==1);}else CHECK(p::decode(*sessions.pop("C",0)).body["error"]["code"]=="feature.unsupported"&&store.writes==0);
        }
    }else if(name=="DURABLE"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());auto bytes=q.dump();bytes.insert(bytes.size()-1,327680-bytes.size(),' ');const auto result=tx.submit("p","C",bytes,authority(),[]{return policy();},0);CHECK(result["outcome"]=="accepted"&&result["revision"]=="41"&&result["durable"]&&!result["visible"]&&store.writes==1);
        auto expected=cases["conditional"];expected["revision"]="41";CHECK(store.current.documents.scene==expected&&store.current.identity->body==bytes);CHECK(tx.submit("p","C",bytes,authority(),[]{return policy();},1)==result&&store.writes==1);
        CHECK(tx.submit("p","C",q.dump(),authority(),[]{return policy();},2)["error"]["code"]=="request.changed"&&store.writes==1);
        c::AsyncCommands restarted(store,"E2",store.provider());restarted.attach("E2",41,policy());Json lookup={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id","visibility"}};auto recovered=restarted.reconcile("p",authority(),lookup,0);CHECK(recovered["result"]["outcome"]=="accepted"&&recovered["result"]["revision"]=="41"&&store.writes==1);
    }else throw std::runtime_error("unknown visibility admission test");
}
