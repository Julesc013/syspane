#pragma once
#include <functional>
#include <memory>
#include <string>
#include <string_view>

namespace syspane::platform {
enum class ClipboardResult { received, cancelled, rejected, timeout };
// Serialized GLib owner. Callbacks must not destroy this object or start a nested
// main loop. A borrow is consumed during one callback only, including each chunk.
class SceneClipboardX11 {
public:
    struct Callbacks {
        std::function<bool()> permitted;
        // Must check current authority and throw on denial before returning the
        // view. The adapter never retains this view beyond the current callback.
        std::function<std::string_view()> borrow;
        std::function<void()> lost;
        std::function<void(ClipboardResult,std::string)> received;
    };
    explicit SceneClipboardX11(Callbacks);
    ~SceneClipboardX11();
    SceneClipboardX11(const SceneClipboardX11&)=delete;
    SceneClipboardX11& operator=(const SceneClipboardX11&)=delete;
    bool available()const;
    bool busy()const;
    bool offer();
    bool request();
    void cancel();
    void invalidate(); // Silent cancellation plus erasure of this owner's offer.
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
