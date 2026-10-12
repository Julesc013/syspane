#include "measurement_owner.hpp"
#include <algorithm>
#include <atomic>
#include <chrono>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>

namespace c=syspane::collectors;namespace m=syspane::model;
void need(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
void competing(bool serialized){
    std::atomic<unsigned> ready{0},active{0},calls{0};std::atomic_bool start{false},overlap{false};
    const auto native=[&]{
        if(active.fetch_add(1)!=0)overlap=true;
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        const auto ordinal=++calls;--active;
        return m::Tick{"test:epoch",ordinal,"test:clock","test:scope"};
    };
    const auto owner=std::make_shared<c::MeasurementOwner>(native);
    // Copies carry one shared facility, as the two production worker callbacks do.
    const auto read=[owner]{return (*owner)();};
    std::vector<m::Tick> values(8);std::vector<std::thread> workers;
    for(unsigned n=0;n<8;++n)workers.emplace_back([&,n,read]{
        ++ready;while(!start.load())std::this_thread::yield();values[n]=serialized?read():native();
    });
    while(ready.load()!=8) { std::this_thread::yield(); }
    start=true;
    for(auto& worker:workers)worker.join();
    need(calls==8&&active==0,"complete callback results");
    need(overlap.load()!=serialized,serialized?"shared owner prohibits overlapping facility mutation":"unguarded diagnostic exposes overlap");
    std::vector<std::uint64_t> ordinals;
    for(const auto& value:values){need(value.epoch=="test:epoch"&&value.clock_id=="test:clock"&&value.clock_scope=="test:scope","domain strings unchanged");ordinals.push_back(value.nanoseconds);}
    std::sort(ordinals.begin(),ordinals.end());need(ordinals==std::vector<std::uint64_t>({1,2,3,4,5,6,7,8}),"every exact native result returned once");
}
void failure(){
    unsigned calls=0;bool failed=true;
    c::MeasurementOwner owner([&]()->m::Tick{++calls;if(failed)throw std::runtime_error("test.provider_failed");return {"test:epoch",91,"test:clock","test:scope"};});
    for(unsigned n=1;n<=2;++n){bool threw=false;try{(void)owner();}catch(const std::runtime_error& e){threw=std::string(e.what())=="test.provider_failed";}need(threw&&calls==n,"provider failure unchanged, no implicit retry or invented timestamp");}
    failed=false;const auto value=owner();need(calls==3&&value.nanoseconds==91&&value.epoch=="test:epoch","exception releases ownership; provider alone changes outcome");
    bool invalid=false;try{c::MeasurementOwner empty{std::function<m::Tick()>{}};}catch(const std::invalid_argument&){invalid=true;}need(invalid,"empty native callback rejected");
}
int main(int argc,char** argv){try{
    need(argc==2,"case required");const std::string name=argv[1];
    if(name=="OVERLAP"){competing(false);competing(true);}else if(name=="FAILURE")failure();else throw std::runtime_error("unknown case");
    std::cout<<name<<": pass\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
