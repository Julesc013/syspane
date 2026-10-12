#pragma once
#include "processor.hpp"
#include <array>
#include <tuple>

namespace syspane::platform {
struct WindowsGroup {std::uint16_t number;std::uint8_t active,maximum;std::uint64_t mask;bool operator==(const WindowsGroup& b)const{return std::tie(number,active,maximum,mask)==std::tie(b.number,b.active,b.maximum,b.mask);}};
struct WindowsAffinity {std::uint16_t group;std::uint64_t mask;bool operator==(const WindowsAffinity& b)const{return group==b.group&&mask==b.mask;}bool operator<(const WindowsAffinity& b)const{return std::tie(group,mask)<std::tie(b.group,b.mask);}};
struct WindowsRelation {std::uint8_t flags,efficiency;std::vector<WindowsAffinity> masks;bool operator==(const WindowsRelation& b)const{return flags==b.flags&&efficiency==b.efficiency&&masks==b.masks;}};
struct WindowsTopology {
    std::uint16_t maximum_groups=0;
    std::vector<WindowsGroup> groups;
    std::vector<WindowsRelation> cores,packages;
    bool operator==(const WindowsTopology& b)const{return maximum_groups==b.maximum_groups&&groups==b.groups&&cores==b.cores&&packages==b.packages;}
};
struct WindowsTopologyResult {ProcessorReadCode code;WindowsTopology value={};};
WindowsTopologyResult decode_windows_topology(const std::vector<unsigned char>& groups,
    const std::vector<unsigned char>& cores,const std::vector<unsigned char>& packages,std::size_t limit=8192);
struct WindowsProcessorCounter {
    std::uint32_t api_status,counter_status,counter_type,multi_count;
    std::int64_t first,second;
    std::uint64_t timestamp;
};
struct WindowsProcessorRow {
    std::uint16_t group;std::uint8_t number;
    // Fixed order: user, non-idle privileged, idle accounting.
    std::array<WindowsProcessorCounter,3> accounting;
};
struct WindowsProcessorCapture {
    ProcessorReadCode code;std::int64_t native_error=0;
    WindowsTopology topology={};std::vector<WindowsProcessorRow> rows={};
    ProcessorResult counters()const;
};
WindowsProcessorCapture decode_windows_processors(const WindowsTopology&,const WindowsTopology&,
    const std::vector<WindowsProcessorRow>&,std::size_t limit=8192);
ProcessorReadCode windows_processor_error(std::uint32_t code);
#if defined(_WIN64)
WindowsProcessorCapture read_windows_processors(const ProcessorRequest&);
#endif
}
