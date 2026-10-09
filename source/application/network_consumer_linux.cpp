#include "network_consumer_linux.hpp"
#include "network_publication.hpp"
#include "local_ipc.hpp"
#include <array>
#include <limits>

namespace syspane::application {
namespace p=protocol;namespace os=platform;namespace r=recovery;
namespace {
void need(bool ok,const char* code){if(!ok)throw p::Error(code);}
p::Handshake offer(){
    p::Handshake h;h.role="console";h.epoch="consumer:network";
    for(const char* document:{"telemetry","snapshot","observation"})h.documents.emplace(document,"0.2.0");
    h.required={"telemetry.snapshot","telemetry.measured-time"};return h;
}
p::Json hello(const p::Handshake& h){
    p::Json docs=p::Json::array();for(const auto& pair:h.documents)docs.push_back({{"document",pair.first},{"version",pair.second}});
    return {{"wire_major",0},{"wire_minor",h.minor},{"role",h.role},{"producer_epoch",h.epoch},{"max_frame_bytes",h.max_frame_bytes},
        {"document_versions",docs},{"required_features",h.required},{"optional_features",p::Json::array()}};
}
}
struct LinuxNetworkConsumer::Impl {
    std::function<bool()> current;os::Stream stream;p::Framer decoder;
    std::string epoch,id;std::unique_ptr<r::TelemetryReceiver> receiver;
    std::uint64_t last_sent=0,next_sequence=0;std::optional<std::uint64_t> sent;
    explicit Impl(std::string endpoint,std::uint64_t process,std::string e,r::DeliveryScope scope,configuration::Policy policy,
        std::function<bool()> guard):current(std::move(guard)),stream(connect(endpoint,process,current)),epoch(std::move(e)){
        const auto started=stream.connected_ms();const auto h=offer();send("hello",hello(h));
        while(!receiver){
            need(os::monotonic_ms()-started<5000,"network.consumer_handshake_timeout");
            input([&](std::string_view raw,std::uint64_t now,const model::Tick& tick){
                need(!receiver&&now-started<5000,"network.consumer_handshake");const auto m=p::decode(raw);
                need(m.type=="welcome"&&m.producer_epoch==epoch,"network.consumer_welcome");const auto welcome=p::handshake(m.body);
                need(welcome.role=="console"&&welcome.epoch==epoch&&welcome.minor==1&&welcome.max_frame_bytes==h.max_frame_bytes&&
                    welcome.documents==h.documents&&welcome.required.empty()&&welcome.optional==h.required,"network.consumer_negotiation");
                id=m.connection_id;
                p::TelemetryBinding binding{{welcome.minor,welcome.max_frame_bytes,welcome.documents,welcome.optional},id,epoch,
                    "producer:network","S","inspector","operational",policy.revision,p::TelemetryDirection::producer_to_consumer,
                    "0.2.0",tick.clock_id,tick.clock_scope};
                receiver=std::make_unique<r::TelemetryReceiver>(scope,policy,runtime::network_metrics(),std::move(binding),now);
                need(receiver->sample(tick,now)==r::DataCode::accepted,"network.consumer_clock");
            });
        }
        const auto snapshot=receiver->view(os::monotonic_ms());need(snapshot.binding&&snapshot.connected,"network.consumer_expired");
        send("subscribe",{{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","producer:network"},
            {"policy_revision",std::to_string(policy.revision)},{"channel","inspector"},{"classification","operational"},{"clock_id",snapshot.binding->clock_id}});
    }
    static os::Stream connect(const std::string& endpoint,std::uint64_t process,const std::function<bool()>& current){
        need(process&&current&&current(),"network.consumer_withdrawn");return os::Stream::connect(endpoint,process);
    }
    void valid(){need(current(),"network.consumer_withdrawn");}
    model::Tick clock(){const auto tick=stream.measurement_clock();return {epoch,tick.nanoseconds,tick.clock_id,tick.local_scope};}
    void send(const char* kind,p::Json body){
        valid();p::Json message={{"type",kind},{"body",std::move(body)}};
        if(!id.empty()){message["connection_id"]=id;message["producer_epoch"]=epoch;}
        stream.write(p::frame(message.dump()),100);valid();
    }
    void input(const std::function<void(std::string_view,std::uint64_t,const model::Tick&)>& consume){
        valid();std::array<char,16384> bytes{};const auto got=stream.read(bytes.data(),bytes.size(),10);valid();
        need(!got.eof,"network.consumer_eof");std::size_t count=0,total=0;
        decoder.feed({bytes.data(),got.bytes},got.observed_ms,[&](auto raw){
            need(count++<16&&raw.size()<=2097152-total,"network.consumer_input_capacity");total+=raw.size();valid();
            // Stamp completion at the native reader, before parsing/importing.
            // GUI delivery never rewrites these identities or admits a future value.
            const auto tick=clock();const auto now=os::monotonic_ms();consume(raw,now,tick);valid();
        });decoder.tick(os::monotonic_ms());
    }
    r::TelemetryDelivery poll(){
        try{
            valid();auto now=os::monotonic_ms();need(receiver->view(now).connected,"network.consumer_expired");
            if(!sent||now-last_sent>=1000){
                need(next_sequence<std::numeric_limits<std::uint64_t>::max(),"network.consumer_sequence");
                send("heartbeat",{{"sequence",std::to_string(next_sequence)}});sent=next_sequence++;last_sent=now;
            }
            input([&](std::string_view raw,std::uint64_t received,const model::Tick& tick){
                const auto message=p::decode(raw);need(message.connection_id==id&&message.producer_epoch==epoch,"network.consumer_scope");
                if(message.type=="snapshot"){
                    const auto result=receiver->receive(raw,received,tick);
                    need(result.code==r::DataCode::accepted||result.code==r::DataCode::duplicate,"network.consumer_snapshot");
                }else if(message.type=="heartbeat"){
                    const auto sequence=p::decimal(message.body.at("sequence").get<std::string>());
                    need(sequence&&sent&&*sequence<=*sent,"network.consumer_heartbeat");
                    const auto result=receiver->heartbeat(*sequence,received);
                    need(result==r::DataCode::accepted||result==r::DataCode::duplicate,"network.consumer_lease");
                }else throw p::Error("network.consumer_direction");
            });
            const auto tick=clock();now=os::monotonic_ms();
            need(receiver->sample(tick,now)==r::DataCode::accepted,"network.consumer_clock");valid();return receiver->view(now);
        }catch(...){receiver->disconnect(os::monotonic_ms());throw;}
    }
};
LinuxNetworkConsumer::LinuxNetworkConsumer(std::string endpoint,std::uint64_t process,std::string epoch,r::DeliveryScope scope,
    configuration::Policy policy,std::function<bool()> current):impl_(std::make_unique<Impl>(std::move(endpoint),process,std::move(epoch),scope,std::move(policy),std::move(current))){}
LinuxNetworkConsumer::~LinuxNetworkConsumer()=default;
r::TelemetryDelivery LinuxNetworkConsumer::poll(){return impl_->poll();}
}
