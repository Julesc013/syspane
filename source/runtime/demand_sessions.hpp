#pragma once
#include "demand.hpp"
#include "session.hpp"

namespace syspane::runtime {
// Serialized trusted composition. Native callers own peer authentication, I/O,
// acquisition threads and stop proof; peers never supply the local request.
class DemandSessions {
public:
    DemandSessions(std::string epoch,std::uint64_t revision,configuration::Policy policy,
                   configuration::TelemetrySource source,std::vector<DemandSource> catalog,DemandLimits limits={});
    void open(const std::string& id,std::string principal,configuration::Authority authority,DemandRequest request,std::uint64_t now);
    void receive(const std::string& id,std::string_view payload,std::uint64_t now);
    std::optional<std::string> pop(const std::string& id,std::uint64_t now);
    bool offer(const std::string& id,std::uint64_t ticket,const std::string& record,const protocol::Json& snapshot,
               std::optional<std::uint64_t> base,std::uint64_t now);
    void disconnect(const std::string& id,std::uint64_t now);
    void policy(configuration::Policy next,std::uint64_t now);
    void tick(std::uint64_t now);
    bool closed(const std::string& id)const{return sessions_.closed(id);}
    std::string close_reason(const std::string& id)const{return sessions_.close_reason(id);}
    std::optional<configuration::Subscription> subscription(const std::string& id)const{return sessions_.subscription(id);}
    std::optional<DemandJob> take(std::uint64_t now);
    DemandCode complete(std::uint64_t ticket,std::uint64_t now);
    DemandCode confirm_stopped(std::uint64_t ticket){return demand_.confirm_stopped(ticket);}
    std::vector<DemandJob> outstanding()const{return demand_.outstanding();}
    std::size_t lease_count()const{return demand_.lease_count();}
private:
    struct Request {DemandRequest value;std::uint64_t lease=0;std::optional<std::uint64_t> heartbeat={};};
    void fail(std::uint64_t now);
    configuration::Sessions sessions_;
    DemandOwner demand_;
    std::map<std::string,Request> requests_;
};
}
