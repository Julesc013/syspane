#pragma once
#include "scene_surface.hpp"
#include "image_job.hpp"
namespace syspane::rendering {
// Private scene owner. Caller authorizes the entire current resource/scene first.
class SceneImages {
public:
    explicit SceneImages(std::string worker){if(!worker.empty())factory_=[path=std::move(worker)](std::string media,std::string bytes){return std::make_unique<ImageJob>(path,std::move(media),std::move(bytes));};}
    explicit SceneImages(ImageFactory factory):factory_(std::move(factory)){}
    void clear(std::string blocked_reason={});
    bool poll();
    void prepare(const SurfaceConfig&);
    TextRaster raster(const configuration::Json&,const TextRequest&,SurfaceText&);
private:
    struct Entry {std::string media;const std::string* encoded=nullptr;scene::Image pixels;std::string state="loading",reason;};
    ImageFactory factory_;std::string active_;std::unique_ptr<ImageTask> job_;
    configuration::ResourceSnapshot resources_;std::map<std::string,Entry> entries_;
    std::size_t pixels_=0;bool prepared_=false,valid_job_=false;std::string blocked_reason_;
};
}
