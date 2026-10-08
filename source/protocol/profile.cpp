#include "profile.hpp"
#include <algorithm>
namespace syspane::protocol {
namespace {
void need(bool v){if(!v)throw Error("profile.body");}
std::uint64_t number(const Json& v){need(v.is_string());const auto n=decimal(v.get_ref<const std::string&>());need(n.has_value());return *n;}
void common(const Json& v){need(v.is_object()&&v.value("schema_version",Json())=="0.1.0"&&v.contains("query_id")&&v["query_id"].is_string()&&identifier(v["query_id"].get_ref<const std::string&>()));}
}
void validate_profile_request(const Json& v){
    common(v);const auto op=v.value("op",Json());
    if(op=="open")need(members(v,{"schema_version","query_id","op"}));
    else if(op=="read"){
        need(members(v,{"schema_version","query_id","op","transfer_id","part","offset"}));
        need(number(v["transfer_id"])>0&&number(v["part"])<profile_part_limit&&number(v["offset"])<=16777216);
    }else if(op=="close"){
        need(members(v,{"schema_version","query_id","op","transfer_id"}));need(number(v["transfer_id"])>0);
    }else need(false);
}
void validate_profile_result(const Json& v){
    common(v);const auto outcome=v.value("outcome",Json());
    if(outcome=="busy"||outcome=="denied"||outcome=="unavailable")need(members(v,{"schema_version","query_id","outcome"}));
    else if(outcome=="closed"){
        need(members(v,{"schema_version","query_id","outcome","transfer_id"}));need(number(v["transfer_id"])>0);
    }else{
        need(outcome=="chunk"&&members(v,{"schema_version","query_id","outcome","transfer_id","revision","policy_generation","part","offset","part_count","part_bytes","sha256","hex","complete"}));
        need(number(v["transfer_id"])>0);(void)number(v["revision"]);(void)number(v["policy_generation"]);
        const auto part=number(v["part"]),count=number(v["part_count"]),offset=number(v["offset"]),bytes=number(v["part_bytes"]);
        need(count>=4&&count<=profile_part_limit&&part<count&&bytes<=16777216&&offset<=bytes);
        need(v["sha256"].is_string()&&v["hex"].is_string()&&v["complete"].is_boolean());
        const auto& hash=v["sha256"].get_ref<const std::string&>();const auto& hex=v["hex"].get_ref<const std::string&>();
        need(hash.size()==64&&hash.find_first_not_of("0123456789abcdef")==std::string::npos);
        need(hex.size()%2==0&&hex.size()/2==std::min<std::uint64_t>(profile_chunk_bytes,bytes-offset)&&hex.find_first_not_of("0123456789abcdef")==std::string::npos);
        need((bytes==0&&offset==0)||(offset<bytes));
        need(v["complete"].get<bool>()==(part+1==count&&offset+hex.size()/2==bytes));
    }
}
}
