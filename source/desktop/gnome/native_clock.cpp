#include "native_clock.hpp"
#include "local_ipc.hpp"
#include <exception>
#include <memory>

struct _SysPaneClock {
    GObject parent_instance;
    syspane::platform::Stream* stream;
};
G_DEFINE_TYPE(SysPaneClock, syspane_clock, G_TYPE_OBJECT)

namespace {
void fail(GError** error, const char* message) {
    g_set_error_literal(error, g_quark_from_static_string("syspane-clock-error"), 1, message);
}
void finalize(GObject* object) {
    syspane_clock_close(SYSPANE_CLOCK(object));
    G_OBJECT_CLASS(syspane_clock_parent_class)->finalize(object);
}
}
static void syspane_clock_class_init(SysPaneClockClass* klass) {
    G_OBJECT_CLASS(klass)->finalize = finalize;
}
static void syspane_clock_init(SysPaneClock* self) { self->stream = nullptr; }

SysPaneClock* syspane_clock_new_from_socket(gint fd, guint expected_pid, GError** error) {
    try {
        auto stream = std::make_unique<syspane::platform::Stream>(
            syspane::platform::Stream::from_connected_socket(fd, expected_pid));
        auto* self = SYSPANE_CLOCK(g_object_new(SYSPANE_TYPE_CLOCK, nullptr));
        self->stream = stream.release();
        return self;
    } catch (const syspane::platform::IpcError& exception) {
        fail(error, exception.what());
    } catch (...) { fail(error, "clock.internal"); }
    return nullptr;
}
gchar* syspane_clock_sample(SysPaneClock* self, GError** error) {
    if (!SYSPANE_IS_CLOCK(self) || !self->stream) { fail(error, "clock.closed"); return nullptr; }
    try {
        const auto reading = self->stream->measurement_clock();
        return g_strdup(std::to_string(reading.nanoseconds).c_str());
    } catch (const syspane::platform::IpcError& exception) {
        fail(error, exception.what());
    } catch (...) { fail(error, "clock.internal"); }
    return nullptr;
}
void syspane_clock_close(SysPaneClock* self) {
    if (!SYSPANE_IS_CLOCK(self)) return;
    delete self->stream;
    self->stream = nullptr;
}
