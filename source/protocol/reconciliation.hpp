#pragma once
#include "wire.hpp"

namespace syspane::protocol {
constexpr std::size_t reconciliation_frame_bound=6144;
void validate_reconciliation_request(const Json&);
void validate_reconciliation_result(const Json&,const std::string& current_epoch);
// Consumer binds a response to the complete admitted request/session tuple.
Json consume_reconciliation(const Message&,const Negotiated&,const Json& query,
    const std::string& connection,const std::string& current_epoch);
}
