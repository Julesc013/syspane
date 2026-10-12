#include "network_controller_linux.hpp"
#include "profile_controller_linux.hpp"
#include <fstream>
#include <thread>
#include <unistd.h>
namespace c=syspane::configuration;
std::string read(const char* path){std::ifstream file(path);std::string value;std::getline(file,value);return value;}
int main(int argc,char** argv){
    if(argc==3&&std::string(argv[1])=="--network"){
        const auto parent=syspane::protocol::decimal(argv[2]);if(!parent||!*parent)return 2;
        namespace os=syspane::platform;
        std::function<os::WatchedNetworkResult(const os::NetworkRequest&)> acquisition;
        std::function<os::LinuxProcessorCapture(const os::ProcessorRequest&)> processor_acquisition=[](const os::ProcessorRequest& request){
            const auto mode=read("processor-mode");
            if(mode=="hold"){
                std::ofstream("processor-held")<<::getpid();
                while(read("processor-release")!="yes")std::this_thread::sleep_for(std::chrono::milliseconds(5));
            }
            auto capture=mode=="failure"?os::LinuxProcessorCapture{os::ProcessorReadCode::failed,5}:os::read_linux_processors(request);
            if(read("processor-record")=="yes"){
                syspane::protocol::Json value{{"code",static_cast<int>(capture.code)},{"hz",capture.ticks_per_second},{"rows",syspane::protocol::Json::array()}};
                for(const auto& row:capture.rows)value["rows"].push_back({{"index",row.index},{"package",row.package},{"core",row.core},{"peers",row.peers},{"accounting",row.accounting}});
                std::ofstream file("processor-captures.jsonl",std::ios::app);file<<value.dump()<<'\n';file.flush();
                if(!file)throw syspane::protocol::Error("fixture.processor_observer");
            }
            return capture;
        };
        const auto count_text=read("workload-rows");
        if(!count_text.empty()){
            const auto count=syspane::protocol::decimal(count_text);if(!count||(*count!=64&&*count!=65))return 2;
            acquisition=[count=*count,calls=std::make_shared<unsigned>(0)](const os::NetworkRequest& request){
                os::WatchedNetworkResult result{{os::NetworkCode::success},{},0,0,true};
                if(const auto stopped=os::network_stopped(request)){result.sample.code=*stopped;return result;}
                if(count>request.row_limit||++*calls>128){result.sample.code=os::NetworkCode::capacity;return result;}
                const auto round=syspane::protocol::decimal(read("workload-round"));
                if(!round||(*round!=1&&*round!=2)){result.sample.code=os::NetworkCode::malformed;return result;}
                for(std::uint64_t i=1;i<=count;++i)result.sample.rows.push_back({i,static_cast<std::uint32_t>(i),6,os::NetworkCounters{1000 * *round+i,2000 * *round+i}});
                if(const auto stopped=os::network_stopped(request)){result.sample.code=*stopped;result.sample.rows.clear();return result;}
                std::ofstream("workload-read")<<*calls<<' '<<*round<<' '<<count;
                return result;
            };
        }
        return syspane::application::run_network_controller(*parent,[]{
            c::Policy p;p.available=read("policy")!="deny"&&read("network-policy")!="deny";p.revision=7;
            if(read("processor-policy")=="deny")p.denied_capabilities.insert("collection.processor");
            if(read("processor-network-policy")=="deny")p.denied_capabilities.insert("collection.network");
            if(read("policy")=="allow")for(const char* channel:{"inspector","accessibility"})p.disclosure[{"console",channel}]={"operational"};
            return p;
        },[]{if(read("network-mode")=="hold"){
            std::ofstream("network-held")<<::getpid();
            while(read("network-release")!="yes")std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }},std::move(acquisition),std::move(processor_acquisition));
    }
    if(argc!=2)return 2;
    const auto parent=syspane::protocol::decimal(argv[1]);if(!parent||!*parent)return 2;
    return syspane::application::run_profile_controller(*parent,[]{
        c::Policy policy;policy.available=read("policy")=="allow";policy.revision=7;
        if(read("network")!="allow"||read("network-policy")=="deny")policy.denied_capabilities.insert("collection.network");
        if(read("reconcile")=="deny")policy.denied_capabilities.insert("result.reconcile");
        for(const char* channel:{"inspector","accessibility"})policy.disclosure[{"console",channel}]={"public","operational","sensitive"};
        const auto history=read("history");
        if(history=="allow"||history=="erase-denied")policy.disclosure[{"console","history"}]={"public","operational","sensitive"};
        if(history=="erase-denied")policy.denied_capabilities.insert("editor.recovery.erase");
        return policy;
    },[](const std::string& phase){
        if(phase!=read("phase"))return;
        std::ofstream("held")<<c::Json{{"pid",::getpid()},{"phase",phase}}.dump();
        while(read("release")!="yes")std::this_thread::sleep_for(std::chrono::milliseconds(5));
    });
}
