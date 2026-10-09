#include "editor_recovery_session.hpp"
#include "digest.hpp"

namespace syspane::interfaces {
namespace {
void need(bool ok){if(!ok)throw protocol::Error("recovery.unavailable");}
void erase(std::string& value){std::string{}.swap(value);}
bool withdrawn(platform::RecoveryQueueState state){return state==platform::RecoveryQueueState::unavailable||state==platform::RecoveryQueueState::closing||state==platform::RecoveryQueueState::closed;}
}
EditorRecoverySession::EditorRecoverySession(EditorDraft& draft,std::string worker,std::string directory)
    :draft_(draft),worker_(std::move(worker)),directory_(std::move(directory)){
    need(!worker_.empty()&&worker_.front()=='/'&&worker_.size()<=512&&!directory_.empty()&&directory_.front()=='/'&&directory_.size()<=4096);
    factory_=std::make_shared<const platform::RecoveryFactory>([path=worker_](std::string directory,platform::RecoveryContext context){return std::make_unique<platform::LinuxRecoveryQueue>(path,std::move(directory),std::move(context));});
}
EditorRecoverySession::EditorRecoverySession(EditorDraft& draft,std::shared_ptr<const platform::RecoveryFactory> factory,std::string directory,std::shared_ptr<const RecoveryPreparationFactory> preparations)
    :draft_(draft),directory_(std::move(directory)),factory_(std::move(factory)),preparations_(std::move(preparations)){
    need(factory_&&*factory_&&(!preparations_||*preparations_)&&!directory_.empty()&&directory_.front()=='/'&&directory_.size()<=4096);
}
RecoveryIdentity EditorRecoverySession::identity()const{need(binding_.has_value());return {binding_->profile,binding_->generation};}
void EditorRecoverySession::stop(){
    stop_preparation();
    erase(offer_);restorable_=false;automatic_=false;latest_.reset();owned_.reset();reopen_=false;
    if(queue_){queue_->close();closing_=true;}
}
void EditorRecoverySession::invalidate(){stop();binding_.reset();cleanup_.reset();retiring_receipt_=retirement_decided_=false;cancel_=false;state_=EditorRecoveryState::disabled;}
void EditorRecoverySession::fail(){stop();binding_.reset();cleanup_.reset();retiring_receipt_=retirement_decided_=false;cancel_=false;state_=EditorRecoveryState::unavailable;}
void EditorRecoverySession::bind(EditorRecoveryBinding binding,std::optional<std::string> retirement){
    need(!closed_&&draft_.recovery_available()&&protocol::identifier(binding.session)&&protocol::identifier(binding.profile)&&
        binding.generation.size()==64&&binding.generation.find_first_not_of("0123456789abcdef")==std::string::npos);
    need(!retirement||(binding.erase&&retirement->size()==64&&retirement->find_first_not_of("0123456789abcdef")==std::string::npos));
    if(binding.session!=session_||binding.profile!=profile_){submitted_.reset();cleanup_.reset();}
    session_=binding.session;profile_=binding.profile;
    if(retirement)cleanup_=std::move(retirement);
    retiring_receipt_=retirement_decided_=false;
    stop();binding_=std::move(binding);cancel_=false;cancelled_=false;state_=EditorRecoveryState::loading;
}
void EditorRecoverySession::start(){
    need(binding_&&draft_.recovery_available());const auto& b=*binding_;
    queue_=(*factory_)(directory_,platform::RecoveryContext{b.session,b.profile,b.generation,b.policy_revision,true,true,b.erase});need(static_cast<bool>(queue_));
    state_=EditorRecoveryState::loading;closing_=false;
}
bool EditorRecoverySession::editing()const{return state_!=EditorRecoveryState::loading&&state_!=EditorRecoveryState::offer&&state_!=EditorRecoveryState::retiring;}
bool EditorRecoverySession::may_apply()const{return editing()&&state_!=EditorRecoveryState::capturing;}
bool EditorRecoverySession::erasable()const{return binding_&&binding_->erase&&state_==EditorRecoveryState::offer;}
bool EditorRecoverySession::stopped()const{return (!queue_||queue_->status().reaped)&&(!preparation_||preparation_->status().stopped)&&!pending_;}
void EditorRecoverySession::retire(bool reopen){
    need(queue_&&binding_&&binding_->erase);stop_preparation();queue_->retire();erase(offer_);restorable_=false;automatic_=false;reopen_=reopen;state_=EditorRecoveryState::retiring;
}
void EditorRecoverySession::stop_preparation(){
    pending_.reset();prepared_offer_.reset();preparation_obsolete_=true;if(preparation_)preparation_->cancel();
}
void EditorRecoverySession::prepare(std::unique_ptr<RecoveryWork> work,bool capture){
    need(preparations_&&work);if(preparation_){preparation_->cancel();preparation_obsolete_=true;}
    pending_=std::move(work);pending_capture_=capture;
    state_=capture?EditorRecoveryState::capturing:EditorRecoveryState::loading;
}
void EditorRecoverySession::capture(std::optional<std::string> bytes){
    if(!bytes){if(latest_||owned_)retire(true);else state_=EditorRecoveryState::ready;return;}
    const auto digest=configuration::sha256(*bytes);
    if(latest_&&*latest_==digest){state_=owned_==latest_?EditorRecoveryState::ready:EditorRecoveryState::capturing;return;}
    queue_->replace(std::move(*bytes));latest_=digest;state_=EditorRecoveryState::capturing;
}
void EditorRecoverySession::poll_preparation(){
    if(preparation_){
        const auto status=preparation_->status();if(!status.stopped)return;
        auto result=!preparation_obsolete_&&status.ready?preparation_->take():nullptr;
        preparation_.reset();
        if(!preparation_obsolete_){
            if(preparation_capture_){need(static_cast<bool>(result));capture(draft_.recovery_capture(std::move(result),identity()));}
            else{
                restorable_=false;state_=EditorRecoveryState::offer;
                if(result)try{draft_.inspect_recovery(*result,identity());prepared_offer_=std::move(result);restorable_=true;}catch(const protocol::Error&){}
            }
        }
    }
    if(pending_){preparation_capture_=pending_capture_;preparation_obsolete_=false;preparation_=(*preparations_)(std::move(pending_));need(static_cast<bool>(preparation_));}
}
void EditorRecoverySession::changed(){
    if(!automatic_||!queue_||closing_||state_==EditorRecoveryState::retiring)return;
    try{
        need(draft_.recovery_available());
        if(preparations_)prepare(draft_.recovery_capture_work(identity()),true);
        else capture(draft_.recovery_snapshot(identity()));
    }catch(...){fail();}
}
std::optional<std::string> EditorRecoverySession::submitting(){need(may_apply());submitted_=automatic_?owned_:std::nullopt;return submitted_;}
void EditorRecoverySession::settled(bool accepted){
    if(accepted){auto digest=submitted_;invalidate();cleanup_=std::move(digest);}submitted_.reset();
}
void EditorRecoverySession::restore(){
    need(queue_&&state_==EditorRecoveryState::offer&&restorable_&&draft_.recovery_available());
    if(withdrawn(queue_->status().state)){fail();throw protocol::Error("recovery.unavailable");}
    if(preparations_)draft_.restore_recovery(std::move(prepared_offer_),identity());else draft_.restore_recovery(offer_,identity());
    owned_=configuration::sha256(offer_);latest_=owned_;erase(offer_);restorable_=false;automatic_=true;state_=EditorRecoveryState::ready;changed();
}
void EditorRecoverySession::keep(){need(state_==EditorRecoveryState::offer);stop();state_=EditorRecoveryState::kept;}
void EditorRecoverySession::discard(){
    need(erasable()&&draft_.recovery_available());
    // Keep relinquishes the file owner. Reload through a fresh queue before any
    // later deletion; the UI exposes Discard only while its offer is held.
    need(state_==EditorRecoveryState::offer);retire(true);
}
void EditorRecoverySession::cancel_session(){
    need(state_!=EditorRecoveryState::retiring&&draft_.recovery_available());cancel_=true;
    if(automatic_&&(owned_||latest_))retire(false);else{stop();cancelled_=true;state_=EditorRecoveryState::ready;}
}
void EditorRecoverySession::close(){invalidate();submitted_.reset();closed_=true;}
void EditorRecoverySession::poll(){
    try{
        if(queue_&&!closing_&&withdrawn(queue_->status().state)){fail();return;}
        poll_preparation();
        if(closing_){
            if(!queue_->poll().reaped)return;
            queue_.reset();closing_=false;
        }
        if(!queue_){if(state_==EditorRecoveryState::loading&&binding_)start();else return;}
        const auto status=queue_->poll();auto done=queue_->take();
        if(withdrawn(status.state)){fail();return;}
        if(!done)return;
        if(done->operation=="load"){
            need(done->outcome=="loaded"&&draft_.recovery_available());
            if(cleanup_&&done->digest==cleanup_){cleanup_.reset();retiring_receipt_=true;retire(true);return;}
            if(cleanup_)retirement_decided_=true;
            cleanup_.reset();
            if(done->bytes){
                offer_=std::move(*done->bytes);state_=EditorRecoveryState::offer;automatic_=false;
                try{
                    if(preparations_)prepare(draft_.recovery_restore_work(offer_,identity()),false);
                    else{draft_.inspect_recovery(offer_,identity());restorable_=true;}
                }catch(const protocol::Error&){restorable_=false;}
            }else{state_=EditorRecoveryState::ready;automatic_=true;changed();}
        }else if(done->operation=="replace"){
            need(done->outcome=="durable"&&done->digest==latest_);owned_=done->digest;state_=(preparation_||pending_)?EditorRecoveryState::capturing:EditorRecoveryState::ready;
        }else{
            need(done->operation=="retire"&&done->outcome=="durable");
            if(retiring_receipt_){need(status.reaped);retiring_receipt_=false;retirement_decided_=true;}
            const bool reopen=reopen_;stop();cancelled_=cancel_;state_=reopen?EditorRecoveryState::loading:EditorRecoveryState::ready;
        }
    }catch(...){fail();}
}
}
