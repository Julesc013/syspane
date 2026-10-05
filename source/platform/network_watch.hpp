#pragma once
#if defined(__linux__)
#include "network.hpp"
#include <memory>

namespace syspane::platform {
struct NetworkIndication { std::uint64_t key; bool removed; };
struct WatchedNetworkResult {
    NetworkResult sample;
    std::vector<NetworkIndication> indications={};
    std::uint64_t before=0,after=0;
    bool continuity=false;
};
class NetworkWatch {
public:
    NetworkWatch();
    ~NetworkWatch();
    NetworkWatch(const NetworkWatch&)=delete;
    NetworkWatch& operator=(const NetworkWatch&)=delete;
    bool active() const;
    WatchedNetworkResult read(const NetworkRequest&);
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};
}
#endif
