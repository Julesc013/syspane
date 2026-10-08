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
const std::array<const char*,3> helper_names={"syspane-configuration-host","syspane-image-worker","syspane-recovery-worker"};
const std::array<const char*,3> helper_keys={"configuration_host","image_worker","recovery_worker"};
p::Json helper_imports(std::size_t index){
    if(index==1)return p::Json::array({"libc.so.6","libgcc_s.so.1","libgdk_pixbuf-2.0.so.0","libglib-2.0.so.0","libgobject-2.0.so.0","libstdc++.so.6"});
    return p::Json::array({"libc.so.6","libgcc_s.so.1","libm.so.6","libstdc++.so.6"});
}
}
struct LinuxInstallation::Impl {
    struct Node {Fd fd;int parent;std::string name;struct stat before;bool dir;};
    struct Helper {int node;Fd image;};
    std::thread::id owner=std::this_thread::get_id();mutable bool invalid=false;
    std::vector<Node> nodes;std::vector<Helper> helpers;std::string root,executable;
    int prefix=-1,self=-1,record=-1;uid_t payload_owner=0;
    void initialize(const std::string&,const std::vector<HelperImageExpectation>&,bool);
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
            for(const auto& helper:helpers)executable_access(nodes[static_cast<std::size_t>(helper.node)].fd.value);
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
void LinuxInstallation::Impl::initialize(const std::string& record_digest,const std::vector<HelperImageExpectation>& expected,bool bundle){
    auto& s=*this;need(unprivileged_context(),"installation.context");
    need(digest(record_digest)&&expected.size()==(bundle?3:1),"installation.expectation");
    for(const auto& helper:expected)need(digest(helper.sha256)&&helper.bytes&&helper.bytes<=67108864,"installation.expectation");
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
    for(std::size_t index=0;index<expected.size();++index)s.helpers.push_back({s.open(libexec,helper_names[index],false,true),Fd{}});
    const int share=s.open(s.open(at,"share",true,true),"syspane",true,true);s.record=s.open(share,"helpers.json",false,true);
    need(s.nodes[static_cast<std::size_t>(s.self)].before.st_mode&0111,"installation.executable_mode");
    for(const auto& helper:s.helpers)need(s.nodes[static_cast<std::size_t>(helper.node)].before.st_mode&0111,"installation.executable_mode");
    s.verify();const auto record=s.read(s.record,65536);need(configuration::sha256(record)==record_digest,"installation.record_digest");
    const auto parsed=p::parse(record);
    need((bundle?p::members(parsed,{"format","schema_version","target_profile","product_version","helpers"}):
                 p::members(parsed,{"format","schema_version","target_profile","product_version","configuration_host"}))&&parsed["format"]=="SysPane.Helpers"&&
         parsed["schema_version"]==(bundle?"0.2.0":"0.1.0")&&parsed["target_profile"]=="linux-x64-gcc13"&&parsed["product_version"]=="0.0.1","installation.record");
    if(bundle)need(p::members(parsed.at("helpers"),{"configuration_host","image_worker","recovery_worker"}),"installation.record");
    for(std::size_t index=0;index<expected.size();++index){
        const auto& helper=bundle?parsed.at("helpers").at(helper_keys[index]):parsed.at("configuration_host");
        need(p::members(helper,{"path","sha256","bytes","imports"})&&helper["path"]==std::string("libexec/syspane/")+helper_names[index]&&helper["sha256"]==expected[index].sha256&&
             helper["bytes"]==std::to_string(expected[index].bytes)&&helper["imports"]==helper_imports(index),"installation.record");
        auto bytes=s.read(s.helpers[index].node,67108864,expected[index].bytes);
        need(bytes.size()>=4&&bytes.compare(0,4,"\x7f" "ELF")==0&&configuration::payload_sha256(bytes)==expected[index].sha256,"installation.helper_digest");s.verify();
        auto& image=s.helpers[index].image;
        image.value=::memfd_create(helper_names[index],MFD_CLOEXEC|MFD_ALLOW_SEALING|MFD_EXEC);
        need(image.value>=3,"installation.memfd");std::size_t offset=0;unsigned interruptions=0;
        while(offset<bytes.size()){
            const auto n=::write(image.value,bytes.data()+offset,std::min(std::size_t{65536},bytes.size()-offset));
            if(n<0){need(errno==EINTR&&++interruptions<=16,"installation.copy");continue;}
            need(n>0,"installation.copy");offset+=static_cast<std::size_t>(n);
        }
        need(::fchmod(image.value,0500)==0,"installation.memfd_mode");
        constexpr int seals=F_SEAL_WRITE|F_SEAL_SHRINK|F_SEAL_GROW|F_SEAL_SEAL;
        need(::fcntl(image.value,F_ADD_SEALS,seals)==0&&(::fcntl(image.value,F_GET_SEALS)&seals)==seals,"installation.seals");
        std::string{}.swap(bytes);s.verify();
    }
}
LinuxInstallation::LinuxInstallation(const HelperExpectation& expected):impl_(std::make_unique<Impl>()){
    impl_->initialize(expected.record_sha256,{{expected.helper_sha256,expected.helper_bytes}},false);
}
LinuxInstallation::LinuxInstallation(const HelperBundleExpectation& expected):impl_(std::make_unique<Impl>()){
    impl_->initialize(expected.record_sha256,{expected.helpers.begin(),expected.helpers.end()},true);
}
LinuxInstallation::~LinuxInstallation()=default;
int LinuxInstallation::verified_helper()const{return verified_helper(HelperKind::configuration);}
int LinuxInstallation::verified_helper(HelperKind kind)const{
    impl_->check();const auto index=static_cast<std::size_t>(kind);need(index<impl_->helpers.size(),"installation.helper_role");
    impl_->verify();return impl_->helpers[index].image.value;
}
const std::string& LinuxInstallation::root()const{impl_->check();return impl_->root;}
}
