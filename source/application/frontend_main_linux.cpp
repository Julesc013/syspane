#include "frontend_linux.hpp"
#include "bundle_identity.hpp"
#ifndef SYSPANE_EXPERIMENTAL_RECOVERY
#define SYSPANE_EXPERIMENTAL_RECOVERY 0
#endif
#if SYSPANE_EXPERIMENTAL_RECOVERY
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#endif
int main(int argc,char** argv){
    syspane::application::FrontendTimingObserver timing;
#if SYSPANE_EXPERIMENTAL_RECOVERY
    const auto* observe=std::getenv("SYSPANE_TEST_TIMING");
    if(observe&&std::strcmp(observe,"1")==0){
        const auto flags=fcntl(STDOUT_FILENO,F_GETFL);
        if(flags<0||fcntl(STDOUT_FILENO,F_SETFL,flags|O_NONBLOCK)<0)return 2;
        timing=[](std::uint64_t work,std::uint64_t delay){
            char row[96];const auto size=std::snprintf(row,sizeof(row),"timing %llu %llu\n",static_cast<unsigned long long>(work),static_cast<unsigned long long>(delay));
            return size>0&&static_cast<std::size_t>(size)<sizeof(row)&&write(STDOUT_FILENO,row,static_cast<std::size_t>(size))==size;
        };
    }
#endif
    return syspane::application::run_frontend(argc,argv,syspane::platform::built_helper_bundle_expectation(),SYSPANE_EXPERIMENTAL_RECOVERY!=0,std::move(timing));
}
