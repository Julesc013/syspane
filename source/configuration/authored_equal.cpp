#include "authored_equal.hpp"
#include <cmath>
namespace syspane::configuration {
namespace {
bool negative_integer(const Json& n){return n.is_number_integer()&&!n.is_number_unsigned()&&n.get<std::int64_t>()<0;}
bool numbers(const Json& a,const Json& b){
    if(a.is_number_float()&&b.is_number_float())return a.get<double>()==b.get<double>();
    if(!a.is_number_float()&&!b.is_number_float()){
        const bool an=negative_integer(a),bn=negative_integer(b);
        if(an||bn)return an&&bn&&a.get<std::int64_t>()==b.get<std::int64_t>();
        return a.get<std::uint64_t>()==b.get<std::uint64_t>();
    }
    const auto real=(a.is_number_float()?a:b).get<double>();const auto& integer=a.is_number_float()?b:a;
    if(!std::isfinite(real)||std::trunc(real)!=real)return false;
    if(real>=0)return real<18446744073709551616.0&&!negative_integer(integer)&&static_cast<std::uint64_t>(real)==integer.get<std::uint64_t>();
    return real>=-9223372036854775808.0&&!integer.is_number_unsigned()&&static_cast<std::int64_t>(real)==integer.get<std::int64_t>();
}
bool equal_values(const Json& a,const Json& b,unsigned depth){
    if(depth>=64)throw protocol::Error("authored.equality_depth");
    if(a.is_number()&&b.is_number())return numbers(a,b);
    if(a.type()!=b.type())return false;
    if(!a.is_structured())return a==b;
    if(a.size()!=b.size())return false;
    auto other=b.begin();
    for(auto current=a.begin();current!=a.end();++current,++other){
        if(a.is_object()&&current.key()!=other.key())return false;
        if(!equal_values(current.value(),other.value(),depth+1))return false;
    }
    return true;
}
}
bool authored_equal(const Json& left,const Json& right){return equal_values(left,right,0);}
}
