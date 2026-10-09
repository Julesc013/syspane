#include "profile_supervisor_linux.hpp"
#include "health_link.hpp"
#include <array>
#include <cerrno>
#include <dirent.h>
#include <fcntl.h>
#include <filesystem>
#include <limits>
#include <sys/file.h>
#include <sys/random.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <thread>
#include <unistd.h>

namespace syspane::application {
namespace os=platform;namespace p=protocol;namespace r=recovery;
namespace {
void need(bool ok,const char* code){if(!ok)throw p::Error(code);}
struct Fd {
    int value=-1;
    ~Fd(){close();}
    void close(){if(value>=0)::close(value);value=-1;}
};
bool same(const struct stat& a,const struct stat& b){return a.st_dev==b.st_dev&&a.st_ino==b.st_ino;}
bool directory(const struct stat& s){return S_ISDIR(s.st_mode)&&s.st_uid==::getuid()&&(s.st_mode&07777)==0700;}
bool socket_file(const struct stat& s){return S_ISSOCK(s.st_mode)&&s.st_uid==::getuid()&&(s.st_mode&07777)==0600&&s.st_nlink==1;}
void entries(int fd,bool socket_allowed){
    const int copy=::openat(fd,".",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    need(copy>=0,"supervisor.runtime");
    struct Dir {DIR* value;~Dir(){if(value)::closedir(value);}} dir{::fdopendir(copy)};
    if(!dir.value){::close(copy);throw p::Error("supervisor.runtime");}
    unsigned count=0;
    for(;;){
        errno=0;const auto* e=::readdir(dir.value);
        if(!e){need(errno==0,"supervisor.runtime");break;}
        need(++count<=3,"supervisor.runtime");const std::string name=e->d_name;
        need(name=="."||name==".."||(socket_allowed&&name=="s"),"supervisor.runtime");
    }
}
std::string nonce(){
    std::array<unsigned char,16> bytes{};std::size_t n=0;
    for(unsigned attempt=0;n<bytes.size()&&attempt<16;++attempt){
        const auto got=::getrandom(bytes.data()+n,bytes.size()-n,GRND_NONBLOCK);
        if(got>0)n+=static_cast<std::size_t>(got);
        else need(got<0&&errno==EINTR,"supervisor.random");
    }
    need(n==bytes.size(),"supervisor.random");std::string text;const char hex[]="0123456789abcdef";
    for(const auto b:bytes){text+=hex[b>>4];text+=hex[b&15];}return text;
}
struct Call {
    bool& active;
    explicit Call(bool& value):active(value){need(!active,"supervisor.reentrant");active=true;}
    ~Call(){active=false;}
};
}
struct LinuxProfileSupervisor::Impl {
    std::string helper,root,owner_nonce,leaf,endpoint,epoch,fault;
    LocalService service=LocalService::configuration;
    os::ProfileLocation location;bool create=false,closing=false,killed=false,ready=false,hello=false,terminal=false;
    std::shared_ptr<os::LinuxInstallation> installation;
    std::uint64_t console=0,generation=0,started=0,stop_started=0,last_sent=0,sequence=0,token=0;
    std::size_t sent=0,stderr_bytes=0;
    Fd root_fd,leaf_fd,channel,errors;
    struct stat root_identity{},leaf_identity{};std::optional<struct stat> socket_identity;
    std::thread::id owner=std::this_thread::get_id();mutable bool calling=false;
    ProfileSupervisorState state=ProfileSupervisorState::starting;
    r::RestartGate gate{0};r::Clock clock;
    std::unique_ptr<os::Child> child;
    std::unique_ptr<r::HealthLink> health;
    std::unique_ptr<r::ProducerLease> lease;
    std::unique_ptr<r::TransactionWatch> operation;
    p::Framer frames{4096};std::string output;
    std::optional<os::ChildExit> last_exit;
    std::vector<ProfileSupervisorEvent> events;

    void check()const{need(owner==std::this_thread::get_id(),"supervisor.owner");}
    ProfileSupervisorView view()const{return {state,generation,child?child->id():0,epoch,ready?endpoint:std::string{},fault,gate.view(),last_exit};}
    void event(const char* kind,std::uint64_t now,std::uint64_t ticket=0,bool final=false){
        if(final){if(events.size()>=64)return;}else need(events.size()<60,"supervisor.events");
        events.push_back({kind,view(),now,ticket});
    }
    void verify_root(){
        struct stat held{},named{};
        need(::fstat(root_fd.value,&held)==0&&::lstat(root.c_str(),&named)==0&&directory(held)&&directory(named)&&
             same(held,root_identity)&&same(named,root_identity),"supervisor.runtime");
    }
    void verify_leaf(){
        verify_root();struct stat held{},named{};
        need(leaf_fd.value>=0&&::fstat(leaf_fd.value,&held)==0&&::fstatat(root_fd.value,leaf.c_str(),&named,AT_SYMLINK_NOFOLLOW)==0&&
             directory(held)&&directory(named)&&same(held,leaf_identity)&&same(named,leaf_identity),"supervisor.runtime");
    }
    void record_socket(){
        verify_leaf();entries(leaf_fd.value,true);struct stat value{};
        need(::fstatat(leaf_fd.value,"s",&value,AT_SYMLINK_NOFOLLOW)==0&&socket_file(value),"supervisor.runtime");socket_identity=value;
    }
    void cleanup(){
        if(leaf.empty())return;
        verify_leaf();entries(leaf_fd.value,true);struct stat value{};
        if(::fstatat(leaf_fd.value,"s",&value,AT_SYMLINK_NOFOLLOW)==0){
            need(socket_identity&&same(*socket_identity,value)&&socket_file(value),"supervisor.cleanup");
            need(::unlinkat(leaf_fd.value,"s",0)==0,"supervisor.cleanup");
        }else need(errno==ENOENT,"supervisor.cleanup");
        need(::unlinkat(root_fd.value,leaf.c_str(),AT_REMOVEDIR)==0,"supervisor.cleanup");
        leaf_fd.close();leaf.clear();socket_identity.reset();
    }
    void collect_output(){
        auto bytes=health->take_output();
        if(sent){output.erase(0,sent);sent=0;}
        need(bytes.size()<=65536-output.size(),"supervisor.output");output+=bytes;
    }
    void send(){
        if(sent==output.size())return;
        const auto n=::send(channel.value,output.data()+sent,output.size()-sent,MSG_NOSIGNAL);
        if(n>0){sent+=static_cast<std::size_t>(n);if(sent==output.size()){output.clear();sent=0;}}
        else need(n<0&&(errno==EINTR||errno==EAGAIN||errno==EWOULDBLOCK),"supervisor.channel");
    }
    void kill(){
        if(child&&!killed){child->request_stop();killed=true;}
    }
    void failed(const std::string& why,std::uint64_t now){
        ready=false;fault=why;output.clear();sent=0;channel.close();errors.close();
        if(gate.view().state==r::ChildState::running){
            const auto reason=why=="supervisor.operation_timeout"?r::Failure::operation_timeout:
                why=="supervisor.worker_exit"?r::Failure::crashed:why=="supervisor.launch"?r::Failure::launch_failed:r::Failure::producer_expired;
            need(gate.failed(reason,child?r::StopProof::unconfirmed:r::StopProof::confirmed,now)==r::Code::accepted,"supervisor.gate");
        }
        state=closing?ProfileSupervisorState::closing:child?ProfileSupervisorState::quarantined:ProfileSupervisorState::waiting;
        event("fault",now,0,true);kill();
        if(!child)after_exit(now);
    }
    void after_exit(std::uint64_t now){
        ready=false;channel.close();errors.close();output.clear();sent=0;
        if(gate.view().state==r::ChildState::quarantined)need(gate.confirm_stopped(now)==r::Code::accepted,"supervisor.gate");
        try{cleanup();}catch(...){fault="supervisor.cleanup";terminal=true;}
        state=closing?ProfileSupervisorState::closed:terminal?ProfileSupervisorState::unavailable:
            gate.view().state==r::ChildState::circuit_open?ProfileSupervisorState::circuit_open:ProfileSupervisorState::waiting;
        event(closing?"closed":"stopped",now,0,true);
    }
    bool reap(std::uint64_t now){
        if(!child)return true;
        const auto exited=child->wait();if(!exited)return false;
        last_exit=exited;event("reaped",now,0,true);child.reset();after_exit(now);return true;
    }
    void start(std::uint64_t now){
        need(!child&&leaf.empty(),"supervisor.ownership");verify_root();
        need(generation<std::numeric_limits<std::uint64_t>::max(),"supervisor.generation");
        ++generation;epoch=std::string(service==LocalService::network?"network:":"configuration:")+owner_nonce+":"+std::to_string(generation);leaf="g"+std::to_string(generation);
        endpoint=root+"/"+leaf+"/s";need(endpoint.size()<108,"supervisor.endpoint");
        need(::mkdirat(root_fd.value,leaf.c_str(),0700)==0,"supervisor.runtime");
        leaf_fd.value=::openat(root_fd.value,leaf.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
        need(leaf_fd.value>=0&&::fstat(leaf_fd.value,&leaf_identity)==0&&directory(leaf_identity),"supervisor.runtime");
        int pair[2];need(::socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC|SOCK_NONBLOCK,0,pair)==0,"supervisor.channel");
        Fd remote;channel.value=pair[0];remote.value=pair[1];
        int pipes[2];need(::pipe2(pipes,O_CLOEXEC|O_NONBLOCK)==0,"supervisor.channel");Fd remote_errors;errors.value=pipes[0];remote_errors.value=pipes[1];
        const p::Json profile={{"id",location.profile},{"home",location.home},{"config_home",location.config_home},
            {"data_home",location.data_home},{"state_home",location.state_home},{"portable_root",location.portable_root?p::Json(*location.portable_root):p::Json()}};
        output=p::frame(p::Json{{"format","SysPane.ProfileController"},{"schema_version","0.1.0"},{"producer_epoch",epoch},
            {"client_pid",std::to_string(console)},{"endpoint",endpoint},{"create",create},{"profile",profile}}.dump(),32768);
        if(service==LocalService::network)output=p::frame(p::Json{{"format","SysPane.NetworkController"},{"schema_version","0.1.0"},
            {"producer_epoch",epoch},{"client_pid",std::to_string(console)},{"endpoint",endpoint}}.dump(),32768);
        sent=0;started=now;ready=hello=killed=false;sequence=last_sent=token=0;stderr_bytes=0;
        frames=p::Framer(4096);lease=std::make_unique<r::ProducerLease>();operation=std::make_unique<r::TransactionWatch>();
        health=std::make_unique<r::HealthLink>(true,service==LocalService::network?"collector":"console",epoch,"G",started,service==LocalService::configuration);
        try{
            std::vector<std::string> args{std::to_string(os::current_process_id())};
            if(service==LocalService::network)args.insert(args.begin(),"--network");
            child=std::make_unique<os::Child>(installation?
                os::Child::launch_sealed(installation->verified_helper(),service==LocalService::network?"syspane-network-host":"syspane-configuration-host",args,remote.value,remote.value,remote_errors.value):
                os::Child::launch_program(helper,args,remote.value,remote.value,remote_errors.value));
        }
        catch(const os::ChildError&){throw p::Error("supervisor.launch");}
        state=ProfileSupervisorState::starting;event("launched",os::monotonic_ms());
    }
    void deadlines(std::uint64_t now){
        need(clock.observe(now),"supervisor.clock");
        need(operation->tick(now)==r::Code::accepted,"supervisor.operation_timeout");
        if(!ready)need(now-started<5000,"supervisor.startup_timeout");
        else{lease->tick(now);need(lease->view().alive,"supervisor.health_expired");}
    }
    void packet(std::string_view raw,std::uint64_t now){
        deadlines(now);
        if(!hello){
            const auto message=p::decode(raw);
            need(message.type=="hello"&&message.body.at("producer_epoch")==epoch,"supervisor.epoch");hello=true;
        }
        const auto encoded=p::frame(std::string(raw),4096);std::vector<r::HealthEvent> observed;
        for(std::size_t at=0;at<encoded.size();at+=4096){
            auto part=health->feed(std::string_view(encoded).substr(at,4096),now);observed.insert(observed.end(),part.begin(),part.end());
        }
        for(const auto& e:observed){
            deadlines(now);
            if(e.kind==r::HealthKind::ready){
                record_socket();token=lease->attach(service==LocalService::network?"network-host":"configuration-host",epoch,now).token;need(token!=0,"supervisor.lease");
                ready=true;state=ProfileSupervisorState::ready;event("ready",now);
            }else if(e.kind==r::HealthKind::heartbeat){
                need(lease->heartbeat(token,e.value,now)==r::Code::accepted,"supervisor.heartbeat");
            }else if(e.kind==r::HealthKind::transaction_started){
                need(operation->started(e.value,now)==r::Code::accepted,"supervisor.operation_order");
                health->transaction_armed(e.value);event("armed",now,e.value);
            }else if(e.kind==r::HealthKind::transaction_finished){
                need(operation->finished(e.value,now)==r::Code::accepted,"supervisor.operation_timeout");event("finished",now,e.value);
            }else throw p::Error("supervisor.direction");
        }
        collect_output();
    }
    void transfer(){
        send();std::array<char,4096> bytes{};
        for(unsigned attempt=0;attempt<16;++attempt){
            const auto n=::recv(channel.value,bytes.data(),bytes.size(),0);
            if(n<0){need(errno==EAGAIN||errno==EWOULDBLOCK||errno==EINTR,"supervisor.channel");break;}
            need(n>0,"supervisor.channel");const auto now=os::monotonic_ms();deadlines(now);
            frames.feed({bytes.data(),static_cast<std::size_t>(n)},now,[&](auto raw){packet(raw,now);});
        }
        const auto n=::read(errors.value,bytes.data(),1025);
        if(n>0){stderr_bytes+=static_cast<std::size_t>(n);need(stderr_bytes<=1024,"supervisor.stderr");}
        else if(n<0)need(errno==EAGAIN||errno==EWOULDBLOCK||errno==EINTR,"supervisor.channel");
        const auto now=os::monotonic_ms();deadlines(now);frames.tick(now);health->tick(now);
        if(ready&&(!sequence||now-last_sent>=1000)){
            need(sequence<std::numeric_limits<std::uint64_t>::max(),"supervisor.sequence");
            health->heartbeat(sequence++);last_sent=now;collect_output();
        }
        send();
    }
    void poll(){
        const auto now=os::monotonic_ms();need(clock.observe(now),"supervisor.clock");
        if(closing||state==ProfileSupervisorState::quarantined){
            if(child&&closing&&!killed){
                if(now-stop_started>=2000)kill();
                else try{send();}catch(...){kill();}
            }
            if(child)reap(now);
            return;
        }
        if(terminal||state==ProfileSupervisorState::circuit_open||state==ProfileSupervisorState::closed)return;
        if(!child){
            const auto result=gate.start(now);
            if(result==r::Code::not_due)return;
            if(result==r::Code::circuit_open){state=ProfileSupervisorState::circuit_open;return;}
            need(result==r::Code::accepted,"supervisor.gate");start(now);return;
        }
        if(child->wait()){failed("supervisor.worker_exit",now);reap(now);return;}
        deadlines(now);transfer();
    }
    void close(){
        if(closing)return;
        closing=true;const auto now=os::monotonic_ms();stop_started=now;
        const bool graceful=child&&ready&&state==ProfileSupervisorState::ready&&!sent;
        ready=false;state=child?ProfileSupervisorState::closing:ProfileSupervisorState::closed;
        if(!child){event("closed",now,0,true);return;}
        if(gate.view().state==r::ChildState::running)need(gate.stopped(r::StopProof::unconfirmed,now)==r::Code::accepted,"supervisor.gate");
        if(graceful){
            try{output.clear();health->take_output();health->shutdown();collect_output();send();}
            catch(...){kill();}
        }else kill();
    }
};
LinuxProfileSupervisor::LinuxProfileSupervisor(std::string helper,std::string runtime,os::ProfileLocation location,bool create,std::uint64_t console,LocalService service)
    :impl_(std::make_unique<Impl>()){
    auto& s=*impl_;need(os::unprivileged_context()&&console,"supervisor.context");need(service==LocalService::configuration||service==LocalService::network,"supervisor.service");
    if(service==LocalService::configuration)(void)os::profile_paths(location);
    s.service=service;
    s.helper=std::move(helper);s.root=std::move(runtime);s.location=std::move(location);s.create=create;s.console=console;
    need(!s.root.empty()&&s.root.size()<=70&&std::filesystem::canonical(s.root)==s.root,"supervisor.runtime");
    s.root_fd.value=::open(s.root.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    struct statfs filesystem{};
    need(s.root_fd.value>=0&&::fstat(s.root_fd.value,&s.root_identity)==0&&directory(s.root_identity)&&
         ::fstatfs(s.root_fd.value,&filesystem)==0&&(filesystem.f_type==0xEF53||filesystem.f_type==0x01021994)&&
         ::flock(s.root_fd.value,LOCK_EX|LOCK_NB)==0,"supervisor.runtime");
    s.verify_root();entries(s.root_fd.value,false);s.owner_nonce=nonce();
}
LinuxProfileSupervisor::~LinuxProfileSupervisor()=default;
LinuxProfileSupervisor::LinuxProfileSupervisor(std::shared_ptr<os::LinuxInstallation> installation,std::string runtime,os::ProfileLocation location,bool create,std::uint64_t console,LocalService service)
    :LinuxProfileSupervisor(std::string{},std::move(runtime),std::move(location),create,console,service){
    need(static_cast<bool>(installation),"supervisor.installation");(void)installation->verified_helper();impl_->installation=std::move(installation);
}
ProfileSupervisorView LinuxProfileSupervisor::poll(){
    auto& s=*impl_;s.check();Call call(s.calling);
    try{s.poll();}catch(const std::exception& e){s.failed(std::string(e.what()).find("supervisor.")==0?e.what():"supervisor.protocol",os::monotonic_ms());}
    catch(...){s.failed("supervisor.failure",os::monotonic_ms());}
    return s.view();
}
ProfileSupervisorView LinuxProfileSupervisor::status()const{auto& s=*impl_;s.check();Call call(s.calling);return s.view();}
std::vector<ProfileSupervisorEvent> LinuxProfileSupervisor::take(){auto& s=*impl_;s.check();Call call(s.calling);std::vector<ProfileSupervisorEvent> out;out.swap(s.events);return out;}
void LinuxProfileSupervisor::close(){auto& s=*impl_;s.check();Call call(s.calling);s.close();}
}
