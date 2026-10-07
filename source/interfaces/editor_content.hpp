#pragma once
#include "editor_draft.hpp"
namespace syspane::interfaces {
struct ContentChoice {std::string label;Json value;};
struct ContentChoices {std::vector<ContentChoice> images,themes;};
struct ContentColumn {std::size_t original;std::string label;};
// Private input buffer only. EditorDraft remains the validation/history owner.
struct ContentInput {
    std::map<std::string,std::string> fields;
    std::vector<ContentColumn> columns;
    Json asset;
};
ContentChoices content_choices(const configuration::ResourceSet&);
ContentInput content_input(const Json& widget);
WidgetContentEdit content_edit(const Json& widget,const ContentInput&,const ContentChoices&);
SceneThemeEdit content_theme(const Json& id,const ContentChoices&);
double content_number(const std::string&);
unsigned content_integer(const std::string&,unsigned minimum,unsigned maximum);
}
