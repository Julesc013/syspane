from pathlib import Path
r=Path.cwd();p=r/'source/interfaces/editor_form_linux.cpp';s=p.read_text();assert '#include "editor_theme_form.hpp"' not in s
s=s.replace('#include "editor_visibility_form.hpp"','#include "editor_visibility_form.hpp"\n#include "editor_theme_form.hpp"')
s=s.replace('std::optional<SettingsResources> resources;', 'std::set<std::string> capabilities;')
s=s.replace('resources(std::move(r))','capabilities(std::move(r.capabilities))')
s=s.replace('std::unique_ptr<EditorVisibilityForm> visibility;', 'std::unique_ptr<EditorThemeForm> theme;std::unique_ptr<EditorVisibilityForm> visibility;')
s=s.replace('if(!large_frames||!resources)return false;', 'if(!large_frames||!draft.resources())return false;').replace('resources->capabilities','capabilities')
anchor='    void presentation(const v::SurfaceFrame& frame)'
s=s.replace(anchor,'''    bool typography_supported()const{if(!visibility_supported()||!current.available)return false;for(const char* cap:{"theme.typography","configuration.theme-overrides"})if(!capabilities.count(cap)||current.denied_capabilities.count(cap))return false;return true;}
'''+anchor)
s=s.replace('&&(!visibility||!visibility->opened());','&&(!visibility||!visibility->opened())&&(!theme||!theme->opened());')
s=s.replace('if(!draft.available()||!resources){settings=nullptr;resources.reset();', 'if(!draft.available()||!draft.resources()){settings=nullptr;capabilities.clear();')
s=s.replace('v::SurfaceConfig cfg;cfg.authored={settings,*draft.scene()};cfg.resources=resources->catalog->resources(resources->selection,cfg.authored);cfg.topology=topology;cfg.capabilities=capabilities;cfg.experimental_visibility=visibility_supported();', '''v::SurfaceConfig cfg;cfg.authored={settings,*draft.scene()};const auto* borrowed=draft.resources();auto catalog=c::ContentCatalog::retained(*borrowed);
        cfg.resources=borrowed->selection().contains("schema_version")?catalog.theme_resources(borrowed->selection(),cfg.authored):catalog.resources(borrowed->selection(),cfg.authored);
        cfg.topology=topology;cfg.capabilities=capabilities;cfg.experimental_visibility=visibility_supported();cfg.experimental_typography=typography_supported();''')
s=s.replace('if(id=="visibility")active=', 'if(id=="fonts")active=enabled&&draft.theme_fonts_available();\n            if(id=="visibility")active=')
s=s.replace('||(visibility&&visibility->opened()))active=false;', '||(visibility&&visibility->opened())||(theme&&theme->opened()))active=false;')
s=s.replace('        const char* lock_label=', '''        gtk_widget_set_tooltip_text(buttons.at("fonts"),!typography_supported()?"Font editing is unavailable in this connection's capabilities.":fields_dirty?"Set or revert property fields before editing fonts.":!draft.theme_fonts_available()?"Font editing is unavailable while a request, conflict or current permission prevents it.":"Edit the scene's base font and role overrides.");
        const char* lock_label=''')
s=s.replace('need(resources.has_value(),"editor.resources");const auto snapshot=resources->catalog->resources(resources->selection,{settings,*draft.scene()});','need(draft.resources()!=nullptr,"editor.resources");const auto* snapshot=draft.resources();')
s=s.replace('need(resources.has_value(),"editor.resources");','need(draft.resources()!=nullptr,"editor.resources");')
s=s.replace('const auto snapshot=resources->catalog->resources(resources->selection,{settings,*draft.scene()});','const auto* snapshot=draft.resources();')
s=s.replace('        else if(id=="visibility"){', '''        else if(id=="fonts"){ready();gesture.reset();need(draft.theme_fonts_available(),"editor.theme_unavailable");
            if(!theme)theme=std::make_unique<EditorThemeForm>(root,[this](const std::optional<Json>& candidate){need(draft.theme_fonts_available(),"editor.theme_unavailable");return candidate?draft.set_theme_fonts(candidate->at("font"),candidate->value("font_roles",Json())):draft.execute({SceneThemeEdit{std::nullopt}});},[this](bool changed){if(changed)this->changed();else sync();},[this]{shut();});
            theme->open(draft.resources()->theme());sync();}
        else if(id=="visibility"){''')
s=s.replace('if(visibility)visibility->erase();','if(visibility)visibility->erase();if(theme)theme->erase();')
s=s.replace('if(i.visibility)i.visibility->erase();','if(i.visibility)i.visibility->erase();if(i.theme)i.theme->erase();')
s=s.replace('resources.reset();','capabilities.clear();')
s=s.replace('i.resources=std::move(resources);','i.capabilities=std::move(resources.capabilities);')
s=s.replace('{"layout","Layout"}})button(top', '{"layout","Layout"},{"fonts","Fonts"}})button(top')
assert 'resources->' not in s and 'i.resources' not in s
p.write_text(s,encoding='utf-8',newline='\n')
p=r/'source/interfaces/editor_theme_form_linux.cpp';s=p.read_text().replace('from 6 to 96 DIP','from 9 to 72 DIP');p.write_text(s,encoding='utf-8',newline='\n')
