#pragma once
#include "transaction.hpp"
namespace syspane::configuration {
// Shipped content plus descriptor defaults. No filesystem discovery or policy grant.
Committed initial_profile(const Policy&,const std::set<std::string>& capabilities);
}
