#include "child.hpp"
#include "health_link.hpp"
#include "recovery.hpp"
#include <filesystem>
#include <iostream>
#include <thread>
#include <poll.h>
#include <sys/stat.h>
#include <unistd.h>

namespace os=syspane::platform;namespace r=syspane::recovery;namespace p=syspane::protocol;
namespace {
void need(bool ok,const char* code){if(!ok)throw p::Error(code);}
void report(p::Json value){value["observed_ms"]=os::monotonic_ms();std::cout<<value.dump()<<std::endl;}
bool stopping(){
    pollfd fd{STDIN_FILENO,POLLIN,0};need(::poll(&fd,1,0)>=0,"supervisor.control");
    if(fd.revents&POLLHUP)return true;
    if(fd.revents&POLLIN){std::string line;std::getline(std::cin,line);need(line=="stop","supervisor.control");return true;}
    return false;
}
}
int supervise_commands(int argc,char** argv,const std::optional<std::string>& content){
    need(argc==7&&os::unprivileged_context(),"supervisor.arguments");
    const std::string root=argv[2],store=argv[3],scenario=argv[4],permission=argv[6];const auto parent=p::decimal(argv[5]);
    need(parent&&*parent&&(permission=="allow"||permission=="deny")&&
        (scenario=="normal"||scenario=="prepare"||scenario=="durable"||scenario=="repeat"||scenario=="resource"),"supervisor.arguments");
    os::arm_parent_lifetime(*parent);
    struct stat info{};need(std::filesystem::canonical(root)==root&&::lstat(root.c_str(),&info)==0&&S_ISDIR(info.st_mode)&&
        info.st_uid==::getuid()&&(info.st_mode&0777)==0700,"supervisor.root");
    r::RestartGate restart(0);const auto started=os::monotonic_ms();std::uint64_t generation=0;
    while(os::monotonic_ms()-started<90000){
        if(stopping())return 0;
        const auto admitted=restart.start(os::monotonic_ms());
        if(admitted==r::Code::not_due){std::this_thread::sleep_for(std::chrono::milliseconds(5));continue;}
        if(admitted==r::Code::circuit_open){report({{"event","circuit_open"},{"generations",generation}});return 0;}
        need(admitted==r::Code::accepted,"supervisor.restart");
        ++generation;const auto epoch="supervised:"+std::to_string(os::current_process_id())+":"+std::to_string(generation);
        const auto client_dir=root+"/c"+std::to_string(generation),guard_dir=root+"/g"+std::to_string(generation);
        need(::mkdir(client_dir.c_str(),0700)==0&&::mkdir(guard_dir.c_str(),0700)==0,"supervisor.directory");
        const auto endpoint=client_dir+"/s",guard_endpoint=guard_dir+"/s";os::Listener listener(guard_endpoint);
        const auto phase=scenario=="repeat"?"hang-prepare":(generation>1||scenario=="normal"?"plain":(scenario=="prepare"?"hang-prepare":(scenario=="resource"?"hang-resource":"hang-durable")));
        std::vector<std::string> args{endpoint,store,phase,argv[5],epoch,permission,guard_endpoint,std::to_string(os::current_process_id())};
        if(content){args.insert(args.begin(),*content);args.insert(args.begin(),"content");}
        auto child=os::Child::launch_self(args);
        report({{"event","launched"},{"pid",child.id()},{"epoch",epoch},{"endpoint",endpoint},{"generation",generation}});
        std::optional<os::Stream> stream;std::unique_ptr<r::HealthLink> link;r::ProducerLease lease;r::TransactionWatch operation;
        std::uint64_t token=0,sequence=0,last_sent=0,heartbeats=0;const auto launched=os::monotonic_ms();
        const auto check=[&](std::uint64_t now){
            need(operation.tick(now)==r::Code::accepted,"transaction.deadline");
            if(token){lease.tick(now);need(lease.view().alive,"supervisor.health_expired");}
            else need(now-launched<5000,"supervisor.startup_timeout");
        };
        bool requested=false;std::string fault;
        try{
            for(;;){
                if(stopping()){requested=true;break;}
                if(child.wait())throw p::Error("supervisor.child_exit");
                if(!stream){stream=listener.accept_ready(child.id());if(stream)link=std::make_unique<r::HealthLink>(*stream,true,"console",epoch,"G",true);}
                if(link)for(const auto& event:link->poll(10)){
                    check(event.observed_ms);
                    if(event.kind==r::HealthKind::ready){token=lease.attach("controller",epoch,event.observed_ms).token;
                        report({{"event","ready"},{"pid",child.id()},{"epoch",epoch},{"endpoint",endpoint}});}
                    else if(event.kind==r::HealthKind::heartbeat){need(lease.heartbeat(token,event.value,event.observed_ms)==r::Code::accepted,"supervisor.heartbeat");++heartbeats;}
                    else if(event.kind==r::HealthKind::transaction_started){
                        need(operation.started(event.value,event.observed_ms)==r::Code::accepted,"transaction.order");link->transaction_armed(event.value);
                        report({{"event","armed"},{"pid",child.id()},{"ticket",event.value}});
                    }else if(event.kind==r::HealthKind::transaction_finished){
                        need(operation.finished(event.value,event.observed_ms)==r::Code::accepted,"transaction.deadline");
                        report({{"event","finished"},{"pid",child.id()},{"ticket",event.value}});
                    }else throw p::Error("supervisor.direction");
                }
                const auto now=os::monotonic_ms();check(now);
                if(link&&link->ready()&&(!sequence||now-last_sent>=1000)){link->heartbeat(sequence++);last_sent=now;}
                need(now-started<90000,"supervisor.fixture_deadline");
                if(!stream)std::this_thread::sleep_for(std::chrono::milliseconds(2));
            }
        }catch(const std::exception& error){fault=error.what();}
        if(requested)need(restart.stopped(r::StopProof::unconfirmed,os::monotonic_ms())==r::Code::accepted,"supervisor.stop");
        else{
            need(restart.failed(fault=="transaction.deadline"?r::Failure::operation_timeout:r::Failure::producer_expired,
                r::StopProof::unconfirmed,os::monotonic_ms())==r::Code::accepted,"supervisor.quarantine");
            report({{"event","fault"},{"reason",fault},{"pid",child.id()},{"heartbeats",heartbeats},{"quarantined",restart.view().state==r::ChildState::quarantined}});
        }
        child.request_stop();const auto exited=child.wait(2000);need(exited.has_value(),"supervisor.stop_unconfirmed");
        need(restart.confirm_stopped(os::monotonic_ms())==r::Code::accepted,"supervisor.stop_proof");
        report({{"event","reaped"},{"pid",child.id()},{"signaled",exited->signaled},{"code",exited->code}});
        if(requested)return 0;
    }
    throw p::Error("supervisor.fixture_deadline");
}
