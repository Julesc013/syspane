#include "profile_store_linux.hpp"
#include "generation_store_linux.hpp"
#include "machine_policy.hpp"
#include "initial_profile.hpp"
#include <thread>

namespace syspane::platform {
namespace c=configuration;
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
bool same_policy(const c::Policy& a,const c::Policy& b){return a.available==b.available&&a.revision==b.revision&&a.forced==b.forced&&a.denied_capabilities==b.denied_capabilities&&a.disclosure==b.disclosure;}
struct Active {bool& value;explicit Active(bool& v):value(v){need(!value,"profile_store.reentrant");value=true;}~Active(){value=false;}};
}
struct LinuxProfileStore::Impl {
    PolicySource source;std::set<std::string> capabilities;c::Policy policy;
    const std::thread::id thread=std::this_thread::get_id();bool reading_policy=false,publishing=false,invalid=false;
    std::unique_ptr<LinuxProfileOwner> profile;std::unique_ptr<LinuxGenerationStore> store;
    c::Policy current(){Active active(reading_policy);return source();}
    bool permitted(){
        need(thread==std::this_thread::get_id(),"profile_store.thread");
        if(invalid)return false;
        try{const auto now=current();if(!now.available||now.denied_capabilities.count("profile.open")||!same_policy(now,policy)){invalid=true;return false;}}
        catch(...){invalid=true;return false;}
        return true;
    }
    ProfilePaths verify(){
        need(thread==std::this_thread::get_id(),"profile_store.thread");need(!invalid,"profile_store.invalidated");
        try{return profile->verified_paths([&]{return permitted();});}catch(...){invalid=true;throw;}
    }
    void authorize(const c::Committed& value){need(value.resources!=nullptr,"profile_store.resources");c::authorize_resources(*value.resources,policy,capabilities);}
    Impl(const ProfileLocation& location,bool create,std::set<std::string> caps,PolicySource provider,LinuxProfileOwner::Transition transition)
        :source(provider?std::move(provider):PolicySource(machine_policy)),capabilities(std::move(caps)){
        try{policy=current();}catch(...){throw protocol::Error("profile_store.policy");}
        need(policy.available&&!policy.denied_capabilities.count("profile.open"),"profile_store.policy");
        profile=std::make_unique<LinuxProfileOwner>(location,create&&!policy.denied_capabilities.count("profile.create"),[&]{return permitted();},transition,
            [&]{return c::initial_profile(policy,capabilities);});
        const auto paths=verify();store=std::make_unique<LinuxGenerationStore>(paths.generations,[transition](const char* phase){if(transition)transition(std::string("store.")+phase);});
        authorize(store->load());verify();
    }
};
LinuxProfileStore::LinuxProfileStore(const ProfileLocation& location,bool create,std::set<std::string> capabilities,PolicySource source,LinuxProfileOwner::Transition transition)
    :impl_(std::make_unique<Impl>(location,create,std::move(capabilities),std::move(source),std::move(transition))){}
LinuxProfileStore::~LinuxProfileStore()=default;
c::Committed LinuxProfileStore::load()const{impl_->verify();auto value=impl_->store->load();impl_->authorize(value);return value;}
ProfileRecoverySnapshot LinuxProfileStore::recovery_snapshot(const c::Authority& authority)const{
    impl_->verify();ProfileRecoverySnapshot snapshot{impl_->store->load(),{}};impl_->authorize(snapshot.committed);
    if(impl_->capabilities.count("editor.recovery")&&authority.role=="console"&&
       !impl_->policy.denied_capabilities.count("editor.recovery")&&c::permits(authority,impl_->policy,"history","sensitive")){
        std::optional<std::string> generation;
        try{generation=impl_->store->generation_token();}
        catch(const protocol::Error& error){if(std::string(error.what())!="storage.unavailable")throw;}
        if(generation){
            try{snapshot.recovery=ProfileRecoveryAdmission{impl_->profile->verified_recovery([&]{return impl_->permitted();}),
                *generation,impl_->policy.revision,!impl_->policy.denied_capabilities.count("editor.recovery.erase")};}
            catch(...){impl_->invalid=true;throw;}
        }
    }
    impl_->verify();return snapshot;
}
std::vector<c::CommitReceipt> LinuxProfileStore::receipts()const{impl_->verify();return impl_->store->receipts();}
std::optional<c::Committed> LinuxProfileStore::reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const{
    impl_->verify();auto value=impl_->store->reconcile(principal,epoch,request);if(value)impl_->authorize(*value);return value;
}
c::Publication LinuxProfileStore::publish(const c::Committed& value,const std::function<void()>& guard){
    need(impl_->thread==std::this_thread::get_id(),"profile_store.thread");Active active(impl_->publishing);impl_->verify();impl_->authorize(value);
    need(static_cast<bool>(guard),"profile_store.guard");
    auto outcome=impl_->store->publish(value,[&]{impl_->verify();impl_->authorize(value);guard();impl_->verify();});
    if(outcome==c::Publication::unknown)impl_->invalid=true;
    return outcome;
}
ProfilePaths LinuxProfileStore::verified_paths()const{return impl_->verify();}
std::string LinuxProfileStore::generation_token()const{impl_->verify();return impl_->store->generation_token();}
bool LinuxProfileStore::recovered_previous()const{impl_->verify();return impl_->store->recovered_previous();}
}
