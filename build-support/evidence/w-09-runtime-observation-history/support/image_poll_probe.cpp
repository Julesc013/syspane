#include "image_job.hpp"
#include "image.hpp"
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <thread>
using Clock=std::chrono::steady_clock;
using Json=syspane::protocol::Json;
namespace r=syspane::rendering;namespace s=syspane::scene;
double ms(Clock::time_point t){return std::chrono::duration<double,std::milli>(Clock::now()-t).count();}
void need(bool ok){if(!ok)throw std::runtime_error("diagnostic invariant");}
int main(int argc,char** argv){try{
 need(argc==3);std::ifstream file(argv[2],std::ios::binary);need(bool(file));const std::string encoded{std::istreambuf_iterator<char>(file),{}};
 Json report=Json::array();
 for(unsigned trial=0;trial<3;++trial){
  r::ImageJob job(argv[1],"image/png",encoded);const auto deadline=Clock::now()+std::chrono::seconds(5);Json times=Json::array();r::ImageJobStatus status;
  do{const auto begin=Clock::now();status=job.poll();times.push_back({{"ms",ms(begin)},{"state",static_cast<int>(status.state)},{"reaped",status.reaped}});need(Clock::now()<deadline);if(!status.reaped)std::this_thread::sleep_for(std::chrono::milliseconds(1));}while(!status.reaped);
  need(status.state==r::ImageJobState::ready);auto image=job.take();need(image.width==2048&&image.height==2048&&image.rgba.size()==16777216&&std::all_of(image.rgba.begin(),image.rgba.end(),[](auto v){return v==0;}));
  auto begin=Clock::now();s::validate_image(image);const auto validate_ms=ms(begin);
  begin=Clock::now();auto raster=s::fit_image(image,32,16,s::ImageFit::contain);const auto fit_ms=ms(begin);need(raster.width==32&&raster.height==16&&raster.rgba.size()==2048&&std::all_of(raster.rgba.begin(),raster.rgba.end(),[](auto v){return v==0;}));
  report.push_back({{"trial",trial},{"polls",times},{"validate_ms",validate_ms},{"fit_ms",fit_ms},{"exact_pixels",true}});
 }
 std::cout<<report.dump(2)<<'\n';return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
