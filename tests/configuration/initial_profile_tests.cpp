#include "initial_profile.hpp"
#include "digest.hpp"
#include <fstream>
#include <iostream>
namespace c=syspane::configuration;using c::Json;
namespace {
void check(bool v,int line){if(!v)throw std::runtime_error("initial assertion:"+std::to_string(line));}
#define CHECK(v) check(static_cast<bool>(v),__LINE__)
template<class F>void refuses(F f){bool failed=false;try{f();}catch(const syspane::protocol::Error&){failed=true;}CHECK(failed);}
Json packages(const c::Committed& v){Json out=Json::object();for(const auto& p:v.resources->packages())out[c::sha256(p->manifest)]={{"manifest",p->manifest},{"assets",p->assets}};return out;}
}
int main(int argc,char** argv){try{
    CHECK(argc==2);std::ifstream file(argv[1]);Json expected;file>>expected;
    const std::set<std::string> caps={"scene.selector","scene.content"};c::Policy policy;policy.available=true;policy.revision=7;
    const auto value=c::initial_profile(policy,caps);CHECK(value.documents.settings==expected["documents"]["settings"]&&value.documents.scene==expected["documents"]["scene"]);
    CHECK(!value.identity&&value.resources->selection()==expected["selection"]&&value.resources->theme_pin()==expected["theme_pin"]);
    Json want=Json::object();for(const auto& p:expected["packages"])want[c::sha256(p["manifest"].get<std::string>())]=p;
    CHECK(packages(value)==want);CHECK(packages(c::initial_profile(policy,caps))==want);
    for(const char* cap:{"profile.open","profile.create","settings.commit","scene.replace","preset.apply","scene.content"}){
        auto denied=policy;denied.denied_capabilities.insert(cap);refuses([&]{c::initial_profile(denied,caps);});}
    auto unavailable=policy;unavailable.available=false;refuses([&]{c::initial_profile(unavailable,caps);});
    refuses([&]{c::initial_profile(policy,{});});
    auto forced=policy;forced.forced={{"sampling.resources_ms",1500},{"display.enabled",false},{"privacy.export_enabled",false}};
    const auto constrained=c::initial_profile(forced,caps);auto settings=expected["documents"]["settings"];settings["sampling"]["resources_ms"]=1500;settings["display"]["enabled"]=false;
    CHECK(constrained.documents.settings==settings&&constrained.documents.scene==value.documents.scene&&packages(constrained)==want);
    for(const auto& change:std::vector<std::pair<std::string,Json>>{{"display.theme_id","theme:absent"},{"unknown.setting",true},{"sampling.resources_ms",0},{"sampling.resources_ms",true}}){
        forced=policy;forced.forced.emplace(change);refuses([&]{c::initial_profile(forced,caps);});}
    auto copy=value.documents;copy.settings["sampling"]["resources_ms"]=2000;CHECK(c::initial_profile(policy,caps).documents.settings==expected["documents"]["settings"]);
    std::cout<<"INITIAL-PROFILE: exact defaults/packages, repeatability, policy/capability refusal and forced values passed\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
