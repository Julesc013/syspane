#include "profile_worker_linux.hpp"
#include "digest.hpp"
#include <condition_variable>
#include <fstream>
#include <iostream>
#include <mutex>
#include <thread>
#include <sys/syscall.h>
#include <unistd.h>
namespace c=syspane::configuration;namespace os=syspane::platform;using c::Json;
namespace {
void emit(const Json& value){std::cout<<value.dump()<<std::endl;}
long tid(){return ::syscall(SYS_gettid);}
struct Fixture {
    c::Policy policy,original;long storage_tid=0;bool wrong_thread=false;
    unsigned reads=0,mutate_at=0,hold_at=0;bool released=false;
    std::mutex mutex;std::condition_variable changed;
    c::Policy sample(){
        if(!storage_tid)storage_tid=tid();
        if(storage_tid!=tid())wrong_thread=true;
        ++reads;if(reads==mutate_at)++policy.revision;
        if(reads==hold_at){std::unique_lock<std::mutex> lock(mutex);emit({{"event","held"},{"tid",tid()},{"reads",reads}});changed.wait(lock,[&]{return released;});}
        return policy;
    }
    void release(){std::lock_guard<std::mutex> lock(mutex);released=true;changed.notify_all();}
};
Json view(const os::ProfileRecoverySnapshot& snapshot,const c::ResourceSnapshot& retained){
    const auto& value=snapshot.committed;Json packages=Json::object();
    for(const auto& p:value.resources->packages())packages[c::sha256(p->manifest)]={{"manifest",p->manifest},{"assets",p->assets}};
    Json result={{"settings",value.documents.settings},{"scene",value.documents.scene},{"selection",value.resources->selection()},
        {"theme_pin",value.resources->theme_pin()},{"packages",packages},{"shared_resources",value.resources==retained},{"recovery",nullptr}};
    if(snapshot.recovery){const auto& a=*snapshot.recovery;const auto& d=a.directory;
        result["recovery"]={{"profile",d.profile},{"path",d.path},{"uid",d.uid},{"state_device",d.state_device},{"state_inode",d.state_inode},
            {"recovery_device",d.recovery_device},{"recovery_inode",d.recovery_inode},{"generation",a.generation},{"policy_revision",a.policy_revision},{"erase",a.erase}};}
    return result;
}
template<class Store> int session(const Json& config){
    os::ProfileLocation location;location.profile=config.at("profile");location.portable_root=config.at("root");
    std::set<std::string> caps={"scene.selector","scene.content","scene.edit-locks","scene.visibility","theme.typography","configuration.theme-overrides","editor.recovery"};
    if(!config.value("recovery_capability",true))caps.erase("editor.recovery");
    Fixture f;f.policy.available=true;f.policy.revision=7;
    f.policy.disclosure[{"console","history"}]=config.value("history",std::set<std::string>{"sensitive"});
    f.policy.denied_capabilities=config.value("denied",std::set<std::string>{});f.original=f.policy;
    Store store(location,true,caps,[&]{return f.sample();});auto retained=store.load().resources;
    const c::Authority trusted{true,"console",{"console"}};
    auto snapshot=[&](const c::Authority& a){return view(store.recovery_snapshot(a),retained);};
    emit({{"event","ready"},{"pid",::getpid()},{"caller_tid",tid()},{"storage_tid",f.storage_tid},{"snapshot",snapshot(trusted)}});
    std::thread caller;Json pending;long caller_tid=0;
    try{
        std::string line;while(std::getline(std::cin,line)){
            const auto q=Json::parse(line);const std::string op=q.at("op");if(op=="exit")break;
            try{
                if(op=="hold"){
                    if(caller.joinable())throw syspane::protocol::Error("probe.busy");
                    f.reads=0;f.hold_at=q.value("at",1U);f.released=false;
                    caller=std::thread([&]{caller_tid=tid();try{pending=snapshot(trusted);}catch(const std::exception& e){pending={{"error",e.what()}};}});continue;
                }
                if(op=="release"){
                    f.release();caller.join();f.hold_at=0;
                    emit({{"snapshot",pending},{"caller_tid",caller_tid},{"storage_tid",f.storage_tid},{"wrong_thread",f.wrong_thread}});continue;
                }
                if(op=="commit"){
                    c::Transactions tx(store,"E1",c::make_resource_provider(store,caps));
                    auto result=tx.submit("fixture:principal","fixture:connection",q.at("body"),trusted,[&]{return f.policy;},0);
                    retained=store.load().resources;emit({{"result",result},{"snapshot",snapshot(trusted)}});continue;
                }
                if(op=="thread"){
                    Json answer;long other=0;std::thread t([&]{other=tid();try{answer=snapshot(trusted);}catch(const std::exception& e){answer={{"error",e.what()}};}});t.join();
                    emit({{"snapshot",answer},{"caller_tid",other},{"storage_tid",f.storage_tid},{"wrong_thread",f.wrong_thread}});continue;
                }
                if(op=="late-revision"){f.reads=0;f.mutate_at=q.at("at");}
                if(op=="revision")++f.policy.revision;
                if(op=="deny")f.policy.available=false;
                if(op=="profile-denied")f.policy.denied_capabilities.insert("profile.open");
                if(op=="regrant")f.policy=f.original;
                c::Authority authority=trusted;
                if(op=="authority"){authority.authenticated=q.at("authenticated");authority.role=q.at("role");authority.role_grants=q.at("grants").get<std::set<std::string>>();}
                emit(snapshot(authority));
            }catch(const std::exception& e){emit({{"error",e.what()}});}
        }
    }catch(...){f.release();if(caller.joinable())caller.join();throw;}
    f.release();if(caller.joinable())caller.join();return 0;
}
}
int main(int argc,char** argv){try{
    if(argc!=2||::geteuid()==0)throw syspane::protocol::Error("probe.arguments");
    std::ifstream input(argv[1]);Json config;input>>config;
    return config.value("worker",false)?session<os::LinuxProfileWorker>(config):session<os::LinuxProfileStore>(config);
}catch(const std::exception& e){emit({{"error",e.what()}});return 1;}}
