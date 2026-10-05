#include "network_state.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>

namespace r=syspane::runtime;namespace p=syspane::platform;namespace m=syspane::model;
using C=r::NetworkStateCode;
void need(bool value){if(!value)throw std::runtime_error("fixed network reconciliation expectation failed");}
m::Tick tick(std::uint64_t time){return {"epoch:1",time,"clock:1","scope:1"};}
p::NetworkRow row(std::uint64_t key,std::uint64_t receive=100,std::uint64_t transmit=200){return {key,static_cast<std::uint32_t>(key),6,p::NetworkCounters{receive,transmit}};}
C commit(r::NetworkState& state,std::vector<p::NetworkRow> rows,std::uint64_t time,std::uint64_t ticket=1){return state.commit(ticket,state.revision(),{p::NetworkCode::success,0,std::move(rows)},tick(time),tick(time));}
r::NetworkState owner(std::size_t limit=8192){return r::NetworkState("epoch:1","clock:1","scope:1",limit);}
void identity(){
    auto state=owner();need(state.demand(1)==C::accepted);
    need(commit(state,{row(2),row(1)},100)==C::accepted);const auto original=state.sample();
    need(original->values[0].native.native_key==1 && !original->values[0].delta);
    const auto one=original->values[0].lifetime,two=original->values[1].lifetime;
    need(commit(state,{row(1),row(2)},110)==C::accepted && state.sample()->values[0].lifetime==one);
    const auto before=state.revision();need(state.indicate(1,true)==C::accepted && !state.current());
    need(state.commit(1,before,{p::NetworkCode::success,0,{row(1)}},tick(120),tick(120))==C::dirty);
    need(commit(state,{row(1),row(2)},130)==C::accepted);
    const auto replaced=state.sample()->values[0].lifetime;need(replaced!=one && state.sample()->values[1].lifetime==two && !state.sample()->values[0].delta);
    need(commit(state,{row(1)},140)==C::accepted);need(commit(state,{row(1),row(2)},150)==C::accepted && state.sample()->values[1].lifetime!=two);
    auto changed=row(1);changed.native_type=99;need(commit(state,{changed},160)==C::accepted && state.sample()->values[0].lifetime!=replaced);
    const auto typed=state.sample()->values[0].lifetime;changed.index=42;need(commit(state,{changed},170)==C::accepted && state.sample()->values[0].lifetime!=typed);
    need(original->values[0].lifetime==one && original->measured_at.nanoseconds==100);
}
void clock_rate(){
    auto state=owner();state.demand(1);need(commit(state,{row(1)},100)==C::accepted);need(commit(state,{row(1,130,260)},110)==C::accepted);
    auto d=state.sample()->values[0].delta;need(d&&d->receive==30&&d->transmit==60&&d->interval_ns==10);
    need(commit(state,{row(1,130,260)},120)==C::accepted);d=state.sample()->values[0].delta;need(d&&d->receive==0&&d->transmit==0);
    need(commit(state,{row(1,3,4)},130)==C::accepted&&!state.sample()->values[0].delta);
    auto absent=row(1);absent.counters.reset();need(commit(state,{absent},140)==C::accepted&&!state.sample()->values[0].delta);
    need(commit(state,{row(1,6,8)},150)==C::accepted&&!state.sample()->values[0].delta);
    need(commit(state,{row(1,6,8)},150)==C::accepted&&!state.sample()->values[0].delta);
    need(state.commit(1,state.revision(),{p::NetworkCode::success,0,{row(1,9,10)}},tick(160),tick(165))==C::accepted);
    need(state.sample()->measured_at.nanoseconds==160&&state.sample()->completed_at.nanoseconds==165);
    need(commit(state,{row(1)},164)==C::clock_fault&&!state.current());need(commit(state,{row(1)},200)==C::clock_fault);
    for(unsigned mode=0;mode<4;++mode){auto broken=owner();broken.demand(1);auto begin=tick(1),end=tick(2);
        if(mode==0)begin.clock_scope="wrong";
        if(mode==1)end.epoch="wrong";
        if(mode==2)end.clock_id="wrong";
        if(mode==3)end.nanoseconds=0;
        need(broken.commit(1,0,{p::NetworkCode::success,0,{row(1)}},begin,end)==C::clock_fault && !broken.sample());}
    auto extreme=owner();extreme.demand(1);const auto max=std::numeric_limits<std::uint64_t>::max();
    need(commit(extreme,{row(1,0,0)},0)==C::accepted);need(commit(extreme,{row(1,max,max)},max)==C::accepted);
    d=extreme.sample()->values[0].delta;need(d&&d->receive==max&&d->transmit==max&&d->interval_ns==max);
}
void cancellation(){
    auto state=owner();state.demand(1);need(commit(state,{row(1)},100)==C::accepted);const auto previous=state.sample();
    need(state.demand(2)==C::accepted&&!state.current());auto bad=tick(0);bad.clock_scope="wrong";
    need(state.commit(1,0,{p::NetworkCode::failed},bad,bad)==C::obsolete&&!state.faulted());
    need(state.demand(1)==C::obsolete);need(state.demand(0)==C::accepted&&state.demand(2)==C::obsolete);state.demand(3);
    need(state.commit(3,0,{p::NetworkCode::failed,5},tick(110),tick(120))==C::source_failed&&state.sample()==previous&&!state.current());
    state.indicate(1,false);need(state.commit(3,0,{p::NetworkCode::success,0,{row(1)}},tick(130),tick(130))==C::dirty&&state.sample()==previous);
    need(commit(state,{row(1,150,300)},140,3)==C::accepted&&state.current());auto d=state.sample()->values[0].delta;need(d&&d->interval_ns==40);
    state.gap();need(commit(state,{row(1)},150,3)==C::closed&&!state.current()&&state.sample());
}
void capacity(){
    auto state=owner(2);state.demand(1);need(commit(state,{row(1),row(2)},100)==C::accepted);const auto previous=state.sample();
    state.indicate(1,true);need(commit(state,{row(1),row(2)},110)==C::capacity&&state.sample()==previous&&!state.current());
    need(commit(state,{row(2)},120)==C::accepted&&state.sample()->values[0].lifetime==previous->values[1].lifetime);
    for(const auto& rows:std::vector<std::vector<p::NetworkRow>>{{row(0)},{row(1),row(1)},{row(1),{2,1,6,{}}}}){
        auto invalid=owner();invalid.demand(1);need(commit(invalid,rows,100)==C::invalid&&!invalid.sample());
        need(commit(invalid,{row(3)},110)==C::accepted&&invalid.sample()->values[0].lifetime==1);}
    auto invalid=owner();invalid.demand(1);need(invalid.indicate(0,false)==C::invalid&&invalid.faulted());
}
int main(int argc,char** argv){try{need(argc==2);const std::string test=argv[1];
    if(test=="RECONCILE-IDENTITY")identity();else if(test=="RECONCILE-CLOCK-RATE")clock_rate();
    else if(test=="RECONCILE-CANCEL-FAILURE")cancellation();else if(test=="RECONCILE-CAPACITY")capacity();else return 2;
    std::cout<<test<<": pass\n";return 0;}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
