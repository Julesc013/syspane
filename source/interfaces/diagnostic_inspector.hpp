#pragma once
#include <functional>
#include <string>
namespace syspane::interfaces {
struct PreservationControls {
    std::function<bool()> permitted, busy;
    std::function<bool(std::string, std::string)> start;
    std::function<void()> cancel;
    std::function<std::string()> status;
};
// Owner callback returns bounded public text after a fresh policy decision.
int diagnostic_inspector(const std::function<std::string()>& text, bool hidden, const PreservationControls& controls);
}
