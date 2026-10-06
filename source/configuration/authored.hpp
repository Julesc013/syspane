#pragma once
#include "policy.hpp"

namespace syspane::configuration {
struct Authored { Json settings,scene; };
// Throws a bounded protocol::Error; optional annotations remain authored content.
void validate_authored(const Authored& value);
void validate_command(const Json& value);
std::uint64_t authored_revision(const Authored& value);
Authored prepare_authored(const Authored& current,const Json& command,const Authority& authority,const Policy& policy);
// Validate current policy and authorization again just before native publication.
void authorize_authored(const Json& command,const Authority& authority,const Policy& policy,std::uint64_t revision);
}
