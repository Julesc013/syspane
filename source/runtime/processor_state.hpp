#pragma once
#include "state.hpp"
#include "processor.hpp"
#include <thread>

namespace syspane::runtime {
using ProcessorReadCode=platform::ProcessorReadCode;
using ProcessorCounters=platform::ProcessorCounters;
using ProcessorResult=platform::ProcessorResult;
enum class ProcessorStateCode {accepted,obsolete,dirty,source_failed,clock_fault,capacity,invalid,closed};
enum class ProcessorPending {none,first,demand_changed,topology_changed,counter_reset,interval_zero,no_progress,acquisition_gap};
struct ProcessorUsage {
    std::uint64_t busy,total,interval_ns;
    double percent()const;
};
struct ProcessorValue {ProcessorCounters counters;std::optional<ProcessorUsage> utilization={};};
struct ProcessorSample {
    std::uint64_t generation,topology_revision;
    model::Tick measured_at,completed_at;
    std::string counter_definition;
    ProcessorPending pending;
    std::vector<ProcessorValue> processors;
    std::map<std::string,ProcessorUsage> domains;
    std::optional<ProcessorUsage> aggregate={};
};
struct ProcessorStatus {ProcessorStateCode code;ProcessorReadCode acquisition;std::int64_t native_error;};
// Serialized acquisition reconciliation, below publication/policy/demand scheduling.
class ProcessorState {
public:
    ProcessorState(std::string epoch,std::string clock,std::string scope,std::string counter_definition,std::size_t limit=8192);
    ProcessorState(const ProcessorState&)=delete;ProcessorState& operator=(const ProcessorState&)=delete;
    ProcessorStateCode demand(std::uint64_t ticket);
    ProcessorStateCode topology_changed();
    ProcessorStateCode commit(std::uint64_t ticket,std::uint64_t topology_revision,const ProcessorResult&,const model::Tick& start,const model::Tick& end);
    std::shared_ptr<const ProcessorSample> sample()const;
    ProcessorStatus status()const;
    bool current()const;bool faulted()const;std::uint64_t revision()const;
private:
    void owner()const;
    ProcessorStateCode checked(const ProcessorResult&,const model::Tick&,const model::Tick&);
    ProcessorStateCode reject(ProcessorStateCode);
    const std::thread::id owner_=std::this_thread::get_id();
    const std::string epoch_,clock_,scope_,definition_;const std::size_t limit_;
    std::uint64_t ticket_=0,highest_=0,revision_=0;
    bool current_=false,fault_=false,gap_=true;
    ProcessorPending gap_reason_=ProcessorPending::first;
    ProcessorStatus status_{ProcessorStateCode::closed,ProcessorReadCode::success,0};
    std::shared_ptr<const ProcessorSample> sample_;
};
}
