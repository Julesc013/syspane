#pragma once
#include "scene_surface.hpp"
#include "telemetry_delivery.hpp"
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
// One native UI thread owns this component, its GTK hierarchy and current authority.
class SceneInspector {
public:
    using Translator=std::function<std::string(const std::string&)>;
    enum class Phase {admission,paint,presentation};
    // Borrowed synchronous experiment observer; paint includes presentation.
    // Refusal or exception closes/erases the inspector. Never retained.
    using PhaseObserver=std::function<bool(Phase,std::uint64_t microseconds,bool completed)>;
    SceneInspector(configuration::Authority,configuration::Policy,rendering::SurfaceConfig,
                   std::vector<rendering::SurfaceProvider>,std::string image_worker={},Translator translate={},rendering::ImageFactory images={});
    ~SceneInspector();
    SceneInspector(const SceneInspector&)=delete;SceneInspector& operator=(const SceneInspector&)=delete;
    GtkWidget* widget()const;
    recovery::DataAttachment attach(const std::string&,const protocol::TelemetryBinding&,std::uint64_t now,const std::map<std::string,model::Tick>& ticks={});
    recovery::DataResult receive(const std::string&,std::uint64_t token,std::uint64_t revision,std::string_view,
        std::uint64_t now,const model::Tick&,const std::map<std::string,model::Tick>& other_ticks={});
    recovery::DataCode heartbeat(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now,const std::map<std::string,model::Tick>& ticks={});
    recovery::DataCode gap(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t now,const std::map<std::string,model::Tick>& ticks={});
    recovery::DataCode disconnect(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t now,const std::map<std::string,model::Tick>& ticks={});
    void refresh(std::uint64_t now,const std::map<std::string,model::Tick>& ticks={},const PhaseObserver& observer={});
    // One paint after native-validated attachment/full/heartbeat adoption.
    // The absolute native deadline and fresh clock gate every refresh, including
    // updates with no new frame. A different profile requires a new inspector.
    void deliver(const recovery::TelemetryDelivery&,recovery::DeliveryScope current,std::uint64_t now,const PhaseObserver& observer={});
    void policy(configuration::Policy,std::uint64_t now);
    void replace(rendering::SurfaceConfig,std::uint64_t now);
    void close();bool poll_image_jobs();rendering::SurfaceStatus status()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
