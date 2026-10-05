#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <iphlpapi.h>
#include "network.hpp"
#include <algorithm>
#include <memory>
#include <new>
#include <set>

namespace syspane::platform {
NetworkResult read_network(const NetworkRequest& request) {
    if (const auto code=network_stopped(request)) return {*code};
    try {
        MIB_IF_TABLE2* raw=nullptr;
        const auto error=GetIfTable2(&raw);
        const std::unique_ptr<MIB_IF_TABLE2,decltype(&FreeMibTable)> table(raw,&FreeMibTable);
        if (const auto code=network_stopped(request)) return {*code};
        if (error) return {error==ERROR_ACCESS_DENIED ? NetworkCode::denied :
            error==ERROR_NOT_SUPPORTED ? NetworkCode::unsupported :
            error==ERROR_NOT_ENOUGH_MEMORY ? NetworkCode::capacity : NetworkCode::failed,error};
        if (!table) return {NetworkCode::malformed};
        if (table->NumEntries>request.row_limit) return {NetworkCode::capacity};
        NetworkResult result{NetworkCode::success};
        std::set<std::uint64_t> keys;
        std::set<std::uint32_t> indices;
        for (ULONG i=0;i<table->NumEntries;++i) {
            if (const auto code=network_stopped(request)) return {*code};
            const auto& row=table->Table[i];
            if (!row.InterfaceLuid.Value || !row.InterfaceIndex || !keys.insert(row.InterfaceLuid.Value).second ||
                !indices.insert(row.InterfaceIndex).second) return {NetworkCode::malformed};
            result.rows.push_back({row.InterfaceLuid.Value,row.InterfaceIndex,row.Type,
                NetworkCounters{row.InOctets,row.OutOctets}});
        }
        std::sort(result.rows.begin(),result.rows.end(),[](const auto& a,const auto& b){return a.native_key<b.native_key;});
        if (const auto code=network_stopped(request)) return {*code};
        return result;
    } catch (const std::bad_alloc&) { return {NetworkCode::capacity}; }
}
}
#endif
