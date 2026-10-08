#include "editor_recovery_session.hpp"
#include "digest.hpp"

namespace syspane::interfaces {
namespace {
void need(bool ok){if(!ok)throw protocol::Error("recovery.unavailable");}
void erase(std::string& value){std::string{}.swap(value);}
}
EditorRecoverySession::EditorRecoverySession(EditorDraft& draft,std::string worker,std::string directory)
    :draft_(draft),worker_(std::move(worker)),directory_(std::move(directory)){
    need(!worker_.empty()&&worker_.front()=='/'&&worker_.size()<=512&&!directory_.empty()&&directory_.front()=='/'&&directory_.size()<=4096);
}
RecoveryIdentity EditorRecoverySession::identity()const{need(binding_.has_value());return {binding_->profile,binding_->generation};}
void EditorRecoverySession::stop(){
    erase(offer_);restorable_=false;automatic_=false;latest_.reset();owned_.reset();reopen_=false;
    if(queue_){queue_->close();closing_=true;}
}
void EditorRecoverySession::invalidate(){stop();binding_.reset();cleanup_.reset();cancel_=false;state_=EditorRecoveryState::disabled;}
void EditorRecoverySession::fail(){stop();binding_.reset();cleanup_.reset();cancel_=false;state_=EditorRecoveryState::unavailable;}
void EditorRecoverySession::bind(EditorRecoveryBinding binding){
    need(!closed_&&draft_.recovery_available()&&protocol::identifier(binding.session)&&protocol::identifier(binding.profile)&&
        binding.generation.size()==64&&binding.generation.find_first_not_of("0123456789abcdef")==std::string::npos);
    if(binding.session!=session_||binding.profile!=profile_){submitted_.reset();cleanup_.reset();}
    session_=binding.session;profile_=binding.profile;
    stop();binding_=std::move(binding);cancel_=false;cancelled_=false;state_=EditorRecoveryState::loading;
}
void EditorRecoverySession::start(){
    need(binding_&&draft_.recovery_available());const auto& b=*binding_;
    queue_=std::make_unique<platform::LinuxRecoveryQueue>(worker_,directory_,platform::RecoveryContext{b.session,b.profile,b.generation,b.policy_revision,true,true,b.erase});
    state_=EditorRecoveryState::loading;closing_=false;
}
bool EditorRecoverySession::editing()const{return state_!=EditorRecoveryState::loading&&state_!=EditorRecoveryState::offer&&state_!=EditorRecoveryState::retiring;}
bool EditorRecoverySession::may_apply()const{return editing()&&state_!=EditorRecoveryState::capturing;}
bool EditorRecoverySession::erasable()const{return binding_&&binding_->erase&&state_==EditorRecoveryState::offer;}
bool EditorRecoverySession::stopped()const{return !queue_||queue_->status().reaped;}
void EditorRecoverySession::retire(bool reopen){
    need(queue_&&binding_&&binding_->erase);queue_->retire();erase(offer_);restorable_=false;automatic_=false;reopen_=reopen;state_=EditorRecoveryState::retiring;
}
void EditorRecoverySession::changed(){
    if(!automatic_||!queue_||closing_||state_==EditorRecoveryState::retiring)return;
    try{
        need(draft_.recovery_available());auto bytes=draft_.recovery_snapshot(identity());
        if(!bytes){if(latest_||owned_)retire(true);return;}
        const auto digest=configuration::sha256(*bytes);if(latest_&&*latest_==digest)return;
        queue_->replace(std::move(*bytes));latest_=digest;state_=EditorRecoveryState::capturing;
    }catch(...){fail();}
}
void EditorRecoverySession::submitting(){need(may_apply());submitted_=automatic_?owned_:std::nullopt;}
void EditorRecoverySession::settled(bool accepted){
    if(accepted){auto digest=submitted_;invalidate();cleanup_=std::move(digest);}submitted_.reset();
}
void EditorRecoverySession::restore(){
    need(state_==EditorRecoveryState::offer&&restorable_&&draft_.recovery_available());
    draft_.restore_recovery(offer_,identity());owned_=configuration::sha256(offer_);latest_=owned_;erase(offer_);restorable_=false;automatic_=true;state_=EditorRecoveryState::ready;changed();
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
    if(automatic_&&(owned_||latest_))retire(false);else cancelled_=true;
}
void EditorRecoverySession::close(){invalidate();submitted_.reset();closed_=true;}
void EditorRecoverySession::poll(){
    try{
        if(closing_){
            if(!queue_->poll().reaped)return;
            queue_.reset();closing_=false;
        }
        if(!queue_){if(state_==EditorRecoveryState::loading&&binding_)start();else return;}
        const auto status=queue_->poll();auto done=queue_->take();
        if(status.state==platform::RecoveryQueueState::unavailable){fail();return;}
        if(!done)return;
        if(done->operation=="load"){
            need(done->outcome=="loaded"&&draft_.recovery_available());
            if(cleanup_&&done->digest==cleanup_){cleanup_.reset();retire(true);return;}
            cleanup_.reset();
            if(done->bytes){
                offer_=std::move(*done->bytes);state_=EditorRecoveryState::offer;automatic_=false;
                try{draft_.inspect_recovery(offer_,identity());restorable_=true;}catch(const protocol::Error&){restorable_=false;}
            }else{state_=EditorRecoveryState::ready;automatic_=true;changed();}
        }else if(done->operation=="replace"){
            need(done->outcome=="durable"&&done->digest==latest_);owned_=done->digest;state_=EditorRecoveryState::ready;
        }else{
            need(done->operation=="retire"&&done->outcome=="durable");
            const bool reopen=reopen_;stop();cancelled_=cancel_;state_=reopen?EditorRecoveryState::loading:EditorRecoveryState::ready;
        }
    }catch(...){fail();}
}
}
