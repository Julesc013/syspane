#if defined(__linux__)
#include "network_watch.hpp"
#include "network_netlink.hpp"
#include <array>
#include <cerrno>
#include <fcntl.h>
#include <limits>
#include <linux/rtnetlink.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>

namespace syspane::platform {
namespace {
NetworkResult error(int code){return {code==EACCES||code==EPERM?NetworkCode::denied:code==ENOMEM?NetworkCode::capacity:
    code==ENOBUFS?NetworkCode::interrupted:code==EAFNOSUPPORT||code==EPROTONOSUPPORT?NetworkCode::unsupported:NetworkCode::failed,code};}
}
struct NetworkWatch::Impl {
    int fd=-1,ns=-1;std::uint32_t port=0,sequence=0;std::uint64_t revision=0;
    struct stat namespace_stat{};
    NetworkResult failure{NetworkCode::success};
    ~Impl(){close();}
    void close(){if(fd>=0)::close(fd);if(ns>=0)::close(ns);fd=-1;ns=-1;}
    bool same_namespace()const{struct stat now{};return ns>=0&&::stat("/proc/thread-self/ns/net",&now)==0&&
        now.st_dev==namespace_stat.st_dev&&now.st_ino==namespace_stat.st_ino;}
    void fail(NetworkResult result){failure=std::move(result);close();}
};
NetworkWatch::NetworkWatch():impl_(std::make_unique<Impl>()) {
    auto& state=*impl_;
    state.ns=::open("/proc/thread-self/ns/net",O_RDONLY|O_CLOEXEC);
    if(state.ns<0){state.fail(error(errno));return;}
    if(::fstat(state.ns,&state.namespace_stat)){state.fail(error(errno));return;}
    state.fd=::socket(AF_NETLINK,SOCK_RAW|SOCK_CLOEXEC|SOCK_NONBLOCK,NETLINK_ROUTE);
    if(state.fd<0){state.fail(error(errno));return;}
    sockaddr_nl local{};local.nl_family=AF_NETLINK;local.nl_groups=RTMGRP_LINK;
    if(::bind(state.fd,reinterpret_cast<sockaddr*>(&local),sizeof(local))){state.fail(error(errno));return;}
    socklen_t length=sizeof(local);
    if(::getsockname(state.fd,reinterpret_cast<sockaddr*>(&local),&length)){state.fail(error(errno));return;}
    if(length!=sizeof(local)||!local.nl_pid||local.nl_groups!=RTMGRP_LINK||!state.same_namespace()){
        state.fail({NetworkCode::malformed});return;}
    state.port=local.nl_pid;
}
NetworkWatch::~NetworkWatch()=default;
bool NetworkWatch::active()const{return impl_->fd>=0;}
WatchedNetworkResult NetworkWatch::read(const NetworkRequest& request) {
    auto& state=*impl_;WatchedNetworkResult result{{NetworkCode::success},{},state.revision,state.revision,active()};
    if(!active()){result.sample=state.failure;return result;}
    if(const auto code=network_stopped(request)){result.sample={*code};return result;}
    const auto fail=[&](NetworkResult failure){
        state.fail(failure);result.sample=std::move(failure);result.continuity=false;result.after=state.revision;
        return std::move(result); // The captured result needs an explicit move; failure must not copy/allocate its event buffer.
    };
    try {
        if(!state.same_namespace())return fail({NetworkCode::interrupted});
        if(state.sequence==std::numeric_limits<std::uint32_t>::max())return fail({NetworkCode::capacity});
        const auto sequence=++state.sequence;
        detail::LinkDump dump(sequence,state.port,request.row_limit);
        std::array<char,65536> buffer{};std::size_t datagrams=0,bytes=0;
        // Returns false only when the nonblocking socket has no queued datagram.
        const auto receive=[&](bool allow_replies)->bool {
            sockaddr_nl sender{};iovec io{buffer.data(),buffer.size()};msghdr message{};
            message.msg_name=&sender;message.msg_namelen=sizeof(sender);message.msg_iov=&io;message.msg_iovlen=1;
            const auto received=::recvmsg(state.fd,&message,0);
            if(received<0){if(errno==EAGAIN)return false;if(errno==EINTR)throw NetworkResult{NetworkCode::interrupted};throw error(errno);}
            if(message.msg_flags&(MSG_TRUNC|MSG_CTRUNC))throw NetworkResult{NetworkCode::capacity};
            if(message.msg_namelen!=sizeof(sender)||sender.nl_family!=AF_NETLINK||sender.nl_pid)throw NetworkResult{NetworkCode::malformed};
            if(++datagrams>128||static_cast<std::size_t>(received)>8388608-bytes)throw NetworkResult{NetworkCode::capacity};
            bytes+=static_cast<std::size_t>(received);
            auto split=detail::split_link_messages(std::string_view(buffer.data(),static_cast<std::size_t>(received)));
            if(split.code!=NetworkCode::success)throw NetworkResult{split.code};
            if(split.indications.size()>1024-result.indications.size())throw NetworkResult{NetworkCode::capacity};
            for(const auto& event:split.indications){
                if(state.revision==std::numeric_limits<std::uint64_t>::max())throw NetworkResult{NetworkCode::capacity};
                result.indications.push_back(event);++state.revision;
            }
            if(!split.replies.empty()){
                if(!allow_replies)throw NetworkResult{NetworkCode::malformed};
                dump.feed(split.replies);
            }
            return true;
        };
        const auto drain=[&]{while(receive(false)){if(const auto code=network_stopped(request))throw NetworkResult{*code};}};
        drain();result.before=state.revision;
        if(const auto code=network_stopped(request))return fail({*code});
        struct {nlmsghdr header;ifinfomsg link;} query{};
        query.header.nlmsg_len=sizeof(query);query.header.nlmsg_type=RTM_GETLINK;
        query.header.nlmsg_flags=NLM_F_REQUEST|NLM_F_DUMP;query.header.nlmsg_seq=sequence;query.header.nlmsg_pid=state.port;
        query.link.ifi_family=AF_UNSPEC;sockaddr_nl kernel{};kernel.nl_family=AF_NETLINK;
        const auto sent=::sendto(state.fd,&query,sizeof(query),0,reinterpret_cast<sockaddr*>(&kernel),sizeof(kernel));
        if(sent<0)return fail(error(errno));
        if(sent!=sizeof(query))return fail({NetworkCode::failed});
        while(!dump.terminal()){
            if(const auto code=network_stopped(request))return fail({*code});
            pollfd ready{state.fd,POLLIN,0};const auto polled=::poll(&ready,1,20);
            if(polled<0){if(errno==EINTR)continue;return fail(error(errno));}
            if(!polled)continue;
            if(ready.revents&(POLLERR|POLLHUP|POLLNVAL))return fail({NetworkCode::interrupted});
            receive(true);
        }
        result.sample=dump.finish();
        if(result.sample.code!=NetworkCode::success)return fail(result.sample);
        drain();result.after=state.revision;
        if(!state.same_namespace())return fail({NetworkCode::interrupted});
        if(const auto code=network_stopped(request))return fail({*code});
        if(result.before!=result.after)result.sample={NetworkCode::interrupted};
        return result;
    } catch(const NetworkResult& failure){return fail(failure);}
      catch(const std::bad_alloc&){return fail({NetworkCode::capacity});}
}
}
#endif
