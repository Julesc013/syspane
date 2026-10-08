#pragma once
#include "editor_visibility.hpp"
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
class EditorVisibilityForm {
public:
    EditorVisibilityForm(GtkWidget*,std::function<bool(const std::optional<SetWidgetVisibility>&)>,std::function<void(bool)>,std::function<void()>);
    ~EditorVisibilityForm();
    void open(const Json&,const std::vector<std::string>&);
    void erase();
    bool opened()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
