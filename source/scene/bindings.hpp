#pragma once
#include "authored.hpp"
#include "data_view.hpp"

namespace syspane::scene {
enum class BindingCode { matched, pending, empty, denied, unsupported, ambiguous, invalid, capacity };
struct BindingScope { std::string kind="local_host", asset; };
struct PinMapping { std::string name_space,key,entity_type,epoch,entity; };
// Trusted controller catalog, not a client document. Complete for the queried scope/type.
struct BindingInput {
    recovery::DataView* view=nullptr;
    std::string producer;
    BindingScope scope;
    std::set<std::string> entity_types;
    std::map<std::string,std::optional<std::uint64_t>> fields;
    std::vector<PinMapping> pins;
    std::optional<model::Tick> now;
};
struct BindingRow {
    std::string producer,epoch,entity;
    std::uint64_t generation=0;
    BindingCode code=BindingCode::pending;
    bool metadata=false; // Synthetic configured field; observation timestamps do not apply.
    model::Observation observation;
    model::Freshness effective=model::Freshness::unknown;
    std::optional<std::uint64_t> age_ns;
    recovery::Presentation presentation=recovery::Presentation::empty;
    recovery::LeaseReason reason=recovery::LeaseReason::none;
};
struct BindingFrame {
    BindingCode code=BindingCode::pending;
    std::size_t total=0,accounted_bytes=0;
    bool truncated=false;
    std::vector<BindingRow> rows;
};
struct BindingLimits { std::size_t output_bytes=4*1024*1024,index_bytes=8*1024*1024,work_steps=4194304; };
// Synchronous policy-bound borrow; the sink cannot retain/export payload or reenter views.
// Invalid grammar/context throws before delivery. Sink exceptions propagate exactly once.
void project_binding(const configuration::Json& binding,const std::vector<BindingInput>& inputs,
    std::uint64_t now_ms,const std::function<void(const BindingFrame&)>& sink,BindingLimits limits={});
enum class BindingBatchCode { ready,capacity };
struct BindingBatch {
    BindingBatchCode code=BindingBatchCode::ready;
    std::vector<BindingFrame> frames;
};
// Ordered queries, one union borrow. Limits account the entire batch (128 bytes
// per frame plus rows); sink lifetime and exception rules match project_binding.
void project_bindings(const std::vector<configuration::Json>& bindings,const std::vector<BindingInput>& inputs,
    std::uint64_t now_ms,const std::function<void(const BindingBatch&)>& sink,BindingLimits limits={});
}
