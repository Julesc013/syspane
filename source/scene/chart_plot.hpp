#pragma once
#include "chart_history.hpp"
namespace syspane::scene {
struct ChartAxis {bool automatic=true,include_zero=false;ChartNumber minimum=0.0,maximum=1.0;};
enum class ChartInterpolation {linear,step};
struct ChartPlot {
    unsigned width=0,height=0;
    std::optional<ChartNumber> minimum,maximum;
    std::size_t segments=0,clipped=0,work=0;
    std::vector<unsigned char> mask;
};
// Exact finite-number normalization; no payload pointers escape and history is unchanged.
ChartPlot plot_chart(const std::vector<ChartPoint>&,std::optional<std::uint64_t> horizon,
    std::uint64_t window_ms,const ChartAxis&,ChartInterpolation,unsigned width,unsigned height,
    std::size_t work_limit=1048576);
}
