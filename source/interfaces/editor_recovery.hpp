#pragma once
#include <cstddef>
#include <cstdint>
#include <string>

namespace syspane::interfaces {
constexpr std::size_t recovery_record_limit=786432;
// The native owner derives these from its private profile and verified committed
// selector/manifest. Values read from a recovery record are never trusted inputs.
struct RecoveryIdentity {std::string profile,generation;};
struct RecoveryDescription {
    std::string scene_id;
    std::uint64_t revision=0;
    std::size_t widgets=0;
    bool theme_changed=false;
};
}
