#include "content_reader_linux.hpp"
#include <iostream>
namespace c=syspane::configuration;namespace p=syspane::protocol;
int main(int argc,char** argv){try{
    if(argc<3||argc>66)throw p::Error("probe.arguments");
    const std::string mode=argv[1];if(mode!="preview"&&mode!="snapshot"&&mode!="denied")throw p::Error("probe.arguments");
    std::vector<std::string> paths;for(int i=2;i<argc;++i)paths.emplace_back(argv[i]);
    const c::ContentCatalog catalog(syspane::platform::read_content_packages(paths));
    if(mode=="snapshot")std::cout<<"{\"ready\":true}\n"<<std::flush;
    std::string line;char ch=0;while(std::cin.get(ch)&&ch!='\n'){if(line.size()>=524288)throw p::Error("probe.size");line+=ch;}
    const auto input=c::parse_content_json(line,524288);if(!p::members(input,{"settings","scene","package","preset"}))throw p::Error("probe.input");
    c::Policy policy;policy.available=true;policy.revision=7;if(mode=="denied")policy.denied_capabilities.insert("settings.preview");
    const auto plan=catalog.preview(input["package"],input["preset"],{input["settings"],input["scene"]},"P",{true,"console",{"console"}},policy,{"scene.selector","scene.content"});
    std::cout<<p::Json({{"command",plan.command},{"settings",plan.candidate.settings},{"scene",plan.candidate.scene},{"theme",plan.theme},
        {"packages",plan.package_pins},{"presets",plan.preset_pins},{"origins",plan.setting_origins},{"missing_optional",plan.missing_optional}}).dump()<<'\n';return 0;
}catch(const p::Error& e){std::cout<<p::Json({{"error",e.what()}}).dump()<<'\n';return 2;}
catch(const std::exception&){std::cout<<"{\"error\":\"probe.failure\"}\n";return 3;}}
