#include "recovery_store_linux.hpp"
#include "digest.hpp"
#include <array>
#include <cerrno>
#include <dirent.h>
#include <fcntl.h>
#include <limits>
#include <sys/file.h>
#include <sys/random.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <thread>
#include <unistd.h>

namespace syspane::platform {
namespace {
using protocol::Error;using configuration::Publication;
void need(bool ok,const char* code){if(!ok)throw Error(code);}
struct File {
    int fd=-1;
    explicit File(int n=-1):fd(n){}
    ~File(){if(fd>=0)::close(fd);}
    File(const File&)=delete;File& operator=(const File&)=delete;
    File(File&& other)noexcept:fd(other.fd){other.fd=-1;}
    File& operator=(File&& other)noexcept{if(this!=&other){if(fd>=0)::close(fd);fd=other.fd;other.fd=-1;}return *this;}
};
bool same_node(const struct stat& a,const struct stat& b){return a.st_dev==b.st_dev&&a.st_ino==b.st_ino;}
bool same_file(const struct stat& a,const struct stat& b){
    return same_node(a,b)&&a.st_size==b.st_size&&a.st_uid==b.st_uid&&a.st_gid==b.st_gid&&a.st_mode==b.st_mode&&a.st_nlink==b.st_nlink&&
        a.st_mtim.tv_sec==b.st_mtim.tv_sec&&a.st_mtim.tv_nsec==b.st_mtim.tv_nsec&&a.st_ctim.tv_sec==b.st_ctim.tv_sec&&a.st_ctim.tv_nsec==b.st_ctim.tv_nsec;
}
struct stat private_node(int fd,bool directory,std::size_t limit=LinuxRecoveryStore::maximum_bytes){
    struct stat s{};need(fd>=0&&::fstat(fd,&s)==0,"recovery_store.open");
    need(s.st_uid==::geteuid()&&(s.st_mode&07777)==(directory?0700:0600),"recovery_store.permissions");
    need(directory?S_ISDIR(s.st_mode):(S_ISREG(s.st_mode)&&s.st_nlink==1&&s.st_size>=0&&static_cast<std::uint64_t>(s.st_size)<=limit),"recovery_store.type");return s;
}
void flush(int fd){unsigned retries=0;for(;;){if(::fsync(fd)==0)return;need(errno==EINTR&&++retries<=16,"recovery_store.flush");}}
File root_directory(const std::string& path){
    need(path.size()>1&&path.size()<=4096&&path.front()=='/'&&path.back()!='/'&&path.find('\0')==std::string::npos,"recovery_store.path");
    File dir(::open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC));need(dir.fd>=0,"recovery_store.path");std::size_t begin=1;
    while(begin<path.size()){
        const auto end=path.find('/',begin);const auto part=path.substr(begin,end==std::string::npos?path.size()-begin:end-begin);
        need(!part.empty()&&part!="."&&part!="..","recovery_store.path");
        File next(::openat(dir.fd,part.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));need(next.fd>=0,"recovery_store.path");dir=std::move(next);
        if(end==std::string::npos)break;
        begin=end+1;
    }
    private_node(dir.fd,true);struct statfs fs{};need(::fstatfs(dir.fd,&fs)==0&&fs.f_type==0xef53,"recovery_store.filesystem");return dir;
}
void layout(int fd){
    File copy(::openat(fd,".",O_RDONLY|O_DIRECTORY|O_CLOEXEC));need(copy.fd>=0,"recovery_store.layout");
    DIR* raw=::fdopendir(copy.fd);need(raw!=nullptr,"recovery_store.layout");copy.fd=-1;
    std::unique_ptr<DIR,int(*)(DIR*)> list(raw,::closedir);std::size_t count=0;
    for(;;){errno=0;const auto* entry=::readdir(list.get());if(!entry){need(errno==0,"recovery_store.layout");break;}
        const std::string name=entry->d_name;if(name=="."||name=="..")continue;
        need(++count<=3&&(name==".writer"||name=="draft.json"||name==".pending"),"recovery_store.layout");
    }
}
struct Node {File file;struct stat info{};std::string bytes;};
void bound_name(int parent,const char* name,const struct stat& info){
    struct stat current{};need(::fstatat(parent,name,&current,AT_SYMLINK_NOFOLLOW)==0&&same_file(current,info),"recovery_store.external_change");
}
std::optional<Node> read_node(int parent,const char* name){
    File file(::openat(parent,name,O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK));
    if(file.fd<0&&errno==ENOENT)return {};
    const auto before=private_node(file.fd,false);std::string bytes;bytes.reserve(static_cast<std::size_t>(before.st_size));std::array<char,4096> buffer{};unsigned retries=0;
    for(;;){const auto n=::read(file.fd,buffer.data(),buffer.size());if(n<0&&errno==EINTR&&++retries<=16)continue;
        need(n>=0,"recovery_store.read");if(!n)break;
        need(bytes.size()+static_cast<std::size_t>(n)<=LinuxRecoveryStore::maximum_bytes,"recovery_store.size");bytes.append(buffer.data(),static_cast<std::size_t>(n));}
    const auto after=private_node(file.fd,false);need(same_file(before,after)&&bytes.size()==static_cast<std::size_t>(after.st_size),"recovery_store.external_change");
    bound_name(parent,name,after);return Node{std::move(file),after,std::move(bytes)};
}
void write_bytes(int fd,std::string_view bytes){
    unsigned retries=0;while(!bytes.empty()){const auto n=::write(fd,bytes.data(),bytes.size());if(n<0&&errno==EINTR&&++retries<=16)continue;
        need(n>0,"recovery_store.write");bytes.remove_prefix(static_cast<std::size_t>(n));}
}
std::string nonce(){
    std::array<unsigned char,16> bytes{};std::size_t pos=0;unsigned retries=0;
    while(pos<bytes.size()){const auto n=::getrandom(bytes.data()+pos,bytes.size()-pos,0);if(n<0&&errno==EINTR&&++retries<=16)continue;need(n>0,"recovery_store.identity");pos+=static_cast<std::size_t>(n);}
    std::string out;constexpr char hex[]="0123456789abcdef";for(auto b:bytes){out+=hex[b>>4];out+=hex[b&15];}return out;
}
void authorized(const LinuxRecoveryStore::Guard& guard){
    bool allowed=false;try{allowed=guard&&guard();}catch(...){allowed=false;}need(allowed,"recovery_store.denied");
}
std::optional<std::string> digest(const std::optional<Node>& node){return node?std::optional<std::string>(configuration::sha256(node->bytes)):std::nullopt;}
struct Active {bool& value;explicit Active(bool& v):value(v){need(!value,"recovery_store.reentrant");value=true;}~Active(){value=false;}};
}
struct LinuxRecoveryStore::Impl {
    std::string path,instance=nonce();File root,lock;struct stat root_id{},lock_id{};std::thread::id owner=std::this_thread::get_id();
    std::uint64_t sequence=0;bool poisoned=false;mutable bool active=false;std::function<void(const char*)> hook;
    void check_owner()const{need(std::this_thread::get_id()==owner,"recovery_store.owner");need(!poisoned,"recovery_store.unknown");}
    void step(const char* name){if(hook)hook(name);}
    void validate()const{
        const auto reopened=root_directory(path);need(same_node(private_node(reopened.fd,true),root_id)&&same_node(private_node(root.fd,true),root_id),"recovery_store.external_change");
        const auto current=private_node(lock.fd,false,0);need(same_file(current,lock_id),"recovery_store.external_change");bound_name(root.fd,".writer",current);layout(root.fd);
    }
    void unchanged(const std::optional<Node>& prior)const{
        const auto now=read_node(root.fd,"draft.json");need(prior.has_value()==now.has_value()&&(!prior||(same_file(prior->info,now->info)&&prior->bytes==now->bytes)),"recovery_store.external_change");
    }
    void remove_pending(const std::optional<Node>& node,const Guard& guard){
        authorized(guard);validate();if(node){bound_name(root.fd,".pending",node->info);need(::unlinkat(root.fd,".pending",0)==0,"recovery_store.unlink");}
        else need(!read_node(root.fd,".pending"),"recovery_store.external_change");
        flush(root.fd);step("pending_removed");
    }
    RecoveryPublication mutate(const RecoveryVersion& expected,std::optional<std::string_view> bytes,const Guard& guard){
        check_owner();Active busy(active);bool published=false;
        try{
            need(!bytes||(!bytes->empty()&&bytes->size()<=maximum_bytes),"recovery_store.size");
            need(expected.instance==instance&&expected.sequence==sequence&&sequence<std::numeric_limits<std::uint64_t>::max(),"recovery_store.conflict");
            authorized(guard);validate();auto old=read_node(root.fd,"draft.json");auto pending=read_node(root.fd,".pending");
            need(digest(old)==expected.digest,"recovery_store.conflict");authorized(guard);++sequence;step("admitted");
            unchanged(old);remove_pending(pending,guard);pending.reset();
            if(bytes){
                File staging(::openat(root.fd,".pending",O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK,0600));private_node(staging.fd,false);step("pending_created");
                const auto split=(bytes->size()+1)/2;write_bytes(staging.fd,bytes->substr(0,split));step("pending_partial");
                write_bytes(staging.fd,bytes->substr(split));step("pending_written");flush(staging.fd);step("pending_flushed");step("publish_ready");
                authorized(guard);validate();unchanged(old);const auto staged=read_node(root.fd,".pending");
                need(staged&&same_file(staged->info,private_node(staging.fd,false))&&staged->bytes==*bytes,"recovery_store.external_change");
                need(::renameat(root.fd,".pending",root.fd,"draft.json")==0,"recovery_store.rename");published=true;step("published");
                flush(root.fd);validate();bound_name(root.fd,"draft.json",private_node(staging.fd,false));need(!read_node(root.fd,".pending"),"recovery_store.external_change");
            }else{
                step("retire_ready");authorized(guard);validate();unchanged(old);
                if(old)need(::unlinkat(root.fd,"draft.json",0)==0,"recovery_store.unlink");
                published=true;step("retired");
                flush(root.fd);validate();need(!read_node(root.fd,"draft.json")&&!read_node(root.fd,".pending"),"recovery_store.external_change");
            }
            step("durable");return {Publication::durable,{}};
        }catch(const Error& e){
            if(published){poisoned=true;return {Publication::unknown,"recovery_store.unknown"};}
            const std::string code=e.what();return {Publication::unchanged,code.size()<=64&&code.substr(0,15)=="recovery_store."?code:"recovery_store.io"};
        }catch(...){if(published)poisoned=true;return {published?Publication::unknown:Publication::unchanged,published?"recovery_store.unknown":"recovery_store.io"};}
    }
};
LinuxRecoveryStore::LinuxRecoveryStore(const std::string& path,std::function<void(const char*)> hook):impl_(std::make_unique<Impl>()){
    auto& s=*impl_;s.path=path;s.hook=std::move(hook);s.root=root_directory(path);s.root_id=private_node(s.root.fd,true);layout(s.root.fd);
    s.lock=File(::openat(s.root.fd,".writer",O_RDWR|O_CREAT|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC,0600));s.lock_id=private_node(s.lock.fd,false,0);
    need(::flock(s.lock.fd,LOCK_EX|LOCK_NB)==0,"recovery_store.busy");s.validate();
}
LinuxRecoveryStore::~LinuxRecoveryStore()=default;
RecoverySnapshot LinuxRecoveryStore::snapshot(const Guard& guard)const{
    auto& s=*impl_;s.check_owner();Active busy(s.active);authorized(guard);s.validate();auto current=read_node(s.root.fd,"draft.json");const auto pending=read_node(s.root.fd,".pending");
    if(current)flush(current->file.fd);
    flush(s.root.fd);s.validate();s.unchanged(current);authorized(guard);
    RecoverySnapshot out{{s.instance,s.sequence,digest(current)},std::nullopt,pending.has_value()};if(current)out.bytes=std::move(current->bytes);return out;
}
RecoveryPublication LinuxRecoveryStore::replace(const RecoveryVersion& version,std::string_view bytes,const Guard& guard){return impl_->mutate(version,bytes,guard);}
RecoveryPublication LinuxRecoveryStore::retire(const RecoveryVersion& version,const Guard& guard){return impl_->mutate(version,std::nullopt,guard);}
}
