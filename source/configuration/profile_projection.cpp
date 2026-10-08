#include "profile_projection.hpp"
#include "digest.hpp"
#include <algorithm>
#include <limits>

namespace syspane::configuration {
namespace p=protocol;
namespace {
void need(bool value,const char* code){if(!value)throw p::Error(code);}
std::size_t number(const Json& value){need(value.is_string(),"profile.number");const auto n=p::decimal(value.get_ref<const std::string&>());need(n&&*n<=p::profile_byte_limit,"profile.number");return static_cast<std::size_t>(*n);}
void disclosure(const Authority& a,const Policy& policy){
    need(policy.available&&a.authenticated&&a.role=="console"&&a.role_grants.count("console")&&
         !policy.denied_capabilities.count("profile.open")&&!policy.denied_capabilities.count("profile.read"),"policy.denied");
    for(const auto* channel:{"inspector","accessibility"})for(const auto* classification:{"operational","sensitive"})
        need(permits(a,policy,channel,classification),"policy.denied");
}
Json policy_view(const Policy& policy){
    Json forced=Json::array(),rules=Json::array();
    for(const auto& row:policy.forced)forced.push_back({{"path",row.first},{"value",row.second}});
    for(const auto& row:policy.disclosure)if(row.first.first=="console")rules.push_back({{"channel",row.first.second},{"allow_classifications",row.second}});
    return {{"revision",std::to_string(policy.revision)},{"forced_settings",std::move(forced)},
            {"denied_capabilities",policy.denied_capabilities},{"disclosure",std::move(rules)}};
}
Policy read_policy(const Json& value){
    need(p::members(value,{"revision","forced_settings","denied_capabilities","disclosure"})&&value["disclosure"].is_array(),"profile.policy");
    auto rules=value["disclosure"];for(auto& row:rules){need(p::members(row,{"channel","allow_classifications"}),"profile.policy");row["role"]="console";}
    // Reuse policy field validation. These private synthetic decoder fields are
    // never transmitted, persisted, or evidence of protected native provenance.
    auto policy=decode_policy(Json{{"schema_version","0.1.0"},{"policy_id","profile:effective"},{"scope","machine"},
        {"retained_data_on_revocation","restrict"},{"revision",value["revision"]},{"forced_settings",value["forced_settings"]},
        {"denied_capabilities",value["denied_capabilities"]},{"disclosure",std::move(rules)}}.dump());
    policy.available=true;disclosure({true,"console",{"console"}},policy);return policy;
}
std::string hexadecimal(std::string_view bytes){
    static constexpr char digits[]="0123456789abcdef";std::string out;out.reserve(bytes.size()*2);
    for(unsigned char c:bytes){out.push_back(digits[c>>4]);out.push_back(digits[c&15]);}return out;
}
}
ProfileImage::ProfileImage(const Committed& value,std::set<std::string> caps)
    :resources_(value.resources),capabilities_(std::move(caps)),revision_(authored_revision(value.documents)){
    need(static_cast<bool>(resources_),"profile.resources");validate_resource_binding(*resources_,value.documents);
    need(capabilities_.size()<=128,"profile.capabilities");for(const auto& cap:capabilities_)need(p::identifier(cap),"profile.capabilities");
    parts_.resize(4);parts_[1].text=value.documents.settings.dump();parts_[2].text=value.documents.scene.dump();
    Json packages=Json::array();auto ordered=resources_->packages();
    std::sort(ordered.begin(),ordered.end(),[](const auto& a,const auto& b){return sha256(a->manifest)<sha256(b->manifest);});
    need(ordered.size()<=64,"profile.capacity");
    for(const auto& package:ordered){
        Json row{{"manifest",std::to_string(parts_.size())},{"assets",Json::array()}};
        parts_.push_back({{},sha256(package->manifest),{},package});
        for(const auto& asset:package->assets){
            row["assets"].push_back({{"path",asset.first},{"part",std::to_string(parts_.size())}});
            parts_.push_back({{},content_sha256(asset.second),asset.first,package});
        }
        packages.push_back(std::move(row));
    }
    parts_[0].text=Json{{"format","SysPane.ProfileImage"},{"schema_version","0.1.0"},{"revision",std::to_string(revision_)},
        {"selection",resources_->selection()},{"theme",resources_->theme_pin()},{"capabilities",capabilities_},{"packages",std::move(packages)}}.dump();
    (void)p::parse(parts_[0].text);need(parts_.size()<=p::profile_part_limit,"profile.capacity");
    for(std::size_t i=0;i<parts_.size();++i){const auto& raw=part(i);need(raw.size()<=16777216&&raw.size()<=p::profile_byte_limit-bytes_,"profile.capacity");bytes_+=raw.size();if(parts_[i].hash.empty())parts_[i].hash=content_sha256(raw);}
}
const std::string& ProfileImage::part(std::size_t index)const{
    const auto& value=parts_.at(index);return !value.package?value.text:value.asset.empty()?value.package->manifest:value.package->assets.at(value.asset);
}
const std::string& ProfileImage::hash(std::size_t index)const{return parts_.at(index).hash;}
void ProfileImage::authorize(const Authority& a,const Policy& policy)const{disclosure(a,policy);authorize_resources(*resources_,policy,capabilities_);}
bool ProfileTransfer::expired(const std::string& connection,std::uint64_t lifetime,std::uint64_t now)const{
    if(!active_||active_->connection!=connection||active_->lifetime!=lifetime)return false;
    return now<active_->last||now-active_->last>=5000||now-active_->opened>=60000;
}
void ProfileTransfer::invalidate(){active_.reset();}
void ProfileTransfer::disconnect(const std::string& id,std::uint64_t lifetime){if(active_&&active_->connection==id&&active_->lifetime==lifetime)invalidate();}
Json ProfileTransfer::receive(const std::string& id,std::uint64_t lifetime,const Authority& a,const Policy& policy,ProfileSnapshot image,const Json& query,std::uint64_t now){
    p::validate_profile_request(query);
    Json result{{"schema_version","0.1.0"},{"query_id",query["query_id"]},{"outcome","unavailable"}};
    try{disclosure(a,policy);if(image)image->authorize(a,policy);}catch(const p::Error&){disconnect(id,lifetime);result["outcome"]="denied";return result;}
    if(!image){disconnect(id,lifetime);return result;}
    if(query["op"]=="open"){
        if(active_){result["outcome"]="busy";return result;}
        if(counter_==std::numeric_limits<std::uint64_t>::max())return result;
        auto view=policy_view(policy).dump();need(view.size()<=65536&&view.size()<=p::profile_byte_limit-image->bytes(),"profile.capacity");
        (void)read_policy(p::parse(view));const auto hash=sha256(view);
        active_.emplace(Active{id,std::move(view),hash,lifetime,++counter_,policy.revision,now,now,std::move(image)});
    }else{
        need(active_&&active_->connection==id&&active_->lifetime==lifetime&&query["transfer_id"]==std::to_string(active_->id),"profile.transfer");
        if(expired(id,lifetime,now)){invalidate();throw p::Error("profile.expired");}
        if(query["op"]=="close"){result["outcome"]="closed";result["transfer_id"]=query["transfer_id"];invalidate();return result;}
        need(query["part"]==std::to_string(active_->part)&&query["offset"]==std::to_string(active_->offset),"profile.cursor");
    }
    auto& active=*active_;active.image->authorize(a,policy);
    need(active.generation==policy.revision,"profile.policy");active.last=now;
    const auto& bytes=active.part==3?active.policy:active.image->part(active.part);
    const auto length=std::min(p::profile_chunk_bytes,bytes.size()-active.offset);
    const bool complete=active.part+1==active.image->count()&&active.offset+length==bytes.size();
    result.update(Json{{"outcome","chunk"},{"transfer_id",std::to_string(active.id)},{"revision",std::to_string(active.image->revision())},
        {"policy_generation",std::to_string(active.generation)},{"part",std::to_string(active.part)},{"offset",std::to_string(active.offset)},
        {"part_count",std::to_string(active.image->count())},{"part_bytes",std::to_string(bytes.size())},
        {"sha256",active.part==3?active.policy_hash:active.image->hash(active.part)},
        {"hex",hexadecimal(std::string_view(bytes).substr(active.offset,length))},{"complete",complete}});
    active.offset+=length;if(active.offset==bytes.size()){++active.part;active.offset=0;}
    if(complete)invalidate();
    return result;
}
ProfileDownload::ProfileDownload(std::string connection,std::string epoch,std::set<std::string> capabilities)
    :connection_(std::move(connection)),epoch_(std::move(epoch)),capabilities_(std::move(capabilities)){
    need(p::identifier(connection_)&&p::identifier(epoch_)&&capabilities_.size()<=128,"profile.identity");
    for(const auto& cap:capabilities_)need(p::identifier(cap),"profile.capabilities");
}
void ProfileDownload::invalidate(){invalid_=true;view_.reset();std::vector<std::string>{}.swap(parts_);query_.clear();hash_.clear();}
const ProfileView& ProfileDownload::view()const{need(!invalid_&&view_.has_value(),"profile.incomplete");return *view_;}
Json ProfileDownload::request(const std::string& query){
    need(!invalid_&&!view_&&query_.empty()&&p::identifier(query),"profile.request");query_=query;
    Json out{{"schema_version","0.1.0"},{"query_id",query},{"op",transfer_.empty()?"open":"read"}};
    if(!transfer_.empty()){out["transfer_id"]=transfer_;out["part"]=std::to_string(part_);out["offset"]=std::to_string(offset_);}return out;
}
void ProfileDownload::receive(const p::Message& message){
    try{
        need(!invalid_&&!view_&&!query_.empty()&&message.type=="profile.chunk"&&message.connection_id==connection_&&message.producer_epoch==epoch_,"profile.identity");
        const auto& value=message.body;p::validate_profile_result(value);need(value["query_id"]==query_,"profile.query");
        need(value["outcome"]=="chunk","profile.unavailable");query_.clear();
        if(transfer_.empty()){
            transfer_=value["transfer_id"];revision_=value["revision"];generation_=value["policy_generation"];count_=number(value["part_count"]);parts_.resize(count_);
        }
        need(value["transfer_id"]==transfer_&&value["revision"]==revision_&&value["policy_generation"]==generation_&&number(value["part_count"])==count_,"profile.identity");
        need(number(value["part"])==part_&&number(value["offset"])==offset_,"profile.cursor");
        const auto size=number(value["part_bytes"]);const auto hash=value["sha256"].get<std::string>();
        if(offset_==0){
            const std::size_t limit=part_==0?1048576:part_==1||part_==2?262144:part_==3?65536:16777216;
            need(size<=limit&&size<=p::profile_byte_limit-bytes_,"profile.capacity");bytes_+=size;part_bytes_=size;hash_=hash;parts_[part_].reserve(size);
        }else need(size==part_bytes_&&hash==hash_,"profile.part_changed");
        const auto& hex=value["hex"].get_ref<const std::string&>();auto& bytes=parts_[part_];
        const auto nibble=[](char c){return c<='9'?c-'0':c-'a'+10;};
        for(std::size_t i=0;i<hex.size();i+=2)bytes.push_back(static_cast<char>((nibble(hex[i])<<4)|nibble(hex[i+1])));
        offset_+=hex.size()/2;if(offset_==part_bytes_){need(content_sha256(bytes)==hash_,"profile.digest");++part_;offset_=0;}
        need(value["complete"].get<bool>()==(part_==count_),"profile.complete");if(part_==count_)finish();
    }catch(...){invalidate();throw;}
}
void ProfileDownload::finish(){
    const auto header=p::parse(parts_[0]);
    need(p::members(header,{"format","schema_version","revision","selection","theme","capabilities","packages"})&&header["format"]=="SysPane.ProfileImage"&&header["schema_version"]=="0.1.0"&&header["revision"]==revision_,"profile.header");
    need(header["capabilities"].is_array()&&header["capabilities"].size()<=128&&header["packages"].is_array()&&!header["packages"].empty()&&header["packages"].size()<=64,"profile.header");
    std::set<std::string> admitted;std::string previous_capability;
    for(const auto& cap:header["capabilities"]){
        need(cap.is_string()&&p::identifier(cap.get_ref<const std::string&>())&&(previous_capability.empty()||previous_capability<cap.get_ref<const std::string&>()),"profile.capabilities");
        previous_capability=cap.get<std::string>();if(capabilities_.count(previous_capability))admitted.insert(previous_capability);
    }
    Authored documents{parse_content_json(parts_[1]),parse_content_json(parts_[2])};validate_authored(documents);
    need(std::to_string(authored_revision(documents))==revision_,"profile.revision");
    auto policy=read_policy(p::parse(parts_[3]));need(std::to_string(policy.revision)==generation_,"profile.policy");
    std::vector<ContentPackage> packages;std::size_t index=4;std::string previous_hash;
    for(const auto& row:header["packages"]){
        need(p::members(row,{"manifest","assets"})&&number(row["manifest"])==index&&index<parts_.size()&&row["assets"].is_array(),"profile.package");
        need(parts_[index].size()<=65536,"profile.manifest");const auto hash=sha256(parts_[index]);need(previous_hash.empty()||previous_hash<hash,"profile.package_order");previous_hash=hash;
        ContentPackage package{std::move(parts_[index++]),{}};std::string previous_path;
        for(const auto& asset:row["assets"]){
            need(p::members(asset,{"path","part"})&&asset["path"].is_string()&&number(asset["part"])==index&&index<parts_.size(),"profile.asset");
            const auto path=asset["path"].get<std::string>();validate_content_path(path);need(previous_path.empty()||previous_path<path,"profile.asset_order");previous_path=path;
            need(package.assets.emplace(path,std::move(parts_[index++])).second,"profile.asset");
        }
        packages.push_back(std::move(package));
    }
    need(index==parts_.size(),"profile.trailing");ContentCatalog catalog(std::move(packages));
    auto resources=header["selection"].contains("schema_version")?catalog.theme_resources(header["selection"],documents):catalog.resources(header["selection"],documents);
    need(resources->theme_pin()==header["theme"]&&resources->packages().size()==header["packages"].size(),"profile.closure");authorize_resources(*resources,policy,admitted);
    view_.emplace(ProfileView{std::move(documents),std::move(resources),std::move(policy),std::move(admitted)});std::vector<std::string>{}.swap(parts_);
}
}
