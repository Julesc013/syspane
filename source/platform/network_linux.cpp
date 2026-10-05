#if defined(__linux__)
#include "network_netlink.hpp"
#include <array>
#include <cerrno>
#include <linux/rtnetlink.h>
#include <new>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

namespace syspane::platform {
namespace {
struct Socket { int fd=-1; ~Socket(){if(fd>=0) ::close(fd);} };
NetworkResult failure(int error) {
    return {error==EACCES || error==EPERM ? NetworkCode::denied :
        error==EAFNOSUPPORT || error==EPROTONOSUPPORT || error==EOPNOTSUPP ? NetworkCode::unsupported :
        error==ENOMEM ? NetworkCode::capacity : error==ENOBUFS ? NetworkCode::interrupted : NetworkCode::failed,error};
}
}
NetworkResult read_network(const NetworkRequest& request) {
    if (const auto code=network_stopped(request)) return {*code};
    try {
        Socket socket{::socket(AF_NETLINK,SOCK_RAW|SOCK_CLOEXEC|SOCK_NONBLOCK,NETLINK_ROUTE)};
        if (socket.fd<0) return failure(errno);
        sockaddr_nl local{}; local.nl_family=AF_NETLINK;
        if (::bind(socket.fd,reinterpret_cast<sockaddr*>(&local),sizeof(local))) return failure(errno);
        socklen_t length=sizeof(local);
        if (::getsockname(socket.fd,reinterpret_cast<sockaddr*>(&local),&length)) return failure(errno);
        if (length!=sizeof(local) || !local.nl_pid) return {NetworkCode::malformed};
        struct { nlmsghdr header; ifinfomsg link; } query{};
        query.header.nlmsg_len=sizeof(query); query.header.nlmsg_type=RTM_GETLINK;
        query.header.nlmsg_flags=NLM_F_REQUEST|NLM_F_DUMP; query.header.nlmsg_seq=1;
        query.header.nlmsg_pid=local.nl_pid; query.link.ifi_family=AF_UNSPEC;
        sockaddr_nl kernel{}; kernel.nl_family=AF_NETLINK;
        if (const auto code=network_stopped(request)) return {*code};
        const auto sent=::sendto(socket.fd,&query,sizeof(query),0,reinterpret_cast<sockaddr*>(&kernel),sizeof(kernel));
        if (sent<0) return failure(errno);
        if (sent!=sizeof(query)) return {NetworkCode::failed};
        detail::LinkDump dump(1,local.nl_pid,request.row_limit);
        std::array<char,65536> buffer{};
        while (!dump.terminal()) {
            if (const auto code=network_stopped(request)) return {*code};
            pollfd ready{socket.fd,POLLIN,0};
            const auto polled=::poll(&ready,1,20);
            if (polled<0) { if(errno==EINTR) continue; return failure(errno); }
            if (!polled) continue;
            if (ready.revents&(POLLERR|POLLHUP|POLLNVAL)) return {NetworkCode::interrupted};
            sockaddr_nl sender{}; iovec io{buffer.data(),buffer.size()};
            msghdr message{}; message.msg_name=&sender; message.msg_namelen=sizeof(sender);
            message.msg_iov=&io; message.msg_iovlen=1;
            const auto received=::recvmsg(socket.fd,&message,0);
            if (received<0) { if(errno==EINTR || errno==EAGAIN) continue; return failure(errno); }
            if (message.msg_flags&(MSG_TRUNC|MSG_CTRUNC)) return {NetworkCode::capacity};
            if (message.msg_namelen!=sizeof(sender) || sender.nl_family!=AF_NETLINK || sender.nl_pid || sender.nl_groups)
                return {NetworkCode::malformed};
            dump.feed(std::string_view(buffer.data(),static_cast<std::size_t>(received)));
        }
        if (const auto code=network_stopped(request)) return {*code};
        return dump.finish();
    } catch (const std::bad_alloc&) { return {NetworkCode::capacity}; }
}
}
#endif
