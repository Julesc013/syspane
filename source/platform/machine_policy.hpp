#pragma once
#include "policy.hpp"

namespace syspane::platform {
// Fixed protected system source, read-only, no caller-supplied location or authority.
// All unavailable/unsupported/invalid sources return an empty unavailable snapshot.
configuration::Policy machine_policy();
}
