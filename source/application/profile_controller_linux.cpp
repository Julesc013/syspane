#include "profile_controller_linux.hpp"
#include "profile_worker_linux.hpp"
#include "machine_policy.hpp"
#include "async_commands.hpp"
#include "session.hpp"
#include "child.hpp"
#include "health_link.hpp"
#include "recovery.hpp"
#include <array>
#include <atomic>
#include <cstdlib>
#include <deque>
#include <limits>
#include <thread>
#include <unistd.h>

namespace syspane::application {
namespace c=configuration;namespace os=platform;namespace p=protocol;namespace r=recovery;
namespace {
void need(bool ok,const char* code){if(!ok)throw p::Error(code);}
bool same(const c::Policy& a,const c::Policy& b){return a.available==b.available&&a.revision==b.revision&&a.forced==b.forced&&a.denied_capabilities==b.denied_capabilities&&a.disclosure==b.disclosure;}
struct Bootstrap {os::ProfileLocation location;bool create;std::string endpoint,epoch;std::uint64_t client;};
Bootstrap bootstrap(os::Stream& parent){
    p::Framer decoder(32768);std::optional<p::Json> value;const auto start=os::monotonic_ms();
    while(!value){
        need(os::monotonic_ms()-start<5000,"controller.bootstrap_timeout");std::array<char,4096> buffer{};
        const auto got=parent.read(buffer.data(),buffer.size(),10);need(!got.eof,"controller.bootstrap_eof");
        decoder.feed({buffer.data(),got.bytes},got.observed_ms,[&](auto raw){need(!value,"controller.bootstrap_trailing");value=p::parse(raw);});
        decoder.tick(os::monotonic_ms());
    }
    need(decoder.buffered()==0,"controller.bootstrap_trailing");const auto& v=*value;
    need(p::members(v,{"format","schema_version","producer_epoch","client_pid","endpoint","create","profile"})&&
         v["format"]=="SysPane.ProfileController"&&v["schema_version"]=="0.1.0"&&v["create"].is_boolean(),"controller.bootstrap");
    const auto& profile=v.at("profile");need(p::members(profile,{"id","home","config_home","data_home","state_home","portable_root"}),"controller.profile");
    Bootstrap out;out.create=v["create"];out.epoch=v.at("producer_epoch");out.endpoint=v.at("endpoint");
    need(p::identifier(out.epoch)&&v["client_pid"].is_string(),"controller.identity");const auto client=p::decimal(v["client_pid"].get<std::string>());
    need(client&&*client,"controller.client");out.client=*client;
    out.location.profile=profile.at("id");out.location.home=profile.at("home");out.location.config_home=profile.at("config_home");
    out.location.data_home=profile.at("data_home");out.location.state_home=profile.at("state_home");
    if(!profile["portable_root"].is_null())out.location.portable_root=profile.at("portable_root").get<std::string>();
    (void)os::profile_paths(out.location);return out;
}
}
int run_profile_controller(std::uint64_t parent,os::LinuxProfileStore::PolicySource source,os::LinuxProfileOwner::Transition transition){
    try{
        need(os::unprivileged_context(),"controller.context");os::arm_parent_lifetime(parent);::close(3);
        auto guardian=os::Stream::from_connected_socket(0,parent);const auto startup=bootstrap(guardian);
        if(!source)source=os::machine_policy;
        std::optional<c::Policy> baseline;
        const auto sample=[&]{auto value=source();if(!baseline)baseline=value;return value;};
        const std::set<std::string> caps={"scene.selector","scene.content","scene.edit-locks","scene.visibility","theme.typography","configuration.theme-overrides"};
        auto native_caps=caps;native_caps.insert("editor.recovery");
        os::LinuxProfileWorker store(startup.location,startup.create,std::move(native_caps),sample,std::move(transition));
        need(baseline&&baseline->available,"controller.policy");
        auto owner=std::make_shared<c::AsyncCommands>(store,startup.epoch,c::make_resource_provider(store,caps),[&](const c::Committed& value)->std::optional<c::ProfileRecoveryData>{
            auto snapshot=store.recovery_snapshot({true,"console",{"console"}});
            need(snapshot.committed.documents.settings==value.documents.settings&&snapshot.committed.documents.scene==value.documents.scene&&
                 snapshot.committed.resources==value.resources,"controller.recovery_coherence");
            if(!snapshot.recovery)return {};
            const auto& admission=*snapshot.recovery;const auto& directory=admission.directory;
            return c::ProfileRecoveryData{directory.profile,admission.generation,{directory.path,directory.uid,directory.state_device,directory.state_inode,
                directory.recovery_device,directory.recovery_inode},admission.policy_revision,admission.erase};
        });
        c::Sessions sessions(startup.epoch,owner->revision(),*baseline,{},owner);
        os::Listener listener(startup.endpoint);r::HealthLink health(guardian,false,"console",startup.epoch,"",true);
        r::ProducerLease lease;std::uint64_t lease_token=0,sequence=0,last_heartbeat=0;
        std::optional<os::Stream> client;std::unique_ptr<p::Framer> decoder;
        std::deque<std::string> incoming;std::size_t incoming_bytes=0;
        std::thread command_worker,policy_worker;std::optional<c::AsyncCommands::Completion> completion;
        std::atomic<bool> command_done{false},policy_done{false};std::exception_ptr command_error; c::Policy sampled;
        std::uint64_t watch_counter=0,watch=0,command_ticket=0,last_policy=os::monotonic_ms(),last_clock=last_policy,stop_started=0;
        std::uint64_t completed_commands=0,policy_for_completion=0;
        bool armed=false,stopping=false,need_policy=false,need_output=false,fresh=false;
        const auto disconnect=[&]{if(client)sessions.disconnect("C");client.reset();decoder.reset();incoming.clear();incoming_bytes=0;need_output=false;};
        const auto die=[&](int code){owner->invalidate();std::_Exit(code);};
        const auto start_policy=[&]{policy_done=false;policy_for_completion=completed_commands;policy_worker=std::thread([&]{try{sampled=source();}catch(...){sampled={};}policy_done.store(true,std::memory_order_release);});};
        try{
            for(;;){
                auto now=os::monotonic_ms();if(now<last_clock)die(125);last_clock=now;
                if(!stopping)try{
                    for(const auto& event:health.poll(1)){
                        if(lease_token){lease.tick(event.observed_ms);if(!lease.view().alive)die(124);}
                        if(event.kind==r::HealthKind::ready){need(health.epoch()==startup.epoch,"controller.epoch");lease_token=lease.attach("supervisor",startup.epoch,event.observed_ms).token;}
                        else if(event.kind==r::HealthKind::heartbeat){if(lease.heartbeat(lease_token,event.value,event.observed_ms)!=r::Code::accepted)die(124);}
                        else if(event.kind==r::HealthKind::transaction_armed){need(watch&&event.value==watch&&!armed,"controller.arm");armed=true;}
                        else if(event.kind==r::HealthKind::shutdown){stopping=true;stop_started=os::monotonic_ms();owner->invalidate();disconnect();}
                        else die(124);
                    }
                    now=os::monotonic_ms();if(lease_token){lease.tick(now);if(!lease.view().alive)die(124);}
                    if(!stopping&&health.ready()&&(!sequence||now-last_heartbeat>=1000)){health.heartbeat(sequence++);last_heartbeat=now;}
                }catch(...){die(124);}
                if(command_done.load(std::memory_order_acquire)){
                    command_worker.join();command_done=false;command_ticket=0;
                    if(!stopping){if(command_error)std::rethrow_exception(command_error);need(completion.has_value()&&owner->finish(std::move(*completion),os::monotonic_ms(),true),"controller.finish");
                        need(completed_commands<std::numeric_limits<std::uint64_t>::max(),"controller.completion_capacity");++completed_commands;
                        fresh=false;need_policy=true;need_output=true;}
                    completion.reset();
                }
                if(policy_done.load(std::memory_order_acquire)){
                    policy_worker.join();policy_done=false;
                    if(!stopping){if(!sampled.available||!same(sampled,*baseline))die(126);last_policy=os::monotonic_ms();fresh=policy_for_completion==completed_commands;need_policy=!fresh;}
                }
                if(stopping){
                    if(!command_worker.joinable()&&!policy_worker.joinable()){store.close();return 0;}
                    if(os::monotonic_ms()-stop_started>=2000)die(125);
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));continue;
                }
                if(!health.ready())continue;
                if(!client)try{
                    client=listener.accept_ready(startup.client);
                    if(client){sessions.open("C",client->peer().principal,{true,"console",{"console"}},os::monotonic_ms());decoder=std::make_unique<p::Framer>();}
                }catch(const os::IpcError&){disconnect();}
                if(client)try{
                    std::array<char,4096> buffer{};const auto got=client->read(buffer.data(),buffer.size(),1);
                    if(got.eof){decoder->eof();disconnect();}
                    else{
                        decoder->feed({buffer.data(),got.bytes},got.observed_ms,[&](auto raw){
                            need(incoming.size()<8&&raw.size()<=2097152-incoming_bytes,"controller.input_capacity");incoming.emplace_back(raw);incoming_bytes+=raw.size();});
                        decoder->tick(os::monotonic_ms());
                    }
                }catch(...){disconnect();}
                if(fresh){
                    fresh=false;
                    if(owner->storage_faulted())die(125);
                    if(!client)need_output=false;
                    if(client)try{
                        while(!incoming.empty()){
                            auto raw=std::move(incoming.front());incoming.pop_front();incoming_bytes-=raw.size();
                            sessions.receive("C",raw,os::monotonic_ms());decoder->restrict_limit(sessions.frame_bound("C"));need_output=true;
                            if(sessions.closed("C")){disconnect();break;}
                        }
                        if(client){sessions.tick(os::monotonic_ms());if(sessions.closed("C"))disconnect();}
                        if(client){
                            need_output=false;for(unsigned sent=0;sent<4;++sent){auto raw=sessions.pop("C",os::monotonic_ms());if(!raw)break;
                                client->write(p::frame(*raw),100);need_output=sent==3;}
                        }
                    }catch(...){disconnect();}
                }
                now=os::monotonic_ms();
                if(!watch){
                    if(auto next=owner->take())command_ticket=*next;
                    if(command_ticket||!incoming.empty()||need_output||need_policy||now-last_policy>=1000){
                        need(watch_counter<std::numeric_limits<std::uint64_t>::max(),"controller.watch_capacity");watch=++watch_counter;armed=false;health.transaction_started(watch);
                    }
                }
                if(watch&&armed){
                    if(command_ticket&&!command_worker.joinable()){
                        command_done=false;command_error={};command_worker=std::thread([&]{try{completion.emplace(owner->run(command_ticket));}catch(...){command_error=std::current_exception();}command_done.store(true,std::memory_order_release);});
                    }
                    if(!policy_worker.joinable()&&(need_policy||!incoming.empty()||need_output||now-last_policy>=1000))start_policy();
                    if(!command_worker.joinable()&&!policy_worker.joinable()&&!command_ticket&&!need_policy&&!need_output&&incoming.empty()){
                        health.transaction_finished(watch);watch=0;armed=false;
                    }
                }
                if(!client)std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
        }catch(...){die(125);}
        std::_Exit(125);
    }catch(...){static constexpr char message[]="controller.startup\n";(void)::write(2,message,sizeof(message)-1);return 2;}
}
}
