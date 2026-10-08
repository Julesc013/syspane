#include "frontend_linux.hpp"
#include "helper_identity.hpp"
int main(int argc,char** argv){return syspane::application::run_frontend(argc,argv,syspane::platform::built_helper_expectation());}
