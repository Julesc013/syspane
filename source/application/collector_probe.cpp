#include "child.hpp"
#include "health_link.hpp"
#include "data_view.hpp"
#include "network_publication.hpp"
#include "network_view.hpp"
#include "network_watch.hpp"
#include "session.hpp"
#include <array>
#include <chrono>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <thread>

namespace os=syspane::platform;namespace r=syspane::recovery;namespace n=syspane::runtime;
namespace p=syspane::protocol;namespace c=syspane::configuration;namespace m=syspane::model;
using p::Json;
namespace {
void need(bool ok,const char* code){if(!ok)throw p::Error(code);}
void emit(Json value){value["observed_ms"]=os::monotonic_ms();std::cout<<value.dump()<<std::endl;}
void pause(unsigned ms){std::this_thread::sleep_for(std::chrono::milliseconds(ms));}
std::string utc(){
    const auto value=std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());std::tm calendar{};
    need(::gmtime_r(&value,&calendar)!=nullptr,"collector.utc");std::array<char,32> buffer{};
    need(std::strftime(buffer.data(),buffer.size(),"%Y-%m-%dT%H:%M:%SZ",&calendar)>0,"collector.utc");return buffer.data();
}
c::Policy policy(bool permitted=true){c::Policy value;value.available=permitted;value.revision=permitted?7:8;
    value.disclosure[{"desktop","desktop"}]={"operational"};value.disclosure[{"desktop","accessibility"}]={"operational"};return value;}
Json hello(){return {{"type","hello"},{"body",{{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","collector:consumer"},
    {"max_frame_bytes",p::frame_limit},{"document_versions",Json::array({{{"document","telemetry"},{"version","0.2.0"}},
    {{"document","snapshot"},{"version","0.2.0"}},{{"document","observation"},{"version","0.2.0"}}})},
    {"required_features",{"telemetry.snapshot","telemetry.measured-time"}},{"optional_features",Json::array()}}}};}
class DataPipe {
public:
    explicit DataPipe(os::Stream& stream):stream_(stream){}
    std::vector<std::string> poll(){std::vector<std::string> values;std::array<char,16384> buffer{};
        const auto input=stream_.read(buffer.data(),buffer.size(),1);if(input.eof){decoder_.eof();throw p::Error("collector.data_eof");}
        if(input.bytes)decoder_.feed(std::string_view(buffer.data(),input.bytes),input.observed_ms,[&](auto payload){
            need(values.size()<16,"collector.input_capacity");values.emplace_back(payload);});
        decoder_.tick(input.observed_ms);return values;}
    void send(const std::string& payload){stream_.write(p::frame(payload),100);}
private:os::Stream& stream_;p::Framer decoder_;
};
m::Tick tick(os::Stream& stream,const std::string& epoch){const auto now=stream.measurement_clock();return {epoch,now.nanoseconds,now.clock_id,now.local_scope};}

void worker(const std::string& address,const std::string& mode,const std::string& epoch,std::uint64_t parent){
    os::arm_parent_lifetime(parent);
    auto health_stream=os::Stream::connect(address+"/h/s",parent);r::HealthLink health(health_stream,false,"collector",epoch,"");
    auto data_stream=os::Stream::connect(address+"/d/s",parent);DataPipe pipe(data_stream);
    const auto clock=data_stream.measurement_clock();
    c::TelemetrySource source{"producer:network","desktop","operational"};source.document_version="0.2.0";source.clock_id=clock.clock_id;source.clock_scope=clock.local_scope;
    c::Sessions sessions(epoch,0,policy(),source);sessions.open("D",data_stream.peer().principal,{true,"desktop",{"desktop"}},data_stream.connected_ms());
    r::ProducerLease parent_lease;std::uint64_t parent_token=0,sent=0,last_sent=0,last_attempt=0,publication=0,delivered=0;
    std::unique_ptr<os::NetworkWatch> watch;std::unique_ptr<n::NetworkState> state;
    std::string sampled_utc;Json replay;bool replayed=false,revoked=false,retired=false;
    const auto started=os::monotonic_ms();std::atomic_bool cancel{false};
    while(os::monotonic_ms()-started<25000){
        for(const auto& event:health.poll()){
            if(event.kind==r::HealthKind::ready)parent_token=parent_lease.attach("supervisor",epoch,event.observed_ms).token;
            else if(event.kind==r::HealthKind::heartbeat){const auto code=parent_lease.heartbeat(parent_token,event.value,event.observed_ms);need(code==r::Code::accepted||code==r::Code::duplicate,"collector.parent_heartbeat");}
            else if(event.kind==r::HealthKind::shutdown)return;
            else throw p::Error("collector.health_direction");
        }
        const auto now=os::monotonic_ms();
        if(health.ready()){
            parent_lease.tick(now);need(parent_lease.view().alive,"collector.parent_expired");
            if(!sent||now-last_sent>=1000){health.heartbeat(sent++);last_sent=now;}
        }
        for(const auto& payload:pipe.poll()){
            sessions.receive("D",payload,os::monotonic_ms());
            if(mode=="crash"&&delivered==1){const auto message=p::decode(payload);
                if(message.type=="heartbeat"&&message.body["sequence"]=="0")std::_Exit(73);}
        }
        sessions.tick(os::monotonic_ms());
        if(mode=="revoke"&&delivered&&!revoked){sessions.policy(policy(false),os::monotonic_ms());revoked=true;}
        if(sessions.closed("D"))return;
        auto subscription=sessions.subscription("D");
        if(!subscription){if(state){state.reset();watch.reset();replay=Json();sampled_utc.clear();retired=true;}}
        else {
            need(!retired,"collector.retired_source");
            if(!state){watch=std::make_unique<os::NetworkWatch>();need(watch->active(),"collector.watch_unavailable");
                state=std::make_unique<n::NetworkState>(epoch,clock.clock_id,clock.local_scope);}
            need(state->demand(subscription->ticket)==n::NetworkStateCode::accepted,"collector.demand");
            if(mode=="replay"&&delivered==1&&!replayed){
                need(sessions.offer("D",subscription->ticket,"network:1",replay,{},os::monotonic_ms()),"collector.replay_offer");replayed=true;
            } else if(!publication||now-last_attempt>=1000){
                last_attempt=now;const auto attempt_utc=utc();const auto begin=tick(data_stream,epoch);
                const auto revision=state->revision();os::NetworkResult raw;
                if(mode=="failure"&&publication==1)raw={os::NetworkCode::failed,5};
                else {
                    auto acquired=watch->read({std::chrono::steady_clock::now()+std::chrono::seconds(2),cancel});
                    need(acquired.continuity,"collector.watch_gap");
                    for(const auto& event:acquired.indications)need(state->indicate(event.key,event.removed)==n::NetworkStateCode::accepted,"collector.indication");
                    raw=std::move(acquired.sample);
                }
                const auto end=tick(data_stream,epoch);
                // Pending events drained at acquisition start may advance the owner's
                // revision; that candidate is conservatively retried next cadence.
                const auto result=state->commit(subscription->ticket,revision,raw,begin,end);
                need(result==n::NetworkStateCode::accepted||result==n::NetworkStateCode::dirty||result==n::NetworkStateCode::source_failed,"collector.source_contract");
                if(result==n::NetworkStateCode::accepted)sampled_utc=attempt_utc;
                if(result!=n::NetworkStateCode::dirty){
                    need(static_cast<bool>(state->sample()),"collector.no_inventory");
                    const auto doc=n::network_document(*state->sample(),publication+1,sampled_utc,attempt_utc,state->current());
                    sessions.tick(os::monotonic_ms());const auto active=sessions.subscription("D");
                    if(active&&active->ticket==subscription->ticket){
                        need(sessions.offer("D",active->ticket,"network:"+std::to_string(publication+1),doc,{},os::monotonic_ms()),"collector.offer");
                        ++publication;if(publication==1&&mode=="replay")replay=doc;
                    }
                }
            }
        }
        while(auto payload=sessions.pop("D",os::monotonic_ms())){
            const bool sample=p::decode(*payload).type=="snapshot";pipe.send(*payload);
            if(sample){++delivered;if(mode=="hang"&&delivered==1)for(;;)pause(100);}
        }
    }
    throw p::Error("collector.worker_deadline");
}

void projection(r::DataView& view,const char* event,std::uint64_t pid,const std::string& epoch,const std::optional<m::Tick>& measured){
    Json result{{"event",event},{"pid",pid},{"payload",false}};
    view.project(os::monotonic_ms(),[&](const auto& snapshot,const auto& lease){
        result["payload"]=true;result["retained"]=lease.presentation==r::Presentation::retained;
        result["snapshot"]=Json::parse(snapshot.reported_document);
    });emit(std::move(result));
    // Explicit finite development selection; no persisted selector or native cache.
    const auto render=[&](const auto& frame){
        Json report{{"event","presentation"},{"phase",event},{"pid",pid},{"code",static_cast<int>(frame.code)},
            {"measurement_now_ns",measured?Json(std::to_string(measured->nanoseconds)):Json()},{"generation",frame.generation},{"epoch",frame.selected.epoch},{"entity",frame.selected.entity},
            {"lease",static_cast<int>(frame.presentation)},{"fields",Json::array()}};
        if(frame.code==syspane::rendering::NetworkViewCode::ready){
            for(const auto& field:frame.fields){
                report["fields"].push_back({{"value",field.value?Json(*field.value):Json()},
                    {"unit",field.unit},{"acquisition",static_cast<int>(field.acquisition)},
                    {"reported",static_cast<int>(field.reported)},{"effective",static_cast<int>(field.effective)},
                    {"measured_ns",field.measured_at?Json(std::to_string(field.measured_at->nanoseconds)):Json()},
                    {"age_ns",field.age_ns?Json(std::to_string(*field.age_ns)):Json()},
                    {"interval_ns",field.interval_ns?Json(std::to_string(*field.interval_ns)):Json()},
                    {"error_code",field.error_code}});
            }
        }
        // The admitted test pipe consumes the frame synchronously; nothing is cached.
        emit(std::move(report));
    };
    const syspane::rendering::NetworkSelection selected{"producer:network",epoch,"network:interface:1"};
    if(measured)syspane::rendering::project_network(view,selected,os::monotonic_ms(),*measured,render);
    else syspane::rendering::project_network_retained(view,selected,os::monotonic_ms(),render);
}
void stopped(os::Child& child,const os::ChildExit& status,bool forced){emit({{"event","stopped"},{"pid",child.id()},{"code",status.code},{"signaled",status.signaled},{"forced",forced},{"os_confirmed",true}});}
void supervisor(const std::string& address,const std::string& scenario){
    need(std::set<std::string>{"live","failure","replay","hang","crash","unsubscribe","revoke","parent-loss"}.count(scenario),"collector.scenario");
    os::Listener health_listener(address+"/h/s"),data_listener(address+"/d/s");
    need(health_listener.access_controls_verified()&&data_listener.access_controls_verified(),"collector.endpoint_controls");
    emit({{"event","ready"},{"unprivileged",true},{"endpoint_controls",true}});
    r::RestartGate gate(0);r::DataView view({true,"desktop",{"desktop"}},policy(),"desktop","operational",n::network_metrics());
    const auto started=os::monotonic_ms();
    for(unsigned attempt=0;attempt<2;++attempt){
        for(;;){need(os::monotonic_ms()-started<30000,"collector.deadline");const auto code=gate.start(os::monotonic_ms());
            if(code==r::Code::accepted)break;
            need(code==r::Code::not_due,"collector.restart_gate");pause(10);}
        const auto epoch="collector:"+std::to_string(os::current_process_id())+":"+std::to_string(attempt+1);
        auto child=os::Child::launch_self({"worker",address,attempt?"live":scenario,epoch,std::to_string(os::current_process_id())});
        emit({{"event","spawned"},{"pid",child.id()},{"attempt",attempt},{"epoch",epoch}});pause(250);
        auto health_stream=health_listener.accept(child.id());r::HealthLink health(health_stream,true,"collector",epoch,"H");
        auto data_stream=data_listener.accept(child.id());DataPipe pipe(data_stream);pipe.send(hello().dump());
        const auto local=data_stream.measurement_clock();r::ProducerLease lease;
        std::uint64_t token=0,data_token=0,last_received=0,sent=0,last_sent=0,received=0,data_sequence=0;
        p::TelemetryBinding binding{};bool ready=false,done=false,released=false,unsubscribed=false,parent_loss_announced=false;
        std::optional<std::uint64_t> barrier;
        std::string reason;
        const auto send=[&](const char* type,Json body){need(ready,"collector.data_not_ready");
            pipe.send(Json{{"type",type},{"connection_id","D"},{"producer_epoch",epoch},{"body",std::move(body)}}.dump());};
        try {
            while(!done){
                need(os::monotonic_ms()-started<30000,"collector.deadline");
                for(const auto& event:health.poll()){
                    if(event.kind==r::HealthKind::ready){token=lease.attach("producer:network",epoch,event.observed_ms).token;last_received=event.observed_ms;
                        emit({{"event","authenticated"},{"pid",child.id()},{"health_peer",health_stream.peer().process_id},{"data_peer",data_stream.peer().process_id}});}
                    else if(event.kind==r::HealthKind::heartbeat){const auto code=lease.heartbeat(token,event.value,event.observed_ms);
                        need(code==r::Code::accepted||code==r::Code::duplicate,"collector.heartbeat");
                        if(code==r::Code::accepted){last_received=event.observed_ms;if(data_token)view.heartbeat(data_token,7,event.value,event.observed_ms);}
                    } else throw p::Error("collector.health_direction");
                }
                const auto now=os::monotonic_ms();
                if(health.ready()){
                    lease.tick(now);view.status(now);
                    if(!lease.view().alive){reason="producer.expired";break;}
                    if(!sent||now-last_sent>=1000){health.heartbeat(sent++);last_sent=now;
                        if(ready&&(attempt||scenario!="crash"||received))send("heartbeat",{{"sequence",std::to_string(data_sequence++)}});}
                }
                for(const auto& bytes:pipe.poll()){
                    const auto message=p::decode(bytes);
                    if(message.type=="welcome"){
                        need(!ready&&message.connection_id=="D"&&message.producer_epoch==epoch,"collector.welcome");
                        const auto remote=p::handshake(message.body);need(remote.role=="console","collector.server_role");
                        const auto selected=p::negotiate(remote,p::handshake(hello()["body"]),{"desktop"});
                        binding={selected,"D",epoch,"producer:network","S","desktop","operational",7,p::TelemetryDirection::producer_to_consumer,"0.2.0",local.clock_id,local.local_scope};
                        const auto attached=view.attach_wire(binding,os::monotonic_ms());need(attached.code==r::DataCode::accepted,"collector.attach");data_token=attached.token;ready=true;
                        send("subscribe",{{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","producer:network"},{"policy_revision","7"},
                            {"channel","desktop"},{"classification","operational"},{"clock_id",local.clock_id}});
                    } else if(message.type=="snapshot"){
                        need(ready&&!released,"collector.unexpected_data");const auto measured=tick(data_stream,epoch);
                        const auto result=view.receive(data_token,7,bytes,os::monotonic_ms(),measured);
                        need(result.code==r::DataCode::accepted||result.code==r::DataCode::duplicate,"collector.import");++received;
                        emit({{"event","imported"},{"pid",child.id()},{"duplicate",result.code==r::DataCode::duplicate},{"body",message.body_bytes},
                            {"now_ns",std::to_string(measured.nanoseconds)},{"clock_id",measured.clock_id}});
                        projection(view,"projection",child.id(),epoch,measured);
                        const auto mode=attempt?"live":scenario;
                        if(mode=="crash"&&received==1){need(data_sequence==0,"collector.crash_barrier");send("heartbeat",{{"sequence",std::to_string(data_sequence++)}});}
                        else if(mode=="unsubscribe"&&!unsubscribed){send("unsubscribe",{{"schema_version","0.2.0"},{"subscription_id","S"},{"clock_id",local.clock_id}});
                            barrier=data_sequence++;send("heartbeat",{{"sequence",std::to_string(*barrier)}});unsubscribed=true;}
                        else if(mode=="parent-loss"&&!parent_loss_announced){emit({{"event","parent_loss_ready"},{"pid",child.id()}});parent_loss_announced=true;}
                        else if((mode=="live"&&received==2)||((mode=="failure"||mode=="replay")&&received==3))done=true;
                    } else if(message.type=="gap"){
                        need(scenario=="revoke"&&message.body["reason"]=="policy_changed","collector.gap");
                        view.policy(policy(false),os::monotonic_ms());projection(view,"revoked",child.id(),epoch,{});released=true;
                    } else if(message.type=="heartbeat"){
                        if(barrier&&message.body["sequence"]==std::to_string(*barrier))released=true;
                    } else throw p::Error("collector.data_direction");
                }
                if(released){emit({{"event","demand_released"},{"pid",child.id()}});
                    const auto until=os::monotonic_ms();while(os::monotonic_ms()-until<500){
                        for(const auto& bytes:pipe.poll())need(p::decode(bytes).type=="heartbeat","collector.data_after_release");
                        pause(10);}
                    done=true;
                }
                if(child.wait(0)){reason="child.exited";break;}
            }
        }catch(const p::Error& error){reason=error.what();}catch(const os::IpcError& error){reason=error.what();}
        if(done&&reason.empty()){
            health.shutdown();const auto status=child.wait(1000);need(status&&status->code==0&&!status->signaled,"collector.graceful_exit");
            need(gate.stopped(r::StopProof::confirmed,os::monotonic_ms())==r::Code::accepted,"collector.graceful_gate");
            stopped(child,*status,false);emit({{"event","complete"},{"launches",attempt+1}});return;
        }
        const bool hung=scenario=="hang"&&attempt==0&&reason=="producer.expired";
        const bool crashed=scenario=="crash"&&attempt==0&&received==1&&
            (reason=="health.eof"||reason=="collector.data_eof"||reason=="child.exited");
        if(!hung&&!crashed){
            emit({{"event","unexpected_failure"},{"pid",child.id()},{"reason",reason}});throw p::Error("collector.unexpected_failure");
        }
        const auto fault_time=os::monotonic_ms();view.disconnect(data_token,7,fault_time);projection(view,"retained",child.id(),epoch,{});
        if(crashed){
            const auto status=child.wait(100);need(status&&status->code==73&&!status->signaled,"collector.crash_exit");
            need(gate.failed(r::Failure::crashed,r::StopProof::confirmed,fault_time)==r::Code::accepted,"collector.crash_gate");
            emit({{"event","fault"},{"pid",child.id()},{"reason","child.crashed"},{"backoff_ms",gate.view().backoff_ms}});
            stopped(child,*status,false);continue;
        }
        need(gate.failed(r::Failure::producer_expired,r::StopProof::unconfirmed,fault_time)==r::Code::accepted,"collector.failure_gate");
        need(gate.start(fault_time)==r::Code::quarantined,"collector.quarantine");
        emit({{"event","fault"},{"pid",child.id()},{"reason",reason},{"since_heartbeat_ms",fault_time-last_received},{"backoff_ms",gate.view().backoff_ms}});
        health.shutdown();auto status=child.wait(250);bool forced=false;
        if(!status){child.request_stop();forced=true;status=child.wait(2000);}
        need(status.has_value(),"collector.stop_unconfirmed");need(gate.confirm_stopped(os::monotonic_ms())==r::Code::accepted,"collector.confirm_stopped");stopped(child,*status,forced);
    }
    throw p::Error("collector.launch_limit");
}
}
int main(int argc,char** argv){try{need(os::unprivileged_context(),"collector.privileged_context");
    if(argc==4&&std::string(argv[1])=="supervisor")supervisor(argv[2],argv[3]);
    else if(argc==6&&std::string(argv[1])=="worker"){const auto parent=p::decimal(argv[5]);need(parent&&*parent,"collector.parent");worker(argv[2],argv[3],argv[4],*parent);}
    else return 2;
    return 0;
}catch(const std::exception& error){emit({{"event","error"},{"code",error.what()}});return 1;}}
