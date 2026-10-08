#include "profile_controller_linux.hpp"
#include <fstream>
#include <thread>
#include <sys/syscall.h>
#include <unistd.h>
namespace c=syspane::configuration;
namespace {
void forever(){for(;;)std::this_thread::sleep_for(std::chrono::milliseconds(10));}
void marker(const std::string& path){std::ofstream out(path);out<<c::Json{{"pid",::getpid()},{"tid",::syscall(SYS_gettid)}}.dump();}
}
int main(int argc,char** argv){
    if(argc!=4)return 2;
    const auto parent=syspane::protocol::decimal(argv[1]);if(!parent||!*parent)return 2;
    const std::string control=argv[2],phase=argv[3];
    const auto policy=[&]{
        std::ifstream file(control);std::string mode;std::getline(file,mode);
        if(mode=="hang"){marker(control+".policy-held");forever();}
        if(mode=="wait"){
            marker(control+".policy-held");
            while(!std::ifstream(control+".policy-release").good())std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        c::Policy value;value.available=mode=="allow"||mode=="drift"||mode=="wait";value.revision=7;
        if(mode=="drift")value.forced["display.enabled"]=false;
        return value;
    };
    return syspane::application::run_profile_controller(*parent,policy,[&](const std::string& at){
        if(at!=phase)return;
        marker(control+".held");
        while(!std::ifstream(control+".release").good())std::this_thread::sleep_for(std::chrono::milliseconds(10));
    });
}
