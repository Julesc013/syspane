#pragma once
#include "editor_create.hpp"
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
class EditorCreateForm {
public:
    EditorCreateForm(GtkWidget*,std::function<bool(const CreateInput&)>,std::function<void(bool)>,std::function<void()>);
    ~EditorCreateForm();
    void open(const Json& scene,const std::vector<std::string>& selection,ContentChoices);
    void erase();
    bool opened()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
