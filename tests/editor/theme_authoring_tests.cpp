#include "editor_theme.hpp"
#include "authored_theme.hpp"
#include "digest.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include <algorithm>
#include <iostream>
#include <locale>
namespace {
namespace c=syspane::configuration;namespace ui=syspane::interfaces;using c::Json;
void check(bool b,int line){if(!b)throw std::runtime_error("theme authoring assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f){bool caught=false;try{f();}catch(const syspane::protocol::Error&){caught=true;}CHECK(caught);}
c::Policy policy(){c::Policy p;p.available=true;p.revision=7;return p;}
c::ResourceSnapshot derived(const settings_fixture::Fixture& f,const c::AuthoredTheme& art){
    auto old=f.catalog->resources(f.document["selection"],f.authored);std::vector<c::ContentPackage> packages;for(const auto& p:old->packages())packages.push_back(*p);packages.push_back(art.package);
    const auto leaf=std::find_if(packages.begin(),packages.end(),[&](const auto& p){return c::sha256(p.manifest)==f.document["selection"]["package"]["sha256"];});CHECK(leaf!=packages.end());
    auto doc=Json::parse(leaf->assets.at("preset.json"));doc["preset_id"]="preset:author-test";doc["parent"]=nullptr;doc["theme"]=art.theme_pin;
    const auto bytes=doc.dump()+"\n";Json m={{"schema_version","0.1.0"},{"package_id","package:author-test"},{"version","0.1.0"},{"kind","preset"},{"license","MIT"},
        {"dependencies",Json::array({f.document["selection"]["package"],art.package_pin})},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()},
        {"assets",Json::array({{{"path","preset.json"},{"media_type","application/json"},{"bytes",bytes.size()},{"sha256",c::sha256(bytes)}}})},{"total_unpacked_bytes",bytes.size()}};
    const auto manifest=m.dump()+"\n";packages.push_back({manifest,{{"preset.json",bytes}}});auto authored=f.authored;authored.scene["theme_id"]=art.theme.at("theme_id");
    return c::ContentCatalog(std::move(packages)).resources({{"package",{{"id","package:author-test"},{"version","0.1.0"},{"sha256",c::sha256(manifest)}}},{"preset",{{"id","preset:author-test"},{"version","0.1.0"},{"sha256",c::sha256(bytes)}}}},authored);
}
void run(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/editor/theme-authoring-cases.json");const auto resource=f.catalog->resources(f.document["selection"],f.authored);
    const auto original=resource->theme();CHECK(original==cases["source"]);const auto expected=cases["candidate"];const std::set<std::string> caps{"theme.typography","scene.content"};
    if(name=="INPUT"){
        const auto baseline=ui::theme_input(original);CHECK(baseline.font.weight=="400"&&baseline.font.style=="normal"&&baseline.roles.empty());
        auto input=ui::theme_input(expected);CHECK(input.roles.size()==4&&input.font.size_dip=="17.25");CHECK(ui::theme_edit(original,input).dump()==expected.dump());
        input.roles.erase("value");auto removed=ui::theme_edit(expected,input);CHECK(!removed["font_roles"].contains("value")&&removed["font"]==expected["font"]);
        input.roles.clear();CHECK(!ui::theme_edit(expected,input).contains("font_roles"));
        input=ui::theme_input(expected);input.font.family="Literal family";CHECK(ui::theme_edit(expected,input)["font"]["family"]=="Literal family"&&expected==cases["candidate"]&&resource->theme()==original);
        struct Comma:std::numpunct<char>{char do_decimal_point()const override{return ',';}};const auto prior=std::locale();std::locale::global(std::locale(prior,new Comma));
        try{CHECK(ui::theme_input(expected).font.size_dip=="17.25");auto in=ui::theme_input(expected);in.font.size_dip="+1.725e1";CHECK(ui::theme_edit(expected,in).dump()==expected.dump());}catch(...){std::locale::global(prior);throw;}std::locale::global(prior);
    }else if(name=="NOOP"){
        for(auto theme:{original,expected}){const auto before=theme.dump();CHECK(ui::theme_edit(theme,ui::theme_input(theme)).dump()==before);theme.erase("font_roles");CHECK(ui::theme_edit(theme,ui::theme_input(theme)).dump()==theme.dump());if(theme["schema_version"]=="0.2.0"){theme["font_roles"]=Json::object();CHECK(ui::theme_edit(theme,ui::theme_input(theme)).dump()==theme.dump());}}
        CHECK(!c::author_theme(*resource,original,policy(),caps));auto in=ui::theme_input(original);in.font.size_dip="1.3e1";CHECK(ui::theme_edit(original,in).dump()==original.dump());
    }else if(name=="INVALID"){
        for(const auto& v:cases["invalid_size"]){auto in=ui::theme_input(expected);in.font.size_dip=v;rejects([&]{ui::theme_edit(original,in);});}
        for(const auto& v:cases["invalid_weight"]){auto in=ui::theme_input(expected);in.roles.at("diagnostic").weight=v;rejects([&]{ui::theme_edit(original,in);});}
        for(const auto& v:cases["invalid_style"]){auto in=ui::theme_input(expected);in.font.style=v.is_null()?"null":v.get<std::string>();rejects([&]{ui::theme_edit(original,in);});}
        for(const auto& v:cases["invalid_family"]){auto in=ui::theme_input(expected);in.roles.at("value").family=v;rejects([&]{ui::theme_edit(original,in);});}
        auto in=ui::theme_input(expected);in.roles["unknown"]=in.font;rejects([&]{ui::theme_edit(original,in);});in.roles.clear();in.roles["unknown"]=in.font;rejects([&]{ui::theme_edit(original,in);});
        for(const char* k:{"theme_id","name","motion","tokens","extensions"}){auto bad=expected;bad[k]=k==std::string("tokens")?original.at(k):Json("changed");if(k==std::string("tokens"))bad[k]["foreground"]="#ff0000ff";rejects([&]{c::author_theme(*resource,bad,policy(),caps);});}
        auto denied=policy();denied.denied_capabilities.insert("theme.typography");rejects([&]{c::author_theme(*resource,expected,denied,caps);});denied.available=false;rejects([&]{c::author_theme(*resource,expected,denied,caps);});rejects([&]{c::author_theme(*resource,expected,policy(),{"scene.content"});});rejects([&]{c::author_theme(*resource,expected,policy(),{"theme.typography"});});
        CHECK(resource->theme()==original);
    }else if(name=="ARTIFACT"){
        auto art=c::author_theme(*resource,expected,policy(),caps);CHECK(art.has_value());const auto& want=cases["expected"];
        CHECK(art->theme.dump()==want["theme"].dump()&&art->package.manifest==want["manifest"]&&art->package.assets.size()==1&&art->package.assets.at("theme.json")==want["asset"]);
        CHECK(art->theme_pin==want["theme_pin"]&&art->package_pin==want["package_pin"]);CHECK(resource->theme()==original);
        for(unsigned n=0;n<20;++n){auto repeated=c::author_theme(*resource,expected,policy(),caps);CHECK(repeated->package.manifest==art->package.manifest&&repeated->package.assets==art->package.assets);}
        auto next=derived(f,*art);CHECK(next->theme()==art->theme&&next->theme_pin()==art->theme_pin);auto changed=next->theme();changed["font"]["size_dip"]=21.25;const auto different=c::author_theme(*next,changed,policy(),caps);CHECK(different->package_pin!=art->package_pin);
        // Returning from a differently identified copy to the fixed content has the same seed.
        auto copy=expected;copy["theme_id"]=different->theme.at("theme_id");auto other=derived(f,*different);auto back=c::author_theme(*other,copy,policy(),caps);CHECK(back->package_pin==art->package_pin&&back->package.assets==art->package.assets);
        auto licensed=*different;auto manifest=Json::parse(licensed.package.manifest);manifest["license"]="BSD-2-Clause";licensed.package.manifest=manifest.dump()+"\n";licensed.package_pin["sha256"]=c::sha256(licensed.package.manifest);
        const auto licensed_source=derived(f,licensed);auto preserved=c::author_theme(*licensed_source,copy,policy(),caps);const auto& license_want=cases["expected_license"];
        CHECK(preserved->package.manifest==license_want["manifest"]&&preserved->package.assets.at("theme.json")==license_want["asset"]&&preserved->package_pin==license_want["package_pin"]&&preserved->theme_pin==license_want["theme_pin"]);
        CHECK(preserved->package_pin.at("id")!=art->package_pin.at("id")&&preserved->theme.at("theme_id")!=art->theme.at("theme_id"));
        art->theme["font"]["family"]="owned";CHECK(next->theme()==want["theme"]&&resource->theme()==original);
    }else throw std::runtime_error("unknown theme authoring test");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
