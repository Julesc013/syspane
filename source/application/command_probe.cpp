#include "async_commands.hpp"
#include "generation_store_linux.hpp"
#include "local_ipc.hpp"
#include "session.hpp"
#include <array>
#include <atomic>
#include <condition_variable>
#include <csignal>
#include <iostream>
#include <thread>
#include <poll.h>
#include <unistd.h>

namespace c=syspane::configuration;namespace p=syspane::protocol;namespace os=syspane::platform;using p::Json;
std::mutex output;
void emit(Json v){std::lock_guard<std::mutex> lock(output);std::cout<<v.dump()<<std::endl;}
struct Gate {
    std::mutex mutex;std::condition_variable condition;bool released=false;
    void release(){std::lock_guard<std::mutex> lock(mutex);released=true;condition.notify_all();}
    void wait(const char* phase){
        emit({{"event","held"},{"phase",phase}});std::unique_lock<std::mutex> lock(mutex);
        if(!condition.wait_for(lock,std::chrono::seconds(8),[&]{return released;}))throw p::Error("probe.gate_timeout");
    }
};
int main(int argc,char** argv){try{
    if(argc<5||argc>7||!os::unprivileged_context())throw p::Error("probe.arguments");
    const std::string phase=argv[3];const auto expected=p::decimal(argv[4]);
    const std::string epoch=argc>=6?argv[5]:"E1",permission=argc>=7?argv[6]:"allow";
    if(!expected||!*expected||!p::identifier(epoch)||(permission!="allow"&&permission!="deny")||
       (phase!="preparing"&&phase!="permitted"&&phase!="plain"&&phase!="crash-before"&&phase!="crash-durable"))throw p::Error("probe.arguments");
    Gate gate;
    os::LinuxGenerationStore store(argv[2],[&](const char* step){
        if(phase=="permitted"&&std::string(step)=="authorized")gate.wait("permitted");
        if((phase=="crash-before"&&std::string(step)=="selector_ready")||(phase=="crash-durable"&&std::string(step)=="durable")){
            emit({{"event","held"},{"phase",phase}});std::raise(SIGSTOP);
        }
    });
    auto owner=std::make_shared<c::AsyncCommands>(store,epoch,[&](const c::Authored& value){
        if(value.settings["display"]["theme_id"]!="theme:native"||(!value.scene["theme_id"].is_null()&&value.scene["theme_id"]!="theme:native"))throw p::Error("resource.unavailable");
        if(phase=="preparing")gate.wait("preparing");
    });
    c::Policy policy;policy.available=true;policy.revision=epoch=="E1"?7:8;if(permission=="deny")policy.denied_capabilities.insert("scene.replace");
    c::Sessions sessions(epoch,c::authored_revision(store.load().documents),policy,{},owner);
    os::Listener listener(argv[1]);std::optional<os::Stream> stream;std::unique_ptr<p::Framer> decoder;
    std::thread worker;std::optional<c::AsyncCommands::Completion> completion;std::exception_ptr worker_error;std::atomic<bool> done{false};
    const auto stop=[&]{owner->invalidate();gate.release();if(worker.joinable())worker.join();};
    emit({{"event","ready"},{"access_controls_verified",listener.access_controls_verified()},{"recovered_previous",store.recovered_previous()}});
    const auto start=os::monotonic_ms();bool stopping=false;
    try{
        while(!stopping){
            if(os::monotonic_ms()-start>20000)throw p::Error("probe.deadline");
            pollfd control{STDIN_FILENO,POLLIN,0};
            if(::poll(&control,1,0)>0){
                if(control.revents&POLLHUP)throw p::Error("probe.parent_lost");
                if(control.revents&POLLIN){
                    std::string line;std::getline(std::cin,line);
                    if(line=="release")gate.release();
                    else if(line=="revoke"){policy.revision=8;policy.denied_capabilities.insert("settings.commit");sessions.policy(policy,os::monotonic_ms());emit({{"event","revoked"}});}
                    else if(line=="stop")stopping=true;
                    else throw p::Error("probe.control");
                }
            }
            if(done.load(std::memory_order_acquire)){
                worker.join();if(worker_error)std::rethrow_exception(worker_error);
                if(!owner->finish(std::move(*completion),os::monotonic_ms(),true))throw p::Error("probe.finish");
                completion.reset();done.store(false,std::memory_order_relaxed);emit({{"event","joined"},{"revision",owner->revision()}});
            }
            if(!stream){
                stream=listener.accept_ready(*expected);
                if(stream){sessions.open("C",stream->peer().principal,{true,"console",{"console"}},os::monotonic_ms());decoder=std::make_unique<p::Framer>();
                    emit({{"event","authenticated"},{"peer_pid",stream->peer().process_id}});}
            }
            if(stream){
                std::array<char,4096> buffer{};const auto read=stream->read(buffer.data(),buffer.size(),10);
                if(read.eof){decoder->eof();sessions.disconnect("C");stream.reset();decoder.reset();emit({{"event","disconnected"}});}
                else{
                    if(read.bytes)decoder->feed(std::string_view(buffer.data(),read.bytes),read.observed_ms,[&](auto payload){sessions.receive("C",payload,os::monotonic_ms());decoder->restrict_limit(sessions.frame_bound("C"));});
                    decoder->tick(os::monotonic_ms());sessions.tick(os::monotonic_ms());
                    if(sessions.closed("C"))throw p::Error("probe.session_closed");
                    while(auto payload=sessions.pop("C",os::monotonic_ms()))stream->write(p::frame(*payload),100);
                }
            }else std::this_thread::sleep_for(std::chrono::milliseconds(2));
            if(!worker.joinable()&&!stopping)if(auto ticket=owner->take()){
                worker=std::thread([&,ticket=*ticket]{try{completion.emplace(owner->run(ticket));}catch(...){worker_error=std::current_exception();}done.store(true,std::memory_order_release);});
            }
        }
    }catch(...){stop();throw;}
    stop();emit({{"event","stopped"},{"revision",c::authored_revision(store.load().documents)}});return 0;
}catch(const std::exception& e){emit({{"event","error"},{"code",e.what()}});return 1;}}
