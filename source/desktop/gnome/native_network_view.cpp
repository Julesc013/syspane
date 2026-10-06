#include "native_network_view.hpp"
#include "local_ipc.hpp"
#include "network_publication.hpp"
#include "network_view.hpp"
#include <memory>

namespace p = syspane::protocol;
namespace c = syspane::configuration;
namespace r = syspane::recovery;
namespace m = syspane::model;
namespace v = syspane::rendering;
namespace os = syspane::platform;
namespace {
using p::Json;
void need(bool value, const char* code) { if (!value) throw p::Error(code); }
std::uint64_t revision(const gchar* text) {
    need(text != nullptr, "network.policy");
    const auto value = p::decimal(text);
    need(value && *value, "network.policy");
    return *value;
}
c::Policy policy(std::uint64_t number, bool permit) {
    c::Policy result; result.available = true; result.revision = number;
    if (permit) {
        result.disclosure[{"desktop", "desktop"}] = {"operational"};
        result.disclosure[{"desktop", "accessibility"}] = {"operational"};
    }
    return result;
}
Json hello() {
    return {{"type", "hello"}, {"body", {{"wire_major", 0}, {"wire_minor", 1},
        {"role", "desktop"}, {"producer_epoch", "shell:consumer"}, {"max_frame_bytes", p::frame_limit},
        {"document_versions", Json::array({{{"document", "telemetry"}, {"version", "0.2.0"}},
            {{"document", "snapshot"}, {"version", "0.2.0"}}, {{"document", "observation"}, {"version", "0.2.0"}}})},
        {"required_features", {"telemetry.snapshot", "telemetry.measured-time"}}, {"optional_features", Json::array()}}}};
}
const char* code(r::DataCode value) {
    switch (value) {
    case r::DataCode::accepted: return "accepted";
    case r::DataCode::duplicate: return "duplicate";
    case r::DataCode::denied: return "restricted";
    case r::DataCode::stale_attachment: return "stale_attachment";
    case r::DataCode::policy_changed: return "policy_changed";
    case r::DataCode::snapshot_required: return "snapshot_required";
    case r::DataCode::closed: return "closed";
    default: throw p::Error("network.receive");
    }
}
const char* view_code(v::NetworkViewCode value) {
    switch (value) {
    case v::NetworkViewCode::ready: return "ready";
    case v::NetworkViewCode::restricted: return "restricted";
    case v::NetworkViewCode::waiting: return "waiting";
    case v::NetworkViewCode::unavailable: return "unavailable";
    case v::NetworkViewCode::selection_missing: return "selection_missing";
    case v::NetworkViewCode::invalid: return "invalid";
    case v::NetworkViewCode::capacity: return "capacity";
    }
    throw p::Error("network.internal");
}
Json optional_number(const std::optional<std::uint64_t>& value) {
    return value ? Json(std::to_string(*value)) : Json();
}
Json utc(const m::UtcTime& value) {
    return {{"seconds", std::to_string(value.seconds)}, {"nanoseconds", value.nanoseconds},
        {"subnanoseconds", value.subnanoseconds}};
}
Json projection(const v::NetworkFrame& frame) {
    Json result{{"code", view_code(frame.code)}, {"fields", Json::array()}};
    if (frame.code != v::NetworkViewCode::ready) return result;
    result.update({{"producer", frame.selected.producer}, {"epoch", frame.selected.epoch},
        {"entity", frame.selected.entity}, {"generation", frame.generation},
        {"lease", static_cast<int>(frame.presentation)}, {"reason", static_cast<int>(frame.reason)}});
    for (const auto& field : frame.fields) {
        result["fields"].push_back({{"value", field.value ? Json(*field.value) : Json()},
            {"unit", field.unit}, {"support", static_cast<int>(field.support)},
            {"acquisition", static_cast<int>(field.acquisition)}, {"presence", static_cast<int>(field.presence)},
            {"origin", static_cast<int>(field.origin)}, {"reported", static_cast<int>(field.reported)},
            {"effective", static_cast<int>(field.effective)}, {"error_code", field.error_code},
            {"measured_ns", field.measured_at ? Json(std::to_string(field.measured_at->nanoseconds)) : Json()},
            {"observed_at", field.observed_at ? utc(*field.observed_at) : Json()},
            {"attempted_at", utc(field.attempted_at)}, {"age_ns", optional_number(field.age_ns)},
            {"interval_ns", optional_number(field.interval_ns)}});
    }
    return result;
}
struct Consumer {
    os::Stream stream;
    r::DataView view;
    p::Framer decoder;
    std::uint64_t revision, token = 0, started = os::monotonic_ms();
    bool permit, welcomed = false, obsolete = false;
    std::string epoch, connection;
    Consumer(gint fd, guint pid, std::uint64_t number, bool allowed)
        : stream(os::Stream::from_connected_socket(fd, pid)),
          view({true, "desktop", {"desktop"}}, policy(number, allowed), "desktop", "operational",
               syspane::runtime::network_metrics()), revision(number), permit(allowed) {
        stream.measurement_clock();
    }
    m::Tick tick() {
        const auto sample = stream.measurement_clock();
        return {epoch, sample.nanoseconds, sample.clock_id, sample.local_scope};
    }
    void advance(std::uint64_t now) {
        decoder.tick(now);
        if (!welcomed) need(now >= started && now - started < 5000, "network.welcome_timeout");
    }
    const char* receive(std::string_view bytes, std::uint64_t now) {
        const auto message = p::decode(bytes);
        if (!welcomed) {
            need(message.type == "welcome", "network.welcome");
            const auto remote = p::handshake(message.body);
            need(remote.role == "console" && remote.epoch == message.producer_epoch, "network.welcome");
            const auto selected = p::negotiate(remote, p::handshake(hello()["body"]), {"desktop"});
            need(selected.documents.count({"telemetry", "0.2.0"}) && selected.documents.count({"snapshot", "0.2.0"}) &&
                selected.documents.count({"observation", "0.2.0"}) && selected.features.count("telemetry.measured-time"), "network.version");
            epoch = message.producer_epoch; connection = message.connection_id;
            const auto measured = tick();
            p::TelemetryBinding binding{selected, connection, epoch, "producer:network", "S", "desktop", "operational",
                revision, p::TelemetryDirection::producer_to_consumer, "0.2.0", measured.clock_id, measured.clock_scope};
            const auto attached = view.attach_wire(binding, now);
            need(attached.code == r::DataCode::accepted, "network.attach");
            token = attached.token; welcomed = true;
            decoder.restrict_limit(selected.max_frame_bytes);
            return "accepted";
        }
        need(message.connection_id == connection && message.producer_epoch == epoch, "network.envelope");
        if (message.type == "snapshot" || message.type == "delta")
            return code(view.receive(token, revision, bytes, now, tick()).code);
        if (message.type == "heartbeat")
            return code(view.heartbeat(token, revision, *p::decimal(message.body["sequence"].get_ref<const std::string&>()), now));
        if (message.type == "gap") return code(view.gap(token, revision, now));
        if (message.type == "shutdown") return code(view.disconnect(token, revision, now));
        throw p::Error("network.direction");
    }
};
}

struct _SysPaneNetworkView { GObject parent_instance; Consumer* consumer; };
G_DEFINE_TYPE(SysPaneNetworkView, syspane_network_view, G_TYPE_OBJECT)
namespace {
void fail(SysPaneNetworkView* self, GError** error, const char* message) {
    syspane_network_view_close(self);
    g_set_error_literal(error, g_quark_from_static_string("syspane-network-error"), 1, message);
}
template<class Result, class Call>
Result guarded(SysPaneNetworkView* self, GError** error, Call&& call) {
    try {
        need(SYSPANE_IS_NETWORK_VIEW(self) && self->consumer, "network.closed");
        return call(*self->consumer);
    } catch (const p::Error& exception) { fail(self, error, exception.what()); }
    catch (const os::IpcError& exception) { fail(self, error, exception.what()); }
    catch (...) { fail(self, error, "network.internal"); }
    return nullptr;
}
GBytes* framed(const Json& value) {
    const auto raw = p::frame(value.dump());
    return g_bytes_new(raw.data(), raw.size());
}
void finalize(GObject* object) {
    syspane_network_view_close(SYSPANE_NETWORK_VIEW(object));
    G_OBJECT_CLASS(syspane_network_view_parent_class)->finalize(object);
}
}
static void syspane_network_view_class_init(SysPaneNetworkViewClass* klass) {
    G_OBJECT_CLASS(klass)->finalize = finalize;
}
static void syspane_network_view_init(SysPaneNetworkView* self) { self->consumer = nullptr; }

SysPaneNetworkView* syspane_network_view_new_from_socket(gint fd, guint pid, const gchar* number, gboolean permit, GError** error) {
    try {
        auto consumer = std::make_unique<Consumer>(fd, pid, revision(number), permit);
        auto* self = SYSPANE_NETWORK_VIEW(g_object_new(SYSPANE_TYPE_NETWORK_VIEW, nullptr));
        self->consumer = consumer.release();
        return self;
    } catch (const p::Error& exception) { fail(nullptr, error, exception.what()); }
    catch (const os::IpcError& exception) { fail(nullptr, error, exception.what()); }
    catch (...) { fail(nullptr, error, "network.internal"); }
    return nullptr;
}
GBytes* syspane_network_view_hello(SysPaneNetworkView* self, GError** error) {
    return guarded<GBytes*>(self, error, [](Consumer&) { return framed(hello()); });
}
GBytes* syspane_network_view_subscribe(SysPaneNetworkView* self, GError** error) {
    return guarded<GBytes*>(self, error, [](Consumer& state) {
        need(state.welcomed && state.permit && !state.obsolete, "network.subscription");
        return framed({{"type", "subscribe"}, {"connection_id", state.connection}, {"producer_epoch", state.epoch},
            {"body", {{"schema_version", "0.2.0"}, {"subscription_id", "S"}, {"producer_id", "producer:network"},
                {"policy_revision", std::to_string(state.revision)}, {"channel", "desktop"}, {"classification", "operational"},
                {"clock_id", state.tick().clock_id}}}});
    });
}
GBytes* syspane_network_view_heartbeat(SysPaneNetworkView* self, const gchar* sequence, GError** error) {
    return guarded<GBytes*>(self, error, [&](Consumer& state) {
        need(state.welcomed && state.permit && !state.obsolete, "network.subscription");
        need(sequence && p::decimal(sequence).has_value(), "network.sequence");
        return framed({{"type", "heartbeat"}, {"connection_id", state.connection}, {"producer_epoch", state.epoch},
            {"body", {{"sequence", sequence}}}});
    });
}
gchar* syspane_network_view_feed(SysPaneNetworkView* self, GBytes* bytes, GError** error) {
    return guarded<gchar*>(self, error, [&](Consumer& state) {
        if (!state.permit) return g_strdup("restricted");
        if (state.obsolete) return g_strdup("policy_changed");
        need(bytes != nullptr, "network.input");
        gsize size = 0; const auto* data = static_cast<const char*>(g_bytes_get_data(bytes, &size));
        need(data && size && size <= 16384, "network.input");
        const auto now = os::monotonic_ms(); const char* result = "buffered"; unsigned count = 0;
        state.advance(now);
        state.decoder.feed(std::string_view(data, size), now, [&](auto payload) {
            need(++count <= 16, "network.batch"); result = state.receive(payload, now);
        });
        return g_strdup(result);
    });
}
gchar* syspane_network_view_project(SysPaneNetworkView* self, GError** error) {
    return guarded<gchar*>(self, error, [](Consumer& state) {
        Json result;
        if (!state.permit) result = {{"code", "restricted"}, {"fields", Json::array()}};
        else if (state.obsolete) result = {{"code", "waiting"}, {"fields", Json::array()}};
        else {
            const auto now = os::monotonic_ms(); state.advance(now);
            if (!state.welcomed) result = {{"code", "waiting"}, {"fields", Json::array()}};
            else v::project_network(state.view, {"producer:network", state.epoch, "network:interface:1"}, now, state.tick(),
                    [&](const auto& frame) { result = projection(frame); });
        }
        const auto raw = result.dump(); need(raw.size() <= 16384, "network.output_capacity");
        return g_strdup(raw.c_str());
    });
}
gchar* syspane_network_view_policy(SysPaneNetworkView* self, const gchar* number, gboolean permit, GError** error) {
    return guarded<gchar*>(self, error, [&](Consumer& state) {
        const auto next = revision(number);
        if (next < state.revision || (next == state.revision && bool(permit) != state.permit)) return g_strdup("invalid");
        if (next == state.revision) return g_strdup("duplicate");
        state.view.policy(policy(next, permit), os::monotonic_ms());
        state.revision = next; state.permit = permit; state.obsolete = true; state.decoder = p::Framer();
        return g_strdup("cleared");
    });
}
GBytes* syspane_network_view_shutdown(SysPaneNetworkView* self, GError** error) {
    return guarded<GBytes*>(self, error, [](Consumer& state) {
        need(state.welcomed, "network.welcome");
        return framed({{"type", "shutdown"}, {"connection_id", state.connection}, {"producer_epoch", state.epoch},
            {"body", {{"reason", "normal"}}}});
    });
}
void syspane_network_view_close(SysPaneNetworkView* self) {
    if (!SYSPANE_IS_NETWORK_VIEW(self)) return;
    delete self->consumer; self->consumer = nullptr;
}
