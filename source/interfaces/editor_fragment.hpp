#pragma once
#include "editor_draft.hpp"
namespace syspane::interfaces::detail {
// Internal transformations. EditorDraft owns authority, lifetime and adoption.
std::string selection_fragment(const Json&,const std::vector<std::string>&);
std::vector<std::string> paste_fragment(Json&,const PasteWidgets&);
}
