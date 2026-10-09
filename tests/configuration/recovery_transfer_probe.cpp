#include "profile_controller_linux.hpp"
#include <fstream>
namespace c=syspane::configuration;
int main(int argc,char** argv){
    if(argc!=4)return 2;
    const auto parent=syspane::protocol::decimal(argv[1]);if(!parent||!*parent)return 2;
    const std::string control=argv[2],initial=argv[3];
    return syspane::application::run_profile_controller(*parent,[&]{
        std::ifstream file(control);std::string mode;std::getline(file,mode);
        c::Policy value;value.available=mode=="allow";value.revision=7;
        for(const char* channel:{"inspector","accessibility","history"})value.disclosure[{"console",channel}]={"public","operational","sensitive"};
        if(initial=="retention-denied")value.denied_capabilities.insert("editor.recovery");
        if(initial=="erase-denied")value.denied_capabilities.insert("editor.recovery.erase");
        return value;
    });
}
