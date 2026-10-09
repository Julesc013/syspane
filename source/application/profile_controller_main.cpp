#include "profile_controller_linux.hpp"
#include "network_controller_linux.hpp"
int main(int argc,char** argv){
    if(argc==3&&std::string(argv[1])=="--network"){
        const auto parent=syspane::protocol::decimal(argv[2]);
        return parent&&*parent?syspane::application::run_network_controller(*parent):2;
    }
    if(argc!=2)return 2;
    const auto parent=syspane::protocol::decimal(argv[1]);
    return parent&&*parent?syspane::application::run_profile_controller(*parent):2;
}
