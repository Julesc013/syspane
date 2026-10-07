#include "image.hpp"
#include <algorithm>
namespace syspane::scene {
namespace {
void need(bool b){if(!b)throw protocol::Error("image.input");}
struct Axis {unsigned lo,hi;std::uint64_t fraction,denominator;bool inside;};
Axis axis(unsigned p,unsigned output,unsigned source,std::uint64_t numerator,std::uint64_t denominator){
    const auto q=(static_cast<std::int64_t>(p)*2+1-output)*static_cast<std::int64_t>(denominator)+static_cast<std::int64_t>(source*numerator);
    const auto d=numerator*2;const bool inside=q>=0&&static_cast<std::uint64_t>(q)<source*d;
    const auto center=q-static_cast<std::int64_t>(numerator);
    const auto clamped=static_cast<std::uint64_t>(std::max(std::int64_t{0},std::min(center,static_cast<std::int64_t>((source-1)*d))));
    const auto lo=static_cast<unsigned>(clamped/d);return {lo,std::min(source-1,lo+1),clamped%d,d,inside};
}
}
void validate_image(const Image& image){
    need(image.width&&image.height&&image.width<=4096&&image.height<=4096);
    const auto count=static_cast<std::size_t>(image.width)*image.height;need(count<=4194304&&image.rgba.size()==count*4);
    for(std::size_t i=0;i<image.rgba.size();i+=4)need(image.rgba[i]<=image.rgba[i+3]&&image.rgba[i+1]<=image.rgba[i+3]&&image.rgba[i+2]<=image.rgba[i+3]);
}
Image orient_image(const Image& image,unsigned orientation){
    validate_image(image);need(orientation>=1&&orientation<=8);
    Image out{orientation>=5?image.height:image.width,orientation>=5?image.width:image.height,{}};out.rgba.resize(image.rgba.size());
    for(unsigned y=0;y<out.height;++y)for(unsigned x=0;x<out.width;++x){unsigned sx=x,sy=y;
        switch(orientation){case 2:sx=image.width-1-x;break;case 3:sx=image.width-1-x;sy=image.height-1-y;break;case 4:sy=image.height-1-y;break;
            case 5:sx=y;sy=x;break;case 6:sx=y;sy=image.height-1-x;break;case 7:sx=image.width-1-y;sy=image.height-1-x;break;case 8:sx=image.width-1-y;sy=x;break;default:break;}
        for(unsigned c=0;c<4;++c)out.rgba[(static_cast<std::size_t>(y)*out.width+x)*4+c]=image.rgba[(static_cast<std::size_t>(sy)*image.width+sx)*4+c];}
    return out;
}
Image fit_image(const Image& image,unsigned width,unsigned height,ImageFit fit,std::size_t budget){
    validate_image(image);need(width&&height&&width<=2048&&height<=2048&&static_cast<std::size_t>(width)*height<=std::min(budget,std::size_t{4194304}));
    need(fit==ImageFit::contain||fit==ImageFit::cover||fit==ImageFit::stretch);
    std::uint64_t nx=width,dx=image.width,ny=height,dy=image.height;
    if(fit!=ImageFit::stretch){const bool use_x=fit==ImageFit::contain?nx*dy<=ny*dx:nx*dy>=ny*dx;if(use_x){ny=nx;dy=dx;}else{nx=ny;dx=dy;}}
    Image out{width,height,{}};out.rgba.resize(static_cast<std::size_t>(width)*height*4);
    for(unsigned y=0;y<height;++y){const auto ay=axis(y,height,image.height,ny,dy);
        for(unsigned x=0;x<width;++x){const auto ax=axis(x,width,image.width,nx,dx);if(!ax.inside||!ay.inside)continue;
            const auto denominator=ax.denominator*ay.denominator;
            for(unsigned c=0;c<4;++c){std::uint64_t total=0;
                for(unsigned j=0;j<2;++j)for(unsigned i=0;i<2;++i){const auto sx=i?ax.hi:ax.lo,sy=j?ay.hi:ay.lo;
                    total+=image.rgba[(static_cast<std::size_t>(sy)*image.width+sx)*4+c]*(i?ax.fraction:ax.denominator-ax.fraction)*(j?ay.fraction:ay.denominator-ay.fraction);}
                out.rgba[(static_cast<std::size_t>(y)*width+x)*4+c]=static_cast<unsigned char>((total*2+denominator)/(denominator*2));}}}
    return out;
}
}
