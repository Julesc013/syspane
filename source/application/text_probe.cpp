#include "native_text.hpp"
#include <fstream>
#include <iostream>
#include <thread>

namespace {
using syspane::configuration::Json;
Json rect(syspane::scene::Rect r){return Json::array({r.x,r.y,r.width,r.height});}
}
namespace {
Json run(const Json& j,const std::string& path,syspane::rendering::TextSession* session=nullptr){
    try{
        syspane::rendering::TextRequest r;
        r.text=j.at("text");r.theme=j.at("theme");r.role=j.value("role",r.role);
        if(j.value("fault",std::string())=="ignore-role")r.role="body";
        if(j.value("fault",std::string())=="ignore-weight"){
            r.theme["font"]["weight"]=400;
            if(r.theme.contains("font_roles"))for(auto& f:r.theme["font_roles"])f["weight"]=400;
        }
        if(j.contains("text_hex")){
            const auto hex=j.at("text_hex").get<std::string>();
            if(hex.size()>8192||hex.size()%2)throw syspane::protocol::Error("text.input");
            r.text.clear();
            for(std::size_t i=0;i<hex.size();i+=2){
                std::size_t used=0;const auto byte=std::stoul(hex.substr(i,2),&used,16);
                if(used!=2||byte>255)throw syspane::protocol::Error("text.input");
                r.text.push_back(static_cast<char>(byte));
            }
        }
        r.language=j.value("language",r.language);r.token=j.value("token",r.token);r.contrast=j.value("contrast",r.contrast);
        r.numerator=j.value("numerator",r.numerator);r.denominator=j.value("denominator",r.denominator);
        r.pixel_budget=j.value("pixel_budget",r.pixel_budget);
        if(j.contains("wrap_units"))r.wrap_units=j.at("wrap_units").get<syspane::scene::Unit>();
        const auto original=r.theme;
        const auto a=syspane::rendering::render_text(r,session);
        std::ofstream f(path,std::ios::binary);
        f.write(reinterpret_cast<const char*>(a.rgba.data()),static_cast<std::streamsize>(a.rgba.size()));
        f.close();if(!f)throw syspane::protocol::Error("probe.output");
        return Json({{"ink",rect(a.ink)},{"logical",rect(a.logical)},{"extent",rect(a.extent)},
            {"preferred",Json::array({a.preferred.width,a.preferred.height})},{"baseline",a.baseline},
            {"lines",a.lines},{"missing_glyphs",a.missing_glyphs},{"fonts",a.fonts},{"width",a.width},
            {"height",a.height},{"theme_unchanged",r.theme==original}});
    }catch(const syspane::protocol::Error& e){return Json({{"error",e.what()}});}
    catch(const std::exception&){return Json({{"error","text.input"}});}
}
}
int main(int argc,char** argv){
    const bool batch=argc==3&&std::string(argv[2])=="--session";
    if(argc!=2&&!batch)return 2;
    try{
        std::string bytes;char c;
        while(std::cin.get(c)){
            if(bytes.size()>=32768)throw syspane::protocol::Error("text.input");
            bytes.push_back(c);
        }
        const auto j=Json::parse(bytes);
        if(!batch){std::cout<<run(j,argv[1]).dump()<<'\n';return 0;}
        if(!j.is_array()||j.empty()||j.size()>64)throw syspane::protocol::Error("text.input");
        syspane::rendering::TextSession session;
        const auto seed=run(j[0],std::string(argv[1])+".seed",&session);
        std::string owner_error;
        std::thread other([&]{try{syspane::rendering::TextRequest q;session.render(q);}catch(const syspane::protocol::Error& e){owner_error=e.what();}});
        other.join();
        Json results=Json::array();
        for(std::size_t i=0;i<j.size();++i)results.push_back(run(j[i],std::string(argv[1])+"."+std::to_string(i),&session));
        std::cout<<Json({{"owner_error",owner_error},{"seed",seed},{"results",results}}).dump()<<'\n';
    }catch(const syspane::protocol::Error& e){std::cout<<Json({{"error",e.what()}}).dump()<<'\n';}
    catch(const std::exception&){std::cout<<"{\"error\":\"text.input\"}\n";}
}
