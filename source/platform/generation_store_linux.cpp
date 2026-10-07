#include "generation_store_linux.hpp"
#include "digest.hpp"
#include <array>
#include <cerrno>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/random.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <unistd.h>

namespace syspane::platform {
namespace c=configuration;using protocol::Json;using protocol::Error;
namespace {
void need(bool ok,const char* code){if(!ok)throw Error(code);}
struct File {
    int fd=-1;
    explicit File(int value=-1):fd(value){}
    ~File(){if(fd>=0)::close(fd);}
    File(const File&)=delete;File& operator=(const File&)=delete;
    File(File&& other)noexcept:fd(other.fd){other.fd=-1;}
    File& operator=(File&& other)noexcept{if(this!=&other){if(fd>=0)::close(fd);fd=other.fd;other.fd=-1;}return *this;}
};
void private_node(int fd,bool directory,std::size_t maximum=1048576){
    struct stat s{};need(fd>=0&&::fstat(fd,&s)==0,"storage.open");
    need(s.st_uid==::geteuid()&&!(s.st_mode&0077)&&!(s.st_mode&07000),"storage.permissions");
    need(directory?S_ISDIR(s.st_mode):(S_ISREG(s.st_mode)&&s.st_nlink==1&&!(s.st_mode&0111)&&s.st_size>=0&&static_cast<std::uint64_t>(s.st_size)<=maximum),"storage.type");
}
void flush(int fd){need(::fsync(fd)==0,"storage.flush");}
File directory_at(int parent,const char* name){File f(::openat(parent,name,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));private_node(f.fd,true);return f;}
File root_directory(const std::string& path){
    need(path.size()>1&&path.size()<=4096&&path[0]=='/'&&path.back()!='/'&&path.find('\0')==std::string::npos,"storage.path");
    File f(::open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC));std::size_t begin=1;
    while(begin<path.size()){
        const auto end=path.find('/',begin);const auto part=path.substr(begin,end==std::string::npos?path.size()-begin:end-begin);
        need(!part.empty()&&part!="."&&part!="..","storage.path");
        File next(::openat(f.fd,part.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));need(next.fd>=0,"storage.path");f=std::move(next);
        if(end==std::string::npos)break;
        begin=end+1;
    }
    private_node(f.fd,true);struct statfs fs{};need(::fstatfs(f.fd,&fs)==0&&fs.f_type==0xef53,"storage.filesystem");return f;
}
std::optional<std::string> read(int parent,const char* name,std::size_t maximum,bool synchronize=false){
    File f(::openat(parent,name,O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK));
    if(f.fd<0&&errno==ENOENT)return {};
    private_node(f.fd,false,maximum);std::string bytes;std::array<char,4096> buffer{};
    for(;;){const auto count=::read(f.fd,buffer.data(),buffer.size());if(count<0&&errno==EINTR)continue;
        need(count>=0,"storage.read");if(count==0)break;
        need(bytes.size()+static_cast<std::size_t>(count)<=maximum,"storage.size");bytes.append(buffer.data(),static_cast<std::size_t>(count));}
    if(synchronize)flush(f.fd);
    return bytes;
}
std::string required(int parent,const char* name,std::size_t maximum,bool synchronize=false){auto value=read(parent,name,maximum,synchronize);need(value.has_value(),"storage.missing");return *value;}
void write(int parent,const char* name,std::string_view bytes){
    File f(::openat(parent,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600));private_node(f.fd,false);
    std::size_t position=0;while(position<bytes.size()){
        const auto count=::write(f.fd,bytes.data()+position,bytes.size()-position);if(count<0&&errno==EINTR)continue;
        need(count>0,"storage.write");position+=static_cast<std::size_t>(count);
    }
    flush(f.fd);
}
std::string random_name(const char* prefix){
    std::array<unsigned char,16> bytes{};std::size_t count=0;
    while(count<bytes.size()){const auto n=::getrandom(bytes.data()+count,bytes.size()-count,0);if(n<0&&errno==EINTR)continue;need(n>0,"storage.identity");count+=static_cast<std::size_t>(n);}
    std::string result=prefix;constexpr char hex[]="0123456789abcdef";for(auto n:bytes){result+=hex[n>>4];result+=hex[n&15];}return result;
}
bool digest(const Json& value){
    if(!value.is_string())return false;
    const auto& s=value.get_ref<const std::string&>();return s.size()==64&&s.find_first_not_of("0123456789abcdef")==std::string::npos;
}
Json identity(const std::optional<c::CommitIdentity>& value){
    if(!value)return nullptr;
    return {{"principal",value->principal},{"epoch",value->epoch},{"request",value->request},{"body",value->body}};
}
void exact_files(int fd,const std::set<std::string>& expected){
    File listing(::openat(fd,".",O_RDONLY|O_DIRECTORY|O_CLOEXEC));need(listing.fd>=0,"storage.directory");
    DIR* raw=::fdopendir(listing.fd);need(raw!=nullptr,"storage.directory");listing.fd=-1;
    std::unique_ptr<DIR,int(*)(DIR*)> dir(raw,::closedir);std::set<std::string> found;
    for(;;){errno=0;const auto* entry=::readdir(dir.get());if(!entry){need(errno==0,"storage.directory");break;}
        const std::string name=entry->d_name;if(name=="."||name=="..")continue;
        need(expected.count(name)&&found.insert(name).second,"storage.resource_files");}
    need(found==expected,"storage.resource_files");
}
c::ResourceSnapshot decode_resources(int parent,const Json& hash,const c::Authored& documents,bool synchronize){
    need(digest(hash),"storage.resources");const auto bytes=required(parent,"resources.json",65536,synchronize);
    need(c::sha256(bytes)==hash,"storage.resources");const auto index=protocol::parse(bytes);
    need(protocol::members(index,{"version","selection","theme","packages"})&&index["version"]=="0.1.0"&&
        index["packages"].is_array()&&!index["packages"].empty()&&index["packages"].size()<=64,"storage.resources");
    auto dir=directory_at(parent,"resources");std::set<std::string> expected;std::string prior;std::vector<c::ContentPackage> packages;std::size_t count=0,total=0;
    for(const auto& item:index["packages"]){need(digest(item),"storage.resources");const auto pin=item.get<std::string>();need(prior.empty()||prior<pin,"storage.resources");prior=pin;
        const auto filename="m-"+pin+".json";expected.insert(filename);c::ContentPackage package;package.manifest=required(dir.fd,filename.c_str(),65536,synchronize);
        need(c::sha256(package.manifest)==pin,"storage.resources");const auto manifest=c::validate_content_manifest(package.manifest);
        for(const auto& asset:manifest["assets"]){const auto size=asset["bytes"].get<std::size_t>();total+=size;
            need(++count<=1024&&total<=67108864&&(asset["media_type"]!="application/json"||size<=262144),"storage.resource_capacity");
            const auto file="a-"+asset["sha256"].get<std::string>()+".bin";expected.insert(file);
            auto payload=required(dir.fd,file.c_str(),size,synchronize);need(payload.size()==size&&c::content_sha256(payload)==asset["sha256"],"storage.resources");
            package.assets.emplace(asset["path"].get<std::string>(),std::move(payload));}
        packages.push_back(std::move(package));
    }
    exact_files(dir.fd,expected);const auto resources=c::ContentCatalog(std::move(packages)).resources(index["selection"],documents);
    need(resources->packages().size()==index["packages"].size()&&resources->theme_pin()==index["theme"],"storage.resources");
    if(synchronize)flush(dir.fd);
    return resources;
}
std::string write_resources(int parent,const c::ResourceSet& resources,const std::function<void(const char*)>& hook){
    need(::mkdirat(parent,"resources",0700)==0,"storage.mkdir");auto dir=directory_at(parent,"resources");if(hook)hook("resources_created");
    std::map<std::string,const std::string*> manifests,assets;
    for(const auto& package:resources.packages()){
        manifests.emplace(c::sha256(package->manifest),&package->manifest);
        for(const auto& asset:package->assets)assets.emplace(c::content_sha256(asset.second),&asset.second);}
    Json pins=Json::array();unsigned n=0;
    for(const auto& row:manifests){write(dir.fd,("m-"+row.first+".json").c_str(),*row.second);pins.push_back(row.first);
        const auto phase="resource_manifest:"+std::to_string(n++);if(hook)hook(phase.c_str());}
    n=0;for(const auto& row:assets){write(dir.fd,("a-"+row.first+".bin").c_str(),*row.second);
        const auto phase="resource_asset:"+std::to_string(n++);if(hook)hook(phase.c_str());}
    const auto index=Json{{"version","0.1.0"},{"selection",resources.selection()},{"theme",resources.theme_pin()},{"packages",pins}}.dump();
    need(index.size()<=65536,"storage.resource_capacity");write(parent,"resources.json",index);if(hook)hook("resource_index");flush(dir.fd);if(hook)hook("resources_flushed");return c::sha256(index);
}
}
struct LinuxGenerationStore::Impl {
    File root,lock;std::function<void(const char*)> hook;
    std::optional<c::Committed> current,previous;
    std::optional<std::string> current_selector,selected;
    bool fallback=false,poisoned=false,damaged=false;
    void step(const char* name){if(hook)hook(name);}
    c::Committed decode(const std::string& bytes,bool synchronize){
        const auto pointer=protocol::parse(bytes);
        need(protocol::members(pointer,{"version","generation","manifest"})&&pointer["version"]=="0.1.0"&&pointer["generation"].is_string()&&digest(pointer["manifest"]),"storage.selector");
        const auto name=pointer["generation"].get<std::string>();
        need(name.size()==34&&name.substr(0,2)=="g-"&&name.substr(2).find_first_not_of("0123456789abcdef")==std::string::npos,"storage.generation");
        auto dir=directory_at(root.fd,name.c_str());const auto manifest_bytes=required(dir.fd,"manifest.json",65536,synchronize);
        need(c::sha256(manifest_bytes)==pointer["manifest"],"storage.manifest_digest");const auto manifest=protocol::parse(manifest_bytes);
        const bool separate=manifest.is_object()&&manifest.value("version",Json())=="0.3.0";
        const bool resources=manifest.is_object()&&(manifest.value("version",Json())=="0.2.0"||(separate&&manifest.contains("resources")));
        need((resources?protocol::members(manifest,{"version","revision","settings","scene","identity","resources"}):
            (protocol::members(manifest,{"version","revision","settings","scene","identity"})&&(separate||manifest["version"]=="0.1.0")))&&digest(manifest["settings"])&&digest(manifest["scene"]),"storage.manifest");
        const auto settings=required(dir.fd,"settings.json",16384,synchronize),scene=required(dir.fd,"scene.json",262144,synchronize);
        need(c::sha256(settings)==manifest["settings"]&&c::sha256(scene)==manifest["scene"],"storage.document_digest");
        c::Committed value{{protocol::parse(settings),protocol::parse(scene)},std::nullopt};c::validate_authored(value.documents);
        need(resources||value.documents.scene["schema_version"]!="0.3.0","storage.resource_required");
        if(resources||separate){
            std::set<std::string> expected={"settings.json","scene.json","manifest.json"};
            if(resources)expected.insert({"resources.json","resources"});
            if(separate)expected.insert("request.json");
            exact_files(dir.fd,expected);
        }
        if(resources)value.resources=decode_resources(dir.fd,manifest["resources"],value.documents,synchronize);
        need(value.documents.settings["revision"]==manifest["revision"],"storage.revision");const auto& id=manifest["identity"];
        if(!id.is_null()){
            need(separate?protocol::members(id,{"principal","epoch","request","body_sha256"}):protocol::members(id,{"principal","epoch","request","body"}),"storage.identity");
            for(const char* key:{"principal","epoch","request"})need(id[key].is_string()&&protocol::identifier(id[key].get_ref<const std::string&>()),"storage.identity");
            std::string body;
            if(separate){
                need(digest(id["body_sha256"]),"storage.identity");body=required(dir.fd,"request.json",protocol::large_command_limit,synchronize);
                need(c::sha256(body)==id["body_sha256"],"storage.request_digest");
            }else{
                need(id["body"].is_string()&&id["body"].get_ref<const std::string&>().size()<=protocol::command_limit,"storage.identity");
                body=id["body"].get<std::string>();
            }
            const auto command=c::parse_command(body);c::validate_command(command);
            need((command["schema_version"]=="0.5.0")==separate,"storage.identity_version");
            need(command.contains("content")==resources&&(!resources||command["content"]==value.resources->selection()),"storage.resource_identity");
            const auto expected=protocol::decimal(command["expected_revision"].get_ref<const std::string&>());
            need(command["request_id"]==id["request"]&&command["intent"]=="commit"&&*expected<c::authored_revision(value.documents)&&
                 c::authored_revision(value.documents)-*expected==1,"storage.identity");
            value.identity=c::CommitIdentity{id["principal"],id["epoch"],id["request"],std::move(body)};
        }
        need((!resources&&!separate)||value.identity.has_value(),"storage.resource_identity");
        if(synchronize){flush(dir.fd);flush(root.fd);}
        return value;
    }
    std::size_t generations(){
        File listing(::openat(root.fd,".",O_RDONLY|O_DIRECTORY|O_CLOEXEC));need(listing.fd>=0,"storage.directory");
        DIR* raw=::fdopendir(listing.fd);need(raw!=nullptr,"storage.directory");listing.fd=-1;
        std::unique_ptr<DIR,int(*)(DIR*)> dir(raw,::closedir);std::size_t count=0,entries=0;errno=0;
        while(const auto* entry=::readdir(dir.get())){const std::string name=entry->d_name;
            if(name=="."||name=="..")continue;
            ++entries;if(name.substr(0,2)=="g-")++count;need(entries<=100,"storage.capacity");errno=0;}
        need(errno==0,"storage.directory");return count;
    }
    void replace(const char* destination,const std::string& bytes,const std::function<void()>& before_rename={}){
        const auto temp=random_name(".selector-");write(root.fd,temp.c_str(),bytes);
        if(before_rename)before_rename();
        need(::renameat(root.fd,temp.c_str(),root.fd,destination)==0,"storage.replace");
    }
    c::Publication publish(const c::Committed& next,const std::function<void()>& guard){
        need(!poisoned&&!fallback&&!damaged,"storage.recovery_required");c::validate_authored(next.documents);
        need(next.resources||next.documents.scene["schema_version"]!="0.3.0","storage.resource_required");
        need(generations()<32,"storage.capacity");bool published=false;std::exception_ptr guard_failure;
        try{
            const auto generation=random_name("g-");need(::mkdirat(root.fd,generation.c_str(),0700)==0,"storage.mkdir");auto dir=directory_at(root.fd,generation.c_str());step("created");
            const auto settings=next.documents.settings.dump(),scene=next.documents.scene.dump();
            write(dir.fd,"settings.json",settings);step("settings");write(dir.fd,"scene.json",scene);step("scene");
            Json manifest_value={{"version",next.resources?"0.2.0":"0.1.0"},{"revision",next.documents.settings["revision"]},{"settings",c::sha256(settings)},{"scene",c::sha256(scene)},{"identity",identity(next.identity)}};
            if(next.identity&&c::parse_command(next.identity->body)["schema_version"]=="0.5.0"){
                manifest_value["version"]="0.3.0";manifest_value["identity"].erase("body");
                manifest_value["identity"]["body_sha256"]=c::sha256(next.identity->body);
                write(dir.fd,"request.json",next.identity->body);step("request");
            }
            if(next.resources){c::validate_resource_binding(*next.resources,next.documents);manifest_value["resources"]=write_resources(dir.fd,*next.resources,hook);}
            const auto manifest=manifest_value.dump();
            need(manifest.size()<=65536,"storage.manifest_size");write(dir.fd,"manifest.json",manifest);step("manifest");flush(dir.fd);flush(root.fd);step("generation");
            const auto selector=Json{{"version","0.1.0"},{"generation",generation},{"manifest",c::sha256(manifest)}}.dump();
            (void)decode(selector,false);
            need(read(root.fd,"current.json",4096)==current_selector,"storage.external_change");
            if(selected){(void)decode(*selected,false);replace("previous.json",*selected);flush(root.fd);}
            step("previous");
            replace("current.json",selector,[&]{
                step("selector_ready");
                try{guard();}catch(...){guard_failure=std::current_exception();throw;}
                step("authorized");
                need(read(root.fd,"current.json",4096)==current_selector,"storage.external_change");
            });published=true;step("selected");flush(root.fd);
            previous=current;current=next;current_selector=selected=selector;step("durable");return c::Publication::durable;
        }catch(...){
            if(published){poisoned=true;return c::Publication::unknown;}
            if(guard_failure)std::rethrow_exception(guard_failure);
            return c::Publication::unchanged;
        }
    }
};
LinuxGenerationStore::LinuxGenerationStore(const std::string& path,std::function<void(const char*)> hook):impl_(std::make_unique<Impl>()){
    auto& s=*impl_;s.root=root_directory(path);s.hook=std::move(hook);
    s.lock=File(::openat(s.root.fd,".writer",O_RDWR|O_CREAT|O_NOFOLLOW|O_CLOEXEC,0600));private_node(s.lock.fd,false,0);
    need(::flock(s.lock.fd,LOCK_EX|LOCK_NB)==0,"storage.busy");
    bool bad=false;try{s.current_selector=read(s.root.fd,"current.json",4096);if(s.current_selector){s.current=s.decode(*s.current_selector,true);s.selected=s.current_selector;}}catch(...){bad=true;}
    try{const auto prior=read(s.root.fd,"previous.json",4096);if(prior){s.previous=s.decode(*prior,true);if(!s.current){s.current=s.previous;s.selected=prior;s.fallback=true;}
        else need(c::authored_revision(s.previous->documents)<=c::authored_revision(s.current->documents),"storage.previous_revision");}}
    catch(...){s.previous.reset();s.damaged=true;if(!s.current)throw;}
    if(!s.current){need(!bad&&s.generations()==0,"storage.unrecoverable");}
    else if(bad||!s.current_selector)s.fallback=true;
    s.damaged=s.damaged||bad;
}
LinuxGenerationStore::~LinuxGenerationStore()=default;
void LinuxGenerationStore::initialize(const c::Authored& documents){
    need(!impl_->current&&impl_->generations()==0,"storage.not_empty");
    need(impl_->publish({documents,std::nullopt},[] {})==c::Publication::durable,"storage.bootstrap");
}
c::Committed LinuxGenerationStore::load()const{need(!impl_->poisoned&&impl_->current.has_value(),"storage.unavailable");return *impl_->current;}
std::vector<c::CommitReceipt> LinuxGenerationStore::receipts()const{
    need(!impl_->poisoned,"storage.unavailable");std::vector<c::CommitReceipt> result;
    for(const auto* record:{&impl_->current,&impl_->previous})if(*record&&(*record)->identity)
        result.push_back({*(*record)->identity,c::authored_revision((*record)->documents)});
    return result;
}
std::optional<c::Committed> LinuxGenerationStore::reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const{
    need(!impl_->poisoned,"storage.unavailable");
    for(const auto* record:{&impl_->current,&impl_->previous})if(*record&&(*record)->identity){const auto& id=*(*record)->identity;if(id.principal==principal&&id.epoch==epoch&&id.request==request)return *record;}
    return {};
}
c::Publication LinuxGenerationStore::publish(const c::Committed& next,const std::function<void()>& guard){
    need(impl_->current.has_value()&&next.identity.has_value(),"storage.state");return impl_->publish(next,guard);
}
bool LinuxGenerationStore::recovered_previous()const{return impl_->fallback;}
}
