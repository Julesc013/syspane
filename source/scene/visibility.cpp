#include "visibility.hpp"
#include "value_compare.hpp"
#include <cmath>

namespace syspane::scene {
namespace {
using configuration::Json;using Code=VisibilityCode;
Code from_binding(BindingCode code){
    switch(code){
    case BindingCode::pending:return Code::pending;
    case BindingCode::empty:return Code::empty;
    case BindingCode::denied:return Code::denied;
    case BindingCode::unsupported:return Code::unsupported;
    case BindingCode::ambiguous:return Code::ambiguous;
    case BindingCode::capacity:return Code::capacity;
    default:return Code::invalid;
    }
}
Code evaluate(const Json& rule,const BindingFrame& frame){
    if(frame.code!=BindingCode::matched)return from_binding(frame.code);
    if(frame.total!=1||frame.rows.size()!=1||frame.truncated)return Code::invalid;
    const auto& row=frame.rows.front();const auto& o=row.observation;
    if(row.code!=BindingCode::matched)return from_binding(row.code);
    if(o.acquisition==model::Acquisition::denied)return Code::denied;
    if(o.support==model::Support::unsupported)return Code::unsupported;
    if(row.presentation!=recovery::Presentation::active)return Code::lease_lost;
    if(o.acquisition!=model::Acquisition::success||o.support!=model::Support::supported||
       o.presence!=model::Presence::present||std::holds_alternative<std::monostate>(o.value))return Code::unavailable;
    if(row.effective!=model::Freshness::current)return Code::stale;
    const auto real=std::get_if<double>(&o.value);
    if(real&&!std::isfinite(*real))return Code::invalid;
    if(o.unit!=rule.at("unit"))return Code::unit_mismatch;
    const auto& literal=rule.at("value");const auto& op=rule.at("op");int order=0;
    if(const auto boolean=std::get_if<bool>(&o.value)){
        if(!literal.is_boolean())return Code::type_mismatch;
        const auto expected=literal.get<bool>();order=*boolean==expected?0:(*boolean?1:-1);
    }else if(const auto text=std::get_if<std::string>(&o.value)){
        if(!literal.is_string())return Code::type_mismatch;
        const auto& expected=literal.get_ref<const std::string&>();order=*text==expected?0:1;
    }else{
        if(!literal.is_number())return Code::type_mismatch;
        order=detail::compare(detail::number(o.value),detail::number(literal));
    }
    const bool show=op=="eq"?order==0:op=="ne"?order!=0:op=="lt"?order<0:op=="le"?order<=0:op=="gt"?order>0:order>=0;
    return show?Code::shown:Code::hidden;
}
}
void project_visibility(const Json& rule,const std::vector<BindingInput>& inputs,std::uint64_t now_ms,
                        const std::function<void(const VisibilityResult&)>& sink,BindingLimits limits){
    configuration::validate_visibility_document(rule);
    if(!sink)throw protocol::Error("binding.context");
    project_binding(rule.at("binding"),inputs,now_ms,[&](const BindingFrame& frame){sink({evaluate(rule,frame)});},limits);
}
}
