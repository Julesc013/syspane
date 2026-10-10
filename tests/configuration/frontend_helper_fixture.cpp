#include "network_controller_linux.hpp"
#include "profile_controller_linux.hpp"
#include <fstream>
#include <thread>
#include <unistd.h>
namespace c=syspane::configuration;
std::string read(const char* path){std::ifstream file(path);std::string value;std::getline(file,value);return value;}
int main(int argc,char** argv){
    if(argc==3&&std::string(argv[1])=="--network"){
        const auto parent=syspane::protocol::decimal(argv[2]);if(!parent||!*parent)return 2;
        return syspane::application::run_network_controller(*parent,[]{
            c::Policy p;p.available=read("policy")!="deny"&&read("network-policy")!="deny";p.revision=7;
            if(read("policy")=="allow")for(const char* channel:{"inspector","accessibility"})p.disclosure[{"console",channel}]={"operational"};
            return p;
        },[]{if(read("network-mode")=="hold"){
            std::ofstream("network-held")<<::getpid();
            while(read("network-release")!="yes")std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }});
    }
    if(argc!=2)return 2;
    const auto parent=syspane::protocol::decimal(argv[1]);if(!parent||!*parent)return 2;
    return syspane::application::run_profile_controller(*parent,[]{
        c::Policy policy;policy.available=read("policy")=="allow";policy.revision=7;
        if(read("network")!="allow"||read("network-policy")=="deny")policy.denied_capabilities.insert("collection.network");
        if(read("reconcile")=="deny")policy.denied_capabilities.insert("result.reconcile");
        for(const char* channel:{"inspector","accessibility"})policy.disclosure[{"console",channel}]={"public","operational","sensitive"};
        const auto history=read("history");
        if(history=="allow"||history=="erase-denied")policy.disclosure[{"console","history"}]={"public","operational","sensitive"};
        if(history=="erase-denied")policy.denied_capabilities.insert("editor.recovery.erase");
        return policy;
    },[](const std::string& phase){
        if(phase!=read("phase"))return;
        std::ofstream("held")<<c::Json{{"pid",::getpid()},{"phase",phase}}.dump();
        while(read("release")!="yes")std::this_thread::sleep_for(std::chrono::milliseconds(5));
    });
}
