#pragma once
#include "inspector_admission_owner.hpp"
#include <glib.h>
#include <atomic>
#include <condition_variable>
#include <functional>
#include <mutex>
#include <optional>
#include <thread>

namespace gtk_history_limits {
using namespace fixture;
inline std::uint64_t host_ms(){return static_cast<std::uint64_t>(g_get_monotonic_time()/1000);}
inline c::Policy producer_grant(std::uint64_t revision){auto value=inspector_admission_owner_test::grant();value.revision=revision;return value;}
inline p::TelemetryBinding producer_binding(std::uint64_t revision){auto value=inspector_admission_owner_test::binding();value.policy_revision=revision;value.negotiated.features.insert("telemetry.monotonic-replay");return value;}

// Only the creator calls this API. All receiver operations, including destruction,
// belong to worker_. The mutex protects a single primitive job and immutable view.
class Producer {
public:
    struct Job {unsigned generation;std::uint64_t ns,revision;bool reset=false,invalid=false;};
    struct Snapshot {r::TelemetryDelivery delivery;unsigned generation=0,accepted=0;std::uint64_t publication_max_us=0,clock_gap_max_ms=0;bool receiver_owner=false;};
    using Barrier=std::function<void(const std::atomic<bool>&)>;
private:
    const std::thread::id api_owner_=std::this_thread::get_id();const bool mixed_;Barrier barrier_;
    std::mutex mutex_;std::condition_variable wake_;std::optional<Job> queued_;bool outstanding_=false;unsigned requested_acceptance_=0;
    Snapshot latest_;std::atomic<bool> closing_{false},stopped_{false};std::atomic<unsigned> failure_{0};std::thread worker_;
    void owner()const{need(std::this_thread::get_id()==api_owner_,"history producer API owner");}
    void run(){
        std::unique_ptr<r::TelemetryReceiver> receiver;Snapshot current;std::uint64_t revision=7,sequence=0,measured=0;
        const auto receiver_owner=std::this_thread::get_id();
        const auto checked=[&]{need(std::this_thread::get_id()==receiver_owner&&receiver_owner!=api_owner_,"history receiver owner");};
        const auto create=[&]{checked();receiver=std::make_unique<r::TelemetryReceiver>(r::DeliveryScope{11,revision==9?5U:4U},producer_grant(revision),n::network_metrics(),producer_binding(revision),host_ms());current.receiver_owner=true;};
        const auto destroy=[&]{checked();if(receiver){receiver->withdraw(host_ms());receiver.reset();}};
        const auto refresh=[&]{checked();const auto now=host_ms();if(current.delivery.clock){need(now>=current.delivery.clock_ms,"history producer monotonic clock");current.clock_gap_max_ms=std::max(current.clock_gap_max_ms,now-current.delivery.clock_ms);need(current.clock_gap_max_ms<=250,"history producer clock gap");}
            need(receiver->heartbeat(++sequence,now)==r::DataCode::accepted,"history producer heartbeat");need(receiver->sample(tick(measured),now)==r::DataCode::accepted,"history producer clock");current.delivery=receiver->view(now);
            std::lock_guard<std::mutex> lock(mutex_);if(!closing_.load())latest_=current;};
        try{
            create();refresh();
            while(!closing_.load()){
                std::optional<Job> job;
                {std::unique_lock<std::mutex> lock(mutex_);wake_.wait_for(lock,std::chrono::milliseconds(20),[&]{return closing_.load()||queued_.has_value();});if(closing_.load())break;job=queued_;queued_.reset();}
                if(job){
                    if(barrier_)barrier_(closing_);
                    if(closing_.load())break;
                    const auto begin=g_get_monotonic_time();checked();
                    if(job->reset){need(job->revision==9,"history producer reset revision");destroy();revision=job->revision;sequence=0;measured=0;current.delivery={};current.generation=0;create();}
                    need(job->revision==revision&&job->generation&&job->generation<=4099&&job->ns>=measured,"history producer job identity");
                    refresh();
                    n::NetworkState state("E1","clock:1","scope:1");state.demand(1);syspane::platform::NetworkResult input{syspane::platform::NetworkCode::success,0,{}};
                    for(unsigned i=1;i<=(mixed_?64U:1U);++i)input.rows.push_back({i,i,6,syspane::platform::NetworkCounters{10,7}});
                    need(state.commit(1,0,std::move(input),tick(job->ns),tick(job->ns))==n::NetworkStateCode::accepted,"history producer acquisition");
                    auto doc=n::network_document(*state.sample(),job->generation,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
                    Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","P1"},{"record_id","sample:"+std::to_string(job->generation)},{"policy_revision",std::to_string(revision)},{"clock_id","clock:1"},{"snapshot",doc}};
                    refresh();
                    const auto bytes=job->invalid?std::string("{}"):p::encode_telemetry({"snapshot","D","E1",body.dump(),body},producer_binding(revision));
                    refresh();
                    need(receiver->receive(bytes,host_ms(),tick(job->ns)).code==r::DataCode::accepted,"history producer complete receipt");
                    current.generation=job->generation;measured=job->ns;++current.accepted;
                    current.publication_max_us=std::max(current.publication_max_us,static_cast<std::uint64_t>(g_get_monotonic_time()-begin));
                }
                refresh();
            }
        }catch(...){failure_.store(1);}
        try{destroy();}catch(...){receiver.reset();failure_.store(2);}
        {std::lock_guard<std::mutex> lock(mutex_);current.delivery={};latest_=current;queued_.reset();outstanding_=false;}
        stopped_.store(true);
    }
public:
    explicit Producer(bool mixed,Barrier barrier={}):mixed_(mixed),barrier_(std::move(barrier)),worker_([this]{run();}){}
    ~Producer(){closing_.store(true);wake_.notify_all();if(worker_.joinable())worker_.join();}
    bool offer(Job job){owner();if(closing_.load()||stopped_.load())return false;need(!failure_.load(),"history producer failed");
        std::unique_lock<std::mutex> lock(mutex_,std::try_to_lock);if(!lock.owns_lock()||outstanding_||closing_.load())return false;
        queued_=job;requested_acceptance_=latest_.accepted+1;outstanding_=true;wake_.notify_one();return true;}
    bool poll(Snapshot& value){owner();need(!failure_.load(),"history producer failed");if(closing_.load()||stopped_.load())return false;
        std::unique_lock<std::mutex> lock(mutex_,std::try_to_lock);if(!lock.owns_lock()||closing_.load()||failure_.load())return false;
        value=latest_;if(value.accepted==requested_acceptance_&& !queued_)outstanding_=false;return true;}
    void close(){owner();closing_.store(true);wake_.notify_all();}
    bool stopped()const{owner();return stopped_.load();}
    unsigned failure()const{owner();return failure_.load();}
    Snapshot terminal(){owner();need(stopped_.load(),"history producer still running");if(worker_.joinable())worker_.join();std::lock_guard<std::mutex> lock(mutex_);return latest_;}
};

template<class Predicate> inline void producer_wait(Predicate condition){const auto until=g_get_monotonic_time()+3000000;while(!condition()){need(g_get_monotonic_time()<until,"history producer probe deadline");g_usleep(1000);}}
inline int producer_probe(){
    Json output;std::atomic<bool> entered{false},released{false};
    const auto barrier=[&](const std::atomic<bool>& closing){entered.store(true);while(!released.load()&&!closing.load())g_usleep(1000);};
    Producer source(true,barrier);producer_wait([&]{return source.offer({1,0,7});});producer_wait([&]{return entered.load();});
    need(!source.offer({2,1000000,7}),"history producer busy refusal");released.store(true);
    Producer::Snapshot first;producer_wait([&]{return source.poll(first)&&first.generation==1;});
    need(first.receiver_owner&&first.accepted==1&&first.delivery.deliverable({11,4},host_ms())&&first.delivery.frame->ordinal==1,"history producer first delivery");
    output["first_wire"]=first.delivery.frame->bytes;output["first_receipt_ms"]=first.delivery.frame->received_ms;output["first_clock_ms"]=first.delivery.clock_ms;
    need(!first.delivery.deliverable({11,4},first.delivery.clock_ms+251)&&!first.delivery.live({11,4},first.delivery.live_until_ms),"history producer original freshness limits");
    entered.store(false);released.store(false);
    producer_wait([&]{return source.offer({4099,21000000000ULL,9,true});});
    producer_wait([&]{return entered.load();});Producer::Snapshot old;need(source.poll(old)&&old.generation==1&&!source.offer({2,1000000,7}),"history producer old mailbox cannot free in-flight job");released.store(true);
    Producer::Snapshot fresh;producer_wait([&]{return source.poll(fresh)&&fresh.generation==4099;});
    need(!first.delivery.live({11,5},host_ms())&&fresh.delivery.deliverable({11,5},host_ms())&&fresh.delivery.frame->ordinal==1&&fresh.accepted==2,"history producer fresh scope");
    output["fresh_wire"]=fresh.delivery.frame->bytes;output["fresh_clock_ns"]=fresh.delivery.clock->nanoseconds;
    std::atomic<bool> refused{false};std::thread wrong([&]{try{source.close();}catch(const std::exception&){refused.store(true);}});wrong.join();need(refused.load(),"history producer wrong owner refusal");
    source.close();producer_wait([&]{return source.stopped();});const auto terminal=source.terminal();
    need(!source.poll(fresh)&&!source.offer({2,0,7})&&!terminal.delivery.frame&&terminal.accepted==2&&!source.failure(),"history producer real stop");
    entered.store(false);released.store(false);Producer held(false,barrier);producer_wait([&]{return held.offer({1,0,7});});producer_wait([&]{return entered.load();});held.close();producer_wait([&]{return held.stopped();});need(held.terminal().accepted==0&&!held.failure(),"history producer held close");
    entered.store(false);released.store(true);Producer repeated(false,barrier);producer_wait([&]{return repeated.offer({1,0,7});});Producer::Snapshot repeated_view;producer_wait([&]{return repeated.poll(repeated_view)&&repeated_view.generation==1;});
    entered.store(false);released.store(false);producer_wait([&]{return repeated.offer({1,0,7});});producer_wait([&]{return entered.load();});need(repeated.poll(repeated_view)&&!repeated.offer({2,1000000,7}),"history producer held repeat busy refusal");
    repeated.close();producer_wait([&]{return repeated.stopped();});need(repeated.terminal().accepted==1&&!repeated.failure(),"history producer held repeat close");
    Producer broken(false);producer_wait([&]{return broken.offer({1,0,7});});Producer::Snapshot good;producer_wait([&]{return broken.poll(good)&&good.generation==1;});
    producer_wait([&]{return broken.offer({2,1000000,7,false,true});});producer_wait([&]{return broken.stopped();});const auto bad=broken.terminal();
    bool stale_refused=false;try{broken.poll(good);}catch(const std::exception&){stale_refused=true;}
    need(broken.failure()==1&&bad.accepted==1&&!bad.delivery.frame&&stale_refused,"history producer invalid receipt closes");
    entered.store(false);released.store(true);Producer stale(false,barrier);producer_wait([&]{return stale.offer({1,0,7});});Producer::Snapshot stale_view;producer_wait([&]{return stale.poll(stale_view)&&stale_view.generation==1;});
    entered.store(false);released.store(false);producer_wait([&]{return stale.offer({2,1000000,7});});producer_wait([&]{return entered.load();});g_usleep(300000);released.store(true);producer_wait([&]{return stale.stopped();});const auto expired=stale.terminal();
    need(stale.failure()==1&&expired.accepted==1&&!expired.delivery.frame&&expired.clock_gap_max_ms>250,"history producer expired clock clears");
    output["expired_clock_gap_ms"]=expired.clock_gap_max_ms;
    output["controls"]={{"busy_refused",true},{"old_mailbox_busy_refused",true},{"held_repeat_busy_refused",true},{"clock_gap_stale_refused",true},{"original_clock_lease",true},{"wrong_owner_refused",true},{"fresh_scope",true},{"held_close_accepted",0},{"invalid_accepted",1},{"invalid_stale_refused",true},{"accepted",terminal.accepted},{"receiver_owner",terminal.receiver_owner},{"producer_stopped",true}};
    std::cout<<output.dump()<<std::endl;return 0;
}
}
