#include "profile_supervisor_linux.hpp"
#include "profile_controller_linux.hpp"
#include "health_link.hpp"
#include <fstream>
#include <cerrno>
#include <fcntl.h>
#include <iostream>
#include <poll.h>
#include <thread>
#include <unistd.h>

namespace a=syspane::application;namespace os=syspane::platform;namespace r=syspane::recovery;namespace p=syspane::protocol;
namespace {
p::Json read(const std::string& path){std::ifstream file(path);p::Json value;file>>value;return value;}
void forever(){for(;;)std::this_thread::sleep_for(std::chrono::milliseconds(10));}
const char* state(a::ProfileSupervisorState s){
    switch(s){
    case a::ProfileSupervisorState::starting:return "starting";case a::ProfileSupervisorState::ready:return "ready";
    case a::ProfileSupervisorState::quarantined:return "quarantined";case a::ProfileSupervisorState::waiting:return "waiting";
    case a::ProfileSupervisorState::circuit_open:return "circuit_open";case a::ProfileSupervisorState::unavailable:return "unavailable";
    case a::ProfileSupervisorState::closing:return "closing";case a::ProfileSupervisorState::closed:return "closed";
    }return "invalid";
}
p::Json view(const a::ProfileSupervisorView& v){
    return {{"state",state(v.state)},{"generation",v.generation},{"pid",v.process},{"epoch",v.epoch},{"endpoint",v.endpoint},
        {"fault",v.fault},{"restarts",v.restart.restarts_in_window},{"backoff_ms",v.restart.backoff_ms},
        {"exit",v.last_exit?p::Json{{"signaled",v.last_exit->signaled},{"code",v.last_exit->code}}:p::Json()}};
}
void emit(const char* kind,const a::ProfileSupervisorView& v,std::uint64_t at,std::uint64_t ticket=0){
    auto value=view(v);value["event"]=kind;value["observed_ms"]=at;value["ticket"]=ticket;std::cout<<value.dump()<<std::endl;
}
int child(const std::string& path,std::uint64_t parent){
    const auto initial=read(path);const std::string mode=initial.at("mode");
    if(mode=="real"){
        return a::run_profile_controller(parent,[&]{
            const auto current=read(path);syspane::configuration::Policy policy;policy.available=current.value("allow",true);policy.revision=7;return policy;
        },[&](const std::string& phase){
            if(phase!=initial.value("phase",std::string{}))return;
            std::ofstream(path+".held")<<phase;
            while(!read(path).value("release",false))std::this_thread::sleep_for(std::chrono::milliseconds(5));
        });
    }
    os::arm_parent_lifetime(parent);::close(3);
    if(mode=="startup")forever();
    auto stream=os::Stream::from_connected_socket(0,parent);p::Framer frames(32768);std::optional<p::Json> bootstrap;
    while(!bootstrap){char bytes[4096];const auto got=stream.read(bytes,sizeof bytes,10);if(got.eof)return 2;
        frames.feed({bytes,got.bytes},got.observed_ms,[&](auto raw){bootstrap=p::parse(raw);});}
    if(mode=="malformed"){stream.write(std::string("\0\0\0\1!",5));forever();}
    if(mode=="stderr"){std::cerr<<std::string(1025,'X')<<std::flush;forever();}
    os::Listener listener(bootstrap->at("endpoint"));
    r::HealthLink link(stream,false,"console",mode=="epoch"?"wrong":bootstrap->at("producer_epoch").get<std::string>(),"",true);
    std::uint64_t sequence=0,last=0,ticket=0;bool pending=false;
    for(;;){
        for(const auto& e:link.poll(5)){
            if(e.kind==r::HealthKind::ready&&mode=="zero")return 0;
            if(e.kind==r::HealthKind::shutdown){if(mode=="blocked-close")forever();return 0;}
            if(e.kind==r::HealthKind::transaction_armed&&mode=="flood"){link.transaction_finished(e.value);pending=false;}
        }
        const auto now=os::monotonic_ms();
        if(link.ready()&&mode!="heartbeat"&&(!sequence||now-last>=500)){
            link.heartbeat(sequence++);last=now;std::ofstream(path+".beats")<<sequence;
        }
        if(link.ready()&&!pending&&(mode=="operation"||mode=="flood")){link.transaction_started(++ticket);pending=true;}
    }
}
}
int main(int argc,char** argv){
    try{
        if(argc==2){const auto parent=p::decimal(argv[1]);if(!parent||!*parent)return 2;return child(std::string(argv[0])+".fixture",*parent);}
        if(argc!=6)return 2;
        const auto console=p::decimal(argv[4]);if(!console)return 2;
        os::ProfileLocation location{"profile:supervisor","","","","",std::string(argv[3])};
        a::LinuxProfileSupervisor supervisor(argv[1],argv[2],location,true,*console);const std::string mode=argv[5];
        if(mode=="preclose")supervisor.close();
        if(mode=="wrongthread"){
            unsigned refused=0;std::thread other([&]{
                try{supervisor.status();}catch(const p::Error& e){if(std::string(e.what())=="supervisor.owner")++refused;}
                try{supervisor.close();}catch(const p::Error& e){if(std::string(e.what())=="supervisor.owner")++refused;}
            });other.join();if(refused!=2)return 3;std::cout<<p::Json{{"event","thread-refused"},{"count",refused}}.dump()<<std::endl;
        }
        bool drain=mode!="hold-events";auto previous=supervisor.status();const auto started=os::monotonic_ms();std::string input_bytes;
        if(::fcntl(STDIN_FILENO,F_SETFL,O_NONBLOCK)<0)return 3;
        for(;;){
            pollfd input{STDIN_FILENO,POLLIN,0};if(::poll(&input,1,0)<0)return 3;
            if(input.revents&POLLIN){
                char bytes[128];const auto n=::read(STDIN_FILENO,bytes,sizeof bytes);
                if(n>0)input_bytes.append(bytes,static_cast<std::size_t>(n));
                else if(n<0&&errno!=EINTR&&errno!=EAGAIN)return 3;
                if(input_bytes.size()>1024)return 3;
                for(auto end=input_bytes.find('\n');end!=std::string::npos;end=input_bytes.find('\n')){
                    const auto line=input_bytes.substr(0,end);input_bytes.erase(0,end+1);
                    if(line=="close")supervisor.close();else if(line=="drain")drain=true;else return 3;
                }
            }
            if(input.revents&POLLHUP)supervisor.close();
            if(os::monotonic_ms()-started>90000)supervisor.close();
            const auto current=supervisor.poll();
            if(drain)for(const auto& e:supervisor.take())emit(e.kind.c_str(),e.view,e.observed_ms,e.ticket);
            if(current.state!=previous.state||current.fault!=previous.fault||current.process!=previous.process)emit("view",current,os::monotonic_ms());
            previous=current;
            if(current.state==a::ProfileSupervisorState::closed)return 0;
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
