#include "processor_windows.hpp"
#include <algorithm>
#include <limits>
#include <map>
#include <new>
#include <set>

namespace syspane::platform {
namespace {
struct Invalid {};
struct Capacity {};
std::uint64_t integer(const std::vector<unsigned char>& bytes,std::size_t offset,std::size_t width){
    if(offset>bytes.size()||width>bytes.size()-offset)throw Invalid{};
    std::uint64_t n=0;for(std::size_t i=0;i<width;++i)n|=static_cast<std::uint64_t>(bytes[offset+i])<<(i*8);return n;
}
unsigned count(std::uint64_t mask){unsigned n=0;while(mask){mask&=mask-1;++n;}return n;}
using Cpu=std::pair<std::uint16_t,std::uint8_t>;
std::set<Cpu> active(const WindowsTopology& value,std::size_t limit){
    if(!limit||limit>8192||value.groups.size()>8192)throw Capacity{};
    if(value.groups.empty()||value.maximum_groups<value.groups.size())throw Invalid{};
    std::set<Cpu> result;
    for(std::size_t n=0;n<value.groups.size();++n){const auto& group=value.groups[n];
        if(group.number!=n||!group.active||!group.maximum||group.maximum>64||group.active>group.maximum||count(group.mask)!=group.active||(group.maximum<64&&(group.mask>>group.maximum)))throw Invalid{};
        for(unsigned bit=0;bit<64;++bit)if(group.mask&(std::uint64_t{1}<<bit)){if(result.size()>=limit)throw Capacity{};result.emplace(group.number,static_cast<std::uint8_t>(bit));}
    }return result;
}
void records(const std::vector<unsigned char>& bytes,std::uint32_t kind,WindowsTopology& value){
    if(bytes.empty())throw Invalid{};
    std::size_t offset=0;
    while(offset<bytes.size()){
        const auto type=integer(bytes,offset,4),size=integer(bytes,offset+4,4);
        if(type!=kind||size<32||size>bytes.size()-offset)throw Invalid{};
        if(kind==4){
            if(!value.groups.empty())throw Invalid{};
            value.maximum_groups=static_cast<std::uint16_t>(integer(bytes,offset+8,2));const auto groups=integer(bytes,offset+10,2);
            if(groups>8192)throw Capacity{};
            if(!groups||size!=32+groups*48)throw Invalid{};
            for(std::uint64_t n=0;n<groups;++n){const auto at=offset+32+static_cast<std::size_t>(n)*48;value.groups.push_back({static_cast<std::uint16_t>(n),static_cast<std::uint8_t>(integer(bytes,at+1,1)),static_cast<std::uint8_t>(integer(bytes,at,1)),integer(bytes,at+40,8)});}
        }else{
            const auto groups=integer(bytes,offset+30,2);if(groups>8192)throw Capacity{};
            if(!groups||size!=32+groups*16)throw Invalid{};
            WindowsRelation relation{static_cast<std::uint8_t>(integer(bytes,offset+8,1)),static_cast<std::uint8_t>(integer(bytes,offset+9,1)),{}};
            for(std::uint64_t n=0;n<groups;++n){const auto at=offset+32+static_cast<std::size_t>(n)*16;relation.masks.push_back({static_cast<std::uint16_t>(integer(bytes,at+8,2)),integer(bytes,at,8)});}
            std::sort(relation.masks.begin(),relation.masks.end());
            auto& output=kind==0?value.cores:value.packages;if(output.size()>=8192)throw Capacity{};output.push_back(std::move(relation));
        }offset+=static_cast<std::size_t>(size);
    }
}
std::map<Cpu,std::size_t> coverage(std::vector<WindowsRelation>& records,const WindowsTopology& topology,const std::set<Cpu>& cpus){
    if(records.empty())throw Invalid{};
    std::sort(records.begin(),records.end(),[](const auto& a,const auto& b){return a.masks<b.masks;});
    std::map<Cpu,std::size_t> result;
    for(std::size_t n=0;n<records.size();++n){const auto& record=records[n];std::set<std::uint16_t> groups;
        for(const auto& affinity:record.masks){
            if(!affinity.mask||affinity.group>=topology.groups.size()||!groups.insert(affinity.group).second)throw Invalid{};
            const auto maximum=topology.groups[affinity.group].maximum;if(maximum<64&&(affinity.mask>>maximum))throw Invalid{};
            for(unsigned bit=0;bit<64;++bit)if(affinity.mask&(std::uint64_t{1}<<bit)){const Cpu cpu{affinity.group,static_cast<std::uint8_t>(bit)};if(cpus.count(cpu)&&!result.emplace(cpu,n).second)throw Invalid{};}
        }
    }
    if(result.size()!=cpus.size())throw Invalid{};
    return result;
}
void validate(WindowsTopology& topology,std::size_t limit){
    const auto cpus=active(topology,limit);const auto cores=coverage(topology.cores,topology,cpus),packages=coverage(topology.packages,topology,cpus);
    std::map<std::size_t,std::size_t> core_packages;
    for(const auto& cpu:cpus){const auto core=cores.at(cpu),package=packages.at(cpu);const auto found=core_packages.emplace(core,package);if(!found.second&&found.first->second!=package)throw Invalid{};}
}
}
ProcessorReadCode windows_processor_error(std::uint32_t code){
    if(code==5||code==0xc0000bdb)return ProcessorReadCode::denied;
    if(code==8||code==14||code==0xc0000bbb)return ProcessorReadCode::capacity;
    if(code==0x800007d1)return ProcessorReadCode::interrupted;
    if(code==50||code==120||code==126||code==127||code==0xc0000bb8||code==0xc0000bb9||code==0xc0000bbe)return ProcessorReadCode::unsupported;
    return ProcessorReadCode::failed;
}
WindowsTopologyResult decode_windows_topology(const std::vector<unsigned char>& groups,const std::vector<unsigned char>& cores,const std::vector<unsigned char>& packages,std::size_t limit){
    if(groups.size()>8388608||cores.size()>8388608||packages.size()>8388608)return {ProcessorReadCode::capacity};
    try{WindowsTopology value;records(groups,4,value);records(cores,0,value);records(packages,3,value);validate(value,limit);return {ProcessorReadCode::success,std::move(value)};}
    catch(const Invalid&){return {ProcessorReadCode::malformed};}catch(const Capacity&){return {ProcessorReadCode::capacity};}catch(const std::bad_alloc&){return {ProcessorReadCode::capacity};}
}
WindowsProcessorCapture decode_windows_processors(const WindowsTopology& first,const WindowsTopology& last,const std::vector<WindowsProcessorRow>& rows,std::size_t limit){
    if(rows.size()>limit||rows.size()>8192)return {ProcessorReadCode::capacity};
    for(const auto* topology:{&first,&last}){
        if(topology->groups.size()>8192||topology->cores.size()>8192||topology->packages.size()>8192)return {ProcessorReadCode::capacity};
        for(const auto* relations:{&topology->cores,&topology->packages})for(const auto& relation:*relations)if(relation.masks.size()>8192)return {ProcessorReadCode::capacity};
    }
    try{
        auto before=first,after=last;validate(before,limit);validate(after,limit);
        if(!(before==after))return {ProcessorReadCode::interrupted};
        const auto cpus=active(before,limit);if(rows.size()!=cpus.size())return {ProcessorReadCode::malformed};
        std::set<Cpu> seen;
        for(const auto& row:rows){
            if(!cpus.count({row.group,row.number})||!seen.emplace(row.group,row.number).second)return {ProcessorReadCode::malformed};
            std::uint64_t total=0;
            for(const auto& part:row.accounting){
                if(part.api_status)return {windows_processor_error(part.api_status),part.api_status};
                if(part.counter_status>1)return {windows_processor_error(part.counter_status),part.counter_status};
                if(part.counter_type!=0x20510500)return {ProcessorReadCode::unsupported};
                if(part.first<0||part.second<=0||part.first>part.second||part.multi_count!=1)return {ProcessorReadCode::malformed};
                if(part.second!=row.accounting[0].second||part.timestamp!=row.accounting[0].timestamp)return {ProcessorReadCode::interrupted};
                const auto amount=static_cast<std::uint64_t>(part.first);if(amount>std::numeric_limits<std::uint64_t>::max()-total)return {ProcessorReadCode::capacity};total+=amount;
            }
        }
        auto sorted=rows;std::sort(sorted.begin(),sorted.end(),[](const auto& a,const auto& b){return std::tie(a.group,a.number)<std::tie(b.group,b.number);});
        return {ProcessorReadCode::success,0,std::move(before),std::move(sorted)};
    }catch(const Invalid&){return {ProcessorReadCode::malformed};}catch(const Capacity&){return {ProcessorReadCode::capacity};}catch(const std::bad_alloc&){return {ProcessorReadCode::capacity};}
}
ProcessorResult WindowsProcessorCapture::counters()const{
    if(code!=ProcessorReadCode::success)return {code,native_error};
    try{ProcessorResult result{ProcessorReadCode::success};result.rows.reserve(rows.size());
        for(const auto& row:rows){std::uint64_t total=0;std::vector<std::uint64_t> parts;for(const auto& part:row.accounting){if(part.first<0)return {ProcessorReadCode::malformed};const auto amount=static_cast<std::uint64_t>(part.first);if(amount>std::numeric_limits<std::uint64_t>::max()-total)return {ProcessorReadCode::capacity};total+=amount;parts.push_back(amount);}result.rows.push_back({"windows:cpu:"+std::to_string(row.group)+":"+std::to_string(row.number),"windows:group:"+std::to_string(row.group),total,parts[2],std::move(parts)});}return result;
    }catch(const std::bad_alloc&){return {ProcessorReadCode::capacity};}
}
}
