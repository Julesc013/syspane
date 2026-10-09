#include "network_consumer_linux.hpp"
#include "profile_supervisor_linux.hpp"
#include "bundle_identity.hpp"
#include "local_ipc.hpp"
#include <atomic>
#include <iostream>
#include <mutex>
#include <poll.h>
#include <thread>
#include <unistd.h>
namespace a=syspane::application;namespace p=syspane::protocol;namespace os=syspane::platform;namespace c=syspane::configuration;
std::mutex output;std::atomic<bool> wanted{true},done{false},failed{false};
void emit(p::Json value){std::lock_guard<std::mutex> lock(output);std::cout<<value.dump()<<std::endl;}
c::Policy policy(){c::Policy v;v.available=true;v.revision=7;for(const char* channel:{"inspector","accessibility"})v.disclosure[{"console",channel}]={"operational"};return v;}
void consume(const std::string& endpoint,std::uint64_t process,const std::string& epoch){
    try{
        a::LinuxNetworkConsumer consumer(endpoint,process,epoch,{11,4},policy(),[]{return wanted.load();});
        std::shared_ptr<const syspane::recovery::DeliveredFrame> previous;
        while(wanted){
            const auto v=consumer.poll();
            if(v.frame&&v.frame!=previous){
                emit({{"event","frame"},{"raw",v.frame->bytes},{"epoch",v.binding->epoch},{"profile",v.scope.profile},{"generation",v.scope.generation},
                    {"receipt_ms",v.frame->received_ms},{"receipt_ns",std::to_string(v.frame->received_tick.nanoseconds)},
                    {"clock_ms",v.clock_ms},{"clock_ns",std::to_string(v.clock->nanoseconds)},{"deadline",v.live_until_ms}});previous=v.frame;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }
    }catch(const std::exception& e){if(wanted){failed=true;emit({{"event","fault"},{"code",e.what()}});}}
    done=true;
}
bool close_requested(){pollfd pfd{STDIN_FILENO,POLLIN,0};return ::poll(&pfd,1,0)>0&&(pfd.revents&(POLLIN|POLLHUP));}
int main(int argc,char** argv){
    std::thread worker;
    try{
        if(argc==5&&std::string(argv[1])=="--peer"){
            const auto peer=p::decimal(argv[3]);if(!peer||!*peer)return 2;
            worker=std::thread(consume,argv[2],*peer,argv[4]);const auto started=os::monotonic_ms();
            while(!done){if(close_requested()||os::monotonic_ms()-started>12000)wanted=false;std::this_thread::sleep_for(std::chrono::milliseconds(1));}
            worker.join();return failed?1:0;
        }
        if(argc!=3)return 2;
        auto installation=std::make_shared<os::LinuxInstallation>(os::built_helper_bundle_expectation());
        a::LinuxProfileSupervisor supervisor(installation,argv[1],{},false,static_cast<std::uint64_t>(::getpid()),a::LocalService::network);
        const auto started=os::monotonic_ms();
        for(;;){
            if(close_requested()||done||os::monotonic_ms()-started>15000){wanted=false;supervisor.close();}
            const auto state=supervisor.poll();
            for(const auto& e:supervisor.take()){
                emit({{"event",e.kind},{"pid",e.view.process},{"epoch",e.view.epoch},{"exit",e.view.last_exit?p::Json(e.view.last_exit->code):p::Json()}});
                if(e.kind=="ready"&&!worker.joinable())worker=std::thread(consume,e.view.endpoint,e.view.process,e.view.epoch);
            }
            if(state.state==a::ProfileSupervisorState::closed)break;
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        wanted=false;if(worker.joinable())worker.join();return 0;
    }catch(const std::exception& e){wanted=false;if(worker.joinable())worker.join();std::cerr<<e.what()<<'\n';return 2;}
}
