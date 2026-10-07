#pragma once
#include "settings_draft.hpp"
#include <deque>
#include <variant>

namespace syspane::interfaces {
enum class WidgetProperty {title,display,layout,priority};
struct WidgetPropertyEdit {std::string id;WidgetProperty property;Json value;};
struct WidgetContentEdit {std::string id;Json bindings,content;};
struct SceneThemeEdit {std::optional<std::string> theme;};
struct InsertWidget {Json widget;std::optional<std::string> parent;std::size_t index;};
struct RemoveWidgets {std::vector<std::string> ids;};
struct ReparentWidgets {std::vector<std::string> ids;std::optional<std::string> parent;std::size_t index;};
struct DuplicateWidgets {std::vector<std::string> ids;std::map<std::string,std::string> mapping;};
struct MoveWidgets {std::vector<std::string> ids;double dx,dy;};
struct ResizeWidget {std::string id;double width,height;};
enum class Alignment {left,hcenter,right,top,vcenter,bottom};
enum class Spacing {horizontal,vertical};
struct AlignWidgets {std::vector<std::string> ids;Alignment alignment;};
struct DistributeWidgets {std::vector<std::string> ids;Spacing spacing;};
struct GroupWidgets {std::vector<std::string> ids;std::string id,title;};
struct UngroupWidget {std::string id;};
using SceneEdit=std::variant<WidgetPropertyEdit,WidgetContentEdit,SceneThemeEdit,InsertWidget,RemoveWidgets,ReparentWidgets,DuplicateWidgets,MoveWidgets,ResizeWidget,AlignWidgets,DistributeWidgets,GroupWidgets,UngroupWidget>;

// One serialized native owner. Scene/selection borrows expire on every mutation,
// policy update or close; adapters must erase their own caches on disclosure loss.
class EditorDraft {
public:
    EditorDraft(configuration::Authority,configuration::Policy,configuration::Authored,std::string epoch,std::optional<SettingsResources> resources={},bool large_commands=false);
    const Json* scene()const;
    const std::vector<std::string>& selection()const{return selected_;}
    void select(std::vector<std::string>);
    bool execute(const std::vector<SceneEdit>&);
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
    std::optional<EditRequest> begin(const std::string& intent,const std::string& request){return transaction_.begin(intent,request);}
    std::optional<EditRequest> active_request()const{return transaction_.active_request();}
    std::optional<EditRequest> cancel_request(){return transaction_.cancel_request();}
    void disconnected(){transaction_.disconnected();}
    DraftState state()const{return transaction_.state();}
    bool available()const{return transaction_.available();}
    bool dirty()const{return transaction_.dirty();}
    bool may_submit(const std::string& intent)const{return transaction_.may_submit(intent);}
    const Json& last_result()const{return transaction_.last_result();}
    std::optional<std::uint64_t> revision()const{return transaction_.revision();}
private:
    struct State {Json scene;std::vector<std::string> selection;};
    struct Change {State before,after;std::size_t bytes;};
    SettingsDraft transaction_;
    std::vector<std::string> selected_;
    std::deque<Change> undo_,redo_;
    void clear_history();
    void settled(bool);
    bool travel(bool forward);
};
}
