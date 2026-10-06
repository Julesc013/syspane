#include "native_text.hpp"
#include <pango/pangocairo.h>
#include <algorithm>
#include <cmath>
#include <cstring>
#include <memory>

namespace syspane::rendering {
namespace {
using U=scene::Unit;
using protocol::Error;
template<class T,void(*Free)(T*)> using Owned=std::unique_ptr<T,decltype(Free)>;
void unref_map(PangoFontMap* p){g_object_unref(p);}
void unref_context(PangoContext* p){g_object_unref(p);}
void unref_layout(PangoLayout* p){g_object_unref(p);}
bool ascii_letter(char c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z');}
void text_valid(const std::string& s,std::size_t bytes,std::size_t scalars,bool newline){
    if(s.size()>bytes||!g_utf8_validate(s.data(),static_cast<gssize>(s.size()),nullptr))throw Error("text.input");
    std::size_t count=0,lines=1;
    const char* p=s.data();const char* end=p+s.size();
    while(p<end){
        const auto c=g_utf8_get_char(p);p=g_utf8_next_char(p);
        if(++count>scalars||((c<32||(c>=127&&c<=159))&&!(newline&&c==10)))throw Error("text.input");
        if(c==10&&++lines>64)throw Error("text.input");
    }
}
U down(U v){return v>=0?v/16:-((-v+15)/16);}
U up(U v){return -down(-v);}
scene::Rect rect(PangoRectangle r){
    U x=down(r.x),y=down(r.y);
    return {x,y,up(static_cast<U>(r.x)+r.width)-x,up(static_cast<U>(r.y)+r.height)-y};
}
scene::Rect extent(PangoLayout* layout,scene::Rect* ink=nullptr,scene::Rect* logical=nullptr){
    PangoRectangle a{},b{};pango_layout_get_extents(layout,&a,&b);
    const auto i=rect(a),l=rect(b);
    if(ink)*ink=i;
    if(logical)*logical=l;
    const U x=std::min(i.x,l.x),y=std::min(i.y,l.y);
    scene::Rect e{x,y,std::max(i.x+i.width,l.x+l.width)-x,std::max(i.y+i.height,l.y+l.height)-y};
    if(e.width<0||e.height<=0||e.width>32768*64||e.height>32768*64)throw Error("text.capacity");
    return e;
}
void color(cairo_t* cr,const std::string& s){
    const auto channel=[&](std::size_t offset){return std::stoul(s.substr(offset,2),nullptr,16)/255.0;};
    cairo_set_source_rgba(cr,channel(1),channel(3),channel(5),channel(7));
}
void native_ok(cairo_t* cr,cairo_surface_t* surface){
    if(cairo_status(cr)!=CAIRO_STATUS_SUCCESS||cairo_surface_status(surface)!=CAIRO_STATUS_SUCCESS)throw Error("text.native");
}
TextRaster render(const TextRequest& r){
    configuration::validate_content_document(r.theme,"theme");
    text_valid(r.text,4096,1024,true);
    const auto family=r.theme.at("font").at("family").get<std::string>();
    text_valid(family,512,128,false);
    if(r.language.empty()||r.language.size()>35||!ascii_letter(r.language[0])||
       !std::all_of(r.language.begin(),r.language.end(),[](char c){return ascii_letter(c)||(c>='0'&&c<='9')||c=='-';})||
       (r.token!="foreground"&&r.token!="warning"&&r.token!="error"&&r.token!="muted")||
       (r.contrast!="authored"&&r.contrast!="light"&&r.contrast!="dark")||
       r.numerator<1||r.numerator>16||r.denominator<1||r.denominator>16||
       r.numerator*4<r.denominator||r.numerator>r.denominator*8||
       (r.wrap_units&&(*r.wrap_units<64||*r.wrap_units>32768*64))||
       !r.pixel_budget||r.pixel_budget>4194304)throw Error("text.input");

    Owned<PangoFontMap,unref_map> map(pango_cairo_font_map_new(),unref_map);
    if(!map)throw Error("text.native");
    pango_cairo_font_map_set_resolution(PANGO_CAIRO_FONT_MAP(map.get()),96);
    Owned<PangoContext,unref_context> context(pango_font_map_create_context(map.get()),unref_context);
    if(!context)throw Error("text.native");
    Owned<cairo_font_options_t,cairo_font_options_destroy> options(cairo_font_options_create(),cairo_font_options_destroy);
    cairo_font_options_set_antialias(options.get(),CAIRO_ANTIALIAS_GRAY);
    cairo_font_options_set_hint_style(options.get(),CAIRO_HINT_STYLE_NONE);
    cairo_font_options_set_hint_metrics(options.get(),CAIRO_HINT_METRICS_OFF);
    pango_cairo_context_set_resolution(context.get(),96);
    pango_cairo_context_set_font_options(context.get(),options.get());
    pango_context_set_round_glyph_positions(context.get(),FALSE);
    pango_context_set_language(context.get(),pango_language_from_string(r.language.c_str()));
    Owned<PangoFontDescription,pango_font_description_free> font(pango_font_description_new(),pango_font_description_free);
    pango_font_description_set_family(font.get(),family.c_str());
    pango_font_description_set_weight(font.get(),PANGO_WEIGHT_NORMAL);
    pango_font_description_set_style(font.get(),PANGO_STYLE_NORMAL);
    pango_font_description_set_absolute_size(font.get(),r.theme.at("font").at("size_dip").get<double>()*PANGO_SCALE);
    Owned<PangoLayout,unref_layout> layout(pango_layout_new(context.get()),unref_layout);
    if(!layout)throw Error("text.native");
    pango_layout_set_font_description(layout.get(),font.get());
    pango_layout_set_auto_dir(layout.get(),TRUE);
    pango_layout_set_alignment(layout.get(),PANGO_ALIGN_LEFT);
    pango_layout_set_wrap(layout.get(),PANGO_WRAP_WORD_CHAR);
    pango_layout_set_ellipsize(layout.get(),PANGO_ELLIPSIZE_NONE);
    pango_layout_set_text(layout.get(),r.text.data(),static_cast<int>(r.text.size()));
    TextRaster result;
    const auto preferred=extent(layout.get());result.preferred={preferred.width,preferred.height};
    if(r.wrap_units)pango_layout_set_width(layout.get(),static_cast<int>(*r.wrap_units*16));
    result.extent=extent(layout.get(),&result.ink,&result.logical);
    result.baseline=up(pango_layout_get_baseline(layout.get()));
    result.lines=static_cast<unsigned>(pango_layout_get_line_count(layout.get()));
    result.missing_glyphs=static_cast<unsigned>(pango_layout_get_unknown_glyphs_count(layout.get()));
    if(!result.lines||result.lines>1024)throw Error("text.capacity");
    std::set<std::string> families;
    Owned<PangoLayoutIter,pango_layout_iter_free> iter(pango_layout_get_iter(layout.get()),pango_layout_iter_free);
    if(!iter)throw Error("text.native");
    do{
        auto* run=pango_layout_iter_get_run_readonly(iter.get());
        if(run&&run->item&&run->item->analysis.font){
            Owned<PangoFontDescription,pango_font_description_free> actual(pango_font_describe(run->item->analysis.font),pango_font_description_free);
            const char* name=pango_font_description_get_family(actual.get());
            if(name)families.emplace(name);
        }
    }while(pango_layout_iter_next_run(iter.get()));
    result.fonts.assign(families.begin(),families.end());
    const auto pixels=[&](U size){return (size*r.numerator+64*r.denominator-1)/(64*r.denominator)+2;};
    const auto w=pixels(result.extent.width),h=pixels(result.extent.height);
    if(w>2048||h>2048||static_cast<std::size_t>(w*h)>r.pixel_budget)throw Error("text.capacity");
    result.width=static_cast<unsigned>(w);result.height=static_cast<unsigned>(h);
    Owned<cairo_surface_t,cairo_surface_destroy> surface(cairo_image_surface_create(CAIRO_FORMAT_ARGB32,static_cast<int>(w),static_cast<int>(h)),cairo_surface_destroy);
    Owned<cairo_t,cairo_destroy> cr(cairo_create(surface.get()),cairo_destroy);
    native_ok(cr.get(),surface.get());
    cairo_set_font_options(cr.get(),options.get());
    std::string fg=r.theme.at("tokens").at(r.token),bg=r.theme.at("tokens").at("background");
    if(r.contrast=="light"){fg="#000000ff";bg="#ffffffff";}
    if(r.contrast=="dark"){fg="#ffffffff";bg="#000000ff";}
    cairo_set_operator(cr.get(),CAIRO_OPERATOR_SOURCE);color(cr.get(),bg);cairo_paint(cr.get());
    cairo_set_operator(cr.get(),CAIRO_OPERATOR_OVER);
    cairo_translate(cr.get(),1,1);
    const double scale=static_cast<double>(r.numerator)/r.denominator;
    cairo_scale(cr.get(),scale,scale);
    cairo_translate(cr.get(),-result.extent.x/64.0,-result.extent.y/64.0);
    // Color-font layers must not bypass the selected semantic/contrast color.
    cairo_push_group_with_content(cr.get(),CAIRO_CONTENT_ALPHA);
    cairo_set_source_rgba(cr.get(),1,1,1,1);
    cairo_move_to(cr.get(),0,0);pango_cairo_show_layout(cr.get(),layout.get());
    Owned<cairo_pattern_t,cairo_pattern_destroy> mask(cairo_pop_group(cr.get()),cairo_pattern_destroy);
    if(cairo_pattern_status(mask.get())!=CAIRO_STATUS_SUCCESS)throw Error("text.native");
    color(cr.get(),fg);cairo_mask(cr.get(),mask.get());
    cairo_surface_flush(surface.get());native_ok(cr.get(),surface.get());
    const auto* data=cairo_image_surface_get_data(surface.get());
    const auto stride=cairo_image_surface_get_stride(surface.get());
    if(!data||stride<static_cast<int>(w*4))throw Error("text.native");
    result.rgba.resize(static_cast<std::size_t>(w*h*4));
    for(U y=0;y<h;++y)for(U x=0;x<w;++x){
        std::uint32_t pixel=0;std::memcpy(&pixel,data+y*stride+x*4,4);
        const auto offset=static_cast<std::size_t>((y*w+x)*4);
        result.rgba[offset]=static_cast<unsigned char>(pixel>>16);
        result.rgba[offset+1]=static_cast<unsigned char>(pixel>>8);
        result.rgba[offset+2]=static_cast<unsigned char>(pixel);
        result.rgba[offset+3]=static_cast<unsigned char>(pixel>>24);
    }
    return result;
}
}
TextRaster render_text(const TextRequest& r){
    try{return render(r);}catch(const std::bad_alloc&){throw Error("text.capacity");}
}
}
