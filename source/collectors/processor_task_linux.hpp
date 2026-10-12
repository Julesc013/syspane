#pragma once
#include "processor_linux.hpp"
#include "state.hpp"
#include <functional>
#include <thread>

namespace syspane::collectors {
class ProcessorTask {
public:
    struct Result {platform::LinuxProcessorCapture acquired;model::Tick begin,end;std::string sampled_utc;};
    const std::uint64_t ticket,plan;
    ProcessorTask(std::uint64_t ticket,std::uint64_t plan,std::function<model::Tick()> clock,
        std::function<platform::LinuxProcessorCapture(const platform::ProcessorRequest&)> read={});
    ~ProcessorTask();
    void cancel(){cancelled_.store(true);}
    bool done()const{return done_.load();}
    Result finish();
private:
    std::atomic_bool cancelled_{false},done_{false};Result result_{};
    std::exception_ptr error_;std::thread thread_;
};
}
