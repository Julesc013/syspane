#pragma once
#include "telemetry_delivery.hpp"
#include <functional>

namespace syspane::application {
// Serialized native client worker. The supplied guard verifies the exact live
// profile/supervisor scope before and after I/O. Connect and handshake each have
// a five-second bound; poll performs one bounded read. Neither belongs on GTK.
class LinuxNetworkConsumer {
public:
    LinuxNetworkConsumer(std::string endpoint,std::uint64_t process,std::string epoch,
                         recovery::DeliveryScope,configuration::Policy,std::function<bool()> current);
    ~LinuxNetworkConsumer();
    LinuxNetworkConsumer(const LinuxNetworkConsumer&)=delete;
    LinuxNetworkConsumer& operator=(const LinuxNetworkConsumer&)=delete;
    recovery::TelemetryDelivery poll();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
