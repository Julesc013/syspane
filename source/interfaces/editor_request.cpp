#include "editor_draft.hpp"
#include <limits>
#include <type_traits>

namespace syspane::interfaces {
namespace {
namespace c=configuration;
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
}
struct RequestWork::Impl {
    std::unique_ptr<SettingsDraft> draft;
    std::weak_ptr<const char> validity;
    std::string intent,request;
    std::uint64_t revision=0;
};
struct RequestPrepared::Impl {
    std::weak_ptr<const char> validity;
    EditRequest request;Json command;std::string intent;
    std::uint64_t revision=0;
};
RequestWork::RequestWork(std::unique_ptr<Impl> value):impl_(std::move(value)){}
RequestWork::~RequestWork()=default;
RequestPrepared::RequestPrepared(std::unique_ptr<Impl> value):impl_(std::move(value)){}
RequestPrepared::~RequestPrepared()=default;
std::unique_ptr<RequestWork> EditorDraft::request_work(const std::string& intent,const std::string& request){
    invalidate_recovery();transaction_.editable();
    need(intent=="preview"||intent=="commit","settings.intent");need(protocol::identifier(request),"settings.request");
    if(!dirty())return {};
    auto input=std::make_unique<RequestWork::Impl>();
    input->draft=std::unique_ptr<SettingsDraft>(new SettingsDraft(transaction_,SettingsDraft::RecoveryCopy{}));
    input->validity=history_validity_.value;input->intent=intent;input->request=request;input->revision=*revision();
    return std::unique_ptr<RequestWork>(new RequestWork(std::move(input)));
}
std::unique_ptr<RequestPrepared> RequestWork::run(){
    auto input=std::move(impl_);need(input&&input->draft,"editor.request_consumed");
    // The ordinary entry retains all existing authored/command/theme checks.
    // Its detached ticket is discarded; no live transaction is mutated here.
    auto request=input->draft->begin(input->intent,input->request);need(request.has_value(),"editor.request_empty");
    auto result=std::make_unique<RequestPrepared::Impl>();
    result->command=c::parse_command(request->body);result->request=std::move(*request);result->request.ticket=0;
    result->validity=input->validity;result->intent=std::move(input->intent);result->revision=input->revision;
    return std::unique_ptr<RequestPrepared>(new RequestPrepared(std::move(result)));
}
EditRequest EditorDraft::adopt_request(std::unique_ptr<RequestPrepared> prepared){
    try{
        need(prepared&&prepared->impl_,"editor.request_prepared");auto& value=*prepared->impl_;auto& draft=transaction_;
        draft.editable();need(value.validity.lock()==history_validity_.value,"editor.request_stale");
        need(value.request.epoch==draft.epoch_&&value.revision==*revision(),"editor.request_stale");
        c::authorize_authored(value.command,draft.authority_,draft.policy_,value.revision);draft.authorize_resources();
        need(draft.tickets_<std::numeric_limits<std::uint64_t>::max(),"settings.capacity");
        auto request=std::move(value.request);request.ticket=draft.tickets_+1;
        SettingsDraft::Active active{request,value.intent,value.revision,false};Json empty_result;
        static_assert(std::is_nothrow_move_constructible<SettingsDraft::Active>::value,"request adoption must not throw after publication");
        invalidate_recovery();
        draft.active_.emplace(std::move(active));draft.tickets_=request.ticket;
        draft.submission_validation_.clear();draft.result_.swap(empty_result);draft.state_=DraftState::pending;clear_clipboard();
        return request;
    }catch(...){invalidate_recovery();throw;}
}
}
