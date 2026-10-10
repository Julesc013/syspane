#include "network_task_linux.hpp"
#include "wire.hpp"
#include <array>
#include <ctime>
#include <sys/syscall.h>
#include <unistd.h>

namespace syspane::collectors {
namespace {
std::string utc(){
    const auto value=std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());std::tm calendar{};
    if(!::gmtime_r(&value,&calendar))throw protocol::Error("collector.utc");
    std::array<char,32> buffer{};
    if(!std::strftime(buffer.data(),buffer.size(),"%Y-%m-%dT%H:%M:%SZ",&calendar))throw protocol::Error("collector.utc");
    return buffer.data();
}
}
NetworkTask::NetworkTask(platform::NetworkWatch& watch,std::uint64_t id,std::uint64_t rev,
    std::function<model::Tick()> clock,bool failure,unsigned hold_ms,std::function<void()> before_read,
    std::function<platform::WatchedNetworkResult(const platform::NetworkRequest&)> read)
    :ticket(id),revision(rev){
    if(hold_ms>1500)throw protocol::Error("collector.task_hold");
    thread_=std::thread([this,&watch,clock=std::move(clock),failure,hold_ms,before_read=std::move(before_read),read=std::move(read)]{
        native_thread_.store(static_cast<std::uint64_t>(::syscall(SYS_gettid)));
        try{
            if(before_read)before_read();
            result_.sampled_utc=utc();result_.begin=clock();
            if(failure){result_.acquired.sample={platform::NetworkCode::failed,5};result_.acquired.continuity=true;}
            else {
                const platform::NetworkRequest request{std::chrono::steady_clock::now()+std::chrono::seconds(2),cancelled_};
                result_.acquired=read?read(request):watch.read(request);
            }
            result_.end=clock();read_ready_.store(true);
            // Trusted finite fault injection: preserve the original late-result test.
            if(hold_ms)std::this_thread::sleep_for(std::chrono::milliseconds(hold_ms));
        }catch(...){error_=std::current_exception();}
        done_.store(true);
    });
}
NetworkTask::~NetworkTask(){cancel();if(thread_.joinable())thread_.join();}
NetworkTask::Result NetworkTask::finish(){
    if(!done())throw protocol::Error("collector.task_pending");
    thread_.join();if(error_)std::rethrow_exception(error_);return std::move(result_);
}
}
