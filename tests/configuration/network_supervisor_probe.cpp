#include "profile_supervisor_linux.hpp"
#include "bundle_identity.hpp"
#include "wire.hpp"
#include "local_ipc.hpp"
#include <iostream>
#include <poll.h>
#include <thread>
#include <unistd.h>

int main(int argc,char** argv){
    namespace a=syspane::application;namespace os=syspane::platform;namespace p=syspane::protocol;
    try{
        if(argc!=3)return 2;
        const auto client=p::decimal(argv[2]);if(!client||!*client)return 2;
        auto installation=std::make_shared<os::LinuxInstallation>(os::built_helper_bundle_expectation());
        a::LinuxProfileSupervisor supervisor(installation,argv[1],{},false,*client,a::LocalService::network);
        const auto started=os::monotonic_ms();
        for(;;){
            pollfd input{STDIN_FILENO,POLLIN,0};if(::poll(&input,1,0)<0)return 3;
            if(input.revents&(POLLIN|POLLHUP))supervisor.close();
            if(os::monotonic_ms()-started>45000)supervisor.close();
            const auto view=supervisor.poll();
            for(const auto& event:supervisor.take()){
                const auto& v=event.view;
                std::cout<<p::Json{{"event",event.kind},{"observed_ms",event.observed_ms},{"pid",v.process},{"epoch",v.epoch},
                    {"endpoint",v.endpoint},{"generation",v.generation},{"fault",v.fault},
                    {"exit",v.last_exit?p::Json{{"signaled",v.last_exit->signaled},{"code",v.last_exit->code}}:p::Json()}}.dump()<<std::endl;
            }
            if(view.state==a::ProfileSupervisorState::closed)return 0;
            if(view.state==a::ProfileSupervisorState::unavailable||view.state==a::ProfileSupervisorState::circuit_open)return 4;
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
