#include "bindings.hpp"
#include "value_compare.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <new>
#include <tuple>

namespace syspane::scene {
namespace {
using configuration::Json;using Code=BindingCode;
struct Stop { Code code; };
void need(bool ok){if(!ok)throw protocol::Error("binding.context");}
bool metadata(const std::string& name){return name=="entity.id"||name=="entity.kind"||name=="entity.display_name";}
bool scope_matches(const BindingScope& scope,const Json& query){return scope.kind==query["kind"]&&
    (scope.kind!="registered_asset"||scope.asset==query["asset_id"]);}
void validate(const std::vector<BindingInput>& inputs,const BindingLimits& limits){
    need(inputs.size()<=16&&limits.output_bytes<=4*1024*1024&&limits.index_bytes<=8*1024*1024&&limits.work_steps<=4194304);
    std::set<std::string> producers;std::set<recovery::DataView*> views;
    for(const auto& input:inputs){
        need(input.view&&views.insert(input.view).second&&protocol::identifier(input.producer)&&producers.insert(input.producer).second);
        need((input.scope.kind=="registered_asset"&&protocol::identifier(input.scope.asset))||
            ((input.scope.kind=="local_host"||input.scope.kind=="current_session")&&input.scope.asset.empty()));
        need(!input.entity_types.empty()&&input.entity_types.size()<=256&&input.fields.size()<=256&&input.pins.size()<=256);
        for(const auto& type:input.entity_types)need(protocol::identifier(type));
        for(const auto& field:input.fields)need(protocol::identifier(field.first)&&!metadata(field.first)&&(!field.second||*field.second>0));
        std::set<std::tuple<std::string,std::string,std::string,std::string,std::string>> pins;
        for(const auto& pin:input.pins){
            need(protocol::identifier(pin.name_space)&&input.entity_types.count(pin.entity_type)&&protocol::identifier(pin.epoch)&&protocol::identifier(pin.entity));
            need(!pin.key.empty()&&pin.key.size()<=2048);
            need(std::count_if(pin.key.begin(),pin.key.end(),[](unsigned char c){return (c&0xc0)!=0x80;})<=512);
            try{need(protocol::parse(Json(pin.key).dump())==pin.key);}catch(const Json::exception&){throw protocol::Error("binding.context");}
            need(pins.emplace(pin.name_space,pin.key,pin.entity_type,pin.epoch,pin.entity).second);
        }
    }
}
using detail::number;
using detail::compare;
struct Datum {
    const model::Value* value=nullptr;const std::string* text=nullptr;
    const model::Observation* observation=nullptr;
    Code field=Code::pending,condition=Code::pending;
    model::Freshness effective=model::Freshness::unknown;
    bool available()const{return condition==Code::matched;}
    int category()const{return text||(value&&std::holds_alternative<std::string>(*value))?3:
        (value&&std::holds_alternative<bool>(*value)?1:2);}
    const std::string& string()const{return text?*text:std::get<std::string>(*value);}
};
int compare(const Datum& a,const Datum& b){
    if(a.category()!=b.category())return a.category()<b.category()?-1:1;
    if(a.category()==3)return a.string()==b.string()?0:(a.string()<b.string()?-1:1);
    if(a.category()==1){const auto x=std::get<bool>(*a.value),y=std::get<bool>(*b.value);return x==y?0:(x?1:-1);}
    return compare(number(*a.value),number(*b.value));
}
bool equal(const Datum& d,const Json& value){
    if(d.category()==3)return value.is_string()&&d.string()==value.get_ref<const std::string&>();
    if(d.category()==1)return value.is_boolean()&&std::get<bool>(*d.value)==value.get<bool>();
    return value.is_number()&&compare(number(*d.value),number(value))==0;
}
int rank(Code c){return c==Code::denied?4:(c==Code::ambiguous?3:(c==Code::unsupported?2:(c==Code::pending?1:0)));}
struct Borrow { const BindingInput* input;const model::Snapshot* snapshot;const recovery::LeaseView* lease; };
struct Candidate {const Borrow* borrow;const model::Entity* entity;Datum field;std::array<Datum,8> sort;};
struct Indexed {const model::Observation* first=nullptr;bool multiple=false;};
using Index=std::map<std::pair<std::string,std::string>,Indexed>;
class Resolver {
public:
    Resolver(const Json& query,const std::vector<Borrow>& borrows,BindingLimits limits):q_(query),borrows_(borrows),limits_(limits){
        field_=q_["field"];requested_.insert(field_);selector_=q_["kind"]=="selector";pin_=q_["kind"]=="persistent_pin";
        collection_=selector_&&q_["mode"]=="collection";limit_=collection_?q_["limit"].get<std::size_t>():1;
        if(selector_){for(const auto& p:q_["predicates"])requested_.insert(p["field"]);for(const auto& s:q_["sort"])requested_.insert(s["field"]);}
    }
    BindingFrame run(){
        bool mapped=false;Code uncertainty=Code::matched;std::vector<Candidate> best;best.reserve(limit_);
        const auto less=[&](const Candidate& a,const Candidate& b){return before(a,b);};
        std::size_t total=0;
        for(const auto& borrow:borrows_){const auto& input=*borrow.input;const auto& snapshot=*borrow.snapshot;
            if(snapshot.producer!=input.producer)throw Stop{Code::invalid};
            if(snapshot.entities.size()>8192||snapshot.observations.size()>65536)throw Stop{Code::capacity};
            std::set<std::string> targets;
            if(pin_)for(const auto& pin:input.pins){step();if(pin.name_space==q_["namespace"]&&pin.key==q_["key"]&&pin.entity_type==q_["entity_type"]){
                mapped=true;if(pin.epoch==snapshot.epoch)targets.insert(pin.entity);}}
            if(!selector_&&!pin_&&snapshot.epoch!=q_["producer_epoch"])continue;
            Index index;std::size_t index_bytes=0;
            for(const auto& observation:snapshot.observations){step();if(!requested_.count(observation.field))continue;
                index_bytes+=128+observation.entity_id.size()+observation.field.size();if(index_bytes>limits_.index_bytes)throw Stop{Code::capacity};
                auto& slot=index[{observation.entity_id,observation.field}];if(slot.first)slot.multiple=true;else slot.first=&observation;}
            for(const auto& entity:snapshot.entities){step();
                if(selector_||pin_){if(entity.kind!=q_["entity_type"])continue;}else if(entity.id!=q_["entity_id"])continue;
                if(pin_&&!targets.count(entity.id))continue;
                bool excluded=false;Code unknown=Code::matched;
                if(selector_)for(const auto& predicate:q_["predicates"]){step();const auto value=datum(borrow,entity,index,predicate["field"]);
                    if(!value.available()){if(rank(value.condition)>rank(unknown))unknown=value.condition;continue;}
                    const auto matches=equal(value,predicate["value"]);if(matches!=(predicate["op"]=="eq"))excluded=true;}
                if(excluded)continue;
                if(unknown!=Code::matched){if(rank(unknown)>rank(uncertainty))uncertainty=unknown;continue;}
                ++total;Candidate candidate{&borrow,&entity,datum(borrow,entity,index,field_),{}};
                if(selector_)for(std::size_t i=0;i<q_["sort"].size();++i)candidate.sort[i]=datum(borrow,entity,index,q_["sort"][i]["field"]);
                if(best.size()<limit_){best.push_back(candidate);std::push_heap(best.begin(),best.end(),less);}
                else if(less(candidate,best.front())){std::pop_heap(best.begin(),best.end(),less);best.back()=candidate;std::push_heap(best.begin(),best.end(),less);}
            }
        }
        if(uncertainty!=Code::matched)throw Stop{uncertainty};
        if(pin_&&!mapped)throw Stop{Code::pending};
        if(!collection_&&total>1)throw Stop{Code::ambiguous};
        if(!total)throw Stop{Code::empty};
        std::sort(best.begin(),best.end(),less);BindingFrame result;result.code=Code::matched;result.total=total;result.truncated=total>best.size();
        for(const auto& candidate:best){const auto bytes=accounted(candidate);if(bytes>limits_.output_bytes-result.accounted_bytes)throw Stop{Code::capacity};
            result.accounted_bytes+=bytes;result.rows.push_back(row(candidate));}
        return result;
    }
private:
    void step(){if(work_==limits_.work_steps)throw Stop{Code::capacity};++work_;}
    Datum datum(const Borrow& borrow,const model::Entity& entity,const Index& index,const std::string& field)const{
        Datum result;
        if(metadata(field)){result.text=field=="entity.id"?&entity.id:(field=="entity.kind"?&entity.kind:&entity.display_name);
            result.field=Code::matched;result.condition=borrow.input->now?Code::matched:Code::pending;
            result.effective=borrow.input->now?model::Freshness::current:model::Freshness::stale;return result;}
        const auto found=index.find({entity.id,field});if(found==index.end())return result;
        if(found->second.multiple){result.field=result.condition=Code::ambiguous;return result;}
        const auto& observation=*found->second.first;result.field=Code::matched;result.observation=&observation;result.value=&observation.value;
        result.effective=borrow.input->now?model::freshness_at(observation,*borrow.input->now,borrow.input->fields.at(field)):
            (observation.support==model::Support::unsupported?model::Freshness::not_applicable:(observation.value.index()?model::Freshness::stale:model::Freshness::unknown));
        if(observation.acquisition==model::Acquisition::denied)result.condition=Code::denied;
        else if(observation.support==model::Support::unsupported)result.condition=Code::unsupported;
        else if(observation.support==model::Support::supported&&observation.acquisition==model::Acquisition::success&&
            observation.presence==model::Presence::present&&observation.value.index()&&result.effective==model::Freshness::current)result.condition=Code::matched;
        return result;
    }
    bool before(const Candidate& a,const Candidate& b){
        if(selector_)for(std::size_t i=0;i<q_["sort"].size();++i){step();const auto& x=a.sort[i];const auto& y=b.sort[i];
            if(x.available()!=y.available())return x.available();
            if(!x.available())continue;
            const auto order=compare(x,y);if(order)return q_["sort"][i]["direction"]=="ascending"?order<0:order>0;}
        return std::tie(a.borrow->snapshot->producer,a.borrow->snapshot->epoch,a.entity->id)<std::tie(b.borrow->snapshot->producer,b.borrow->snapshot->epoch,b.entity->id);
    }
    std::size_t accounted(const Candidate& candidate)const{
        const auto& snap=*candidate.borrow->snapshot;std::size_t bytes=256+snap.producer.size()+snap.epoch.size()+candidate.entity->id.size();
        const auto& d=candidate.field;
        if(d.text)return bytes+candidate.entity->id.size()+field_.size()+d.text->size()+1;
        if(!d.observation)return bytes;
        const auto& o=*d.observation;bytes+=o.entity_id.size()+o.field.size()+o.source_id.size()+o.unit.size()+o.attempted_at.subnanoseconds.size();
        if(const auto* str=std::get_if<std::string>(&o.value))bytes+=str->size();
        if(o.observed_at)bytes+=o.observed_at->subnanoseconds.size();
        if(o.measured_at)bytes+=o.measured_at->epoch.size()+o.measured_at->clock_id.size()+o.measured_at->clock_scope.size();
        if(o.error)bytes+=o.error->code.size();
        return bytes;
    }
    BindingRow row(const Candidate& candidate)const{
        const auto& borrow=*candidate.borrow;const auto& d=candidate.field;BindingRow result;
        result.producer=borrow.snapshot->producer;result.epoch=borrow.snapshot->epoch;result.entity=candidate.entity->id;result.generation=borrow.snapshot->generation;
        result.code=d.field;result.effective=d.effective;result.presentation=borrow.lease->presentation;result.reason=borrow.lease->reason;
        if(d.text){result.metadata=true;auto& o=result.observation;o.entity_id=result.entity;o.field=field_;o.value=*d.text;o.unit="1";o.origin=model::Origin::configured;
            o.support=model::Support::supported;o.acquisition=model::Acquisition::success;o.presence=model::Presence::present;o.freshness=model::Freshness::current;
            if(!borrow.input->now){o.freshness=result.effective=model::Freshness::stale;}return result;}
        if(d.observation){const auto& o=*d.observation;auto& out=result.observation;
            out.entity_id=o.entity_id;out.field=o.field;out.source_id=o.source_id;out.value=o.value;out.unit=o.unit;out.origin=o.origin;out.support=o.support;
            out.acquisition=o.acquisition;out.freshness=o.freshness;out.presence=o.presence;out.observed_at=o.observed_at;out.attempted_at=o.attempted_at;
            out.measured_at=o.measured_at;out.sample_interval_ns=o.sample_interval_ns;out.generation=o.generation;
            if(o.error)out.error=model::Error{o.error->code,"",o.error->retryable};
            if(o.measured_at&&borrow.input->now){
                const auto& measured=*o.measured_at;const auto& now=*borrow.input->now;
                if(!measured.epoch.empty()&&measured.epoch==now.epoch&&measured.clock_id==now.clock_id&&
                   measured.clock_scope==now.clock_scope&&measured.nanoseconds<=now.nanoseconds)
                    result.age_ns=now.nanoseconds-measured.nanoseconds;
            }
        }
        return result;
    }
    const Json& q_;const std::vector<Borrow>& borrows_;BindingLimits limits_;std::set<std::string> requested_;std::string field_;
    bool selector_=false,pin_=false,collection_=false;std::size_t limit_=1,work_=0;
};
BindingFrame empty(Code code){BindingFrame frame;frame.code=code;return frame;}
}
void project_binding(const Json& binding,const std::vector<BindingInput>& inputs,std::uint64_t now_ms,
    const std::function<void(const BindingFrame&)>& sink,BindingLimits limits){
    configuration::validate_binding_document(binding);validate(inputs,limits);need(static_cast<bool>(sink));
    bool delivered=false;
    const auto deliver=[&](const BindingFrame& frame){delivered=true;sink(frame);};
    try{
        if(binding["kind"]=="unresolved_pin")throw Stop{Code::pending};
        std::vector<const BindingInput*> routed;
        for(const auto& input:inputs)if(binding["kind"]=="direct"?input.producer==binding["producer_id"]:
            scope_matches(input.scope,binding["scope"])&&input.entity_types.count(binding["entity_type"].get<std::string>()))routed.push_back(&input);
        if(routed.empty())throw Stop{Code::unsupported};
        bool waiting=false;
        for(const auto* input:routed){const auto state=input->view->status(now_ms);if(!state.permitted)throw Stop{Code::denied};
            waiting=waiting||!state.payload_available||(!input->now&&state.presentation!=recovery::Presentation::retained);}
        if(waiting)throw Stop{Code::pending};
        std::set<std::string> fields{binding["field"].get<std::string>()};
        if(binding["kind"]=="selector")for(const char* key:{"predicates","sort"})for(const auto& item:binding[key])fields.insert(item["field"]);
        for(const auto* input:routed)for(const auto& field:fields)if(!metadata(field)&&!input->fields.count(field))throw Stop{Code::unsupported};
        std::vector<Borrow> borrows;borrows.reserve(routed.size());
        std::function<void(std::size_t)> borrow=[&](std::size_t index){
            if(index==routed.size()){deliver(Resolver(binding,borrows,limits).run());return;}
            const auto* input=routed[index];const auto next=[&](const model::Snapshot& snapshot,const recovery::LeaseView& lease){
                borrows.push_back({input,&snapshot,&lease});borrow(index+1);borrows.pop_back();};
            const bool accepted=input->now?input->view->project_measured(now_ms,*input->now,[&](const auto& snapshot,const auto& lease,const auto&){next(snapshot,lease);}):input->view->project(now_ms,next);
            if(!accepted)throw Stop{Code::pending};
        };
        borrow(0);
    }catch(const Stop& stop){if(delivered)throw;deliver(empty(stop.code));}
    catch(const std::bad_alloc&){if(delivered)throw;deliver(empty(Code::capacity));}
}
}
