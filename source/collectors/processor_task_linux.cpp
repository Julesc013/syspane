#include "processor_task_linux.hpp"
#include "wire.hpp"
#include <array>
#include <ctime>

namespace syspane::collectors {
ProcessorTask::ProcessorTask(std::uint64_t id,std::uint64_t revision,std::function<model::Tick()> clock,
    std::function<platform::LinuxProcessorCapture(const platform::ProcessorRequest&)> read):ticket(id),plan(revision){
    if(!id||!revision||!clock)throw protocol::Error("processor.task_contract");
    thread_=std::thread([this,clock=std::move(clock),read=std::move(read)]{
        try{
            const auto value=std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());std::tm calendar{};std::array<char,32> text{};
            if(!::gmtime_r(&value,&calendar)||!std::strftime(text.data(),text.size(),"%Y-%m-%dT%H:%M:%SZ",&calendar))throw protocol::Error("processor.utc");
            result_.sampled_utc=text.data();result_.begin=clock();
            const platform::ProcessorRequest request{std::chrono::steady_clock::now()+std::chrono::seconds(2),cancelled_};
            result_.acquired=read?read(request):platform::read_linux_processors(request);result_.end=clock();
        }catch(...){error_=std::current_exception();}done_.store(true);
    });
}
ProcessorTask::~ProcessorTask(){cancel();if(thread_.joinable())thread_.join();}
ProcessorTask::Result ProcessorTask::finish(){if(!done())throw protocol::Error("processor.task_pending");thread_.join();if(error_)std::rethrow_exception(error_);return std::move(result_);}
}
