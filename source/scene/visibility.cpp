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
void project_scene_visibility(const Json& scene,const std::vector<BindingInput>& inputs,std::uint64_t now_ms,
                             const std::function<void(const VisibilityScene&)>& sink,BindingLimits limits){
    configuration::validate_scene_document(scene);
    if(!sink)throw protocol::Error("binding.context");
    std::map<std::string,const Json*> widgets;std::vector<const Json*> ordered;std::vector<std::string> parents;
    for(const auto& w:scene.at("widgets"))widgets.emplace(w.at("id").get<std::string>(),&w);
    std::function<void(const std::string&,const std::string&)> visit=[&](const std::string& id,const std::string& parent){
        const auto& w=*widgets.at(id);ordered.push_back(&w);parents.push_back(parent);
        if(w.at("kind")=="group")for(const auto& child:w.at("children"))visit(child.get<std::string>(),id);
    };
    for(const auto& root:scene.at("roots"))visit(root.get<std::string>(),"");
    std::vector<Json> queries;for(const auto* w:ordered)if(w->contains("visibility"))queries.push_back(w->at("visibility").at("binding"));
    project_bindings(queries,inputs,now_ms,[&](const BindingBatch& batch){
        if(batch.code==BindingBatchCode::capacity){sink({VisibilitySceneCode::capacity,{},{}});return;}
        VisibilityScene out;std::map<std::string,std::string> blockers;std::size_t index=0;bool denied=false;
        for(std::size_t n=0;n<ordered.size();++n){const auto& w=*ordered[n];VisibilityNode node;node.id=w.at("id");node.parent=parents[n];
            if(w.contains("visibility"))node.own=evaluate(w.at("visibility"),batch.frames.at(index++));
            denied=denied||node.own==Code::denied;
            if(!node.parent.empty())node.blocker=blockers.at(node.parent);
            if(node.blocker.empty()&&node.own!=Code::shown)node.blocker=node.id;
            node.show_content=node.blocker.empty();blockers.emplace(node.id,node.blocker);
            if(node.own!=Code::shown&&node.own!=Code::hidden)out.diagnostics.push_back({node.id,node.own});
            out.nodes.push_back(std::move(node));
        }
        if(denied)sink({VisibilitySceneCode::restricted,{},{}});else sink(out);
    },limits);
}
}
