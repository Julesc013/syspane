from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
p=r/'source/interfaces/editor_form_linux.cpp';s=p.read_text()
def replace(old,new):
    global s
    assert old in s,old[:70];s=s.replace(old,new)
replace('#include "editor_create_form.hpp"','#include "editor_create_form.hpp"\n#include "editor_layout_form.hpp"')
replace('std::unique_ptr<EditorCreateForm> creation;','std::unique_ptr<EditorCreateForm> creation;std::unique_ptr<EditorLayoutForm> layout_form;int field_variant=-2;GtkWidget* variant_label=nullptr;')
replace('&&(!creation||!creation->opened());','&&(!creation||!creation->opened())&&(!layout_form||!layout_form->opened());')
replace('return n&&n->variant==-1&&authored_widget(*draft.scene(),id)["layout"]["base"]["kind"]=="fixed";','return n&&active_layout(id).at("kind")=="fixed";')
replace('            fields_dirty=false;\n            for(auto& row:fields)', '            fields_dirty=false;field_variant=selected&&fixed(draft.selection()[0])?node(draft.selection()[0])->variant:-2;\n            for(auto& row:fields)')
replace('else if((*selected)["layout"]["base"]["kind"]=="fixed")value=(*selected)["layout"]["base"][row.first].dump();','else if(fixed(draft.selection()[0]))value=active_layout(draft.selection()[0]).at(row.first).dump();')
replace('if(id=="insert")active=', 'if(id=="layout")active=enabled&&selected;\n            if(id=="insert")active=')
replace('||(creation&&creation->opened()))active=false;', '||(creation&&creation->opened())||(layout_form&&layout_form->opened()))active=false;')
replace('message(value);guide_feedback();updating=false;', 'message(value);guide_feedback();if(variant_label){std::string variant;if(selected){const auto* n=node(draft.selection()[0]);variant=n?(n->variant<0?"Active layout: Base":"Active layout: Breakpoint "+std::to_string(n->variant+1)):"Not on this display";}gtk_label_set_text(GTK_LABEL(variant_label),variant.c_str());}updating=false;')
replace('        std::vector<SceneEdit> edits{WidgetPropertyEdit{id,WidgetProperty::title', '        need(field_variant==-2||(node(id)&&node(id)->variant==field_variant),"editor.layout_changed");\n        std::vector<SceneEdit> edits{WidgetPropertyEdit{id,WidgetProperty::title')
replace('if(fixed(id)){auto layout=w["layout"];for(const char* key:{"x","y","width","height"})layout["base"][key]=number(text(fields[key]));edits.push_back', 'if(fixed(id)){auto layout=w["layout"];const int index=node(id)->variant;auto& target=index<0?layout["base"]:layout["breakpoints"][static_cast<std::size_t>(index)]["layout"];for(const char* key:{"x","y","width","height"})target[key]=number(text(fields[key]));edits.push_back')
replace('const s::Node* first=nullptr;', 'const s::Node* first=nullptr;std::vector<int> indices;')
replace('const auto& b=authored_widget(*draft.scene(),selected_id)["layout"]["base"];', 'const auto& b=active_layout(selected_id);indices.push_back(n->variant);')
replace('Spacing::horizontal:Spacing::vertical}});','Spacing::horizontal:Spacing::vertical,indices}});')
replace('AlignWidgets{ids,kinds.at(id)}','AlignWidgets{ids,kinds.at(id),indices}')
replace('        else if(id=="properties")properties();', '''        else if(id=="layout"){ready();gesture.reset();need(draft.selection().size()==1,"editor.selection");
            if(!layout_form)layout_form=std::make_unique<EditorLayoutForm>(root,[this](const std::vector<SceneEdit>& edits){return draft.execute(edits);},[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});
            layout_form->open(*draft.scene(),draft.selection()[0]);sync();}
        else if(id=="properties")properties();''')
replace('const auto& base=authored_widget(*draft.scene(),g.nodes[0].id)["layout"]["base"];','const auto& base=active_layout(g.nodes[0].id);')
replace('base["height"].get<double>()+g.dy*scale}});','base["height"].get<double>()+g.dy*scale,g.nodes[0].variant}});')
replace('else execute({MoveWidgets{draft.selection(),g.dx*scale,g.dy*scale}});','else {std::vector<int> indices;for(const auto& n:g.nodes)indices.push_back(n.variant);execute({MoveWidgets{draft.selection(),g.dx*scale,g.dy*scale,indices}});}')
replace('const auto& b=authored_widget(*draft.scene(),id)["layout"]["base"];execute({ResizeWidget{id,b["width"].get<double>()+x,b["height"].get<double>()+y}});','const auto& b=active_layout(id);execute({ResizeWidget{id,b["width"].get<double>()+x,b["height"].get<double>()+y,node(id)->variant}});')
replace('else execute({MoveWidgets{draft.selection(),x,y}});','else {std::vector<int> indices;for(const auto& id:draft.selection())indices.push_back(node(id)->variant);execute({MoveWidgets{draft.selection(),x,y,indices}});}')
replace('if(draft.selection().size()==1){cairo_rectangle', 'if(draft.selection().size()==1&&fixed(n.id)){cairo_rectangle')
replace('if(creation)creation->erase();', 'if(creation)creation->erase();if(layout_form)layout_form->erase();')
replace('if(i.creation)i.creation->erase();','if(i.creation)i.creation->erase();if(i.layout_form)i.layout_form->erase();')
replace('code=="editor.number"?"Enter a number using digits and an optional decimal point.":','code=="editor.number"?"Enter a number using digits and an optional decimal point.":code=="editor.layout_changed"?"Layout changed; Revert fields before applying.":')
replace('{"content","Content"},{"bindings","Bindings"}', '{"content","Content"},{"bindings","Bindings"},{"layout","Layout"}')
replace('    auto* bottom=gtk_box_new', '    i.variant_label=i.label("");accessible(i.variant_label,"","editor.variant");gtk_box_pack_start(GTK_BOX(side),i.variant_label,FALSE,FALSE,0);\n    auto* bottom=gtk_box_new')
replace('i.preview();i.sync();}\nrecovery::DataAttachment EditorForm::attach', 'i.preview();i.sync(!i.fields_dirty);}\nrecovery::DataAttachment EditorForm::attach')
p.write_text(s,encoding='utf-8',newline='\n')
p=r/'CMakeLists.txt';s=p.read_text().replace('source/interfaces/editor_create.cpp)','source/interfaces/editor_create.cpp source/interfaces/editor_layout.cpp)').replace('source/interfaces/editor_create_form_linux.cpp)','source/interfaces/editor_create_form_linux.cpp source/interfaces/editor_layout_form_linux.cpp)').replace('tests/editor/widget_creation_tests.cpp)','tests/editor/widget_creation_tests.cpp tests/editor/layout_authoring_tests.cpp)').replace('CREATE-POLICY)','CREATE-POLICY LAYOUT-KINDS LAYOUT-VARIANTS LAYOUT-ORDER LAYOUT-DISPLAY LAYOUT-BOUNDS LAYOUT-ATOMIC LAYOUT-POLICY LAYOUT-GEOMETRY)');p.write_text(s,encoding='utf-8',newline='\n')
p=r/'build-support/components.json';v=json.loads(p.read_text());components=v['components']
for target,fields in {'syspane_editor_draft':{'public_interfaces':['source/interfaces/editor_layout.hpp'],'sources':['source/interfaces/editor_layout.cpp']},'syspane_editor_tests':{'sources':['tests/editor/layout_authoring_tests.cpp']},'syspane_editor_form':{'private_interfaces':['source/interfaces/editor_layout_form.hpp'],'sources':['source/interfaces/editor_layout_form_linux.cpp']}}.items():
    component=next(c for c in components if c['target']==target)
    for key,names in fields.items():component[key]+=names
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'tests/editor/editor_draft_tests.cpp';s=p.read_text().replace('void run_widget_creation(', 'void run_layout_authoring(const std::string&,const std::string&);\nvoid run_widget_creation(',1).replace('    if(name.substr(0,7)=="CREATE-")','    if(name.substr(0,7)=="LAYOUT-"){run_layout_authoring(name.substr(7),root);return;}\n    if(name.substr(0,7)=="CREATE-")');p.write_text(s,encoding='utf-8',newline='\n')
