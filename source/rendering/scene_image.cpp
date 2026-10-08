#include "scene_image.hpp"
#include "digest.hpp"
#include "child.hpp"
#include <algorithm>
#include <array>
#include <cmath>
namespace syspane::rendering {
namespace {
using configuration::Json;namespace c=configuration;
void need(bool b,const char* why){if(!b)throw protocol::Error(why);}
std::uint64_t extent(const Json& value,unsigned numerator,unsigned denominator){
    const auto dip=value.get<double>();need(std::isfinite(dip)&&dip>=1&&dip<=4096&&numerator>=1&&numerator<=16&&denominator>=1&&denominator<=16,"surface.capacity");
    int exponent=0;const auto fraction=std::frexp(dip,&exponent);
    const auto top=static_cast<std::uint64_t>(std::ldexp(fraction,53))*numerator;
    const auto bottom=(std::uint64_t{1}<<(53-exponent))*denominator;
    return (top+bottom-1)/bottom;
}
std::array<unsigned char,4> color(const std::string& token){std::array<unsigned char,4> out{};for(unsigned i=0;i<4;++i)out[i]=static_cast<unsigned char>(std::stoul(token.substr(1+i*2,2),nullptr,16));
    for(unsigned i=0;i<3;++i)out[i]=static_cast<unsigned char>((out[i]*out[3]+127)/255);
    return out;}
}
void SceneImages::clear(std::string blocked_reason){
    entries_.clear();resources_.reset();pixels_=0;prepared_=false;blocked_reason_=std::move(blocked_reason);active_.clear();
    if(job_&&valid_job_)job_->cancel();
    valid_job_=false;
}
bool SceneImages::poll(){
    if(!job_)return true;
    const auto status=job_->poll();if(!status.reaped)return false;
    if(valid_job_){auto& entry=entries_.at(active_);
        if(status.state==ImageJobState::ready){auto image=job_->take();const auto count=static_cast<std::size_t>(image.width)*image.height;
            if(count>4194304-pixels_){job_.reset();valid_job_=false;clear("surface.capacity");throw protocol::Error("surface.capacity");}
            pixels_+=count;entry.pixels=std::move(image);entry.state="ready";
        }else{entry.state="failed";entry.reason=status.reason;}
    }
    job_.reset();active_.clear();valid_job_=false;return true;
}
void SceneImages::prepare(const SurfaceConfig& cfg){
    if(!blocked_reason_.empty())throw protocol::Error(blocked_reason_.c_str());
    if(!prepared_){
        std::map<std::string,std::pair<Json,std::shared_ptr<const c::ContentPackage>>> packages;
        for(const auto& bytes:cfg.resources->packages()){auto m=c::parse_content_json(bytes->manifest,65536);Json pin={{"id",m["package_id"]},{"version",m["version"]},{"sha256",c::sha256(bytes->manifest)}};
            packages.emplace(pin.dump(),std::make_pair(std::move(m),bytes));}
        std::size_t count=0,encoded=0;std::map<std::string,Entry> next;
        for(const auto& w:cfg.authored.scene["widgets"])if(w["kind"]=="image"){
            need(w.contains("content")&&factory_,"surface.unsupported");need(++count<=32,"surface.capacity");
            const auto& ref=w["content"]["asset"];const auto key=ref.dump();if(next.count(key))continue;
            const auto found=packages.find(ref["package"].dump());need(found!=packages.end(),"content.asset");
            const auto& pack=found->second;Entry entry;
            for(const auto& a:pack.first["assets"])if(a["path"]==ref["path"]&&a["sha256"]==ref["sha256"]){entry.media=a["media_type"];entry.encoded=&pack.second->assets.at(a["path"].get<std::string>());}
            need(entry.encoded&&(entry.media=="image/png"||entry.media=="image/jpeg"||entry.media=="image/svg+xml"),"content.asset");
            encoded+=entry.encoded->size();need(encoded<=33554432&&next.size()<32,"surface.capacity");next.emplace(key,std::move(entry));
        }
        resources_=cfg.resources;entries_=std::move(next);prepared_=true;
    }
    poll();if(job_)return;
    for(auto& pair:entries_)if(pair.second.state=="loading"){
        try{job_=factory_(pair.second.media,*pair.second.encoded);need(static_cast<bool>(job_),"image.startup");active_=pair.first;valid_job_=true;}
        catch(const platform::ChildError&){pair.second.state="failed";pair.second.reason="image.startup";}
        catch(const protocol::Error& e){pair.second.state="failed";pair.second.reason=e.what();}
        break;
    }
}
TextRaster SceneImages::raster(const Json& w,const TextRequest& request,SurfaceText& out){
    const auto& content=w["content"];const auto& e=entries_.at(content["asset"].dump());
    out.id=w["id"];out.kind="image";out.image.emplace();out.image->state=e.state;out.image->asset=content["asset"];out.image->width=e.pixels.width;out.image->height=e.pixels.height;
    out.accessible=content["alt"].get<std::string>()+"\nImage "+(e.state=="loading"?"loading":e.state=="ready"?"ready":"failed ("+e.reason+")");
    if(e.state!="ready")out.notices.push_back(e.state=="loading"?"Image loading":"Image failed");
    const auto width=extent(content["width_dip"],request.numerator,request.denominator);
    const auto height=extent(content["height_dip"],request.numerator,request.denominator);
    need(width&&height&&width<=2048&&height<=2048&&width*height<=request.pixel_budget,"surface.capacity");
    TextRaster raster;raster.width=static_cast<unsigned>(width);raster.height=static_cast<unsigned>(height);
    if(e.state=="ready"){const std::string mode=content["fit"];auto image=scene::fit_image(e.pixels,raster.width,raster.height,mode=="contain"?scene::ImageFit::contain:mode=="cover"?scene::ImageFit::cover:scene::ImageFit::stretch,request.pixel_budget);raster.rgba=std::move(image.rgba);}
    else{
        raster.rgba.resize(static_cast<std::size_t>(width*height*4));const auto c=color(request.contrast=="light"?"#000000ff":request.contrast=="dark"?"#ffffffff":request.theme["tokens"][e.state=="loading"?"muted":"error"].get<std::string>());
        const auto mark=[&](unsigned x,unsigned y){std::copy(c.begin(),c.end(),raster.rgba.begin()+(static_cast<std::size_t>(y)*raster.width+x)*4);};
        for(unsigned x=0;x<width;++x){mark(x,0);mark(x,raster.height-1);}for(unsigned y=0;y<height;++y){mark(0,y);mark(raster.width-1,y);}
        if(e.state=="failed"){const auto n=std::max(width-1,height-1);for(std::uint64_t i=0;i<=n;++i){const auto x=n?((width-1)*i*2+n)/(n*2):0,y=n?((height-1)*i*2+n)/(n*2):0,reverse=n?((width-1)*(n-i)*2+n)/(n*2):0;mark(static_cast<unsigned>(x),static_cast<unsigned>(y));mark(static_cast<unsigned>(reverse),static_cast<unsigned>(y));}}
    }
    return raster;
}
}
