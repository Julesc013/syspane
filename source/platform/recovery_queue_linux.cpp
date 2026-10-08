#include "recovery_queue_linux.hpp"
#include "recovery_channel.hpp"
#include "child.hpp"
#include "local_ipc.hpp"
#include "digest.hpp"
#include <array>
#include <cerrno>
#include <fcntl.h>
#include <limits>
#include <sys/socket.h>
#include <thread>
#include <unistd.h>

namespace syspane::platform {
namespace {
using namespace recovery_io;
struct Fd {int value=-1;~Fd(){close();}void close(){if(value>=0)::close(value);value=-1;}};
void erase(std::string& s){std::string{}.swap(s);}
struct Call {bool& active;explicit Call(bool& flag):active(flag){need(!active,"recovery_queue.reentrant");active=true;}~Call(){active=false;}};
Json binding(const RecoveryContext& c){return {{"session",c.session},{"profile",c.profile},{"generation",c.generation},{"policy_revision",std::to_string(c.policy_revision)}};}
}
struct LinuxRecoveryQueue::Impl {
    struct Job {std::uint64_t ticket;std::string operation,bytes;std::optional<std::string> digest;};
    std::string worker,path;RecoveryContext context;Json identity;
    std::thread::id owner=std::this_thread::get_id();mutable bool calling=false;
    std::uint64_t tickets=1,started=0;unsigned guards=0;
    bool initialized=false,sealed=false,closed=false,fault=false,eof=false,error_eof=false;
    RecoveryQueueState state=RecoveryQueueState::loading;std::string error;
    std::optional<Job> active,pending=Job{1,"load",{},{} };
    std::optional<std::string> expected;
    std::optional<RecoveryCompletion> completion,stopped;
    std::unique_ptr<Child> child;Fd channel,errors;
    protocol::Framer framer{frame_limit};std::string output,diagnostics;std::size_t sent=0;
    Json request;std::optional<Packet> reply;
    void check()const{need(std::this_thread::get_id()==owner,"recovery_queue.owner");}
    bool permitted(const std::string& operation)const{return !closed&&!fault&&(operation=="load"?context.read:operation=="replace"?context.retain:context.erase);}
    RecoveryQueueStatus view()const{
        std::size_t bytes=output.size()+diagnostics.size()+framer.buffered();
        if(pending)bytes+=pending->bytes.size();
        if(active)bytes+=active->bytes.size();
        if(reply)bytes+=reply->bytes.size();
        if(completion&&completion->bytes)bytes+=completion->bytes->size();
        return {state,active?active->ticket:0,pending?pending->ticket:0,child?child->id():0,bytes,!child,error};
    }
    void buffers(){erase(output);erase(diagnostics);sent=0;framer=protocol::Framer(frame_limit);reply.reset();completion.reset();pending.reset();if(active)erase(active->bytes);}
    void stop(const char* why,bool closing=false){
        if(closing)closed=true;else fault=true;
        if(closed)stopped.reset();
        else if(active)stopped=RecoveryCompletion{context,active->ticket,active->operation,active->operation=="load"?"unchanged":"unknown",why,{},{},false};
        error=why;buffers();channel.close();errors.close();
        state=closed?(child?RecoveryQueueState::closing:RecoveryQueueState::closed):RecoveryQueueState::unavailable;
        if(child)child->request_stop();
        else{active.reset();if(!closed){completion=std::move(stopped);stopped.reset();}}
    }
    void start(){
        need(!child&&!active&&pending,"recovery_queue.owner");active=std::move(pending);pending.reset();
        request={{"kind","request"},{"binding",identity},{"ticket",std::to_string(active->ticket)},{"operation",active->operation},{"root",path},{"expected",expected?Json(*expected):Json()}};
        output=encode(request,active->bytes);erase(active->bytes);sent=0;guards=0;reply.reset();framer=protocol::Framer(frame_limit);eof=error_eof=false;
        int sockets[2],pipes[2];need(::socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0,sockets)==0,"recovery_queue.channel");Fd remote;remote.value=sockets[1];channel.value=sockets[0];
        need(::pipe2(pipes,O_CLOEXEC)==0,"recovery_queue.channel");Fd remote_errors;remote_errors.value=pipes[1];errors.value=pipes[0];
        need(::fcntl(channel.value,F_SETFL,O_NONBLOCK)==0&&::fcntl(errors.value,F_SETFL,O_NONBLOCK)==0,"recovery_queue.channel");
        started=monotonic_ms();child=std::make_unique<Child>(Child::launch_program(worker,{std::to_string(current_process_id())},remote.value,remote.value,remote_errors.value));
    }
    void packet(std::string_view raw){
        auto p=decode(raw);const auto& h=p.header;need(matches(h,request)&&h.contains("kind")&&!reply,"recovery_queue.reply");
        if(h["kind"]=="guard"){
            need(output.empty()&&p.bytes.empty()&&protocol::members(h,{"kind","binding","ticket","operation","guard"})&&guards<8&&h["guard"]==std::to_string(guards+1),"recovery_queue.guard");
            ++guards;auto grant=stamp(request,"grant");grant["guard"]=std::to_string(guards);grant["allow"]=permitted(active->operation);output=encode(grant);sent=0;return;
        }
        need(output.empty()&&h["kind"]=="result"&&protocol::members(h,{"kind","binding","ticket","operation","outcome","error","digest","present","pending"})&&
            error_code(h["error"])&&nullable_digest(h["digest"])&&h["present"].is_boolean()&&h["pending"].is_boolean(),"recovery_queue.reply");
        if(h["outcome"]=="loaded"){
            need(active->operation=="load"&&h["error"]==""&&guards==2,"recovery_queue.reply");
            need(h["present"].get<bool>()?(h["digest"]==configuration::sha256(p.bytes)):(h["digest"].is_null()&&p.bytes.empty()),"recovery_queue.reply");
        }else if(h["outcome"]=="durable"){
            need(active->operation!="load"&&h["error"]==""&&p.bytes.empty()&&h["pending"]==false&&guards==6,"recovery_queue.reply");
            need(active->operation=="replace"?(h["present"]==true&&active->digest&&h["digest"]==*active->digest):(h["present"]==false&&h["digest"].is_null()),"recovery_queue.reply");
        }else need((h["outcome"]=="unchanged"||h["outcome"]=="unknown")&&h["error"]!=""&&h["digest"].is_null()&&h["present"]==false&&h["pending"]==false&&p.bytes.empty(),"recovery_queue.reply");
        reply=std::move(p);
    }
    void transfer(){
        if(!output.empty()){
            const auto n=::send(channel.value,output.data()+sent,std::min(std::size_t{262144},output.size()-sent),MSG_NOSIGNAL);
            if(n>0){sent+=static_cast<std::size_t>(n);if(sent==output.size()){erase(output);sent=0;}}
            else need(n<0&&(errno==EINTR||errno==EAGAIN||errno==EWOULDBLOCK),"recovery_queue.channel");
        }
        std::array<char,8192> bytes{};std::size_t received=0;
        for(unsigned attempt=0;attempt<31&&!eof&&received<261119;++attempt){
            const auto n=::recv(channel.value,bytes.data(),std::min(bytes.size(),std::size_t{261119}-received),0);
            if(n<0){need(errno==EAGAIN||errno==EWOULDBLOCK||errno==EINTR,"recovery_queue.channel");break;}
            if(!n){eof=true;framer.eof();break;}
            received+=static_cast<std::size_t>(n);framer.feed({bytes.data(),static_cast<std::size_t>(n)},monotonic_ms(),[&](auto raw){packet(raw);});
        }
        if(!error_eof){
            const auto n=::read(errors.value,bytes.data(),1025);
            if(n>0){need(diagnostics.size()+static_cast<std::size_t>(n)<=1024,"recovery_queue.error_limit");diagnostics.append(bytes.data(),static_cast<std::size_t>(n));}
            else if(!n)error_eof=true;
            else need(errno==EAGAIN||errno==EWOULDBLOCK||errno==EINTR,"recovery_queue.channel");
        }
    }
    void finished(){
        need(active&&reply&&output.empty()&&diagnostics.empty(),"recovery_queue.reply");
        const auto& h=reply->header;RecoveryCompletion done{context,active->ticket,active->operation,h["outcome"],h["error"],std::nullopt,std::nullopt,h["pending"]};
        if(h["digest"].is_string())done.digest=h["digest"].get<std::string>();
        if(done.operation=="load"&&h["present"]==true)done.bytes=std::move(reply->bytes);
        if(done.outcome=="loaded"||done.outcome=="durable"){
            expected=done.digest;
            if(!pending){completion=std::move(done);state=sealed?RecoveryQueueState::retired:RecoveryQueueState::ready;}
        }else{
            fault=true;error=done.error;pending.reset();completion=std::move(done);state=RecoveryQueueState::unavailable;
        }
        active.reset();reply.reset();request=nullptr;framer=protocol::Framer(frame_limit);channel.close();errors.close();erase(diagnostics);
    }
    void poll(){
        if(closed||fault){
            if(child&&child->wait()){child.reset();active.reset();if(!closed){completion=std::move(stopped);stopped.reset();}}
            if(closed&&!child)state=RecoveryQueueState::closed;
            return;
        }
        if(!child){if(pending)start();return;}
        if(monotonic_ms()-started>=5000){stop("recovery_queue.timeout");return;}
        transfer();const auto exited=child->wait();if(!exited)return;
        if(exited->signaled||exited->code){child.reset();stop("recovery_queue.worker_exit");return;}
        if(!eof||!error_eof)return;
        child.reset();finished();
    }
};
LinuxRecoveryQueue::LinuxRecoveryQueue(std::string worker,std::string path,RecoveryContext c):impl_(std::make_unique<Impl>()){
    auto& s=*impl_;s.worker=std::move(worker);s.path=std::move(path);s.context=std::move(c);s.identity=binding(s.context);
    need(recovery_io::binding(s.identity),"recovery_queue.identity");need(s.context.read,"recovery_queue.denied");
    need(!s.path.empty()&&s.path.front()=='/'&&s.path.size()<=4096,"recovery_queue.path");
}
LinuxRecoveryQueue::~LinuxRecoveryQueue()=default;
std::uint64_t LinuxRecoveryQueue::replace(std::string bytes){
    auto& s=*impl_;s.check();Call call(s.calling);need(s.initialized&&!s.sealed&&s.permitted("replace"),"recovery_queue.denied");
    need(!bytes.empty()&&bytes.size()<=record_limit,"recovery_queue.size");need(s.tickets<std::numeric_limits<std::uint64_t>::max(),"recovery_queue.capacity");
    auto digest=configuration::sha256(bytes);const auto ticket=++s.tickets;s.pending=Impl::Job{ticket,"replace",std::move(bytes),std::move(digest)};s.completion.reset();s.state=RecoveryQueueState::busy;return ticket;
}
std::uint64_t LinuxRecoveryQueue::retire(){
    auto& s=*impl_;s.check();Call call(s.calling);need(s.initialized&&!s.sealed&&s.permitted("retire"),"recovery_queue.denied");need(s.tickets<std::numeric_limits<std::uint64_t>::max(),"recovery_queue.capacity");
    const auto ticket=++s.tickets;s.pending=Impl::Job{ticket,"retire",{},{} };s.completion.reset();s.sealed=true;s.state=RecoveryQueueState::retiring;return ticket;
}
RecoveryQueueStatus LinuxRecoveryQueue::poll(){
    auto& s=*impl_;s.check();Call call(s.calling);
    try{s.poll();}catch(...){s.stop("recovery_queue.failure");}
    return s.view();
}
RecoveryQueueStatus LinuxRecoveryQueue::status()const{auto& s=*impl_;s.check();Call call(s.calling);return s.view();}
std::optional<RecoveryCompletion> LinuxRecoveryQueue::take(){
    auto& s=*impl_;s.check();Call call(s.calling);auto value=std::move(s.completion);s.completion.reset();if(value&&value->operation=="load"&&value->outcome=="loaded")s.initialized=true;return value;
}
void LinuxRecoveryQueue::close(){auto& s=*impl_;s.check();Call call(s.calling);s.stop("recovery_queue.closed",true);}
}
