#include "processor_state.hpp"
#include <algorithm>
#include <limits>
#include <stdexcept>

namespace syspane::runtime {
namespace {
bool identifier(const std::string& text){
    const auto alnum=[](char c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9');};
    return !text.empty()&&text.size()<=256&&alnum(text.front())&&std::all_of(text.begin(),text.end(),[&](char c){return alnum(c)||c==':'||c=='.'||c=='_'||c=='/'||c=='-';});
}
bool add(std::uint64_t& value,std::uint64_t amount){if(amount>std::numeric_limits<std::uint64_t>::max()-value)return false;value+=amount;return true;}
}
double ProcessorUsage::percent()const{if(!total||busy>total||!interval_ns)throw std::logic_error("processor.invalid_ratio");return 100.0*(static_cast<double>(busy)/static_cast<double>(total));}
ProcessorState::ProcessorState(std::string epoch,std::string clock,std::string scope,std::string definition,std::size_t limit):
    epoch_(std::move(epoch)),clock_(std::move(clock)),scope_(std::move(scope)),definition_(std::move(definition)),limit_(limit){
    if(!identifier(epoch_)||!identifier(clock_)||!identifier(scope_)||!identifier(definition_)||!limit||limit>8192)throw std::invalid_argument("processor.state_contract");
}
void ProcessorState::owner()const{if(std::this_thread::get_id()!=owner_)throw std::logic_error("processor.owner");}
ProcessorStateCode ProcessorState::demand(std::uint64_t ticket){
    owner();if(fault_)return ProcessorStateCode::closed;if(ticket==ticket_)return ProcessorStateCode::accepted;
    if(ticket&&ticket<=highest_)return ProcessorStateCode::obsolete;
    ticket_=ticket;if(ticket)highest_=ticket;current_=false;gap_=true;gap_reason_=sample_?ProcessorPending::demand_changed:ProcessorPending::first;return ProcessorStateCode::accepted;
}
ProcessorStateCode ProcessorState::topology_changed(){
    owner();if(fault_)return ProcessorStateCode::closed;
    if(revision_==std::numeric_limits<std::uint64_t>::max())return reject(ProcessorStateCode::capacity);
    ++revision_;current_=false;gap_=true;gap_reason_=ProcessorPending::topology_changed;return ProcessorStateCode::accepted;
}
ProcessorStateCode ProcessorState::reject(ProcessorStateCode code){current_=false;gap_=true;gap_reason_=ProcessorPending::acquisition_gap;status_.code=code;return code;}
ProcessorStateCode ProcessorState::commit(std::uint64_t ticket,std::uint64_t revision,const ProcessorResult& result,const model::Tick& start,const model::Tick& end){
    owner();if(!ticket||ticket!=ticket_)return ProcessorStateCode::obsolete;
    if(fault_)return ProcessorStateCode::clock_fault;
    if(revision!=revision_)return ProcessorStateCode::dirty;
    current_=false;status_={ProcessorStateCode::invalid,result.code,result.native_error};
    const auto domain=[&](const model::Tick& tick){return tick.epoch==epoch_&&tick.clock_id==clock_&&tick.clock_scope==scope_;};
    if(!domain(start)||!domain(end)||end.nanoseconds<start.nanoseconds||(sample_&&start.nanoseconds<sample_->completed_at.nanoseconds)){
        fault_=true;return reject(ProcessorStateCode::clock_fault);
    }
    if(result.code!=ProcessorReadCode::success)return reject(ProcessorStateCode::source_failed);
    if(result.native_error)return reject(ProcessorStateCode::invalid);
    try{return checked(result,start,end);}catch(const std::bad_alloc&){return reject(ProcessorStateCode::capacity);}
}
ProcessorStateCode ProcessorState::checked(const ProcessorResult& result,const model::Tick& start,const model::Tick& end){
    if(result.rows.empty())return reject(ProcessorStateCode::invalid);
    if(result.rows.size()>limit_||(sample_&&sample_->generation==std::numeric_limits<std::uint64_t>::max()))return reject(ProcessorStateCode::capacity);
    for(const auto& row:result.rows)if(row.accounting.size()>16||row.accounting.size()!=result.rows.front().accounting.size())return reject(ProcessorStateCode::invalid);
    auto rows=result.rows;std::sort(rows.begin(),rows.end(),[](const auto& a,const auto& b){return a.id<b.id;});
    for(std::size_t i=0;i<rows.size();++i)if(!identifier(rows[i].id)||!identifier(rows[i].domain)||rows[i].idle>rows[i].total||(i&&rows[i].id==rows[i-1].id))return reject(ProcessorStateCode::invalid);
    for(const auto& row:rows){
        if(sample_){const auto before=std::lower_bound(sample_->processors.begin(),sample_->processors.end(),row.id,
            [](const ProcessorValue& value,const std::string& id){return value.counters.id<id;});
            if(before!=sample_->processors.end()&&before->counters.id==row.id&&before->counters.accounting.size()!=row.accounting.size())return reject(ProcessorStateCode::invalid);
        }
    }
    auto next=std::make_shared<ProcessorSample>();next->generation=sample_?sample_->generation+1:1;next->topology_revision=revision_;next->measured_at=start;next->completed_at=end;next->counter_definition=definition_;
    next->pending=gap_?gap_reason_:ProcessorPending::none;next->processors.reserve(rows.size());
    if(!sample_)next->pending=ProcessorPending::first;
    else if(!gap_){
        if(rows.size()!=sample_->processors.size())next->pending=ProcessorPending::topology_changed;
        else for(std::size_t i=0;i<rows.size();++i){const auto& before=sample_->processors[i].counters;
            if(rows[i].id!=before.id||rows[i].domain!=before.domain){next->pending=ProcessorPending::topology_changed;break;}}
        if(next->pending==ProcessorPending::none&&start.nanoseconds==sample_->measured_at.nanoseconds)next->pending=ProcessorPending::interval_zero;
    }
    if(next->pending==ProcessorPending::none){
        bool reset=false,no_progress=false;
        for(std::size_t i=0;i<rows.size();++i){const auto& before=sample_->processors[i].counters;const auto& after=rows[i];
            bool part_reset=false;
            for(std::size_t n=0;n<after.accounting.size();++n)if(after.accounting[n]<before.accounting[n])part_reset=true;
            if(after.total<before.total||after.idle<before.idle||part_reset){reset=true;continue;}
            if(after.idle-before.idle>after.total-before.total)return reject(ProcessorStateCode::invalid);
            if(after.total==before.total)no_progress=true;
        }
        if(reset)next->pending=ProcessorPending::counter_reset;else if(no_progress)next->pending=ProcessorPending::no_progress;
    }
    ProcessorUsage total{0,0,sample_?start.nanoseconds-sample_->measured_at.nanoseconds:0};
    for(std::size_t i=0;i<rows.size();++i){ProcessorValue value{std::move(rows[i]),{}};
        if(next->pending==ProcessorPending::none){const auto& before=sample_->processors[i].counters;const auto denominator=value.counters.total-before.total;const auto busy=denominator-(value.counters.idle-before.idle);
            value.utilization=ProcessorUsage{busy,denominator,total.interval_ns};auto inserted=next->domains.emplace(value.counters.domain,ProcessorUsage{0,0,total.interval_ns});auto& domain=inserted.first->second;
            if(!add(total.busy,busy)||!add(total.total,denominator)||!add(domain.busy,busy)||!add(domain.total,denominator))return reject(ProcessorStateCode::capacity);
        }next->processors.push_back(std::move(value));
    }
    if(next->pending==ProcessorPending::none)next->aggregate=total;
    sample_=std::move(next);current_=true;gap_=false;gap_reason_=ProcessorPending::none;status_.code=ProcessorStateCode::accepted;return status_.code;
}
std::shared_ptr<const ProcessorSample> ProcessorState::sample()const{owner();return sample_;}
ProcessorStatus ProcessorState::status()const{owner();return status_;}
bool ProcessorState::current()const{owner();return current_&&ticket_&&!fault_;}
bool ProcessorState::faulted()const{owner();return fault_;}
std::uint64_t ProcessorState::revision()const{owner();return revision_;}
}
