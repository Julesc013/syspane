#include "editor_draft.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include "transaction.hpp"
#include <iostream>
#include <limits>
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace ui=syspane::interfaces;using c::Json;
void run_arrange(const std::string&,const std::string&);
void run_container(const std::string&,const std::string&);
void run_edit_lock(const std::string&,const std::string&);
void run_visibility_controls(const std::string&,const std::string&);
void run_visibility_admission(const std::string&,const std::string&);
void run_layout_authoring(const std::string&,const std::string&);
void run_widget_creation(const std::string&,const std::string&);
void run_binding_authoring(const std::string&,const std::string&);
void run_content_properties(const std::string&,const std::string&);
void run_snap(const std::string&,const std::string&);
void run_group(const std::string&,const std::string&);
void verify(bool ok,int line){if(!ok)throw std::runtime_error("editor assertion:"+std::to_string(line));}
#define CHECK(x) verify(static_cast<bool>(x),__LINE__)
template<class F> void rejects(F f){bool bad=false;try{f();}catch(const p::Error&){bad=true;}CHECK(bad);}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(std::uint64_t n=7){c::Policy p;p.available=true;p.revision=n;p.disclosure[{"desktop","inspector"}]={"operational"};p.disclosure[{"desktop","accessibility"}]={"operational"};return p;}
using Fixture=settings_fixture::Fixture;
ui::EditorDraft draft(const Fixture& f){return {authority(),policy(),f.authored,"E1",f.resources()};}
std::optional<std::string> parent(const Json& v){return v.is_null()?std::nullopt:std::optional<std::string>(v.get<std::string>());}
std::vector<ui::SceneEdit> operations(const Json& rows){
    std::vector<ui::SceneEdit> out;
    for(const auto& op:rows){const auto name=op["op"].get<std::string>();
        if(name=="property")out.push_back(ui::WidgetPropertyEdit{op["id"],op["property"]=="title"?ui::WidgetProperty::title:ui::WidgetProperty::display,op["value"]});
        else if(name=="content")out.push_back(ui::WidgetContentEdit{op["id"],op["bindings"],op["content"]});
        else if(name=="theme")out.push_back(ui::SceneThemeEdit{parent(op["theme"])});
        else if(name=="insert")out.push_back(ui::InsertWidget{op["widget"],parent(op["parent"]),op["index"]});
        else if(name=="remove")out.push_back(ui::RemoveWidgets{op["ids"].get<std::vector<std::string>>()});
        else if(name=="reparent")out.push_back(ui::ReparentWidgets{op["ids"].get<std::vector<std::string>>(),parent(op["parent"]),op["index"]});
        else if(name=="duplicate")out.push_back(ui::DuplicateWidgets{op["ids"].get<std::vector<std::string>>(),op["mapping"].get<std::map<std::string,std::string>>()});
        else if(name=="move")out.push_back(ui::MoveWidgets{op["ids"].get<std::vector<std::string>>(),op["dx"],op["dy"]});
        else if(name=="resize")out.push_back(ui::ResizeWidget{op["id"],op["width"],op["height"]});
        else throw std::runtime_error("unknown fixed operation");
    }return out;
}
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
ui::SceneEdit title(const std::string& value){return ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,value};}
void run(const std::string& name,const std::string& root){
    if(name.substr(0,8)=="ARRANGE-"){run_arrange(name.substr(8),root);return;}
    if(name.substr(0,5)=="SNAP-"){run_snap(name.substr(5),root);return;}
    if(name.substr(0,6)=="GROUP-"){run_group(name.substr(6),root);return;}
    if(name.substr(0,5)=="VCTL-"){run_visibility_controls(name.substr(5),root);return;}
    if(name.substr(0,4)=="VIS-"){run_visibility_admission(name.substr(4),root);return;}
    if(name.substr(0,5)=="LOCK-"){run_edit_lock(name.substr(5),root);return;}
    if(name.substr(0,10)=="CONTAINER-"){run_container(name.substr(10),root);return;}
    if(name.substr(0,7)=="LAYOUT-"){run_layout_authoring(name.substr(7),root);return;}
    if(name.substr(0,7)=="CREATE-"){run_widget_creation(name.substr(7),root);return;}
    if(name.substr(0,8)=="BINDING-"){run_binding_authoring(name.substr(8),root);return;}
    if(name.substr(0,8)=="CONTENT-"){run_content_properties(name.substr(8),root);return;}
    Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/cases.json");auto d=draft(f);
    if(name=="OPERATIONS"){
        for(const auto& row:cases["cases"]){auto e=draft(f);CHECK(e.execute(operations(row["operations"])));CHECK(*e.scene()==row["expected"]);CHECK(e.undo_count()==1&&e.revision()==40);
            CHECK(e.undo()&&*e.scene()==f.authored.scene);CHECK(e.redo()&&*e.scene()==row["expected"]);e.discard();CHECK(*e.scene()==f.authored.scene&&!e.dirty()&&e.undo_count()==0);}
        d.execute(operations(cases["cases"][9]["operations"]));
        d.execute({ui::ReparentWidgets{{"widget:text","widget:value"},std::nullopt,0},ui::RemoveWidgets{{"widget:newgroup"}}});CHECK(*d.scene()==f.authored.scene);
    }else if(name=="ATOMIC"){
        d.select({"widget:text"});CHECK(d.execute({title("first")}));const auto before=*d.scene();
        const std::vector<std::vector<ui::SceneEdit>> bad={
            {title("partial"),ui::RemoveWidgets{{"missing"}}},
            {ui::ReparentWidgets{{"widget:group"},std::string("widget:group"),0}},
            {ui::ReparentWidgets{{"widget:text"},std::string("widget:value"),0}},
            {ui::ReparentWidgets{{"widget:text"},std::nullopt,999}},
            {ui::RemoveWidgets{{"widget:text","widget:text"}}},
            {ui::DuplicateWidgets{{"widget:text"},{{"widget:text","widget:value"}}}},
            {ui::DuplicateWidgets{{"widget:text"},{}}},
            {ui::InsertWidget{f.authored.scene["widgets"][0],std::nullopt,0}},
            {ui::WidgetContentEdit{"widget:text",Json::array(),{{"body","bad\ttext"}}}},
            {ui::SceneThemeEdit{std::string("theme:missing")}},
            {ui::ResizeWidget{"widget:text",31,96}},
            {ui::MoveWidgets{{"widget:text"},std::numeric_limits<double>::infinity(),0}},
            {ui::MoveWidgets{{"widget:text"},100001,0}},
            {ui::WidgetPropertyEdit{"widget:text",static_cast<ui::WidgetProperty>(99),"bad"}}};
        for(const auto& edits:bad){rejects([&]{d.execute(edits);});CHECK(*d.scene()==before&&d.undo_count()==1&&d.redo_count()==0&&d.selection()==std::vector<std::string>{"widget:text"});}
        d.execute({ui::ReparentWidgets{{"widget:text"},std::string("widget:group"),0}});const auto grouped=*d.scene();
        rejects([&]{d.execute({ui::RemoveWidgets{{"widget:group","widget:text"}}});});CHECK(*d.scene()==grouped);
        auto layout=f.authored.scene["widgets"][0]["layout"];layout["breakpoints"]=Json::array({{{"min_width_dip",800},{"layout",layout["base"]}}});
        d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::layout,layout},ui::MoveWidgets{{"widget:text"},1,2}});
        CHECK((*d.scene())["widgets"][0]["layout"]["breakpoints"]==layout["breakpoints"]);
        const auto valid=*d.scene();rejects([&]{d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::layout,"invalid"},ui::MoveWidgets{{"widget:text"},1,0}});});CHECK(*d.scene()==valid);
    }else if(name=="SELECTION"){
        d.select({"widget:image","widget:text"});CHECK(d.selection()==std::vector<std::string>({"widget:text","widget:image"}));CHECK(!d.dirty());
        rejects([&]{d.select({"widget:text","widget:text"});});rejects([&]{d.select({"missing"});});CHECK(d.selection().size()==2);
        d.execute({ui::RemoveWidgets{{"widget:text"}}});CHECK(d.selection()==std::vector<std::string>{"widget:image"});d.undo();CHECK(d.selection()==std::vector<std::string>({"widget:text","widget:image"}));
        d.redo();d.discard();CHECK(d.selection()==std::vector<std::string>{"widget:image"});CHECK(*d.scene()==f.authored.scene);
        auto invalid=f.authored;invalid.scene["revision"]="99";rejects([&]{d.reload(invalid,"E2",f.resources());});CHECK(d.selection().size()==1);
    }else if(name=="HISTORY"){
        for(unsigned i=1;i<=70;++i)d.execute({title("title "+std::to_string(i))});
        CHECK(d.undo_count()==cases["history_entries"]);for(unsigned i=0;i<64;++i)CHECK(d.undo());CHECK(!d.undo()&&(*d.scene())["widgets"][0]["title"]=="title 6");
        CHECK(d.redo_count()==64);CHECK(!d.execute({title("title 6")}));CHECK(d.redo_count()==64);
        rejects([&]{d.execute({ui::RemoveWidgets{{"missing"}}});});CHECK(d.redo_count()==64);
        CHECK(d.redo());CHECK(d.execute({title("new branch")}));CHECK(d.redo_count()==0);d.discard();CHECK(*d.scene()==f.authored.scene&&d.history_bytes()==0);
    }else if(name=="TRANSACTION"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());auto edits=operations(cases["cases"][10]["operations"]);d.execute(edits);const auto expected=*d.scene();
        const auto q=*d.begin("preview","P");const auto body=p::parse(q.body);CHECK(body["schema_version"]=="0.4.0"&&body["content"]==f.document["selection"]&&body["operations"].size()==1);
        CHECK(body["operations"][0]==Json({{"op","scene.replace"},{"scene",expected}}));CHECK(c::prepare_authored(f.authored,body,authority(),policy()).scene==expected);
        rejects([&]{d.undo();});rejects([&]{d.select({});});rejects([&]{d.discard();});auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0);CHECK(result["outcome"]=="preview"&&store.writes==0);d.complete(q.ticket,result);CHECK(d.undo_count()==1);
        auto commit=*d.begin("commit","R");result=tx.submit("P","C",commit.body,authority(),[]{return policy();},1);CHECK(result["outcome"]=="accepted");d.complete(commit.ticket,result);
        auto accepted=expected;accepted["revision"]="41";auto settings=f.authored.settings;settings["revision"]="41";
        CHECK(store.current.documents.scene==accepted&&store.current.documents.settings==settings);CHECK(*d.scene()==accepted&&!d.dirty()&&d.undo_count()==0&&store.writes==1);
        CHECK(store.current.resources->selection()==f.document["selection"]);CHECK(!d.begin("commit","empty"));
        d.execute({title("after apply")});d.discard();CHECK(*d.scene()==accepted);CHECK(result["durable"]==true&&result["visible"]==false);
    }else if(name=="POLICY"){
        for(const auto* cap:{"scene.replace","content.select","settings.preview","scene.content"}){
            auto e=draft(f);e.execute({title("edit")});auto next=policy(8);next.denied_capabilities.insert(cap);e.policy(next);
            rejects([&]{e.undo();});CHECK(e.undo_count()==1&&(*e.scene())["widgets"][0]["title"]=="edit");rejects([&]{e.execute({title("denied")});});
        }
        d.execute({title("edit")});auto next=policy(8);next.denied_capabilities.insert("settings.commit");d.policy(next);CHECK(!d.may_submit("commit"));rejects([&]{d.begin("commit","R");});CHECK(d.undo());
        auto e=draft(f);e.select({"widget:text"});e.execute({title("secret draft")});d.close();std::weak_ptr<const c::ContentCatalog> weak=f.catalog;f.catalog.reset();CHECK(!weak.expired());
        next=policy(8);next.disclosure.clear();e.policy(next);CHECK(!e.scene()&&e.selection().empty()&&e.history_bytes()==0&&weak.expired());
        e.policy(policy(9));CHECK(!e.available());Fixture fresh(root);rejects([&]{e.reload(fresh.authored,"E2");});e.reload(fresh.authored,"E2",fresh.resources());CHECK(e.available()&&*e.scene()==fresh.authored.scene);
        e.policy(policy(9));CHECK(!e.available());
        Fixture pending_fixture(root);auto pending=draft(pending_fixture);Store store(pending_fixture);c::Transactions tx(store,"E1",store.provider());
        pending.execute({title("late")});const auto q=*pending.begin("commit","R");const auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0);
        next=policy(8);next.disclosure.clear();pending.policy(next);CHECK(pending.history_bytes()==0&&pending.active_request()->body.empty());
        pending.complete(q.ticket,result);CHECK(!pending.scene()&&pending.history_bytes()==0&&!pending.active_request());pending.policy(policy(9));CHECK(!pending.available());
    }else if(name=="RECONCILE"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());d.execute({title("committed")});auto q=*d.begin("commit","R");const auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0);
        CHECK(result["outcome"]=="accepted");d.disconnected();rejects([&]{d.execute({title("duplicate")});});CHECK(d.active_request()->body==q.body);
        c::Transactions restarted(store,"E2",store.provider());Json response={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id","R"},{"result",restarted.reconcile("P","E1","R",authority(),policy())}};
        CHECK(!d.complete(q.ticket+1,result));CHECK(d.reconciled(q.ticket,"Q","E2",response)&&d.revision()==41&&d.undo_count()==0&&store.writes==1);
        d.execute({title("next")});CHECK(d.begin("commit","S")->epoch=="E2");d.close();CHECK(!d.complete(q.ticket,result)&&!d.scene());
    }else if(name=="CONFLICT"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());d.execute({title("mine")});auto q=*d.begin("commit","R");auto other=p::parse(q.body);other["request_id"]="other";other["operations"][0]["scene"]["widgets"][0]["title"]="theirs";
        CHECK(tx.submit("P","C",other.dump(),authority(),[]{return policy();},0)["outcome"]=="accepted");auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},1);CHECK(result["outcome"]=="conflict");d.complete(q.ticket,result);
        CHECK(d.state()==ui::DraftState::conflict&&d.undo_count()==1);rejects([&]{d.undo();});rejects([&]{d.discard();});d.reload(store.current.documents,"E1",f.resources());CHECK(!d.dirty()&&d.undo_count()==0&&(*d.scene())["widgets"][0]["title"]=="theirs");
    }else if(name=="CANCEL"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());d.execute({title("maybe")});auto q=*d.begin("commit","R");CHECK(d.cancel_request()->ticket==q.ticket&&!d.cancel_request());
        CHECK(d.state()==ui::DraftState::pending);rejects([&]{d.discard();});auto result=tx.submit("P","C",q.body,authority(),[]{return policy();},0);auto malformed=result;malformed["request_id"]="wrong";
        rejects([&]{d.complete(q.ticket,malformed);});CHECK(d.state()==ui::DraftState::unknown&&d.active_request()->ticket==q.ticket);d.complete(q.ticket,result);CHECK(d.revision()==41&&store.writes==1);
        d.execute({title("not saved")});d.discard();CHECK((*d.scene())["widgets"][0]["title"]=="maybe"&&store.writes==1);
    }else if(name=="BOUNDS"){
        rejects([&]{d.execute({});});std::vector<ui::SceneEdit> too_many(129,title("bad"));rejects([&]{d.execute(too_many);});CHECK(!d.dirty());
        std::vector<ui::SceneEdit> insert;
        for(unsigned i=0;i<120;++i){auto w=f.authored.scene["widgets"][0];w["id"]="widget:large"+std::to_string(i);w["content"]["body"]=std::string(900,'x');insert.push_back(ui::InsertWidget{w,std::nullopt,0});}
        CHECK(d.execute(insert));const auto before=*d.scene();CHECK(before.dump().size()>16384&&!d.may_submit("commit"));rejects([&]{d.begin("commit","large");});CHECK(!d.active_request()&&*d.scene()==before&&d.undo_count()==1);
        for(unsigned i=0;i<40;++i)d.execute({title("large "+std::to_string(i))});
        CHECK(d.history_bytes()<=cases["history_bytes"]&&d.undo_count()<41&&d.undo_count()>0);d.discard();CHECK(*d.scene()==f.authored.scene&&d.history_bytes()==0);
    }else if(name=="COMPAT"){
        auto old=f.authored;old.scene=settings_fixture::read(root+"/spec/fixtures/valid/scene-portable.json");old.scene["revision"]="40";
        ui::EditorDraft bare(authority(),policy(),old,"E1");const auto id=old.scene["widgets"][0]["id"].get<std::string>();bare.execute({ui::WidgetPropertyEdit{id,ui::WidgetProperty::title,"old edit"}});CHECK(p::parse(bare.begin("preview","P")->body)["schema_version"]=="0.2.0");
        ui::EditorDraft resources(authority(),policy(),old,"E1",f.resources());resources.execute({ui::WidgetPropertyEdit{id,ui::WidgetProperty::title,"old edit"}});CHECK(p::parse(resources.begin("preview","P")->body)["schema_version"]=="0.3.0");
    }else throw std::runtime_error("unknown editor case");
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" passed\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
