#include "image_job.hpp"
#include "child.hpp"
#include "digest.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <csignal>
#include <cstring>
#include <cstdlib>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <thread>
#include <unistd.h>
namespace r=syspane::rendering;namespace p=syspane::platform;
namespace {
void need(bool b,const char* why){if(!b)throw std::runtime_error(why);}
std::string read(const std::string& file){std::ifstream f(file,std::ios::binary);need(f.good(),"fixture missing");return {std::istreambuf_iterator<char>(f),{}};}
r::ImageJobStatus finish(r::ImageJob& job){const auto end=std::chrono::steady_clock::now()+std::chrono::seconds(5);r::ImageJobStatus status;
    do{const auto before=std::chrono::steady_clock::now();status=job.poll();need(std::chrono::steady_clock::now()-before<std::chrono::milliseconds(100),"poll blocked");
        if(status.reaped)return status;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));}while(std::chrono::steady_clock::now()<end);throw std::runtime_error("job did not reap");}
int mock(const char* parent){p::arm_parent_lifetime(std::stoull(parent));::close(3);::alarm(10);std::array<char,4> header{};std::cin.read(header.data(),4);std::string bytes{std::istreambuf_iterator<char>(std::cin),{}};
    if(bytes=="environment"){need(!std::getenv("HOME")&&!std::getenv("PATH")&&!std::getenv("LD_PRELOAD"),"clean child environment");
        for(int fd=3;fd<64;++fd)need(::fcntl(fd,F_GETFD)<0&&errno==EBADF,"inherited descriptor");
        std::cout.write("SPIM0001\0\0\0\x01\0\0\0\x01\x01\x02\x03\x04",20);return 0;}
    if(bytes=="stall"){for(;;)::pause();}
    if(bytes=="signal")::raise(SIGKILL);
    if(bytes=="fail")return 9;
    if(bytes=="header")std::cout<<"XXXXXXXXXXXXXXXX";
    else if(bytes=="large")std::cout.write("SPIM0001\0\0\x10\x01\0\0\0\x01",16);
    else if(bytes=="error")std::cerr<<std::string(2048,'x');
    else if(bytes=="partial")std::cout<<"SPIM0001";
    else if(bytes=="premultiplied")std::cout.write("SPIM0001\0\0\0\x01\0\0\0\x01\xff\0\0\0",20);
    else if(bytes=="extra")std::cout.write("SPIM0001\0\0\0\x01\0\0\0\x01\0\0\0\0X",21);
    return 0;
}
}
int main(int argc,char** argv){try{
    if(argc==3&&std::strcmp(argv[1],"image/png")==0)return mock(argv[2]);
    need(argc==3,"arguments");const std::string worker=argv[1],fixtures=argv[2];const auto png=read(fixtures+"/rgba.png");
    r::ImageJob job(worker,"image/png",png);need(job.input_sha256()==syspane::configuration::sha256(png),"input identity");
    auto status=finish(job);need(status.state==r::ImageJobState::ready&&status.reaped,"real worker ready");auto image=job.take();need(image.width==2&&image.height==2&&image.rgba==std::vector<unsigned char>{255,0,0,255,0,128,0,128,0,0,0,0,255,255,255,255},"real worker pixels");
    bool refused=false;try{job.take();}catch(const syspane::protocol::Error&){refused=true;}need(refused,"second take refused");
    const auto encoded=read(fixtures+"/large-encoded.png");need(encoded.size()>1048576,"large encoded fixture");r::ImageJob large_encoded(worker,"image/png",encoded);status=finish(large_encoded);need(status.state==r::ImageJobState::ready&&large_encoded.input_sha256()==syspane::configuration::content_sha256(encoded),"large input identity");need(large_encoded.take().rgba==image.rgba,"large encoded input retains exact pixels");
    r::ImageJob maximum(worker,"image/png",read(fixtures+"/maximum.png"));status=finish(maximum);need(status.state==r::ImageJobState::ready,"maximum native raster ready");
    image=maximum.take();need(image.width==2048&&image.height==2048&&image.rgba.size()==16777216&&std::all_of(image.rgba.begin(),image.rgba.end(),[](auto v){return v==0;}),"maximum native raster bytes");
    std::array<char,4096> executable{};const auto n=::readlink("/proc/self/exe",executable.data(),executable.size()-1);need(n>0,"self executable");const std::string self(executable.data(),n);
    r::ImageJob clean(self,"image/png","environment");status=finish(clean);need(status.state==r::ImageJobState::ready&&clean.take().rgba==std::vector<unsigned char>{1,2,3,4},"clean launch context");
    refused=false;try{r::ImageJob missing(worker+".absent","image/png",png);}catch(const p::ChildError& e){refused=std::string(e.what())=="child.program_path";}need(refused,"startup failure distinct");
    refused=false;try{r::ImageJob wrong(worker,"application/octet-stream",png);}catch(const syspane::protocol::Error& e){refused=std::string(e.what())=="image.media";}need(refused,"unsupported media before spawn");
    refused=false;try{r::ImageJob large(worker,"image/png",std::string(8388609,'x'));}catch(const syspane::protocol::Error& e){refused=std::string(e.what())=="image.capacity";}need(refused,"encoded bound before spawn");
    for(const char* mode:{"header","large","error","partial","premultiplied","extra","signal","fail","stall"}){
        const auto began=std::chrono::steady_clock::now();r::ImageJob bad(self,"image/png",mode);status=finish(bad);need(status.state==r::ImageJobState::failed&&status.reaped,mode);
        if(std::strcmp(mode,"stall")==0)need(status.reason=="image.timeout"&&std::chrono::steady_clock::now()-began>=std::chrono::seconds(3),"independent owner deadline");
        need(::kill(static_cast<pid_t>(bad.process_id()),0)<0&&errno==ESRCH,"failed child actually gone");
        std::cout<<"IMAGE-JOB "<<mode<<" "<<status.reason<<" reaped\n";
    }
    r::ImageJob cancelled(self,"image/png","stall");cancelled.cancel();status=finish(cancelled);need(status.state==r::ImageJobState::cancelled&&status.reaped,"cancelled child reaped");
    refused=false;try{cancelled.take();}catch(const syspane::protocol::Error&){refused=true;}need(refused,"cancel cannot disclose result");
    r::ImageJob decode(worker,"image/png","invalid");status=finish(decode);need(status.state==r::ImageJobState::failed&&status.reason=="image.decode"&&status.reaped,"decoder failure distinct");
    std::cout<<"IMAGE-JOB pass\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
