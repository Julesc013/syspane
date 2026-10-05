#include "network.hpp"
#include "network_watch.hpp"
#include "local_ipc.hpp"
#include "wire.hpp"
#include <iostream>
#include <string>
#if defined(__linux__)
#include <thread>
#include <unistd.h>
#endif

namespace p=syspane::platform;
using syspane::protocol::Json;
Json encode(const p::NetworkResult& result){
    Json rows=Json::array();
    for(const auto& row:result.rows)rows.push_back({{"key",std::to_string(row.native_key)},
        {"index",row.index},{"native_type",row.native_type},
        {"receive",row.counters?Json(std::to_string(row.counters->receive)):Json(nullptr)},
        {"transmit",row.counters?Json(std::to_string(row.counters->transmit)):Json(nullptr)}});
    return {{"status",p::network_code_name(result.code)},{"native_error",result.native_error},{"rows",rows}};
}
#if defined(__linux__)
Json watched(){
    p::NetworkWatch watch;std::atomic_bool cancel{false};Json output{{"registered",watch.active()},{"calls",Json::array()}};
    std::cout<<Json{{"event","watch_ready"},{"pid",::getpid()},{"registered",watch.active()}}.dump()<<std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(750)); // Fixed external socket-observation window, before any dump.
    const auto acquire=[&]{auto value=watch.read({std::chrono::steady_clock::now()+std::chrono::seconds(2),cancel});
        auto row=encode(value.sample);row["before"]=std::to_string(value.before);row["after"]=std::to_string(value.after);
        row["continuity"]=value.continuity;row["indications"]=Json::array();
        for(const auto& event:value.indications)row["indications"].push_back({{"key",std::to_string(event.key)},{"removed",event.removed}});
        output["calls"].push_back(row);};
    acquire();cancel=true;
    output["cancelled"]=encode(watch.read({std::chrono::steady_clock::now()-std::chrono::seconds(1),cancel}).sample);
    output["active_after_cancel"]=watch.active();cancel=false;
    output["expired"]=encode(watch.read({std::chrono::steady_clock::now()-std::chrono::seconds(1),cancel}).sample);
    output["active_after_expiry"]=watch.active();acquire();output["event"]="watched_result";return output;
}
#endif
int main(int argc,char** argv) {
    if (argc!=2 || !p::unprivileged_context()) return 2;
    const std::string mode=argv[1];
#if defined(__linux__)
    if(mode=="watch"){std::cout<<watched().dump()<<std::endl;return 0;}
#endif
    if (mode!="read" && mode!="cancel" && mode!="deadline" && mode!="capacity") return 2;
    std::atomic_bool cancel{mode=="cancel"};
    const auto deadline=std::chrono::steady_clock::now()+std::chrono::milliseconds(mode=="cancel" || mode=="deadline" ? -1 : 2000);
    const auto result=p::read_network({deadline,cancel,mode=="capacity"?0U:8192U});
    std::cout<<encode(result).dump()<<std::endl;
    return 0;
}
