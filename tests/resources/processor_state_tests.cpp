#include "processor_state.hpp"
#include <atomic>
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace r=syspane::runtime;namespace m=syspane::model;
using C=r::ProcessorStateCode;using P=r::ProcessorPending;using R=r::ProcessorReadCode;
void need(bool yes,const char* message){if(!yes)throw std::runtime_error(message);}
m::Tick tick(std::uint64_t ns){return {"epoch:1",ns,"clock:1","scope:1"};}
r::ProcessorCounters cpu(const std::string& id,std::uint64_t total,std::uint64_t idle,const std::string& domain="group:0"){return {id,domain,total,idle};}
r::ProcessorState owner(std::size_t limit=8192){return r::ProcessorState("epoch:1","clock:1","scope:1","test:cpu-scheduling-ticks",limit);}
C commit(r::ProcessorState& state,std::vector<r::ProcessorCounters> rows,std::uint64_t ns,std::uint64_t end=0){return state.commit(1,state.revision(),{R::success,0,std::move(rows)},tick(ns),tick(end?end:ns));}
void pending(const r::ProcessorState& state,P reason){auto value=state.sample();need(value&&state.current()&&value->pending==reason&&!value->aggregate&&value->domains.empty(),"explicit pending projection");for(const auto& cpu:value->processors)need(!cpu.utilization,"pending processor has no utilization");}
void ratio(const r::ProcessorUsage& value,std::uint64_t busy,std::uint64_t total,std::uint64_t interval,double percent){need(value.busy==busy&&value.total==total&&value.interval_ns==interval&&std::abs(value.percent()-percent)<1e-12,"fixed exact ratio and elapsed interval");}
void weighted(){auto state=owner();need(state.demand(1)==C::accepted,"initial demand");need(commit(state,{cpu("b",200,50,"group:1"),cpu("a",100,60)},100,110)==C::accepted,"first complete receipt");pending(state,P::first);auto before=state.sample();need(before->generation==1&&before->processors[0].counters.id=="a","canonical complete IDs");
    need(commit(state,{cpu("b",300,70,"group:1"),cpu("a",160,80)},200,205)==C::accepted,"second receipt");const auto value=state.sample();need(value->generation==2&&value->pending==P::none&&value->counter_definition=="test:cpu-scheduling-ticks","current exact sample metadata");ratio(*value->aggregate,120,160,100,75);ratio(*value->processors[0].utilization,40,60,100,100.0*2/3);ratio(value->domains.at("group:1"),80,100,100,80);need(before->generation==1&&!before->aggregate&&before->measured_at.nanoseconds==100,"old immutable sample preserved");
    auto same=owner();same.demand(1);commit(same,{cpu("a",100,60),cpu("b",200,50)},100);commit(same,{cpu("a",160,80),cpu("b",300,70)},200);ratio(same.sample()->domains.at("group:0"),120,160,100,75);
}
void boundaries(){auto state=owner();state.demand(1);commit(state,{cpu("a",0,0)},0);pending(state,P::first);commit(state,{cpu("a",100,100)},100);ratio(*state.sample()->aggregate,0,100,100,0);commit(state,{cpu("a",200,100)},200);ratio(*state.sample()->aggregate,100,100,100,100);
    commit(state,{cpu("a",200,100)},300);pending(state,P::no_progress);commit(state,{cpu("a",250,125)},400);ratio(*state.sample()->aggregate,25,50,100,50);
    commit(state,{cpu("a",300,150)},400);pending(state,P::interval_zero);commit(state,{cpu("a",400,175)},500);ratio(*state.sample()->aggregate,75,100,100,75);
    bool rejected=false;try{r::ProcessorUsage{0,0,100}.percent();}catch(const std::logic_error&){rejected=true;}need(rejected,"zero denominator never zero percent");
}
void groups(){auto state=owner();state.demand(1);std::vector<r::ProcessorCounters> first,next;
    for(unsigned i=0;i<128;++i){const auto id="cpu:"+std::to_string(i);const auto* domain=i<64?"group:0":"group:1";first.push_back(cpu(id,100,50,domain));next.push_back(cpu(id,200,100,domain));}
    commit(state,first,100);commit(state,next,200);const auto value=state.sample();need(value->processors.size()==128&&value->domains.size()==2,"all 128 processors and two groups contribute");ratio(*value->aggregate,6400,12800,100,50);ratio(value->domains.at("group:0"),3200,6400,100,50);ratio(value->domains.at("group:1"),3200,6400,100,50);
}
void topology(){auto state=owner();state.demand(1);commit(state,{cpu("a",100,50)},100);commit(state,{cpu("a",200,75)},200);need(state.sample()->aggregate.has_value(),"pre-hotplug interval");
    commit(state,{cpu("a",250,100),cpu("b",300,200)},300);pending(state,P::topology_changed);commit(state,{cpu("a",300,125),cpu("b",400,225)},400);ratio(*state.sample()->aggregate,100,150,100,100.0*2/3);
    commit(state,{cpu("b",500,250)},500);pending(state,P::topology_changed);commit(state,{cpu("b",600,275,"group:1")},600);pending(state,P::topology_changed);
    const auto old=state.sample();need(state.topology_changed()==C::accepted&&!state.current()&&state.revision()==1,"explicit topology notice invalidates current projection");auto wrong=tick(0);wrong.epoch="wrong";need(state.commit(1,0,{R::failed,5},wrong,wrong)==C::dirty&&!state.faulted()&&state.sample()==old,"dirty bad-clock callback cannot poison source");commit(state,{cpu("b",700,300,"group:1")},700);pending(state,P::topology_changed);
}
void resets(){auto state=owner();state.demand(1);commit(state,{cpu("a",100,60),cpu("b",200,100)},100);commit(state,{cpu("a",3,1),cpu("b",300,150)},200);pending(state,P::counter_reset);commit(state,{cpu("a",53,21),cpu("b",400,190)},300);ratio(*state.sample()->aggregate,90,150,100,60);
    const auto old=state.sample();need(commit(state,{cpu("a",54,23),cpu("b",500,220)},400)==C::invalid&&state.sample()==old&&!state.current(),"invalid idle delta is not clamped or published");commit(state,{cpu("a",100,50),cpu("b",600,240)},500);pending(state,P::acquisition_gap);
    auto mixed=owner();mixed.demand(1);commit(mixed,{cpu("a",100,50),cpu("b",100,50)},100);need(commit(mixed,{cpu("a",1,0),cpu("b",110,70)},200)==C::invalid,"another reset cannot hide an invalid idle delta");
}
void failures(){for(auto code:{R::denied,R::unsupported,R::cancelled,R::timed_out,R::malformed,R::failed,R::capacity}){auto state=owner();state.demand(1);commit(state,{cpu("a",100,50)},100);auto old=state.sample();need(state.commit(1,0,{code,17},tick(200),tick(205))==C::source_failed&&!state.current()&&state.sample()==old,"failed acquisition preserves old sample as noncurrent");need(state.status().acquisition==code&&state.status().native_error==17,"native source status remains distinct");commit(state,{cpu("a",300,150)},300);pending(state,P::acquisition_gap);commit(state,{cpu("a",400,175)},400);ratio(*state.sample()->aggregate,75,100,100,75);}}
void invalid(){for(unsigned mode=0;mode<6;++mode){auto state=owner(2);state.demand(1);commit(state,{cpu("a",100,50)},100);auto old=state.sample();auto rows=std::vector<r::ProcessorCounters>{cpu("a",200,75)};
    if(mode==0)rows.clear();
    if(mode==1)rows.push_back(cpu("a",200,75));
    if(mode==2)rows[0].id="bad id";
    if(mode==3)rows[0].domain="";
    if(mode==4)rows[0].idle=201;
    if(mode==5)rows[0].id=std::string(257,'a');
    need(commit(state,rows,200)==C::invalid&&state.sample()==old&&!state.current(),"invalid complete candidate is atomic");}
    auto state=owner(1);state.demand(1);commit(state,{cpu("a",100,50)},100);auto old=state.sample();need(commit(state,{cpu("a",200,75),cpu("b",100,50)},200)==C::capacity&&state.sample()==old&&!state.current(),"capacity never truncates processors");need(state.commit(1,0,{R::success,5,{cpu("a",200,75)}},tick(300),tick(300))==C::invalid,"success with native error is invalid");
    for(unsigned mode=0;mode<3;++mode){bool rejected=false;try{r::ProcessorState broken("epoch:1","clock:1","scope:1",mode==0?"bad definition":"valid",mode==1?0:mode==2?8193:1);}catch(const std::invalid_argument&){rejected=true;}need(rejected,"invalid construction rejected");}
}
void overflow(){const auto max=std::numeric_limits<std::uint64_t>::max();auto state=owner();state.demand(1);commit(state,{cpu("a",0,0),cpu("b",0,0)},0);auto old=state.sample();need(commit(state,{cpu("a",max,0),cpu("b",max,0)},100)==C::capacity&&state.sample()==old&&!state.current(),"checked aggregate overflow is atomic");
    auto exact=owner();exact.demand(1);commit(exact,{cpu("a",0,0)},0);commit(exact,{cpu("a",max,0)},max);ratio(*exact.sample()->aggregate,max,max,max,100);need(exact.sample()->processors[0].utilization->total==max,"uint64 exact denominator retained");
}
void demand(){auto state=owner();state.demand(1);commit(state,{cpu("a",100,50)},100);auto old=state.sample();need(state.demand(1)==C::accepted&&state.current(),"idempotent active ticket");state.demand(2);auto wrong=tick(0);wrong.clock_id="wrong";need(state.commit(1,0,{R::failed,5},wrong,wrong)==C::obsolete&&!state.faulted()&&state.sample()==old,"obsolete callback cannot poison successor");need(state.demand(1)==C::obsolete,"retired demand cannot restart");need(state.commit(2,0,{R::success,0,{cpu("a",200,75)}},tick(200),tick(200))==C::accepted,"successor receipt");pending(state,P::demand_changed);state.demand(0);need(!state.current()&&state.demand(2)==C::obsolete,"stopped ticket cannot reactivate");state.demand(3);need(state.commit(3,0,{R::success,0,{cpu("a",300,100)}},tick(300),tick(300))==C::accepted,"new demand receipt");pending(state,P::demand_changed);}
void clocks(){for(unsigned mode=0;mode<5;++mode){auto state=owner();state.demand(1);commit(state,{cpu("a",100,50)},100,110);auto old=state.sample();auto begin=tick(200),end=tick(205);
    if(mode==0)begin.epoch="wrong";
    if(mode==1)end.clock_id="wrong";
    if(mode==2)begin.clock_scope="wrong";
    if(mode==3)end.nanoseconds=199;
    if(mode==4)begin.nanoseconds=109;
    need(state.commit(1,0,{R::success,0,{cpu("a",200,75)}},begin,end)==C::clock_fault&&state.faulted()&&!state.current()&&state.sample()==old,"sticky clock-domain/backward fault");need(commit(state,{cpu("a",300,100)},300)==C::clock_fault&&state.demand(2)==C::closed,"no implicit epoch reset");}}
void threading(){auto state=owner();state.demand(1);commit(state,{cpu("a",100,50)},100);const auto original=state.sample();std::atomic<bool> refused{false};std::thread wrong([&]{try{state.sample();}catch(const std::logic_error&){refused.store(true);}});wrong.join();need(refused.load()&&state.sample()==original&&state.current(),"wrong owner cannot mutate source");std::atomic<bool> readable{false};std::thread reader([&]{readable.store(original->processors[0].counters.total==100&&!original->aggregate);});reader.join();need(readable.load(),"immutable sample can transfer to reader");}
int main(int argc,char** argv){try{need(argc==2,"processor case argument");const std::string name=argv[1];if(name=="WEIGHTED")weighted();else if(name=="BOUNDARIES")boundaries();else if(name=="GROUPS")groups();else if(name=="TOPOLOGY")topology();else if(name=="RESETS")resets();else if(name=="FAILURES")failures();else if(name=="INVALID")invalid();else if(name=="OVERFLOW")overflow();else if(name=="DEMAND")demand();else if(name=="CLOCKS")clocks();else if(name=="THREADING")threading();else throw std::runtime_error("unknown processor case");std::cout<<name<<": pass\n";return 0;}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
