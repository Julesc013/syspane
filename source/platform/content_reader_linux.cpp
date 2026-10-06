#include "content_reader_linux.hpp"
#include <array>
#include <cerrno>
#include <dirent.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace syspane::platform {
namespace c=configuration;
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
struct File {
    int fd;explicit File(int value):fd(value){}~File(){if(fd>=0)::close(fd);}
    File(const File&)=delete;File& operator=(const File&)=delete;
    File(File&& other)noexcept:fd(other.fd){other.fd=-1;}
    File& operator=(File&& other)noexcept{if(this!=&other){if(fd>=0)::close(fd);fd=other.fd;other.fd=-1;}return *this;}
};
struct stat inspect(int fd,bool directory,std::size_t bound){
    struct stat s{};need(fd>=0&&::fstat(fd,&s)==0,"content.open");
    need(s.st_uid==::geteuid()&&!(s.st_mode&0077)&&!(s.st_mode&07000),"content.permissions");
    need(directory?S_ISDIR(s.st_mode):(S_ISREG(s.st_mode)&&s.st_nlink==1&&!(s.st_mode&0111)&&s.st_size>=0&&static_cast<std::uint64_t>(s.st_size)<=bound),"content.file");
    return s;
}
File root(const std::string& path){
    need(path.size()>1&&path.size()<=4096&&path.front()=='/'&&path.back()!='/'&&path.find('\0')==std::string::npos,"content.root");
    File current(::open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC));std::size_t begin=1;
    for(;;){const auto end=path.find('/',begin);const auto part=path.substr(begin,end==std::string::npos?end:end-begin);
        need(!part.empty()&&part!="."&&part!="..","content.root");
        File next(::openat(current.fd,part.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));need(next.fd>=0,"content.root");current=std::move(next);
        if(end==std::string::npos)break;
        begin=end+1;
    }
    (void)inspect(current.fd,true,0);return current;
}
std::string read(int parent,const std::string& name,std::size_t maximum){
    File f(::openat(parent,name.c_str(),O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK));const auto before=inspect(f.fd,false,maximum);
    std::array<char,4096> buffer{};std::string bytes;
    for(;;){const auto n=::read(f.fd,buffer.data(),buffer.size());if(n<0&&errno==EINTR)continue;need(n>=0,"content.read");if(!n)break;
        need(bytes.size()+static_cast<std::size_t>(n)<=maximum,"content.size");bytes.append(buffer.data(),static_cast<std::size_t>(n));}
    const auto after=inspect(f.fd,false,maximum);
    need(before.st_dev==after.st_dev&&before.st_ino==after.st_ino&&before.st_size==after.st_size&&
        before.st_mtim.tv_sec==after.st_mtim.tv_sec&&before.st_mtim.tv_nsec==after.st_mtim.tv_nsec&&
        before.st_ctim.tv_sec==after.st_ctim.tv_sec&&before.st_ctim.tv_nsec==after.st_ctim.tv_nsec&&
        bytes.size()==static_cast<std::uint64_t>(before.st_size),"content.changed");return bytes;
}
void walk(int fd,const std::string& prefix,const std::map<std::string,std::size_t>& expected,
    const std::set<std::string>& directories,std::map<std::string,std::string>& assets){
    File listing(::openat(fd,".",O_RDONLY|O_DIRECTORY|O_CLOEXEC));need(listing.fd>=0,"content.directory");
    DIR* raw=::fdopendir(listing.fd);need(raw!=nullptr,"content.directory");listing.fd=-1;
    std::unique_ptr<DIR,int(*)(DIR*)> dir(raw,::closedir);std::size_t entries=0;
    for(;;){errno=0;const auto* ent=::readdir(dir.get());if(!ent){need(errno==0,"content.directory");break;}
        const std::string name=ent->d_name;if(name=="."||name=="..")continue;need(++entries<=4097,"content.capacity");
        if(prefix.empty()&&name=="manifest.json")continue;
        const auto path=prefix+name;const auto found=expected.find(path);
        if(found!=expected.end())need(assets.emplace(path,read(fd,name,found->second)).second,"content.assets");
        else {need(directories.count(path)!=0,"content.undeclared");File child(::openat(fd,name.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));
            (void)inspect(child.fd,true,0);walk(child.fd,path+"/",expected,directories,assets);}
    }
}
}
std::vector<c::ContentPackage> read_content_packages(const std::vector<std::string>& paths){
    need(!paths.empty()&&paths.size()<=64,"content.capacity");std::size_t count=0,total=0;std::vector<c::ContentPackage> result;
    for(const auto& path:paths){auto dir=root(path);c::ContentPackage bytes;bytes.manifest=read(dir.fd,"manifest.json",65536);
        const auto manifest=c::validate_content_manifest(bytes.manifest);std::map<std::string,std::size_t> expected;std::set<std::string> directories;
        for(const auto& asset:manifest["assets"]){const auto name=asset["path"].get<std::string>();const auto size=asset["bytes"].get<std::size_t>();
            total+=size;need(++count<=1024&&total<=67108864,"content.capacity");
            need(asset["media_type"]!="application/json"||size<=262144,"content.size");expected.emplace(name,size);
            for(auto slash=name.find('/');slash!=std::string::npos;slash=name.find('/',slash+1))directories.insert(name.substr(0,slash));}
        walk(dir.fd,"",expected,directories,bytes.assets);need(bytes.assets.size()==expected.size(),"content.assets");result.push_back(std::move(bytes));
    }
    return result;
}
}
