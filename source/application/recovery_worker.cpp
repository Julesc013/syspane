#include "recovery_worker_linux.hpp"
int main(int argc,char** argv){
    if(argc!=2)return 2;
    const auto parent=syspane::protocol::decimal(argv[1]);
    return parent&&*parent?syspane::platform::run_recovery_worker(*parent):2;
}
