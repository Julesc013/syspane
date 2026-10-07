from pathlib import Path
import json
r=Path.cwd()
def change(path,old,new):
 p=r/path;s=p.read_text();assert old in s,(path,old[:80]);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
change('source/interfaces/editor_form_linux.cpp','#include "editor_content_form.hpp"','#include "editor_content_form.hpp"\n#include "editor_binding_form.hpp"')
change('source/interfaces/editor_form_linux.cpp','std::unique_ptr<EditorContentForm> content;','std::unique_ptr<EditorContentForm> content;std::unique_ptr<EditorBindingForm> binding;')
change('source/interfaces/editor_form_linux.cpp','&&(!content||!content->opened());','&&(!content||!content->opened())&&(!binding||!binding->opened());')
change('source/interfaces/editor_form_linux.cpp','if(content&&content->opened())active=false;','if(id=="bindings")active=enabled&&selected&&draft.scene()->at("schema_version")=="0.3.0"&&(selected->at("kind")=="value"||selected->at("kind")=="status"||selected->at("kind")=="chart"||selected->at("kind")=="table");\n            if((content&&content->opened())||(binding&&binding->opened()))active=false;')
change('source/interfaces/editor_form_linux.cpp','if(id=="content"){ready();','if(id=="bindings"){ready();gesture.reset();need(draft.selection().size()==1,"editor.selection");\n            if(!binding)binding=std::make_unique<EditorBindingForm>(root,[this](const std::vector<SceneEdit>& edits){return draft.execute(edits);},[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});\n            binding->open(authored_widget(*draft.scene(),draft.selection()[0]));sync();}\n        else if(id=="content"){ready();')
change('source/interfaces/editor_form_linux.cpp','if(content)content->erase();draft.close();','if(content)content->erase();if(binding)binding->erase();draft.close();')
change('source/interfaces/editor_form_linux.cpp','if(i.content)i.content->erase();','if(i.content)i.content->erase();if(i.binding)i.binding->erase();')
change('source/interfaces/editor_form_linux.cpp','{"content","Content"}','{"content","Content"},{"bindings","Bindings"}')
change('CMakeLists.txt','source/interfaces/editor_content.cpp)','source/interfaces/editor_content.cpp source/interfaces/editor_binding.cpp)')
change('CMakeLists.txt','source/interfaces/editor_content_form_linux.cpp)','source/interfaces/editor_content_form_linux.cpp source/interfaces/editor_binding_form_linux.cpp)')
change('CMakeLists.txt','tests/editor/content_properties_tests.cpp)','tests/editor/content_properties_tests.cpp tests/editor/binding_authoring_tests.cpp)')
change('CMakeLists.txt','CONTENT-CHOICES CONTENT-POLICY)','CONTENT-CHOICES CONTENT-POLICY BINDING-MAPPING BINDING-NUMBERS BINDING-ATOMIC BINDING-BOUNDS BINDING-HISTORY BINDING-POLICY)')
change('tests/editor/editor_draft_tests.cpp','void run_content_properties(', 'void run_binding_authoring(const std::string&,const std::string&);\nvoid run_content_properties(')
change('tests/editor/editor_draft_tests.cpp','if(name.substr(0,8)=="CONTENT-")', 'if(name.substr(0,8)=="BINDING-"){run_binding_authoring(name.substr(8),root);return;}\n    if(name.substr(0,8)=="CONTENT-")')
p=r/'build-support/components.json';v=json.loads(p.read_text())
def add(v):
 if isinstance(v,list):
  for it in v:add(it)
  if 'source/interfaces/editor_content.cpp' in v:v.append('source/interfaces/editor_binding.cpp')
  if 'source/interfaces/editor_content_form_linux.cpp' in v:v.append('source/interfaces/editor_binding_form_linux.cpp')
  if 'source/interfaces/editor_content.hpp' in v:v.append('source/interfaces/editor_binding.hpp')
  if 'source/interfaces/editor_content_form.hpp' in v:v.append('source/interfaces/editor_binding_form.hpp')
 elif isinstance(v,dict):
  for it in v.values():add(it)
add(v);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for src,dst in [('properties_step.py','binding_step.py'),('properties_flow.py','binding_flow.py')]:
 s=(r/'out/campaign'/src).read_text().replace('w-10-content-properties','w-10-binding-authoring').replace('properties_step.py','binding_step.py').replace('properties-execution','binding-execution').replace('^editor[.]CONTENT-','^editor[.]BINDING-')
 (r/'out/campaign'/dst).write_text(s,encoding='utf-8',newline='\n')
