#include "helper_identity.hpp"
#include "profile_supervisor_linux.hpp"
#include "local_ipc.hpp"
#include "wire.hpp"
#include <cerrno>
#include <fcntl.h>
#include <iostream>
#include <sys/socket.h>
#include <thread>
#include <unistd.h>

namespace os=syspane::platform;namespace a=syspane::application;namespace p=syspane::protocol;
namespace {
void need(bool b,const char* error){if(!b)throw p::Error(error);}
struct Fd{int value=-1;~Fd(){if(value>=0)::close(value);}void close(){if(value>=0)::close(value);value=-1;}};
void emit(p::Json value){std::cout<<value.dump()<<std::endl;}
std::string control(){std::string value;need(static_cast<bool>(std::getline(std::cin,value)),"probe.control");return value;}
void launch(int fd){
    int pair[2],pipes[2];need(::socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC|SOCK_NONBLOCK,0,pair)==0,"probe.socket");
    Fd parent{pair[0]},remote{pair[1]};need(::pipe2(pipes,O_CLOEXEC|O_NONBLOCK)==0,"probe.pipe");Fd errors{pipes[0]},sink{pipes[1]};
    auto child=os::Child::launch_sealed(fd,"syspane-configuration-host",{std::to_string(os::current_process_id())},remote.value,remote.value,sink.value);
    remote.close();sink.close();emit({{"event","launched"},{"pid",child.id()}});
    need(control()=="finish","probe.control");const auto frame=p::frame("{}",32768);
    need(::send(parent.value,frame.data(),frame.size(),MSG_NOSIGNAL)==static_cast<ssize_t>(frame.size()),"probe.send");
    const auto exited=child.wait(2000);need(exited.has_value(),"probe.exit");char bytes[1025];const auto n=::read(errors.value,bytes,sizeof bytes);
    need(n>=0&&n<1025,"probe.diagnostic");emit({{"event","exited"},{"pid",child.id()},{"signaled",exited->signaled},{"code",exited->code},{"stderr",std::string(bytes,static_cast<std::size_t>(n))}});
}
}
int main(int argc,char** argv){
    try{
        if(argc==2&&p::decimal(argv[1])){std::cerr<<"substituted\n";return 42;}
        need(argc>=2&&argc<=4,"probe.arguments");const std::string mode=argv[1];
        const auto expected=os::built_helper_expectation();auto installation=std::make_shared<os::LinuxInstallation>(expected);
        const int borrowed=installation->verified_helper();errno=0;const auto write=::pwrite(borrowed,"X",1,0);const int error=errno;
        emit({{"event","verified"},{"root",installation->root()},{"record",expected.record_sha256},{"helper",expected.helper_sha256},
              {"bytes",expected.helper_bytes},{"seals",::fcntl(borrowed,F_GET_SEALS)},{"write",write},{"write_errno",error}});
        if(mode=="check")return 0;
        if(mode=="supervisor"){
            need(argc==4,"probe.arguments");os::ProfileLocation profile{"profile:installation","","","","",std::string(argv[3])};
            a::LinuxProfileSupervisor supervisor(installation,argv[2],profile,true,os::current_process_id());const auto start=os::monotonic_ms();
            bool closing=false;
            for(;;){
                const auto status=supervisor.poll();
                for(const auto& e:supervisor.take()){
                    emit({{"event",e.kind},{"pid",e.view.process},{"fault",e.view.fault},{"code",e.view.last_exit?p::Json(e.view.last_exit->code):p::Json()}});
                    if(e.kind=="launched")need(control()=="continue","probe.control");
                }
                if(!closing&&(!status.fault.empty()||os::monotonic_ms()-start>=8000)){supervisor.close();closing=true;}
                if(status.state==a::ProfileSupervisorState::closed)return 0;
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
        }
        need(mode=="hold","probe.arguments");const auto action=control();
        if(action=="verify"){(void)installation->verified_helper();emit({{"event","verified-again"}});return 0;}
        if(action=="verify-twice"){
            try{(void)installation->verified_helper();throw p::Error("probe.change_missed");}
            catch(const p::Error& e){emit({{"event","invalidated"},{"code",e.what()}});}
            need(control()=="again","probe.control");(void)installation->verified_helper();return 3;
        }
        if(action=="thread"){
            unsigned refused=0;std::thread worker([&]{
                try{installation->verified_helper();}catch(const p::Error& e){if(std::string(e.what())=="installation.owner")++refused;}
                try{installation->root();}catch(const p::Error& e){if(std::string(e.what())=="installation.owner")++refused;}
            });worker.join();need(refused==2,"probe.thread");emit({{"event","thread-refused"},{"count",refused}});return 0;
        }
        if(action=="mutable"){
            Fd file{::open((installation->root()+"/libexec/syspane/syspane-configuration-host").c_str(),O_RDONLY|O_CLOEXEC)};launch(file.value);return 3;
        }
        need(action=="launch"||action=="borrowed","probe.control");launch(action=="launch"?installation->verified_helper():borrowed);return 0;
    }catch(const std::exception& e){emit({{"event","error"},{"code",e.what()}});return 2;}
}
