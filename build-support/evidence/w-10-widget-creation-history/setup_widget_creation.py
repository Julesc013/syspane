from pathlib import Path
import json
r=Path.cwd()
def change(p,old,new):
 path=r/p;s=path.read_text();assert old in s,(p,old[:60]);path.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
change('source/interfaces/editor_form_linux.cpp','#include "editor_binding_form.hpp"','#include "editor_binding_form.hpp"\n#include "editor_create_form.hpp"')
change('source/interfaces/editor_form_linux.cpp','std::unique_ptr<EditorBindingForm> binding;','std::unique_ptr<EditorBindingForm> binding;std::unique_ptr<EditorCreateForm> creation;')
change('source/interfaces/editor_form_linux.cpp','&&(!binding||!binding->opened());','&&(!binding||!binding->opened())&&(!creation||!creation->opened());')
change('source/interfaces/editor_form_linux.cpp','if((content&&content->opened())||(binding&&binding->opened()))active=false;','if(id=="insert")active=enabled&&draft.scene()&&draft.scene()->at("schema_version")=="0.3.0";\n            if((content&&content->opened())||(binding&&binding->opened())||(creation&&creation->opened()))active=false;')
change('source/interfaces/editor_form_linux.cpp','if(id=="bindings"){ready();', '''if(id=="insert"){ready();gesture.reset();need(resources.has_value(),"editor.resources");
            if(!creation)creation=std::make_unique<EditorCreateForm>(root,[this](const CreateInput& input){
                need(resources.has_value(),"editor.resources");const auto snapshot=resources->catalog->resources(resources->selection,{settings,*draft.scene()});
                auto edit=create_widget(*draft.scene(),input,"editor:proposed",{{"local_id",viewport().id}},content_choices(*snapshot));edit.widget["id"]=actions.widget_id();return draft.execute({edit});
            },[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});
            const auto snapshot=resources->catalog->resources(resources->selection,{settings,*draft.scene()});creation->open(*draft.scene(),draft.selection(),content_choices(*snapshot));sync();}
        else if(id=="bindings"){ready();''')
change('source/interfaces/editor_form_linux.cpp','if(binding)binding->erase();draft.close();','if(binding)binding->erase();if(creation)creation->erase();draft.close();')
change('source/interfaces/editor_form_linux.cpp','if(i.binding)i.binding->erase();','if(i.binding)i.binding->erase();if(i.creation)i.creation->erase();')
# Keep the existing Add text action and place the general Add action with the second toolbar.
change('source/interfaces/editor_form_linux.cpp','{{"align-left","Align left"}', '{{"insert","Add widget"},{"align-left","Align left"}')
change('source/interfaces/editor_form_linux.cpp','    if(i.binding)i.binding->erase();if(i.creation)i.creation->erase();\n','    if(i.binding)i.binding->erase();\n    if(i.creation)i.creation->erase();\n')
change('CMakeLists.txt','source/interfaces/editor_binding.cpp)','source/interfaces/editor_binding.cpp source/interfaces/editor_create.cpp)')
change('CMakeLists.txt','source/interfaces/editor_binding_form_linux.cpp)','source/interfaces/editor_binding_form_linux.cpp source/interfaces/editor_create_form_linux.cpp)')
change('CMakeLists.txt','tests/editor/binding_authoring_tests.cpp)','tests/editor/binding_authoring_tests.cpp tests/editor/widget_creation_tests.cpp)')
change('CMakeLists.txt','BINDING-TEXT)','BINDING-TEXT CREATE-KINDS CREATE-PARENTS CREATE-HISTORY CREATE-ATOMIC CREATE-BOUNDS CREATE-POLICY)')
change('tests/editor/editor_draft_tests.cpp','void run_binding_authoring(', 'void run_widget_creation(const std::string&,const std::string&);\nvoid run_binding_authoring(')
change('tests/editor/editor_draft_tests.cpp','if(name.substr(0,8)=="BINDING-")', 'if(name.substr(0,7)=="CREATE-"){run_widget_creation(name.substr(7),root);return;}\n    if(name.substr(0,8)=="BINDING-")')
p=r/'build-support/components.json';v=json.loads(p.read_text())
def add(v):
 if isinstance(v,list):
  for it in v:add(it)
  for old,new in [('source/interfaces/editor_binding.cpp','source/interfaces/editor_create.cpp'),('source/interfaces/editor_binding_form_linux.cpp','source/interfaces/editor_create_form_linux.cpp'),('source/interfaces/editor_binding.hpp','source/interfaces/editor_create.hpp'),('source/interfaces/editor_binding_form.hpp','source/interfaces/editor_create_form.hpp'),('tests/editor/binding_authoring_tests.cpp','tests/editor/widget_creation_tests.cpp')]:
   if old in v:v.append(new)
 elif isinstance(v,dict):
  for it in v.values():add(it)
add(v);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for src,dst in [('binding_step.py','creation_step.py'),('binding_flow.py','creation_flow.py')]:
 s=(r/'out/campaign'/src).read_text().replace('w-10-binding-authoring','w-10-widget-creation').replace(",r/'spec/delivery/packages/w-10-binding-text.md'",'').replace('binding_step.py','creation_step.py').replace('binding-execution','creation-execution').replace('^editor[.]BINDING-','^editor[.]CREATE-').replace("'bindings','properties','test'","'creation','bindings','properties','test'").replace("'properties','bindings')","'properties','bindings','creation')").replace("'snap','properties','bindings')","'snap','properties','bindings','creation')")
 if src.endswith('step.py'):
  s=s.replace("command={'bindings':","command={'creation':['ctest','--preset',profile,'-R','^native[.]EDITOR-WIDGET-CREATION$','--output-on-failure'],'bindings':").replace("artifact_name={'bindings':","artifact_name={'creation':'syspane_editor_window','bindings':")
 (r/'out/campaign'/dst).write_text(s,encoding='utf-8',newline='\n')
