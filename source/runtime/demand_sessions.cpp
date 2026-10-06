#include "demand_sessions.hpp"

namespace syspane::runtime {
namespace c=configuration;namespace p=protocol;
DemandSessions::DemandSessions(std::string epoch,std::uint64_t revision,c::Policy policy,c::TelemetrySource source,
                               std::vector<DemandSource> catalog,DemandLimits limits)
    :sessions_(std::move(epoch),revision,policy,std::move(source)),demand_(std::move(catalog),std::move(policy),limits){}
void DemandSessions::fail(std::uint64_t now){
    (void)demand_.policy(c::Policy{},now);
    for(auto& entry:requests_){sessions_.reject_demand(entry.first);entry.second.lease=0;entry.second.heartbeat.reset();}
}
void DemandSessions::tick(std::uint64_t now){
    try{
        if(demand_.tick(now)!=DemandCode::accepted)throw p::Error("demand.fault");
        sessions_.tick(now);
        for(auto& entry:requests_){
            auto& request=entry.second;const auto active=sessions_.subscription(entry.first);
            if(!active){
                if(request.lease)(void)demand_.release(request.lease,now);
                request.lease=0;request.heartbeat.reset();continue;
            }
            if(!request.lease){
                const auto admitted=request.value.channel==active->binding.channel?
                    demand_.admit(request.value,active->authority,now):DemandAdmission{DemandCode::denied,0};
                if(admitted.code!=DemandCode::accepted){sessions_.reject_demand(entry.first);continue;}
                request.lease=admitted.lease;request.heartbeat=active->heartbeat;
            }else if(active->heartbeat!=request.heartbeat){
                if(!active->heartbeat||demand_.renew(request.lease,*active->heartbeat,now)!=DemandCode::accepted)
                    throw p::Error("demand.renewal");
                request.heartbeat=active->heartbeat;
            }
        }
        if(demand_.fault())throw p::Error("demand.fault");
    }catch(...){fail(now);throw;}
}
void DemandSessions::open(const std::string& id,std::string principal,c::Authority authority,DemandRequest request,std::uint64_t now){
    tick(now);
    if(request.selections.empty()||request.selections.size()>64||request.maximum_age_ms<100||request.maximum_age_ms>3600000||
       request.priority>3||!p::identifier(request.channel))throw p::Error("demand.request");
    for(const auto& selected:request.selections)
        if(!p::identifier(selected.field)||(selected.entity&&!p::identifier(*selected.entity)))throw p::Error("demand.request");
    sessions_.open(id,std::move(principal),std::move(authority),now);
    try{requests_.emplace(id,Request{std::move(request),0,{}});}
    catch(...){sessions_.disconnect(id);fail(now);throw;}
}
void DemandSessions::receive(const std::string& id,std::string_view payload,std::uint64_t now){
    tick(now);
    if(sessions_.closed(id))throw p::Error("session.closed");
    try{sessions_.receive(id,payload,now);tick(now);}catch(...){fail(now);throw;}
}
std::optional<std::string> DemandSessions::pop(const std::string& id,std::uint64_t now){
    tick(now);try{auto value=sessions_.pop(id,now);tick(now);return value;}catch(...){fail(now);throw;}
}
bool DemandSessions::offer(const std::string& id,std::uint64_t ticket,const std::string& record,const p::Json& snapshot,
                          std::optional<std::uint64_t> base,std::uint64_t now){
    if(!sessions_.current_subscription(id,ticket))return false;
    tick(now);try{const auto result=sessions_.offer(id,ticket,record,snapshot,base,now);tick(now);return result;}catch(...){fail(now);throw;}
}
void DemandSessions::disconnect(const std::string& id,std::uint64_t now){
    const auto it=requests_.find(id);
    if(it!=requests_.end()){if(it->second.lease)(void)demand_.release(it->second.lease,now);requests_.erase(it);}
    sessions_.disconnect(id);tick(now);
}
void DemandSessions::policy(c::Policy next,std::uint64_t now){
    try{
        const auto result=demand_.policy(next,now);
        for(auto& entry:requests_){entry.second.lease=0;entry.second.heartbeat.reset();}
        sessions_.policy(std::move(next),now);
        if(result!=DemandCode::accepted)throw p::Error("demand.policy");
        tick(now);
    }catch(...){fail(now);throw;}
}
std::optional<DemandJob> DemandSessions::take(std::uint64_t now){
    tick(now);try{return demand_.take(now);}catch(...){fail(now);throw;}
}
DemandCode DemandSessions::complete(std::uint64_t ticket,std::uint64_t now){
    tick(now);try{return demand_.complete(ticket,now);}catch(...){fail(now);throw;}
}
}
