#include "profile_worker_linux.hpp"
#include "async_commands.hpp"
#include <atomic>
#include <condition_variable>
#include <fstream>
#include <iostream>
#include <mutex>
#include <thread>
#include <sys/syscall.h>
#include <unistd.h>
namespace c=syspane::configuration;namespace os=syspane::platform;using c::Json;
namespace {
std::mutex output;
void emit(const Json& value){std::lock_guard<std::mutex> lock(output);std::cout<<value.dump()<<std::endl;}
void need(bool ok){if(!ok)throw syspane::protocol::Error("probe.state");}
long tid(){return ::syscall(SYS_gettid);}
struct Gate {
    std::mutex mutex;std::condition_variable changed;std::string phase;bool released=false;
    void set(std::string next){std::lock_guard<std::mutex> lock(mutex);phase=std::move(next);released=false;}
    void release(){std::lock_guard<std::mutex> lock(mutex);released=true;changed.notify_all();}
    void hold(const std::string& at){std::unique_lock<std::mutex> lock(mutex);if(phase!=at||released)return;
        emit({{"event","held"},{"phase",at},{"tid",tid()}});changed.wait(lock,[&]{return released;});}
};
Json view(os::LinuxProfileWorker& store){auto value=store.load();const auto paths=store.verified_paths();
    return {{"settings",value.documents.settings},{"scene",value.documents.scene},{"receipts",store.receipts().size()},
        {"generation",store.generation_token()},{"recovered_previous",store.recovered_previous()},{"generations",paths.generations}};
}
}
int main(int argc,char** argv){try{
    need(argc==2&&::geteuid()!=0);std::ifstream input(argv[1]);Json config;input>>config;
    os::ProfileLocation location;location.profile=config.at("profile");location.portable_root=config.at("root");
    const std::set<std::string> caps={"scene.selector","scene.content","scene.edit-locks","scene.visibility","theme.typography","configuration.theme-overrides"};
    std::atomic<bool> available{config.value("available",true)},reentry{false},wrong_thread{false};std::atomic<long> storage_tid{0};
    Gate storage_gate,exit_gate;os::LinuxProfileWorker* pointer=nullptr;
    os::LinuxProfileStore::PolicySource policy_source;
    if(!config.value("native",false))policy_source=[&]{
        long zero=0;storage_tid.compare_exchange_strong(zero,tid());if(storage_tid!=tid())wrong_thread=true;
        storage_gate.hold("policy");if(reentry&&pointer)pointer->load();
        c::Policy policy;policy.available=available;policy.revision=7;return policy;
    };
    os::LinuxProfileWorker store(location,true,caps,std::move(policy_source),[&](const auto& phase){storage_gate.hold(phase);});pointer=&store;
    c::Policy policy;policy.available=true;policy.revision=7;const c::Authority authority{true,"console",{"console"}};
    const auto epoch=config.value("epoch","E1");c::AsyncCommands owner(store,epoch,c::make_resource_provider(store,caps));
    owner.attach(epoch,c::authored_revision(store.load().documents),policy);
    emit({{"event","ready"},{"pid",::getpid()},{"caller_tid",tid()},{"storage_tid",storage_tid.load()},{"snapshot",view(store)}});
    std::thread transaction;std::atomic<bool> done{false};std::atomic<long> transaction_tid{0};
    std::optional<c::AsyncCommands::Completion> completion;Json answer;std::uint64_t now=0;
    const auto shutdown=[&]{owner.invalidate();storage_gate.release();exit_gate.release();if(transaction.joinable())transaction.join();};
    try{
        std::string line;while(std::getline(std::cin,line)){
            const auto q=Json::parse(line);const std::string op=q.at("op");++now;
            if(op=="exit")break;
            try{
                if(op=="start"){
                    need(!transaction.joinable());done=false;completion.reset();answer=nullptr;
                    storage_gate.set(q.value("hold","-"));exit_gate.set(q.value("hold_exit",false)?"exit":"-");
                    const auto kind=q.value("kind","commit");std::uint64_t ticket=0;
                    if(kind=="commit"){
                        const auto admission=owner.submit("fixture:principal","fixture:connection",1,authority,q.at("body"),true,now);
                        if(!admission.ticket){emit({{"event","immediate"},{"result",admission.reply}});continue;}
                        auto next=owner.take();need(next.has_value());ticket=*next;
                    }
                    emit({{"event","started"},{"ticket",ticket}});
                    transaction=std::thread([&,kind,ticket]{
                        transaction_tid=tid();emit({{"event","executing"},{"tid",tid()}});
                        try{if(kind=="commit")completion.emplace(owner.run(ticket));else answer=view(store);}
                        catch(const std::exception& e){answer={{"error",e.what()}};}
                        exit_gate.hold("exit");done=true;
                    });continue;
                }
                if(op=="release"){storage_gate.release();emit({{"released",true}});continue;}
                if(op=="release-exit"){exit_gate.release();emit({{"released",true}});continue;}
                if(op=="finish"){
                    need(transaction.joinable());if(!done){emit({{"pending",true}});continue;}
                    transaction.join();Json out={{"joined_tid",transaction_tid.load()},{"wrong_thread",wrong_thread.load()}};
                    if(completion){need(owner.finish(std::move(*completion),now,true));completion.reset();auto delivery=owner.delivery(now);need(delivery.has_value());out["result"]=delivery->reply;}
                    else out["answer"]=answer;
                    emit(out);continue;
                }
                if(op=="query"||op=="cancel"){emit(owner.query("fixture:principal",authority,q.value("request","R"),op=="cancel",now));continue;}
                if(op=="reconcile"){
                    Json query={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch",q.value("original_epoch","E1")},{"request_id",q.value("request","R")}};
                    emit(owner.reconcile("fixture:principal",authority,query,now));continue;
                }
                if(op=="deny"){available=false;policy.available=false;policy.revision=8;owner.policy(policy);emit({{"denied",true}});continue;}
                if(op=="regrant"){available=true;emit({{"regranted",true}});continue;}
                if(op=="reentry"){reentry=true;store.load();throw syspane::protocol::Error("probe.expected_refusal");}
                if(op=="close"){store.close();emit({{"closed",true}});continue;}
                if(op=="guard"){
                    auto next=store.load();next.documents.settings["revision"]=next.documents.scene["revision"]="1";
                    next.documents.settings["sampling"]["resources_ms"]=1500;
                    next.identity=c::CommitIdentity{"fixture:principal",epoch,"R",q.at("body")};Json facts;
                    const auto guard=[&]{
                        facts["revision"]=c::authored_revision(store.load().documents);facts["receipts"]=store.receipts().size();
                        facts["absent"]=!store.reconcile("fixture:principal",epoch,"R").has_value();
                        facts["path"]=store.verified_paths().generations;facts["generation"]=store.generation_token();facts["previous"]=store.recovered_previous();
                        try{store.publish(next,[]{});}catch(const std::exception& e){facts["nested_publish"]=e.what();}
                        try{store.close();}catch(const std::exception& e){facts["nested_close"]=e.what();}
                    };
                    const auto outcome=store.publish(next,guard);facts["durable"]=outcome==c::Publication::durable;emit(facts);continue;
                }
                if(op=="state"){emit(view(store));continue;}
                throw syspane::protocol::Error("probe.operation");
            }catch(const std::exception& e){emit({{"error",e.what()}});}
        }
    }catch(...){shutdown();throw;}
    shutdown();return 0;
}catch(const std::exception& e){emit({{"error",e.what()}});return 1;}}
