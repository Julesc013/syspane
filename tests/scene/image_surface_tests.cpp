#include "image_fixture.hpp"
#include "child.hpp"
#include <chrono>
#include <csignal>
#include <cmath>
#include <iostream>
#include <thread>
using namespace fixture;
namespace {
using Clock=std::chrono::steady_clock;
struct Images {
    v::SurfaceConfig cfg;std::unique_ptr<v::SceneSurface> owner;std::uint64_t now=0;bool clear_ok=true;
    explicit Images(const std::string& root,std::string bytes={},std::string media="image/png",std::string worker={}):cfg(image_config(root,bytes,media)){
        owner=std::make_unique<v::SceneSurface>(c::Authority{true,"desktop",{"desktop"}},chart_policy(),cfg,std::vector<v::SurfaceProvider>{provider()},[&]{return clear_ok;},worker.empty()?image_worker_path():worker);}
    ~Images(){owner->close();const auto deadline=Clock::now()+std::chrono::seconds(4);while(!owner->poll_image_jobs()&&Clock::now()<deadline)std::this_thread::sleep_for(std::chrono::milliseconds(1));}
    v::SurfaceFrame paint(){v::SurfaceFrame frame;const auto before=Clock::now();owner->paint(++now,{{"P1",tick()}},[&](auto code,const auto* f){need((code==v::SurfaceCode::ready||code==v::SurfaceCode::degraded)&&f,"image publication");frame=*f;});need(Clock::now()-before<std::chrono::milliseconds(100),"scene paint waited for decoder");return frame;}
    v::SurfaceFrame settled(){const auto deadline=Clock::now()+std::chrono::seconds(4);for(;;){auto frame=paint();bool pending=false;for(const auto& w:frame.widgets)if(w.image&&w.image->state=="loading")pending=true;if(!pending)return frame;need(Clock::now()<deadline,"image settle deadline");std::this_thread::sleep_for(std::chrono::milliseconds(1));}}
    void replace(v::SurfaceConfig next){cfg=next;owner->replace(std::move(next),++now);}
    void empty(v::SurfaceCode expected){owner->paint(++now,{},[&](auto code,const auto* f){need(code==expected&&!f,"image erased publication");});}
};
std::string self(){std::array<char,4096> b{};const auto n=::readlink("/proc/self/exe",b.data(),b.size()-1);need(n>0,"mock self");return {b.data(),static_cast<std::size_t>(n)};}
std::vector<unsigned> children(){std::ifstream f("/proc/self/task/"+std::to_string(::getpid())+"/children");std::vector<unsigned> result;unsigned pid;while(f>>pid)result.push_back(pid);return result;}
void extra(v::SurfaceConfig& cfg,const std::string& bytes,unsigned index){
    std::vector<c::ContentPackage> packages;for(const auto& p:cfg.resources->packages())packages.push_back(*p);
    auto theme=std::find_if(packages.begin(),packages.end(),[](const auto& p){return Json::parse(p.manifest)["kind"]=="theme";});need(theme!=packages.end(),"extra theme");const auto old=package_pin(*theme);
    const auto path="second"+std::to_string(index)+".data";theme->assets[path]=bytes;auto m=Json::parse(theme->manifest);m["assets"].push_back({{"path",path},{"media_type","image/png"},{"bytes",bytes.size()},{"sha256",c::content_sha256(bytes)}});m["total_unpacked_bytes"]=m["total_unpacked_bytes"].get<std::size_t>()+bytes.size();theme->manifest=m.dump()+"\n";const auto pin=package_pin(*theme);
    for(auto& w:cfg.authored.scene["widgets"])if(w["kind"]=="image")w["content"]["asset"]["package"]=pin;
    auto w=cfg.authored.scene["widgets"][0];w["id"]="extra:"+std::to_string(index);w["layout"]["base"]["x"]=40*index;w["content"]["asset"]={{"package",pin},{"path",path},{"sha256",c::content_sha256(bytes)}};cfg.authored.scene["widgets"].push_back(w);cfg.authored.scene["roots"].push_back(w["id"]);
    auto selection=cfg.resources->selection();for(auto& p:packages){auto manifest=Json::parse(p.manifest);if(manifest["kind"]!="preset")continue;for(auto& dependency:manifest["dependencies"])if(dependency==old)dependency=pin;p.manifest=manifest.dump()+"\n";selection["package"]=package_pin(p);}
    cfg.resources=c::ContentCatalog(std::move(packages)).resources(selection,cfg.authored);
}
}
int image_surface_mock(const char* parent){syspane::platform::arm_parent_lifetime(std::stoull(parent));::close(3);::alarm(5);char header[4];std::cin.read(header,4);std::string bytes{std::istreambuf_iterator<char>(std::cin),{}};
    if(bytes=="stall")for(;;)::pause();
    if(bytes=="fail")return 17;
    if(bytes=="delayed")std::this_thread::sleep_for(std::chrono::milliseconds(20));
    if(bytes=="green"){std::cout.write("SPIM0001\0\0\0\x01\0\0\0\x01\0\xff\0\xff",20);return 0;}
    std::cout.write("SPIM0001\0\0\0\x01\0\0\0\x01\xff\0\0\xff",20);return 0;
}
int image_surface_tests(const std::string& root){unsigned count=0;const auto test=[&](const char* name,const std::function<void()>& f){f();++count;std::cout<<name<<" pass\n";};
    test("FIXED-FIT",[&]{const auto cases=read(root+"/../../../tests/scene/image-cases","surface.json");for(const auto& expected:cases){Images f(root);auto cfg=f.cfg;auto& w=cfg.authored.scene["widgets"][0];w["content"]["fit"]=expected["fit"];cfg.topology.displays[0].scale_numerator=expected["width"]==18?2:1;f.replace(cfg);
        const auto frame=f.settled();const auto& image=frame.widgets[0];need(image.image&&image.image->state=="ready"&&image.image->width==2&&image.image->height==2,"decoded source dimensions");need(image.accessible=="Public image\nImage ready","ready alt exact");need(image.image->asset==w["content"]["asset"],"exact asset result identity");
        const unsigned width=expected["width"],height=expected["height"];need(frame.layout.nodes[0].pixels.width==32*cfg.topology.displays[0].scale_numerator&&frame.layout.nodes[0].pixels.height==16*cfg.topology.displays[0].scale_numerator,"authored fixed box stays separate from raster");
        for(unsigned y=0;y<height;++y)for(unsigned x=0;x<width;++x)for(unsigned c=0;c<4;++c)need(frame.displays[0].rgba[(y*frame.displays[0].width+x)*4+c]==expected["rgba"][(y*width+x)*4+c],"independent image pixels");
    }});
    test("FRACTIONAL-EXTENT",[&]{Images f(root);auto cfg=f.cfg;cfg.authored.scene["widgets"][0]["content"]["width_dip"]=std::nextafter(1.5,2.0);cfg.authored.scene["widgets"][0]["content"]["height_dip"]=1.25;cfg.topology.displays[0].scale_numerator=2;f.replace(cfg);auto frame=f.paint();const auto& rgba=frame.displays[0].rgba;need(rgba[(2*1600+3)*4+3]!=0&&rgba[4*4+3]==0&&rgba[(3*1600)*4+3]==0,"exact binary64 extent ceil without truncation");});
    test("PENDING-REPLACE",[&]{Images f(root,"stall","image/png",self());auto pending=f.paint();need(pending.widgets[0].image->state=="loading"&&f.owner->status().code==v::SurfaceCode::degraded,"pending explicit");const auto old=children();need(old.size()==1,"one native job");
        f.replace(image_config(root,"solid"));const auto frame=f.settled();need(frame.widgets[0].image->state=="ready"&&frame.widgets[0].image->width==1,"successor content only");need(children().empty(),"successor and cancelled child reaped");need(::kill(static_cast<pid_t>(old[0]),0)<0&&errno==ESRCH,"old job cannot complete late");});
    test("FAILURE-LATCH",[&]{Images f(root,"fail","image/png",self());const auto frame=f.settled();need(frame.widgets[0].accessible=="Public image\nImage failed (image.decode)","failed alt exact");for(unsigned n=0;n<5;++n){f.paint();need(children().empty(),"failure cannot retry");}
        f.replace(image_config(root,"solid"));need(f.settled().widgets[0].image->state=="ready","replacement retries explicitly");});
    test("UNOBSERVED-COMPLETION",[&]{Images f(root,"delayed","image/png",self());f.paint();need(f.paint().widgets[0].image->state=="loading","request sent before delayed completion");need(children().size()==1,"unobserved worker");const auto pid=children()[0];const auto deadline=Clock::now()+std::chrono::seconds(2);bool exited=false;
        while(!exited){std::ifstream file("/proc/"+std::to_string(pid)+"/stat");std::string line;std::getline(file,line);const auto at=line.rfind(')');exited=at!=std::string::npos&&line.substr(at+2,1)=="Z";need(Clock::now()<deadline,"worker completion observed externally");if(!exited)std::this_thread::sleep_for(std::chrono::milliseconds(1));}
        f.replace(image_config(root,"green"));auto frame=f.settled();const auto& rgba=frame.displays[0].rgba;need(rgba[2*4]==0&&rgba[2*4+1]==255&&frame.widgets[0].image->asset==f.cfg.authored.scene["widgets"][0]["content"]["asset"],"unobserved old result cannot enter replacement");});
    test("POLICY",[&]{for(const std::string channel:{"desktop","accessibility","resource"}){Images f(root);f.settled();auto p=policy(8);if(channel=="resource")p.denied_capabilities.insert("scene.content");else p.disclosure.erase({"desktop",channel});f.owner->policy(p,++f.now);f.empty(v::SurfaceCode::restricted);
        f.owner->policy(policy(9),++f.now);need(f.paint().widgets[0].image->state=="loading","regrant needs fresh decode");need(f.settled().widgets[0].image->state=="ready","authorized regrant");}});
    test("CANCEL-CLOSE",[&]{Images f(root,"stall","image/png",self());f.paint();f.owner->close();const auto deadline=Clock::now()+std::chrono::seconds(2);while(!f.owner->poll_image_jobs()){need(Clock::now()<deadline,"close reap deadline");std::this_thread::sleep_for(std::chrono::milliseconds(1));}need(children().empty(),"closed child reaped");f.empty(v::SurfaceCode::closed);});
    test("PENDING-DENIAL",[&]{Images f(root,"stall","image/png",self());f.paint();f.owner->policy(policy(8,false),++f.now);f.empty(v::SurfaceCode::restricted);const auto deadline=Clock::now()+std::chrono::seconds(2);while(!f.owner->poll_image_jobs()){need(Clock::now()<deadline,"denial reap");std::this_thread::sleep_for(std::chrono::milliseconds(1));}need(children().empty(),"denied worker gone");f.owner->policy(policy(9),++f.now);need(f.paint().widgets[0].image->state=="loading"&&children().size()==1,"regrant starts new owned job");});
    test("CLEAR-FAILURE",[&]{Images f(root,"stall","image/png",self());f.paint();f.clear_ok=false;f.owner->policy(policy(8,false),++f.now);f.empty(v::SurfaceCode::closed);});
    test("DISABLED",[&]{Images f(root);f.settled();auto cfg=f.cfg;cfg.authored.settings["display"]["enabled"]=false;f.replace(cfg);f.empty(v::SurfaceCode::empty);cfg.authored.settings["display"]["enabled"]=true;f.replace(cfg);need(f.paint().widgets[0].image->state=="loading","enable cannot resurrect cache");});
    test("RESOURCE-IDENTITY",[&]{for(const char* key:{"sha256","path"}){Images f(root);f.settled();auto cfg=f.cfg;cfg.authored.scene["widgets"][0]["content"]["asset"][key]=std::string(key)=="sha256"?std::string(64,'0'):"other.png";bool rejected=false;try{f.owner->replace(cfg,++f.now);}catch(const p::Error& e){rejected=std::string(e.what())=="content.asset";}need(rejected,"exact immutable resource");need(f.paint().widgets[0].image->state=="loading","invalid replace erased old cache");}});
    test("SHARED-AND-COUNT",[&]{Images f(root);auto cfg=f.cfg;auto w=cfg.authored.scene["widgets"][0];for(unsigned n=1;n<32;++n){w["id"]="image:"+std::to_string(n);w["layout"]["base"]["x"]=n*10;cfg.authored.scene["widgets"].push_back(w);cfg.authored.scene["roots"].push_back(w["id"]);}f.replace(cfg);auto pending=f.paint();need(children().size()==1&&pending.widgets.size()==32,"shared one decode");need(f.settled().widgets.size()==32,"shared ready rasters");w["id"]="excess";cfg.authored.scene["widgets"].push_back(w);cfg.authored.scene["roots"].push_back("excess");f.replace(cfg);f.empty(v::SurfaceCode::alternative);});
    test("ENCODED-BUDGET",[&]{Images f(root);auto cfg=image_config(root,std::string(8388608,'a'));for(unsigned n=1;n<=4;++n)extra(cfg,std::string(n==4?1:8388608,static_cast<char>('a'+n)),n);f.replace(cfg);f.empty(v::SurfaceCode::alternative);need(f.owner->status().reason=="surface.capacity"&&children().empty(),"aggregate encoded admission before spawn");});
    test("DECODED-BUDGET",[&]{std::ifstream file(root+"/../../../tests/scene/image-cases/maximum.png",std::ios::binary);const std::string bytes{std::istreambuf_iterator<char>(file),{}};Images f(root,bytes);auto cfg=f.cfg;extra(cfg,image_bytes(root),1);f.replace(cfg);const auto deadline=Clock::now()+std::chrono::seconds(5);bool refused=false;
        while(!refused){f.owner->paint(++f.now,{},[&](auto code,const auto* frame){if(code==v::SurfaceCode::alternative){need(!frame,"capacity no partial scene");refused=true;}else need(frame&&code==v::SurfaceCode::degraded,"bounded cache pending");});need(Clock::now()<deadline,"cache budget deadline");std::this_thread::sleep_for(std::chrono::milliseconds(1));}
        need(f.owner->status().reason=="surface.capacity"&&children().empty(),"decoded budget and actual reaping");f.empty(v::SurfaceCode::alternative);need(children().empty(),"capacity cannot retry storm");});
    test("CAPACITY-CLEAR-FAILURE",[&]{std::ifstream file(root+"/../../../tests/scene/image-cases/maximum.png",std::ios::binary);const std::string bytes{std::istreambuf_iterator<char>(file),{}};Images f(root,bytes);auto cfg=f.cfg;extra(cfg,image_bytes(root),1);f.replace(cfg);const auto deadline=Clock::now()+std::chrono::seconds(5);bool first=false;
        while(!first){auto frame=f.paint();first=frame.widgets[0].image->state=="ready";need(frame.widgets[1].image->state=="loading","second job pending");need(Clock::now()<deadline,"first cache deadline");if(!first)std::this_thread::sleep_for(std::chrono::milliseconds(1));}
        f.clear_ok=false;while(!f.owner->poll_image_jobs()){need(Clock::now()<deadline,"capacity clearing deadline");std::this_thread::sleep_for(std::chrono::milliseconds(1));}
        need(f.owner->status().code==v::SurfaceCode::closed&&children().empty(),"native clear failure stays terminal after capacity error");f.empty(v::SurfaceCode::closed);});
    test("PENDING-CHART",[&]{Images f(root,"stall","image/png",self());auto cfg=f.cfg;auto chart=chart_config(root).authored.scene["widgets"][0];chart["id"]="chart";cfg.authored.scene["widgets"][0]["layout"]["base"]["y"]=500;cfg.authored.scene["widgets"].push_back(chart);cfg.authored.scene["roots"].push_back("chart");f.replace(cfg);const auto token=f.owner->attach("P1",link(),++f.now).token;
        for(unsigned n=1;n<=3;++n){need(f.owner->receive("P1",token,7,wire(chart_document(10*n,n,n*100),link()),++f.now,tick(n*100)).code==r::DataCode::accepted,"image mixed chart delivery");f.owner->paint(++f.now,{{"P1",tick(n*100)}},[&](auto code,const auto* frame){need(code==v::SurfaceCode::degraded&&frame&&frame->widgets[1].chart->samples==n,"pending preserves every chart sample");});}});
    std::cout<<"IMAGE-SURFACE-FAMILIES "<<count<<'\n';return 0;
}
