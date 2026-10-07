#pragma once
#include "editor_binding.hpp"
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
class EditorBindingForm {
public:
    EditorBindingForm(GtkWidget*,std::function<bool(const std::vector<SceneEdit>&)>,std::function<void(bool)>,std::function<void()>);
    ~EditorBindingForm();
    void open(const Json& widget);
    void erase();
    bool opened()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
