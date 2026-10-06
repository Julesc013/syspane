#pragma once
#include "policy.hpp"

namespace syspane::configuration {
struct Authored { Json settings,scene; };
// Throws a bounded protocol::Error; optional annotations remain authored content.
void validate_authored(const Authored& value);
void validate_command(const Json& value);
// Closed content schemas use the same compiled validator as authored transactions.
void validate_content_document(const Json& value,const std::string& kind);
void validate_scene_document(const Json& value);
// Copies supported legacy content without guessing chart/image semantics.
Json upgrade_scene_content(const Json& value);
void validate_binding_document(const Json& value);
std::uint64_t authored_revision(const Authored& value);
Authored prepare_authored(const Authored& current,const Json& command,const Authority& authority,const Policy& policy);
// Validate current policy and authorization again just before native publication.
void authorize_authored(const Json& command,const Authority& authority,const Policy& policy,std::uint64_t revision);
}
