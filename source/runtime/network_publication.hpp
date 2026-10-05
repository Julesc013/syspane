#pragma once
#include "network_state.hpp"
#include "telemetry.hpp"

namespace syspane::runtime {
std::vector<model::Metric> network_metrics();
// The caller retains sampled_utc with the accepted sample and owns publication
// revision/policy. A failed attempt never replaces the source-owned sample.
protocol::Json network_document(const NetworkSample& sample, std::uint64_t generation,
    const std::string& sampled_utc, const std::string& attempted_utc, bool current,
    std::size_t byte_limit=protocol::frame_limit-8192);
}
