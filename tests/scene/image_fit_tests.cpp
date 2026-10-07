#include "image.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
namespace s=syspane::scene;using syspane::protocol::Json;
namespace {
void need(bool b,const char* why){if(!b)throw std::runtime_error(why);}
template<class F>void reject(F f){bool rejected=false;try{f();}catch(const syspane::protocol::Error&){rejected=true;}need(rejected,"image rejection");}
void fit(const std::string& root){std::ifstream f(root+"/../image-cases/fit.json");need(f.good(),"fit oracle absent");Json rows;f>>rows;
    for(const auto& v:rows){s::Image src{v["source"][0],v["source"][1],v["rgba"].get<std::vector<unsigned char>>()};const auto before=src.rgba;
        const auto mode=v["mode"]=="contain"?s::ImageFit::contain:v["mode"]=="cover"?s::ImageFit::cover:s::ImageFit::stretch;
        const auto got=s::fit_image(src,v["target"][0],v["target"][1],mode);need(got.rgba==v["expected"].get<std::vector<unsigned char>>(),"exact bilinear fit");need(src.rgba==before,"source mutated");}}
void orientation(){s::Image src{3,2,{}};for(unsigned char c=1;c<=6;++c)src.rgba.insert(src.rgba.end(),{c,c,c,255});
    const std::vector<std::vector<unsigned char>> expected{{1,2,3,4,5,6},{3,2,1,6,5,4},{6,5,4,3,2,1},{4,5,6,1,2,3},
        {1,4,2,5,3,6},{4,1,5,2,6,3},{6,3,5,2,4,1},{3,6,2,5,1,4}};
    for(unsigned n=1;n<=8;++n){const auto got=s::orient_image(src,n);need(got.width==(n>=5?2u:3u)&&got.height==(n>=5?3u:2u),"orientation dimensions");
        for(unsigned i=0;i<6;++i)need(got.rgba[i*4]==expected[n-1][i],"orientation mapping");}}
void validation(const std::string& root){
    std::ifstream file(root+"/../image-validation-cases.json");need(file.good(),"validation fixture");Json cases;file>>cases;
    for(const auto& valid:cases["valid"]){
        s::Image image{valid["size"][0],valid["size"][1],{}};const auto pixel=valid["pixel"].get<std::array<unsigned char,4>>();
        image.rgba.resize(static_cast<std::size_t>(image.width)*image.height*4);for(std::size_t i=0;i<image.rgba.size();i+=4)std::copy(pixel.begin(),pixel.end(),image.rgba.begin()+i);
        s::validate_image(image);if(image.width==1)continue;
        const auto original=image.rgba;
        for(const auto& mutation:cases["invalid"]){
            const auto offset=mutation["pixel_index"].get<std::size_t>()*4+mutation["channel"].get<unsigned>();image.rgba[offset]=cases["invalid_component"];
            const auto rejected=[&](const auto& call){bool failed=false;try{call();}catch(const syspane::protocol::Error& e){failed=std::string(e.what())==cases["error"];}need(failed,"invalid source accepted");};
            rejected([&]{s::validate_image(image);});rejected([&]{s::fit_image(image,1,1,s::ImageFit::contain);});rejected([&]{s::orient_image(image,1);});
            need(image.rgba[offset]==cases["invalid_component"],"rejection mutated source");image.rgba[offset]=original[offset];need(image.rgba==original,"source changed");
        }
    }
}
void limits(){s::Image src{1,1,{1,2,3,4}};reject([&]{s::fit_image(src,0,1,s::ImageFit::contain);});reject([&]{s::fit_image(src,2049,1,s::ImageFit::contain);});
    reject([&]{s::fit_image(src,2,2,s::ImageFit::contain,3);});reject([&]{s::orient_image(src,0);});reject([&]{s::orient_image(src,9);});
    src.rgba[0]=5;reject([&]{s::validate_image(src);});src.rgba[0]=1;src.rgba.pop_back();reject([&]{s::validate_image(src);});src.width=4097;reject([&]{s::validate_image(src);});}
}
int image_fit_test(const std::string& name,const std::string& root){if(name=="IMAGE-FIT")fit(root);else if(name=="IMAGE-ORIENTATION")orientation();else if(name=="IMAGE-LIMITS")limits();else if(name=="IMAGE-VALIDATION")validation(root);else throw std::runtime_error("unknown image fit case");std::cout<<name<<" pass\n";return 0;}
