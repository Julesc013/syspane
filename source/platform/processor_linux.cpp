#if defined(__linux__)
#include "processor_linux.hpp"
#include <array>
#include <cerrno>
#include <fcntl.h>
#include <new>
#include <unistd.h>

namespace syspane::platform {
namespace {
struct File {int fd;~File(){if(fd>=0)::close(fd);}};
struct Reader {
    const ProcessorRequest& request;
    ProcessorReadCode code=ProcessorReadCode::success;
    int error=0;std::size_t bytes=0;
    bool stopped(){const auto value=processor_stopped(request);if(value!=ProcessorReadCode::success){code=value;return true;}return false;}
    bool failure(int value){error=value;code=linux_processor_error(value);return false;}
    bool read(const std::string& path,std::size_t limit,std::string& text){
        if(stopped())return false;
        int fd=-1,saved=0;
        do {fd=::open(path.c_str(),O_RDONLY|O_CLOEXEC);saved=errno;if(stopped()){if(fd>=0)::close(fd);return false;}}while(fd<0&&saved==EINTR);
        if(fd<0)return failure(saved);
        File file{fd};std::array<char,4096> buffer{};
        for(;;){
            if(stopped())return false;
            const auto n=::read(file.fd,buffer.data(),buffer.size());const int saved=errno;
            if(stopped())return false;
            if(n<0){if(saved==EINTR)continue;return failure(saved);}
            if(!n)return true;
            const auto count=static_cast<std::size_t>(n);
            if(count>limit-text.size()||count>25165824-bytes){code=ProcessorReadCode::capacity;return false;}
            bytes+=count;text.append(buffer.data(),count);
        }
    }
    bool topology(const std::vector<std::uint32_t>& ids,std::vector<LinuxProcessorTopologyText>& out){
        out.reserve(ids.size());
        for(auto id:ids){
            LinuxProcessorTopologyText text{id,{},{},{}};
            const auto path="/sys/devices/system/cpu/cpu"+std::to_string(id)+"/topology/";
            if(!read(path+"physical_package_id",32,text.package)||!read(path+"core_id",32,text.core)||!read(path+"core_cpus_list",65536,text.peers))return false;
            out.push_back(std::move(text));
        }
        return true;
    }
};
}
LinuxProcessorCapture read_linux_processors(const ProcessorRequest& request){
    Reader reader{request};if(reader.stopped())return {reader.code};
    try {
        const auto hz=::sysconf(_SC_CLK_TCK);if(reader.stopped())return {reader.code};
        if(hz<=0)return {ProcessorReadCode::unsupported};
        LinuxProcessorFiles files{{},{},{},{},{},static_cast<std::uint64_t>(hz)};std::vector<std::uint32_t> ids;
        if(!reader.read("/sys/devices/system/cpu/online",65536,files.online_before))return {reader.code,reader.error};
        const auto code=linux_processor_ids(files.online_before,request.row_limit,ids);if(code!=ProcessorReadCode::success)return {code};
        if(!reader.topology(ids,files.topology_before)||!reader.read("/proc/stat",2097152,files.stat)||!reader.topology(ids,files.topology_after)||!reader.read("/sys/devices/system/cpu/online",65536,files.online_after))return {reader.code,reader.error};
        if(reader.stopped())return {reader.code};
        auto result=decode_linux_processors(files,request.row_limit);
        if(reader.stopped())return {reader.code};
        return result;
    }catch(const std::bad_alloc&){return {ProcessorReadCode::capacity};}
}
}
#endif
