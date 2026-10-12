#pragma once
#include <gtk/gtk.h>
#include <memory>
#include <cstdint>
namespace syspane::interfaces {
class InspectorRetirement {
public:
    struct State {std::size_t pending=0;std::uint64_t accepted=0,delivered=0,polls=0,total_us=0,max_us=0;bool failed=false;};
    InspectorRetirement();~InspectorRetirement();
    bool unset(GtkAccessible*,void(*)(GtkAccessible*))noexcept;
    bool dispatch(GObject*,guint,GParamSpec**,void(*)(GObject*,guint,GParamSpec**))noexcept;
    void poll();void finish();State state()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
// Internal GTK-thread factory. Every cell clears its cache before native retirement.
GtkCellRenderer* inspector_text_renderer(const std::shared_ptr<InspectorRetirement>& owner={});
}
