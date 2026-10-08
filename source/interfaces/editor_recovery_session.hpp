#pragma once
#include "editor_draft.hpp"
#include "recovery_queue_linux.hpp"

namespace syspane::interfaces {
struct EditorRecoveryBinding {
    std::string session,profile,generation;
    std::uint64_t policy_revision=0;
    bool erase=false;
};
enum class EditorRecoveryState {disabled,loading,offer,ready,capturing,retiring,kept,unavailable};
// Same serialized owner as EditorDraft. The host invalidates before changing its
// trusted context, and polls closed children to completion before destruction.
class EditorRecoverySession {
public:
    EditorRecoverySession(EditorDraft&,std::string worker,std::string directory);
    EditorRecoverySession(EditorDraft&,std::shared_ptr<const platform::RecoveryFactory>,std::string directory);
    bool location(const std::string& worker,const std::string& directory)const{return worker_==worker&&directory_==directory;}
    bool location(const std::shared_ptr<const platform::RecoveryFactory>& factory,const std::string& directory)const{return factory_==factory&&directory_==directory;}
    void bind(EditorRecoveryBinding);
    void invalidate();
    void changed();
    void submitting();
    void settled(bool accepted);
    void restore();
    void keep();
    void discard();
    void cancel_session();
    void close();
    void poll();
    bool stopped()const;
    bool editing()const;
    bool may_apply()const;
    bool restorable()const{return restorable_;}
    bool erasable()const;
    bool cancelled()const{return cancelled_;}
    EditorRecoveryState state()const{return state_;}
private:
    EditorDraft& draft_;
    std::string worker_,directory_,offer_,session_,profile_;
    std::optional<EditorRecoveryBinding> binding_;
    std::shared_ptr<const platform::RecoveryFactory> factory_;
    std::unique_ptr<platform::RecoveryTask> queue_;
    std::optional<std::string> latest_,owned_,submitted_,cleanup_;
    EditorRecoveryState state_=EditorRecoveryState::disabled;
    bool restorable_=false,automatic_=false,closing_=false,reopen_=false,cancel_=false,cancelled_=false,closed_=false;
    RecoveryIdentity identity()const;
    void stop();
    void fail();
    void start();
    void retire(bool reopen);
};
}
