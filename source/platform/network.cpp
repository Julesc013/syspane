#include "network.hpp"
namespace syspane::platform {
const char* network_code_name(NetworkCode code) {
    switch (code) {
    case NetworkCode::success: return "success";
    case NetworkCode::cancelled: return "cancelled";
    case NetworkCode::timed_out: return "timed_out";
    case NetworkCode::capacity: return "capacity";
    case NetworkCode::denied: return "denied";
    case NetworkCode::unsupported: return "unsupported";
    case NetworkCode::interrupted: return "interrupted";
    case NetworkCode::malformed: return "malformed";
    case NetworkCode::failed: return "failed";
    }
    return "failed";
}
}
