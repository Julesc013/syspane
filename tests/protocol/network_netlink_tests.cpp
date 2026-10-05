#include "network_netlink.hpp"
#include <cstring>
#include <cerrno>
#include <iostream>
#include <limits>
#include <linux/if_link.h>
#include <linux/rtnetlink.h>
#include <stdexcept>
#include <string>
#include <vector>

namespace p=syspane::platform;
void check(bool value) { if(!value) throw std::runtime_error("fixed netlink expectation failed"); }
template<class T> std::string bytes(const T& value) { return {reinterpret_cast<const char*>(&value),sizeof(value)}; }
std::string message(unsigned type,std::string body,unsigned flags=NLM_F_MULTI,unsigned seq=7,unsigned port=19) {
    nlmsghdr header{}; header.nlmsg_len=static_cast<unsigned>(sizeof(header)+body.size());
    header.nlmsg_type=static_cast<unsigned short>(type); header.nlmsg_flags=static_cast<unsigned short>(flags);
    header.nlmsg_seq=seq; header.nlmsg_pid=port;
    auto result=bytes(header)+body; result.resize((result.size()+3)&~std::size_t(3),'\0'); return result;
}
std::string attribute(unsigned type,std::string payload) {
    rtattr attr{}; attr.rta_type=static_cast<unsigned short>(type); attr.rta_len=static_cast<unsigned short>(sizeof(attr)+payload.size());
    auto result=bytes(attr)+payload; result.resize((result.size()+3)&~std::size_t(3),'\0'); return result;
}
std::string stats() { const std::uint64_t value[4]={17,23,std::numeric_limits<std::uint64_t>::max(),0}; return attribute(IFLA_STATS64,bytes(value)); }
std::string link(int index,bool with_stats=true) {
    ifinfomsg info{}; info.ifi_index=index; info.ifi_type=772;
    return bytes(info)+attribute(IFLA_IFNAME,"private-fixture")+(with_stats?stats():"");
}
std::string done(unsigned flags=NLM_F_MULTI) { return message(NLMSG_DONE,bytes(std::int32_t(0)),flags); }
void valid() {
    p::detail::LinkDump dump(7,19,2);
    dump.feed(message(RTM_NEWLINK,link(2))+message(RTM_NEWLINK,link(1,false)));
    check(!dump.terminal()); dump.feed(done()); check(dump.terminal());
    const auto result=dump.finish(); check(result.code==p::NetworkCode::success && result.rows.size()==2);
    check(result.rows[0].native_key==1 && result.rows[0].index==1 && result.rows[0].native_type==772 && !result.rows[0].counters);
    check(result.rows[1].native_key==2 && result.rows[1].counters && result.rows[1].counters->receive==std::numeric_limits<std::uint64_t>::max() && result.rows[1].counters->transmit==0);
}
void rejected() {
    const auto good=message(RTM_NEWLINK,link(1));
    auto length=good; nlmsghdr invalid{}; invalid.nlmsg_len=3; std::memcpy(length.data(),&invalid,sizeof(invalid));
    auto malformed_attr=link(1,false); rtattr attr{}; attr.rta_len=2; malformed_attr+=bytes(attr);
    std::vector<std::pair<std::string,p::NetworkCode>> variants{
        {good.substr(0,good.size()-1),p::NetworkCode::malformed},
        {length,p::NetworkCode::malformed},
        {good+good,p::NetworkCode::malformed},
        {message(RTM_NEWLINK,link(1)+stats()),p::NetworkCode::malformed},
        {message(RTM_NEWLINK,malformed_attr),p::NetworkCode::malformed},
        {message(RTM_NEWLINK,link(1),NLM_F_MULTI,8),p::NetworkCode::malformed},
        {message(RTM_NEWLINK,link(1),NLM_F_MULTI,7,20),p::NetworkCode::malformed},
        {message(NLMSG_ERROR,bytes(std::int32_t(-5))),p::NetworkCode::failed},
        {message(NLMSG_ERROR,bytes(std::int32_t(-EACCES))),p::NetworkCode::denied},
        {message(NLMSG_ERROR,bytes(std::int32_t(-EOPNOTSUPP))),p::NetworkCode::unsupported},
        {message(NLMSG_ERROR,bytes(std::int32_t(5))),p::NetworkCode::malformed},
        {message(NLMSG_OVERRUN,""),p::NetworkCode::interrupted},
        {good+done(NLM_F_MULTI|NLM_F_DUMP_INTR),p::NetworkCode::interrupted},
        {message(RTM_NEWLINK,link(1),NLM_F_MULTI|NLM_F_DUMP_INTR),p::NetworkCode::interrupted},
        {good,p::NetworkCode::interrupted},
        {good+done()+good,p::NetworkCode::malformed},
        {message(RTM_NEWLINK,link(1,false)+attribute(IFLA_STATS64,"short")),p::NetworkCode::malformed}
    };
    for(const auto& variant:variants) { p::detail::LinkDump dump(7,19,2); dump.feed(variant.first); auto r=dump.finish(); check(r.code==variant.second && r.rows.empty()); }
    p::detail::LinkDump bounded(7,19,1); bounded.feed(good+message(RTM_NEWLINK,link(2))+done());
    check(bounded.finish().code==p::NetworkCode::capacity && bounded.finish().rows.empty());
    p::detail::LinkDump too_big(7,19,2); too_big.feed(std::string(65537,'x')); check(too_big.finish().code==p::NetworkCode::capacity);
    p::detail::LinkDump count(7,19,2); for(unsigned i=0;i<129;++i)count.feed(message(NLMSG_NOOP,"")); check(count.finish().code==p::NetworkCode::capacity);
}
void watch_decode(){
    const auto update=message(RTM_NEWLINK,link(4,false),0,0,0);
    const auto remove=message(RTM_DELLINK,link(7,false),0,0,0);
    const auto reply=message(RTM_NEWLINK,link(4));
    const auto split=p::detail::split_link_messages(update+reply+remove+done());
    check(split.code==p::NetworkCode::success&&split.replies==reply+done()&&split.indications.size()==2);
    check(split.indications[0].key==4&&!split.indications[0].removed&&split.indications[1].key==7&&split.indications[1].removed);
    p::detail::LinkDump dump(7,19,2);dump.feed(split.replies);check(dump.finish().code==p::NetworkCode::success);
    for(const auto& malformed:std::vector<std::string>{update.substr(0,update.size()-1),message(RTM_NEWLINK,link(4),0,0,9),
        message(RTM_NEWLINK,"bad",0,0,0),message(NLMSG_OVERRUN,"",0,0,0),message(RTM_NEWLINK,link(0),0,0,0)}){
        const auto result=p::detail::split_link_messages(malformed);check(result.code!=p::NetworkCode::success&&result.indications.empty()&&result.replies.empty());}
}
int main(int argc,char** argv) {
    try { check(argc==2); const std::string mode=argv[1]; if(mode=="NETWORK-NETLINK")valid(); else if(mode=="NETWORK-NETLINK-REJECT")rejected(); else if(mode=="NETWORK-WATCH-DECODE")watch_decode(); else return 2;
        std::cout<<mode<<": pass\n"; return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
