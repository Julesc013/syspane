#include "bundle_identity.hpp"
#include "helper_identity.hpp"
#include "image_job.hpp"
#include "recovery_queue_linux.hpp"
#include "child.hpp"
#include "local_ipc.hpp"
#include "digest.hpp"
#include <array>
#include <cerrno>
#include <chrono>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <sys/socket.h>
#include <thread>
#include <tuple>
#include <unistd.h>

namespace os=syspane::platform;namespace p=syspane::protocol;namespace r=syspane::rendering;namespace c=syspane::configuration;
namespace {
void need(bool b,const char* code){if(!b)throw p::Error(code);}
void emit(const p::Json& value){std::cout<<value.dump()<<std::endl;}
std::string read(const std::string& path){std::ifstream f(path,std::ios::binary);need(static_cast<bool>(f),"probe.input");std::string result;char bytes[4096];while(f){f.read(bytes,sizeof bytes);result.append(bytes,static_cast<std::size_t>(f.gcount()));need(result.size()<=8388608,"probe.capacity");}return result;}
std::string hex(std::string_view raw){std::string out;for(unsigned char b:raw){out+="0123456789abcdef"[b>>4];out+="0123456789abcdef"[b&15];}return out;}
struct Fd{int value=-1;~Fd(){close();}void close(){if(value>=0)::close(value);value=-1;}};
const char* image_state(r::ImageJobState state){switch(state){case r::ImageJobState::running:return "running";case r::ImageJobState::stopping:return "stopping";case r::ImageJobState::ready:return "ready";case r::ImageJobState::failed:return "failed";case r::ImageJobState::cancelled:return "cancelled";case r::ImageJobState::consumed:return "consumed";}return "invalid";}
const char* recovery_state(os::RecoveryQueueState state){switch(state){case os::RecoveryQueueState::loading:return "loading";case os::RecoveryQueueState::ready:return "ready";case os::RecoveryQueueState::busy:return "busy";case os::RecoveryQueueState::retiring:return "retiring";case os::RecoveryQueueState::retired:return "retired";case os::RecoveryQueueState::unavailable:return "unavailable";case os::RecoveryQueueState::closing:return "closing";case os::RecoveryQueueState::closed:return "closed";}return "invalid";}
p::Json status(const os::RecoveryQueueStatus& s){return {{"state",recovery_state(s.state)},{"pid",s.process},{"reaped",s.reaped},{"error",s.error}};}
struct RawImage {
    Fd channel,errors;std::unique_ptr<os::Child> child;bool sandbox;
    RawImage(int fd,bool check):sandbox(check){
        int pair[2],pipes[2];need(!::socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0,pair),"probe.channel");channel.value=pair[0];Fd remote{pair[1]};
        need(!::fcntl(channel.value,F_SETFL,O_NONBLOCK),"probe.channel");
        need(!::pipe2(pipes,O_CLOEXEC|O_NONBLOCK),"probe.channel");errors.value=pipes[0];Fd sink{pipes[1]};
        child=std::make_unique<os::Child>(os::Child::launch_sealed(fd,"syspane-image-worker",{check?"--check-sandbox":"image/png",std::to_string(os::current_process_id())},remote.value,remote.value,sink.value));
    }
    p::Json finish(const std::string& input){
        if(!sandbox){need(input.size()<4096,"probe.capacity");const auto size=static_cast<unsigned>(input.size());std::string packet(4,'\0');for(unsigned n=0;n<4;++n)packet[n]=static_cast<char>(size>>(24-n*8));packet+=input;
            need(::send(channel.value,packet.data(),packet.size(),MSG_NOSIGNAL)==static_cast<ssize_t>(packet.size()),"probe.send");}
        need(!::shutdown(channel.value,SHUT_WR),"probe.shutdown");std::string output,diagnostics;bool eof=false,error_eof=false;std::optional<os::ChildExit> done;
        const auto start=os::monotonic_ms();
        while(!done||!eof||!error_eof){
            need(os::monotonic_ms()-start<5000,"probe.deadline");std::array<char,8192> b{};
            for(auto tuple:{std::make_tuple(channel.value,&output,&eof),std::make_tuple(errors.value,&diagnostics,&error_eof)}){
                if(*std::get<2>(tuple))continue;
                const auto n=::read(std::get<0>(tuple),b.data(),b.size());
                if(n>0)std::get<1>(tuple)->append(b.data(),static_cast<std::size_t>(n));else if(!n)*std::get<2>(tuple)=true;else need(errno==EAGAIN||errno==EWOULDBLOCK||errno==EINTR,"probe.read");
            }
            need(output.size()<=65536&&diagnostics.size()<=1024,"probe.capacity");done=child->wait();std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        return {{"pid",child->id()},{"signaled",done->signaled},{"code",done->code},{"output",hex(output)},{"stderr",diagnostics}};
    }
};
}
int main(int argc,char** argv){try{
    need(argc==2&&os::unprivileged_context(),"probe.arguments");const std::string mode=argv[1];need(mode=="bundle"||mode=="legacy","probe.arguments");
    auto owner=mode=="bundle"?std::make_shared<os::LinuxInstallation>(os::built_helper_bundle_expectation()):std::make_shared<os::LinuxInstallation>(os::built_helper_expectation());
    p::Json roles=p::Json::array();std::array<int,3> descriptors{{-1,-1,-1}};
    for(unsigned i=0;i<(mode=="bundle"?3u:1u);++i){const int fd=owner->verified_helper(static_cast<os::HelperKind>(i));descriptors[i]=fd;errno=0;const auto written=::pwrite(fd,"X",1,0);const auto error=errno;
        roles.push_back({{"role",i},{"fd",fd},{"seals",::fcntl(fd,F_GET_SEALS)},{"write",written},{"write_errno",error}});}
    emit({{"event","ready"},{"root",owner->root()},{"roles",roles}});
    std::unique_ptr<r::ImageJob> image;std::unique_ptr<os::LinuxRecoveryQueue> recovery;std::unique_ptr<RawImage> raw;
    std::string line;
    while(std::getline(std::cin,line)){
        try{
            need(line.size()<=65536,"probe.capacity");const auto q=p::Json::parse(line);const std::string op=q.at("op");p::Json reply;
            if(op=="verify"){const int fd=owner->verified_helper(static_cast<os::HelperKind>(q.at("role").get<int>()));reply={{"fd",fd}};}
            else if(op=="thread"){
                unsigned refused=0;std::thread other([&]{for(int i=0;i<3;++i)try{owner->verified_helper(static_cast<os::HelperKind>(i));}catch(const p::Error& e){if(std::string(e.what())=="installation.owner")++refused;}});other.join();reply={{"refused",refused}};
            }else if(op=="image"){
                need(!image,"probe.active");image=std::make_unique<r::ImageJob>(owner,q.at("media"),read(q.at("file")));reply={{"pid",image->process_id()}};
            }else if(op=="image-poll"){
                need(static_cast<bool>(image),"probe.image");const auto s=image->poll();reply={{"pid",image->process_id()},{"state",image_state(s.state)},{"reaped",s.reaped},{"reason",s.reason}};
            }else if(op=="image-take"){
                need(static_cast<bool>(image),"probe.image");auto pixels=image->take();need(pixels.rgba.size()<=65536,"probe.capacity");reply={{"width",pixels.width},{"height",pixels.height},{"rgba",pixels.rgba}};image.reset();
            }else if(op=="image-reset"){if(image){image->cancel();while(!image->poll().reaped)std::this_thread::sleep_for(std::chrono::milliseconds(1));image.reset();}reply={{"closed",true}};
            }else if(op=="raw-image"||op=="sandbox"){
                need(!raw,"probe.active");raw=std::make_unique<RawImage>(op=="raw-image"?descriptors[1]:owner->verified_helper(os::HelperKind::image),op=="sandbox");reply={{"pid",raw->child->id()}};
            }else if(op=="raw-finish"){need(static_cast<bool>(raw),"probe.raw");reply=raw->finish(q.contains("file")?read(q.at("file")):std::string{});raw.reset();
            }else if(op=="recovery"){
                need(!recovery,"probe.active");recovery=std::make_unique<os::LinuxRecoveryQueue>(owner,q.at("directory"),os::RecoveryContext{"editor:bundle","profile:primary",std::string(64,'4'),7,true,true,true});reply=status(recovery->status());
            }else if(op=="recovery-poll"){need(static_cast<bool>(recovery),"probe.recovery");reply=status(recovery->poll());
            }else if(op=="recovery-take"){
                need(static_cast<bool>(recovery),"probe.recovery");const auto done=recovery->take();reply=nullptr;
                if(done)reply={{"operation",done->operation},{"outcome",done->outcome},{"error",done->error},{"bytes",done->bytes?p::Json(*done->bytes):p::Json()},{"digest",done->digest?p::Json(*done->digest):p::Json()},{"pending",done->pending}};
            }else if(op=="replace"){need(static_cast<bool>(recovery),"probe.recovery");reply={{"ticket",recovery->replace(read(q.at("file")))}};
            }else if(op=="retire"){need(static_cast<bool>(recovery),"probe.recovery");reply={{"ticket",recovery->retire()}};
            }else if(op=="recovery-close"){need(static_cast<bool>(recovery),"probe.recovery");recovery->close();reply=status(recovery->status());
            }else if(op=="recovery-reset"){
                if(recovery){recovery->close();while(!recovery->poll().reaped)std::this_thread::sleep_for(std::chrono::milliseconds(1));recovery.reset();}reply={{"closed",true}};
            }else if(op=="quit"){need(!image&&!raw&&!recovery,"probe.active");emit({{"exit",true}});return 0;}
            else throw p::Error("probe.operation");
            emit(reply);
        }catch(const std::exception& e){emit({{"error",e.what()}});}
    }
    return 2;
}catch(const std::exception& e){emit({{"error",e.what()}});return 2;}}
