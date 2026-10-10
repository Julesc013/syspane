#include "telemetry_delivery.hpp"
#include <limits>

namespace syspane::recovery {
bool TelemetryDelivery::live(DeliveryScope current,std::uint64_t now)const{
    return connected&&binding&&current.profile&&current.generation&&current.profile==scope.profile&&
        current.generation==scope.generation&&now<live_until_ms;
}
bool TelemetryDelivery::deliverable(DeliveryScope current,std::uint64_t now)const{
    return live(current,now)&&frame&&frame->ordinal&&clock&&now>=clock_ms&&now-clock_ms<=250&&now>=frame->received_ms;
}
TelemetryReceiver::TelemetryReceiver(DeliveryScope scope,configuration::Policy policy,std::vector<model::Metric> metrics,
    protocol::TelemetryBinding binding,std::uint64_t now):
    model_({true,"console",{"console"}},policy,"inspector","operational",std::move(metrics)),last_ms_(now){
    if(!scope.profile||!scope.generation||policy.denied_capabilities.count("collection.network")||binding.document_version!="0.2.0")
        throw protocol::Error("delivery.admission");
    const auto attached=model_.attach_wire(binding,now);
    if(attached.code!=DataCode::accepted)throw protocol::Error("delivery.binding");
    token_=attached.token;delivery_.scope=scope;delivery_.binding=std::make_shared<const protocol::TelemetryBinding>(std::move(binding));
    delivery_.connected=true;
    if(!deadline(now))throw protocol::Error("delivery.deadline");
}
bool TelemetryReceiver::deadline(std::uint64_t now){
    if(now>std::numeric_limits<std::uint64_t>::max()-3000){disconnect(now);return false;}
    delivery_.live_until_ms=now+3000;return true;
}
DataCode TelemetryReceiver::advance(std::uint64_t now){
    if(!delivery_.connected)return DataCode::closed;
    if(now<last_ms_){disconnect(now);return DataCode::clock_fault;}
    last_ms_=now;
    if(now>=delivery_.live_until_ms||!model_.status(now).alive){disconnect(now);return DataCode::closed;}
    return DataCode::accepted;
}
DataCode TelemetryReceiver::sample(const model::Tick& tick,std::uint64_t now){
    const auto state=advance(now);if(state!=DataCode::accepted)return state;
    const auto& b=*delivery_.binding;
    if(tick.epoch!=b.epoch||tick.clock_id!=b.clock_id||tick.clock_scope!=b.clock_scope||
       (delivery_.clock&&tick.nanoseconds<delivery_.clock->nanoseconds)){
        disconnect(now);return DataCode::clock_fault;
    }
    delivery_.clock=tick;delivery_.clock_ms=now;return DataCode::accepted;
}
DataResult TelemetryReceiver::receive(std::string_view bytes,std::uint64_t now,const model::Tick& tick){
    const auto state=sample(tick,now);if(state!=DataCode::accepted)return {state};
    if(bytes.size()>protocol::frame_limit){disconnect(now);return {DataCode::capacity};}
    try{
        // The slot is a complete-state replacement. Even a valid delta cannot
        // be dropped/coalesced into it without changing the protocol meaning.
        if(protocol::decode(bytes).type!="snapshot"){disconnect(now);return {DataCode::invalid};}
        const bool exhausted=ordinal_==std::numeric_limits<std::uint64_t>::max();
        auto next=std::make_shared<const DeliveredFrame>(DeliveredFrame{std::string(bytes),now,tick,exhausted?ordinal_:ordinal_+1});
        const auto result=model_.receive(token_,delivery_.binding->policy_revision,bytes,now,tick);
        if(result.code==DataCode::accepted){
            if(exhausted){disconnect(now);return {DataCode::capacity};}
            ++ordinal_;delivery_.frame=std::move(next);
        }
        else if(result.code!=DataCode::duplicate)disconnect(now);
        return result;
    }catch(const protocol::Error&){disconnect(now);return {DataCode::invalid};}
    catch(const std::bad_alloc&){disconnect(now);return {DataCode::capacity};}
}
DataCode TelemetryReceiver::heartbeat(std::uint64_t sequence,std::uint64_t now){
    const auto state=advance(now);if(state!=DataCode::accepted)return state;
    const auto result=model_.heartbeat(token_,delivery_.binding->policy_revision,sequence,now);
    if(result==DataCode::accepted){if(!deadline(now))return DataCode::clock_fault;delivery_.heartbeat=sequence;}
    else if(result!=DataCode::duplicate)disconnect(now);
    return result;
}
TelemetryDelivery TelemetryReceiver::view(std::uint64_t now){(void)advance(now);return delivery_;}
void TelemetryReceiver::disconnect(std::uint64_t now){
    delivery_.connected=false;delivery_.frame.reset();delivery_.clock.reset();delivery_.heartbeat.reset();delivery_.live_until_ms=0;
    if(token_)(void)model_.disconnect(token_,delivery_.binding->policy_revision,now);
}
void TelemetryReceiver::withdraw(std::uint64_t now){disconnect(now);(void)model_.policy({},now);}
}
