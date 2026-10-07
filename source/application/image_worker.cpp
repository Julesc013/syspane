#include "image_decode.hpp"
#include "child.hpp"
#include <array>
#include <cerrno>
#include <csignal>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <sys/socket.h>
#include <unistd.h>
namespace r=syspane::rendering;
namespace {
void word(unsigned value){const std::array<char,4> bytes{static_cast<char>(value>>24),static_cast<char>(value>>16),static_cast<char>(value>>8),static_cast<char>(value)};std::cout.write(bytes.data(),4);}
void need(bool b,const char* why){if(!b)throw syspane::protocol::Error(why);}
}
int main(int argc,char** argv){try{
    need(argc==3,"image.arguments");const auto parent=std::stoull(argv[2]);syspane::platform::arm_parent_lifetime(parent);::close(3);r::restrict_image_worker();
    if(std::strcmp(argv[1],"--check-sandbox")==0){const int file=::open("/etc/passwd",O_RDONLY);need(file<0&&errno==EACCES,"image.sandbox_read");
        const int network=::socket(AF_INET,SOCK_STREAM,0);need(network<0&&errno==EPERM,"image.sandbox_network");
        need(::kill(::getppid(),0)<0&&errno==EPERM,"image.sandbox_signal");
        const int output=::open("image-denied-output",O_WRONLY|O_CREAT|O_EXCL,0600);need(output<0&&errno==EACCES,"image.sandbox_write");std::cout<<"sandbox.pass\n";return 0;}
    std::array<unsigned char,4> header{};std::cin.read(reinterpret_cast<char*>(header.data()),4);need(std::cin.gcount()==4,"image.input");
    const unsigned size=(static_cast<unsigned>(header[0])<<24)|(static_cast<unsigned>(header[1])<<16)|(static_cast<unsigned>(header[2])<<8)|header[3];need(size&&size<=8388608,"image.capacity");
    std::string bytes(size,'\0');std::cin.read(bytes.data(),size);need(std::cin.gcount()==size&&std::cin.peek()==std::char_traits<char>::eof(),"image.input");
    auto image=r::decode_image(argv[1],bytes);std::cout.write("SPIM0001",8);word(image.width);word(image.height);std::cout.write(reinterpret_cast<const char*>(image.rgba.data()),image.rgba.size());std::cout.flush();need(std::cout.good(),"image.output");return 0;
}catch(const syspane::protocol::Error& e){std::cerr<<e.what()<<'\n';return 2;}catch(const std::bad_alloc&){std::cerr<<"image.capacity\n";return 3;}catch(...){std::cerr<<"image.failure\n";return 4;}}
