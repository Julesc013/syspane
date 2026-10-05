#include "network.hpp"
#include "local_ipc.hpp"
#include "wire.hpp"
#include <iostream>
#include <string>

int main(int argc,char** argv) {
    namespace p=syspane::platform;
    using syspane::protocol::Json;
    if (argc!=2 || !p::unprivileged_context()) return 2;
    const std::string mode=argv[1];
    if (mode!="read" && mode!="cancel" && mode!="deadline" && mode!="capacity") return 2;
    std::atomic_bool cancel{mode=="cancel"};
    const auto deadline=std::chrono::steady_clock::now()+std::chrono::milliseconds(mode=="cancel" || mode=="deadline" ? -1 : 2000);
    const auto result=p::read_network({deadline,cancel,mode=="capacity"?0U:8192U});
    Json rows=Json::array();
    for (const auto& row:result.rows) rows.push_back({{"key",std::to_string(row.native_key)},
        {"index",row.index},{"native_type",row.native_type},
        {"receive",row.counters?Json(std::to_string(row.counters->receive)):Json(nullptr)},
        {"transmit",row.counters?Json(std::to_string(row.counters->transmit)):Json(nullptr)}});
    std::cout<<Json{{"status",p::network_code_name(result.code)},{"native_error",result.native_error},{"rows",rows}}.dump()<<std::endl;
    return 0;
}
