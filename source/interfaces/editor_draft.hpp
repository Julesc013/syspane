#pragma once
#include "settings_draft.hpp"
#include "editor_recovery.hpp"
#include <deque>
#include <variant>

namespace syspane::interfaces {
enum class WidgetProperty {title,display,layout,priority};
struct WidgetPropertyEdit {std::string id;WidgetProperty property;Json value;};
struct WidgetContentEdit {std::string id;Json bindings,content;};
struct SceneThemeEdit {std::optional<std::string> theme;};
struct InsertWidget {Json widget;std::optional<std::string> parent;std::size_t index;bool select_inserted=false;};
struct RemoveWidgets {std::vector<std::string> ids;};
struct ReparentWidgets {std::vector<std::string> ids;std::optional<std::string> parent;std::size_t index;};
struct DuplicateWidgets {std::vector<std::string> ids;std::map<std::string,std::string> mapping;};
struct PasteWidgets {std::string bytes;std::map<std::string,std::string> mapping;std::optional<std::string> parent;std::size_t index;};
struct MoveWidgets {std::vector<std::string> ids;double dx,dy;std::vector<int> variants={};};
struct ResizeWidget {std::string id;double width,height;int variant=-1;};
struct RootDisplayEdit {std::string root;Json display;};
enum class Alignment {left,hcenter,right,top,vcenter,bottom};
enum class Spacing {horizontal,vertical};
struct AlignWidgets {std::vector<std::string> ids;Alignment alignment;std::vector<int> variants={};};
struct DistributeWidgets {std::vector<std::string> ids;Spacing spacing;std::vector<int> variants={};};
struct GroupWidgets {std::vector<std::string> ids;std::string id,title;};
struct UngroupWidget {std::string id;};
struct WrapWidgets {std::vector<std::string> ids;std::string id,title;Json layout;std::string priority="normal";};
struct UnwrapWidget {std::string id;};
struct SetWidgetVisibility {std::vector<std::string> ids;std::optional<Json> rule;};
struct SetWidgetLocks {std::vector<std::string> ids;bool locked;};
bool edit_locked(const Json& scene,const std::string& id);
bool edit_protected(const Json& scene,const std::string& id);
using SceneEdit=std::variant<WidgetPropertyEdit,WidgetContentEdit,SceneThemeEdit,InsertWidget,RemoveWidgets,ReparentWidgets,DuplicateWidgets,MoveWidgets,ResizeWidget,AlignWidgets,DistributeWidgets,GroupWidgets,UngroupWidget,RootDisplayEdit,WrapWidgets,UnwrapWidget,SetWidgetLocks,SetWidgetVisibility,PasteWidgets>;

// One serialized native owner. Scene/selection borrows expire on every mutation,
// policy update or close; adapters must erase their own caches on disclosure loss.
class EditorDraft {
public:
    EditorDraft(configuration::Authority,configuration::Policy,configuration::Authored,std::string epoch,std::optional<SettingsResources> resources={},bool large_commands=false);
    const Json* scene()const;
    const std::vector<std::string>& selection()const{return selected_;}
    void select(std::vector<std::string>);
    bool execute(const std::vector<SceneEdit>&);
    bool recovery_available()const;
    std::optional<std::string> recovery_snapshot(const RecoveryIdentity&)const;
    RecoveryDescription inspect_recovery(std::string_view,const RecoveryIdentity&)const;
    bool restore_recovery(std::string_view,const RecoveryIdentity&);
    std::unique_ptr<RecoveryWork> recovery_capture_work(const RecoveryIdentity&)const;
    std::unique_ptr<RecoveryWork> recovery_restore_work(std::string,const RecoveryIdentity&)const;
    std::optional<std::string> recovery_capture(std::unique_ptr<RecoveryPrepared>,const RecoveryIdentity&)const;
    RecoveryDescription inspect_recovery(const RecoveryPrepared&,const RecoveryIdentity&)const;
    bool restore_recovery(std::unique_ptr<RecoveryPrepared>,const RecoveryIdentity&);
    bool clipboard_available()const;
    void copy_selection();
    // Recheck permission for each delivery. Borrow expires at the next operation.
    std::string_view clipboard_data();
    void clear_clipboard(){clipboard_.clear();}
    bool theme_fonts_available()const;
    bool set_theme_fonts(const Json& font,const Json& font_roles);
    const configuration::ResourceSet* resources()const{return available()?transaction_.draft_resources_.get():nullptr;}
    bool locks_available()const;
    bool visibility_available()const;
    bool undo();
    bool redo();
    std::size_t undo_count()const{return undo_.size();}
    std::size_t redo_count()const{return redo_.size();}
    std::size_t history_bytes()const;
    void discard();
    void close();
    void policy(configuration::Policy);
    void reload(configuration::Authored,std::string epoch,std::optional<SettingsResources> resources={});
    bool complete(std::uint64_t ticket,const Json&);
    bool reconciled(std::uint64_t ticket,const std::string& query,const std::string& epoch,const Json&);
    std::optional<EditRequest> begin(const std::string& intent,const std::string& request);
    std::optional<EditRequest> active_request()const{return transaction_.active_request();}
    std::optional<EditRequest> cancel_request(){invalidate_recovery();return transaction_.cancel_request();}
    void disconnected(){invalidate_recovery();clear_clipboard();transaction_.disconnected();}
    DraftState state()const{return transaction_.state();}
    bool available()const{return transaction_.available();}
    bool dirty()const{return transaction_.dirty();}
    bool may_submit(const std::string& intent)const{return transaction_.may_submit(intent);}
    const Json& last_result()const{return transaction_.last_result();}
    std::optional<std::uint64_t> revision()const{return transaction_.revision();}
private:
    friend class RecoveryWork;
    struct RecoveryValidity {
        std::shared_ptr<const char> value=std::make_shared<const char>(char{});
        RecoveryValidity()=default;
        RecoveryValidity(const RecoveryValidity&){}
        RecoveryValidity& operator=(const RecoveryValidity&){value=std::make_shared<const char>(char{});return *this;}
    } recovery_validity_;
    EditorDraft(const SettingsDraft& value,int):transaction_(value,SettingsDraft::RecoveryCopy{}){}
    void invalidate_recovery(){recovery_validity_.value=std::make_shared<const char>(char{});}
    void check_recovery(const RecoveryPrepared&,const RecoveryIdentity&,bool capture)const;
    struct State {Json scene;std::vector<std::string> selection;configuration::ResourceSnapshot resources;std::size_t resource_metadata_bytes=0;};
    struct Change {State before,after;std::size_t bytes;};
    SettingsDraft transaction_;
    std::vector<std::string> selected_;
    std::deque<Change> undo_,redo_;
    std::string clipboard_;
    void admit_fragment_version(const Json&)const;
    void authorize_recovery()const;
    void recovery_destination()const;
    std::pair<configuration::Authored,configuration::ResourceSnapshot> prepare_recovery(std::string_view,const RecoveryIdentity&)const;
    void clear_history();
    void settled(bool);
    bool travel(bool forward);
    bool record(Json,std::vector<std::string>,configuration::ResourceSnapshot={});
    bool record_prepared(std::pair<configuration::Authored,configuration::ResourceSnapshot>,std::vector<std::string>);
    std::size_t history_bytes(const std::deque<Change>&,const std::deque<Change>&)const;
};
}
