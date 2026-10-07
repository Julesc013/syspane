#pragma once
#include "content.hpp"
#include "ledger.hpp"
#include <vector>

namespace syspane::configuration {
struct CommitIdentity {std::string principal,epoch,request,body;};
struct Committed {Authored documents;std::optional<CommitIdentity> identity;ResourceSnapshot resources{};};
struct ResourceProvider {
    std::set<std::string> capabilities;
    std::function<ResourceSnapshot(const Authored&,const Json& selection)> prepare;
};
struct CommitReceipt {CommitIdentity identity;std::uint64_t revision;};
// Pure formatting; the caller must authorize disclosure of the receipt first.
Json committed_result(const std::string& request,const std::string& epoch,std::uint64_t revision);
enum class Publication { unchanged, durable, unknown };
// Native implementation owns its writer lock and immutable generations. A guard
// rejection throws before changing the selecting record. unknown poisons this
// store/coordinator until a fresh native open validates coherent recovery.
class GenerationStore {
public:
    virtual ~GenerationStore()=default;
    virtual Committed load()const=0;
    virtual std::vector<CommitReceipt> receipts()const=0;
    virtual std::optional<Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const=0;
    virtual Publication publish(const Committed& next,const std::function<void()>& guard)=0;
};
// Store outlives the provider. Invoke on the store's serialized transaction worker.
ResourceProvider make_resource_provider(GenerationStore& store,std::set<std::string> capabilities,
    std::function<std::vector<ContentPackage>()> imports={});
class Transactions {
public:
    Transactions(GenerationStore& store,std::string epoch,std::function<void(const Authored&)> prepare_resources);
    Transactions(GenerationStore& store,std::string epoch,ResourceProvider resources);
    bool supports_resources()const{return static_cast<bool>(resource_provider_.prepare);}
    bool supports_edit_locks()const{return supports_resources()&&resource_provider_.capabilities.count("scene.edit-locks");}
    Json submit(const std::string& principal,const std::string& connection,std::string body,const Authority& authority,
                const std::function<Policy()>& policy,std::uint64_t now,const std::function<bool()>& cancelled=[] {return false;});
    Json reconcile(const std::string& principal,const std::string& original_epoch,const std::string& request,
                   const Authority& authority,const Policy& policy)const;
    const Authored& authored()const{return current_.documents;} // Trusted owner only; external projection requires policy.
    bool faulted()const{return faulted_;}
private:
    friend class AsyncCommands;
    std::vector<CommitReceipt> receipts()const;
    Json submit_impl(const std::string&,const std::string&,std::string,const Authority&,
        const std::function<Policy()>&,std::uint64_t,const std::function<bool()>&,bool,const std::function<void()>&);
    Json reply(const std::string& request,const char* outcome,const char* code="",std::optional<std::uint64_t> committed={})const;
    GenerationStore& store_;
    std::string epoch_;
    Committed current_;
    protocol::Ledger ledger_;
    std::function<void(const Authored&)> prepare_resources_;
    ResourceProvider resource_provider_;
    bool faulted_=false;
};
}
