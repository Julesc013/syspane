#include "scene_inspector_render.hpp"
#include "scene_inspector_admission.hpp"
#include <glib.h>
#include <condition_variable>
#include <limits>
#include <mutex>
#include <thread>

namespace syspane::interfaces {
namespace r=rendering;namespace d=recovery;
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
std::uint64_t now(){return static_cast<std::uint64_t>(g_get_monotonic_time()/1000);}
bool domain(const model::Tick& a,const model::Tick& b){return a.epoch==b.epoch&&a.clock_id==b.clock_id&&a.clock_scope==b.clock_scope;}
std::string reason(const std::exception& e){const std::string value=e.what();return !value.empty()&&value.size()<=64&&value.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789._")==std::string::npos?value:"inspector.render_failed";}
class RenderTask final:public InspectorRenderTask {
    struct Pending {std::uint64_t ticket;InspectorRenderInput input;};
    const std::thread::id gui_=std::this_thread::get_id();
    mutable std::mutex mutex_;std::condition_variable wake_;std::thread worker_;
    InspectorRenderStatus status_;std::optional<Pending> pending_;
    std::unique_ptr<InspectorRenderResult> result_;
    void owner()const{need(std::this_thread::get_id()==gui_,"inspector.render_owner");}
    bool closing(){std::lock_guard<std::mutex> lock(mutex_);return status_.closing;}
    void work(std::shared_ptr<const InspectorRenderSetup> setup,InspectorImageInitializer initialize,InspectorRenderBarrier barrier)noexcept{
        std::unique_ptr<r::SceneSurface> surface;std::unique_ptr<InspectorAdmission> admission;std::string error;
        try{
            auto images=initialize?initialize():r::ImageFactory{};
            surface=std::make_unique<r::SceneSurface>(setup->authority,setup->policy,*setup->config,setup->providers,[]{return true;},"",r::SurfaceAudience::inspector,std::move(images));
            admission=std::make_unique<InspectorAdmission>(*surface);
            while(!closing()){
                std::optional<Pending> claimed;
                {
                    std::unique_lock<std::mutex> lock(mutex_);
                    wake_.wait_for(lock,std::chrono::milliseconds(10),[&]{return status_.closing||pending_.has_value();});
                    if(status_.closing)break;
                    if(pending_){claimed=std::move(pending_);pending_.reset();status_.running=true;}
                }
                (void)surface->poll_image_jobs();if(!claimed)continue;
                auto value=std::make_unique<InspectorRenderResult>();value->ticket=claimed->ticket;value->input=std::move(claimed->input);claimed.reset();
                if(barrier)barrier(value->ticket);
                if(closing()){value.reset();break;}
                value->started_ms=now();const auto admission_begin=g_get_monotonic_time();
                auto ticks=value->input.ticks;
                if(value->input.delivery){
                    need(value->input.scope.profile==setup->profile,"inspector.render_profile");
                    ticks=admission->admit(*value->input.delivery,value->input.scope,value->started_ms);
                    value->active=!ticks.empty();
                }
                value->admission_us=static_cast<std::uint64_t>(g_get_monotonic_time()-admission_begin);
                const auto paint_begin=g_get_monotonic_time();
                surface->paint(value->started_ms,ticks,[&](auto,const auto* frame){if(frame){value->rows=inspector_rows(*frame);
                    for(const auto& widget:frame->widgets)if(widget.chart||(widget.image&&widget.image->state=="loading"))value->time_dependent=true;}});
                value->timeline=surface->timeline(value->started_ms,ticks);value->status=surface->status();
                value->paint_us=static_cast<std::uint64_t>(g_get_monotonic_time()-paint_begin);value->completed_ms=now();
                {
                    std::lock_guard<std::mutex> lock(mutex_);
                    if(!status_.closing){result_=std::move(value);status_.ready=true;++status_.completed;}
                }
                value.reset();
                {std::lock_guard<std::mutex> lock(mutex_);status_.running=false;}
            }
        }catch(const std::exception& e){error=reason(e);}catch(...){error="inspector.render_failed";}
        // Cancellation acknowledgement includes concrete native child drainage.
        admission.reset();
        if(surface){
            try{surface->close();while(!surface->poll_image_jobs())std::this_thread::sleep_for(std::chrono::milliseconds(10));}
            catch(...){if(error.empty())error="inspector.render_drain";}
            surface.reset();
        }
        setup.reset();initialize={};barrier={};
        std::lock_guard<std::mutex> lock(mutex_);pending_.reset();result_.reset();status_.ready=status_.running=false;status_.error=std::move(error);status_.stopped=true;
    }
public:
    RenderTask(std::shared_ptr<const InspectorRenderSetup> setup,InspectorImageInitializer initialize,InspectorRenderBarrier barrier){
        need(setup&&setup->config&&setup->profile&&setup->providers.size()<=16,"inspector.render_setup");
        worker_=std::thread([this,setup=std::move(setup),initialize=std::move(initialize),barrier=std::move(barrier)]()mutable{work(std::move(setup),std::move(initialize),std::move(barrier));});
    }
    ~RenderTask()override{close();if(worker_.joinable())worker_.join();}
    std::uint64_t submit(InspectorRenderInput input)override{
        owner();need(input.ticks.size()<=16,"inspector.render_capacity");
        for(const auto& clock:input.ticks)need(protocol::identifier(clock.first)&&protocol::identifier(clock.second.epoch)&&
            protocol::identifier(clock.second.clock_id)&&protocol::identifier(clock.second.clock_scope),"inspector.render_clock");
        if(input.delivery&&input.delivery->frame)need(input.delivery->frame->bytes.size()<=protocol::frame_limit,"inspector.render_capacity");
        std::lock_guard<std::mutex> lock(mutex_);need(!status_.closing&&!status_.stopped,"inspector.render_closed");
        need(status_.accepted<std::numeric_limits<std::uint64_t>::max(),"inspector.render_capacity");
        const auto ticket=++status_.accepted;if(pending_)++status_.replaced;
        pending_=Pending{ticket,std::move(input)};wake_.notify_one();return ticket;
    }
    std::unique_ptr<InspectorRenderResult> take()override{owner();std::lock_guard<std::mutex> lock(mutex_);status_.ready=false;return std::move(result_);}
    InspectorRenderStatus status()const override{owner();std::lock_guard<std::mutex> lock(mutex_);return status_;}
    void close()override{owner();std::lock_guard<std::mutex> lock(mutex_);status_.closing=true;pending_.reset();result_.reset();status_.ready=false;wake_.notify_one();}
};
}
bool InspectorRenderResult::current(const InspectorRenderInput& current,std::uint64_t profile,std::uint64_t stamp,bool publication_match)const{
    if(!profile||input.scope.profile!=profile||completed_ms>stamp||started_ms>completed_ms||input.scope.profile!=current.scope.profile||input.scope.generation!=current.scope.generation)return false;
    if(input.delivery.has_value()!=current.delivery.has_value())return false;
    if(!input.delivery){
        for(const auto& item:timeline){const auto found=current.ticks.find(item.first);
            if(found==current.ticks.end()||!domain(item.second.sample,found->second)||found->second.nanoseconds<item.second.sample.nanoseconds||found->second.nanoseconds>item.second.maximum_ns)return false;}
        return true;
    }
    if(current.scope.profile!=profile)return false;
    const auto& original=*input.delivery;const auto& native=*current.delivery;
    if(!active)return !native.deliverable(current.scope,stamp)&&timeline.empty();
    if((publication_match&&!original.deliverable(current.scope,stamp))||!native.deliverable(current.scope,stamp)||original.binding!=native.binding||
       (publication_match&&original.frame!=native.frame))return false;
    for(const auto& item:timeline){
        if(!native.clock||!native.binding||item.first!=native.binding->producer||!domain(item.second.sample,*native.clock)||
           native.clock->nanoseconds<item.second.sample.nanoseconds||native.clock->nanoseconds>item.second.maximum_ns)return false;
    }
    return true;
}
InspectorRenderFactory threaded_inspector_renderer(InspectorImageInitializer initialize,InspectorRenderBarrier barrier){
    return [initialize=std::move(initialize),barrier=std::move(barrier)](std::shared_ptr<const InspectorRenderSetup> setup){return std::make_unique<RenderTask>(std::move(setup),initialize,barrier);};
}
}
