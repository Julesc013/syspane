#pragma once
#include "wire.hpp"
namespace syspane::protocol {
constexpr std::size_t profile_chunk_bytes=4096,profile_frame_floor=12288;
constexpr std::size_t profile_part_limit=1092,profile_byte_limit=73400320;
void validate_profile_request(const Json&);
void validate_profile_result(const Json&);
}
