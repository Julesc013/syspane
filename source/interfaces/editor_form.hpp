#pragma once
#include "editor_draft.hpp"
#include "editor_history_task.hpp"
#include "editor_request_task.hpp"
#include "scene_surface.hpp"
#include "recovery_queue_linux.hpp"
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
struct EditorRecoveryBinding;
class EditorForm {
public:
    struct Actions {
        std::function<std::string()> request_id,widget_id;
        std::function<void(const EditRequest&)> submit,cancel;
        std::function<void()> reload,exit;
        std::function<void(const EditRequest&,std::optional<std::string>)> submit_recovery;
    };
    EditorForm(configuration::Authority,configuration::Policy,configuration::Authored,std::string epoch,SettingsResources,
        scene::Topology,std::string display,std::vector<rendering::SurfaceProvider>,std::string image_worker,Actions,bool large_commands=false,rendering::ImageFactory images={},std::shared_ptr<const HistoryPreparationFactory> history={},std::shared_ptr<const RequestPreparationFactory> requests={});
    EditorForm(std::unique_ptr<PreparedEditor>,scene::Topology,std::string display,std::vector<rendering::SurfaceProvider>,std::string image_worker,Actions,rendering::ImageFactory images={},std::shared_ptr<const HistoryPreparationFactory> history={},std::shared_ptr<const RequestPreparationFactory> requests={});
    ~EditorForm();
    EditorForm(const EditorForm&)=delete;EditorForm& operator=(const EditorForm&)=delete;
    GtkWidget* widget()const;
    bool can_leave()const;
    enum class ReplyView { refresh, close_on_accepted };
    // Closing still validates the reply and requires stopped() before destruction.
    bool complete(std::uint64_t,const Json&,ReplyView=ReplyView::refresh);
    bool reconciled(std::uint64_t,const std::string& query,const std::string& epoch,const Json&,ReplyView=ReplyView::refresh);
    void disconnected();
    void policy(configuration::Policy);
    void reload(configuration::Authored,std::string epoch,SettingsResources);
    void topology(scene::Topology,std::string display);
    recovery::DataAttachment attach(const std::string&,const protocol::TelemetryBinding&,std::uint64_t now);
    recovery::DataResult receive(const std::string&,std::uint64_t token,std::uint64_t revision,std::string_view,std::uint64_t now,const model::Tick&);
    recovery::DataCode heartbeat(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now);
    recovery::DataCode disconnect(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t now);
    void close();
    void recovery(std::string worker,std::string directory,const EditorRecoveryBinding&);
    void recovery(std::shared_ptr<const platform::RecoveryFactory>,std::string directory,const EditorRecoveryBinding&,std::shared_ptr<const RecoveryPreparationFactory> preparations={},std::optional<std::string> retirement={});
    bool retirement_decided()const;
    // Continue the host loop after close until the held recovery helper is reaped.
    bool stopped();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
