#pragma once
#include "image.hpp"
#include <memory>
#include <functional>
#include <string>
namespace syspane::platform {class LinuxInstallation;}
namespace syspane::rendering {
enum class ImageJobState { running,stopping,ready,failed,cancelled,consumed };
struct ImageJobStatus {ImageJobState state=ImageJobState::running;std::string reason;bool reaped=false;};
class ImageTask {
public:
    virtual ~ImageTask()=default;
    virtual ImageJobStatus poll()=0;
    virtual void cancel()=0;
    virtual scene::Image take()=0;
    virtual std::uint64_t process_id()const=0;
};
using ImageFactory=std::function<std::unique_ptr<ImageTask>(std::string media,std::string encoded)>;
// Single owner, Linux only. No callback, background thread or unbounded wait in
// poll/cancel. Caller separately binds immutable input and results to authority.
class ImageJob final:public ImageTask {
public:
    ImageJob(const std::string& worker,std::string media,std::string encoded);
    // Verified mode belongs to the installation's native worker, never GTK.
    // Revalidates the whole bundle; no pathname fallback on refusal.
    ImageJob(std::shared_ptr<platform::LinuxInstallation>,std::string media,std::string encoded);
    ~ImageJob() override;
    ImageJob(const ImageJob&)=delete;ImageJob& operator=(const ImageJob&)=delete;
    ImageJobStatus poll() override;
    void cancel() override;
    scene::Image take() override;
    std::uint64_t process_id()const override;
    const std::string& input_sha256()const;
private:
    ImageJob(const std::string&,std::string,std::string,std::shared_ptr<platform::LinuxInstallation>);
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
