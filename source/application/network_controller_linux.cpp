#include "network_controller_linux.hpp"
#include "network_task_linux.hpp"
#include "network_publication.hpp"
#include "demand_sessions.hpp"
#include "machine_policy.hpp"
#include "child.hpp"
#include "health_link.hpp"
#include "recovery.hpp"
#include <array>
#include <cstdlib>
#include <limits>
#include <unistd.h>

namespace syspane::application {
namespace os=platform;namespace p=protocol;namespace c=configuration;namespace r=recovery;namespace n=runtime;
namespace {
void need(bool ok,const char* code){if(!ok)throw p::Error(code);}
bool same(const c::Policy& a,const c::Policy& b){return a.available==b.available&&a.revision==b.revision&&
    a.forced==b.forced&&a.denied_capabilities==b.denied_capabilities&&a.disclosure==b.disclosure;}
struct Bootstrap {std::string endpoint,epoch;std::uint64_t client;};
Bootstrap bootstrap(os::Stream& parent){
    p::Framer decoder(32768);std::optional<p::Json> value;const auto start=os::monotonic_ms();
    while(!value){
        need(os::monotonic_ms()-start<5000,"network.bootstrap_timeout");std::array<char,4096> bytes{};
        const auto got=parent.read(bytes.data(),bytes.size(),10);need(!got.eof,"network.bootstrap_eof");
        decoder.feed({bytes.data(),got.bytes},got.observed_ms,[&](auto raw){need(!value,"network.bootstrap_trailing");value=p::parse(raw);});
        decoder.tick(os::monotonic_ms());
    }
    need(!decoder.buffered(),"network.bootstrap_trailing");const auto& v=*value;
    need(p::members(v,{"format","schema_version","producer_epoch","client_pid","endpoint"})&&
        v["format"]=="SysPane.NetworkController"&&v["schema_version"]=="0.1.0","network.bootstrap");
    Bootstrap out;out.epoch=v.at("producer_epoch");out.endpoint=v.at("endpoint");
    need(p::identifier(out.epoch)&&v["client_pid"].is_string(),"network.identity");
    const auto client=p::decimal(v["client_pid"].get<std::string>());need(client&&*client,"network.client");out.client=*client;return out;
}
}
int run_network_controller(std::uint64_t parent,std::function<c::Policy()> policy,std::function<void()> before_read){
    try{
        need(os::unprivileged_context(),"network.context");os::arm_parent_lifetime(parent);::close(3);
        auto guardian=os::Stream::from_connected_socket(0,parent);const auto startup=bootstrap(guardian);
        if(!policy)policy=os::machine_policy;
        const auto baseline=policy();need(baseline.available,"network.policy");
        os::Listener listener(startup.endpoint);r::HealthLink health(guardian,false,"collector",startup.epoch,"");
        r::ProducerLease lease;std::uint64_t token=0,sequence=0,last_sent=0,publication=0,stop_at=0,last_policy=os::monotonic_ms();
        std::uint64_t last_clock=last_policy;bool stopping=false,had_subscription=false;
        std::optional<os::Stream> client;std::unique_ptr<p::Framer> decoder;std::unique_ptr<n::DemandSessions> sessions;
        std::unique_ptr<os::NetworkWatch> watch;std::unique_ptr<n::NetworkState> state;
        std::unique_ptr<collectors::NetworkTask> task;std::string sampled_utc;
        const auto check_policy=[&]{const auto current=policy();need(current.available&&same(current,baseline),"network.policy");last_policy=os::monotonic_ms();};
        const auto stop=[&]{
            if(stopping)return;
            stopping=true;stop_at=os::monotonic_ms();if(task)task->cancel();
            if(sessions)sessions->disconnect("C",stop_at);
        };
        // Catch before task destruction: a non-cooperative native read must not
        // block process exit in join(). The external guardian proves termination.
        try{
            for(;;){
                auto now=os::monotonic_ms();need(now>=last_clock,"network.clock");last_clock=now;
                if(stopping){
                    if(task&&task->done()){(void)task->finish();task.reset();}
                    if(!task)return 0;
                    need(now-stop_at<2000,"network.stop_timeout");
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));continue;
                }
                if(token){lease.tick(now);need(lease.view().alive,"network.guardian_expired");}
                for(const auto& event:health.poll(1)){
                    if(token){lease.tick(event.observed_ms);need(lease.view().alive,"network.guardian_expired");}
                    if(event.kind==r::HealthKind::ready){need(health.epoch()==startup.epoch,"network.epoch");token=lease.attach("guardian",startup.epoch,event.observed_ms).token;}
                    else if(event.kind==r::HealthKind::heartbeat)need(lease.heartbeat(token,event.value,event.observed_ms)==r::Code::accepted,"network.heartbeat");
                    else if(event.kind==r::HealthKind::shutdown)stop();
                    else throw p::Error("network.health_direction");
                }
                if(stopping)continue;
                now=os::monotonic_ms();if(now-last_policy>=100)check_policy();
                if(!health.ready())continue;
                if(!sequence||now-last_sent>=1000){need(sequence<std::numeric_limits<std::uint64_t>::max(),"network.sequence");health.heartbeat(sequence++);last_sent=now;}
                if(!client){
                    try{client=listener.accept_ready(startup.client);}catch(const os::IpcError&){continue;}
                    if(!client)continue;
                    check_policy();const auto clock=client->measurement_clock();
                    c::TelemetrySource source{"producer:network","inspector","operational"};
                    source.document_version="0.2.0";source.clock_id=clock.clock_id;source.clock_scope=clock.local_scope;
                    n::DemandSource catalog{"network","collection.network",1000,2500,"",{}};n::DemandRequest request;request.channel="inspector";
                    for(const auto& metric:n::network_metrics()){catalog.fields.push_back({metric.field,"operational"});request.selections.push_back({metric.field,{}});}
                    sessions=std::make_unique<n::DemandSessions>(startup.epoch,0,baseline,source,std::vector<n::DemandSource>{catalog},n::DemandLimits{32,64,1});
                    sessions->open("C",client->peer().principal,{true,"console",{"console"}},request,client->connected_ms());
                    decoder=std::make_unique<p::Framer>();state=std::make_unique<n::NetworkState>(startup.epoch,clock.clock_id,clock.local_scope);
                }
                std::array<char,16384> bytes{};const auto got=client->read(bytes.data(),bytes.size(),1);
                if(got.eof){decoder->eof();stop();continue;}
                std::vector<std::string> incoming;std::size_t input_bytes=0;
                decoder->feed({bytes.data(),got.bytes},got.observed_ms,[&](auto raw){
                    need(incoming.size()<16&&raw.size()<=2097152-input_bytes,"network.input_capacity");input_bytes+=raw.size();incoming.emplace_back(raw);
                });
                decoder->tick(os::monotonic_ms());
                for(const auto& raw:incoming){
                    check_policy();const auto message=p::decode(raw);
                    need(message.type=="hello"||message.type=="heartbeat"||message.type=="subscribe"||message.type=="unsubscribe"||message.type=="shutdown","network.direction");
                    if(message.type=="hello"){
                        const auto offer=p::handshake(message.body);
                        const std::set<std::string> features={"telemetry.snapshot","telemetry.measured-time"};
                        for(const auto& feature:offer.required)need(features.count(feature),"network.feature");
                        for(const auto& feature:offer.optional)need(features.count(feature),"network.feature");
                    }
                    sessions->receive("C",raw,os::monotonic_ms());decoder->restrict_limit(sessions->frame_bound("C"));
                    need(!sessions->closed("C")||message.type=="shutdown","network.session");
                    if(message.type=="unsubscribe"||message.type=="shutdown"){stop();break;}
                }
                if(stopping)continue;
                sessions->tick(os::monotonic_ms());const auto subscription=sessions->subscription("C");
                if(had_subscription&&!subscription){stop();continue;}
                need(!sessions->closed("C"),"network.session");
                if(task)for(const auto& job:sessions->outstanding())if(job.ticket==task->ticket&&job.cancelled){
                    task->cancel();throw p::Error("network.acquisition_timeout");
                }
                if(task&&task->done()){
                    const auto ticket=task->ticket,revision=task->revision;auto completed=task->finish();task.reset();
                    need(sessions->complete(ticket,os::monotonic_ms())==n::DemandCode::accepted,"network.obsolete_read");
                    if(subscription){
                        need(completed.acquired.continuity,"network.watch_gap");
                        for(const auto& e:completed.acquired.indications)need(state->indicate(e.key,e.removed)==n::NetworkStateCode::accepted,"network.indication");
                        const auto result=state->commit(ticket,revision,completed.acquired.sample,completed.begin,completed.end);
                        need(result==n::NetworkStateCode::accepted||result==n::NetworkStateCode::dirty||result==n::NetworkStateCode::source_failed,"network.source");
                        if(result==n::NetworkStateCode::accepted)sampled_utc=completed.sampled_utc;
                        if(result!=n::NetworkStateCode::dirty&&state->sample()){
                            need(publication<std::numeric_limits<std::uint64_t>::max(),"network.publication");
                            const auto doc=n::network_document(*state->sample(),publication+1,sampled_utc,completed.sampled_utc,state->current());
                            check_policy();
                            need(sessions->offer("C",subscription->ticket,"network:"+std::to_string(publication+1),doc,{},os::monotonic_ms()),"network.offer");++publication;
                        }
                    }
                }
                if(subscription){
                    had_subscription=true;
                    if(!watch){watch=std::make_unique<os::NetworkWatch>();need(watch->active(),"network.watch");}
                    if(!task)if(const auto job=sessions->take(os::monotonic_ms())){
                        need(state->demand(job->ticket)==n::NetworkStateCode::accepted,"network.demand");
                        task=std::make_unique<collectors::NetworkTask>(*watch,job->ticket,state->revision(),[&]{
                            const auto clock=client->measurement_clock();return model::Tick{startup.epoch,clock.nanoseconds,clock.clock_id,clock.local_scope};
                        },false,0,before_read);
                    }
                }
                for(unsigned i=0;i<4;++i){
                    check_policy();const auto payload=sessions->pop("C",os::monotonic_ms());if(!payload)break;
                    client->write(p::frame(*payload,sessions->frame_bound("C")),100);
                }
            }
        }catch(...){std::_Exit(125);}
    }catch(...){const char message[]="network controller startup failed\n";(void)::write(2,message,sizeof(message)-1);return 2;}
}
}
