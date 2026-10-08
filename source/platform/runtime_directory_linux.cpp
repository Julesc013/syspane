#include "runtime_directory_linux.hpp"
#include "local_ipc.hpp"
#include "wire.hpp"
#include <array>
#include <cerrno>
#include <dirent.h>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/random.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

namespace syspane::platform {
namespace {
void need(bool value,const char* code){if(!value)throw protocol::Error(code);}
struct Fd {
    int value=-1;
    explicit Fd(int fd=-1):value(fd){}
    Fd(Fd&& other)noexcept:value(std::exchange(other.value,-1)){}
    Fd(const Fd&)=delete;Fd& operator=(const Fd&)=delete;
    ~Fd(){if(value>=0)::close(value);}
};
bool same(const struct stat& a,const struct stat& b){
    return a.st_dev==b.st_dev&&a.st_ino==b.st_ino&&a.st_uid==b.st_uid&&a.st_gid==b.st_gid&&a.st_mode==b.st_mode;
}
bool protected_directory(const struct stat& value){
    return S_ISDIR(value.st_mode)&&(value.st_uid==0||value.st_uid==::getuid())&&!(value.st_mode&07022);
}
bool private_directory(const struct stat& value){
    return S_ISDIR(value.st_mode)&&value.st_uid==::getuid()&&(value.st_mode&07777)==0700;
}
std::vector<std::string> components(const std::string& base){
    need(base.size()>1&&base.size()<=50&&base.front()=='/'&&base.back()!='/'&&base.find('\0')==std::string::npos,"runtime.path");
    std::vector<std::string> out;std::size_t start=1;
    while(start<base.size()){
        const auto end=base.find('/',start);const auto part=base.substr(start,end==std::string::npos?base.size()-start:end-start);
        need(!part.empty()&&part!="."&&part!=".."&&out.size()<32,"runtime.path");out.push_back(part);
        if(end==std::string::npos)break;
        start=end+1;
    }
    return out;
}
std::string nonce(){
    std::array<unsigned char,8> bytes{};std::size_t count=0;
    for(unsigned attempt=0;attempt<16&&count<bytes.size();++attempt){
        const auto got=::getrandom(bytes.data()+count,bytes.size()-count,GRND_NONBLOCK);
        if(got>0)count+=static_cast<std::size_t>(got);
        else need(got<0&&errno==EINTR,"runtime.random");
    }
    need(count==bytes.size(),"runtime.random");std::string text="sp-";constexpr char hex[]="0123456789abcdef";
    for(const auto b:bytes){text+=hex[b>>4];text+=hex[b&15];}return text;
}
void empty(int fd){
    Fd copy(::openat(fd,".",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));need(copy.value>=0,"runtime.read");
    DIR* raw=::fdopendir(copy.value);need(raw!=nullptr,"runtime.read");copy.value=-1;
    std::unique_ptr<DIR,int(*)(DIR*)> directory(raw,::closedir);unsigned count=0;
    for(;;){
        errno=0;const auto* entry=::readdir(raw);if(!entry){need(errno==0,"runtime.read");return;}
        need(++count<=3,"runtime.contents");const std::string name=entry->d_name;
        need(name=="."||name=="..","runtime.contents");
    }
}
}
struct LinuxRuntimeDirectory::Impl {
    struct Node {Fd fd;int parent;std::string name;struct stat identity;};
    std::vector<Node> nodes;std::string root,leaf;int base=-1;
    std::thread::id owner=std::this_thread::get_id();mutable bool invalid=false;bool closed=false;
    void thread()const{need(owner==std::this_thread::get_id(),"runtime.owner");}
    void usable()const{thread();need(!closed,"runtime.closed");need(!invalid,"runtime.invalidated");}
    void open(int parent,const std::string& name){
        Fd fd(parent<0?::open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC):
            ::openat(nodes[static_cast<std::size_t>(parent)].fd.value,name.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));
        struct stat value{};need(fd.value>=0&&::fstat(fd.value,&value)==0&&protected_directory(value),"runtime.path");
        nodes.push_back({std::move(fd),parent,name,value});
    }
    void verify()const{
        usable();
        try{
            for(const auto& n:nodes){
                struct stat held{},named{};
                need(::fstat(n.fd.value,&held)==0&&
                     (n.parent<0?::lstat("/",&named): ::fstatat(nodes[static_cast<std::size_t>(n.parent)].fd.value,n.name.c_str(),&named,AT_SYMLINK_NOFOLLOW))==0&&
                     same(n.identity,held)&&same(held,named)&&protected_directory(held),"runtime.changed");
            }
        }catch(...){invalid=true;throw;}
    }
};
LinuxRuntimeDirectory::LinuxRuntimeDirectory(std::string base):impl_(std::make_unique<Impl>()){
    const auto parts=components(base);auto& s=*impl_;need(unprivileged_context(),"runtime.context");s.open(-1,"/");
    for(const auto& part:parts)s.open(static_cast<int>(s.nodes.size()-1),part);
    s.base=static_cast<int>(s.nodes.size()-1);const auto& parent=s.nodes.back();struct statfs filesystem{};
    need(private_directory(parent.identity),"runtime.permissions");
    need(::fstatfs(parent.fd.value,&filesystem)==0&&(filesystem.f_type==0xEF53||filesystem.f_type==0x01021994),"runtime.filesystem");
    const int fd=parent.fd.value;bool made=false;
    for(unsigned attempt=0;attempt<8&&!made;++attempt){
        s.verify();s.leaf=nonce();
        if(::mkdirat(fd,s.leaf.c_str(),0700)==0)made=true;
        else need(errno==EEXIST,"runtime.create");
    }
    need(made,"runtime.collision");s.root=base+"/"+s.leaf;s.open(s.base,s.leaf);
    need(private_directory(s.nodes.back().identity),"runtime.permissions");s.verify();empty(s.nodes.back().fd.value);
}
LinuxRuntimeDirectory::~LinuxRuntimeDirectory()=default;
std::string LinuxRuntimeDirectory::path()const{impl_->verify();return impl_->root;}
void LinuxRuntimeDirectory::cleanup(){
    auto& s=*impl_;s.thread();if(s.closed)return;s.verify();
    Fd lock(::openat(s.nodes.back().fd.value,".",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));
    if(lock.value<0){s.invalid=true;throw protocol::Error("runtime.open");}
    if(::flock(lock.value,LOCK_EX|LOCK_NB)<0){
        if(errno==EWOULDBLOCK||errno==EAGAIN)throw protocol::Error("runtime.busy");
        s.invalid=true;throw protocol::Error("runtime.lock");
    }
    try{
        empty(lock.value);s.verify();struct stat held{};
        need(::fstat(lock.value,&held)==0&&same(held,s.nodes.back().identity),"runtime.changed");
        need(::unlinkat(s.nodes[static_cast<std::size_t>(s.base)].fd.value,s.leaf.c_str(),AT_REMOVEDIR)==0,"runtime.remove");
        s.closed=true;s.nodes.clear();
    }catch(...){s.invalid=true;throw;}
}
}
