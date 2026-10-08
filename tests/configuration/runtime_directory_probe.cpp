#include "runtime_directory_linux.hpp"
#include "profile_supervisor_linux.hpp"
#include "local_ipc.hpp"
#include "wire.hpp"
#include <iostream>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>

namespace os=syspane::platform;namespace a=syspane::application;namespace p=syspane::protocol;
namespace {
p::Json input(){std::string line;if(!std::getline(std::cin,line)||line.size()>4096)throw p::Error("probe.input");return p::parse(line);}
void emit(p::Json value){std::cout<<value.dump()<<std::endl;}
std::string refused(os::LinuxRuntimeDirectory& value){try{value.cleanup();return "removed";}catch(const p::Error& e){return e.what();}}
void supervise(os::LinuxRuntimeDirectory& runtime,const p::Json& value){
    os::ProfileLocation profile{"profile:runtime","","","","",value.at("profile").get<std::string>()};
    auto supervisor=std::make_unique<a::LinuxProfileSupervisor>(value.at("helper").get<std::string>(),runtime.path(),profile,true,static_cast<std::uint64_t>(::getpid()));
    const auto start=os::monotonic_ms();auto status=supervisor->status();
    while(status.state!=a::ProfileSupervisorState::ready){
        if(os::monotonic_ms()-start>=6000)throw p::Error("probe.startup");
        status=supervisor->poll();supervisor->take();std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    emit({{"event","ready"},{"pid",status.process},{"cleanup",refused(runtime)}});
    if(input().at("op")!="proceed")throw p::Error("probe.proceed");
    supervisor->close();const auto closing=os::monotonic_ms();
    while(status.state!=a::ProfileSupervisorState::closed){
        if(os::monotonic_ms()-closing>=6000)throw p::Error("probe.close");
        status=supervisor->poll();supervisor->take();std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    if(!status.last_exit)throw p::Error("probe.exit");
    emit({{"event","closed"},{"code",status.last_exit->code},{"signaled",status.last_exit->signaled},
          {"elapsed_ms",os::monotonic_ms()-closing},{"cleanup",refused(runtime)}});
    supervisor.reset();runtime.cleanup();emit({{"event","retired"}});
}
}
int main(){
    try{
        const auto initial=input();const auto mask=static_cast<mode_t>(initial.value("umask",0077));::umask(mask);
        std::unique_ptr<os::LinuxRuntimeDirectory> runtime;
        try{runtime=std::make_unique<os::LinuxRuntimeDirectory>(initial.at("base"));}
        catch(const p::Error& e){emit({{"ok",false},{"error",e.what()},{"umask_unchanged",::umask(mask)==mask}});return 0;}
        emit({{"event","created"},{"path",runtime->path()},{"umask_unchanged",::umask(mask)==mask}});
        for(;;){
            const auto request=input();const std::string op=request.at("op");
            try{
                if(op=="path")emit({{"ok",true},{"path",runtime->path()}});
                else if(op=="cleanup"){runtime->cleanup();emit({{"ok",true}});}
                else if(op=="destroy"){runtime.reset();emit({{"event","destroyed"}});return 0;}
                else if(op=="owner"){
                    p::Json errors=p::Json::array();std::thread other([&]{
                        try{runtime->path();}catch(const p::Error& e){errors.push_back(e.what());}
                        try{runtime->cleanup();}catch(const p::Error& e){errors.push_back(e.what());}
                    });other.join();emit({{"errors",errors}});
                }else if(op=="supervise")supervise(*runtime,request);
                else throw p::Error("probe.operation");
            }catch(const p::Error& e){emit({{"ok",false},{"error",e.what()}});}
        }
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
