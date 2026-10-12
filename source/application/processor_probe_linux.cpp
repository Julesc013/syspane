#if defined(__linux__)
#include "processor_linux.hpp"
#include "processor_state.hpp"
#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <thread>
#include <unistd.h>

namespace p=syspane::platform;namespace r=syspane::runtime;
std::uint64_t now(){return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());}
syspane::model::Tick tick(std::uint64_t value){return {"probe:linux",value,"steady:linux","host:linux"};}
void print(const p::LinuxProcessorCapture& capture,std::uint64_t start,std::uint64_t end){
    std::cout<<"{\"start\":"<<start<<",\"end\":"<<end<<",\"hz\":"<<capture.ticks_per_second<<",\"rows\":[";bool comma=false;
    for(const auto& row:capture.rows){if(comma)std::cout<<',';comma=true;std::cout<<"{\"index\":"<<row.index<<",\"package\":"<<row.package<<",\"core\":"<<row.core<<",\"peers\":[";for(std::size_t i=0;i<row.peers.size();++i){if(i)std::cout<<',';std::cout<<row.peers[i];}std::cout<<"],\"accounting\":[";for(std::size_t i=0;i<8;++i){if(i)std::cout<<',';std::cout<<row.accounting[i];}std::cout<<"],\"guest\":";if(row.guest)std::cout<<'['<<row.guest->at(0)<<','<<row.guest->at(1)<<']';else std::cout<<"null";std::cout<<'}';}std::cout<<"]}";
}
int main(){try{
    std::atomic_bool cancel{true};p::ProcessorRequest request{std::chrono::steady_clock::now()+std::chrono::seconds(10),cancel};
    if(p::read_linux_processors(request).code!=p::ProcessorReadCode::cancelled)throw std::runtime_error("actual cancellation");
    cancel=false;request.deadline=std::chrono::steady_clock::now()-std::chrono::seconds(1);
    if(p::read_linux_processors(request).code!=p::ProcessorReadCode::timed_out)throw std::runtime_error("actual timeout");
    request.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(10);const auto start=now();auto first=p::read_linux_processors(request);const auto end=now();
    if(first.code!=p::ProcessorReadCode::success)throw std::runtime_error("first acquisition code="+std::to_string(static_cast<int>(first.code))+" errno="+std::to_string(first.native_error));
    std::this_thread::sleep_for(std::chrono::milliseconds(250));request.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(10);const auto next_start=now();auto second=p::read_linux_processors(request);const auto next_end=now();
    if(second.code!=p::ProcessorReadCode::success)throw std::runtime_error("second acquisition code="+std::to_string(static_cast<int>(second.code))+" errno="+std::to_string(second.native_error));
    r::ProcessorState state("probe:linux","steady:linux","host:linux","linux:execution-ticks-v1");state.demand(1);
    if(state.commit(1,0,first.counters(),tick(start),tick(end))!=r::ProcessorStateCode::accepted)throw std::runtime_error("first state commit");
    if(!p::same_linux_topology(first,second))state.topology_changed();
    if(state.commit(1,state.revision(),second.counters(),tick(next_start),tick(next_end))!=r::ProcessorStateCode::accepted)throw std::runtime_error("second state commit");
    std::cout<<"{\"uid\":"<<::getuid()<<",\"cancelled\":true,\"timed_out\":true,\"definition\":\"linux:execution-ticks-v1\",\"first\":";print(first,start,end);std::cout<<",\"second\":";print(second,next_start,next_end);
    const auto sample=state.sample();std::cout<<",\"pending\":"<<static_cast<int>(sample->pending)<<",\"aggregate\":";
    if(sample->aggregate)std::cout<<"{\"busy\":"<<sample->aggregate->busy<<",\"total\":"<<sample->aggregate->total<<",\"interval_ns\":"<<sample->aggregate->interval_ns<<'}';else std::cout<<"null";
    std::cout<<",\"ratios\":[";bool comma=false;for(const auto& value:sample->processors){if(comma)std::cout<<',';comma=true;std::cout<<"{\"id\":\""<<value.counters.id<<"\",\"busy\":";if(value.utilization)std::cout<<value.utilization->busy<<",\"total\":"<<value.utilization->total;else std::cout<<"null,\"total\":null";std::cout<<'}';}std::cout<<"]}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
#endif
