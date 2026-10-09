#pragma once
#include "wire.hpp"
#include <algorithm>

namespace syspane::platform::recovery_io {
using protocol::Json;
constexpr std::size_t record_limit=786432,header_limit=32768,frame_limit=819201;
inline void need(bool ok,const char* why){if(!ok)throw protocol::Error(why);}
inline bool digest(const Json& v){return v.is_string()&&v.get_ref<const std::string&>().size()==64&&v.get_ref<const std::string&>().find_first_not_of("0123456789abcdef")==std::string::npos;}
inline bool nullable_digest(const Json& v){return v.is_null()||digest(v);}
inline bool number(const Json& v){return v.is_string()&&protocol::decimal(v.get_ref<const std::string&>()).has_value();}
inline bool directory(const Json& v){
    if(!protocol::members(v,{"uid","state_device","state_inode","recovery_device","recovery_inode"}))return false;
    for(const char* key:{"uid","state_device","state_inode","recovery_device","recovery_inode"})if(!number(v[key]))return false;
    return *protocol::decimal(v["uid"].get_ref<const std::string&>())<=4294967295ULL&&v["state_inode"]!="0"&&v["recovery_inode"]!="0"&&v["state_device"]==v["recovery_device"];
}
inline bool binding(const Json& v){return protocol::members(v,{"session","profile","generation","policy_revision"})&&
    v["session"].is_string()&&protocol::identifier(v["session"].get_ref<const std::string&>())&&
    v["profile"].is_string()&&protocol::identifier(v["profile"].get_ref<const std::string&>())&&digest(v["generation"])&&number(v["policy_revision"]);}
inline bool operation(const Json& v){return v=="load"||v=="replace"||v=="retire";}
inline bool error_code(const Json& v){return v.is_string()&&v.get_ref<const std::string&>().size()<=64&&
    std::all_of(v.get_ref<const std::string&>().begin(),v.get_ref<const std::string&>().end(),[](char c){return (c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='.';});}
struct Packet {Json header;std::string bytes;};
inline Packet decode(std::string_view bytes){
    const auto zero=bytes.find('\0');need(zero!=std::string_view::npos&&zero>0&&zero<=header_limit&&bytes.size()-zero-1<=record_limit,"recovery_queue.frame");
    return {protocol::parse(bytes.substr(0,zero)),std::string(bytes.substr(zero+1))};
}
inline std::string encode(const Json& header,std::string_view bytes={}){
    auto raw=header.dump();need(raw.size()<=header_limit&&bytes.size()<=record_limit,"recovery_queue.frame");raw+='\0';raw.append(bytes);return protocol::frame(raw,frame_limit);
}
inline Json stamp(const Json& request,const char* kind){return {{"kind",kind},{"binding",request.at("binding")},{"ticket",request.at("ticket")},{"operation",request.at("operation")}};}
inline bool matches(const Json& value,const Json& request){return value.is_object()&&value.contains("binding")&&value.contains("ticket")&&value.contains("operation")&&
    value["binding"]==request["binding"]&&value["ticket"]==request["ticket"]&&value["operation"]==request["operation"];}
inline void request(const Packet& p){const auto& h=p.header;
    const bool bound=h.contains("directory");
    need((bound?protocol::members(h,{"kind","binding","ticket","operation","root","expected","directory"})&&directory(h["directory"]):protocol::members(h,{"kind","binding","ticket","operation","root","expected"}))&&h["kind"]=="request"&&binding(h["binding"])&&number(h["ticket"])&&h["ticket"]!="0"&&operation(h["operation"])&&
        h["root"].is_string()&&!h["root"].get_ref<const std::string&>().empty()&&h["root"].get_ref<const std::string&>().size()<=4096&&h["root"].get_ref<const std::string&>().front()=='/'&&nullable_digest(h["expected"]),"recovery_queue.request");
    need(h["operation"]=="replace"?!p.bytes.empty():p.bytes.empty(),"recovery_queue.request");need(h["operation"]!="load"||h["expected"].is_null(),"recovery_queue.request");
}
}
