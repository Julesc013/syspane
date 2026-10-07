#pragma once
#include "bindings.hpp"

namespace syspane::scene {
enum class VisibilityCode {
    shown,hidden,pending,empty,denied,unsupported,ambiguous,invalid,capacity,
    lease_lost,unavailable,stale,unit_mismatch,type_mismatch
};
struct VisibilityResult { VisibilityCode code=VisibilityCode::pending; };
// One bounded comparison inside the existing policy-bound binding borrow.
// Derived decisions are operational data: no retaining/exporting/reentry in sink.
// Scene/native admission is separate; existing scenes do not accept this document.
void project_visibility(const configuration::Json& rule,const std::vector<BindingInput>& inputs,
    std::uint64_t now_ms,const std::function<void(const VisibilityResult&)>& sink,BindingLimits limits={});
}
