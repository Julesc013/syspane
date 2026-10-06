#include "chart_plot.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <limits>

namespace syspane::scene {
namespace {
void need(bool ok,const char* why="chart.input"){if(!ok)throw protocol::Error(why);}
// Finite binary64 and uint64, in units of 2^-1074. Extra words bound small pixel multipliers.
using Magnitude=std::array<std::uint32_t,68>;
struct Exact {Magnitude words{};bool negative=false;};
int compare(const Magnitude& a,const Magnitude& b){for(std::size_t i=a.size();i>0;--i)if(a[i-1]!=b[i-1])return a[i-1]<b[i-1]?-1:1;return 0;}
int compare(const Exact& a,const Exact& b){if(a.negative!=b.negative)return a.negative?-1:1;return compare(a.words,b.words)*(a.negative?-1:1);}
Exact exact(const ChartNumber& value){
    Exact result;std::uint64_t mantissa=0;unsigned shift=0;
    if(const auto p=std::get_if<std::uint64_t>(&value)){mantissa=*p;shift=1074;}
    else{const double d=std::get<double>(value);need(std::isfinite(d));
        static_assert(sizeof(double)==8&&std::numeric_limits<double>::is_iec559,"binary64 required");
        std::uint64_t bits=0;std::memcpy(&bits,&d,sizeof bits);const auto exponent=static_cast<unsigned>((bits>>52)&2047);
        mantissa=bits&0xfffffffffffffULL;if(exponent){mantissa|=0x10000000000000ULL;shift=exponent-1;}
        result.negative=(bits>>63)!=0&&mantissa!=0;
    }
    for(unsigned bit=0;bit<64;++bit)if((mantissa>>bit)&1)result.words[(bit+shift)/32]|=std::uint32_t{1}<<((bit+shift)%32);
    return result;
}
Magnitude sum(const Magnitude& a,const Magnitude& b){Magnitude out{};std::uint64_t carry=0;
    for(std::size_t i=0;i<a.size();++i){const auto v=static_cast<std::uint64_t>(a[i])+b[i]+carry;out[i]=static_cast<std::uint32_t>(v);carry=v>>32;}need(!carry);return out;}
Magnitude subtract(const Magnitude& a,const Magnitude& b){Magnitude out{};std::uint64_t borrow=0;
    for(std::size_t i=0;i<a.size();++i){const auto v=static_cast<std::uint64_t>(b[i])+borrow;out[i]=static_cast<std::uint32_t>(static_cast<std::uint64_t>(a[i])-v);borrow=a[i]<v?1:0;}need(!borrow);return out;}
Magnitude distance(const Exact& hi,const Exact& lo){need(compare(hi,lo)>=0);if(hi.negative!=lo.negative)return sum(hi.words,lo.words);
    return hi.negative?subtract(lo.words,hi.words):subtract(hi.words,lo.words);}
Magnitude multiply(const Magnitude& a,unsigned n){Magnitude out{};std::uint64_t carry=0;
    for(std::size_t i=0;i<a.size();++i){const auto v=static_cast<std::uint64_t>(a[i])*n+carry;out[i]=static_cast<std::uint32_t>(v);carry=v>>32;}need(!carry);return out;}
unsigned normalized(const Exact& value,const Exact& lo,const Exact& hi,unsigned span){
    if(compare(value,lo)<=0)return 0;
    if(compare(value,hi)>=0)return span;
    const auto numerator=multiply(distance(value,lo),span*2),denominator=distance(hi,lo);
    unsigned lower=0,upper=span;
    while(lower<upper){const auto middle=(lower+upper+1)/2;
        if(compare(numerator,multiply(denominator,middle*2-1))>=0)lower=middle;else upper=middle-1;}
    return lower;
}
struct Pixel {unsigned x,y;};
unsigned steps(Pixel a,Pixel b){return std::max(a.x>b.x?a.x-b.x:b.x-a.x,a.y>b.y?a.y-b.y:b.y-a.y);}
}
ChartPlot plot_chart(const std::vector<ChartPoint>& points,std::optional<std::uint64_t> horizon,
    std::uint64_t window_ms,const ChartAxis& axis,ChartInterpolation interpolation,unsigned width,unsigned height,std::size_t work_limit){
    need(width>=2&&height>=2&&width<=2048&&height<=2048&&window_ms>=1000&&window_ms<=3600000&&points.size()<=4096);
    need(interpolation==ChartInterpolation::linear||interpolation==ChartInterpolation::step);
    need(points.empty()||horizon.has_value());ChartPlot out;out.width=width;out.height=height;
    if(!axis.automatic){need(compare(exact(axis.minimum),exact(axis.maximum))<0);out.minimum=axis.minimum;out.maximum=axis.maximum;}
    const auto duration=window_ms*1000000,end=horizon.value_or(0),start=end>duration?end-duration:0;
    for(std::size_t i=0;i<points.size();++i){const auto& p=points[i];const auto v=exact(p.value);
        need(p.measured_ns>=start&&p.measured_ns<=end&&(!i?!p.joins_previous:p.measured_ns>points[i-1].measured_ns));
        need(p.value.index()==points[0].value.index());if(!p.joins_previous)++out.segments;
        if(axis.automatic){if(!out.minimum||compare(v,exact(*out.minimum))<0)out.minimum=p.value;if(!out.maximum||compare(v,exact(*out.maximum))>0)out.maximum=p.value;}}
    if(axis.automatic&&axis.include_zero&&out.minimum){ChartNumber zero=out.minimum->index()==0?ChartNumber(0.0):ChartNumber(std::uint64_t{0});
        if(compare(exact(*out.minimum),exact(zero))>0)out.minimum=zero;
        if(compare(exact(*out.maximum),exact(zero))<0)out.maximum=zero;}
    std::vector<Pixel> pixels;pixels.reserve(points.size());
    if(!points.empty()){const auto lo=exact(*out.minimum),hi=exact(*out.maximum);const bool constant=compare(lo,hi)==0;
        for(const auto& p:points){const auto v=exact(p.value);if(compare(v,lo)<0||compare(v,hi)>0)++out.clipped;
            const auto x=end==start?width-1:static_cast<unsigned>(((p.measured_ns-start)*(width-1)*2+(end-start))/((end-start)*2));
            const auto y=constant?(height-1)/2:height-1-normalized(v,lo,hi,height-1);pixels.push_back({x,y});}}
    struct Leg {Pixel a,b;};std::vector<Leg> legs;legs.reserve(points.size()*2);
    const auto add=[&](Pixel a,Pixel b){const auto work=static_cast<std::size_t>(steps(a,b))+1;const auto limit=std::min(work_limit,std::size_t{1048576});
        need(out.work<=limit&&work<=limit-out.work,"chart.capacity");out.work+=work;legs.push_back({a,b});};
    for(std::size_t i=0;i<pixels.size();++i){if(!points[i].joins_previous)add(pixels[i],pixels[i]);
        else if(interpolation==ChartInterpolation::linear)add(pixels[i-1],pixels[i]);
        else{const Pixel corner{pixels[i].x,pixels[i-1].y};add(pixels[i-1],corner);add(corner,pixels[i]);}}
    out.mask.resize(static_cast<std::size_t>(width)*height);
    for(const auto& leg:legs){const auto n=steps(leg.a,leg.b);for(unsigned i=0;i<=n;++i){
        const auto coordinate=[&](unsigned a,unsigned b){return n?(2*(a*(n-i)+b*i)+n)/(2*n):a;};
        out.mask[static_cast<std::size_t>(coordinate(leg.a.y,leg.b.y))*width+coordinate(leg.a.x,leg.b.x)]=1;}}
    return out;
}
}
