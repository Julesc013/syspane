#pragma once
#include "authored.hpp"
#include "state.hpp"
#include <cmath>

// Shared exact numeric comparison; callers validate finite values first.
namespace syspane::scene::detail {
using configuration::Json;
struct Number { bool negative=false,real=false;std::uint64_t integer=0;double fraction=0; };
inline Number number(const model::Value& v){
    if(const auto* n=std::get_if<std::uint64_t>(&v))return {false,false,*n,0};
    const auto n=std::get<double>(v);return {n<0,true,0,std::abs(n)};
}
inline Number number(const Json& v){
    if(v.is_number_unsigned())return {false,false,v.get<std::uint64_t>(),0};
    if(v.is_number_integer()){const auto n=v.get<std::int64_t>();return {n<0,false,n<0?static_cast<std::uint64_t>(-(n+1))+1:static_cast<std::uint64_t>(n),0};}
    const auto n=v.get<double>();return {n<0,true,0,std::abs(n)};
}
inline int compare_unsigned_real(std::uint64_t a,double b){
    if(b>=18446744073709551616.0)return -1;
    const auto whole=static_cast<std::uint64_t>(b);
    if(a!=whole)return a<whole?-1:1;
    return b>static_cast<double>(whole)?-1:0;
}
inline int compare(Number a,Number b){
    if(a.negative!=b.negative)return a.negative?-1:1;
    int result=0;
    if(a.real&&b.real)result=a.fraction==b.fraction?0:(a.fraction<b.fraction?-1:1);
    else if(!a.real&&!b.real)result=a.integer==b.integer?0:(a.integer<b.integer?-1:1);
    else result=a.real?-compare_unsigned_real(b.integer,a.fraction):compare_unsigned_real(a.integer,b.fraction);
    return a.negative?-result:result;
}
}
