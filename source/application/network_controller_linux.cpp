#include "network_controller_linux.hpp"
#include "network_task_linux.hpp"
#include "network_publication.hpp"
#include "processor_publication.hpp"
#include "processor_task_linux.hpp"
#include "measurement_owner.hpp"
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
int run_network_controller(std::uint64_t parent,std::function<c::Policy()> policy,std::function<void()> before_read,
    std::function<os::WatchedNetworkResult(const os::NetworkRequest&)> read,
    std::function<os::LinuxProcessorCapture(const os::ProcessorRequest&)> processor_read){
    try{
        need(os::unprivileged_context(),"network.context");os::arm_parent_lifetime(parent);::close(3);
        auto guardian=os::Stream::from_connected_socket(0,parent);const auto startup=bootstrap(guardian);
        if(!policy)policy=os::machine_policy;
        const auto baseline=policy();need(baseline.available,"network.policy");
        os::Listener listener(startup.endpoint);r::HealthLink health(guardian,false,"collector",startup.epoch,"");
        r::ProducerLease lease;std::uint64_t token=0,sequence=0,last_sent=0,publication=0,stop_at=0,last_policy=os::monotonic_ms();
        std::uint64_t last_clock=last_policy;bool stopping=false,had_subscription=false;
        std::optional<os::Stream> client;std::unique_ptr<p::Framer> decoder;std::unique_ptr<n::DemandSessions> sessions;
        std::shared_ptr<collectors::MeasurementOwner> measurement_owner;
        std::unique_ptr<os::NetworkWatch> watch;std::unique_ptr<n::NetworkState> state;
        std::unique_ptr<collectors::NetworkTask> task;std::string sampled_utc;
        std::unique_ptr<collectors::ProcessorTask> processor_task;
        std::unique_ptr<n::ProcessorState> processor_state;
        std::unique_ptr<n::LinuxProcessorPublisher> processor_publisher;
        std::optional<os::LinuxProcessorCapture> processor_topology;
        std::optional<p::Json> network_cache,processor_cache;
        std::string processor_utc;bool processor_enabled=false,hello_seen=false;
        const auto check_policy=[&]{const auto current=policy();if(!current.available||!same(current,baseline))std::_Exit(126);last_policy=os::monotonic_ms();};
        const auto stop=[&]{
            if(stopping)return;
            stopping=true;stop_at=os::monotonic_ms();if(task)task->cancel();if(processor_task)processor_task->cancel();
            if(sessions)sessions->disconnect("C",stop_at);
        };
        // Catch before task destruction: a non-cooperative native read must not
        // block process exit in join(). The external guardian proves termination.
        try{
            for(;;){
                auto now=os::monotonic_ms();need(now>=last_clock,"network.clock");last_clock=now;
                if(stopping){
                    if(task&&task->done()){(void)task->finish();task.reset();}
                    if(processor_task&&processor_task->done()){(void)processor_task->finish();processor_task.reset();}
                    if(!task&&!processor_task)return 0;
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
                    check_policy();measurement_owner=std::make_shared<collectors::MeasurementOwner>([&]{
                        const auto native=client->measurement_clock();return model::Tick{startup.epoch,native.nanoseconds,native.clock_id,native.local_scope};
                    });const auto clock=(*measurement_owner)();
                    decoder=std::make_unique<p::Framer>();state=std::make_unique<n::NetworkState>(startup.epoch,clock.clock_id,clock.clock_scope);
                    processor_state=std::make_unique<n::ProcessorState>(startup.epoch,clock.clock_id,clock.clock_scope,"linux:execution-ticks-v1");
                    processor_publisher=std::make_unique<n::LinuxProcessorPublisher>(startup.epoch,clock.clock_id,clock.clock_scope);
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
                        need(!hello_seen,"network.hello_repeated");hello_seen=true;
                        const auto offer=p::handshake(message.body);
                        const std::set<std::string> features={"telemetry.snapshot","telemetry.measured-time","telemetry.monotonic-replay","telemetry.processor"};
                        for(const auto& feature:offer.required)need(features.count(feature),"network.feature");
                        for(const auto& feature:offer.optional)need(features.count(feature),"network.feature");
                        processor_enabled=offer.required.count("telemetry.processor")||offer.optional.count("telemetry.processor");
                        const auto clock=(*measurement_owner)();c::TelemetrySource source{"producer:network","inspector","operational"};
                        source.document_version="0.2.0";source.clock_id=clock.clock_id;source.clock_scope=clock.clock_scope;source.monotonic_replay=true;source.processor=true;
                        n::DemandSource network{"network","collection.network",1000,2500,"",{}};
                        n::DemandSource cpu{"processor","collection.processor",1000,2500,"sampling.resources_ms",{}};
                        n::DemandRequest request;request.channel="inspector";
                        for(const auto& metric:n::network_metrics()){network.fields.push_back({metric.field,"operational"});if(!baseline.denied_capabilities.count("collection.network"))request.selections.push_back({metric.field,{}});}
                        for(const auto& metric:n::processor_metrics()){cpu.fields.push_back({metric.field,"operational"});if(processor_enabled&&!baseline.denied_capabilities.count("collection.processor"))request.selections.push_back({metric.field,{}});}
                        need(!request.selections.empty(),"network.policy");
                        sessions=std::make_unique<n::DemandSessions>(startup.epoch,0,baseline,source,std::vector<n::DemandSource>{network,cpu},n::DemandLimits{32,64,2});
                        sessions->open("C",client->peer().principal,{true,"console",{"console"}},request,client->connected_ms());
                    }
                    need(static_cast<bool>(sessions),"network.hello_required");
                    sessions->receive("C",raw,os::monotonic_ms());decoder->restrict_limit(sessions->frame_bound("C"));
                    need(!sessions->closed("C")||message.type=="shutdown","network.session");
                    if(message.type=="unsubscribe"||message.type=="shutdown"){stop();break;}
                }
                if(stopping)continue;
                if(!sessions){need(os::monotonic_ms()-client->connected_ms()<5000,"network.hello_timeout");continue;}
                sessions->tick(os::monotonic_ms());const auto subscription=sessions->subscription("C");
                if(had_subscription&&!subscription){stop();continue;}
                need(!sessions->closed("C"),"network.session");
                if(task)for(const auto& job:sessions->outstanding())if(job.ticket==task->ticket&&job.cancelled){
                    task->cancel();throw p::Error("network.acquisition_timeout");
                }
                if(processor_task)for(const auto& job:sessions->outstanding())if(job.ticket==processor_task->ticket&&job.cancelled){
                    processor_task->cancel();throw p::Error("processor.acquisition_timeout");
                }
                const auto publish=[&](const std::string& attempted){
                    need(publication<std::numeric_limits<std::uint64_t>::max(),"network.publication");
                    if(processor_enabled&&!processor_cache)processor_cache=processor_publisher->document(*processor_state,nullptr,publication+1,"",attempted,baseline.denied_capabilities.count("collection.processor")!=0);
                    const auto doc=n::host_document(network_cache,processor_enabled?processor_cache:std::optional<p::Json>{},publication+1,startup.epoch,attempted);
                    check_policy();const auto prefix=subscription->binding.negotiated.features.count("telemetry.monotonic-replay")?"sample:":"network:";
                    need(sessions->offer("C",subscription->ticket,prefix+std::to_string(publication+1),doc,{},os::monotonic_ms()),"network.offer");++publication;
                };
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
                            network_cache=n::network_document(*state->sample(),publication+1,sampled_utc,completed.sampled_utc,state->current());
                            publish(completed.sampled_utc);
                        }
                    }
                }
                if(processor_task&&processor_task->done()){
                    const auto ticket=processor_task->ticket,plan=processor_task->plan;auto completed=processor_task->finish();processor_task.reset();
                    check_policy();need(sessions->complete(ticket,os::monotonic_ms())==n::DemandCode::accepted,"processor.obsolete_read");
                    if(subscription){
                        if(completed.acquired.code==os::ProcessorReadCode::success&&processor_topology&&!os::same_linux_topology(*processor_topology,completed.acquired))need(processor_state->topology_changed()==n::ProcessorStateCode::accepted,"processor.topology");
                        const auto result=processor_state->commit(plan,processor_state->revision(),completed.acquired.counters(),completed.begin,completed.end);
                        need(result==n::ProcessorStateCode::accepted||result==n::ProcessorStateCode::source_failed||result==n::ProcessorStateCode::invalid||result==n::ProcessorStateCode::capacity,"processor.source");
                        if(result==n::ProcessorStateCode::accepted){processor_utc=completed.sampled_utc;processor_topology=std::move(completed.acquired);}
                        processor_cache=processor_publisher->document(*processor_state,processor_topology?&*processor_topology:nullptr,publication+1,processor_utc,completed.sampled_utc);
                        publish(completed.sampled_utc);
                    }
                }
                if(subscription){
                    had_subscription=true;
                    for(unsigned dispatch=0;dispatch<2;++dispatch)if(const auto job=sessions->take(os::monotonic_ms())){
                        const auto clock=[measurement_owner]{return (*measurement_owner)();};
                        check_policy();
                        if(job->plan.source=="network"){
                            need(!task,"network.task_overlap");if(!watch){watch=std::make_unique<os::NetworkWatch>();need(watch->active(),"network.watch");}
                            need(state->demand(job->ticket)==n::NetworkStateCode::accepted,"network.demand");
                            task=std::make_unique<collectors::NetworkTask>(*watch,job->ticket,state->revision(),clock,false,0,before_read,read);
                        }else{
                            need(job->plan.source=="processor"&&processor_enabled&&!processor_task,"processor.demand");
                            need(processor_state->demand(job->plan_revision)==n::ProcessorStateCode::accepted,"processor.demand");
                            processor_task=std::make_unique<collectors::ProcessorTask>(job->ticket,job->plan_revision,clock,processor_read);
                        }
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
