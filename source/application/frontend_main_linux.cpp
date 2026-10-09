#include "frontend_linux.hpp"
#include "bundle_identity.hpp"
#ifndef SYSPANE_FRONTEND_TEST_OBSERVERS
#define SYSPANE_FRONTEND_TEST_OBSERVERS 0
#endif
#if SYSPANE_FRONTEND_TEST_OBSERVERS
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <stdexcept>
#include <unistd.h>
#include <vector>
#endif
int main(int argc,char** argv){
    syspane::application::FrontendTimingObserver timing;
    syspane::application::FrontendPhaseObserver phases;
#if SYSPANE_FRONTEND_TEST_OBSERVERS
    std::vector<syspane::application::FrontendPhaseObservation> journal;
    const auto* phase_option=std::getenv("SYSPANE_TEST_PHASES");const bool phase_enabled=phase_option&&std::strcmp(phase_option,"1")==0;
    const auto* observe=std::getenv("SYSPANE_TEST_TIMING");
    if(observe&&std::strcmp(observe,"1")==0){
        const auto flags=fcntl(STDOUT_FILENO,F_GETFL);
        if(flags<0||fcntl(STDOUT_FILENO,F_SETFL,flags|O_NONBLOCK)<0)return 2;
        timing=[](std::uint64_t work,std::uint64_t delay){
            char row[96];const auto size=std::snprintf(row,sizeof(row),"timing %llu %llu\n",static_cast<unsigned long long>(work),static_cast<unsigned long long>(delay));
            return size>0&&static_cast<std::size_t>(size)<sizeof(row)&&write(STDOUT_FILENO,row,static_cast<std::size_t>(size))==size;
        };
    }
    if(phase_enabled){
        if(!timing)return 2;
        try{journal.reserve(8192);}catch(...){return 2;}
        const auto* fault=std::getenv("SYSPANE_TEST_PHASE_FAULT");
        const bool refuse=fault&&std::strcmp(fault,"refuse")==0,throws=fault&&std::strcmp(fault,"throw")==0;
        if(fault&&!refuse&&!throws)return 2;
        phases=[&journal,refuse,throws](const auto& observation){
            if(observation.phase==syspane::application::FrontendPhase::reply){
                if(throws)throw std::runtime_error("test.phase_observer");
                if(refuse)return false;
            }
            if(journal.size()>=8192)return false;
            journal.push_back(observation);return true;
        };
    }
#endif
    const auto result=syspane::application::run_frontend(argc,argv,syspane::platform::built_helper_bundle_expectation(),true,std::move(timing),std::move(phases));
#if SYSPANE_FRONTEND_TEST_OBSERVERS
    if(phase_enabled){
        // The GTK loop and all frontend owners have ended. No recording I/O is
        // performed inside GTK; ordinary stderr diagnostics remain untouched.
        char row[160];
        const auto emit=[&](int size){return size>0&&static_cast<std::size_t>(size)<sizeof(row)&&write(STDERR_FILENO,row,static_cast<std::size_t>(size))==size;};
        const auto pid=static_cast<unsigned long long>(getpid());
        if(!emit(std::snprintf(row,sizeof(row),"phase-begin %llu %zu\n",pid,journal.size())))return 2;
        for(const auto& v:journal)if(!emit(std::snprintf(row,sizeof(row),"phase %llu %u %llu %u\n",static_cast<unsigned long long>(v.tick),static_cast<unsigned>(v.phase),static_cast<unsigned long long>(v.microseconds),v.completed?1U:0U)))return 2;
        if(!emit(std::snprintf(row,sizeof(row),"phase-end %llu %zu %d\n",pid,journal.size(),result)))return 2;
    }
#endif
    return result;
}
