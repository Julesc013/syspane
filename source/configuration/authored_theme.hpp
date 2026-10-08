#pragma once
#include "content.hpp"
namespace syspane::configuration {
struct AuthoredTheme {Json theme,package_pin,theme_pin;ContentPackage package;};
// Reconstruct the canonical content/license identity and compare every byte.
AuthoredTheme validate_authored_theme(const ContentPackage&);
// Pure immutable artifact construction, not filesystem or generation publication.
std::optional<AuthoredTheme> author_theme(const ResourceSet&,const Json& proposed,const Policy&,const std::set<std::string>& capabilities);
}
