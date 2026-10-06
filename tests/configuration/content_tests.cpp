#include "content.hpp"
#include "digest.hpp"
#include <fstream>
#include <functional>

namespace {
namespace c=syspane::configuration;namespace p=syspane::protocol;using p::Json;
void check(bool ok,int line){if(!ok)throw std::runtime_error("content test:"+std::to_string(line));}
#define VERIFY(x) check(static_cast<bool>(x),__LINE__)
void rejects(const std::function<void()>& call,const char* code=nullptr){bool failed=false;try{call();}catch(const p::Error& e){failed=true;if(code)VERIFY(std::string(e.what())==code);}VERIFY(failed);}
Json read(const std::string& root,const char* name){std::ifstream stream(root+"/"+name);VERIFY(stream.good());Json value;stream>>value;return value;}
Json package_pin(const c::ContentPackage& package){auto m=c::parse_content_json(package.manifest);return {{"id",m["package_id"]},{"version",m["version"]},{"sha256",c::sha256(package.manifest)}};}
Json doc_pin(const c::ContentPackage& package){auto m=c::parse_content_json(package.manifest);const auto kind=m["kind"].get<std::string>();const auto& b=package.assets.at(kind+".json");
    return {{"id",c::parse_content_json(b)[kind+"_id"]},{"version",m["version"]},{"sha256",c::sha256(b)}};}
c::ContentPackage pack(const std::string& id,const std::string& kind,const Json& doc,Json deps=Json::array()){
    const auto bytes=doc.dump()+"\n";Json m={{"schema_version","0.1.0"},{"package_id",id},{"version","0.1.0"},{"kind",kind},{"license","MIT"},{"dependencies",deps},
        {"assets",Json::array({{{"path",kind+".json"},{"media_type","application/json"},{"sha256",c::sha256(bytes)},{"bytes",bytes.size()}}})},
        {"total_unpacked_bytes",bytes.size()},{"required_capabilities",Json::array()},{"optional_capabilities",Json::array()}};
    return {m.dump()+"\n",{{kind+".json",bytes}}};
}
void manifest(c::ContentPackage& bytes,const std::function<void(Json&)>& change){auto m=c::parse_content_json(bytes.manifest);change(m);bytes.manifest=m.dump();}
struct Fixture {
    c::Authored base;std::vector<c::ContentPackage> packages;c::Policy policy;c::Authority authority{true,"console",{"console"}};
    explicit Fixture(const std::string& root):base{read(root,"settings.json"),read(root,"scene-portable.json")}{
        base.settings["revision"]=base.scene["revision"]="40";policy.available=true;policy.revision=7;
        auto theme=read(root,"theme.json");packages.push_back(pack("package:native","theme",theme));theme["theme_id"]="theme:parent";packages.push_back(pack("package:other","theme",theme));
        auto scene=base.scene;scene["revision"]="3";packages.push_back(pack("package:scene","scene",scene));
        Json parent={{"schema_version","0.1.0"},{"preset_id","preset:parent"},{"version","0.1.0"},{"parent",nullptr},{"scene",doc_pin(packages[2])},
            {"theme",doc_pin(packages[1])},{"settings",Json::array({{{"path","display.enabled"},{"value",false}},{{"path","sampling.resources_ms"},{"value",1000}}})},
            {"required_capabilities",Json::array({"scene.selector"})},{"optional_capabilities",Json::array({"optional.z","optional.a"})}};
        packages.push_back(pack("package:parent","preset",parent,Json::array({package_pin(packages[0]),package_pin(packages[1]),package_pin(packages[2])})));
        auto leaf=parent;leaf["preset_id"]="preset:leaf";leaf["parent"]=doc_pin(packages[3]);leaf["theme"]=doc_pin(packages[0]);leaf["settings"]=Json::array({{{"path","sampling.resources_ms"},{"value",1500}}});
        packages.push_back(pack("package:leaf","preset",leaf,Json::array({package_pin(packages[3])})));
    }
    void leaf(const std::function<void(Json&)>& change){auto doc=c::parse_content_json(packages[4].assets.at("preset.json"));change(doc);packages[4]=pack("package:leaf","preset",doc,Json::array({package_pin(packages[3])}));}
    c::PresetPlan preview(){return c::ContentCatalog(packages).preview(package_pin(packages[4]),doc_pin(packages[4]),base,"P",authority,policy,{"scene.selector"});}
};
void compose(const std::string& root){Fixture f(root);const auto base=f.base;auto plan=f.preview();
    VERIFY(plan.candidate.settings["sampling"]["resources_ms"]==1500&&plan.candidate.settings["display"]["enabled"]==false);
    VERIFY(plan.candidate.scene["revision"]=="40"&&plan.candidate.scene["theme_id"]=="theme:native"&&plan.theme["theme_id"]=="theme:native");
    VERIFY(plan.command["intent"]=="preview"&&plan.command["policy_generation"]=="7"&&plan.command["operations"].size()==3);
    VERIFY(plan.command["operations"][0]["path"]=="display.enabled"&&plan.command["operations"][1]["path"]=="sampling.resources_ms");
    VERIFY(plan.setting_origins["display.enabled"]==doc_pin(f.packages[3])&&plan.setting_origins["sampling.resources_ms"]==doc_pin(f.packages[4]));
    VERIFY(plan.preset_pins==Json::array({doc_pin(f.packages[3]),doc_pin(f.packages[4])})&&plan.package_pins.size()==5);
    VERIFY(plan.missing_optional==Json::array({"optional.a","optional.z"}));
    f.leaf([](Json& d){d["theme"]=nullptr;});auto inherited=f.preview();VERIFY(inherited.candidate.scene["theme_id"].is_null()&&inherited.theme["theme_id"]=="theme:native");
    VERIFY(f.base.settings==base.settings&&f.base.scene==base.scene);
    f.packages.clear();bool original=false;for(const auto& bytes:plan.packages)if(bytes->assets.count("scene.json")){VERIFY(c::parse_content_json(bytes->assets.at("scene.json"))["revision"]=="3");original=true;}VERIFY(original);
}
void pins(const std::string& root){Fixture f(root);auto bad=package_pin(f.packages[4]);bad["sha256"]=std::string(64,'0');
    rejects([&]{c::ContentCatalog(f.packages).preview(bad,doc_pin(f.packages[4]),f.base,"P",f.authority,f.policy,{"scene.selector"});},"content.reference");
    f.leaf([](Json& d){d["scene"]["sha256"]=std::string(64,'0');});rejects([&]{f.preview();},"content.reference");
    f=Fixture(root);manifest(f.packages[4],[](Json& m){m["dependencies"]=Json::array();});rejects([&]{f.preview();},"content.reference");
    f=Fixture(root);f.packages[0].assets["theme.json"]+=" ";rejects([&]{f.preview();},"content.digest");
    f=Fixture(root);manifest(f.packages[4],[](Json& m){m["dependencies"][0]["sha256"]=std::string(64,'0');});rejects([&]{f.preview();},"content.dependency");
    f=Fixture(root);f.packages.push_back(f.packages[0]);rejects([&]{f.preview();},"content.duplicate_package");
    f=Fixture(root);f.packages[0].assets["extra.json"]="{}";rejects([&]{f.preview();},"content.assets");
}
void names(const std::string& root){
    for(const char* name:{"/a","a/../b","a//b","a/.","a\\b","C:a","a.","a ","nul.png","COM1/x","manifest.json","MANIFEST.JSON","Manifest.json/child"})rejects([&]{c::validate_content_path(name);},"content.path");
    c::validate_content_path("images/space name-1.png");c::validate_content_path("com10.txt");
    Fixture f(root);for(const char* path:{"Theme.json","theme.json/child"}){auto package=f.packages[0];manifest(package,[&](Json& m){auto a=m["assets"][0];a["path"]=path;m["assets"].push_back(a);m["total_unpacked_bytes"]=2*m["total_unpacked_bytes"].get<unsigned>();});
        rejects([&]{c::validate_content_manifest(package.manifest);},"content.path_collision");}
    auto package=f.packages[0];manifest(package,[](Json& m){auto a=m["assets"][0];a["path"]="Images/a.png";m["assets"].push_back(a);a["path"]="images/b.png";m["assets"].push_back(a);m["total_unpacked_bytes"]=3*m["total_unpacked_bytes"].get<unsigned>();});
    rejects([&]{c::validate_content_manifest(package.manifest);},"content.path_collision");
    rejects([]{c::parse_content_json("{\"x\":1,\"x\":2}");},"json.duplicate_key");
    VERIFY(c::parse_content_json("{}\r\n\t ")==Json::object());
}
void bounds(const std::string& root){Fixture f(root);
    f.leaf([](Json& d){d["settings"].push_back(d["settings"][0]);});rejects([&]{f.preview();},"content.duplicate_setting");
    f=Fixture(root);f.leaf([](Json& d){d["settings"][0]["value"]=1;});rejects([&]{f.preview();},"authored.schema");
    f=Fixture(root);manifest(f.packages[0],[](Json& m){m["total_unpacked_bytes"]=1;});rejects([&]{f.preview();},"content.total");
    f=Fixture(root);auto d=read(root,"theme.json");std::vector<c::ContentPackage> chain;
    for(unsigned i=0;i<9;++i){d["theme_id"]="theme:"+std::to_string(i);chain.push_back(pack("package:"+std::to_string(i),"theme",d,i?Json::array({package_pin(chain.back())}):Json::array()));
        if(i==7)(void)c::ContentCatalog(chain);}
    rejects([&]{c::ContentCatalog catalog(chain);},"content.depth");
    rejects([]{c::ContentCatalog catalog(std::vector<c::ContentPackage>(65));},"content.capacity");
    rejects([]{c::parse_content_json(std::string(262145,' '));},"content.size");
}
void capabilities(const std::string& root){Fixture f(root);f.policy.denied_capabilities.insert("scene.selector");rejects([&]{f.preview();},"content.capability");
    f=Fixture(root);rejects([&]{c::ContentCatalog(f.packages).preview(package_pin(f.packages[4]),doc_pin(f.packages[4]),f.base,"P",f.authority,f.policy,{});},"content.capability");
    f=Fixture(root);f.leaf([](Json& d){d["theme"]=nullptr;d["settings"].push_back({{"path","display.theme_id"},{"value","theme:missing"}});});rejects([&]{f.preview();},"content.theme");
}
void policy(const std::string& root){Fixture f(root);f.policy.forced["sampling.resources_ms"]=1000;rejects([&]{f.preview();},"policy.forced");
    f=Fixture(root);f.policy.available=false;rejects([&]{f.preview();},"policy.denied");
    f=Fixture(root);f.policy.denied_capabilities.insert("settings.preview");rejects([&]{f.preview();},"policy.denied");
    f=Fixture(root);f.authority={true,"saver_settings",{"saver_settings"}};rejects([&]{f.preview();},"policy.denied");
}
}
void content_tests(const std::string& name,const std::string& root){
    if(name=="CONTENT-COMPOSE")compose(root);else if(name=="CONTENT-PINS")pins(root);else if(name=="CONTENT-PATHS")names(root);
    else if(name=="CONTENT-BOUNDS")bounds(root);else if(name=="CONTENT-CAPABILITIES")capabilities(root);else if(name=="CONTENT-POLICY")policy(root);else VERIFY(false);
}
