#include "theme_font.hpp"
#include "content.hpp"
#include "digest.hpp"
#include <fstream>
#include <functional>
#include <iostream>
namespace {
namespace c=syspane::configuration;using c::Json;
void need(bool v,const char* why){if(!v)throw std::runtime_error(why);}
void reject(const std::function<void()>& f,const std::string& context={}){bool failed=false;try{f();}catch(const syspane::protocol::Error&){failed=true;}if(!failed)throw std::runtime_error("expected rejection: "+context);}
Json read(const std::string& path){std::ifstream f(path);need(f.good(),"fixture file");Json v;f>>v;return v;}
Json font(const c::ThemeFont& f){return {{"family",f.family},{"size_dip",f.size_dip},{"weight",f.weight},{"style",f.style}};}
void resolution(const Json& cases){
    const auto theme=cases.at("theme");
    for(const auto& role:{"body","label","value","diagnostic"}){
        need(font(c::theme_font(theme,role))==cases.at("expected_roles").at(role),"literal role");
        need(font(c::theme_font(cases.at("legacy"),role))==cases.at("expected_base"),"legacy default");
        auto absent=theme;absent.erase("font_roles");need(font(c::theme_font(absent,role))==cases.at("expected_base"),"absent fallback");
        absent["font_roles"]=Json::object();need(font(c::theme_font(absent,role))==cases.at("expected_base"),"empty fallback");
        auto single=theme;single["font_roles"].erase(role);need(font(c::theme_font(single,role))==cases.at("expected_base"),"no role-to-role fallback");
    }
    auto changed=theme;const auto owned=c::theme_font(changed,"body");changed["font_roles"]["body"]["family"]="Changed";
    need(font(owned)==cases.at("expected_roles").at("body")&&theme==cases.at("theme"),"owned exact result");
    for(unsigned weight=100;weight<=900;weight+=100)for(const auto& style:{"normal","italic","oblique"}){
        auto t=theme;t.erase("font_roles");t["font"]["weight"]=weight;t["font"]["style"]=style;t["font"]["size_dip"]=9.25;
        auto f=c::theme_font(t,"body");need(f.weight==weight&&f.style==style&&f.size_dip==9.25,"font choices");
    }
    auto unicode=theme;unicode["font"]["family"]=std::string(128,'x');c::validate_content_document(unicode,"theme");
    unicode["font"]["family"]="\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e";c::validate_content_document(unicode,"theme");
}
void invalid(const Json& cases){
    for(const auto& f:cases.at("invalid_fonts")){
        auto t=cases.at("theme");t["font"]=f;reject([&]{c::validate_content_document(t,"theme");},"base "+f.dump());
        t=cases.at("theme");t["font_roles"]["body"]=f;reject([&]{c::theme_font(t,"body");},"body "+f.dump());
    }
    for(const auto& role:cases.at("invalid_roles"))for(const auto* theme:{"theme","legacy"})reject([&]{c::theme_font(cases.at(theme),role);});
    auto t=cases.at("theme");t["font_roles"]["caption"]=t["font"];reject([&]{c::validate_content_document(t,"theme");});
    t=cases.at("theme");t["schema_version"]="0.1.0";reject([&]{c::validate_content_document(t,"theme");});
    t=cases.at("theme");t["font_roles"]=nullptr;reject([&]{c::validate_content_document(t,"theme");});
}
c::ContentPackage pack(const char* id,const char* kind,const Json& doc,Json dependencies=Json::array()){
    const auto bytes=doc.dump()+"\n",path=std::string(kind)+".json";
    Json m={{"schema_version","0.1.0"},{"package_id",id},{"version","0.1.0"},{"kind",kind},{"license","MIT"},{"dependencies",dependencies},
        {"assets",Json::array({{{"path",path},{"media_type","application/json"},{"sha256",c::sha256(bytes)},{"bytes",bytes.size()}}})},
        {"total_unpacked_bytes",bytes.size()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    return {m.dump()+"\n",{{path,bytes}}};
}
Json pin(const c::ContentPackage& p,bool document){const auto m=Json::parse(p.manifest);const auto kind=m.at("kind").get<std::string>();const auto bytes=document?p.assets.at(kind+".json"):p.manifest;
    std::string id;
    if(document){const auto doc=Json::parse(bytes);id=doc.at(kind+"_id").get<std::string>();}else id=m.at("package_id").get<std::string>();
    return {{"id",id},{"version","0.1.0"},{"sha256",c::sha256(bytes)}};}
void resources(const Json& cases,const std::string& root){
    c::Authored a{read(root+"/settings.json"),read(root+"/scene-portable.json")};a.settings["revision"]=a.scene["revision"]="40";a.scene["theme_id"]="theme:typography";
    c::Policy policy;policy.available=true;policy.revision=7;c::Authority authority{true,"console",{"console"}};
    for(const auto* kind:{"theme","legacy"}){
        std::cout<<"Resource case "<<kind<<": packages\n";
        auto t=pack("package:font","theme",cases.at(kind)),s=pack("package:scene","scene",a.scene);
        auto preset=pack("package:preset","preset",{{"schema_version","0.1.0"},{"preset_id","preset:font"},{"version","0.1.0"},{"parent",nullptr},{"scene",pin(s,true)},{"theme",pin(t,true)},
            {"settings",Json::array()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}},Json::array({pin(t,false),pin(s,false)}));
        std::cout<<"Resource case "<<kind<<": catalog\n";
        for(const auto* package:{&t,&s,&preset}){
            const auto m=Json::parse(package->manifest);const auto type=m.at("kind").get<std::string>();
            try{c::validate_content_manifest(package->manifest);const auto doc=c::parse_content_json(package->assets.at(type+".json"));
                if(type=="scene")c::validate_scene_document(doc);else c::validate_content_document(doc,type);
            }catch(const std::exception& error){std::cerr<<"Package boundary "<<type<<" "<<package->manifest<<" document "<<package->assets.at(type+".json")<<'\n';throw std::runtime_error(error.what());}
        }
        c::ContentCatalog catalog({t,s,preset});const Json selection={{"package",pin(preset,false)},{"preset",pin(preset,true)}};
        std::cout<<"Resource case "<<kind<<": resolve\n";auto set=catalog.resources(selection,a);
        const bool modern=std::string(kind)=="theme";need(set->required().count("theme.typography")==static_cast<unsigned>(modern),"derived capability");
        need(set->theme()==cases.at(kind)&&set->theme_pin()==pin(t,true),"exact theme and pin");bool bytes=false;
        for(const auto& p:set->packages())if(p->assets.count("theme.json")){need(p->assets.at("theme.json")==t.assets.at("theme.json"),"immutable theme bytes");bytes=true;}
        need(bytes,"retained package");
        if(modern){reject([&]{c::authorize_resources(*set,policy,{});});reject([&]{catalog.preview(pin(preset,false),pin(preset,true),a,"preview",authority,policy,{});});}
        else c::authorize_resources(*set,policy,{});
        c::authorize_resources(*set,policy,{"theme.typography"});auto denied=policy;denied.denied_capabilities.insert("theme.typography");
        if(modern){reject([&]{c::authorize_resources(*set,denied,{"theme.typography"});});reject([&]{catalog.preview(pin(preset,false),pin(preset,true),a,"preview",authority,denied,{"theme.typography"});});}
        std::cout<<"Resource case "<<kind<<": preview\n";
        auto plan=catalog.preview(pin(preset,false),pin(preset,true),a,"preview",authority,policy,{"theme.typography"});need(plan.theme==cases.at(kind),"preview exact document");
    }
}
}
int main(int argc,char** argv){try{if(argc!=4)return 2;const auto cases=read(argv[2]);const std::string name=argv[1];if(name=="RESOLUTION")resolution(cases);else if(name=="INVALID")invalid(cases);else if(name=="RESOURCES")resources(cases,argv[3]);else return 2;std::cout<<name<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
