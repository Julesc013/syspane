#pragma once
#include "image.hpp"
#include <memory>
#include <string>
namespace syspane::rendering {
enum class ImageJobState { running,stopping,ready,failed,cancelled,consumed };
struct ImageJobStatus {ImageJobState state=ImageJobState::running;std::string reason;bool reaped=false;};
// Single owner, Linux only. No callback, background thread or unbounded wait in
// poll/cancel. Caller separately binds immutable input and results to authority.
class ImageJob {
public:
    ImageJob(const std::string& worker,std::string media,std::string encoded);
    ~ImageJob();
    ImageJob(const ImageJob&)=delete;ImageJob& operator=(const ImageJob&)=delete;
    ImageJobStatus poll();
    void cancel();
    scene::Image take();
    std::uint64_t process_id()const;
    const std::string& input_sha256()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
