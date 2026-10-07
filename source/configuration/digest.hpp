#pragma once
#include <string>
#include <string_view>
namespace syspane::configuration { std::string sha256(std::string_view bytes);
// Same algorithm, bounded to the declared 16 MiB content-asset ceiling.
std::string content_sha256(std::string_view bytes); }
