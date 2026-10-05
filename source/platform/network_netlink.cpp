#if defined(__linux__)
#include "network_netlink.hpp"
#include <algorithm>
#include <cerrno>
#include <cstring>
#include <linux/if_link.h>
#include <linux/rtnetlink.h>

namespace syspane::platform::detail {
namespace {
template<class T> T copied(const char* bytes) { T value{}; std::memcpy(&value,bytes,sizeof(value)); return value; }
std::size_t aligned(std::size_t n) { return (n+3)&~std::size_t(3); }
}
LinkMessages split_link_messages(std::string_view bytes) {
    const auto invalid=[](NetworkCode code=NetworkCode::malformed){LinkMessages r;r.code=code;return r;};
    if(bytes.empty()||bytes.size()>65536)return invalid(NetworkCode::capacity);
    LinkMessages result;std::size_t position=0;
    while(position<bytes.size()) {
        if(bytes.size()-position<sizeof(nlmsghdr))return invalid();
        const auto header=copied<nlmsghdr>(bytes.data()+position);
        if(header.nlmsg_len<sizeof(header)||header.nlmsg_len>bytes.size()-position)return invalid();
        const auto step=aligned(header.nlmsg_len);
        if(step>bytes.size()-position&&header.nlmsg_len!=bytes.size()-position)return invalid();
        const auto record=bytes.substr(position,std::min(step,bytes.size()-position));
        if(header.nlmsg_seq)result.replies.append(record);
        else {
            if(header.nlmsg_pid || header.nlmsg_flags&NLM_F_DUMP_INTR)return invalid();
            if(header.nlmsg_type!=RTM_NEWLINK&&header.nlmsg_type!=RTM_DELLINK)return invalid();
            const auto body=record.substr(sizeof(header),header.nlmsg_len-sizeof(header));
            if(body.size()<sizeof(ifinfomsg))return invalid();
            const auto link=copied<ifinfomsg>(body.data());if(link.ifi_index<=0)return invalid();
            auto offset=aligned(sizeof(link));
            while(offset<body.size()) {
                if(body.size()-offset<sizeof(rtattr))return invalid();
                const auto attribute=copied<rtattr>(body.data()+offset);
                if(attribute.rta_len<sizeof(attribute)||attribute.rta_len>body.size()-offset)return invalid();
                const auto advance=aligned(attribute.rta_len);
                if(advance>body.size()-offset&&attribute.rta_len!=body.size()-offset)return invalid();
                offset+=advance;
            }
            if(result.indications.size()>=1024)return invalid(NetworkCode::capacity);
            result.indications.push_back({static_cast<std::uint64_t>(link.ifi_index),header.nlmsg_type==RTM_DELLINK});
        }
        position+=step;
    }
    return result;
}
LinkDump::LinkDump(std::uint32_t sequence,std::uint32_t port,std::size_t limit):sequence_(sequence),port_(port),limit_(limit) {
    if (!sequence || !port || limit>8192) fail(NetworkCode::malformed);
}
void LinkDump::fail(NetworkCode code,std::int64_t native) { error_=NetworkResult{code,native}; rows_.clear(); }
void LinkDump::feed(std::string_view bytes) {
    if (error_) return;
    if (done_) { fail(NetworkCode::malformed); return; }
    if (bytes.empty() || bytes.size()>65536 || ++datagrams_>128 || bytes.size()>8388608-bytes_) { fail(NetworkCode::capacity); return; }
    bytes_+=bytes.size();
    std::size_t position=0;
    while (position<bytes.size()) {
        if (bytes.size()-position<sizeof(nlmsghdr)) { fail(NetworkCode::malformed); return; }
        const auto header=copied<nlmsghdr>(bytes.data()+position);
        if (header.nlmsg_len<sizeof(header) || header.nlmsg_len>bytes.size()-position ||
            header.nlmsg_seq!=sequence_ || header.nlmsg_pid!=port_ || done_) { fail(NetworkCode::malformed); return; }
        if (header.nlmsg_flags&NLM_F_DUMP_INTR) { fail(NetworkCode::interrupted); return; }
        const auto body=bytes.substr(position+sizeof(header),header.nlmsg_len-sizeof(header));
        if (header.nlmsg_type==NLMSG_OVERRUN) { fail(NetworkCode::interrupted); return; }
        if (header.nlmsg_type==NLMSG_ERROR || header.nlmsg_type==NLMSG_DONE) {
            if (body.size()<sizeof(std::int32_t)) { fail(NetworkCode::malformed); return; }
            const auto error=copied<std::int32_t>(body.data());
            if (error>0) { fail(NetworkCode::malformed); return; }
            if (error) {
                const auto native=-static_cast<std::int64_t>(error);
                fail(native==EACCES || native==EPERM ? NetworkCode::denied :
                    native==EOPNOTSUPP ? NetworkCode::unsupported : native==ENOMEM ? NetworkCode::capacity : NetworkCode::failed,native);
                return;
            }
            if (header.nlmsg_type==NLMSG_DONE) done_=true;
        } else if (header.nlmsg_type==RTM_NEWLINK) {
            if (!(header.nlmsg_flags&NLM_F_MULTI) || body.size()<sizeof(ifinfomsg)) { fail(NetworkCode::malformed); return; }
            const auto link=copied<ifinfomsg>(body.data());
            if (link.ifi_index<=0 || !indices_.insert(static_cast<std::uint32_t>(link.ifi_index)).second) { fail(NetworkCode::malformed); return; }
            if (rows_.size()>=limit_) { fail(NetworkCode::capacity); return; }
            NetworkRow row{static_cast<std::uint64_t>(link.ifi_index),static_cast<std::uint32_t>(link.ifi_index),link.ifi_type,{}};
            auto offset=aligned(sizeof(link));
            while (offset<body.size()) {
                if (body.size()-offset<sizeof(rtattr)) { fail(NetworkCode::malformed); return; }
                const auto attribute=copied<rtattr>(body.data()+offset);
                if (attribute.rta_len<sizeof(attribute) || attribute.rta_len>body.size()-offset) { fail(NetworkCode::malformed); return; }
                if (attribute.rta_type==IFLA_STATS64) {
                    // Stable prefix contains rx/tx packets then rx/tx bytes.
                    if (row.counters || attribute.rta_len-sizeof(attribute)<4*sizeof(std::uint64_t)) { fail(NetworkCode::malformed); return; }
                    const auto data=body.data()+offset+sizeof(attribute);
                    row.counters=NetworkCounters{copied<std::uint64_t>(data+16),copied<std::uint64_t>(data+24)};
                }
                const auto step=aligned(attribute.rta_len);
                if (step>body.size()-offset && attribute.rta_len!=body.size()-offset) { fail(NetworkCode::malformed); return; }
                offset+=step;
            }
            rows_.push_back(row);
        } else if (header.nlmsg_type!=NLMSG_NOOP) { fail(NetworkCode::malformed); return; }
        const auto step=aligned(header.nlmsg_len);
        if (step>bytes.size()-position && header.nlmsg_len!=bytes.size()-position) { fail(NetworkCode::malformed); return; }
        position+=step;
    }
}
NetworkResult LinkDump::finish() {
    if (error_) return *error_;
    if (!done_) return {NetworkCode::interrupted};
    std::sort(rows_.begin(),rows_.end(),[](const auto& a,const auto& b){return a.native_key<b.native_key;});
    return {NetworkCode::success,0,std::move(rows_)};
}
}
#endif
