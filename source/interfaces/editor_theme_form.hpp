#pragma once
#include "editor_theme.hpp"
#include <functional>
#include <memory>
#include <optional>
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
class EditorThemeForm {
public:
    // Null requests existing scene-level inheritance from settings.
    EditorThemeForm(GtkWidget*,std::function<bool(const std::optional<configuration::Json>&)>,std::function<void(bool)>,std::function<void()>);
    ~EditorThemeForm();
    void open(const configuration::Json&);
    void erase();
    bool opened()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
