#include "processor_linux.hpp"
#include <algorithm>
#include <cerrno>
#include <limits>
#include <map>
#include <new>

namespace syspane::platform {
namespace {
constexpr std::size_t list_bytes=65536,stat_bytes=2097152,input_bytes=25165824;
bool space(char c){return c==' '||c=='\t'||c=='\r'||c=='\n';}
std::string_view trim(std::string_view s){while(!s.empty()&&space(s.front()))s.remove_prefix(1);while(!s.empty()&&space(s.back()))s.remove_suffix(1);return s;}
bool number(std::string_view s,std::uint64_t& value,bool canonical=false){
    if(s.empty()||(canonical&&s.size()>1&&s.front()=='0'))return false;
    value=0;
    for(char c:s){if(c<'0'||c>'9'||value>(std::numeric_limits<std::uint64_t>::max()-static_cast<unsigned>(c-'0'))/10)return false;value=value*10+static_cast<unsigned>(c-'0');}
    return true;
}
bool index(std::string_view s,std::uint32_t& value){std::uint64_t n=0;if(!number(s,n,true)||n>2147483647)return false;value=static_cast<std::uint32_t>(n);return true;}
bool topology_id(std::string_view text,std::int32_t& value){text=trim(text);if(text=="-1"){value=-1;return true;}std::uint32_t n=0;if(!index(text,n))return false;value=static_cast<std::int32_t>(n);return true;}
bool add(std::uint64_t& value,std::uint64_t amount){if(amount>std::numeric_limits<std::uint64_t>::max()-value)return false;value+=amount;return true;}
std::vector<std::string_view> words(std::string_view s){
    std::vector<std::string_view> result;
    while(!(s=trim(s)).empty()){const auto at=s.find_first_of(" \t\r\n");result.push_back(s.substr(0,at));if(result.size()>11||at==s.npos)break;s.remove_prefix(at);}
    return result;
}
using Topology=std::map<std::uint32_t,LinuxProcessorRow>;
ProcessorReadCode topology(const std::vector<LinuxProcessorTopologyText>& texts,const std::vector<std::uint32_t>& ids,Topology& out){
    if(texts.size()!=ids.size())return ProcessorReadCode::malformed;
    for(const auto& text:texts){
        LinuxProcessorRow row{};row.index=text.index;
        if(!std::binary_search(ids.begin(),ids.end(),text.index)||!topology_id(text.package,row.package)||!topology_id(text.core,row.core))return ProcessorReadCode::malformed;
        const auto code=linux_processor_ids(text.peers,8192,row.peers);
        if(code!=ProcessorReadCode::success)return code;
        if(!std::binary_search(row.peers.begin(),row.peers.end(),text.index)||!out.emplace(text.index,std::move(row)).second)return ProcessorReadCode::malformed;
    }
    return ProcessorReadCode::success;
}
bool equal(const LinuxProcessorRow& a,const LinuxProcessorRow& b){return a.index==b.index&&a.package==b.package&&a.core==b.core&&a.peers==b.peers;}
}
ProcessorReadCode linux_processor_ids(std::string_view text,std::size_t limit,std::vector<std::uint32_t>& output){
    output.clear();
    if(!limit||limit>8192||text.size()>list_bytes)return ProcessorReadCode::capacity;
    try {
        std::vector<std::uint32_t> candidate;text=trim(text);
        if(text.empty())return ProcessorReadCode::malformed;
        while(!text.empty()){
            const auto comma=text.find(',');const auto token=text.substr(0,comma);const auto dash=token.find('-');std::uint32_t first=0,last=0;
            if(!index(token.substr(0,dash),first))return ProcessorReadCode::malformed;
            last=first;
            if(dash!=token.npos&&(!index(token.substr(dash+1),last)||last<first))return ProcessorReadCode::malformed;
            const auto count=static_cast<std::uint64_t>(last)-first+1;
            if(count>limit-candidate.size())return ProcessorReadCode::capacity;
            for(std::uint64_t i=first;i<=last;++i)candidate.push_back(static_cast<std::uint32_t>(i));
            if(comma==text.npos)break;
            text.remove_prefix(comma+1);if(text.empty())return ProcessorReadCode::malformed;
        }
        std::sort(candidate.begin(),candidate.end());
        if(std::adjacent_find(candidate.begin(),candidate.end())!=candidate.end())return ProcessorReadCode::malformed;
        output=std::move(candidate);return ProcessorReadCode::success;
    }catch(const std::bad_alloc&){return ProcessorReadCode::capacity;}
}
ProcessorReadCode linux_processor_error(int error){
    if(error==EACCES||error==EPERM)return ProcessorReadCode::denied;
    if(error==ENOENT||error==ENOSYS)return ProcessorReadCode::unsupported;
    if(error==ENOMEM)return ProcessorReadCode::capacity;
    if(error==EINTR)return ProcessorReadCode::interrupted;
    if(error==ETIMEDOUT)return ProcessorReadCode::timed_out;
    return ProcessorReadCode::failed;
}
LinuxProcessorCapture decode_linux_processors(const LinuxProcessorFiles& files,std::size_t limit){
    if(!limit||limit>8192||files.stat.size()>stat_bytes||files.online_before.size()>list_bytes||files.online_after.size()>list_bytes||files.topology_before.size()>limit||files.topology_after.size()>limit)return {ProcessorReadCode::capacity};
    std::size_t bytes=files.stat.size()+files.online_before.size()+files.online_after.size();
    for(const auto* texts:{&files.topology_before,&files.topology_after})for(const auto& t:*texts){
        if(t.package.size()>32||t.core.size()>32||t.peers.size()>list_bytes)return {ProcessorReadCode::capacity};
        bytes+=t.package.size()+t.core.size()+t.peers.size();if(bytes>input_bytes)return {ProcessorReadCode::capacity};
    }
    if(!files.ticks_per_second||files.stat.find('\0')!=files.stat.npos)return {ProcessorReadCode::malformed};
    try {
        std::vector<std::uint32_t> before,after;
        auto online_code=linux_processor_ids(files.online_before,limit,before);
        if(online_code!=ProcessorReadCode::success)return {online_code};
        online_code=linux_processor_ids(files.online_after,limit,after);
        if(online_code!=ProcessorReadCode::success)return {online_code};
        if(before!=after)return {ProcessorReadCode::interrupted};
        Topology first,second;
        auto code=topology(files.topology_before,before,first);if(code!=ProcessorReadCode::success)return {code};
        code=topology(files.topology_after,after,second);if(code!=ProcessorReadCode::success)return {code};
        for(const auto& item:first)if(!equal(item.second,second.at(item.first)))return {ProcessorReadCode::interrupted};
        std::map<std::uint32_t,bool> seen;bool aggregate=false;std::size_t shape=0;
        std::string_view remaining=files.stat;
        while(!remaining.empty()){
            const auto newline=remaining.find('\n');const auto line=trim(remaining.substr(0,newline));
            if(newline==remaining.npos)remaining={};else remaining.remove_prefix(newline+1);
            if(line.substr(0,3)!="cpu")continue;
            const auto tokens=words(line);if(tokens.empty())return {ProcessorReadCode::malformed};
            const auto count=tokens.size()-1;if(count>10)return {ProcessorReadCode::unsupported};
            if((count!=8&&count!=10)||(shape&&shape!=count))return {ProcessorReadCode::malformed};
            shape=count;
            std::array<std::uint64_t,10> counters{};
            for(std::size_t n=0;n<count;++n)if(!number(tokens[n+1],counters[n]))return {ProcessorReadCode::malformed};
            if(tokens.front()=="cpu"){if(aggregate)return {ProcessorReadCode::malformed};aggregate=true;continue;}
            std::uint32_t cpu=0;
            if(!index(tokens.front().substr(3),cpu)||!first.count(cpu)||!seen.emplace(cpu,true).second)return {ProcessorReadCode::malformed};
            auto& row=first.at(cpu);std::copy_n(counters.begin(),8,row.accounting.begin());
            std::uint64_t total=0;for(auto value:row.accounting)if(!add(total,value))return {ProcessorReadCode::capacity};
            if(count==10)row.guest=std::array<std::uint64_t,2>{counters[8],counters[9]};
        }
        if(!aggregate||seen.size()!=before.size())return {ProcessorReadCode::malformed};
        LinuxProcessorCapture result{ProcessorReadCode::success,0,files.ticks_per_second,{}};result.rows.reserve(first.size());
        for(auto& item:first)result.rows.push_back(std::move(item.second));
        return result;
    }catch(const std::bad_alloc&){return {ProcessorReadCode::capacity};}
}
ProcessorResult LinuxProcessorCapture::counters()const{
    if(code!=ProcessorReadCode::success)return {code,native_error};
    try {
        ProcessorResult result{ProcessorReadCode::success};result.rows.reserve(rows.size());
        for(const auto& row:rows){
            std::uint64_t total=0,nonexecution=0;
            for(auto value:row.accounting)if(!add(total,value))return {ProcessorReadCode::capacity};
            for(auto n:{3,4,7})if(!add(nonexecution,row.accounting[static_cast<std::size_t>(n)]))return {ProcessorReadCode::capacity};
            result.rows.push_back({"linux:cpu:"+std::to_string(row.index),"linux:online",total,nonexecution,{row.accounting.begin(),row.accounting.end()}});
        }
        return result;
    }catch(const std::bad_alloc&){return {ProcessorReadCode::capacity};}
}
bool same_linux_topology(const LinuxProcessorCapture& a,const LinuxProcessorCapture& b){
    if(a.code!=ProcessorReadCode::success||b.code!=ProcessorReadCode::success||a.rows.size()!=b.rows.size())return false;
    for(std::size_t n=0;n<a.rows.size();++n)if(!equal(a.rows[n],b.rows[n]))return false;
    return true;
}
}
