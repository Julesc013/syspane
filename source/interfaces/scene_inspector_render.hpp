#pragma once
#include "scene_inspector_model.hpp"
#include "telemetry_delivery.hpp"

namespace syspane::interfaces {
struct InspectorRenderSetup {
    configuration::Authority authority;configuration::Policy policy;
    std::shared_ptr<const rendering::SurfaceConfig> config;std::vector<rendering::SurfaceProvider> providers;
    std::uint64_t profile=0;
};
struct InspectorRenderInput {
    std::optional<recovery::TelemetryDelivery> delivery;
    recovery::DeliveryScope scope;
    std::map<std::string,model::Tick> ticks;
};
struct InspectorRenderResult {
    std::uint64_t ticket=0,started_ms=0,completed_ms=0,admission_us=0,paint_us=0;
    InspectorRenderInput input;
    rendering::SurfaceStatus status;
    rendering::SurfaceTimeline timeline;
    std::vector<InspectorRow> rows;
    bool active=false,time_dependent=false;
    bool current(const InspectorRenderInput&,std::uint64_t profile,std::uint64_t now,bool publication_match=true)const;
};
struct InspectorRenderStatus {
    bool running=false,ready=false,closing=false,stopped=false;
    std::uint64_t accepted=0,replaced=0,completed=0;
    std::string error;
};
// GUI task handle: bounded transfers only. Close, poll stopped, then destroy.
// A stopped acknowledgement follows destruction of all worker-owned input/jobs.
class InspectorRenderTask {
public:
    virtual ~InspectorRenderTask()=default;
    virtual std::uint64_t submit(InspectorRenderInput)=0;
    virtual std::unique_ptr<InspectorRenderResult> take()=0;
    // Acknowledge only the latest transferred result, after current GUI adoption.
    // Native image work may start only after this bounded owner notification.
    virtual void acknowledge(std::uint64_t ticket)=0;
    virtual InspectorRenderStatus status()const=0;
    virtual void close()=0;
};
using InspectorRenderFactory=std::function<std::unique_ptr<InspectorRenderTask>(std::shared_ptr<const InspectorRenderSetup>)>;
// Initializer runs once on the rendering owner, never GTK. It may retain only
// same-owner installation/job state. Null factory means no image capability.
using InspectorImageInitializer=std::function<rendering::ImageFactory()>;
// Owned fixture barrier after claim, before admission. Production callers omit.
// Runs on the rendering owner; it is not a retained GUI/phase observer.
using InspectorRenderBarrier=std::function<void(std::uint64_t ticket)>;
InspectorRenderFactory threaded_inspector_renderer(InspectorImageInitializer={},InspectorRenderBarrier={});
}
