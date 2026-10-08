#include "installation_linux.hpp"
#include "local_ipc.hpp"
#include "digest.hpp"
#include "wire.hpp"
#include <array>
#include <algorithm>
#include <cerrno>
#include <fcntl.h>
#include <linux/memfd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/vfs.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

namespace syspane::platform {
namespace p=protocol;
namespace {
void need(bool value,const char* code){if(!value)throw p::Error(code);}
struct Fd {
    int value=-1;
    explicit Fd(int fd=-1):value(fd){}
    Fd(Fd&& other)noexcept:value(std::exchange(other.value,-1)){}
    Fd(const Fd&)=delete;Fd& operator=(const Fd&)=delete;
    ~Fd(){if(value>=0)::close(value);}
};
bool identity(const struct stat& a,const struct stat& b){return a.st_dev==b.st_dev&&a.st_ino==b.st_ino&&a.st_uid==b.st_uid&&a.st_mode==b.st_mode;}
bool unchanged(const struct stat& a,const struct stat& b){
    return identity(a,b)&&a.st_size==b.st_size&&a.st_nlink==b.st_nlink&&a.st_mtim.tv_sec==b.st_mtim.tv_sec&&a.st_mtim.tv_nsec==b.st_mtim.tv_nsec&&
        a.st_ctim.tv_sec==b.st_ctim.tv_sec&&a.st_ctim.tv_nsec==b.st_ctim.tv_nsec;
}
bool protected_mode(const struct stat& value){return (value.st_uid==0||value.st_uid==::getuid())&&!(value.st_mode&07022);}
std::string current_executable(){
    std::array<char,513> bytes{};const auto n=::readlink("/proc/self/exe",bytes.data(),bytes.size());
    need(n>0&&n<=512,"installation.executable");return {bytes.data(),static_cast<std::size_t>(n)};
}
bool digest(const std::string& text){return text.size()==64&&text.find_first_not_of("0123456789abcdef")==std::string::npos;}
void native_filesystem(int fd){
    struct statfs filesystem{};
    need(::fstatfs(fd,&filesystem)==0&&(filesystem.f_type==0xEF53||filesystem.f_type==0x01021994),"installation.filesystem");
}
void executable_access(int fd){
    need(::syscall(SYS_faccessat2,fd,"",X_OK,AT_EMPTY_PATH|AT_EACCESS)==0,"installation.access");
}
}
struct LinuxInstallation::Impl {
    struct Node {Fd fd;int parent;std::string name;struct stat before;bool dir;};
    std::thread::id owner=std::this_thread::get_id();mutable bool invalid=false;
    std::vector<Node> nodes;std::string root,executable;Fd image;
    int prefix=-1,self=-1,helper=-1,record=-1;uid_t payload_owner=0;
    void check()const{need(owner==std::this_thread::get_id(),"installation.owner");need(!invalid,"installation.invalidated");}
    int open(int parent,const std::string& name,bool dir,bool payload){
        need(nodes.size()<64,"installation.depth");
        Fd fd(parent<0?::open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC):
            ::openat(nodes[static_cast<std::size_t>(parent)].fd.value,name.c_str(),O_RDONLY|O_CLOEXEC|O_NOFOLLOW|O_NONBLOCK|(dir?O_DIRECTORY:0)));
        struct stat value{};
        need(fd.value>=0&&::fstat(fd.value,&value)==0&&protected_mode(value)&&(dir?S_ISDIR(value.st_mode):(S_ISREG(value.st_mode)&&value.st_nlink==1)),"installation.path");
        need(!payload||value.st_uid==payload_owner,"installation.owner_mismatch");
        if(payload)native_filesystem(fd.value);
        const int index=static_cast<int>(nodes.size());nodes.push_back({std::move(fd),parent,name,value,dir});return index;
    }
    void verify()const{
        check();
        try{
            need(current_executable()==executable,"installation.executable_changed");
            for(std::size_t index=0;index<nodes.size();++index){
                const auto& node=nodes[index];
                struct stat held{},named{};
                need(::fstat(node.fd.value,&held)==0&&protected_mode(held)&&
                    (node.parent<0?::lstat("/",&named): ::fstatat(nodes[static_cast<std::size_t>(node.parent)].fd.value,node.name.c_str(),&named,AT_SYMLINK_NOFOLLOW))==0,
                    "installation.changed");
                need(node.dir?(identity(node.before,held)&&identity(held,named)):(unchanged(node.before,held)&&unchanged(held,named)),"installation.changed");
                if(static_cast<int>(index)>=prefix)native_filesystem(node.fd.value);
            }
            struct stat running{};need(::stat("/proc/self/exe",&running)==0&&unchanged(nodes[static_cast<std::size_t>(self)].before,running),"installation.executable_changed");
            executable_access(nodes[static_cast<std::size_t>(self)].fd.value);
            executable_access(nodes[static_cast<std::size_t>(helper)].fd.value);
        }catch(...){invalid=true;throw;}
    }
    std::string read(int index,std::size_t maximum,std::size_t exact=0){
        const auto& node=nodes[static_cast<std::size_t>(index)];
        need(node.before.st_size>0&&static_cast<std::uint64_t>(node.before.st_size)<=maximum&&(!exact||static_cast<std::uint64_t>(node.before.st_size)==exact),"installation.size");
        std::string bytes(static_cast<std::size_t>(node.before.st_size),'\0');std::size_t offset=0;unsigned interruptions=0;
        while(offset<bytes.size()){
            const auto n=::pread(node.fd.value,bytes.data()+offset,std::min(std::size_t{65536},bytes.size()-offset),static_cast<off_t>(offset));
            if(n<0){need(errno==EINTR&&++interruptions<=16,"installation.read");continue;}
            need(n>0,"installation.read");offset+=static_cast<std::size_t>(n);
        }
        struct stat after{};need(::fstat(node.fd.value,&after)==0&&unchanged(node.before,after),"installation.changed");return bytes;
    }
};
LinuxInstallation::LinuxInstallation(const HelperExpectation& expected):impl_(std::make_unique<Impl>()){
    auto& s=*impl_;need(unprivileged_context(),"installation.context");
    need(digest(expected.record_sha256)&&digest(expected.helper_sha256)&&expected.helper_bytes&&expected.helper_bytes<=67108864,"installation.expectation");
    s.executable=current_executable();const std::string suffix="/bin/syspane";
    need(s.executable.size()>suffix.size()&&s.executable.compare(s.executable.size()-suffix.size(),suffix.size(),suffix)==0,"installation.layout");
    s.root=s.executable.substr(0,s.executable.size()-suffix.size());need(s.root.front()=='/',"installation.layout");
    int at=s.open(-1,"/",true,false);
    for(std::size_t start=1;start<s.root.size();){
        const auto slash=s.root.find('/',start);const auto name=s.root.substr(start,slash==std::string::npos?std::string::npos:slash-start);
        need(!name.empty()&&name!="."&&name!=".."&&name.size()<=255,"installation.layout");at=s.open(at,name,true,false);
        if(slash==std::string::npos)break;
        start=slash+1;
    }
    s.prefix=at;s.payload_owner=s.nodes[static_cast<std::size_t>(at)].before.st_uid;struct statfs filesystem{};
    need(::fstatfs(s.nodes[static_cast<std::size_t>(at)].fd.value,&filesystem)==0&&(filesystem.f_type==0xEF53||filesystem.f_type==0x01021994),"installation.filesystem");
    const int bin=s.open(at,"bin",true,true);s.self=s.open(bin,"syspane",false,true);
    const int libexec=s.open(s.open(at,"libexec",true,true),"syspane",true,true);
    s.helper=s.open(libexec,"syspane-configuration-host",false,true);
    const int share=s.open(s.open(at,"share",true,true),"syspane",true,true);s.record=s.open(share,"helpers.json",false,true);
    need((s.nodes[static_cast<std::size_t>(s.self)].before.st_mode&0111)&&(s.nodes[static_cast<std::size_t>(s.helper)].before.st_mode&0111),"installation.executable_mode");
    s.verify();const auto record=s.read(s.record,65536);need(configuration::sha256(record)==expected.record_sha256,"installation.record_digest");
    const auto parsed=p::parse(record);
    need(p::members(parsed,{"format","schema_version","target_profile","product_version","configuration_host"})&&parsed["format"]=="SysPane.Helpers"&&
         parsed["schema_version"]=="0.1.0"&&parsed["target_profile"]=="linux-x64-gcc13"&&parsed["product_version"]=="0.0.1","installation.record");
    const auto& helper=parsed.at("configuration_host");
    need(p::members(helper,{"path","sha256","bytes","imports"})&&helper["path"]=="libexec/syspane/syspane-configuration-host"&&helper["sha256"]==expected.helper_sha256&&
         helper["bytes"]==std::to_string(expected.helper_bytes)&&helper["imports"]==p::Json::array({"libc.so.6","libgcc_s.so.1","libm.so.6","libstdc++.so.6"}),"installation.record");
    auto bytes=s.read(s.helper,67108864,expected.helper_bytes);
    need(bytes.size()>=4&&bytes.compare(0,4,"\x7f" "ELF")==0&&configuration::payload_sha256(bytes)==expected.helper_sha256,"installation.helper_digest");s.verify();
    s.image.value=::memfd_create("syspane-configuration-host",MFD_CLOEXEC|MFD_ALLOW_SEALING|MFD_EXEC);
    need(s.image.value>=3,"installation.memfd");std::size_t offset=0;unsigned interruptions=0;
    while(offset<bytes.size()){
        const auto n=::write(s.image.value,bytes.data()+offset,std::min(std::size_t{65536},bytes.size()-offset));
        if(n<0){need(errno==EINTR&&++interruptions<=16,"installation.copy");continue;}
        need(n>0,"installation.copy");offset+=static_cast<std::size_t>(n);
    }
    need(::fchmod(s.image.value,0500)==0,"installation.memfd_mode");
    constexpr int seals=F_SEAL_WRITE|F_SEAL_SHRINK|F_SEAL_GROW|F_SEAL_SEAL;
    need(::fcntl(s.image.value,F_ADD_SEALS,seals)==0&&(::fcntl(s.image.value,F_GET_SEALS)&seals)==seals,"installation.seals");
    std::string{}.swap(bytes);s.verify();
}
LinuxInstallation::~LinuxInstallation()=default;
int LinuxInstallation::verified_helper()const{impl_->verify();return impl_->image.value;}
const std::string& LinuxInstallation::root()const{impl_->check();return impl_->root;}
}
