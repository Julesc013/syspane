#include "native_health_view.hpp"
#include "health_link.hpp"
#include "recovery.hpp"
#include <memory>

namespace p = syspane::protocol;
namespace r = syspane::recovery;
namespace os = syspane::platform;
namespace {
struct Consumer {
    os::Stream stream;
    r::HealthLink link;
    r::ProducerLease lease;
    std::uint64_t token = 0;
    Consumer(gint fd, guint pid) : stream(os::Stream::from_connected_socket(fd, pid)),
        link(false, "desktop", "shell:render", "", stream.connected_ms()) { stream.measurement_clock(); }
    void alive() { stream.measurement_clock(); }
    void advance(std::uint64_t now) {
        link.tick(now);
        if (token) {
            lease.tick(now);
            if (!lease.view().alive) throw p::Error("health.peer_expired");
        }
    }
    GBytes* output() {
        const auto bytes = link.take_output();
        return g_bytes_new(bytes.data(), bytes.size());
    }
};
std::uint64_t integer(const gchar* text) {
    if (!text) throw p::Error("health.integer");
    const auto value = p::decimal(text);
    if (!value) throw p::Error("health.integer");
    return *value;
}
const char* kind(r::HealthKind value) {
    switch (value) {
    case r::HealthKind::ready: return "ready";
    case r::HealthKind::heartbeat: return "heartbeat";
    case r::HealthKind::challenge: return "challenge";
    case r::HealthKind::progress: return "progress";
    case r::HealthKind::shutdown: return "shutdown";
    case r::HealthKind::transaction_started:
    case r::HealthKind::transaction_armed:
    case r::HealthKind::transaction_finished: break; // This renderer link never negotiates transaction supervision.
    }
    throw p::Error("health.internal");
}
}
struct _SysPaneHealthView { GObject parent_instance; Consumer* consumer; };
G_DEFINE_TYPE(SysPaneHealthView, syspane_health_view, G_TYPE_OBJECT)
namespace {
void fail(SysPaneHealthView* self, GError** error, const char* message) {
    syspane_health_view_close(self);
    g_set_error_literal(error, g_quark_from_static_string("syspane-health-error"), 1, message);
}
template<class Result, class Call>
Result guarded(SysPaneHealthView* self, GError** error, Call&& call) {
    try {
        if (!SYSPANE_IS_HEALTH_VIEW(self) || !self->consumer) throw p::Error("health.closed");
        self->consumer->alive(); return call(*self->consumer);
    } catch (const p::Error& exception) { fail(self, error, exception.what()); }
    catch (const os::IpcError& exception) { fail(self, error, exception.what()); }
    catch (...) { fail(self, error, "health.internal"); }
    return Result{};
}
void finalize(GObject* object) {
    syspane_health_view_close(SYSPANE_HEALTH_VIEW(object));
    G_OBJECT_CLASS(syspane_health_view_parent_class)->finalize(object);
}
}
static void syspane_health_view_class_init(SysPaneHealthViewClass* klass) { G_OBJECT_CLASS(klass)->finalize = finalize; }
static void syspane_health_view_init(SysPaneHealthView* self) { self->consumer = nullptr; }
SysPaneHealthView* syspane_health_view_new_from_socket(gint fd, guint expected_pid, GError** error) {
    try {
        auto consumer = std::make_unique<Consumer>(fd, expected_pid);
        auto* self = SYSPANE_HEALTH_VIEW(g_object_new(SYSPANE_TYPE_HEALTH_VIEW, nullptr));
        self->consumer = consumer.release(); return self;
    } catch (const os::IpcError& exception) { fail(nullptr, error, exception.what()); }
    catch (const p::Error& exception) { fail(nullptr, error, exception.what()); }
    catch (...) { fail(nullptr, error, "health.internal"); }
    return nullptr;
}
GBytes* syspane_health_view_hello(SysPaneHealthView* self, GError** error) {
    return guarded<GBytes*>(self, error, [](Consumer& value) { return value.output(); });
}
gchar* syspane_health_view_feed(SysPaneHealthView* self, GBytes* bytes, GError** error) {
    return guarded<gchar*>(self, error, [bytes](Consumer& value) {
        if (!bytes) throw p::Error("health.bytes");
        gsize size = 0; const auto* data = static_cast<const char*>(g_bytes_get_data(bytes, &size));
        const auto now = os::monotonic_ms(); value.advance(now);
        const auto events = value.link.feed(std::string_view(data, size), now);
        auto result = p::Json::array();
        for (const auto& event : events) {
            if (event.kind == r::HealthKind::ready)
                value.token = value.lease.attach("watcher", value.link.epoch(), now).token;
            if (event.kind == r::HealthKind::heartbeat) {
                const auto code = value.lease.heartbeat(value.token, event.value, now);
                if (code != r::Code::accepted && code != r::Code::duplicate) throw p::Error("health.heartbeat");
            }
            result.push_back({{"kind", kind(event.kind)}, {"value", std::to_string(event.value)},
                {"observed_ms", std::to_string(event.observed_ms)}});
        }
        return g_strdup(result.dump().c_str());
    });
}
GBytes* syspane_health_view_heartbeat(SysPaneHealthView* self, const gchar* sequence, GError** error) {
    return guarded<GBytes*>(self, error, [sequence](Consumer& value) { value.advance(os::monotonic_ms()); value.link.heartbeat(integer(sequence)); return value.output(); });
}
GBytes* syspane_health_view_progress(SysPaneHealthView* self, const gchar* generation, GError** error) {
    return guarded<GBytes*>(self, error, [generation](Consumer& value) { value.advance(os::monotonic_ms()); value.link.progress(integer(generation)); return value.output(); });
}
GBytes* syspane_health_view_shutdown(SysPaneHealthView* self, GError** error) {
    return guarded<GBytes*>(self, error, [](Consumer& value) { value.link.shutdown(); return value.output(); });
}
gboolean syspane_health_view_tick(SysPaneHealthView* self, GError** error) {
    return guarded<gboolean>(self, error, [](Consumer& value) { value.advance(os::monotonic_ms()); return TRUE; });
}
void syspane_health_view_close(SysPaneHealthView* self) {
    if (!SYSPANE_IS_HEALTH_VIEW(self)) return;
    delete self->consumer; self->consumer = nullptr;
}
