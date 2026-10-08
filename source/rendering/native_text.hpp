#pragma once
#include "layout.hpp"

namespace syspane::rendering {
struct TextRequest {
    std::string text,language="en",token="foreground",contrast="authored",role="body";
    configuration::Json theme;
    std::optional<scene::Unit> wrap_units;
    unsigned numerator=1,denominator=1;
    std::size_t pixel_budget=4194304;
};
struct TextRaster {
    scene::Rect ink,logical,extent;
    scene::Size preferred;
    scene::Unit baseline=0;
    unsigned lines=0,missing_glyphs=0,width=0,height=0;
    std::vector<std::string> fonts;
    std::vector<unsigned char> rgba; // Explicit premultiplied RGBA8, tightly packed.
};
// Synchronous Linux native backend. Public/authored or synthetic text only until
// the caller has an admitted current-policy pixel/text cache erasure owner.
// No application cache or pointers escape; caller owns all returned bytes.
TextRaster render_text(const TextRequest&);
}
