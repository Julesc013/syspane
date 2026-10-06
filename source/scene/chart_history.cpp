#include "chart_history.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <tuple>

namespace syspane::scene {
namespace {
auto key(const ChartIdentity& v){return std::tie(v.producer,v.epoch,v.entity,v.field,v.source,v.unit,v.clock_id,v.clock_scope,v.origin,v.integer);}
bool domain(const model::Tick& t,const ChartIdentity& id){
    return !t.epoch.empty()&&!t.clock_id.empty()&&!t.clock_scope.empty()&&
        t.epoch==id.epoch&&t.clock_id==id.clock_id&&t.clock_scope==id.clock_scope;
}
bool valid(const ChartIdentity& id){
    std::size_t size=0;
    for(const auto* value:{&id.producer,&id.epoch,&id.entity,&id.field,&id.source,&id.unit,&id.clock_id,&id.clock_scope}){
        if(value->empty()||value->size()>8192-size)return false;
        size+=value->size();
    }
    return true;
}
struct Borrow {bool& active;explicit Borrow(bool& flag):active(flag){active=true;}~Borrow(){active=false;}};
}
bool ChartIdentity::operator==(const ChartIdentity& other)const{return key(*this)==key(other);}
ChartHistory::ChartHistory(std::uint64_t window_ms,std::size_t max_points):window_ns_(0),max_points_(max_points){
    if(window_ms<1000||window_ms>3600000||max_points<2||max_points>4096)throw protocol::Error("chart.settings");
    window_ns_=window_ms*1000000;
}
void ChartHistory::owner()const{if(busy_)throw std::logic_error("chart.reentrant");}
void ChartHistory::erase(){
    identity_.reset();std::vector<ChartPoint>().swap(points_);last_.reset();end_.reset();evicted_.reset();generation_.reset();fault_.reset();pending_=true;
}
void ChartHistory::clear(){owner();erase();}
void ChartHistory::gap(){owner();pending_=true;}
ChartCode ChartHistory::update(const BindingFrame& frame,const std::optional<model::Tick>& now){
    const auto reject=[&](ChartCode code){const auto latched=fault_;erase();fault_=latched;return code;};
    const auto fault=[&](ChartCode code){erase();fault_=code;return code;};
    if(frame.code!=BindingCode::matched){
        return reject(frame.code==BindingCode::denied?ChartCode::denied:
            (frame.code==BindingCode::unsupported?ChartCode::unsupported:
             (frame.code==BindingCode::invalid?ChartCode::invalid:ChartCode::empty)));
    }
    if(frame.rows.size()!=1||frame.total!=1||frame.truncated)return reject(ChartCode::invalid);
    const auto& row=frame.rows[0];const auto& o=row.observation;
    if(row.code==BindingCode::denied||o.acquisition==model::Acquisition::denied)return reject(ChartCode::denied);
    if(fault_)return *fault_;
    if(row.code!=BindingCode::matched)return reject(ChartCode::empty);
    if(row.metadata)return reject(ChartCode::unsupported);
    if(o.entity_id!=row.entity)return reject(ChartCode::invalid);
    const auto integer=std::get_if<std::uint64_t>(&o.value);const auto real=std::get_if<double>(&o.value);
    const bool null=std::holds_alternative<std::monostate>(o.value);
    if(!null&&!integer&&!real)return reject(ChartCode::unsupported);
    if(real&&!std::isfinite(*real))return reject(ChartCode::invalid);
    if(null&&!identity_)return reject(ChartCode::gap);
    const auto measured=o.measured_at;
    // A missing measurement may preserve only an already established clock domain.
    const model::Tick* clock=measured?&*measured:(now?&*now:nullptr);
    ChartIdentity id{row.producer,row.epoch,row.entity,o.field,o.source_id,o.unit,
        clock?clock->clock_id:(identity_?identity_->clock_id:std::string()),
        clock?clock->clock_scope:(identity_?identity_->clock_scope:std::string()),
        o.origin,integer!=nullptr||(null&&identity_->integer)};
    if(!clock&&!identity_)return reject(ChartCode::clock_unknown);
    if(!valid(id))return reject(ChartCode::invalid);
    if((measured&&!domain(*measured,id))||(now&&!domain(*now,id)))return fault(ChartCode::clock_fault);
    if(!identity_||!(*identity_==id)){erase();identity_=std::move(id);}
    if(generation_&&row.generation<*generation_)return fault(ChartCode::conflict);
    generation_=row.generation;
    std::optional<ChartNumber> number;
    if(integer)number=ChartNumber(*integer);
    else if(real)number=ChartNumber(*real);
    // Invalid chronology is a fault even when freshness/lease/context prevents admission.
    if(measured&&last_){
        if(measured->nanoseconds<last_->measured_ns)return fault(ChartCode::clock_fault);
        if(measured->nanoseconds==last_->measured_ns&&number&&*number!=last_->value)return fault(ChartCode::conflict);
    }
    if(!now){pending_=true;return ChartCode::clock_unknown;}
    if((end_&&now->nanoseconds<*end_)||(measured&&measured->nanoseconds>now->nanoseconds))return fault(ChartCode::clock_fault);
    end_=now->nanoseconds;const auto start=*end_>window_ns_?*end_-window_ns_:0;
    points_.erase(points_.begin(),std::lower_bound(points_.begin(),points_.end(),start,
        [](const ChartPoint& point,std::uint64_t t){return point.measured_ns<t;}));
    if(!points_.empty())points_.front().joins_previous=false;
    if(evicted_&&*evicted_<start)evicted_.reset();
    const bool eligible=!null&&measured&&row.presentation==recovery::Presentation::active&&
        row.effective==model::Freshness::current&&o.support==model::Support::supported&&
        o.presence==model::Presence::present&&o.acquisition==model::Acquisition::success;
    if(!eligible){pending_=true;return ChartCode::gap;}
    if(last_&&measured->nanoseconds==last_->measured_ns)return ChartCode::duplicate;
    ChartPoint point{measured->nanoseconds,row.generation,*number,!pending_&&!points_.empty()};
    last_=point;pending_=false;
    if(point.measured_ns>=start){
        if(points_.size()==max_points_){evicted_=points_.front().measured_ns;points_.erase(points_.begin());points_.front().joins_previous=false;}
        points_.push_back(std::move(point));
    }
    return ChartCode::ready;
}
void ChartHistory::observe(const BindingFrame& frame,const std::optional<model::Tick>& now,
                           const std::function<void(const ChartView&)>& sink){
    owner();if(!sink)throw std::invalid_argument("chart.sink");
    ChartCode code;
    try{code=update(frame,now);}catch(...){erase();throw;}
    const ChartView result{code,frame.code,identity_,points_,end_,evicted_.has_value(),pending_};
    Borrow borrow(busy_);sink(result);
}
}
