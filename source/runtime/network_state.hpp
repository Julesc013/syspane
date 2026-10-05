#pragma once
#include "network.hpp"
#include "state.hpp"
#include <map>
#include <memory>
#include <string>

namespace syspane::runtime {
enum class NetworkStateCode { accepted, obsolete, dirty, source_failed, clock_fault, capacity, invalid, closed };
struct CounterDelta { std::uint64_t receive,transmit,interval_ns; };
struct NetworkValue {
    platform::NetworkRow native;
    std::uint64_t lifetime;
    std::optional<CounterDelta> delta;
};
struct NetworkSample {
    std::uint64_t generation,revision;
    model::Tick measured_at,completed_at;
    std::vector<NetworkValue> values;
};
// Serialized source owner, below model/wire publication. Tickets grant no policy.
class NetworkState {
public:
    NetworkState(std::string epoch,std::string clock,std::string scope,std::size_t lifetime_limit=8192);
    NetworkState(const NetworkState&)=delete;
    NetworkState& operator=(const NetworkState&)=delete;
    NetworkStateCode demand(std::uint64_t ticket);
    NetworkStateCode indicate(std::uint64_t key,bool removed);
    void gap();
    NetworkStateCode commit(std::uint64_t ticket,std::uint64_t revision,const platform::NetworkResult& result,
                            const model::Tick& start,const model::Tick& end);
    std::uint64_t revision() const {return revision_;}
    std::shared_ptr<const NetworkSample> sample() const {return sample_;}
    bool current() const {return current_ && ticket_ && !fault_;}
    bool faulted() const {return fault_;}
private:
    struct Mapping {std::uint64_t lifetime;std::uint32_t index,type;};
    NetworkStateCode checked(std::uint64_t ticket,std::uint64_t revision,const platform::NetworkResult&,
                             const model::Tick&,const model::Tick&);
    std::string epoch_,clock_,scope_;
    std::size_t limit_;
    std::uint64_t ticket_=0,highest_ticket_=0,revision_=0,issued_=0;
    bool current_=false,fault_=false,clock_fault_=false;
    std::map<std::uint64_t,Mapping> active_;
    std::shared_ptr<const NetworkSample> sample_;
};
}
