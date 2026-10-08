#include "recovery_queue_linux.hpp"
#include "digest.hpp"
#include <chrono>
#include <fstream>
#include <iostream>
#include <thread>
#include <unistd.h>
namespace {
using namespace syspane;using protocol::Json;
const char* name(platform::RecoveryQueueState state){using S=platform::RecoveryQueueState;switch(state){
case S::loading:return "loading";case S::ready:return "ready";case S::busy:return "busy";case S::retiring:return "retiring";
case S::retired:return "retired";case S::unavailable:return "unavailable";case S::closing:return "closing";case S::closed:return "closed";}return "invalid";}
Json status(const platform::RecoveryQueueStatus& s){return {{"state",name(s.state)},{"active",std::to_string(s.active)},{"pending",std::to_string(s.pending)},{"process",s.process},{"retained_bytes",s.retained_bytes},{"reaped",s.reaped},{"error",s.error}};}
std::string read(const std::string& path){std::ifstream f(path,std::ios::binary);if(!f)throw protocol::Error("probe.input");std::string bytes;char b[4096];while(f){f.read(b,sizeof b);bytes.append(b,static_cast<std::size_t>(f.gcount()));if(bytes.size()>786433)throw protocol::Error("probe.size");}return bytes;}
}
int main(int argc,char** argv){try{
    if(argc!=4||::geteuid()==0)throw protocol::Error("probe.arguments");
    const std::string grants=argv[3];platform::RecoveryContext context{"editor:1","profile:primary",std::string(64,'4'),7,grants.find('r')!=std::string::npos,grants.find('w')!=std::string::npos,grants.find('e')!=std::string::npos};
    platform::LinuxRecoveryQueue queue(argv[1],argv[2],context);std::cout<<status(queue.status()).dump()<<std::endl;std::string line;
    while(std::getline(std::cin,line)){
        const auto input=Json::parse(line);const std::string op=input.at("op");Json answer;
        const auto start=std::chrono::steady_clock::now();
        try{
            if(op=="poll")answer=status(queue.poll());
            else if(op=="status")answer=status(queue.status());
            else if(op=="replace")answer={{"ticket",std::to_string(queue.replace(read(input.at("file"))))}};
            else if(op=="retire")answer={{"ticket",std::to_string(queue.retire())}};
            else if(op=="close"){queue.close();answer=status(queue.status());}
            else if(op=="wrong-thread"){
                std::string error;std::thread t([&]{try{queue.poll();}catch(const protocol::Error& e){error=e.what();}});t.join();answer={{"error",error}};
            }else if(op=="take"){
                const auto v=queue.take();answer=nullptr;
                if(v){answer={{"ticket",std::to_string(v->ticket)},{"operation",v->operation},{"outcome",v->outcome},{"error",v->error},{"digest",v->digest?Json(*v->digest):Json()},{"bytes",v->bytes?Json(v->bytes->size()):Json()},{"sha256",v->bytes?Json(configuration::sha256(*v->bytes)):Json()},{"pending",v->pending},
                    {"binding",{{"session",v->context.session},{"profile",v->context.profile},{"generation",v->context.generation},{"policy_revision",std::to_string(v->context.policy_revision)}}}};
                    if(v->bytes&&v->bytes->size()<=65536){std::string hex;constexpr char digits[]="0123456789abcdef";for(unsigned char b:*v->bytes){hex+=digits[b>>4];hex+=digits[b&15];}answer["hex"]=std::move(hex);}
                }
            }else if(op=="exit"){
                queue.close();const auto end=std::chrono::steady_clock::now()+std::chrono::seconds(3);
                while(!queue.poll().reaped){if(std::chrono::steady_clock::now()>=end)throw protocol::Error("probe.exit");std::this_thread::sleep_for(std::chrono::milliseconds(1));}
                std::cout<<Json({{"exit",true}}).dump()<<std::endl;return 0;
            }else throw protocol::Error("probe.operation");
        }catch(const std::exception& e){answer={{"error",e.what()}};}
        const auto us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start).count();std::cout<<Json({{"reply",answer},{"elapsed_us",us}}).dump()<<std::endl;
    }
    queue.close();while(!queue.poll().reaped)std::this_thread::sleep_for(std::chrono::milliseconds(1));return 0;
}catch(const std::exception& e){std::cout<<Json({{"error",e.what()}}).dump()<<std::endl;return 1;}}
