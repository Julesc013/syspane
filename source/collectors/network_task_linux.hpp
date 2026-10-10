#pragma once
#include "network_watch.hpp"
#include "network_state.hpp"
#include <functional>
#include <thread>

namespace syspane::collectors {
// One joined native acquisition. Only this worker calls the supplied clock while
// active; the watch and clock owner must outlive it. Demand/publication stay on
// the caller. A guardian process is required for non-cooperative native work.
// An optional trusted read callable receives the same deadline/cancellation
// request. Production leaves it empty and uses the supplied native watch.
class NetworkTask {
public:
    struct Result {platform::WatchedNetworkResult acquired; model::Tick begin,end;std::string sampled_utc;};
    const std::uint64_t ticket,revision;
    NetworkTask(platform::NetworkWatch&,std::uint64_t ticket,std::uint64_t revision,
                std::function<model::Tick()> clock,bool failure=false,unsigned hold_ms=0,
                std::function<void()> before_read={},
                std::function<platform::WatchedNetworkResult(const platform::NetworkRequest&)> read={});
    ~NetworkTask();
    void cancel(){cancelled_.store(true);}
    bool done()const{return done_.load();}
    bool read_ready()const{return read_ready_.load();}
    std::uint64_t native_thread()const{return native_thread_.load();}
    Result finish();
private:
    std::atomic_bool cancelled_{false},done_{false},read_ready_{false};
    std::atomic<std::uint64_t> native_thread_{0};
    Result result_{};std::exception_ptr error_;std::thread thread_;
};
}
