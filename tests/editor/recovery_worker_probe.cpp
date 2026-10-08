#include "recovery_worker_linux.hpp"
#include "recovery_channel.hpp"
#include "child.hpp"
#include <csignal>
#include <cstdlib>
#include <filesystem>
#include <sys/socket.h>
#include <unistd.h>
int main(int argc,char** argv){
    if(argc!=2)return 2;
    const auto parent=syspane::protocol::decimal(argv[1]);if(!parent||!*parent)return 2;
    const auto mode=std::filesystem::path(argv[0]).filename().string();
    if(mode=="worker-hung-worker"){syspane::platform::arm_parent_lifetime(*parent);::close(3);for(;;)::pause();}
    return syspane::platform::run_recovery_worker(*parent,[&](const char* phase){
        if(mode==std::string("worker-stop-")+phase)std::raise(SIGSTOP);
        if(mode=="worker-nonzero-after-result"&&std::string(phase)=="reply_sent")std::_Exit(9);
        if(mode=="worker-trailing-result"&&std::string(phase)=="reply_sent")::send(1,"x",1,MSG_NOSIGNAL);
    },[&](syspane::protocol::Json& header){
        if(mode=="worker-stale-grant"&&header["kind"]=="guard")header["guard"]="0";
        if(mode=="worker-forged-binding")header["binding"]["session"]="editor:old";
        if(mode=="worker-forged-ticket")header["ticket"]="999";
        if(header["kind"]=="result"&&mode=="worker-duplicate-result"){
            auto raw=syspane::platform::recovery_io::encode(header);std::size_t sent=0;
            while(sent<raw.size()){const auto n=::send(1,raw.data()+sent,raw.size()-sent,MSG_NOSIGNAL);if(n<=0)std::_Exit(8);sent+=static_cast<std::size_t>(n);}
        }
        if(header["kind"]=="result"&&mode=="worker-oversized-reply"){
            const unsigned size=819202;const char raw[]={static_cast<char>(size>>24),static_cast<char>(size>>16),static_cast<char>(size>>8),static_cast<char>(size)};::send(1,raw,4,MSG_NOSIGNAL);
        }
    });
}
