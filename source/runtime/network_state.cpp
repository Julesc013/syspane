#include "network_state.hpp"
#include <algorithm>
#include <limits>
#include <set>
#include <stdexcept>

namespace syspane::runtime {
namespace {
bool id(const std::string& value) {
    const auto alnum=[](char c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9');};
    return !value.empty() && value.size()<=256 && alnum(value.front()) &&
        std::all_of(value.begin(),value.end(),[&](char c){return alnum(c)||c==':'||c=='.'||c=='_'||c=='/'||c=='-';});
}
}
NetworkState::NetworkState(std::string epoch,std::string clock,std::string scope,std::size_t limit)
    :epoch_(std::move(epoch)),clock_(std::move(clock)),scope_(std::move(scope)),limit_(limit) {
    if(!id(epoch_)||!id(clock_)||!id(scope_)||!limit||limit>8192)throw std::invalid_argument("network.state_contract");
}
NetworkStateCode NetworkState::demand(std::uint64_t ticket) {
    if(fault_)return NetworkStateCode::closed;
    if(ticket==ticket_)return NetworkStateCode::accepted;
    if(ticket && ticket<=highest_ticket_)return NetworkStateCode::obsolete;
    ticket_=ticket; if(ticket)highest_ticket_=ticket; current_=false; return NetworkStateCode::accepted;
}
NetworkStateCode NetworkState::indicate(std::uint64_t key,bool removed) {
    if(fault_)return NetworkStateCode::closed;
    if(!key){gap();return NetworkStateCode::invalid;}
    if(revision_==std::numeric_limits<std::uint64_t>::max()){gap();return NetworkStateCode::capacity;}
    ++revision_;current_=false;if(removed)active_.erase(key);return NetworkStateCode::accepted;
}
void NetworkState::gap(){fault_=true;current_=false;}
NetworkStateCode NetworkState::commit(std::uint64_t ticket,std::uint64_t revision,const platform::NetworkResult& result,
                                      const model::Tick& start,const model::Tick& end) {
    // An obsolete callback cannot poison a successor with a bad native result/clock.
    if(!ticket || ticket!=ticket_)return NetworkStateCode::obsolete;
    if(fault_)return clock_fault_?NetworkStateCode::clock_fault:NetworkStateCode::closed;
    try{return checked(ticket,revision,result,start,end);}
    catch(const std::bad_alloc&){current_=false;return NetworkStateCode::capacity;}
}
NetworkStateCode NetworkState::checked(std::uint64_t,std::uint64_t revision,const platform::NetworkResult& result,
                                      const model::Tick& start,const model::Tick& end) {
    current_=false;
    if(revision!=revision_)return NetworkStateCode::dirty;
    const auto clock_matches=[&](const model::Tick& time){return time.epoch==epoch_&&time.clock_id==clock_&&time.clock_scope==scope_;};
    if(!clock_matches(start)||!clock_matches(end)||end.nanoseconds<start.nanoseconds ||
        (sample_&&start.nanoseconds<sample_->completed_at.nanoseconds)) {
        gap();clock_fault_=true;return NetworkStateCode::clock_fault;
    }
    if(result.code!=platform::NetworkCode::success)return NetworkStateCode::source_failed;
    if(result.native_error)return NetworkStateCode::invalid;
    if(result.rows.size()>8192)return NetworkStateCode::capacity;
    if(sample_&&sample_->generation==std::numeric_limits<std::uint64_t>::max())return NetworkStateCode::capacity;
    std::map<std::uint64_t,Mapping> mapping;
    auto issued=issued_;
    auto next=std::make_shared<NetworkSample>();next->generation=sample_?sample_->generation+1:1;
    next->revision=revision;next->measured_at=start;next->completed_at=end;
    std::set<std::uint32_t> indices;
    for(const auto& row:result.rows) {
        if(!row.native_key||!row.index||mapping.count(row.native_key)||!indices.insert(row.index).second)return NetworkStateCode::invalid;
        const auto old=active_.find(row.native_key);
        Mapping selected{};
        if(old!=active_.end()&&old->second.index==row.index&&old->second.type==row.native_type)selected=old->second;
        else {if(issued>=limit_)return NetworkStateCode::capacity;selected={++issued,row.index,row.native_type};}
        mapping.emplace(row.native_key,selected);
        NetworkValue value{row,selected.lifetime,{}};
        if(sample_&&row.counters&&start.nanoseconds>sample_->measured_at.nanoseconds) {
            const auto previous=std::lower_bound(sample_->values.begin(),sample_->values.end(),row.native_key,
                [](const auto& item,std::uint64_t key){return item.native.native_key<key;});
            if(previous!=sample_->values.end()&&previous->lifetime==selected.lifetime&&previous->native.counters) {
                const auto& before=*previous->native.counters;
                if(row.counters->receive>=before.receive&&row.counters->transmit>=before.transmit)
                    value.delta=CounterDelta{row.counters->receive-before.receive,row.counters->transmit-before.transmit,
                        start.nanoseconds-sample_->measured_at.nanoseconds};
            }
        }
        next->values.push_back(value);
    }
    std::sort(next->values.begin(),next->values.end(),[](const auto& a,const auto& b){return a.native.native_key<b.native.native_key;});
    std::shared_ptr<const NetworkSample> published=next;
    active_.swap(mapping);sample_.swap(published);issued_=issued;current_=true;
    return NetworkStateCode::accepted;
}
}
