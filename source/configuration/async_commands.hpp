#pragma once
#include "command_service.hpp"
#include "transaction.hpp"
#include "profile_projection.hpp"
#include <deque>
#include <memory>
#include <mutex>

namespace syspane::configuration {
class AsyncCommands final:public CommandService {
public:
    struct Completion {
        Completion(Completion&&)=default;
        Completion& operator=(Completion&&)=default;
    private:
        friend class AsyncCommands;
        Completion(const AsyncCommands* o,std::uint64_t t,Json r,std::uint64_t v,bool f,std::vector<CommitReceipt> receipts={},ProfileSnapshot image={})
            :owner(o),ticket(t),reply(std::move(r)),revision(v),fault(f),receipts(std::move(receipts)),image(std::move(image)){}
        const AsyncCommands* owner;std::uint64_t ticket;Json reply;std::uint64_t revision;bool fault;
        std::vector<CommitReceipt> receipts;
        ProfileSnapshot image;
    };
    AsyncCommands(GenerationStore&,std::string epoch,std::function<void(const Authored&)>);
    AsyncCommands(GenerationStore&,std::string epoch,ResourceProvider);
    bool supports_resources()const override{return transactions_.supports_resources();}
    bool supports_large_commands()const override{return true;}
    bool supports_theme_overrides()const override{return transactions_.supports_theme_overrides();}
    bool supports_visibility()const override{return transactions_.supports_visibility();}
    bool supports_edit_locks()const override{return transactions_.supports_edit_locks();}
    bool supports_profile()const override{return transactions_.supports_resources();}
    bool may_disclose_profile(const Authority&)const override;
    Json read_profile(const std::string&,std::uint64_t,const Authority&,const Json&,std::uint64_t)override;
    bool profile_expired(const std::string& id,std::uint64_t lifetime,std::uint64_t now)const override{return profile_.expired(id,lifetime,now);}
    void drop_profile(const std::string& id,std::uint64_t lifetime)override{profile_.disconnect(id,lifetime);}
    void attach(const std::string&,std::uint64_t,Policy)override;
    CommandAdmission submit(const std::string&,const std::string&,std::uint64_t,const Authority&,std::string,bool,std::uint64_t)override;
    Json query(const std::string&,const Authority&,const std::string&,bool,std::uint64_t)override;
    Json reconcile(const std::string&,const Authority&,const Json&,std::uint64_t)override;
    std::optional<CommandDelivery> delivery(std::uint64_t)override;
    void policy(Policy)override;
    void invalidate()override;
    std::size_t request_count()const override{return ledger_.size();}
    std::uint64_t revision()const override{return revision_;}
    // Owning loop only; a latched native fault requires a fresh process/store.
    bool storage_faulted()const{return storage_fault_;}
    // All methods on the owning loop except run(), which executes exactly once
    // on the one native worker. finish requires actual join/process-stop proof.
    std::optional<std::uint64_t> take();
    Completion run(std::uint64_t ticket);
    bool finish(Completion&&,std::uint64_t now,bool confirmed_stopped);
private:
    struct Job {
        std::uint64_t ticket,lifetime;std::string principal,connection,request,body;Authority authority;
        bool cancelled=false,committing=false,started=false;
    };
    void advance(std::uint64_t);
    Json reply(const std::string&,const char*,const char* = "")const;
    Decision authorize(const std::string&,const Authority&)const;
    Policy snapshot()const;
    std::string epoch_;
    Transactions transactions_; // Worker-exclusive after attachment.
    std::vector<CommitReceipt> receipts_; // Owning-loop immutable view, replaced only after actual worker stop.
    std::uint64_t revision_,tickets_=0,active_=0;
    protocol::Ledger ledger_;
    std::optional<std::uint64_t> last_;
    mutable std::mutex mutex_;
    Policy policy_;
    bool attached_=false,invalid_=false,storage_fault_=false;
    std::map<std::uint64_t,std::shared_ptr<Job>> jobs_;
    std::deque<std::shared_ptr<Job>> ready_;
    ProfileSnapshot image_;ProfileTransfer profile_;
};
}
