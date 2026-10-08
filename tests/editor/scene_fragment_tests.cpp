#include "theme_history_fixture.hpp"
#include <iostream>
namespace {
using namespace theme_history_fixture;
void check(bool ok,int line){if(!ok)throw std::runtime_error("fragment assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool rejected=false;try{f();}catch(const syspane::protocol::Error&){rejected=true;}CHECK(rejected);}
c::Policy grant(std::uint64_t generation=7){auto p=policy(generation);p.disclosure[{"desktop","clipboard"}]={"sensitive"};return p;}
ui::SettingsResources admitted(const settings_fixture::Fixture& f){auto out=context(f);out.capabilities.insert("editor.clipboard");return out;}
ui::PasteWidgets paste(const Json& cases,bool nested=false){return {cases.at("fragment").dump(),cases.at("mapping").get<std::map<std::string,std::string>>(),nested?std::optional<std::string>("widget:group"):std::nullopt,nested?0U:2U};}
void unchanged(ui::EditorDraft& d,const Json& cases,const std::vector<ui::SceneEdit>& edits){
    const auto before=*d.scene();const auto selected=d.selection();const auto resources=d.resources();const auto history=d.history_bytes(),undo=d.undo_count(),redo=d.redo_count();
    rejects([&]{d.execute(edits);});CHECK(*d.scene()==before&&d.selection()==selected&&d.resources()==resources&&d.undo_count()==undo&&d.redo_count()==redo&&d.history_bytes()==history&&d.revision()==40);
    (void)cases;
}
Json node(Json& scene,const std::string& id){for(auto& w:scene["widgets"])if(w["id"]==id)return w;throw std::runtime_error("fixture node");}
void run(const std::string& family,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/scene-fragment-cases.json");f.authored={cases["destination"]["settings"],cases["destination"]["scene"]};
    auto original=f.authored;auto source=original;source.scene=cases.at("source");
    ui::EditorDraft d(authority(),grant(),original,"E1",admitted(f),true);
    if(family=="COPY"){
        ui::EditorDraft from(authority(),grant(),source,"E1",admitted(f),true);from.select(cases["selection"].get<std::vector<std::string>>());from.copy_selection();
        CHECK(from.clipboard_data()==cases["fragment"].dump()&&from.undo_count()==0&&!from.dirty()&&*from.scene()==source.scene);
        from.select({});rejects([&]{from.copy_selection();});CHECK(from.clipboard_data()==cases["fragment"].dump());
        std::vector<std::string> ids;for(const auto& w:source.scene["widgets"])ids.push_back(w["id"]);from.select(ids);from.copy_selection();CHECK(from.clipboard_data()==cases["all_fragment"].dump());
        from.select({"widget:text"});from.copy_selection();CHECK(from.clipboard_data()==cases["child_fragment"].dump());
        auto leak=cases["child_fragment"];leak["revision"]="40";CHECK(Json::parse(from.clipboard_data())!=leak);
        from.select({"widget:image"});CHECK(from.clipboard_data()==cases["child_fragment"].dump());from.execute({ui::WidgetPropertyEdit{"widget:image",ui::WidgetProperty::title,"New title"}});CHECK(from.clipboard_data()==cases["child_fragment"].dump());
    }else if(family=="PASTE"){
        d.select({"widget:text"});const auto resource=d.resources();CHECK(d.execute({paste(cases)}));CHECK(*d.scene()==cases["pasted"]&&d.selection()==cases["selected_after"].get<std::vector<std::string>>()&&d.undo_count()==1&&d.resources()->selection()==resource->selection());
        auto wrong=cases["pasted"];wrong["widgets"].back()["id"]="wrong:image";CHECK(*d.scene()!=wrong);
        CHECK(d.undo()&&*d.scene()==original.scene&&d.selection()==std::vector<std::string>{"widget:text"});CHECK(d.redo()&&*d.scene()==cases["pasted"]);
        d.discard();CHECK(d.execute({paste(cases,true)})&&*d.scene()==cases["nested"]);
        d.discard();auto all=paste(cases);all.bytes=cases["all_fragment"].dump();all.mapping.clear();for(const auto& w:cases["all_fragment"]["widgets"])all.mapping.emplace(w["id"],"all:"+w["id"].get<std::string>());
        CHECK(d.execute({all})&&d.scene()->at("widgets").size()==14);const auto& rows=d.scene()->at("widgets");
        for(std::size_t i=0;i<7;++i){auto expected=cases["all_fragment"]["widgets"][i];expected["id"]=all.mapping.at(expected["id"].get<std::string>());if(expected.contains("children"))for(auto& child:expected["children"])child=all.mapping.at(child.get<std::string>());CHECK(rows[i+7]==expected);}
    }else if(family=="INVALID"){
        const auto good=paste(cases);for(int n=0;n<8;++n){auto bad=good;
            if(n==0)bad.mapping.erase("widget:text");
            if(n==1)bad.mapping.emplace("extra","extra:new");
            if(n==2)bad.mapping["widget:text"]="widget:text";
            if(n==3)bad.mapping["widget:text"]="pasted:group";
            if(n==4)bad.mapping["widget:text"]="bad id";
            if(n==5)bad.parent="missing";
            if(n==6)bad.parent="widget:text";
            if(n==7)bad.index=100;
            unchanged(d,cases,{bad});
        }
        for(int n=0;n<10;++n){auto fragment=cases["fragment"];auto bad=good;
            if(n==0)fragment["format"]="other";
            if(n==1)fragment["schema_version"]="0.2.0";
            if(n==2)fragment["scene_version"]="0.2.0";
            if(n==3)fragment["telemetry"]=Json::object();
            if(n==4)fragment["roots"].push_back("widget:text");
            if(n==5)fragment["widgets"][1]["children"]={"widget:group"};
            if(n==6)fragment["widgets"][2]["content"]["asset"]["sha256"]=std::string(64,'0');
            if(n==7)fragment["widgets"][0]["content"]["body"]=12;
            if(n==8)fragment["widgets"]=Json::array();
            if(n==9)fragment["widgets"][0]["unknown"]=true;
            bad.bytes=fragment.dump();unchanged(d,cases,{bad});
        }
        for(const std::string& bytes:{std::string("{}"),std::string("\xef\xbb\xbf")+good.bytes,good.bytes.substr(0,good.bytes.size()-1)+",\"format\":\"syspane.scene-fragment\"}",std::string("\xff"),std::string("null")}){auto bad=good;bad.bytes=bytes;unchanged(d,cases,{bad});}
        auto bad=good;bad.mapping["widget:text"]="widget:text";unchanged(d,cases,{ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"must roll back"},bad});
        auto whitespace=good;whitespace.bytes+="\n \t\r";CHECK(d.execute({whitespace})&&*d.scene()==cases["pasted"]);
    }else if(family=="BOUNDS"){
        auto bad=paste(cases);bad.bytes=std::string(262145,' ');unchanged(d,cases,{bad});
        auto large=cases["child_fragment"];large["widgets"]=Json::array();large["roots"]=Json::array();auto many=paste(cases);many.mapping.clear();
        for(unsigned i=0;i<129;++i){auto w=cases["child_fragment"]["widgets"][0];w["id"]="source:"+std::to_string(i);large["widgets"].push_back(w);large["roots"].push_back(w["id"]);many.mapping.emplace(w["id"],"many:"+std::to_string(i));}
        many.bytes=large.dump();CHECK(d.execute({many})&&d.scene()->at("widgets").size()==136&&d.undo_count()==1&&d.selection().size()==129);CHECK(d.undo());
        for(unsigned i=129;i<256;++i){auto w=large["widgets"][0];w["id"]="source:"+std::to_string(i);large["widgets"].push_back(w);large["roots"].push_back(w["id"]);many.mapping.emplace(w["id"],"many:"+std::to_string(i));}many.bytes=large.dump();unchanged(d,cases,{many});
        auto deep=cases["fragment"];deep["widgets"]=Json::array();deep["roots"]={"g:0"};many.mapping.clear();
        for(unsigned i=0;i<17;++i){auto w=node(source.scene,"widget:group");w["id"]="g:"+std::to_string(i);w["children"]=i<16?Json::array({"g:"+std::to_string(i+1)}):Json::array();deep["widgets"].push_back(w);many.mapping.emplace(w["id"],"fresh:"+std::to_string(i));}many.bytes=deep.dump();unchanged(d,cases,{many});
        deep["widgets"].erase(deep["widgets"].end()-1);deep["widgets"].back()["children"]=Json::array();many.mapping.erase("g:16");many.bytes=deep.dump();many.parent="widget:group";many.index=0;unchanged(d,cases,{many});
        many.parent=std::nullopt;CHECK(d.execute({many})&&d.undo());
        auto crowded=original;crowded.scene["widgets"]=Json::array();crowded.scene["roots"]=Json::array();
        for(unsigned i=0;i<140;++i){auto w=cases["child_fragment"]["widgets"][0];w["id"]="large:"+std::to_string(i);w["content"]["body"]=std::string(1024,'x');crowded.scene["widgets"].push_back(w);crowded.scene["roots"].push_back(w["id"]);}
        ui::EditorDraft bytes(authority(),grant(),crowded,"E1",admitted(f),true);auto piece=cases["child_fragment"];piece["widgets"]=Json::array();piece["roots"]=Json::array();many.mapping.clear();
        for(unsigned i=0;i<90;++i){auto w=crowded.scene["widgets"][i];piece["widgets"].push_back(w);piece["roots"].push_back(w["id"]);many.mapping.emplace(w["id"],"more:"+std::to_string(i));}many.bytes=piece.dump();unchanged(bytes,cases,{many});
        auto nested=Json::object();Json* cursor=&nested;for(unsigned i=0;i<34;++i){(*cursor)["x"]=Json::object();cursor=&(*cursor)["x"];}auto payload=cases["fragment"];payload["widgets"][0]["extensions"]=nested;bad=paste(cases);bad.bytes=payload.dump();unchanged(d,cases,{bad});
        for(unsigned i=0;i<70;++i)d.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"history "+std::to_string(i)}});
        CHECK(d.undo_count()==64&&d.history_bytes()<=8388608);
    }else if(family=="VERSIONS"){
        CHECK(d.execute({paste(cases)}));unchanged(d,cases,{ui::WidgetPropertyEdit{"pasted:text",ui::WidgetProperty::title,"locked"}});auto locked=paste(cases,true);locked.parent="pasted:group";unchanged(d,cases,{locked});
        d.discard();auto source4=cases["fragment"];source4["scene_version"]="0.4.0";source4["widgets"][1].erase("visibility");auto four=paste(cases);four.bytes=source4.dump();CHECK(d.execute({four})&&d.scene()->at("schema_version")=="0.4.0");
        auto fresh=cases["child_fragment"];fresh["scene_version"]="0.3.0";ui::PasteWidgets three{fresh.dump(),{{"widget:text","third:text"}},std::nullopt,0};CHECK(d.execute({three})&&d.scene()->at("schema_version")=="0.4.0");
        for(const char* cap:{"configuration.visibility","scene.visibility","configuration.edit-locks","scene.edit-locks"}){auto ctx=admitted(f);ctx.capabilities.erase(cap);ui::EditorDraft missing(authority(),grant(),original,"E1",ctx,true);unchanged(missing,cases,{paste(cases)});}
        ui::EditorDraft small(authority(),grant(),original,"E1",admitted(f),false);unchanged(small,cases,{paste(cases)});
    }else if(family=="POLICY"){
        CHECK(d.clipboard_available());auto ctx=admitted(f);ctx.capabilities.erase("editor.clipboard");ui::EditorDraft absent(authority(),grant(),original,"E1",ctx,true);CHECK(!absent.clipboard_available());unchanged(absent,cases,{paste(cases)});
        for(int n=0;n<7;++n){auto p=grant();auto a=authority();
            if(n==0)p.disclosure[{"desktop","clipboard"}]={"operational"};
            if(n==1)p.denied_capabilities.insert("editor.clipboard");
            if(n==2)p.denied_capabilities.insert("projection.clipboard");
            if(n==3)p.denied_capabilities.insert("content.select");
            if(n==4)a.authenticated=false;
            if(n==5)a.role_grants.clear();
            if(n==6){a.role="diagnostic";a.role_grants={"diagnostic"};p.disclosure[{"diagnostic","inspector"}]={"operational"};p.disclosure[{"diagnostic","accessibility"}]={"operational"};p.disclosure[{"diagnostic","clipboard"}]={"sensitive"};}
            ui::EditorDraft denied(a,p,original,"E1",admitted(f),true);CHECK(!denied.clipboard_available());rejects([&]{denied.copy_selection();});rejects([&]{denied.clipboard_data();});rejects([&]{denied.execute({paste(cases)});});
        }
        auto a=authority();a.role="console";a.role_grants={"console"};auto p=grant();for(const char* channel:{"inspector","accessibility"})p.disclosure[{"console",channel}]={"operational"};p.disclosure[{"console","clipboard"}]={"sensitive"};ui::EditorDraft console(a,p,original,"E1",admitted(f),true);CHECK(console.clipboard_available());
    }else if(family=="LIFETIME"){
        for(int n=0;n<7;++n){ui::EditorDraft owned(authority(),grant(),original,"E1",admitted(f),true);owned.select({"widget:text"});owned.copy_selection();CHECK(!owned.clipboard_data().empty());
            if(n==0)owned.clear_clipboard();
            if(n==1)owned.policy(grant(8));
            if(n==2)owned.disconnected();
            if(n==3)owned.reload(original,"E2",admitted(f));
            if(n==4)owned.discard();
            if(n==5)owned.close();
            if(n==6){owned.execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"changed"}});CHECK(owned.begin("commit","pending"));CHECK(!owned.clipboard_available());}
            rejects([&]{owned.clipboard_data();});
        }
        d.select({"widget:text"});d.copy_selection();auto p=grant(8);p.disclosure[{"desktop","clipboard"}]={};d.policy(p);CHECK(!d.clipboard_available());rejects([&]{d.clipboard_data();});d.policy(grant(9));CHECK(d.clipboard_available());rejects([&]{d.clipboard_data();});
        d.copy_selection();d.policy(grant(9));CHECK(!d.available());d.policy(grant(10));d.reload(original,"E2",admitted(f));rejects([&]{d.clipboard_data();});
    }else if(family=="TRANSACTION"){
        CHECK(d.execute({paste(cases)}));Store store(f);c::Transactions tx(store,"E1",store.provider());auto q=*d.begin("commit","paste");CHECK(!d.clipboard_available());
        const auto body=c::parse_command(q.body);CHECK(body["schema_version"]=="0.7.0"&&body["operations"][0]["scene"]==cases["pasted"]);
        const auto result=tx.submit("p","C",q.body,authority(),[]{return grant();},0);CHECK(result["outcome"]=="accepted"&&store.writes==1);d.disconnected();CHECK(d.state()==ui::DraftState::unknown);
        c::Transactions restarted(store,"E2",store.provider());const auto recovered=restarted.reconcile("p","E1","paste",authority(),grant());
        const Json response={{"schema_version","0.1.0"},{"query_id","query"},{"original_producer_epoch","E1"},{"request_id","paste"},{"result",recovered}};CHECK(d.reconciled(q.ticket,"query","E2",response)&&d.revision()==41&&store.writes==1&&d.undo_count()==0);
        auto expected=cases["pasted"];expected["revision"]="41";CHECK(*d.scene()==expected&&store.current.documents.scene==expected);
        ui::EditorDraft reopened(authority(),grant(),store.current.documents,"E2",admitted(f),true);CHECK(*reopened.scene()==expected);rejects([&]{reopened.clipboard_data();});
    }else throw std::runtime_error("unknown fragment family");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
