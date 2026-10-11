#pragma once
#include "scene_surface.hpp"
#include "telemetry_delivery.hpp"
#include <thread>

namespace syspane::interfaces {
// Private state owner shared by synchronous presentation and future worker use.
// Surface must outlive this object on the same thread. No native sink is retained.
class InspectorAdmission {
public:
    explicit InspectorAdmission(rendering::SceneSurface&);
    InspectorAdmission(const InspectorAdmission&)=delete;
    InspectorAdmission& operator=(const InspectorAdmission&)=delete;
    bool compatible(recovery::DeliveryScope current)const;
    std::map<std::string,model::Tick> admit(const recovery::TelemetryDelivery&,
                                         recovery::DeliveryScope current,std::uint64_t now);
    // Releases delivery payloads/attachment state, retaining fixed profile identity.
    // Caller separately performs current-policy erasure/close on the surface.
    void reset();
private:
    rendering::SceneSurface& surface_;
    const std::thread::id owner_=std::this_thread::get_id();
    bool calling_=false;
    std::shared_ptr<const protocol::TelemetryBinding> binding_;
    std::shared_ptr<const recovery::DeliveredFrame> frame_;
    recovery::DeliveryScope scope_;
    std::optional<std::uint64_t> heartbeat_;
    std::uint64_t token_=0,until_=0;
    void owner()const;
    void forget();
};
}
