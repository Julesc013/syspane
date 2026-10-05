#pragma once
#if defined(__linux__)
#include "network.hpp"
#include <set>
#include <string_view>

namespace syspane::platform::detail {
// Private native decoder. No candidate escapes before successful DONE.
class LinkDump {
public:
    LinkDump(std::uint32_t sequence,std::uint32_t port,std::size_t limit);
    void feed(std::string_view datagram);
    bool terminal() const { return done_ || error_.has_value(); }
    NetworkResult finish();
private:
    void fail(NetworkCode code,std::int64_t native=0);
    std::uint32_t sequence_,port_;
    std::size_t limit_,bytes_=0,datagrams_=0;
    std::vector<NetworkRow> rows_;
    std::set<std::uint32_t> indices_;
    std::optional<NetworkResult> error_;
    bool done_=false;
};
}
#endif
