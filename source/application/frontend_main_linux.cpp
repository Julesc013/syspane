#include "frontend_linux.hpp"
#include "bundle_identity.hpp"
#ifndef SYSPANE_EXPERIMENTAL_RECOVERY
#define SYSPANE_EXPERIMENTAL_RECOVERY 0
#endif
int main(int argc,char** argv){return syspane::application::run_frontend(argc,argv,syspane::platform::built_helper_bundle_expectation(),SYSPANE_EXPERIMENTAL_RECOVERY!=0);}
