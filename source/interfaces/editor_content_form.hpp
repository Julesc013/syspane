#pragma once
#include "editor_content.hpp"
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
class EditorContentForm {
public:
    EditorContentForm(GtkWidget* parent,std::function<bool(const std::vector<SceneEdit>&)> apply,std::function<void(bool)> finished,std::function<void()> failed);
    ~EditorContentForm();
    void open(const Json& scene,const Json* selected,const configuration::ResourceSet&);
    void erase();
    bool opened()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
