#pragma once
#include "image.hpp"
#include <string_view>
namespace syspane::rendering {
// Worker-only API: call after the admitted OS containment and resource limits.
scene::Image decode_image(std::string_view media,std::string_view bytes);
void restrict_image_worker();
}
