#pragma once
#include "editor_draft.hpp"
namespace syspane::interfaces {
struct PredicateInput {std::string field,op,type,value;std::string encoding="literal";};
struct SortInput {std::string field,direction;};
// Private authored input only; no model snapshot, provider discovery or pin mapping.
struct BindingInput {
    std::map<std::string,std::string> fields;
    std::vector<PredicateInput> predicates;
    std::vector<SortInput> sort;
};
BindingInput binding_input(const Json&);
Json binding_value(const PredicateInput&);
Json binding_text(const std::string& value,const std::string& encoding);
Json binding_descriptor(const BindingInput&,const Json& original,const std::string& mode);
WidgetContentEdit binding_edit(const Json& widget,const BindingInput&,const std::vector<std::string>& fields);
}
