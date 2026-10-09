#include "theme_history_fixture.hpp"
#include "theme_resources.hpp"
#include "digest.hpp"
#include <iostream>
namespace {
using namespace theme_history_fixture;namespace p=syspane::protocol;
void check(bool b,int line){if(!b)throw std::runtime_error("theme history assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool caught=false;try{f();}catch(const p::Error&){caught=true;}CHECK(caught);}
ui::SceneEdit title(const std::string& text){return ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,text};}
c::ContentPackage pack(const std::string& id,const std::string& kind,const Json& document,Json dependencies=Json::array()){
    const auto bytes=document.dump()+"\n";Json manifest={{"schema_version","0.1.0"},{"package_id",id},{"version","0.1.0"},{"kind",kind},{"license","MIT"},{"dependencies",dependencies},
        {"assets",Json::array({{{"path",kind+".json"},{"media_type","application/json"},{"sha256",c::sha256(bytes)},{"bytes",bytes.size()}}})},
        {"total_unpacked_bytes",bytes.size()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    try{c::validate_content_document(document,kind);(void)c::validate_content_manifest(manifest.dump());}
    catch(const p::Error& e){std::cerr<<"fixture package "<<id<<" manifest: "<<manifest.dump()<<'\n';if(kind=="preset")std::cerr<<"preset: "<<document.dump()<<'\n';throw std::runtime_error(std::string("fixture: ")+e.what());}
    return {manifest.dump()+"\n",{{kind+".json",bytes}}};
}
Json pin(const c::ContentPackage& package,bool document=false){
    const auto m=Json::parse(package.manifest);const auto kind=m["kind"].get<std::string>();const auto& bytes=package.assets.at(kind+".json");
    Json id=m.at("package_id");if(document){const auto parsed=Json::parse(bytes);id=parsed.at(kind+"_id");}
    return {{"id",std::move(id)},{"version","0.1.0"},{"sha256",c::sha256(document?bytes:package.manifest)}};
}
void matching(const ui::EditorDraft& d,const Json& cases,const std::string& key){CHECK(*d.scene()==cases["scenes"][key]);CHECK(d.resources()->theme()==cases["artifacts"][key]["theme"]&&d.resources()->selection()==cases["selections"][key]);}
void run(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/theme-history-cases.json");const auto first=cases["artifacts"]["first"],second=cases["artifacts"]["second"];
    auto resources=context(f);ui::EditorDraft d(authority(),policy(),f.authored,"E1",resources,true);
    if(name=="SNAPSHOT"){
        auto base=d.resource_snapshot();CHECK(base&&base.get()==d.resources());
        CHECK(fonts(d,first));auto one=d.resource_snapshot();CHECK(one.get()==d.resources()&&one!=base&&one->theme()==first["theme"]);
        CHECK(fonts(d,second));auto two=d.resource_snapshot();CHECK(two.get()==d.resources()&&two!=one&&two->theme()==second["theme"]);
        CHECK(one->theme()==first["theme"]&&base->theme()!=one->theme());
        CHECK(d.undo()&&d.resource_snapshot()==one);CHECK(d.redo()&&d.resource_snapshot()==two);
        auto value=f.authored;value.scene=*d.scene();c::validate_resource_binding(*two,value);
        d.discard();CHECK(d.resource_snapshot()==base);d.reload(f.authored,"E2",resources);
        CHECK(d.resource_snapshot().get()==d.resources()&&d.resource_snapshot()->theme()==base->theme());
        auto denied=policy(8);denied.disclosure.clear();d.policy(denied);CHECK(!d.resource_snapshot());
        CHECK(one->theme()==first["theme"]&&two->theme()==second["theme"]);d.close();CHECK(!d.resource_snapshot());
        std::weak_ptr<const c::ResourceSet> witness=two;two.reset();CHECK(witness.expired());
    }else if(name=="SHARING"){
        const auto base=d.resources()->base_packages();CHECK(d.theme_fonts_available());CHECK(fonts(d,first));
        for(const auto& b:base){bool found=false;for(const auto& a:d.resources()->base_packages())if(a.get()==b.get())found=true;CHECK(found);}
        const auto current=d.resources();auto catalog=c::ContentCatalog::retained(*current);auto authored=f.authored;authored.scene=*d.scene();auto snapshot=catalog.theme_resources(current->selection(),authored);
        CHECK(snapshot->packages()==current->packages());std::weak_ptr<const c::ContentPackage> override;
        for(const auto& p:current->packages())if(p->manifest==first["manifest"])override=p;
        CHECK(!override.expired());d.close();CHECK(!override.expired());snapshot.reset();catalog=c::ContentCatalog::retained(*f.catalog->resources(f.document["selection"],f.authored));CHECK(override.expired());
        c::ContentPackage addition{first["manifest"],{{"theme.json",first["asset"]}}};auto initial=f.catalog->resources(f.document["selection"],f.authored);auto retained=c::ContentCatalog::retained(*initial,true,addition);addition.assets["theme.json"]="changed caller";
        authored.scene=cases["scenes"]["first"];CHECK(retained.theme_resources(cases["selections"]["first"],authored)->theme()==first["theme"]);
    }else if(name=="HISTORY"){
        d.select({"widget:text"});CHECK(fonts(d,first));matching(d,cases,"first");CHECK(d.undo_count()==1);CHECK(fonts(d,second));matching(d,cases,"second");
        CHECK(d.undo());matching(d,cases,"first");const auto bytes=d.history_bytes();CHECK(!fonts(d,first)&&d.redo_count()==1&&d.history_bytes()==bytes);CHECK(d.redo());matching(d,cases,"second");
        CHECK(d.execute({title("geometry and fonts")}));CHECK(d.resources()->theme()==second["theme"]);CHECK(d.undo());matching(d,cases,"second");
        const auto before=*d.scene();auto invalid=second["theme"]["font"];invalid["size_dip"]=-1;rejects([&]{d.set_theme_fonts(invalid,Json());});CHECK(*d.scene()==before&&d.redo_count()==1);
        CHECK(d.execute({ui::SceneThemeEdit{std::nullopt}}));CHECK(*d.scene()==f.authored.scene&&!d.dirty()&&d.resources()->selection()==f.document["selection"]);CHECK(d.redo_count()==0);
        CHECK(d.undo());matching(d,cases,"second");d.discard();CHECK(*d.scene()==f.authored.scene&&!d.dirty()&&d.history_bytes()==0&&d.resources()->selection()==f.document["selection"]);
        CHECK(fonts(d,first));CHECK(d.set_theme_fonts(first["theme"]["font"],Json()));CHECK(!d.resources()->theme().contains("font_roles"));CHECK(d.set_theme_fonts(first["theme"]["font"],Json::object()));CHECK(d.resources()->theme()["font_roles"].empty()&&d.resources()->theme().contains("font_roles"));CHECK(d.undo());CHECK(!d.resources()->theme().contains("font_roles"));
        d.discard();d.execute({ui::SceneThemeEdit{std::string("theme:contrast")}});const auto changed=*d.scene();const auto pin=d.resources()->theme_pin();const auto history=d.history_bytes();rejects([&]{fonts(d,first);});CHECK(*d.scene()==changed&&d.resources()->theme_pin()==pin&&d.history_bytes()==history);
    }else if(name=="COMMANDS"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());CHECK(fonts(d,first)&&fonts(d,second));
        auto q=*d.begin("preview","history:preview");auto expected=cases["commands"]["second"];expected["intent"]="preview";expected["request_id"]="history:preview";CHECK(c::parse_command(q.body)==expected);auto result=tx.submit("p","C",q.body,authority(),[]{return policy();},0);CHECK(result["outcome"]=="preview"&&d.complete(q.ticket,result)&&d.undo_count()==2&&store.writes==0);
        q=*d.begin("commit","history:second");CHECK(c::parse_command(q.body)==cases["commands"]["second"]);result=tx.submit("p","C",q.body,authority(),[]{return policy();},1);CHECK(result["outcome"]=="accepted"&&d.complete(q.ticket,result)&&!d.dirty()&&d.undo_count()==0&&store.writes==1);
        auto wanted=cases["scenes"]["second"];wanted["revision"]="41";CHECK(*d.scene()==wanted&&store.current.resources->theme()==second["theme"]);
        d.execute({title("after save")});q=*d.begin("commit","retained");CHECK(c::parse_command(q.body)["theme_edit"].is_null());result=tx.submit("p","C",q.body,authority(),[]{return policy();},2);CHECK(result["outcome"]=="accepted"&&d.complete(q.ticket,result));
        d.execute({ui::SceneThemeEdit{std::string("theme:native")}});q=*d.begin("commit","reset");const auto body=c::parse_command(q.body);CHECK(body["schema_version"]=="0.8.0"&&body["theme_edit"].is_null()&&body["content"]==cases["base_selection"]);result=tx.submit("p","C",q.body,authority(),[]{return policy();},3);CHECK(result["outcome"]=="accepted"&&d.complete(q.ticket,result)&&d.revision()==43);
        d.reload(store.current.documents,"E2",context(*store.current.resources));CHECK(d.resources()->selection()==cases["base_selection"]&&!d.dirty());
        ui::SettingsDraft settings(authority(),policy(),store.current.documents,"E2",context(*store.current.resources),true);settings.set("display.reduced_motion",false);const auto setting_request=settings.begin("commit","settings");CHECK(setting_request&&c::parse_command(setting_request->body)["schema_version"]=="0.8.0");
    }else if(name=="RESULTS"){
        Store store(f);c::Transactions tx(store,"E1",store.provider());fonts(d,first);auto q=*d.begin("commit","history:first");CHECK(d.cancel_request()&&!d.cancel_request());d.disconnected();CHECK(d.state()==ui::DraftState::unknown&&d.active_request()->body==q.body);
        rejects([&]{fonts(d,second);});rejects([&]{d.undo();});rejects([&]{d.discard();});
        const auto result=tx.submit("p","C",q.body,authority(),[]{return policy();},0);CHECK(result["outcome"]=="accepted");c::Transactions next(store,"E2",store.provider());const auto reconciled=next.reconcile("p","E1",q.request,authority(),policy());
        Json response={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id",q.request},{"result",reconciled}};CHECK(d.reconciled(q.ticket,"Q","E2",response)&&d.revision()==41&&d.undo_count()==0&&store.writes==1);CHECK(!d.complete(q.ticket,result));
        fonts(d,second);q=*d.begin("commit","conflicting");auto other=c::parse_command(q.body);other["request_id"]="other";CHECK(next.submit("p","C",other.dump(),authority(),[]{return policy();},1)["outcome"]=="accepted");const auto conflict=next.submit("p","C",q.body,authority(),[]{return policy();},2);CHECK(d.complete(q.ticket,conflict)&&d.state()==ui::DraftState::conflict&&d.undo_count()==1);rejects([&]{d.undo();});d.reload(store.current.documents,"E2",context(*store.current.resources));CHECK(!d.dirty()&&d.resources()->theme()==second["theme"]);
    }else if(name=="POLICY"){
        for(const auto& cap:capabilities()){auto missing=resources;missing.capabilities.erase(cap);ui::EditorDraft unsupported(authority(),policy(),f.authored,"E1",missing,true);CHECK(!unsupported.theme_fonts_available());rejects([&]{fonts(unsupported,first);});CHECK(!unsupported.dirty());}
        ui::EditorDraft small(authority(),policy(),f.authored,"E1",resources);CHECK(!small.theme_fonts_available());
        fonts(d,first);d.undo();auto denied=policy(8);denied.denied_capabilities.insert("theme.edit");d.policy(denied);const auto before=*d.scene();rejects([&]{d.redo();});CHECK(*d.scene()==before&&d.redo_count()==1);
        d.policy(policy(9));CHECK(d.redo());std::weak_ptr<const c::ContentPackage> external;for(const auto& p:d.resources()->packages())if(p->manifest==first["manifest"])external=p;CHECK(!external.expired());auto q=*d.begin("commit","private");denied=policy(10);denied.denied_capabilities.insert("theme.typography");d.policy(denied);CHECK(!d.available()&&!d.resources()&&d.history_bytes()==0&&external.expired()&&d.active_request()->body.empty());d.policy(policy(11));CHECK(!d.available());
        Store store(f);c::Transactions tx(store,"E1",store.provider());const auto result=tx.submit("p","C",q.body,authority(),[]{return policy(9);},0);CHECK(result["outcome"]=="accepted");CHECK(d.complete(q.ticket,result)&&!d.resources());d.reload(store.current.documents,"E1",context(*store.current.resources));CHECK(d.resources()&&d.resources()->theme()==first["theme"]);
        auto legacy=f.resources();rejects([&]{d.reload(store.current.documents,"E1",ui::SettingsResources{context(*store.current.resources).catalog,store.current.resources->selection(),legacy.capabilities});});CHECK(d.resources()->theme()==first["theme"]);
    }else if(name=="COUNT-LIMIT"){
        const auto base=d.resources()->base_packages();for(unsigned n=0;n<75;++n){auto font=first["theme"]["font"];font["size_dip"]=10.0+n*.125;CHECK(d.set_theme_fonts(font,Json()));CHECK(d.history_bytes()<=8388608&&d.undo_count()<=64);for(std::size_t i=0;i<base.size();++i)CHECK(d.resources()->base_packages()[i]==base[i]);}CHECK(d.undo_count()==64);
    }else if(name=="SCENE-LIMIT"){
        std::vector<ui::SceneEdit> additions;for(unsigned n=0;n<120;++n){auto w=f.authored.scene["widgets"][0];w["id"]="widget:large"+std::to_string(n);w["content"]["body"]=std::string(900,'x');additions.push_back(ui::InsertWidget{w,std::nullopt,0});}d.execute(additions);
        fonts(d,first);const auto retained=d.resources();for(unsigned n=0;n<45;++n){d.execute({title("retained theme "+std::to_string(n))});CHECK(d.resources()==retained&&d.history_bytes()<=8388608);}CHECK(d.undo_count()<45&&d.undo_count()>0);d.discard();CHECK(!d.dirty()&&d.resources()->selection()==f.document["selection"]);
    }else if(name=="RESOURCE-LIMIT"){
        auto source=f.catalog->resources(f.document["selection"],f.authored);auto theme=source->theme();theme["theme_id"]="theme:large";theme["extensions"]["author.padding"]=std::string(200000,'x');auto big=pack("package:large-theme","theme",theme);
        Json preset;std::vector<c::ContentPackage> packages;for(const auto& p:source->packages()){packages.push_back(*p);if(c::sha256(p->manifest)==f.document["selection"]["package"]["sha256"])preset=Json::parse(p->assets.at("preset.json"));}
        preset["preset_id"]="preset:large";preset["parent"]=f.document["selection"]["preset"];preset["theme"]=pin(big,true);preset["settings"]=Json::array();auto leaf=pack("package:large-preset","preset",preset,Json::array({f.document["selection"]["package"],pin(big)}));packages.push_back(big);packages.push_back(leaf);
        auto catalog=std::make_shared<const c::ContentCatalog>(std::move(packages));auto authored=f.authored;authored.scene["theme_id"]="theme:large";
        ui::EditorDraft retained(authority(),policy(),authored,"E1",ui::SettingsResources{catalog,{{"package",pin(leaf)},{"preset",pin(leaf,true)}},capabilities()},true);
        std::weak_ptr<const c::ContentPackage> first_large;
        for(unsigned n=0;n<35;++n){auto font=first["theme"]["font"];font["size_dip"]=11.0+n*.125;retained.set_theme_fonts(font,Json());if(n==0)for(const auto& p:retained.resources()->packages())if(Json::parse(p->manifest)["package_id"].get<std::string>().find("package:authored-theme:")==0)first_large=p;CHECK(retained.history_bytes()<=8388608);}
        CHECK(retained.undo_count()<30&&retained.undo_count()>0&&first_large.expired());retained.discard();CHECK(*retained.scene()==authored.scene&&retained.history_bytes()==0);
    }else throw std::runtime_error("unknown theme history family");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
