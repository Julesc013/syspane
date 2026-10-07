#pragma once
#include "wire.hpp"
#include <vector>
namespace syspane::scene {
struct Image { unsigned width=0,height=0;std::vector<unsigned char> rgba; };
enum class ImageFit { contain,cover,stretch };
void validate_image(const Image&);
Image orient_image(const Image&,unsigned orientation);
Image fit_image(const Image&,unsigned width,unsigned height,ImageFit,std::size_t pixel_budget=4194304);
}
