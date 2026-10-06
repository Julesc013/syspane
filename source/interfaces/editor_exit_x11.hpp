#pragma once
#include <memory>

namespace syspane::interfaces {
enum class EditorExitInput { none, requested, unavailable };
// One single-threaded recovery owner; Xlib error handlers are process-global.
// Acquire before mapping an editor. No process-control or document authority.
class EditorExitKeys {
public:
    EditorExitKeys();
    ~EditorExitKeys();
    EditorExitKeys(const EditorExitKeys&) = delete;
    EditorExitKeys& operator=(const EditorExitKeys&) = delete;
    EditorExitInput poll();
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};
}
