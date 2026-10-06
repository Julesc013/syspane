#pragma once
#include "content.hpp"
namespace syspane::platform {
// Explicit private, uncompressed directories only. No extraction or installation.
std::vector<configuration::ContentPackage> read_content_packages(const std::vector<std::string>& directories);
std::vector<configuration::ContentPackage> read_content_catalog(const std::string& directory);
}
