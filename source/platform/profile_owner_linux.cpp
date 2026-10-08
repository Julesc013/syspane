#include "profile_owner_linux.hpp"
#include "generation_store_linux.hpp"
#include "digest.hpp"
#include "wire.hpp"
#include <array>
#include <cerrno>
#include <cstdlib>
#include <dirent.h>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/random.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/vfs.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace syspane::platform {
namespace {
using Guard=LinuxProfileOwner::Guard;
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
struct File {
    int fd=-1;
    explicit File(int value=-1):fd(value){}
    ~File(){if(fd>=0)::close(fd);}
    File(const File&)=delete;File& operator=(const File&)=delete;
    File(File&& value)noexcept:fd(value.fd){value.fd=-1;}
    File& operator=(File&& value)noexcept{if(this!=&value){if(fd>=0)::close(fd);fd=value.fd;value.fd=-1;}return *this;}
};
std::string path(std::string value){
    need(!value.empty()&&value.size()<=4096&&value.front()=='/'&&value.find('\0')==std::string::npos,"profile.path");
    while(value.size()>1&&value.back()=='/')value.pop_back();
    std::size_t begin=1,count=0;
    while(begin<value.size()){
        const auto end=value.find('/',begin);const auto part=value.substr(begin,end==std::string::npos?value.size()-begin:end-begin);
        need(!part.empty()&&part!="."&&part!=".."&&part.size()<=255&&++count<=64,"profile.path");
        if(end==std::string::npos)break;
        begin=end+1;
    }
    return value;
}
std::string join(const std::string& base,const std::string& tail){return path((base=="/"?"":base)+"/"+tail);}
std::string base(const std::string& explicit_path,const std::string& home,const char* fallback){
    if(!explicit_path.empty()&&explicit_path.front()=='/')return path(explicit_path);
    return join(path(home),fallback);
}
bool contains(const std::string& a,const std::string& b){return a==b||b.compare(0,a.size()+1,a+"/")==0;}
void authorized(const Guard& guard){bool allowed=false;try{allowed=guard&&guard();}catch(...){ }need(allowed,"profile.denied");}
struct stat info(int fd){struct stat value{};need(fd>=0&&::fstat(fd,&value)==0,"profile.open");return value;}
bool same(const struct stat& a,const struct stat& b){return a.st_dev==b.st_dev&&a.st_ino==b.st_ino;}
bool exact(const struct stat& a,const struct stat& b){
    return same(a,b)&&a.st_mode==b.st_mode&&a.st_uid==b.st_uid&&a.st_gid==b.st_gid&&a.st_nlink==b.st_nlink&&a.st_size==b.st_size&&
        a.st_mtim.tv_sec==b.st_mtim.tv_sec&&a.st_mtim.tv_nsec==b.st_mtim.tv_nsec&&a.st_ctim.tv_sec==b.st_ctim.tv_sec&&a.st_ctim.tv_nsec==b.st_ctim.tv_nsec;
}
struct stat private_node(int fd,bool directory,std::size_t maximum=1024){
    const auto s=info(fd);need(s.st_uid==::geteuid()&&(s.st_mode&07777)==(directory?0700:0600),"profile.permissions");
    need(directory?S_ISDIR(s.st_mode):(S_ISREG(s.st_mode)&&s.st_nlink==1&&s.st_size>=0&&static_cast<std::uint64_t>(s.st_size)<=maximum),"profile.type");return s;
}
void ancestor(int fd){const auto s=info(fd);need(S_ISDIR(s.st_mode)&&(s.st_uid==0||s.st_uid==::geteuid())&&(s.st_mode&07022)==0,"profile.ancestor");}
void filesystem(int fd){struct statfs value{};need(::fstatfs(fd,&value)==0&&value.f_type==0xef53,"profile.filesystem");}
void flush(int fd){unsigned retries=0;for(;;){if(::fsync(fd)==0)return;need(errno==EINTR&&++retries<=16,"profile.flush");}}
File walk(const std::string& selected,bool create=false,const Guard& guard={}){
    const auto value=path(selected);File dir(::open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC));ancestor(dir.fd);
    std::size_t begin=1;std::string prefix="/";
    while(begin<value.size()){
        const auto end=value.find('/',begin);const auto part=value.substr(begin,end==std::string::npos?value.size()-begin:end-begin);
        File next(::openat(dir.fd,part.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));
        if(next.fd<0&&errno==ENOENT&&create){
            authorized(guard);auto fresh=walk(prefix);need(same(info(fresh.fd),info(dir.fd)),"profile.changed");filesystem(dir.fd);
            const int made=::mkdirat(dir.fd,part.c_str(),0700);need(made==0||errno==EEXIST,"profile.mkdir");
            next=File(::openat(dir.fd,part.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));
            if(made==0)private_node(next.fd,true);
            flush(dir.fd);
        }
        need(next.fd>=0,"profile.path");ancestor(next.fd);dir=std::move(next);prefix=join(prefix,part);
        if(end==std::string::npos)break;
        begin=end+1;
    }
    return dir;
}
void bound(int parent,const std::string& name,const struct stat& expected,bool file=false){
    struct stat current{};need(::fstatat(parent,name.c_str(),&current,AT_SYMLINK_NOFOLLOW)==0&&(file?exact(current,expected):same(current,expected)),"profile.changed");
}
std::vector<std::string> entries(int fd,std::size_t maximum){
    File copy(::openat(fd,".",O_RDONLY|O_DIRECTORY|O_CLOEXEC));need(copy.fd>=0,"profile.layout");
    DIR* raw=::fdopendir(copy.fd);need(raw!=nullptr,"profile.layout");copy.fd=-1;
    std::unique_ptr<DIR,int(*)(DIR*)> list(raw,::closedir);std::vector<std::string> names;
    for(;;){errno=0;const auto* e=::readdir(raw);if(!e){need(errno==0,"profile.layout");break;}
        const std::string n=e->d_name;if(n=="."||n=="..")continue;
        need(names.size()<maximum,"profile.capacity");names.push_back(n);
    }
    return names;
}
void layout(int fd,const std::string& child){
    const auto names=entries(fd,3);need(names.size()==3,"profile.layout");
    for(const auto& n:names)need(n==".owner.json"||n==".lease"||n==child,"profile.layout");
}
std::string read(int fd){
    need(::lseek(fd,0,SEEK_SET)==0,"profile.read");const auto before=private_node(fd,false);std::string bytes;std::array<char,1025> buffer{};unsigned retries=0;
    for(;;){const auto n=::read(fd,buffer.data(),buffer.size());if(n<0&&errno==EINTR&&++retries<=16)continue;
        need(n>=0,"profile.read");if(n==0)break;need(bytes.size()+static_cast<std::size_t>(n)<=1024,"profile.size");bytes.append(buffer.data(),static_cast<std::size_t>(n));}
    need(exact(before,private_node(fd,false))&&bytes.size()==static_cast<std::size_t>(before.st_size),"profile.changed");return bytes;
}
void write(int fd,std::string_view bytes){
    unsigned retries=0;while(!bytes.empty()){const auto n=::write(fd,bytes.data(),bytes.size());if(n<0&&errno==EINTR&&++retries<=16)continue;
        need(n>0,"profile.write");bytes.remove_prefix(static_cast<std::size_t>(n));}
}
std::string nonce(){
    std::array<unsigned char,16> bytes{};std::size_t pos=0;unsigned retries=0;
    while(pos<bytes.size()){const auto n=::getrandom(bytes.data()+pos,bytes.size()-pos,0);if(n<0&&errno==EINTR&&++retries<=16)continue;
        need(n>0,"profile.random");pos+=static_cast<std::size_t>(n);}
    std::string value;constexpr char hex[]="0123456789abcdef";for(auto b:bytes){value+=hex[b>>4];value+=hex[b&15];}return value;
}
struct Role {
    std::string name,root,child,marker;
    File directory,lease,marker_file,child_directory;
    struct stat directory_info{},lease_info{},marker_info{},child_info{};
};
void capture(Role& r){
    r.directory_info=private_node(r.directory.fd,true);filesystem(r.directory.fd);layout(r.directory.fd,r.child);
    r.marker_file=File(::openat(r.directory.fd,".owner.json",O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK));
    r.marker_info=private_node(r.marker_file.fd,false);need(read(r.marker_file.fd)==r.marker,"profile.marker");
    r.lease=File(::openat(r.directory.fd,".lease",O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK));
    r.lease_info=private_node(r.lease.fd,false,0);need(::flock(r.lease.fd,LOCK_EX|LOCK_NB)==0,"profile.busy");
    r.child_directory=File(::openat(r.directory.fd,r.child.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));
    r.child_info=private_node(r.child_directory.fd,true);need(r.child_info.st_dev==r.directory_info.st_dev,"profile.filesystem");
}
void validate(Role& r){
    auto fresh=walk(r.root);need(same(private_node(fresh.fd,true),r.directory_info),"profile.changed");filesystem(fresh.fd);layout(fresh.fd,r.child);
    need(same(private_node(r.directory.fd,true),r.directory_info)&&exact(private_node(r.lease.fd,false,0),r.lease_info)&&
        exact(private_node(r.marker_file.fd,false),r.marker_info)&&same(private_node(r.child_directory.fd,true),r.child_info),"profile.changed");
    bound(fresh.fd,".lease",r.lease_info,true);bound(fresh.fd,".owner.json",r.marker_info,true);bound(fresh.fd,r.child,r.child_info);
    need(read(r.marker_file.fd)==r.marker,"profile.marker");
}
void initial_matches(const configuration::Committed& actual,const configuration::Committed& expected){
    need(!actual.identity&&actual.resources&&actual.documents.settings.dump()==expected.documents.settings.dump()&&
        actual.documents.scene.dump()==expected.documents.scene.dump()&&actual.resources->selection()==expected.resources->selection()&&
        actual.resources->theme_pin()==expected.resources->theme_pin(),"profile.initial_changed");
    auto pins=[](const configuration::ResourceSet& resources){std::set<std::string> result;for(const auto& p:resources.packages())result.insert(configuration::sha256(p->manifest));return result;};
    need(pins(*actual.resources)==pins(*expected.resources),"profile.initial_changed");
}
void acquire(Role& r,bool create,const Guard& guard,const LinuxProfileOwner::Transition& transition,const LinuxProfileOwner::InitialProfile& initial){
    const auto slash=r.root.rfind('/');const auto parent_path=r.root.substr(0,slash);const auto key=r.root.substr(slash+1);
    authorized(guard);auto parent=walk(parent_path,create,guard);filesystem(parent.fd);
    r.directory=File(::openat(parent.fd,key.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));
    if(r.directory.fd>=0){capture(r);validate(r);authorized(guard);return;}
    need(errno==ENOENT&&create,"profile.path");
    std::optional<configuration::Committed> seed;
    if(initial&&r.name=="configuration"){
        authorized(guard);seed=initial();
        need(seed->resources&&!seed->identity&&configuration::authored_revision(seed->documents)==0,"profile.initial");
        configuration::validate_resource_binding(*seed->resources,seed->documents);
    }
    const std::string prefix="."+key+".pending-";std::size_t count=0;
    for(const auto& n:entries(parent.fd,4096))if(n.compare(0,prefix.size(),prefix)==0)++count;
    need(count<8,"profile.capacity");
    auto current_parent=[&]{authorized(guard);auto fresh=walk(parent_path);need(same(info(parent.fd),info(fresh.fd)),"profile.changed");};
    const auto staging=prefix+nonce();current_parent();need(::mkdirat(parent.fd,staging.c_str(),0700)==0,"profile.mkdir");
    r.directory=File(::openat(parent.fd,staging.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));
    r.directory_info=private_node(r.directory.fd,true);
    auto check_stage=[&]{current_parent();need(same(private_node(r.directory.fd,true),r.directory_info),"profile.changed");bound(parent.fd,staging,r.directory_info);};
    auto step=[&](const char* phase){if(transition)transition(r.name+"."+phase);};
    step("stage_created");check_stage();
    File marker(::openat(r.directory.fd,".owner.json",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600));private_node(marker.fd,false);
    write(marker.fd,r.marker);flush(marker.fd);step("marker_flushed");check_stage();
    File lease(::openat(r.directory.fd,".lease",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600));private_node(lease.fd,false,0);flush(lease.fd);
    step("lease_flushed");check_stage();need(::mkdirat(r.directory.fd,r.child.c_str(),0700)==0,"profile.mkdir");
    File child(::openat(r.directory.fd,r.child.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));private_node(child.fd,true);
    const auto child_path=join(join(parent_path,staging),r.child);
    if(seed){
        LinuxGenerationStore store(child_path,[&](const char* phase){if(transition)transition(r.name+".initial."+phase);});
        store.bootstrap(*seed,check_stage);
    }
    flush(child.fd);
    step("child_flushed");check_stage();capture(r);flush(r.directory.fd);step("stage_flushed");step("publish_ready");check_stage();
    // Validate immutable initialization bytes and exact child before the no-replace rename.
    bound(r.directory.fd,".owner.json",r.marker_info,true);bound(r.directory.fd,".lease",r.lease_info,true);bound(r.directory.fd,r.child,r.child_info);
    need(same(private_node(r.child_directory.fd,true),r.child_info),"profile.changed");
    need(read(r.marker_file.fd)==r.marker,"profile.changed");layout(r.directory.fd,r.child);
    if(seed){LinuxGenerationStore reopened(child_path);initial_matches(reopened.load(),*seed);check_stage();}
    else need(entries(r.child_directory.fd,0).empty(),"profile.changed");
    need(::syscall(SYS_renameat2,parent.fd,staging.c_str(),parent.fd,key.c_str(),RENAME_NOREPLACE)==0,"profile.publish");
    step("published");current_parent();validate(r);flush(parent.fd);step("parent_flushed");authorized(guard);validate(r);
}
}

ProfilePaths profile_paths(const ProfileLocation& value){
    need(protocol::identifier(value.profile),"profile.identifier");const auto key=configuration::sha256(value.profile);ProfilePaths result;
    result.profile=value.profile;result.mode=value.portable_root?"portable":"xdg";
    const auto config=value.portable_root?path(*value.portable_root):base(value.config_home,value.home,".config");
    const auto data=value.portable_root?path(*value.portable_root):base(value.data_home,value.home,".local/share");
    const auto state=value.portable_root?path(*value.portable_root):base(value.state_home,value.home,".local/state");
    result.configuration=join(config,"syspane/configuration/"+key);result.content=join(data,"syspane/content/"+key);result.state=join(state,"syspane/state/"+key);
    const std::array<std::string,3> roots={result.configuration,result.content,result.state};
    for(std::size_t i=0;i<roots.size();++i)for(std::size_t j=i+1;j<roots.size();++j)need(!contains(roots[i],roots[j])&&!contains(roots[j],roots[i]),"profile.overlap");
    result.generations=join(result.configuration,"generations");result.packages=join(result.content,"packages");result.recovery=join(result.state,"recovery");return result;
}
ProfileLocation profile_environment(std::string profile,std::optional<std::string> portable){
    auto env=[](const char* name){const auto* p=std::getenv(name);return p?std::string(p):std::string();};
    return {std::move(profile),env("HOME"),env("XDG_CONFIG_HOME"),env("XDG_DATA_HOME"),env("XDG_STATE_HOME"),std::move(portable)};
}
struct LinuxProfileOwner::Impl {
    ProfilePaths paths;std::array<Role,3> roles;std::thread::id thread=std::this_thread::get_id();bool active=false,invalid=false;
    Impl(const ProfileLocation& location,bool create,const Guard& guard,const Transition& transition,const InitialProfile& initial):paths(profile_paths(location)){
        need(::geteuid()!=0,"profile.identity");authorized(guard);
        const std::array<std::string,3> names={"configuration","content","state"},roots={paths.configuration,paths.content,paths.state},children={"generations","packages","recovery"};
        for(std::size_t i=0;i<roles.size();++i){auto& role=roles[i];role.name=names[i];role.root=roots[i];role.child=children[i];
            role.marker=protocol::Json{{"format","SysPane.Profile"},{"schema_version","0.1.0"},{"profile",paths.profile},{"kind",role.name},{"mode",paths.mode}}.dump();
            need(role.marker.size()<=1024,"profile.size");acquire(role,create,guard,transition,initial);}
        verify(guard);
    }
    void verify(const Guard& guard){
        need(thread==std::this_thread::get_id(),"profile.thread");need(!active,"profile.reentrant");need(!invalid,"profile.invalidated");
        struct Active {bool& flag;explicit Active(bool& f):flag(f){flag=true;}~Active(){flag=false;}} busy(active);
        try{authorized(guard);for(auto& r:roles)validate(r);
            for(std::size_t i=0;i<roles.size();++i)for(std::size_t j=i+1;j<roles.size();++j)
                need(!same(roles[i].directory_info,roles[j].directory_info)&&!same(roles[i].child_info,roles[j].child_info),"profile.overlap");
            authorized(guard);
        }catch(...){invalid=true;throw;}
    }
};
LinuxProfileOwner::LinuxProfileOwner(const ProfileLocation& location,bool create,const Guard& guard,Transition transition,InitialProfile initial):impl_(std::make_unique<Impl>(location,create,guard,transition,initial)){}
LinuxProfileOwner::~LinuxProfileOwner()=default;
ProfilePaths LinuxProfileOwner::verified_paths(const Guard& guard)const{impl_->verify(guard);return impl_->paths;}
}
