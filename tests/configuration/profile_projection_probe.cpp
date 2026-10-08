#include "profile_controller_linux.hpp"
#include <fstream>
#include <thread>
#include <sys/syscall.h>
#include <unistd.h>
namespace c=syspane::configuration;
int main(int argc,char** argv){
    if(argc!=4)return 2;
    const auto parent=syspane::protocol::decimal(argv[1]);if(!parent||!*parent)return 2;
    const std::string control=argv[2],phase=argv[3];
    const auto marker=[](const std::string& path){std::ofstream out(path);out<<c::Json{{"pid",::getpid()},{"tid",::syscall(SYS_gettid)}}.dump();};
    return syspane::application::run_profile_controller(*parent,[&]{
        std::ifstream file(control);std::string mode;std::getline(file,mode);
        if(mode=="hang"){marker(control+".policy-held");for(;;)std::this_thread::sleep_for(std::chrono::milliseconds(10));}
        c::Policy value;value.available=mode=="allow"||mode=="drift";value.revision=7;
        for(const auto* channel:{"inspector","accessibility"})value.disclosure[{"console",channel}]={"public","operational","sensitive"};
        if(mode=="drift")value.forced["display.enabled"]=false;
        return value;
    },[&](const std::string& at){if(at!=phase)return;marker(control+".held");while(!std::ifstream(control+".release").good())std::this_thread::sleep_for(std::chrono::milliseconds(10));});
}
