#pragma once
#include "processor.hpp"
#include <array>
#include <optional>
#include <string_view>

namespace syspane::platform {
struct LinuxProcessorTopologyText {std::uint32_t index;std::string package,core,peers;};
struct LinuxProcessorFiles {
    std::string online_before,stat,online_after;
    std::vector<LinuxProcessorTopologyText> topology_before,topology_after;
    std::uint64_t ticks_per_second;
};
struct LinuxProcessorRow {
    std::uint32_t index;
    std::int32_t package,core;
    std::vector<std::uint32_t> peers;
    std::array<std::uint64_t,8> accounting;
    std::optional<std::array<std::uint64_t,2>> guest;
};
struct LinuxProcessorCapture {
    ProcessorReadCode code;
    std::int64_t native_error=0;
    std::uint64_t ticks_per_second=0;
    std::vector<LinuxProcessorRow> rows={};
    ProcessorResult counters()const;
};
// Pure bounded decoder; no platform API or runtime dependency.
ProcessorReadCode linux_processor_ids(std::string_view,std::size_t,std::vector<std::uint32_t>&);
LinuxProcessorCapture decode_linux_processors(const LinuxProcessorFiles&,std::size_t limit=8192);
ProcessorReadCode linux_processor_error(int);
bool same_linux_topology(const LinuxProcessorCapture&,const LinuxProcessorCapture&);
#if defined(__linux__)
LinuxProcessorCapture read_linux_processors(const ProcessorRequest&);
#endif
}
