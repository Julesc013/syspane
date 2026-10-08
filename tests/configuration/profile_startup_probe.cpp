#include "profile_store_linux.hpp"
#include "machine_policy.hpp"
#include "digest.hpp"
#include <csignal>
#include <fstream>
#include <iostream>
#include <thread>
#include <unistd.h>
namespace c=syspane::configuration;namespace os=syspane::platform;using c::Json;
namespace {
void emit(const Json& v){std::cout<<v.dump()<<std::endl;}
Json view(os::LinuxProfileStore& store){
    const auto value=store.load();const auto paths=store.verified_paths();Json packages=Json::object();for(const auto& p:value.resources->packages())packages[c::sha256(p->manifest)]={{"manifest",p->manifest},{"assets",p->assets}};
    Json out={{"settings",value.documents.settings},{"scene",value.documents.scene},{"selection",value.resources->selection()},{"theme_pin",value.resources->theme_pin()},{"packages",packages},
        {"identity",value.identity?Json{{"request",value.identity->request},{"epoch",value.identity->epoch},{"body",value.identity->body}}:Json()},
        {"receipts",store.receipts().size()},{"recovered_previous",store.recovered_previous()},
        {"paths",{{"generations",paths.generations},{"packages",paths.packages},{"recovery",paths.recovery}}}};
    try{out["generation"]=store.generation_token();}catch(const std::exception& e){out["generation"]=nullptr;out["generation_error"]=e.what();}
    return out;
}
}
int main(int argc,char** argv){try{
    if(argc!=5||::geteuid()==0)throw syspane::protocol::Error("probe.arguments");
    std::ifstream input(argv[1]);Json config;input>>config;const std::string operation=argv[2],phase=argv[3],fault=argv[4];
    os::ProfileLocation location;location.profile=config.at("profile");location.portable_root=config.at("root");
    c::Policy policy;policy.available=config.value("available",true);policy.revision=config.value("revision",7U);
    if(config.contains("denied"))policy.denied_capabilities=config["denied"].get<std::set<std::string>>();
    if(config.contains("forced"))policy.forced=config["forced"].get<std::map<std::string,Json>>();
    std::set<std::string> caps={"scene.selector","scene.content","scene.edit-locks","scene.visibility","theme.typography","configuration.theme-overrides"};
    if(config.contains("capabilities"))caps=config["capabilities"].get<std::set<std::string>>();
    if(operation=="native-policy"){emit({{"available",os::machine_policy().available}});return 0;}
    bool throws=false,reenter=false;os::LinuxProfileStore* pointer=nullptr;
    os::LinuxProfileStore::PolicySource source;
    if(operation!="native-open")source=[&]{if(throws)throw syspane::protocol::Error("probe.policy");if(reenter&&pointer)pointer->load();return policy;};
    os::LinuxProfileStore store(location,config.value("create",true),caps,std::move(source),[&](const std::string& point){
        if(point!=phase)return;
        if(fault=="deny"){policy.available=false;return;}
        if(fault=="change"){++policy.revision;return;}
        emit({{"event","phase"},{"phase",point},{"pid",::getpid()}});
        if(fault=="stop")std::raise(SIGSTOP);
        else if(fault=="block"){std::string line;if(!std::getline(std::cin,line)||line!="resume")throw syspane::protocol::Error("probe.resume");}
    });pointer=&store;emit(view(store));if(operation!="session")return 0;
    std::string line;while(std::getline(std::cin,line)){
        const auto q=Json::parse(line);const std::string op=q.at("op");if(op=="exit")return 0;
        try{
            if(op=="commit"||op=="reconcile"){
                c::Transactions tx(store,q.value("epoch","E1"),c::make_resource_provider(store,caps));
                const c::Authority authority{true,"console",{"console"}};
                auto answer=op=="commit"?tx.submit("fixture:principal","fixture:connection",q.at("body"),authority,[&]{return policy;},0):
                    tx.reconcile("fixture:principal",q.at("original_epoch"),q.at("request"),authority,policy);
                Json out={{"result",answer}};try{out["snapshot"]=view(store);}catch(const std::exception& e){out["snapshot_error"]=e.what();}emit(out);continue;
            }
            if(op=="deny")policy.available=false;
            if(op=="regrant")policy.available=true;
            if(op=="revision")++policy.revision;
            if(op=="forced")policy.forced["display.enabled"]=false;
            if(op=="disclosure")policy.disclosure[{"console","history"}]={"public"};
            if(op=="capability")policy.denied_capabilities.insert("scene.content");
            if(op=="throw")throws=true;
            if(op=="source-reentry")reenter=true;
            if(op=="thread"){
                std::string error;std::thread t([&]{try{store.load();}catch(const std::exception& e){error=e.what();}});t.join();emit({{"error",error}});continue;
            }
            emit(view(store));
        }catch(const std::exception& e){emit({{"error",e.what()}});}
    }
    return 0;
}catch(const std::exception& e){emit({{"error",e.what()}});return 1;}}
