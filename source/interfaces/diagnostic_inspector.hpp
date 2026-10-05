#pragma once
#include <functional>
#include <string>
namespace syspane::interfaces {
// Owner callback returns bounded public text after a fresh policy decision.
int diagnostic_inspector(const std::function<std::string()>& text, bool hidden);
}
