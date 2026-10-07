#pragma once
#include "editor_layout.hpp"
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
class EditorLayoutForm {
public:
    EditorLayoutForm(GtkWidget*,std::function<bool(const std::vector<SceneEdit>&)>,std::function<void(bool)>,std::function<void()>);
    ~EditorLayoutForm();
    void open(const Json& scene,const std::string& id);
    void wrap(const Json& scene,const std::vector<std::string>& ids,const std::string& fresh_id);
    void unwrap(const Json& scene,const std::string& id);
    void erase();
    bool opened()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
