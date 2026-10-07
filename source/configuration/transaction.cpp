#include "transaction.hpp"
#include <limits>

namespace syspane::configuration {
namespace {
using protocol::Error;
void require(bool value,const char* code){if(!value)throw Error(code);}
bool writer(const Authority& a,const Policy& p){
    return p.available&&a.authenticated&&a.role_grants.count(a.role)&&(a.role=="console"||a.role=="desktop"||a.role=="saver_settings");
}
const char* outcome(const std::string& code){
    if(code=="policy.changed"||code=="revision.changed")return "conflict";
    if(code=="policy.denied"||code=="policy.forced")return "denied";
    if(code=="request.cancelled")return "cancelled";
    return "invalid";
}
}
ResourceProvider make_resource_provider(GenerationStore& store,std::set<std::string> capabilities,
    std::function<std::vector<ContentPackage>()> imports){
    return {std::move(capabilities),[&store,imports=std::move(imports)](const Authored& candidate,const Json& selection){
        const auto current=store.load();
        if(current.resources&&current.resources->selection()==selection){
            std::vector<ContentPackage> packages;for(const auto& package:current.resources->packages())packages.push_back(*package);
            return ContentCatalog(std::move(packages)).resources(selection,candidate);
        }
        require(static_cast<bool>(imports),"resource.unavailable");return ContentCatalog(imports()).resources(selection,candidate);
    }};
}
Transactions::Transactions(GenerationStore& store,std::string epoch,std::function<void(const Authored&)> prepare_resources)
    :store_(store),epoch_(std::move(epoch)),current_(store.load()),prepare_resources_(std::move(prepare_resources)){
    require(protocol::identifier(epoch_)&&static_cast<bool>(prepare_resources_),"transaction.owner");validate_authored(current_.documents);
}
Transactions::Transactions(GenerationStore& store,std::string epoch,ResourceProvider resources)
    :store_(store),epoch_(std::move(epoch)),current_(store.load()),resource_provider_(std::move(resources)){
    require(protocol::identifier(epoch_)&&static_cast<bool>(resource_provider_.prepare),"transaction.owner");validate_authored(current_.documents);
}
Json Transactions::reply(const std::string& request,const char* status,const char* code,std::optional<std::uint64_t> committed)const{
    if(committed)return committed_result(request,epoch_,*committed);
    return result({status,code},request,epoch_,authored_revision(current_.documents));
}
Json committed_result(const std::string& request,const std::string& epoch,std::uint64_t revision){
    auto value=result({"preview",""},request,epoch,revision);
    value["outcome"]="accepted";value["stored"]=true;value["durable"]=true;
    value["activation"]=Json::array({{{"component","presentation"},{"state","pending"},{"reason","Activation has not been reported."}}});
    return value;
}
std::vector<CommitReceipt> Transactions::receipts()const{
    require(!faulted_,"storage.reconcile");const auto rows=store_.receipts();require(rows.size()<=2,"storage.receipts");
    std::vector<CommitReceipt> checked;
    for(const auto& row:rows){
        const auto& id=row.identity;
        require(protocol::identifier(id.principal)&&protocol::identifier(id.epoch)&&protocol::identifier(id.request)&&!id.body.empty()&&id.body.size()<=protocol::large_command_limit,"storage.receipts");
        const auto command=parse_command(id.body);validate_command(command);
        const auto expected=*protocol::decimal(command["expected_revision"].get<std::string>());
        require(command["intent"]=="commit"&&command["request_id"]==id.request&&expected<std::numeric_limits<std::uint64_t>::max()&&
            row.revision==expected+1&&row.revision<=authored_revision(current_.documents),"storage.receipts");
        bool duplicate=false;
        for(const auto& prior:checked)if(prior.identity.principal==id.principal&&prior.identity.epoch==id.epoch&&prior.identity.request==id.request){
            require(prior.identity.body==id.body&&prior.revision==row.revision,"storage.receipts");duplicate=true;
        }
        if(!duplicate)checked.push_back(row);
    }
    return checked;
}
Json Transactions::submit(const std::string& principal,const std::string& connection,std::string body,const Authority& authority,
                         const std::function<Policy()>& policy,std::uint64_t now,const std::function<bool()>& cancelled){
    return submit_impl(principal,connection,std::move(body),authority,policy,now,cancelled,true,[]{});
}
Json Transactions::submit_impl(const std::string& principal,const std::string& connection,std::string body,const Authority& authority,
                         const std::function<Policy()>& policy,std::uint64_t now,const std::function<bool()>& cancelled,
                         bool record,const std::function<void()>& permit){
    require(protocol::identifier(principal)&&protocol::identifier(connection),"transaction.scope");
    const auto command=parse_command(body);validate_command(command);const auto request=command["request_id"].get<std::string>();
    if(faulted_)return reply(request,"unknown","storage.reconcile");
    auto checked_policy=policy();
    if(!writer(authority,checked_policy))return reply(request,"denied","policy.denied");
    // Current authority applies to replay, but expected authored/policy generations
    // describe the original attempt and must not cause an already committed ID to execute again.
    auto authorization=command;authorization["policy_generation"]=std::to_string(checked_policy.revision);
    authorization["expected_revision"]=std::to_string(authored_revision(current_.documents));
    try{authorize_authored(authorization,authority,checked_policy,authored_revision(current_.documents));}
    catch(const Error& e){return reply(request,outcome(e.what()),e.what());}
    const auto retained=store_.reconcile(principal,epoch_,request);
    if(retained){
        require(retained->identity.has_value(),"storage.identity");
        if(retained->identity->body!=body)return reply(request,"conflict","request.changed");
        return reply(request,"accepted","",authored_revision(retained->documents));
    }
    const auto admission=record?ledger_.admit(principal,connection,request,body,now,command["schema_version"]=="0.5.0"):protocol::Admission::admitted;
    if(admission==protocol::Admission::conflict)return reply(request,"conflict","request.changed");
    if(admission==protocol::Admission::replay)return protocol::parse(ledger_.get(principal,request,now)->result);
    if(admission==protocol::Admission::busy||admission==protocol::Admission::pending)return reply(request,"busy","request.capacity");
    Json answer;
    bool did_commit=false;
    try{
        if(cancelled())throw Error("request.cancelled");
        auto candidate=prepare_authored(current_.documents,command,authority,checked_policy);
        ResourceSnapshot resources;
        if(command.contains("content")){
            require(supports_resources(),"resource.contract");resources=resource_provider_.prepare(candidate,command["content"]);
            require(resources&&resources->selection()==command["content"],"resource.selection");
            validate_resource_binding(*resources,candidate);authorize_resources(*resources,checked_policy,resource_provider_.capabilities);
        }else{
            require(!current_.resources&&static_cast<bool>(prepare_resources_),"resource.contract");prepare_resources_(candidate);
        }
        if(cancelled())throw Error("request.cancelled");
        if(command["intent"]=="preview")answer=reply(request,"preview");
        else{
            const auto old=authored_revision(current_.documents);require(old<std::numeric_limits<std::uint64_t>::max(),"revision.exhausted");
            candidate.settings["revision"]=candidate.scene["revision"]=std::to_string(old+1);
            Committed next{std::move(candidate),CommitIdentity{principal,epoch_,request,body},std::move(resources)};
            // Finish all fallible result construction before native publication.
            auto accepted=reply(request,"accepted","",old+1);
            const auto publication=store_.publish(next,[&]{
                if(cancelled())throw Error("request.cancelled");
                require(authored_revision(store_.load().documents)==old,"revision.changed");
                const auto current_policy=policy();authorize_authored(command,authority,current_policy,old);
                if(next.resources)authorize_resources(*next.resources,current_policy,resource_provider_.capabilities);
                permit();
            });
            if(publication==Publication::durable){current_=std::move(next);answer=std::move(accepted);did_commit=true;}
            else if(publication==Publication::unchanged)answer=reply(request,"invalid","storage.unsaved");
            else{faulted_=true;answer=reply(request,"unknown","storage.reconcile");}
        }
    }catch(const Error& e){answer=reply(request,outcome(e.what()),e.what());}
    catch(...){faulted_=true;throw;}
    if(record)ledger_.finish(principal,request,answer.dump(),did_commit,now);
    return answer;
}
Json Transactions::reconcile(const std::string& principal,const std::string& original_epoch,const std::string& request,
                             const Authority& authority,const Policy& policy)const{
    require(protocol::identifier(principal)&&protocol::identifier(original_epoch)&&protocol::identifier(request),"transaction.scope");
    if(!writer(authority,policy))return reply(request,"denied","policy.denied");
    if(faulted_)return reply(request,"unknown","storage.reconcile");
    const auto record=store_.reconcile(principal,original_epoch,request);
    if(!record)return reply(request,"unknown","request.reconcile");
    require(record->identity.has_value(),"storage.identity");
    auto command=parse_command(record->identity->body);validate_command(command);
    command["expected_revision"]=std::to_string(authored_revision(current_.documents));command["policy_generation"]=std::to_string(policy.revision);
    try{authorize_authored(command,authority,policy,authored_revision(current_.documents));}
    catch(const Error& e){return reply(request,outcome(e.what()),e.what());}
    return reply(request,"accepted","",authored_revision(record->documents));
}
}
