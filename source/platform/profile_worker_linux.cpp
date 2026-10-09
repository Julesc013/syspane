#include "profile_worker_linux.hpp"
#include <condition_variable>
#include <exception>
#include <mutex>
#include <thread>
#include <utility>

namespace syspane::platform {
namespace c=configuration;
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
struct GuardScope {unsigned& depth;explicit GuardScope(unsigned& d):depth(d){++depth;}~GuardScope(){--depth;}};
}
struct LinuxProfileWorker::Impl {
    std::mutex mutex;std::condition_variable changed;
    bool ready=false,active=false,completed=false,closing=false,closed=false;
    std::exception_ptr startup_error;
    std::function<void()> work;
    std::unique_ptr<LinuxProfileStore> store;
    std::thread worker;std::thread::id worker_id;unsigned guard_depth=0;

    Impl(ProfileLocation location,bool create,std::set<std::string> caps,
         LinuxProfileStore::PolicySource source,LinuxProfileOwner::Transition transition){
        worker=std::thread([this,location=std::move(location),create,caps=std::move(caps),source=std::move(source),transition=std::move(transition)]()mutable{
            try{store=std::make_unique<LinuxProfileStore>(location,create,std::move(caps),std::move(source),std::move(transition));}
            catch(...){startup_error=std::current_exception();}
            std::unique_lock<std::mutex> lock(mutex);worker_id=std::this_thread::get_id();ready=true;changed.notify_all();
            if(startup_error)return;
            for(;;){
                changed.wait(lock,[&]{return closing||static_cast<bool>(work);});
                if(closing)break;
                auto invoke=std::exchange(work,{});lock.unlock();invoke();invoke={};lock.lock();
                // The callable and its captures have gone before the caller resumes.
                completed=true;changed.notify_all();
            }
            lock.unlock();store.reset();
        });
        std::unique_lock<std::mutex> lock(mutex);changed.wait(lock,[&]{return ready;});
        if(startup_error){auto error=startup_error;lock.unlock();worker.join();std::rethrow_exception(error);}
    }
    ~Impl(){close();}
    template<class F> auto call(bool read,F&& fn)->decltype(fn(std::declval<LinuxProfileStore&>())){
        using Result=decltype(fn(std::declval<LinuxProfileStore&>()));
        std::optional<Result> answer;std::exception_ptr error;
        std::function<void()> invoke=[&]{try{answer.emplace(fn(*store));}catch(...){error=std::current_exception();}};
        std::unique_lock<std::mutex> lock(mutex);
        need(!closing&&!closed,"profile_worker.closed");
        if(std::this_thread::get_id()==worker_id){
            need(read&&active&&guard_depth,"profile_worker.reentrant");lock.unlock();return fn(*store);
        }
        need(!active,"profile_worker.busy");active=true;completed=false;work=std::move(invoke);changed.notify_all();
        changed.wait(lock,[&]{return completed;});active=false;
        lock.unlock();if(error)std::rethrow_exception(error);return std::move(*answer);
    }
    void close(){
        std::unique_lock<std::mutex> lock(mutex);if(closed)return;
        need(std::this_thread::get_id()!=worker_id,"profile_worker.reentrant");
        need(!active&&!closing,"profile_worker.busy");closing=true;changed.notify_all();
        lock.unlock();worker.join();lock.lock();closed=true;
    }
};
LinuxProfileWorker::LinuxProfileWorker(ProfileLocation location,bool create,std::set<std::string> caps,
    LinuxProfileStore::PolicySource source,LinuxProfileOwner::Transition transition)
    :impl_(std::make_unique<Impl>(std::move(location),create,std::move(caps),std::move(source),std::move(transition))){}
LinuxProfileWorker::~LinuxProfileWorker()=default;
c::Committed LinuxProfileWorker::load()const{return impl_->call(true,[](auto& s){return s.load();});}
ProfileRecoverySnapshot LinuxProfileWorker::recovery_snapshot(const c::Authority& authority)const{
    return impl_->call(true,[&](auto& s){return s.recovery_snapshot(authority);});
}
std::vector<c::CommitReceipt> LinuxProfileWorker::receipts()const{return impl_->call(true,[](auto& s){return s.receipts();});}
std::optional<c::Committed> LinuxProfileWorker::reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const{
    return impl_->call(true,[&](auto& s){return s.reconcile(principal,epoch,request);});
}
c::Publication LinuxProfileWorker::publish(const c::Committed& value,const std::function<void()>& guard){
    return impl_->call(false,[&](auto& s){need(static_cast<bool>(guard),"profile_store.guard");return s.publish(value,[&]{GuardScope scope(impl_->guard_depth);guard();});});
}
ProfilePaths LinuxProfileWorker::verified_paths()const{return impl_->call(true,[](auto& s){return s.verified_paths();});}
std::string LinuxProfileWorker::generation_token()const{return impl_->call(true,[](auto& s){return s.generation_token();});}
bool LinuxProfileWorker::recovered_previous()const{return impl_->call(true,[](auto& s){return s.recovered_previous();});}
void LinuxProfileWorker::close(){impl_->close();}
}
