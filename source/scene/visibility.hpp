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
// Scene 0.5 admits rules; native presentation requires its own erasure owner.
void project_visibility(const configuration::Json& rule,const std::vector<BindingInput>& inputs,
    std::uint64_t now_ms,const std::function<void(const VisibilityResult&)>& sink,BindingLimits limits={});
enum class VisibilitySceneCode { ready,restricted,capacity };
struct VisibilityNode {
    std::string id,parent;
    VisibilityCode own=VisibilityCode::shown;
    bool show_content=true;
    std::string blocker;
};
struct VisibilityDiagnostic { std::string id;VisibilityCode code; };
struct VisibilityScene {
    VisibilitySceneCode code=VisibilitySceneCode::ready;
    std::vector<VisibilityNode> nodes;
    std::vector<VisibilityDiagnostic> diagnostics;
};
// Authored preorder, all own rules, one batch borrow. Derived decisions cannot
// escape this synchronous callback or suppress independently owned core status.
void project_scene_visibility(const configuration::Json& scene,const std::vector<BindingInput>& inputs,
    std::uint64_t now_ms,const std::function<void(const VisibilityScene&)>& sink,BindingLimits limits={});
}
