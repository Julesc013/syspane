#include "image_decode.hpp"
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <algorithm>
#include <array>
#include <cstring>
#include <map>
#include <set>
#include <string>
namespace syspane::rendering {
namespace {
void need(bool b,const char* code="image.format"){if(!b)throw protocol::Error(code);}
unsigned byte(std::string_view s,std::size_t i){need(i<s.size());return static_cast<unsigned char>(s[i]);}
std::uint32_t be32(std::string_view s,std::size_t i){return (byte(s,i)<<24)|(byte(s,i+1)<<16)|(byte(s,i+2)<<8)|byte(s,i+3);}
unsigned be16(std::string_view s,std::size_t i){return (byte(s,i)<<8)|byte(s,i+1);}
void dimensions(unsigned w,unsigned h){need(w&&h&&w<=4096&&h<=4096&&static_cast<std::uint64_t>(w)*h<=4194304,"image.capacity");}
struct Prepared {std::string bytes;unsigned width=0,height=0,orientation=1;};
std::uint32_t crc(std::string_view s){std::uint32_t c=0xffffffff;for(unsigned char v:s){c^=v;for(unsigned i=0;i<8;++i)c=(c>>1)^((c&1)?0xedb88320:0);}return c^0xffffffff;}
Prepared png(std::string_view s){need(s.substr(0,8)==std::string_view("\x89PNG\r\n\x1a\n",8));Prepared out;out.bytes=s.substr(0,8);bool header=false,data=false,end=false;unsigned count=0;
    for(std::size_t p=8;p<s.size();){need(++count<=4096&&s.size()-p>=12);const auto length=be32(s,p);need(length<=s.size()-p-12);const auto kind=s.substr(p+4,4),payload=s.substr(p+8,length);
        need(crc(s.substr(p+4,length+4))==be32(s,p+length+8));
        for(unsigned char c:kind)need((c>='A'&&c<='Z')||(c>='a'&&c<='z'));
        need(kind!="acTL"&&kind!="fcTL"&&kind!="fdAT","image.animation");
        if(!header){need(kind=="IHDR"&&length==13);out.width=be32(payload,0);out.height=be32(payload,4);dimensions(out.width,out.height);header=true;}
        else need(kind!="IHDR");
        if(kind=="IDAT")data=true;
        if(kind=="IEND"){need(!length&&data&&p+12==s.size());end=true;}
        const bool keep=kind=="IHDR"||kind=="PLTE"||kind=="tRNS"||kind=="IDAT"||kind=="IEND";
        need(keep||(byte(kind,0)&32));if(keep)out.bytes.append(s.substr(p,length+12));p+=length+12;
    }need(header&&data&&end);return out;
}
unsigned exif(std::string_view s){need(s.size()>=14&&s.substr(0,6)==std::string_view("Exif\0\0",6));s.remove_prefix(6);
    const bool little=s.substr(0,2)=="II";need(little||s.substr(0,2)=="MM");
    const auto u16=[&](std::size_t p){return little?byte(s,p)|(byte(s,p+1)<<8):be16(s,p);};
    const auto u32=[&](std::size_t p){return little?static_cast<std::uint32_t>(u16(p))|(static_cast<std::uint32_t>(u16(p+2))<<16):be32(s,p);};
    need(u16(2)==42);const auto offset=u32(4);need(offset>=8&&offset<=s.size()-2);const auto count=u16(offset);need(count<=1024&&static_cast<std::size_t>(offset)+2+count*12+4<=s.size());
    unsigned orientation=0;for(unsigned i=0;i<count;++i){const auto p=offset+2+i*12;if(u16(p)==274){need(!orientation&&u16(p+2)==3&&u32(p+4)==1);orientation=u16(p+8);need(orientation>=1&&orientation<=8);}}
    return orientation;
}
Prepared jpeg(std::string_view s){need(s.size()>=4&&byte(s,0)==255&&byte(s,1)==216);Prepared out;out.bytes=s.substr(0,2);std::size_t p=2;bool frame=false,scan=false,end=false,seen_exif=false;unsigned markers=0;
    while(p<s.size()){need(++markers<=4096&&byte(s,p)==255);const auto begin=p;while(p<s.size()&&byte(s,p)==255)++p;need(p<s.size());const auto code=byte(s,p++);
        if(code==217){need(scan&&p==s.size());out.bytes.append(s.substr(begin,p-begin));end=true;break;}
        need(code!=0&&code!=216&&code!=1&&(code<208||code>215));const auto length=be16(s,p);need(length>=2&&length<=s.size()-p);const auto payload=s.substr(p+2,length-2);p+=length;
        if(code>=192&&code<=207&&code!=196&&code!=200&&code!=204){need(!frame&&(code==192||code==194)&&payload.size()>=6&&byte(payload,0)==8);out.height=be16(payload,1);out.width=be16(payload,3);dimensions(out.width,out.height);frame=true;}
        if(code==225&&payload.substr(0,6)==std::string_view("Exif\0\0",6)){need(!seen_exif);seen_exif=true;const auto orientation=exif(payload);if(orientation)out.orientation=orientation;}
        const bool app=code>=224&&code<=239;
        const bool keep=(!app&&code!=254)||(code==224&&payload.substr(0,5)==std::string_view("JFIF\0",5)&&payload.size()==14)||(code==238&&payload.substr(0,5)=="Adobe"&&payload.size()==12);
        if(keep)out.bytes.append(s.substr(begin,p-begin));
        if(code==218){need(frame);scan=true;const auto start=p;
            while(p<s.size()){if(byte(s,p++)!=255)continue;const auto mark=p-1;while(p<s.size()&&byte(s,p)==255)++p;need(p<s.size());const auto next=byte(s,p);if(next==0||(next>=208&&next<=215)){++p;continue;}p=mark;break;}
            out.bytes.append(s.substr(start,p-start));}
    }need(frame&&scan&&end);return out;
}
std::string lower(std::string v){for(auto& c:v)if(c>='A'&&c<='Z')c+=32;return v;}
std::string trim(std::string v){const auto first=v.find_first_not_of(" \t\r\n\f");if(first==std::string::npos)return {};const auto last=v.find_last_not_of(" \t\r\n\f");return v.substr(first,last-first+1);}
bool id(const std::string& v){return !v.empty()&&v.size()<=128&&((v[0]>='A'&&v[0]<='Z')||(v[0]>='a'&&v[0]<='z')||v[0]=='_')&&v.find_first_not_of("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.:-")==std::string::npos;}
struct Svg {unsigned depth=0,elements=0;std::size_t text=0;Prepared out;std::set<std::string> ids,refs;std::string css;bool style=false;const char* error=nullptr;};
void reference(Svg& v,const std::string& value){need(value.size()>1&&value[0]=='#'&&id(value.substr(1)),"image.reference");v.refs.insert(value.substr(1));}
std::string css_normal(std::string_view raw){std::string v;
    for(std::size_t i=0;i<raw.size();++i){if(i+1<raw.size()&&raw[i]=='/'&&raw[i+1]=='*'){const auto end=raw.find("*/",i+2);need(end!=std::string_view::npos,"image.svg");i=end+1;continue;}
        if(raw[i]!='\\'){v+=raw[i];continue;}need(++i<raw.size(),"image.svg");if(raw[i]=='\n'||raw[i]=='\r'||raw[i]=='\f')continue;
        const auto hex=[](char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;};
        if(hex(raw[i])<0){v+=raw[i];continue;}unsigned value=0,count=0;while(i<raw.size()&&count<6&&hex(raw[i])>=0){value=value*16+static_cast<unsigned>(hex(raw[i]));++i;++count;}
        if(i<raw.size()&&(raw[i]==' '||raw[i]=='\t'||raw[i]=='\r'||raw[i]=='\n'||raw[i]=='\f'))++i;
        --i;need(value>0&&value<128,"image.svg");v+=static_cast<char>(value);
    }return v;
}
void css(Svg& state,std::string_view raw){const auto normalized=css_normal(raw),v=lower(normalized);need(v.find('@')==std::string::npos,"image.reference");
    need(v.find("animation")==std::string::npos&&v.find("transition")==std::string::npos,"image.animation");
    std::size_t p=0;while((p=v.find("url",p))!=std::string::npos){auto begin=v.find_first_not_of(" \t\r\n\f",p+3);if(begin==std::string::npos||v[begin]!='('){p+=3;continue;}
        const auto end=v.find(')',begin+1);need(end!=std::string::npos,"image.reference");auto value=trim(normalized.substr(begin+1,end-begin-1));
        if(value.size()>=2&&((value.front()=='\''&&value.back()=='\'')||(value.front()=='"'&&value.back()=='"')))value=value.substr(1,value.size()-2);
        reference(state,value);p=end+1;}
}
unsigned dimension(std::string value){if(value.size()>2&&value.substr(value.size()-2)=="px")value.resize(value.size()-2);need(!value.empty()&&value.size()<=5&&value.find_first_not_of("0123456789")==std::string::npos,"image.svg");return static_cast<unsigned>(std::stoul(value));}
template<class F>void capture(Svg* v,GError** error,F f){try{f();}catch(const protocol::Error& e){v->error=std::strcmp(e.what(),"image.capacity")==0?"image.capacity":std::strcmp(e.what(),"image.reference")==0?"image.reference":std::strcmp(e.what(),"image.animation")==0?"image.animation":"image.svg";g_set_error_literal(error,G_MARKUP_ERROR,G_MARKUP_ERROR_INVALID_CONTENT,v->error);}catch(...){v->error="image.capacity";g_set_error_literal(error,G_MARKUP_ERROR,G_MARKUP_ERROR_INVALID_CONTENT,v->error);}}
Prepared svg(std::string_view input){need(input.size()<=1048576,"image.capacity");Svg state;
    GMarkupParser parser{};
    parser.start_element=[](GMarkupParseContext*,const gchar* name,const gchar** names,const gchar** values,gpointer user,GError** error){auto* v=static_cast<Svg*>(user);capture(v,error,[&]{
        const std::string tag=name;need(++v->depth<=64&&++v->elements<=16384,"image.capacity");
        need(tag!="animate"&&tag!="animateMotion"&&tag!="animateTransform"&&tag!="set","image.animation");
        static const std::set<std::string> allowed={"svg","g","defs","symbol","use","path","rect","circle","ellipse","line","polyline","polygon","text","tspan","textPath","title","desc","metadata","linearGradient","radialGradient","stop","pattern","clipPath","mask","filter","marker","style","switch","feBlend","feColorMatrix","feComponentTransfer","feComposite","feConvolveMatrix","feDiffuseLighting","feDisplacementMap","feDistantLight","feDropShadow","feFlood","feFuncA","feFuncB","feFuncG","feFuncR","feGaussianBlur","feImage","feMerge","feMergeNode","feMorphology","feOffset","fePointLight","feSpecularLighting","feSpotLight","feTile","feTurbulence","image"};
        need(allowed.count(tag)!=0,"image.svg");if(v->depth==1)need(tag=="svg"&&v->elements==1,"image.svg");std::map<std::string,std::string> attrs;
        for(unsigned i=0;names[i];++i){need(i<64,"image.capacity");const std::string key=names[i],value=values[i];v->text+=key.size()+value.size();need(v->text<=1048576,"image.capacity");need(attrs.emplace(key,value).second,"image.svg");
            if(key=="xmlns")need(value=="http://www.w3.org/2000/svg","image.svg");
            else if(key=="xmlns:xlink")need(value=="http://www.w3.org/1999/xlink","image.svg");
            else if(key=="xml:base")need(false,"image.reference");
            else{need(key.find(':')==std::string::npos||key=="xlink:href"||key=="xml:space"||key=="xml:lang","image.svg");need(lower(key).substr(0,2)!="on","image.svg");}
            if(key=="href"||key=="xlink:href")reference(*v,value);
            if(key=="id"){need(id(value)&&v->ids.insert(value).second,"image.reference");}
            if(key!="xmlns"&&key!="xmlns:xlink"&&key!="id"&&key!="href"&&key!="xlink:href")css(*v,value);
        }
        if(v->depth==1){need(attrs["xmlns"]=="http://www.w3.org/2000/svg","image.svg");v->out.width=dimension(attrs["width"]);v->out.height=dimension(attrs["height"]);dimensions(v->out.width,v->out.height);}
        if(tag=="style"){need(!v->style,"image.svg");v->style=true;v->css.clear();}
    });};
    parser.end_element=[](GMarkupParseContext*,const gchar* name,gpointer user,GError** error){auto* v=static_cast<Svg*>(user);capture(v,error,[&]{if(std::string_view(name)=="style"){css(*v,v->css);v->style=false;}--v->depth;});};
    parser.text=[](GMarkupParseContext*,const gchar* text,gsize length,gpointer user,GError** error){auto* v=static_cast<Svg*>(user);capture(v,error,[&]{v->text+=length;need(v->text<=1048576,"image.capacity");if(v->style)v->css.append(text,length);});};
    parser.passthrough=[](GMarkupParseContext*,const gchar* data,gsize length,gpointer user,GError** error){auto* v=static_cast<Svg*>(user);capture(v,error,[&]{const std::string_view text(data,length);
        need(text.substr(0,4)=="<!--"||text=="<?xml version=\"1.0\"?>"||text=="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"||text=="<?xml version='1.0'?>"||text=="<?xml version='1.0' encoding='UTF-8'?>","image.svg");});};
    auto* context=g_markup_parse_context_new(&parser,G_MARKUP_TREAT_CDATA_AS_TEXT,&state,nullptr);GError* error=nullptr;
    const bool ok=g_markup_parse_context_parse(context,input.data(),input.size(),&error)&&g_markup_parse_context_end_parse(context,&error);g_markup_parse_context_free(context);if(error)g_error_free(error);
    need(ok,state.error?state.error:"image.svg");need(state.elements&&state.depth==0,"image.svg");for(const auto& ref:state.refs)need(state.ids.count(ref)!=0,"image.reference");state.out.bytes=input;return state.out;
}
}
scene::Image decode_image(std::string_view media,std::string_view input){
    need(!input.empty()&&input.size()<=8388608,"image.capacity");Prepared prepared;const char* type=nullptr;
    if(media=="image/png"){prepared=png(input);type="png";}else if(media=="image/jpeg"){prepared=jpeg(input);type="jpeg";}else if(media=="image/svg+xml"){prepared=svg(input);type="svg";}else need(false,"image.media");
    GError* error=nullptr;auto* loader=gdk_pixbuf_loader_new_with_type(type,&error);if(error)g_error_free(error);need(loader!=nullptr,"image.decoder");
    struct Owner {GdkPixbufLoader* p;~Owner(){g_object_unref(p);}} owner{loader};
    struct Size {unsigned w,h;bool valid=true;};Size size{prepared.width,prepared.height,true};
    g_signal_connect(loader,"size-prepared",G_CALLBACK(+[](GdkPixbufLoader* l,int w,int h,gpointer user){auto& s=*static_cast<Size*>(user);if(w<=0||h<=0||static_cast<unsigned>(w)!=s.w||static_cast<unsigned>(h)!=s.h){s.valid=false;gdk_pixbuf_loader_set_size(l,1,1);}}),&size);
    error=nullptr;const bool written=gdk_pixbuf_loader_write(loader,reinterpret_cast<const guchar*>(prepared.bytes.data()),prepared.bytes.size(),&error);if(error){g_error_free(error);error=nullptr;}
    const bool closed=gdk_pixbuf_loader_close(loader,&error);if(error)g_error_free(error);need(written&&closed&&size.valid,"image.decoder");
    auto* animation=gdk_pixbuf_loader_get_animation(loader);need(animation&&gdk_pixbuf_animation_is_static_image(animation),"image.animation");
    auto* pixels=gdk_pixbuf_loader_get_pixbuf(loader);need(pixels&&gdk_pixbuf_get_bits_per_sample(pixels)==8&&gdk_pixbuf_get_colorspace(pixels)==GDK_COLORSPACE_RGB,"image.decoder");
    const auto w=gdk_pixbuf_get_width(pixels),h=gdk_pixbuf_get_height(pixels),channels=gdk_pixbuf_get_n_channels(pixels),stride=gdk_pixbuf_get_rowstride(pixels);need(w==static_cast<int>(prepared.width)&&h==static_cast<int>(prepared.height)&&(channels==3||channels==4)&&stride>=w*channels,"image.decoder");
    scene::Image out{prepared.width,prepared.height,{}};out.rgba.resize(static_cast<std::size_t>(w)*h*4);const auto* data=gdk_pixbuf_get_pixels(pixels);
    for(int y=0;y<h;++y)for(int x=0;x<w;++x){const auto* in=data+static_cast<std::size_t>(y)*stride+x*channels;auto* dst=out.rgba.data()+(static_cast<std::size_t>(y)*w+x)*4;const unsigned alpha=channels==4?in[3]:255;dst[3]=static_cast<unsigned char>(alpha);for(unsigned c=0;c<3;++c)dst[c]=static_cast<unsigned char>((in[c]*alpha+127)/255);}
    return prepared.orientation==1?out:scene::orient_image(out,prepared.orientation);
}
}
