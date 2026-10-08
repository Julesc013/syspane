from pathlib import Path
import json
r=Path.cwd()
def edit(n,old,new):
 p=r/n;s=p.read_text(encoding='utf-8');assert old in s,(n,old);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
edit('CMakeLists.txt','preset theme)','preset theme theme-v0.2)')
edit('CMakeLists.txt','source/configuration/authored_equal.cpp','source/configuration/authored_equal.cpp source/configuration/theme_font.cpp')
edit('build-support/generate_authored_schemas.py',"'preset','theme')","'preset','theme','theme-v0.2')")
edit('source/configuration/authored.cpp','preset_schema,theme_schema})','preset_schema,theme_schema,theme_v0_2_schema})')
edit('source/configuration/authored.cpp','const auto name="0.1.0/"+kind;structural(value,name.c_str(),kind=="content-catalog"?16384:(kind=="content-package"?65536:262144));','''const bool typography=kind=="theme"&&value.is_object()&&value.value("schema_version",Json())=="0.2.0";
    const auto name=std::string(typography?"0.2.0/":"0.1.0/")+kind;structural(value,name.c_str(),kind=="content-catalog"?16384:(kind=="content-package"?65536:262144));
    if(typography){
        const auto check=[](const Json& font){const auto& family=font.at("family").get_ref<const std::string&>();require(family.size()<=512,"theme.family");
            for(std::size_t i=0;i+1<family.size();++i)if(static_cast<unsigned char>(family[i])==0xc2){const auto next=static_cast<unsigned char>(family[i+1]);require(next<0x80||next>0x9f,"theme.family");}};
        check(value.at("font"));if(value.contains("font_roles"))for(const auto& font:value.at("font_roles"))check(font);
    }''')
edit('source/configuration/content.cpp','result->theme_=entries_[*theme].document;','result->theme_=entries_[*theme].document;\n    if(result->theme_["schema_version"]=="0.2.0")result->required_.insert("theme.typography");')
edit('source/configuration/content.cpp','need(id==resources.theme()["theme_id"],"content.theme");','need(id==resources.theme()["theme_id"],"content.theme");\n    if(resources.theme()["schema_version"]=="0.2.0")need(resources.required().count("theme.typography")!=0,"resource.contract");')
# Preset preview also has a legacy command path without a resource envelope.
edit('source/configuration/content.cpp','result.theme=entries_[*theme].document;','result.theme=entries_[*theme].document;\n    if(result.theme["schema_version"]=="0.2.0")need(capabilities.count("theme.typography")&&!policy.denied_capabilities.count("theme.typography"),"content.capability");')
edit('source/rendering/native_text.hpp','contrast="authored";','contrast="authored",role="body";')
edit('source/rendering/native_text_linux.cpp','#include "native_text.hpp"','#include "native_text.hpp"\n#include "theme_font.hpp"')
edit('source/rendering/native_text_linux.cpp','configuration::validate_content_document(r.theme,"theme");','const auto resolved=configuration::theme_font(r.theme,r.role);')
edit('source/rendering/native_text_linux.cpp','const auto family=r.theme.at("font").at("family").get<std::string>();','const auto& family=resolved.family;')
edit('source/rendering/native_text_linux.cpp','pango_font_description_set_weight(font.get(),PANGO_WEIGHT_NORMAL);','pango_font_description_set_weight(font.get(),static_cast<PangoWeight>(resolved.weight));')
edit('source/rendering/native_text_linux.cpp','pango_font_description_set_style(font.get(),PANGO_STYLE_NORMAL);','pango_font_description_set_style(font.get(),resolved.style=="italic"?PANGO_STYLE_ITALIC:resolved.style=="oblique"?PANGO_STYLE_OBLIQUE:PANGO_STYLE_NORMAL);')
edit('source/rendering/native_text_linux.cpp','r.theme.at("font").at("size_dip").get<double>()*PANGO_SCALE','resolved.size_dip*PANGO_SCALE')
edit('source/rendering/scene_surface.cpp','need(allowed(),"policy.denied");c::authorize_resources(*config.resources,policy,config.capabilities);','need(allowed(),"policy.denied");c::authorize_resources(*config.resources,policy,config.capabilities);\n        need(config.resources->theme().at("schema_version")!="0.2.0","surface.typography_unavailable");')
edit('source/application/text_probe.cpp','r.text=j.at("text");r.theme=j.at("theme");','''r.text=j.at("text");r.theme=j.at("theme");r.role=j.value("role",r.role);
        if(j.value("fault",std::string())=="ignore-role")r.role="body";
        if(j.value("fault",std::string())=="ignore-weight"){
            r.theme["font"]["weight"]=400;
            if(r.theme.contains("font_roles"))for(auto& f:r.theme["font_roles"])f["weight"]=400;
        }''')
p=r/'build-support/components.json';v=json.loads(p.read_bytes());component=next(x for x in v['components'] if x['target']=='syspane_authored');component['sources'].append('source/configuration/theme_font.cpp');component['public_interfaces'].append('source/configuration/theme_font.hpp');p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Implemented versioned theme validation/resolution, resource admission and native font selection; scene composition remains explicitly gated.')
