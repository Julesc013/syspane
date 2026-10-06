#pragma once
#include "authored.hpp"
#include "ledger.hpp"

namespace syspane::configuration {
struct CommitIdentity {std::string principal,epoch,request,body;};
struct Committed {Authored documents;std::optional<CommitIdentity> identity;};
enum class Publication { unchanged, durable, unknown };
// Native implementation owns its writer lock and immutable generations. A guard
// rejection throws before changing the selecting record. unknown poisons this
// store/coordinator until a fresh native open validates coherent recovery.
class GenerationStore {
public:
    virtual ~GenerationStore()=default;
    virtual Committed load()const=0;
    virtual std::optional<Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const=0;
    virtual Publication publish(const Committed& next,const std::function<void()>& guard)=0;
};
class Transactions {
public:
    Transactions(GenerationStore& store,std::string epoch,std::function<void(const Authored&)> prepare_resources);
    Json submit(const std::string& principal,const std::string& connection,std::string body,const Authority& authority,
                const std::function<Policy()>& policy,std::uint64_t now,const std::function<bool()>& cancelled=[] {return false;});
    Json reconcile(const std::string& principal,const std::string& original_epoch,const std::string& request,
                   const Authority& authority,const Policy& policy)const;
    const Authored& authored()const{return current_.documents;} // Trusted owner only; external projection requires policy.
    bool faulted()const{return faulted_;}
private:
    Json reply(const std::string& request,const char* outcome,const char* code="",std::optional<std::uint64_t> committed={})const;
    GenerationStore& store_;
    std::string epoch_;
    Committed current_;
    protocol::Ledger ledger_;
    std::function<void(const Authored&)> prepare_resources_;
    bool faulted_=false;
};
}
