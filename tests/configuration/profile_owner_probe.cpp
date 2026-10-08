#include "profile_owner_linux.hpp"
#include "wire.hpp"
#include <csignal>
#include <fstream>
#include <iostream>
#include <thread>
#include <sys/resource.h>
#include <unistd.h>
using syspane::protocol::Json;using syspane::protocol::Error;namespace p=syspane::platform;
namespace {
void output(const Json& v){std::cout<<v.dump()<<std::endl;}
Json paths(const p::ProfilePaths& v){return {{"profile",v.profile},{"mode",v.mode},{"configuration",v.configuration},{"content",v.content},{"state",v.state},{"generations",v.generations},{"packages",v.packages},{"recovery",v.recovery}};}
p::ProfileLocation location(const Json& v){return {v.at("profile"),v.value("home",""),v.value("config_home",""),v.value("data_home",""),v.value("state_home",""),v.contains("portable_root")?std::optional<std::string>(v.at("portable_root")):std::nullopt};}
}
int main(int argc,char** argv){try{
    if(argc!=5||::geteuid()==0)throw Error("probe.arguments");
    const std::string operation=argv[2],phase=argv[3],fault=argv[4];
    std::ifstream input(argv[1],std::ios::binary);std::string bytes;char buffer[4096];
    if(!input)throw Error("probe.input");
    while(input){input.read(buffer,sizeof buffer);bytes.append(buffer,static_cast<std::size_t>(input.gcount()));if(bytes.size()>32768)throw Error("probe.size");}
    const auto v=Json::parse(bytes);auto selected=location(v);
    if(operation=="environment")selected=p::profile_environment(selected.profile,selected.portable_root);
    if(operation=="plan"||operation=="environment"){output(paths(p::profile_paths(selected)));return 0;}
    bool permitted=!(fault=="deny"&&phase=="-");
    if(fault=="file-size"){struct rlimit limit{};if(::getrlimit(RLIMIT_FSIZE,&limit))throw Error("probe.limit");limit.rlim_cur=64;
        if(::setrlimit(RLIMIT_FSIZE,&limit))throw Error("probe.limit");
        std::signal(SIGXFSZ,SIG_IGN);
    }
    p::LinuxProfileOwner owner(selected,v.value("create",true),[&]{return permitted;},[&](const std::string& point){
        if(point!=phase)return;
        if(fault=="deny"){permitted=false;return;}
        output({{"event","phase"},{"phase",point},{"pid",::getpid()}});
        if(fault=="stop")std::raise(SIGSTOP);
        else if(fault=="block"){std::string line;if(!std::getline(std::cin,line)||line!="resume")throw Error("probe.resume");}
    });
    output(paths(owner.verified_paths([]{return true;})));if(operation!="session")return 0;
    std::string line;while(std::getline(std::cin,line)){
        const auto q=Json::parse(line);const std::string op=q.at("op");if(op=="exit")return 0;
        try{
            if(op=="thread"){
                std::string error;std::thread t([&]{try{owner.verified_paths([]{return true;});}catch(const std::exception& e){error=e.what();}});t.join();output({{"error",error}});continue;
            }
            bool reentrant=false;auto guard=[&]{
                if(op=="deny")return false;
                if(op=="throw")throw Error("probe.guard");
                if(op=="reenter"){try{owner.verified_paths([]{return true;});}catch(const Error& e){reentrant=std::string(e.what())=="profile.reentrant";}}
                return true;
            };
            auto reply=paths(owner.verified_paths(guard));reply["reentrant_rejected"]=reentrant;output(reply);
        }catch(const std::exception& e){output({{"error",e.what()}});}
    }
    return 0;
}catch(const std::exception& e){output({{"error",e.what()}});return 1;}}
