#pragma once
#include "policy.hpp"

namespace syspane::configuration {
struct CommandAdmission { std::uint64_t ticket=0; Json reply; };
struct CommandDelivery { std::string connection; std::uint64_t lifetime,ticket; Json reply; };
// Session-loop interface. Implementation owns the sole command ledger. Native
// worker dispatch/stop proof is a separate trusted composition interface.
class CommandService {
public:
    virtual ~CommandService()=default;
    virtual bool supports_resources()const{return false;}
    virtual bool supports_large_commands()const{return false;}
    virtual bool supports_edit_locks()const{return false;}
    virtual bool supports_theme_overrides()const{return false;}
    virtual bool supports_visibility()const{return false;}
    virtual void attach(const std::string& epoch,std::uint64_t revision,Policy policy)=0;
    virtual CommandAdmission submit(const std::string& principal,const std::string& connection,std::uint64_t lifetime,
        const Authority&,std::string body,bool transactions,std::uint64_t now)=0;
    virtual Json query(const std::string& principal,const Authority&,const std::string& request,bool cancel,std::uint64_t now)=0;
    virtual Json reconcile(const std::string& principal,const Authority&,const Json& query,std::uint64_t now)=0;
    virtual std::optional<CommandDelivery> delivery(std::uint64_t now)=0;
    virtual void policy(Policy)=0;
    virtual void invalidate()=0;
    virtual std::size_t request_count()const=0;
    virtual std::uint64_t revision()const=0;
};
}
