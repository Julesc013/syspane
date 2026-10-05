#pragma once
#include "state.hpp"
#include "telemetry.hpp"

namespace syspane::recovery::detail {
// Internal adapter: only an unchanged, codec-validated complete snapshot/delta.
// This constructs reported state; it never submits an acquisition attempt.
model::Publication reported_state(const protocol::Message& message, const protocol::TelemetryBinding& binding);
}
