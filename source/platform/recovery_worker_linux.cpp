#include "recovery_worker_linux.hpp"
#include "recovery_channel.hpp"
#include "recovery_store_linux.hpp"
#include "child.hpp"
#include "local_ipc.hpp"
#include "digest.hpp"
#include <array>
#include <cerrno>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

namespace syspane::platform {
namespace {
using namespace recovery_io;
class Channel {
    std::uint64_t started_=monotonic_ms();
    protocol::Framer framer_{frame_limit};
    void wait(short events){
        const auto now=monotonic_ms();need(now-started_<5000,"recovery_queue.timeout");
        pollfd fd{events==POLLIN?0:1,events,0};const auto n=::poll(&fd,1,static_cast<int>(5000-(now-started_)));
        need(n>=0||errno==EINTR,"recovery_queue.channel");need(n!=0,"recovery_queue.timeout");
    }
public:
    void send(const Json& h,std::string_view bytes={}){
        const auto raw=encode(h,bytes);std::size_t offset=0;
        while(offset<raw.size()){
            wait(POLLOUT);const auto n=::send(1,raw.data()+offset,raw.size()-offset,MSG_NOSIGNAL|MSG_DONTWAIT);
            if(n<0&&(errno==EINTR||errno==EAGAIN||errno==EWOULDBLOCK))continue;
            need(n>0,"recovery_queue.channel");offset+=static_cast<std::size_t>(n);
        }
    }
    Packet receive(){
        std::optional<Packet> packet;std::array<char,8192> buffer{};
        while(!packet){
            wait(POLLIN);const auto n=::recv(0,buffer.data(),buffer.size(),MSG_DONTWAIT);
            if(n<0&&(errno==EINTR||errno==EAGAIN||errno==EWOULDBLOCK))continue;
            need(n>0,"recovery_queue.channel");framer_.feed({buffer.data(),static_cast<std::size_t>(n)},monotonic_ms(),[&](auto raw){need(!packet,"recovery_queue.trailing");packet=decode(raw);});
        }
        need(framer_.buffered()==0,"recovery_queue.trailing");return std::move(*packet);
    }
    void no_trailing(){char byte;const auto n=::recv(0,&byte,1,MSG_DONTWAIT|MSG_PEEK);need(n<0&&(errno==EAGAIN||errno==EWOULDBLOCK),"recovery_queue.trailing");}
};
std::string code(const std::exception& e){const Json v=e.what();return error_code(v)&&!v.get_ref<const std::string&>().empty()?v.get<std::string>():"recovery_queue.worker";}
}
int run_recovery_worker(std::uint64_t parent,const std::function<void(const char*)>& transition,const std::function<void(Json&)>& outgoing){
    try{
        arm_parent_lifetime(parent);::close(3);Channel channel;const auto input=channel.receive();request(input);
        auto result=stamp(input.header,"result");result.update({{"outcome","unchanged"},{"error",""},{"digest",nullptr},{"present",false},{"pending",false}});std::string body;
        unsigned sequence=0;const auto guard=[&]{
            need(++sequence<=8,"recovery_queue.guard");auto ask=stamp(input.header,"guard");ask["guard"]=std::to_string(sequence);if(outgoing)outgoing(ask);channel.send(ask);
            const auto answer=channel.receive();const auto& h=answer.header;
            need(answer.bytes.empty()&&protocol::members(h,{"kind","binding","ticket","operation","guard","allow"})&&h["kind"]=="grant"&&matches(h,input.header)&&h["guard"]==std::to_string(sequence)&&h["allow"].is_boolean(),"recovery_queue.guard");return h["allow"].get<bool>();
        };
        try{
            LinuxRecoveryStore store(input.header["root"],transition);auto before=store.snapshot(guard);
            if(input.header["operation"]=="load"){
                result["outcome"]="loaded";result["present"]=before.bytes.has_value();result["pending"]=before.pending;result["digest"]=before.version.digest?Json(*before.version.digest):Json();
                if(before.bytes)body=std::move(*before.bytes);
            }else{
                need((before.version.digest?Json(*before.version.digest):Json())==input.header["expected"],"recovery_store.conflict");
                const bool replace=input.header["operation"]=="replace";
                const auto v=replace?store.replace(before.version,input.bytes,guard):store.retire(before.version,guard);
                result["outcome"]=v.outcome==configuration::Publication::durable?"durable":v.outcome==configuration::Publication::unknown?"unknown":"unchanged";result["error"]=v.error;
                if(v.outcome==configuration::Publication::durable&&replace){result["digest"]=configuration::sha256(input.bytes);result["present"]=true;}
            }
        }catch(const std::exception& e){result["error"]=code(e);}
        channel.no_trailing();if(outgoing)outgoing(result);channel.send(result,body);if(transition)transition("reply_sent");return 0;
    }catch(...){return 2;}
}
}
