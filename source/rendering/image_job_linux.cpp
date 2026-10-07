#include "image_job.hpp"
#include "child.hpp"
#include "digest.hpp"
#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>
namespace syspane::rendering {
namespace {
using Clock=std::chrono::steady_clock;
void need(bool b,const char* why){if(!b)throw protocol::Error(why);}
struct Fd{int fd=-1;~Fd(){close();}void close(){if(fd>=0)::close(fd);fd=-1;}};
unsigned word(const unsigned char* b){return (static_cast<unsigned>(b[0])<<24)|(static_cast<unsigned>(b[1])<<16)|(static_cast<unsigned>(b[2])<<8)|b[3];}
}
struct ImageJob::Impl {
    Fd channel,error;std::unique_ptr<platform::Child> child;ImageJobStatus status;Clock::time_point started;
    std::string digest,input,errors;std::size_t sent=0,expected=16;bool eof=false,error_eof=false,shutdown=false,cancelled=false;
    std::vector<unsigned char> output;scene::Image result;
    void stop(const char* reason){if(status.reaped)return;status.state=ImageJobState::stopping;status.reason=reason;input.clear();output.clear();errors.clear();result={};channel.close();error.close();child->request_stop();}
};
ImageJob::ImageJob(const std::string& worker,std::string media,std::string encoded):impl_(std::make_unique<Impl>()){
    need(media=="image/png"||media=="image/jpeg"||media=="image/svg+xml","image.media");need(!encoded.empty()&&encoded.size()<=8388608,"image.capacity");
    auto& i=*impl_;i.digest=configuration::sha256(encoded);const auto size=static_cast<unsigned>(encoded.size());
    i.input.resize(4);for(unsigned n=0;n<4;++n)i.input[n]=static_cast<char>(size>>(24-n*8));i.input+=encoded;
    int socket[2],errors[2];need(!::socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0,socket),"image.channel");Fd remote;remote.fd=socket[1];i.channel.fd=socket[0];
    need(!::pipe2(errors,O_CLOEXEC),"image.channel");Fd remote_error;remote_error.fd=errors[1];i.error.fd=errors[0];
    need(!::fcntl(i.channel.fd,F_SETFL,O_NONBLOCK)&&!::fcntl(i.error.fd,F_SETFL,O_NONBLOCK),"image.channel");
    i.started=Clock::now();i.child=std::make_unique<platform::Child>(platform::Child::launch_program(worker,{media,std::to_string(platform::current_process_id())},remote.fd,remote.fd,remote_error.fd));
}
ImageJob::~ImageJob()=default;
ImageJobStatus ImageJob::poll(){auto& i=*impl_;
    if(i.status.reaped)return i.status;
    try{
        if(i.status.state==ImageJobState::running){
            if(Clock::now()-i.started>=std::chrono::seconds(3))i.stop("image.timeout");
            else{
                if(i.sent<i.input.size()){const auto count=::send(i.channel.fd,i.input.data()+i.sent,std::min(std::size_t{262144},i.input.size()-i.sent),MSG_NOSIGNAL);
                    if(count>0)i.sent+=static_cast<std::size_t>(count);else if(count<0&&errno!=EAGAIN&&errno!=EWOULDBLOCK&&errno!=EINTR)i.stop("image.channel");}
                if(i.status.state==ImageJobState::running&&!i.shutdown&&i.sent==i.input.size()){need(!::shutdown(i.channel.fd,SHUT_WR),"image.channel");i.shutdown=true;i.input.clear();}
                std::size_t received=0;std::array<unsigned char,8192> bytes{};
                while(i.status.state==ImageJobState::running&&!i.eof&&received<262144){const auto count=::recv(i.channel.fd,bytes.data(),std::min(bytes.size(),std::size_t{262144}-received),0);
                    if(count==0){i.eof=true;break;}if(count<0){if(errno==EAGAIN||errno==EWOULDBLOCK||errno==EINTR)break;i.stop("image.channel");break;}
                    const auto n=static_cast<std::size_t>(count);received+=n;
                    if(i.output.size()+n>16777232){i.stop("image.reply_limit");break;}i.output.insert(i.output.end(),bytes.begin(),bytes.begin()+n);
                    if(i.output.size()>=16&&i.expected==16){if(std::memcmp(i.output.data(),"SPIM0001",8)){i.stop("image.reply");break;}
                        const auto w=word(i.output.data()+8),h=word(i.output.data()+12);if(!w||!h||w>4096||h>4096||static_cast<std::uint64_t>(w)*h>4194304){i.stop("image.reply_limit");break;}
                        i.result.width=w;i.result.height=h;i.expected=16+static_cast<std::size_t>(w)*h*4;}
                    if(i.output.size()>i.expected&&i.expected!=16){i.stop("image.reply");break;}
                }
                if(i.status.state==ImageJobState::running&&!i.error_eof){const auto count=::read(i.error.fd,bytes.data(),1025);
                    if(count==0)i.error_eof=true;else if(count>0){if(i.errors.size()+static_cast<std::size_t>(count)>1024)i.stop("image.error_limit");else i.errors.append(reinterpret_cast<const char*>(bytes.data()),count);}
                    else if(errno!=EAGAIN&&errno!=EWOULDBLOCK&&errno!=EINTR)i.stop("image.channel");}
            }
        }
        const auto exit=i.child->wait();if(!exit)return i.status;
        // Successful output is accepted only after both pipe EOFs are consumed.
        // A reaped child may still have bounded unread kernel pipe data.
        if(i.status.state==ImageJobState::running&&!i.eof&&!exit->signaled&&exit->code==0)return i.status;
        if(i.status.state==ImageJobState::running&&!i.error_eof&&!exit->signaled&&exit->code==0)return i.status;
        i.status.reaped=true;i.channel.close();i.error.close();i.input.clear();
        if(i.cancelled){i.status.state=ImageJobState::cancelled;return i.status;}
        if(i.status.state==ImageJobState::stopping){i.status.state=ImageJobState::failed;return i.status;}
        if(exit->signaled||exit->code){i.output.clear();i.result={};i.status.state=ImageJobState::failed;i.status.reason=exit->signaled?"image.signal":"image.decode";return i.status;}
        if(!i.shutdown||i.output.size()!=i.expected||i.expected==16){i.output.clear();i.result={};i.status.state=ImageJobState::failed;i.status.reason="image.reply";return i.status;}
        i.result.rgba.assign(i.output.begin()+16,i.output.end());i.output.clear();scene::validate_image(i.result);i.status.state=ImageJobState::ready;return i.status;
    }catch(const protocol::Error& e){if(i.status.reaped){i.result={};i.status.state=ImageJobState::failed;i.status.reason=e.what();}else i.stop(e.what());return i.status;}
    catch(const std::bad_alloc&){if(i.status.reaped){i.result={};i.status.state=ImageJobState::failed;i.status.reason="image.capacity";}else i.stop("image.capacity");return i.status;}
}
void ImageJob::cancel(){auto& i=*impl_;i.cancelled=true;i.result={};i.input.clear();i.output.clear();if(i.status.reaped){i.status.state=ImageJobState::cancelled;i.status.reason="image.cancelled";}else i.stop("image.cancelled");}
scene::Image ImageJob::take(){auto& i=*impl_;need(i.status.state==ImageJobState::ready&&i.status.reaped,"image.not_ready");i.status.state=ImageJobState::consumed;return std::move(i.result);}
std::uint64_t ImageJob::process_id()const{return impl_->child->id();}
const std::string& ImageJob::input_sha256()const{return impl_->digest;}
}
