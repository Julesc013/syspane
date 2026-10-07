#pragma once
#include "settings_draft.hpp"
#include <fstream>
namespace settings_fixture {
namespace c=syspane::configuration;namespace ui=syspane::interfaces;using c::Json;
inline Json read(const std::string& path){std::ifstream f(path);if(!f.good())throw std::runtime_error("settings resource fixture unavailable");Json v;f>>v;return v;}
inline std::string hex(const std::string& value){
    if(value.size()%2)throw std::runtime_error("fixture hex length");
    std::string bytes;
    const auto digit=[](char c)->unsigned{if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;throw std::runtime_error("fixture hex digit");};
    for(std::size_t i=0;i<value.size();i+=2)bytes.push_back(static_cast<char>((digit(value[i])<<4)|digit(value[i+1])));
    return bytes;
}
struct Fixture {
    Json document;c::Authored authored;std::shared_ptr<const c::ContentCatalog> catalog;
    explicit Fixture(const std::string& root,const std::string& path="tests/configuration/settings-content-fixture.json"):document(read(root+"/"+path)),authored{document["authored"]["settings"],document["authored"]["scene"]}{
        std::vector<c::ContentPackage> packages;
        for(const auto& row:document["packages"]){c::ContentPackage package;package.manifest=row["manifest"];
            for(auto it=row["assets_hex"].begin();it!=row["assets_hex"].end();++it)package.assets[it.key()]=hex(it.value().get<std::string>());
            packages.push_back(std::move(package));}
        catalog=std::make_shared<const c::ContentCatalog>(std::move(packages));
    }
    ui::SettingsResources resources()const{return {catalog,document["selection"],{"scene.content"}};}
};
}
