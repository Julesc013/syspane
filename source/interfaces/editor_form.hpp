#pragma once
#include "editor_draft.hpp"
#include "scene_surface.hpp"
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
class EditorForm {
public:
    struct Actions {
        std::function<std::string()> request_id,widget_id;
        std::function<void(const EditRequest&)> submit,cancel;
        std::function<void()> reload,exit;
    };
    EditorForm(configuration::Authority,configuration::Policy,configuration::Authored,std::string epoch,SettingsResources,
        scene::Topology,std::string display,std::vector<rendering::SurfaceProvider>,std::string image_worker,Actions,bool large_commands=false);
    ~EditorForm();
    EditorForm(const EditorForm&)=delete;EditorForm& operator=(const EditorForm&)=delete;
    GtkWidget* widget()const;
    void complete(std::uint64_t,const Json&);
    void reconciled(std::uint64_t,const std::string& query,const std::string& epoch,const Json&);
    void disconnected();
    void policy(configuration::Policy);
    void reload(configuration::Authored,std::string epoch,SettingsResources);
    void topology(scene::Topology,std::string display);
    recovery::DataAttachment attach(const std::string&,const protocol::TelemetryBinding&,std::uint64_t now);
    recovery::DataResult receive(const std::string&,std::uint64_t token,std::uint64_t revision,std::string_view,std::uint64_t now,const model::Tick&);
    recovery::DataCode heartbeat(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now);
    recovery::DataCode disconnect(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t now);
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
