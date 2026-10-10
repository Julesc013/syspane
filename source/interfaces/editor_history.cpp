#include "editor_draft.hpp"

namespace syspane::interfaces {
namespace {
namespace c=configuration;
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
}
struct HistoryWork::Impl {
    std::unique_ptr<EditorDraft> draft;
    Json target;configuration::ResourceSnapshot resources;
    std::vector<std::string> selection;std::weak_ptr<const char> validity;
    bool forward=false;
};
struct HistoryPrepared::Impl {
    std::pair<c::Authored,c::ResourceSnapshot> candidate;
    std::optional<c::ValidatedAuthored> authored;
    std::vector<std::string> selection;std::weak_ptr<const char> validity;
    std::optional<bool> preview,commit;
    bool forward=false;
};
HistoryWork::HistoryWork(std::unique_ptr<Impl> value):impl_(std::move(value)){}
HistoryWork::~HistoryWork()=default;
HistoryPrepared::HistoryPrepared(std::unique_ptr<Impl> value):impl_(std::move(value)){}
HistoryPrepared::~HistoryPrepared()=default;
std::unique_ptr<HistoryWork> EditorDraft::history_work(bool forward){
    invalidate_recovery();transaction_.editable();const auto& from=forward?redo_:undo_;
    if(from.empty())return {};
    const auto& target=forward?from.back().after:from.back().before;
    auto input=std::make_unique<HistoryWork::Impl>();
    input->draft=std::unique_ptr<EditorDraft>(new EditorDraft(transaction_,0));
    input->target=target.scene;input->resources=target.resources;input->selection=target.selection;
    input->validity=history_validity_.value;input->forward=forward;
    return std::unique_ptr<HistoryWork>(new HistoryWork(std::move(input)));
}
std::unique_ptr<HistoryPrepared> HistoryWork::run(){
    auto input=std::move(impl_);need(input&&input->draft,"editor.history_consumed");
    auto result=std::make_unique<HistoryPrepared::Impl>();auto& draft=input->draft->transaction_;
    auto candidate=draft.prepare_scene(std::move(input->target),std::move(input->resources));
    draft.adopt_scene(std::move(candidate.first),std::move(candidate.second));
    // Prime only structural hints. Current authorization still runs at adoption,
    // at each eligible query, and in the full begin/commit validation path.
    (void)draft.may_submit("preview");(void)draft.may_submit("commit");
    result->preview=draft.submission_validation_.preview;result->commit=draft.submission_validation_.commit;
    result->authored.emplace(*draft.draft_);
    result->candidate={std::move(*draft.draft_),std::move(draft.draft_resources_)};
    result->selection=std::move(input->selection);result->validity=std::move(input->validity);result->forward=input->forward;
    return std::unique_ptr<HistoryPrepared>(new HistoryPrepared(std::move(result)));
}
bool EditorDraft::adopt_history(std::unique_ptr<HistoryPrepared> prepared){
    try{
        need(prepared&&prepared->impl_,"editor.history_prepared");transaction_.editable();
        auto& value=*prepared->impl_;need(value.validity.lock()==history_validity_.value,"editor.history_stale");
        auto& from=value.forward?redo_:undo_;auto& to=value.forward?undo_:redo_;
        need(!from.empty(),"editor.history_stale");transaction_.authorize_resources();
        if(value.candidate.second){
            need(transaction_.context_.has_value(),"editor.history_resources");
            c::authorize_resources(*value.candidate.second,transaction_.policy_,transaction_.context_->capabilities);
        }
        auto command=transaction_.command(value.candidate.first,value.candidate.second,"preview","draft.scene");
        if(command["operations"].empty())command["operations"].push_back({{"op","scene.replace"}});
        c::authorize_authored(command,transaction_.authority_,transaction_.policy_,*revision());
        auto destination=to;destination.push_back(from.back());
        invalidate_recovery();
        transaction_.adopt_scene(std::move(value.candidate.first),std::move(value.candidate.second));
        transaction_.submission_validation_.preview=value.preview;transaction_.submission_validation_.commit=value.commit;
        preview_authored_=std::move(value.authored);
        selected_.swap(value.selection);to.swap(destination);from.pop_back();return true;
    }catch(...){invalidate_recovery();throw;}
}
}
