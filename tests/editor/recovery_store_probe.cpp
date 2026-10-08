#include "recovery_store_linux.hpp"
#include "digest.hpp"
#include <csignal>
#include <fstream>
#include <iostream>
#include <thread>
#include <sys/resource.h>
#include <unistd.h>
namespace {
using namespace syspane;using protocol::Json;using platform::LinuxRecoveryStore;
void output(const Json& v){std::cout<<v.dump()<<std::endl;}
std::string payload(const std::string& path){
    std::ifstream input(path,std::ios::binary);if(!input)throw protocol::Error("probe.input");std::string bytes;char buffer[4096];
    while(input){input.read(buffer,sizeof buffer);bytes.append(buffer,static_cast<std::size_t>(input.gcount()));if(bytes.size()>LinuxRecoveryStore::maximum_bytes+1)throw protocol::Error("probe.size");}return bytes;
}
Json snapshot(LinuxRecoveryStore& s,bool expose=false){const auto v=s.snapshot([]{return true;});Json out={
    {"version",{{"instance",v.version.instance},{"sequence",std::to_string(v.version.sequence)},{"digest",v.version.digest?Json(*v.version.digest):Json()}}},
    {"bytes",v.bytes?Json(v.bytes->size()):Json()},{"sha256",v.bytes?Json(configuration::sha256(*v.bytes)):Json()},{"pending",v.pending}};
    if(expose)out["record"]=v.bytes?Json(*v.bytes):Json();
    return out;
}
platform::RecoveryVersion version(const Json& v){const auto n=protocol::decimal(v.at("sequence").get<std::string>());if(!n)throw protocol::Error("probe.version");return {v.at("instance"),*n,v.at("digest").is_null()?std::nullopt:std::optional<std::string>(v.at("digest"))};}
Json result(const platform::RecoveryPublication& v){return {{"outcome",v.outcome==configuration::Publication::durable?"durable":v.outcome==configuration::Publication::unknown?"unknown":"unchanged"},{"error",v.error}};}
}
int main(int argc,char** argv){try{
    if(argc!=6||::geteuid()==0)throw protocol::Error("probe.arguments");
    const std::string path=argv[1],operation=argv[2],file=argv[3],phase=argv[4],fault=argv[5];bool permitted=true;
    if(fault=="file-size"){
        struct rlimit limit{};if(::getrlimit(RLIMIT_FSIZE,&limit)!=0)throw protocol::Error("probe.limit");
        limit.rlim_cur=1024;if(::setrlimit(RLIMIT_FSIZE,&limit)!=0)throw protocol::Error("probe.limit");std::signal(SIGXFSZ,SIG_IGN);
    }
    LinuxRecoveryStore store(path,[&](const char* point){if(phase!=point)return;
        if(fault=="deny"){permitted=false;return;}
        if(fault=="throw")throw protocol::Error("recovery_store.injected");
        output({{"event","phase"},{"phase",point},{"pid",::getpid()}});
        if(fault=="stop")std::raise(SIGSTOP);
        else if(fault=="block"){std::string reply;if(!std::getline(std::cin,reply)||reply!="resume")throw protocol::Error("probe.resume");}
    });
    if(operation=="read"||operation=="export"){output(snapshot(store,operation=="export"));return 0;}
    if(operation=="session"){
        output(snapshot(store));std::string line;
        while(std::getline(std::cin,line)){
            const auto q=Json::parse(line);const std::string op=q.at("op");if(op=="exit")return 0;
            if(op=="read"){output(snapshot(store));continue;}
            if(op=="deny-read"||op=="deny-read-late"||op=="wrong-thread"){
                std::string error;unsigned calls=0;
                auto run=[&]{try{store.snapshot([&]{return op!="deny-read"&&(op!="deny-read-late"||++calls==1);});}catch(const protocol::Error& e){error=e.what();}};
                if(op=="wrong-thread"){std::thread t(run);t.join();}else run();
                output({{"error",error}});continue;
            }
            bool reentrant=false;auto guard=[&]{
                if(op=="deny")return false;
                if(op=="guard-throw")throw protocol::Error("probe.guard");
                if(op=="reenter"){try{store.snapshot([]{return true;});}catch(const protocol::Error& e){reentrant=std::string(e.what())=="recovery_store.reentrant";}}return true;
            };
            auto v=op=="retire"?store.retire(version(q.at("version")),guard):store.replace(version(q.at("version")),payload(q.at("file")),guard);
            auto reply=result(v);reply["snapshot"]=snapshot(store);reply["reentrant_rejected"]=reentrant;output(reply);
        }
        return 0;
    }
    const auto initial=store.snapshot([]{return true;});const auto v=operation=="replace"?store.replace(initial.version,payload(file),[&]{return permitted;}):store.retire(initial.version,[&]{return permitted;});
    auto reply=result(v);try{reply["snapshot"]=snapshot(store);}catch(const protocol::Error& e){reply["snapshot_error"]=e.what();}output(reply);return 0;
}catch(const std::exception& e){output({{"error",e.what()}});return 1;}}
