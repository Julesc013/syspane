#pragma once
#include "settings_draft.hpp"
#include <memory>
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
class SettingsForm {
public:
    struct Actions {
        std::function<std::string()> request_id;
        std::function<void(const EditRequest&)> submit,cancel;
        std::function<void()> reload;
    };
    using Translator=std::function<std::string(const std::string&,const std::string&)>;
    SettingsForm(configuration::Authority,configuration::Policy,configuration::Authored,std::string epoch,Actions,Translator={},std::optional<SettingsResources> resources={},bool large_commands=false);
    ~SettingsForm();
    SettingsForm(const SettingsForm&)=delete;SettingsForm& operator=(const SettingsForm&)=delete;
    GtkWidget* widget()const;
    void complete(std::uint64_t,const Json&);
    void reconciled(std::uint64_t,const std::string& query_id,const std::string& current_epoch,const Json&);
    void disconnected();
    void policy(configuration::Policy);
    void reload(configuration::Authored,std::string epoch,std::optional<SettingsResources> resources={});
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
