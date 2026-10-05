#pragma once
#include "wire.hpp"

namespace syspane::protocol {
enum class TelemetryDirection { consumer_to_producer, producer_to_consumer };
// A local session supplies this only after native authentication/negotiation.
// Matching it validates a document, never a current-policy or role authorization.
struct TelemetryBinding {
    Negotiated negotiated;
    std::string connection, epoch, producer, subscription, channel, classification;
    std::uint64_t policy_revision;
    TelemetryDirection direction;
};
Message decode_telemetry(std::string_view payload, const TelemetryBinding& binding);
// Original body bytes are retained for exact request/publication replay identity.
// Callers still own current authorization, bounded output and connection lifetime.
std::string encode_telemetry(const Message& message, const TelemetryBinding& binding);
} // namespace syspane::protocol
