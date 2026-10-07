from pathlib import Path
r=Path(__file__).resolve().parents[2]
def edit(path,old,new):
 p=r/path;s=p.read_text();assert old in s,(path,old);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
for name in ('source/interfaces/editor_content_form.hpp','source/interfaces/editor_content_form_linux.cpp'):
 edit(name,'std::function<void(const std::vector<SceneEdit>&)>','std::function<bool(const std::vector<SceneEdit>&)>')
 if name.endswith('.hpp'):edit(name,'std::function<void()> finished','std::function<void(bool)> finished')
 else:
  edit(name,'std::function<void()> finished,failed;','std::function<void(bool)> finished;std::function<void()> failed;')
  edit(name,'std::function<void()> f,std::function<void()> e','std::function<void(bool)> f,std::function<void()> e')
  edit(name,'std::function<void()> finished,std::function<void()> failed','std::function<void(bool)> finished,std::function<void()> failed')
  edit(name,'void finish(){erase();','void finish(bool changed=false){erase();')
  edit(name,'finished();','finished(changed);')
  edit(name,'apply(edits);finish();','const bool changed=apply(edits);finish(changed);')
  edit(name,'gtk_label_set_text(GTK_LABEL(error),e.what());','const std::string code=e.what();gtk_label_set_text(GTK_LABEL(error),code=="editor.content_number"?"Enter a finite decimal number (an exponent is allowed).":code=="editor.content_integer"?"Enter a whole number within the field limits.":code=="editor.content_axis"?"Maximum must be greater than minimum.":code=="editor.content_dimensions"?"Image dimensions must be between 1 and 4096 DIP.":"Content could not be applied. Check values, resources and current permissions.");')
edit('source/interfaces/editor_form_linux.cpp','[&i](const std::vector<SceneEdit>& edits){i.draft.execute(edits);},[&i]{i.changed();}','[&i](const std::vector<SceneEdit>& edits){return i.draft.execute(edits);},[&i](bool changed){if(changed)i.changed();else i.sync();}')
edit('tests/editor/editor_window.cpp','if(properties){data_token=form->attach("P1",fixture::link(),now()).token;','if(properties){auto link=fixture::link();link.channel="inspector";data_token=form->attach("P1",link,now()).token;')
edit('tests/editor/editor_window.cpp','fixture::wire(document,fixture::link())','fixture::wire(document,link)')
edit('tests/editor/native_content_properties.py',"h.click('undo');h.wait(lambda:not h.sensitive('apply'));h.wait(lambda:region(h,kind)==baseline);h.click('redo');", "h.click('undo');h.wait(lambda:not h.sensitive('apply'));h.wait(lambda:'Window 60000 ms | linear' in canvas(h) if kind=='chart' else region(h,kind)==baseline);h.click('redo');")
