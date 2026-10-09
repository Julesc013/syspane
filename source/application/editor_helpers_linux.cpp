#include "editor_helpers_linux.hpp"
#include <algorithm>
#include <limits>
#include <map>
#include <mutex>
#include <thread>
#include <utility>

namespace syspane::application {
namespace os=platform;namespace r=rendering;namespace p=protocol;
namespace ui=interfaces;
namespace {
void need(bool ok,const char* code){if(!ok)throw p::Error(code);}
void erase(std::string& value){std::string{}.swap(value);}
std::uint64_t next(std::uint64_t& value){need(value<std::numeric_limits<std::uint64_t>::max(),"helpers.capacity");return ++value;}
std::string reason(const std::exception& e,const char* fallback){
    const std::string code=e.what();return !code.empty()&&code.size()<=64&&code.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789._")==std::string::npos?code:fallback;
}
struct ImageSlot {
    std::uint64_t id=0,process=0;std::string media,encoded;
    r::ImageJobStatus status;scene::Image pixels;
    bool claimed=false,cancelled=false,released=false;
};
struct RecoverySlot {
    struct Intent {std::uint64_t ticket;std::string operation,bytes;};
    std::string directory;os::RecoveryContext context;
    os::RecoveryQueueStatus status{os::RecoveryQueueState::loading,0,1,0,0,false,{}};
    std::optional<Intent> intent;
    std::optional<os::RecoveryCompletion> completion;
    std::uint64_t latest=1;
    bool loaded=false,sealed=false,closed=false,released=false,fault=false;
};
template<class Work,class Result,class Status>struct PureSlot {
    using Input=Work;using Output=Result;
    std::unique_ptr<Work> input;std::unique_ptr<Result> result;
    Status status;std::uint64_t order=0;
    bool claimed=false,cancelled=false,released=false;
};
using PreparationSlot=PureSlot<ui::RecoveryWork,ui::RecoveryPrepared,ui::RecoveryPreparationStatus>;
using HistorySlot=PureSlot<ui::HistoryWork,ui::HistoryPrepared,ui::HistoryPreparationStatus>;
void cancel(PreparationSlot& s){
    s.cancelled=true;s.input.reset();s.result.reset();s.status.ready=false;s.status.error="recovery.cancelled";
    if(!s.claimed)s.status.stopped=true;
}
void cancel(HistorySlot& s){
    s.cancelled=true;s.input.reset();s.result.reset();s.status.ready=false;s.status.error="history.cancelled";
    if(!s.claimed)s.status.stopped=true;
}
void cancel(ImageSlot& s){s.cancelled=true;erase(s.encoded);s.pixels={};s.status={r::ImageJobState::stopping,"image.cancelled",false};}
void close(RecoverySlot& s){s.closed=true;s.intent.reset();s.completion.reset();s.status.state=os::RecoveryQueueState::closing;s.status.pending=0;s.status.reaped=false;}
}
struct LinuxRecoveryAdmission::Impl {
    configuration::ProfileRecoveryView view;Current current;os::ProfileRecoveryDirectory directory;
    std::unique_ptr<os::LinuxRecoveryDirectory> witness;std::thread::id owner=std::this_thread::get_id();
    bool invalid=false,calling=false;
    std::optional<RecoverySessionAuthority> sample(){
        auto a=current?current():std::nullopt;const auto& v=view;
        need(a&&a->retain&&a->connection==v.connection&&a->epoch==v.epoch&&a->profile==v.admission.profile&&a->session==v.editor_session&&
            a->revision==v.revision&&a->policy_revision==v.admission.policy_revision,"helpers.recovery_scope");return a;
    }
    bool permitted(const std::string& operation){
        need(owner==std::this_thread::get_id(),"helpers.worker_owner");if(invalid)return false;
        if(calling){invalid=true;return false;}
        struct Call{bool& v;explicit Call(bool& value):v(value){v=true;}~Call(){v=false;}} call(calling);
        try{
            need(operation=="load"||operation=="replace"||operation=="retire","helpers.recovery_operation");
            (void)sample();witness->verify();const auto a=sample();need(!invalid,"helpers.recovery_scope");
            return operation!="retire"||(view.admission.erase&&a->erase);
        }catch(...){invalid=true;return false;}
    }
};
LinuxRecoveryAdmission::LinuxRecoveryAdmission(const os::ProfileLocation& location,configuration::ProfileRecoveryView view,Current current):impl_(std::make_unique<Impl>()){
    auto& s=*impl_;s.view=std::move(view);s.current=std::move(current);const auto& v=s.view;const auto& d=v.admission.directory;
    need(p::identifier(v.connection)&&p::identifier(v.epoch)&&p::identifier(v.editor_session)&&v.transfer>0&&
        v.admission.generation.size()==64&&v.admission.generation.find_first_not_of("0123456789abcdef")==std::string::npos,"helpers.recovery_identity");
    const auto paths=os::profile_paths(location);need(paths.profile==v.admission.profile&&paths.recovery==d.path,"helpers.recovery_path");
    (void)s.sample();s.directory={v.admission.profile,d.path,d.uid,d.state_device,d.state_inode,d.recovery_device,d.recovery_inode};
    s.witness=std::make_unique<os::LinuxRecoveryDirectory>(s.directory);need(s.permitted("load"),"helpers.recovery_denied");
}
LinuxRecoveryAdmission::~LinuxRecoveryAdmission()=default;
bool LinuxRecoveryAdmission::permitted(const std::string& operation){return impl_->permitted(operation);}
const os::ProfileRecoveryDirectory& LinuxRecoveryAdmission::directory()const{need(impl_->owner==std::this_thread::get_id(),"helpers.worker_owner");return impl_->directory;}
os::RecoveryContext LinuxRecoveryAdmission::context()const{
    need(impl_->owner==std::this_thread::get_id(),"helpers.worker_owner");const auto& v=impl_->view;
    return {v.editor_session,v.admission.profile,v.admission.generation,v.admission.policy_revision,true,true,v.admission.erase};
}
struct EditorHelperChannel {
    std::thread::id gui=std::this_thread::get_id();mutable std::mutex mutex;
    bool attached=false,closed=false,drained=false;
    std::uint64_t sequence=0;
    std::map<std::uint64_t,std::shared_ptr<ImageSlot>> images;
    std::shared_ptr<RecoverySlot> recovery;
    std::shared_ptr<PreparationSlot> preparation;
    std::shared_ptr<HistorySlot> history;
    void owner()const{need(std::this_thread::get_id()==gui,"helpers.owner");}
    void admit()const{need(attached&&!closed,"helpers.unavailable");}
    void stop(){
        if(closed)return;
        closed=true;for(auto& row:images)cancel(*row.second);if(recovery)close(*recovery);if(preparation)cancel(*preparation);
        if(history)cancel(*history);
    }
};
namespace {
class PreparationProxy final:public ui::RecoveryPreparationTask {
    std::shared_ptr<EditorHelperChannel> channel_;std::shared_ptr<PreparationSlot> slot_;
public:
    PreparationProxy(std::shared_ptr<EditorHelperChannel> channel,std::unique_ptr<ui::RecoveryWork> input):channel_(std::move(channel)){
        channel_->owner();need(static_cast<bool>(input),"recovery.work");std::lock_guard<std::mutex> lock(channel_->mutex);
        channel_->admit();need(!channel_->preparation,"helpers.capacity");slot_=std::make_shared<PreparationSlot>();slot_->order=next(channel_->sequence);slot_->input=std::move(input);channel_->preparation=slot_;
    }
    ~PreparationProxy() override{
        std::lock_guard<std::mutex> lock(channel_->mutex);slot_->released=true;syspane::application::cancel(*slot_);
        if(slot_->status.stopped&&channel_->preparation==slot_)channel_->preparation.reset();
    }
    ui::RecoveryPreparationStatus status()const override{channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);return slot_->status;}
    std::unique_ptr<ui::RecoveryPrepared> take() override{
        channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);
        need(!slot_->cancelled&&slot_->status.ready&&slot_->status.stopped&&slot_->result,"recovery.not_ready");
        slot_->status.ready=false;return std::move(slot_->result);
    }
    void cancel() override{channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);syspane::application::cancel(*slot_);}
};
class HistoryProxy final:public ui::HistoryPreparationTask {
    std::shared_ptr<EditorHelperChannel> channel_;std::shared_ptr<HistorySlot> slot_;
public:
    HistoryProxy(std::shared_ptr<EditorHelperChannel> channel,std::unique_ptr<ui::HistoryWork> input):channel_(std::move(channel)){
        channel_->owner();need(static_cast<bool>(input),"history.work");std::lock_guard<std::mutex> lock(channel_->mutex);
        channel_->admit();need(!channel_->history,"helpers.capacity");slot_=std::make_shared<HistorySlot>();slot_->order=next(channel_->sequence);
        slot_->input=std::move(input);channel_->history=slot_;
    }
    ~HistoryProxy() override{
        std::lock_guard<std::mutex> lock(channel_->mutex);slot_->released=true;syspane::application::cancel(*slot_);
        if(slot_->status.stopped&&channel_->history==slot_)channel_->history.reset();
    }
    ui::HistoryPreparationStatus status()const override{channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);return slot_->status;}
    std::unique_ptr<ui::HistoryPrepared> take() override{
        channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);
        need(!slot_->cancelled&&slot_->status.ready&&slot_->status.stopped&&slot_->result,"history.not_ready");
        slot_->status.ready=false;return std::move(slot_->result);
    }
    void cancel() override{channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);syspane::application::cancel(*slot_);}
};
class ImageProxy final:public r::ImageTask {
    std::shared_ptr<EditorHelperChannel> channel_;std::shared_ptr<ImageSlot> slot_;
public:
    ImageProxy(std::shared_ptr<EditorHelperChannel> c,std::string media,std::string bytes):channel_(std::move(c)){
        channel_->owner();need(media=="image/png"||media=="image/jpeg"||media=="image/svg+xml","image.media");need(!bytes.empty()&&bytes.size()<=8388608,"image.capacity");
        std::lock_guard<std::mutex> lock(channel_->mutex);channel_->admit();need(channel_->images.size()<4,"helpers.capacity");
        auto value=std::make_shared<ImageSlot>();value->id=next(channel_->sequence);value->media=std::move(media);value->encoded=std::move(bytes);
        channel_->images.emplace(value->id,value);slot_=std::move(value);
    }
    ~ImageProxy() override{
        std::lock_guard<std::mutex> lock(channel_->mutex);slot_->released=true;
        if(slot_->status.reaped)channel_->images.erase(slot_->id);else syspane::application::cancel(*slot_);
    }
    r::ImageJobStatus poll() override{channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);return slot_->status;}
    void cancel() override{channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);if(!slot_->cancelled)syspane::application::cancel(*slot_);}
    scene::Image take() override{
        channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);
        need(!slot_->cancelled&&slot_->status.reaped&&slot_->status.state==r::ImageJobState::ready,"image.not_ready");
        slot_->status.state=r::ImageJobState::consumed;return std::move(slot_->pixels);
    }
    std::uint64_t process_id()const override{channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);return slot_->process;}
};
class RecoveryProxy final:public os::RecoveryTask {
    std::shared_ptr<EditorHelperChannel> channel_;std::shared_ptr<RecoverySlot> slot_;
    void admit(bool erase)const{
        channel_->admit();need(!slot_->closed&&!slot_->sealed&&!slot_->fault&&slot_->loaded&&
            (erase?slot_->context.erase:slot_->context.retain),"recovery_queue.denied");
    }
public:
    RecoveryProxy(std::shared_ptr<EditorHelperChannel> c,std::string directory,os::RecoveryContext context):channel_(std::move(c)){
        channel_->owner();need(!directory.empty()&&directory.front()=='/'&&directory.size()<=4096,"recovery_queue.path");
        need(p::identifier(context.session)&&p::identifier(context.profile)&&context.generation.size()==64&&context.generation.find_first_not_of("0123456789abcdef")==std::string::npos,"recovery_queue.identity");
        need(context.read,"recovery_queue.denied");std::lock_guard<std::mutex> lock(channel_->mutex);channel_->admit();need(!channel_->recovery,"helpers.capacity");
        slot_=std::make_shared<RecoverySlot>();slot_->directory=std::move(directory);slot_->context=std::move(context);channel_->recovery=slot_;
    }
    ~RecoveryProxy() override{
        std::lock_guard<std::mutex> lock(channel_->mutex);slot_->released=true;
        if(slot_->closed&&slot_->status.reaped){if(channel_->recovery==slot_)channel_->recovery.reset();}
        else syspane::application::close(*slot_);
    }
    std::uint64_t replace(std::string bytes) override{
        channel_->owner();need(!bytes.empty()&&bytes.size()<=786432,"recovery_queue.size");std::lock_guard<std::mutex> lock(channel_->mutex);admit(false);
        const auto id=next(slot_->latest);slot_->intent=RecoverySlot::Intent{id,"replace",std::move(bytes)};slot_->completion.reset();
        slot_->status.state=os::RecoveryQueueState::busy;slot_->status.pending=id;slot_->status.reaped=false;return id;
    }
    std::uint64_t retire() override{
        channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);admit(true);const auto id=next(slot_->latest);
        slot_->sealed=true;slot_->intent=RecoverySlot::Intent{id,"retire",{}};slot_->completion.reset();
        slot_->status.state=os::RecoveryQueueState::retiring;slot_->status.pending=id;slot_->status.reaped=false;return id;
    }
    os::RecoveryQueueStatus poll() override{return status();}
    os::RecoveryQueueStatus status()const override{
        channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);auto value=slot_->status;
        if(slot_->intent)value.retained_bytes+=slot_->intent->bytes.size();
        if(slot_->completion&&slot_->completion->bytes)value.retained_bytes+=slot_->completion->bytes->size();
        return value;
    }
    std::optional<os::RecoveryCompletion> take() override{
        channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);auto value=std::move(slot_->completion);slot_->completion.reset();
        if(value&&value->operation=="load"&&value->outcome=="loaded")slot_->loaded=true;
        return value;
    }
    void close() override{channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);if(!slot_->closed)syspane::application::close(*slot_);}
};
}
EditorHelperClient::EditorHelperClient():channel_(std::make_shared<EditorHelperChannel>()){
    recovery_=std::make_shared<const os::RecoveryFactory>([channel=channel_](std::string path,os::RecoveryContext context){return std::make_unique<RecoveryProxy>(channel,std::move(path),std::move(context));});
    preparations_=std::make_shared<const ui::RecoveryPreparationFactory>([channel=channel_](std::unique_ptr<ui::RecoveryWork> input){return std::make_unique<PreparationProxy>(channel,std::move(input));});
    history_preparations_=std::make_shared<const ui::HistoryPreparationFactory>([channel=channel_](std::unique_ptr<ui::HistoryWork> input){return std::make_unique<HistoryProxy>(channel,std::move(input));});
}
EditorHelperClient::~EditorHelperClient(){std::lock_guard<std::mutex> lock(channel_->mutex);channel_->stop();}
r::ImageFactory EditorHelperClient::images()const{
    channel_->owner();return [channel=channel_](std::string media,std::string bytes){return std::make_unique<ImageProxy>(channel,std::move(media),std::move(bytes));};
}
std::shared_ptr<const os::RecoveryFactory> EditorHelperClient::recovery()const{channel_->owner();return recovery_;}
std::shared_ptr<const ui::RecoveryPreparationFactory> EditorHelperClient::preparations()const{channel_->owner();return preparations_;}
std::shared_ptr<const ui::HistoryPreparationFactory> EditorHelperClient::history_preparations()const{channel_->owner();return history_preparations_;}
void EditorHelperClient::close(){channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);channel_->stop();}
EditorHelperStatus EditorHelperClient::status()const{
    channel_->owner();std::lock_guard<std::mutex> lock(channel_->mutex);EditorHelperStatus value;
    value.attached=channel_->attached;value.closing=channel_->closed;value.stopped=channel_->closed&&(!channel_->attached||channel_->drained);
    value.image_handles=channel_->images.size();value.recovery_handles=channel_->recovery?1:0;
    value.preparation_handles=channel_->preparation?1:0;
    value.history_handles=channel_->history?1:0;
    for(const auto& row:channel_->images){const auto& s=*row.second;value.retained_bytes+=s.encoded.size()+s.pixels.rgba.size();if(s.process&&!s.status.reaped)value.processes.push_back(s.process);}
    if(channel_->recovery){const auto& s=*channel_->recovery;value.retained_bytes+=s.status.retained_bytes+(s.intent?s.intent->bytes.size():0)+(s.completion&&s.completion->bytes?s.completion->bytes->size():0);if(s.status.process&&!s.status.reaped)value.processes.push_back(s.status.process);}
    return value;
}
struct LinuxEditorHelperOwner::Impl {
    std::shared_ptr<EditorHelperChannel> channel;std::shared_ptr<os::LinuxInstallation> installation;
    std::thread::id owner=std::this_thread::get_id();std::map<std::uint64_t,std::unique_ptr<r::ImageJob>> images;
    std::shared_ptr<RecoverySlot> recovery;std::unique_ptr<os::LinuxRecoveryQueue> queue;
    RecoveryAdmissionFactory admit_recovery;std::shared_ptr<LinuxRecoveryAdmission> admission;
    std::map<std::uint64_t,std::uint64_t> tickets;
    void check()const{need(std::this_thread::get_id()==owner,"helpers.worker_owner");}
    template<class Slot>void prepare(const std::shared_ptr<Slot>& slot,std::shared_ptr<Slot>& reservation,const char* failed,const char* cancelled){
        if(!slot)return;
        std::unique_ptr<typename Slot::Input> input;
        {
            std::lock_guard<std::mutex> lock(channel->mutex);
            if(slot->status.stopped||slot->claimed)return;
            if(slot->cancelled){slot->status.stopped=true;return;}
            slot->claimed=true;slot->status.running=true;input=std::move(slot->input);
        }
        std::unique_ptr<typename Slot::Output> result;std::string error;
        try{result=input->run();}catch(const std::exception& e){error=reason(e,failed);}catch(...){error=failed;}
        input.reset();
        std::lock_guard<std::mutex> lock(channel->mutex);
        if(slot->cancelled||channel->closed){result.reset();slot->status={false,true,cancelled};}
        else{slot->result=std::move(result);slot->status={static_cast<bool>(slot->result),true,std::move(error)};}
        if(slot->released&&reservation==slot)reservation.reset();
    }
    void image(const std::shared_ptr<ImageSlot>& slot){
        std::string media,bytes;bool stop=false,start=false;
        {
            std::lock_guard<std::mutex> lock(channel->mutex);stop=slot->cancelled;
            if(!stop&&!slot->claimed&&images.size()<2){slot->claimed=true;start=true;media=std::move(slot->media);bytes=std::move(slot->encoded);}
        }
        if(start){
            try{images.emplace(slot->id,std::make_unique<r::ImageJob>(installation,std::move(media),std::move(bytes)));}
            catch(const std::exception& e){std::lock_guard<std::mutex> lock(channel->mutex);slot->status={r::ImageJobState::failed,reason(e,"image.startup"),true};}
        }
        auto found=images.find(slot->id);r::ImageJobStatus state;scene::Image pixels;std::uint64_t pid=0;
        if(found!=images.end()){
            {std::lock_guard<std::mutex> lock(channel->mutex);stop=slot->cancelled;}
            if(stop)found->second->cancel();
            pid=found->second->process_id();state=found->second->poll();
            if(state.reaped){if(state.state==r::ImageJobState::ready)pixels=found->second->take();images.erase(found);}
        }
        std::lock_guard<std::mutex> lock(channel->mutex);
        if(pid){slot->process=pid;slot->status=std::move(state);}
        if(slot->cancelled){
            slot->pixels={};const bool gone=images.count(slot->id)==0;slot->status={gone?r::ImageJobState::cancelled:r::ImageJobState::stopping,"image.cancelled",gone};
        }else if(pid&&slot->status.state==r::ImageJobState::ready)slot->pixels=std::move(pixels);
        if(slot->released&&slot->status.reaped)channel->images.erase(slot->id);
    }
    void recover(const std::shared_ptr<RecoverySlot>& selected){
        if(recovery!=selected){
            if(queue){queue->close();if(!queue->poll().reaped)return;queue.reset();}
            recovery=selected;tickets.clear();admission.reset();
        }
        if(!recovery)return;
        bool stop;std::optional<RecoverySlot::Intent> intent;
        {
            std::lock_guard<std::mutex> lock(channel->mutex);stop=recovery->closed||recovery->fault;
            if(!stop){intent=std::move(recovery->intent);recovery->intent.reset();}
        }
        os::RecoveryQueueStatus state;std::optional<os::RecoveryCompletion> completion;
        try{
            if(!stop&&!queue){
                if(admit_recovery){
                    admission=admit_recovery();need(admission&&admission->permitted("load"),"helpers.recovery_denied");
                    const auto expected=admission->context();const auto& actual=recovery->context;
                    need(recovery->directory==admission->directory().path&&actual.profile==expected.profile&&actual.session==expected.session&&
                        actual.generation==expected.generation&&actual.policy_revision==expected.policy_revision&&actual.read==expected.read&&
                        actual.retain==expected.retain&&actual.erase==expected.erase,"helpers.recovery_scope");
                    queue=std::make_unique<os::LinuxRecoveryQueue>(installation,admission->directory(),actual,[this](const std::string& operation){
                        {std::lock_guard<std::mutex> lock(channel->mutex);if(channel->closed||recovery->closed||recovery->fault)return false;}
                        return admission&&admission->permitted(operation);
                    });
                }else queue=std::make_unique<os::LinuxRecoveryQueue>(installation,recovery->directory,recovery->context);
                tickets.emplace(1,1);
            }
            {std::lock_guard<std::mutex> lock(channel->mutex);stop=recovery->closed||recovery->fault;}
            if(queue){
                if(stop)queue->close();
                else if(intent){
                    const auto id=intent->operation=="replace"?queue->replace(std::move(intent->bytes)):queue->retire();tickets[id]=intent->ticket;
                }
                state=queue->poll();completion=queue->take();
                if(admission&&(state.state==os::RecoveryQueueState::closed||state.state==os::RecoveryQueueState::closing||!admission->permitted("load"))){
                    queue->close();state=queue->poll();completion.reset();
                    std::lock_guard<std::mutex> lock(channel->mutex);syspane::application::close(*recovery);
                }
                if(completion){
                    completion->ticket=tickets.at(completion->ticket);
                    if(completion->bytes){need(state.retained_bytes>=completion->bytes->size(),"helpers.capacity");state.retained_bytes-=completion->bytes->size();}
                }
                const auto active=state.active,pending=state.pending;
                if(active)state.active=tickets.at(active);
                if(pending)state.pending=tickets.at(pending);
                for(auto at=tickets.begin();at!=tickets.end();)if(at->first!=active&&at->first!=pending)at=tickets.erase(at);else ++at;
                need(tickets.size()<=2,"helpers.capacity");
            }else state={os::RecoveryQueueState::closed,0,0,0,0,true,{}};
        }catch(...){
            if(queue){queue->close();state=queue->poll();}
            state.state=os::RecoveryQueueState::unavailable;state.error="recovery_queue.failure";
            completion.reset();
        }
        std::lock_guard<std::mutex> lock(channel->mutex);
        if(recovery->closed){
            recovery->intent.reset();recovery->completion.reset();
            const bool acknowledged=state.state==os::RecoveryQueueState::closed&&state.reaped;
            recovery->status=state;recovery->status.state=acknowledged?os::RecoveryQueueState::closed:os::RecoveryQueueState::closing;recovery->status.reaped=acknowledged;
            recovery->status.pending=0;recovery->status.retained_bytes=0;
            if(recovery->released&&acknowledged&&channel->recovery==recovery)channel->recovery.reset();
            return;
        }
        if(recovery->fault||state.state==os::RecoveryQueueState::unavailable){
            if(recovery->fault)state.error=recovery->status.error;
            recovery->fault=true;state.state=os::RecoveryQueueState::unavailable;
            recovery->intent.reset();recovery->status=state;recovery->completion.reset();
            if(completion&&completion->ticket==recovery->latest)recovery->completion=std::move(completion);
            return;
        }
        recovery->status=state;
        if(recovery->intent){recovery->status.pending=recovery->intent->ticket;recovery->status.state=recovery->sealed?os::RecoveryQueueState::retiring:os::RecoveryQueueState::busy;recovery->status.reaped=false;}
        if(completion&&completion->ticket==recovery->latest&&!recovery->intent)recovery->completion=std::move(completion);
    }
};
LinuxEditorHelperOwner::LinuxEditorHelperOwner(EditorHelperClient& client,std::shared_ptr<os::LinuxInstallation> installation,RecoveryAdmissionFactory factory):impl_(std::make_unique<Impl>()){
    auto& s=*impl_;s.channel=client.channel_;s.installation=std::move(installation);s.admit_recovery=std::move(factory);
    need(std::this_thread::get_id()!=s.channel->gui&&s.installation,"helpers.worker_owner");
    s.installation->verified_helper(os::HelperKind::image);s.installation->verified_helper(os::HelperKind::recovery);
    std::lock_guard<std::mutex> lock(s.channel->mutex);need(!s.channel->attached&&!s.channel->closed,"helpers.unavailable");s.channel->attached=true;
}
void LinuxEditorHelperOwner::close(){impl_->check();std::lock_guard<std::mutex> lock(impl_->channel->mutex);impl_->channel->stop();}
bool LinuxEditorHelperOwner::poll(){
    auto& s=*impl_;s.check();std::vector<std::shared_ptr<ImageSlot>> images;std::shared_ptr<RecoverySlot> recovery;
    std::shared_ptr<PreparationSlot> preparation;std::shared_ptr<HistorySlot> history;
    {
        std::lock_guard<std::mutex> lock(s.channel->mutex);for(const auto& row:s.channel->images)images.push_back(row.second);recovery=s.channel->recovery;
        const auto eligible=[](const auto& slot){return slot&&!slot->claimed&&!slot->status.stopped&&!slot->cancelled;};
        if(eligible(s.channel->preparation))preparation=s.channel->preparation;
        if(eligible(s.channel->history))history=s.channel->history;
        if(preparation&&history){if(preparation->order<history->order)history.reset();else preparation.reset();}
    }
    for(const auto& slot:images)s.image(slot);
    s.recover(recovery);
    s.prepare(preparation,s.channel->preparation,"recovery.preparation","recovery.cancelled");
    s.prepare(history,s.channel->history,"history.preparation","history.cancelled");
    std::lock_guard<std::mutex> lock(s.channel->mutex);
    s.channel->drained=s.channel->closed&&s.images.empty()&&(!s.channel->recovery||s.channel->recovery->status.reaped)&&
        std::all_of(s.channel->images.begin(),s.channel->images.end(),[](const auto& row){return row.second->status.reaped;})&&
        (!s.channel->preparation||s.channel->preparation->status.stopped)&&(!s.channel->history||s.channel->history->status.stopped);
    return s.channel->drained;
}
LinuxEditorHelperOwner::~LinuxEditorHelperOwner(){
    auto& s=*impl_;
    // Emergency cleanup is confined to the native owner, never a task/client
    // destructor on GTK. Hosts normally poll closure before reaching this point.
    {std::lock_guard<std::mutex> lock(s.channel->mutex);s.channel->stop();}
    s.images.clear();s.queue.reset();
    std::lock_guard<std::mutex> lock(s.channel->mutex);
    for(auto& row:s.channel->images){row.second->pixels={};row.second->status={r::ImageJobState::cancelled,"image.cancelled",true};}
    if(s.channel->recovery)s.channel->recovery->status={os::RecoveryQueueState::closed,0,0,0,0,true,{}};
    if(s.channel->preparation)s.channel->preparation->status={false,true,"recovery.cancelled"};
    if(s.channel->history)s.channel->history->status={false,true,"history.cancelled"};
    s.channel->drained=true;s.channel->attached=false;
}
}
