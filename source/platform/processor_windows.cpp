#if defined(_WIN64)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <pdh.h>
#include <pdhmsg.h>
#include <winperf.h>
#include "processor_windows.hpp"
#include <array>
#include <cstddef>
#include <cstring>
#include <new>

namespace syspane::platform {
namespace {
static_assert(sizeof(void*)==8&&sizeof(GROUP_AFFINITY)==16&&sizeof(PROCESSOR_GROUP_INFO)==48,"Native x64 topology ABI required");
static_assert(offsetof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX,Processor.GroupMask)==32&&offsetof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX,Group.GroupInfo)==32,"Topology offsets differ from declared decoder");
static_assert(PERF_100NSEC_TIMER==0x20510500&&PDH_CSTATUS_VALID_DATA==0&&PDH_CSTATUS_NEW_DATA==1,"Declared PDH semantics differ");
struct Failure {ProcessorReadCode code;std::int64_t error=0;};
void check(const ProcessorRequest& request){const auto code=processor_stopped(request);if(code!=ProcessorReadCode::success)throw Failure{code};}
void failed(DWORD error){throw Failure{windows_processor_error(error),error};}
std::vector<unsigned char> topology_bytes(LOGICAL_PROCESSOR_RELATIONSHIP kind,const ProcessorRequest& request){
    check(request);DWORD size=0;const auto probe=::GetLogicalProcessorInformationEx(kind,nullptr,&size);const auto error=::GetLastError();check(request);
    if(probe||error!=ERROR_INSUFFICIENT_BUFFER)failed(probe?ERROR_INVALID_DATA:error);
    for(unsigned attempt=0;attempt<3;++attempt){
        if(!size||size>8388608)throw Failure{ProcessorReadCode::capacity};
        std::vector<unsigned char> bytes(size);DWORD actual=size;check(request);
        const auto ok=::GetLogicalProcessorInformationEx(kind,reinterpret_cast<PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX>(bytes.data()),&actual);const auto status=::GetLastError();check(request);
        if(ok){if(!actual||actual>bytes.size())throw Failure{ProcessorReadCode::malformed};bytes.resize(actual);return bytes;}
        if(status!=ERROR_INSUFFICIENT_BUFFER)failed(status);
        size=actual;
    }throw Failure{ProcessorReadCode::interrupted,ERROR_INSUFFICIENT_BUFFER};
}
WindowsTopology topology(const ProcessorRequest& request){
    auto groups=topology_bytes(RelationGroup,request);auto cores=topology_bytes(RelationProcessorCore,request);auto packages=topology_bytes(RelationProcessorPackage,request);
    auto value=decode_windows_topology(groups,cores,packages,request.row_limit);check(request);
    if(value.code!=ProcessorReadCode::success)throw Failure{value.code};
    return std::move(value.value);
}
struct Pdh {
    HMODULE module=nullptr;
    decltype(&PdhOpenQueryW) open=nullptr;decltype(&PdhCloseQuery) close=nullptr;
    decltype(&PdhAddEnglishCounterW) add=nullptr;decltype(&PdhCollectQueryData) collect=nullptr;
    decltype(&PdhGetRawCounterValue) raw=nullptr;
    template<class F> void symbol(F& function,const char* name,const ProcessorRequest& request){
        check(request);const auto address=::GetProcAddress(module,name);const auto error=::GetLastError();check(request);
        if(!address)failed(error?error:ERROR_PROC_NOT_FOUND);
        static_assert(sizeof(F)==sizeof(address),"Windows export ABI");std::memcpy(&function,&address,sizeof(function));
    }
    void load(const ProcessorRequest& request){
        std::array<wchar_t,32768> path{};check(request);const auto size=::GetSystemDirectoryW(path.data(),static_cast<UINT>(path.size()));const auto error=::GetLastError();check(request);
        if(!size)failed(error);
        if(size>=path.size()-9)throw Failure{ProcessorReadCode::capacity};
        const auto name=std::wstring(path.data(),size)+L"\\pdh.dll";
        check(request);module=::LoadLibraryExW(name.c_str(),nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);const auto status=::GetLastError();check(request);
        if(!module)failed(status);
        symbol(open,"PdhOpenQueryW",request);symbol(close,"PdhCloseQuery",request);symbol(add,"PdhAddEnglishCounterW",request);symbol(collect,"PdhCollectQueryData",request);symbol(raw,"PdhGetRawCounterValue",request);
    }
    ~Pdh(){if(module)::FreeLibrary(module);}
};
struct Query {const Pdh& pdh;PDH_HQUERY value=nullptr;~Query(){if(value)pdh.close(value);}DWORD finish(){const auto status=pdh.close(value);value=nullptr;return status;}};
}
WindowsProcessorCapture read_windows_processors(const ProcessorRequest& request){
    try{
        check(request);const auto before=topology(request);Pdh pdh;pdh.load(request);Query query{pdh};
        check(request);auto status=pdh.open(nullptr,0,&query.value);if(status)query.value=nullptr;check(request);if(status)failed(status);
        if(!query.value)throw Failure{ProcessorReadCode::malformed};
        struct Counter {std::uint16_t group;std::uint8_t number;std::array<PDH_HCOUNTER,3> values;};std::vector<Counter> counters;
        for(const auto& group:before.groups)for(unsigned number=0;number<64;++number)if(group.mask&(std::uint64_t{1}<<number)){
            Counter counter{group.number,static_cast<std::uint8_t>(number),{}};std::size_t index=0;
            for(const auto* name:{L"User Time",L"Privileged Time",L"Idle Time"}){
                const auto path=L"\\Processor Information("+std::to_wstring(group.number)+L","+std::to_wstring(number)+L")\\% "+name;
                check(request);status=pdh.add(query.value,path.c_str(),0,&counter.values[index]);check(request);if(status)failed(status);
                if(!counter.values[index])throw Failure{ProcessorReadCode::malformed};
                ++index;
            }
            counters.push_back(counter);
        }
        check(request);status=pdh.collect(query.value);check(request);if(status)failed(status);
        std::vector<WindowsProcessorRow> rows;rows.reserve(counters.size());
        for(const auto& counter:counters){
            WindowsProcessorRow row{counter.group,counter.number,{}};
            for(std::size_t n=0;n<3;++n){
                PDH_RAW_COUNTER value{};DWORD type=0;check(request);status=pdh.raw(counter.values[n],&type,&value);check(request);if(status)failed(status);
                const auto stamp=(static_cast<std::uint64_t>(value.TimeStamp.dwHighDateTime)<<32)|value.TimeStamp.dwLowDateTime;
                row.accounting[n]={0,value.CStatus,type,value.MultiCount,value.FirstValue,value.SecondValue,stamp};
            }
            rows.push_back(row);
        }
        check(request);status=query.finish();check(request);if(status)failed(status);
        const auto after=topology(request);auto result=decode_windows_processors(before,after,rows,request.row_limit);check(request);return result;
    }catch(const Failure& error){return {error.code,error.error};}catch(const std::bad_alloc&){return {ProcessorReadCode::capacity};}
}
}
#endif
