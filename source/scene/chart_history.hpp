#pragma once
#include "bindings.hpp"

namespace syspane::scene {
using ChartNumber = std::variant<double,std::uint64_t>;
struct ChartIdentity {
    std::string producer,epoch,entity,field,source,unit,clock_id,clock_scope;
    model::Origin origin=model::Origin::observed;
    bool integer=false;
    bool operator==(const ChartIdentity& other)const;
};
struct ChartPoint {
    std::uint64_t measured_ns=0,generation=0;
    ChartNumber value=std::uint64_t{0};
    bool joins_previous=false;
};
enum class ChartCode {ready,duplicate,gap,clock_unknown,empty,unsupported,denied,invalid,clock_fault,conflict};
struct ChartView {
    ChartCode code;
    BindingCode selection;
    const std::optional<ChartIdentity>& identity;
    const std::vector<ChartPoint>& points;
    std::optional<std::uint64_t> window_end_ns;
    bool capacity_truncated=false,pending_break=false;
};
// Serialized, policy-bound owner only. Observe every admitted publication, not just paints.
// References exist only during the synchronous sink; clear on all authority/lifetime changes.
class ChartHistory {
public:
    ChartHistory(std::uint64_t window_ms,std::size_t max_points);
    ChartHistory(const ChartHistory&)=delete;
    ChartHistory& operator=(const ChartHistory&)=delete;
    void observe(const BindingFrame&,const std::optional<model::Tick>& now,
                 const std::function<void(const ChartView&)>& sink);
    void gap();
    void clear();
private:
    void owner()const;
    void erase();
    ChartCode update(const BindingFrame&,const std::optional<model::Tick>&);
    std::uint64_t window_ns_;
    std::size_t max_points_;
    std::optional<ChartIdentity> identity_;
    std::vector<ChartPoint> points_;
    std::optional<ChartPoint> last_;
    std::optional<std::uint64_t> end_,evicted_,generation_;
    std::optional<ChartCode> fault_;
    bool pending_=true,busy_=false;
};
}
