#include "editor_draft.hpp"
#include "async_commands.hpp"
#include "session.hpp"
#include "../configuration/settings_content_fixture.hpp"
namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;using p::Json;
using ui::edit_locked;using ui::edit_protected;
void check(bool b,int line){if(!b)throw std::runtime_error("edit-lock assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(){c::Policy v;v.available=true;v.revision=7;v.disclosure[ {"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
struct Store:c::GenerationStore {
    c::Committed current,previous;unsigned writes=0;
    Store(const settings_fixture::Fixture& f):current{f.authored,{},f.catalog->resources(f.document["selection"],f.authored)}{}
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{std::vector<c::CommitReceipt> out;for(const auto* v:{&current,&previous})if(v->identity)out.push_back({*v->identity,c::authored_revision(v->documents)});return out;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;return {};}
    c::Publication publish(const c::Committed& v,const std::function<void()>& guard)override{guard();previous=current;current=v;++writes;return c::Publication::durable;}
    c::ResourceProvider provider(bool locks=true){return c::make_resource_provider(*this,locks?std::set<std::string>{"scene.content","scene.edit-locks"}:std::set<std::string>{"scene.content"});}
};
std::string envelope(const std::string& type,const Json& body){Json v={{"type",type},{"body",body}};if(type!="hello"){v["connection_id"]="C";v["producer_epoch"]="E1";}return v.dump();}
}
void run_edit_lock(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);auto cases=settings_fixture::read(root+"/tests/editor/edit-lock-cases.json");f.authored={cases["authored"]["settings"],cases["authored"]["scene"]};
    auto resources=f.resources();resources.capabilities.insert({"scene.edit-locks","configuration.edit-locks","configuration.large-commands"});
    auto make=[&]{return ui::EditorDraft(authority(),policy(),f.authored,"E1",resources,true);};auto d=make();const ui::SetWidgetLocks lock{{"widget:text"},true},unlock{{"widget:text"},false};
    auto q=settings_fixture::read(root+"/spec/fixtures/valid/command-edit-locks.json");
    if(name=="SCHEMAS"){
        for(const char* key:{"locked","unlocked","multi","grouped"}){c::validate_scene_document(cases[key]);}
        c::validate_command(q);
        for(const char* file:{"scene-edit-lock-type","scene-old-edit-lock"})rejects([&]{c::validate_scene_document(settings_fixture::read(root+"/spec/fixtures/invalid/"+file+".json"));});
        rejects([&]{c::validate_command(settings_fixture::read(root+"/spec/fixtures/invalid/command-old-edit-lock.json"));});
        auto missing=q;missing.erase("content");rejects([&]{c::validate_command(missing);});auto raw=q.dump();raw.insert(raw.size()-1,327680-raw.size(),' ');CHECK(c::parse_command(raw)==q);raw+=' ';rejects([&]{c::parse_command(raw);});
        CHECK(p::decode(envelope("command",q),true).body==q);auto old=q;old["schema_version"]="0.5.0";rejects([&]{c::validate_command(old);});
        auto bound=f.authored;bound.scene=cases["locked"];auto snapshot=f.catalog->resources(f.document["selection"],bound);CHECK(snapshot->required().count("scene.edit-locks"));rejects([&]{c::authorize_resources(*snapshot,policy(),{"scene.content"});});
        rejects([&]{c::validate_resource_binding(*f.catalog->resources(f.document["selection"],f.authored),bound);});CHECK(c::upgrade_scene_content(bound.scene)==bound.scene);
    }else if(name=="DRAFT"){
        d.select({"widget:text"});CHECK(d.locks_available()&&!d.execute({unlock}));CHECK(d.execute({lock})&&*d.scene()==cases["locked"]&&d.undo_count()==1);CHECK(!d.execute({lock})&&d.undo_count()==1);
        CHECK(d.execute({unlock})&&*d.scene()==cases["unlocked"]);CHECK(d.undo()&&*d.scene()==cases["locked"]);CHECK(d.undo()&&*d.scene()==f.authored.scene);CHECK(d.redo()&&d.redo());
        auto request=d.begin("commit","R");CHECK(request);auto body=c::parse_command(request->body);CHECK(body["schema_version"]=="0.6.0"&&body["operations"][0]["scene"]==cases["unlocked"]);
    }else if(name=="GUARDS"){
        d.execute({lock});const auto before=*d.scene();const auto bytes=d.history_bytes();
        std::vector<ui::SceneEdit> edits={ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"changed"},ui::WidgetContentEdit{"widget:text",Json::array(),{{"body","changed"}}},ui::MoveWidgets{{"widget:text"},20,0},ui::ResizeWidget{"widget:text",200,80},ui::RemoveWidgets{{"widget:text"}},ui::DuplicateWidgets{{"widget:text"},{{"widget:text","widget:new"}}},ui::AlignWidgets{{"widget:text","widget:second"},ui::Alignment::top},ui::DistributeWidgets{{"widget:text","widget:second","widget:image"},ui::Spacing::horizontal},ui::GroupWidgets{{"widget:text","widget:second"},"widget:new","Group"},ui::WrapWidgets{{"widget:text"},"widget:new","Wrap",{{"base",{{"kind","stack"},{"axis","vertical"},{"gap_dip",8},{"overflow","diagnose"}}}}},ui::ReparentWidgets{{"widget:text"},std::nullopt,1},ui::RootDisplayEdit{"widget:text",{{"local_id","D2"}}}};
        for(const auto& e:edits){rejects([&]{d.execute({e});});CHECK(*d.scene()==before&&d.history_bytes()==bytes&&d.undo_count()==1);}
        CHECK(d.execute({unlock,ui::MoveWidgets{{"widget:text"},20,0}})&&*d.scene()==cases["moved"]);d.undo();CHECK(*d.scene()==before);
        auto w=f.authored.scene["widgets"][0];w["id"]="widget:new";CHECK(d.execute({ui::InsertWidget{w,{},0}}));CHECK(edit_locked(*d.scene(),"widget:text"));
    }else if(name=="INHERIT"){
        auto value=f.authored;value.scene=cases["grouped"];d.reload(value,"E1",resources);CHECK(edit_locked(*d.scene(),"widget:text")&&edit_protected(*d.scene(),"widget:group"));
        for(const auto& e:std::vector<ui::SceneEdit>{ui::UnwrapWidget{"widget:group"},ui::UngroupWidget{"widget:group"},ui::RemoveWidgets{{"widget:group"}},ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"changed"}})rejects([&]{d.execute({e});});
        d.execute({lock});d.execute({ui::SetWidgetLocks{{"widget:group"},false}});CHECK(edit_locked(*d.scene(),"widget:text")&&!edit_locked(*d.scene(),"widget:second")&&edit_protected(*d.scene(),"widget:group"));
        rejects([&]{d.execute({ui::MoveWidgets{{"widget:group"},20,0}});});auto w=f.authored.scene["widgets"][0];w["id"]="widget:new";CHECK(d.execute({ui::InsertWidget{w,"widget:group",1}}));
        d.execute({ui::SetWidgetLocks{{"widget:group"},true}});w["id"]="widget:new2";rejects([&]{d.execute({ui::InsertWidget{w,"widget:group",0}});});
        d.execute({ui::SetWidgetLocks{{"widget:group","widget:text"},false}});CHECK(!edit_protected(*d.scene(),"widget:group"));CHECK(d.execute({ui::MoveWidgets{{"widget:group"},1,0}}));
    }else if(name=="ATOMIC"){
        d.select({"widget:text"});d.execute({lock});d.undo();const auto before=*d.scene();const auto bytes=d.history_bytes();
        for(const auto& e:std::vector<ui::SetWidgetLocks>{{{},true},{{"widget:text","widget:text"},true},{{"widget:text","missing"},true}}){rejects([&]{d.execute({e});});CHECK(*d.scene()==before&&d.redo_count()==1&&d.history_bytes()==bytes);}
        rejects([&]{d.execute({lock,ui::MoveWidgets{{"widget:text"},1,0}});});CHECK(*d.scene()==before&&d.redo_count()==1);
        auto invalid=cases["grouped"]["widgets"][3];invalid["id"]="widget:invalid";invalid["children"]=Json::array({"missing"});invalid.erase("edit_locked");
        rejects([&]{d.execute({ui::InsertWidget{invalid,{},0},ui::WidgetPropertyEdit{"widget:invalid",ui::WidgetProperty::title,"changed"}});});CHECK(*d.scene()==before&&d.redo_count()==1);
        d.redo();rejects([&]{d.execute({unlock,ui::RemoveWidgets{{"missing"}}});});CHECK(*d.scene()==cases["locked"]&&d.selection()==std::vector<std::string>{"widget:text"});
    }else if(name=="POLICY"){
        auto denied=resources;denied.capabilities.erase("configuration.edit-locks");ui::EditorDraft old(authority(),policy(),f.authored,"E1",denied,true);CHECK(!old.locks_available());rejects([&]{old.execute({lock});});rejects([&]{old.execute({unlock});});
        ui::EditorDraft small(authority(),policy(),f.authored,"E1",resources);CHECK(!small.locks_available());rejects([&]{small.execute({lock});});
        d.execute({lock});d.begin("commit","R");CHECK(!d.locks_available());rejects([&]{d.execute({unlock});});d.disconnected();rejects([&]{d.undo();});
        auto e=make();auto next=policy();next.revision=8;next.denied_capabilities.insert("scene.replace");e.policy(next);CHECK(!e.locks_available());rejects([&]{e.execute({unlock});});next.revision=9;next.disclosure.clear();e.policy(next);CHECK(!e.available()&&e.history_bytes()==0);next=policy();next.revision=10;e.policy(next);CHECK(!e.available());
    }else if(name=="NEGOTIATE"){
        for(unsigned mode=0;mode<9;++mode){Store store(f);auto owner=std::make_shared<c::AsyncCommands>(store,"E1",store.provider(mode!=6&&mode!=8));c::Sessions sessions("E1",40,policy(),{},owner);sessions.open("C","p",authority(),0);
            Json h={{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","client"},{"max_frame_bytes",328704},{"document_versions",Json::array({{{"document","command"},{"version","0.6.0"}},{{"document","command-result"},{"version","0.1.0"}}})},{"required_features",Json::array({"configuration.transactions"})},{"optional_features",Json::array({"configuration.large-commands","configuration.content","configuration.scene-content","configuration.edit-locks"})}};
            if(mode>=1&&mode<=4)h["optional_features"].erase(mode-1);
            if(mode==5)h["max_frame_bytes"]=328703;
            if(mode==6)h["document_versions"].push_back({{"document","command"},{"version","0.5.0"}});
            if(mode==7){h["optional_features"].erase(0);h["required_features"].push_back("configuration.edit-locks");}
            sessions.receive("C",envelope("hello",h),0);if(mode==7||mode==8){CHECK(sessions.closed("C"));continue;}CHECK(!sessions.closed("C"));auto welcome=sessions.pop("C",0);CHECK(welcome);auto features=p::decode(*welcome).body["optional_features"];bool admitted=false;for(const auto& feature:features)if(feature=="configuration.edit-locks")admitted=true;CHECK(admitted==(mode==0));
            sessions.receive("C",envelope("command",q),0);CHECK(!sessions.closed("C"));if(mode==0){auto ticket=owner->take();CHECK(ticket&&owner->finish(owner->run(*ticket),0,true));CHECK(p::decode(*sessions.pop("C",0)).body["outcome"]=="accepted"&&store.writes==1);}else CHECK(p::decode(*sessions.pop("C",0)).body["error"]["code"]=="feature.unsupported"&&store.writes==0);
        }
    }else if(name=="DURABLE"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());auto bytes=q.dump();bytes.insert(bytes.size()-1,327680-bytes.size(),' ');const auto result=tx.submit("p","C",bytes,authority(),[]{return policy();},0);CHECK(result["outcome"]=="accepted"&&result["revision"]=="41"&&result["durable"]&&!result["visible"]&&store.writes==1);
        auto expected=cases["locked"];expected["revision"]="41";CHECK(store.current.documents.scene==expected);CHECK(tx.submit("p","C",bytes,authority(),[]{return policy();},1)==result&&store.writes==1);
        c::AsyncCommands restarted(store,"E2",store.provider());restarted.attach("E2",41,policy());Json lookup={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id","lock"}};auto recovered=restarted.reconcile("p",authority(),lookup,0);CHECK(recovered["result"]["outcome"]=="accepted"&&recovered["result"]["revision"]=="41"&&store.writes==1);
    }else throw std::runtime_error("unknown edit-lock test");
}
