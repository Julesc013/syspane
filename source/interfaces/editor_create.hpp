#pragma once
#include "editor_content.hpp"
namespace syspane::interfaces {
struct CreateInput {
    std::string kind;
    std::map<std::string,std::string> fields;
    std::optional<std::string> parent;
    Json asset;
};
CreateInput create_input(const std::string& kind);
InsertWidget create_widget(const Json& scene,const CreateInput&,const std::string& id,const Json& root_display,const ContentChoices&);
}
