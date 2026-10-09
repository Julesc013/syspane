#pragma once
#include "native_text.hpp"
namespace syspane::rendering {
struct TextBlock {std::string role,text;};
// Owned semantic blocks. Composite dimensions are pixels, not shaped-line metrics.
TextRaster render_blocks(const TextRequest&,const std::vector<TextBlock>&,std::size_t construction_pixels,TextSession* session=nullptr);
}
