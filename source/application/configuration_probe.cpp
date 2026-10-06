#include "generation_store_linux.hpp"
#include "content_reader_linux.hpp"
#include "digest.hpp"
#include <algorithm>
#include <csignal>
#include <fstream>
#include <iostream>
#include <thread>
#include <chrono>
#include <unistd.h>

namespace c=syspane::configuration;namespace os=syspane::platform;using syspane::protocol::Json;
std::string read(const char* path){std::ifstream input(path,std::ios::binary);if(!input)throw syspane::protocol::Error("probe.input");
    std::string value;char buffer[4096];while(input){input.read(buffer,sizeof buffer);value.append(buffer,static_cast<std::size_t>(input.gcount()));
        if(value.size()>262144)throw syspane::protocol::Error("probe.size");}
    const auto end=value.find_last_not_of(" \r\n\t");if(end==std::string::npos)throw syspane::protocol::Error("probe.empty");value.resize(end+1);return value;}
int main(int argc,char** argv){try{
    if(argc<3||argc>69||::geteuid()==0)throw syspane::protocol::Error("probe.arguments");
    const std::string mode=argv[2];const std::string fault=(argc==5&&mode=="commit")||(argc>=6&&mode=="content-commit")?argv[4]:"";
    bool revoked=false;
    os::LinuxGenerationStore store(argv[1],[&](const char* step){if(fault==step){std::cout<<Json{{"transition",step}}.dump()<<std::endl;std::raise(SIGSTOP);}
        if(fault=="revoke"&&std::string(step)=="selector_ready")revoked=true;
        if(fault==std::string("fail:")+step)throw syspane::protocol::Error("probe.injected");});
    if(mode=="init"&&argc==5){store.initialize({syspane::protocol::parse(read(argv[3])),syspane::protocol::parse(read(argv[4]))});}
    else if(mode=="hold"&&argc==3){std::cout<<"{\"locked\":true}"<<std::endl;std::this_thread::sleep_for(std::chrono::seconds(10));return 0;}
    else if(mode=="read"&&argc==3){}
    else if(mode=="content-commit"&&argc>=6){
        std::vector<std::string> packages;for(int i=5;i<argc;++i)packages.emplace_back(argv[i]);
        c::ResourceProvider provider{{"scene.selector"},[&](const c::Authored& candidate,const Json& selection){
            return c::ContentCatalog(os::read_content_packages(packages)).resources(selection,candidate);}};
        c::Transactions tx(store,"E1",std::move(provider));c::Policy policy;policy.available=true;policy.revision=7;
        if(fault=="deny")policy.denied_capabilities.insert("scene.selector");
        std::cout<<Json{{"result",tx.submit("fixture:principal","fixture:connection",read(argv[3]),{true,"console",{"console"}},[&]{auto current=policy;if(revoked)current.revision=8;return current;},0)}}.dump()<<std::endl;return 0;
    }else if(mode=="commit"&&(argc==4||argc==5)){
        c::Transactions tx(store,"E1",[](const c::Authored& v){if(v.settings["display"]["theme_id"]!="theme:native"||
            (!v.scene["theme_id"].is_null()&&v.scene["theme_id"]!="theme:native"))throw syspane::protocol::Error("resource.unavailable");});c::Policy policy;policy.available=true;policy.revision=7;
        std::cout<<Json{{"result",tx.submit("fixture:principal","fixture:connection",read(argv[3]),{true,"console",{"console"}},[&]{auto current=policy;if(revoked)current.revision=8;return current;},0)}}.dump()<<std::endl;return 0;
    }else if((mode=="reconcile"||mode=="deny-reconcile")&&argc==5){
        c::Transactions tx(store,"E2",[](const c::Authored&){});c::Policy policy;policy.available=true;policy.revision=8;if(mode=="deny-reconcile")policy.denied_capabilities.insert("scene.replace");
        std::cout<<Json{{"result",tx.reconcile("fixture:principal",argv[3],argv[4],{true,"console",{"console"}},policy)}}.dump()<<std::endl;return 0;
    }else throw syspane::protocol::Error("probe.arguments");
    const auto current=store.load();Json output={{"settings",current.documents.settings},{"scene",current.documents.scene},{"recovered_previous",store.recovered_previous()}};
    if(current.resources){Json pins=Json::array();for(const auto& package:current.resources->packages())pins.push_back(c::sha256(package->manifest));
        std::sort(pins.begin(),pins.end());output["resources"]={{"selection",current.resources->selection()},{"theme",current.resources->theme()},
            {"theme_pin",current.resources->theme_pin()},{"packages",pins}};}
    std::cout<<output.dump()<<std::endl;return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
