#include "async_commands.hpp"
#include "reconciliation.hpp"
#include <limits>

namespace syspane::configuration {
using protocol::Error;
namespace {
Decision decision(const std::string& code){
    if(code=="policy.denied"||code=="policy.forced")return {"denied",code};
    if(code=="revision.changed"||code=="policy.changed")return {"conflict",code};
    return {"invalid",code};
}
}
AsyncCommands::AsyncCommands(GenerationStore& store,std::string epoch,std::function<void(const Authored&)> prepare)
    :epoch_(std::move(epoch)),transactions_(store,epoch_,std::move(prepare)),receipts_(transactions_.receipts()),revision_(authored_revision(transactions_.authored())){}
AsyncCommands::AsyncCommands(GenerationStore& store,std::string epoch,ResourceProvider prepare,RecoveryProvider recovery)
    :epoch_(std::move(epoch)),transactions_(store,epoch_,std::move(prepare)),receipts_(transactions_.receipts()),revision_(authored_revision(transactions_.authored())),recovery_provider_(std::move(recovery)){
    image_=prepare_image();
}
ProfileSnapshot AsyncCommands::prepare_image(){
    if(!transactions_.current_.resources)return {};
    auto recovery=recovery_provider_?recovery_provider_(transactions_.current_):std::optional<ProfileRecoveryData>{};
    return std::make_shared<ProfileImage>(transactions_.current_,transactions_.resource_provider_.capabilities,std::move(recovery));
}
void AsyncCommands::attach(const std::string& epoch,std::uint64_t revision,Policy policy){
    std::lock_guard<std::mutex> lock(mutex_);
    if(attached_||invalid_||epoch!=epoch_||revision!=revision_)throw Error("command.owner");
    policy_=std::move(policy);attached_=true;
}
Policy AsyncCommands::snapshot()const{std::lock_guard<std::mutex> lock(mutex_);return policy_;}
void AsyncCommands::invalidate(){std::lock_guard<std::mutex> lock(mutex_);invalid_=true;policy_.available=false;profile_.invalidate();image_.reset();}
void AsyncCommands::policy(Policy next){
    std::lock_guard<std::mutex> lock(mutex_);
    profile_.invalidate();
    if(!attached_||invalid_||next.revision<=policy_.revision){invalid_=true;policy_.available=false;throw Error("policy.revision");}
    policy_=std::move(next);
}
void AsyncCommands::advance(std::uint64_t now){
    if(last_&&now<*last_){invalidate();throw Error("clock.regressed");}last_=now;
}
Json AsyncCommands::reply(const std::string& request,const char* outcome,const char* code)const{return result({outcome,code},request,epoch_,revision_);}
Decision AsyncCommands::authorize(const std::string& body,const Authority& authority)const{
    try{
        auto command=parse_command(body);validate_command(command);const auto policy=snapshot();
        command["expected_revision"]=std::to_string(revision_);command["policy_generation"]=std::to_string(policy.revision);
        authorize_authored(command,authority,policy,revision_);return {"preview",""};
    }catch(const Error& e){return decision(e.what());}
}
CommandAdmission AsyncCommands::submit(const std::string& principal,const std::string& connection,std::uint64_t lifetime,
    const Authority& authority,std::string body,bool transactions,std::uint64_t now){
    advance(now);
    const auto command=protocol::parse(body,protocol::ParseProfile::large_command);
    const auto request=command.at("request_id").get<std::string>();
    try{(void)parse_command(body);validate_command(command);}catch(const Error& e){const auto d=decision(e.what());return {0,result(d,request,epoch_,revision_)};}
    const auto authorized=authorize(body,authority);
    if(authorized.outcome!="preview")return {0,result(authorized,request,epoch_,revision_)};
    // Negotiation restricts this connection before a retained outcome is disclosed.
    if(!transactions){
        auto check=command;check["expected_revision"]=std::to_string(revision_);check["policy_generation"]=std::to_string(snapshot().revision);
        const auto d=preview(check,authority,snapshot(),revision_);
        if(d.outcome!="preview")return {0,result(d,request,epoch_,revision_)};
    }
    if(const auto prior=ledger_.get(principal,request,now)){
        if(prior->body!=body)return {0,reply(request,"conflict","request.changed")};
        return {0,prior->finished_ms?protocol::parse(prior->result):reply(request,"unknown","request.pending")};
    }
    {
        std::lock_guard<std::mutex> lock(mutex_);
        if(!attached_||invalid_)return {0,reply(request,"denied","policy.denied")};
        if(storage_fault_)return {0,reply(request,"unknown","storage.reconcile")};
        if(jobs_.size()+ready_.size()>=128||tickets_==std::numeric_limits<std::uint64_t>::max())return {0,reply(request,"busy","request.capacity")};
    }
    auto job=std::make_shared<Job>(Job{tickets_+1,lifetime,principal,connection,request,std::move(body),authority});
    const auto admission=ledger_.admit(principal,connection,request,job->body,now,(command["schema_version"]=="0.5.0"||command["schema_version"]=="0.6.0"||command["schema_version"]=="0.7.0"||command["schema_version"]=="0.8.0"));
    if(admission!=protocol::Admission::admitted)return {0,reply(request,"busy","request.capacity")};
    std::lock_guard<std::mutex> lock(mutex_);jobs_.emplace(job->ticket,job);++tickets_;return {job->ticket,{}};
}
Json AsyncCommands::query(const std::string& principal,const Authority& authority,const std::string& request,bool cancel,std::uint64_t now){
    advance(now);const auto policy=snapshot();
    const auto concealed=[&](const Decision& d){
        auto value=result({"unknown",d.code},request,epoch_,revision_);
        value["error"]["message"]="Current policy does not permit this result.";return value;
    };
    if(!policy.available||!authority.authenticated||!authority.role_grants.count(authority.role)||
       (authority.role!="console"&&authority.role!="desktop"&&authority.role!="saver_settings"))return concealed({"denied","policy.denied"});
    const auto record=ledger_.get(principal,request,now);
    if(!record)return reply(request,"unknown","request.reconcile");
    const auto authorized=authorize(record->body,authority);
    if(authorized.outcome!="preview")return concealed(authorized);
    if(record->finished_ms)return protocol::parse(record->result);
    if(cancel){
        std::lock_guard<std::mutex> lock(mutex_);
        for(auto& entry:jobs_)if(entry.second->principal==principal&&entry.second->request==request&&!entry.second->committing)entry.second->cancelled=true;
    }
    return reply(request,"unknown","request.pending");
}
std::optional<std::uint64_t> AsyncCommands::take(){
    std::lock_guard<std::mutex> lock(mutex_);
    if(active_||jobs_.empty())return {};
    active_=jobs_.begin()->first;return active_;
}
Json AsyncCommands::reconcile(const std::string& principal,const Authority& authority,const Json& query,std::uint64_t now){
    advance(now);protocol::validate_reconciliation_request(query);
    const auto request=query["request_id"].get<std::string>(),original=query["original_producer_epoch"].get<std::string>();
    const auto wrapped=[&](Json answer){auto value=query;value["result"]=std::move(answer);return value;};
    const auto current_policy=snapshot();
    if(!current_policy.available||!authority.authenticated||!authority.role_grants.count(authority.role)||
       (authority.role!="console"&&authority.role!="desktop"&&authority.role!="saver_settings")||current_policy.denied_capabilities.count("result.reconcile"))
        return wrapped(reply(request,"unknown","policy.denied"));
    if(storage_fault_)return wrapped(reply(request,"unknown","storage.reconcile"));
    for(const auto& row:receipts_)if(row.identity.principal==principal&&row.identity.epoch==original&&row.identity.request==request){
        const auto authorized=authorize(row.identity.body,authority);
        if(authorized.outcome!="preview")return wrapped(result({"unknown",authorized.code},request,epoch_,revision_));
        return wrapped(committed_result(request,epoch_,row.revision));
    }
    if(original==epoch_)if(const auto record=ledger_.get(principal,request,now))if(!record->finished_ms){
        const auto authorized=authorize(record->body,authority);
        return wrapped(reply(request,"unknown",authorized.outcome=="preview"?"request.pending":authorized.code.c_str()));
    }
    return wrapped(reply(request,"unknown","request.reconcile"));
}
AsyncCommands::Completion AsyncCommands::run(std::uint64_t ticket){
    std::shared_ptr<Job> job;
    {
        std::lock_guard<std::mutex> lock(mutex_);
        const auto found=jobs_.find(ticket);
        if(!ticket||active_!=ticket||found==jobs_.end()||found->second->started)throw Error("command.worker");
        job=found->second;job->started=true;
    }
    const auto cancelled=[&]{std::lock_guard<std::mutex> lock(mutex_);return job->cancelled||invalid_;};
    Json answer;std::vector<CommitReceipt> receipts;ProfileSnapshot image;
    try{
        answer=transactions_.submit_impl(job->principal,job->connection,job->body,job->authority,[&]{return snapshot();},0,cancelled,false,[&]{
            std::lock_guard<std::mutex> lock(mutex_);
            if(job->cancelled||invalid_)throw Error("request.cancelled");
            authorize_authored(parse_command(job->body),job->authority,policy_,authored_revision(transactions_.authored()));
            job->committing=true;
        });
        if(!transactions_.faulted()){
            receipts=transactions_.receipts();
            image=prepare_image();
        }
    }catch(...){
        // A native exception may follow publication; never manufacture unsaved facts.
        answer=result({"unknown","storage.reconcile"},job->request,epoch_,0);
        return Completion(this,ticket,std::move(answer),authored_revision(transactions_.authored()),true);
    }
    return Completion(this,ticket,std::move(answer),authored_revision(transactions_.authored()),transactions_.faulted(),std::move(receipts),std::move(image));
}
bool AsyncCommands::finish(Completion&& done,std::uint64_t now,bool confirmed_stopped){
    if(!confirmed_stopped||done.owner!=this)return false;
    std::lock_guard<std::mutex> lock(mutex_);
    const auto found=jobs_.find(done.ticket);
    if(!done.ticket||active_!=done.ticket||found==jobs_.end()||!found->second->started)return false;
    // Stale completions cannot advance the owner's clock or release another slot.
    if(last_&&now<*last_){invalid_=true;policy_.available=false;throw Error("clock.regressed");}last_=now;
    const auto& job=found->second;
    ledger_.finish(job->principal,job->request,done.reply.dump(),done.reply["outcome"]=="accepted",now);
    revision_=done.revision;storage_fault_=storage_fault_||done.fault;
    receipts_=storage_fault_?std::vector<CommitReceipt>{}:std::move(done.receipts);
    image_=storage_fault_||invalid_?ProfileSnapshot{}:std::move(done.image);
    if(storage_fault_||invalid_)profile_.invalidate();
    ready_.push_back(job);jobs_.erase(found);active_=0;done.ticket=0;return true;
}
std::optional<CommandDelivery> AsyncCommands::delivery(std::uint64_t now){
    advance(now);if(ready_.empty())return {};
    auto job=ready_.front();ready_.pop_front();
    return CommandDelivery{job->connection,job->lifetime,job->ticket,query(job->principal,job->authority,job->request,false,now)};
}
bool AsyncCommands::may_disclose_profile(const Authority& authority)const{
    if(!attached_||invalid_||storage_fault_||!image_)return false;
    try{image_->authorize(authority,snapshot());return true;}catch(const protocol::Error&){return false;}
}
Json AsyncCommands::read_profile(const std::string& connection,std::uint64_t lifetime,const Authority& authority,const Json& request,std::uint64_t now){
    if(request.value("schema_version",Json())=="0.2.0"&&!supports_profile_recovery())throw Error("feature.unsupported");
    advance(now);return profile_.receive(connection,lifetime,authority,snapshot(),!invalid_&&!storage_fault_?image_:ProfileSnapshot{},request,now,epoch_);
}
}
