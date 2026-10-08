#pragma once
#include "transaction.hpp"
#include "profile.hpp"

namespace syspane::configuration {
// Prepare only on the supervised storage/command worker. Validated package bytes
// remain shared and immutable; a transfer does no filesystem work or media hashing.
class ProfileImage {
public:
    ProfileImage(const Committed&,std::set<std::string> capabilities);
    std::uint64_t revision()const{return revision_;}
    std::size_t count()const{return parts_.size();}
    std::size_t bytes()const{return bytes_;}
    const std::string& part(std::size_t)const;
    const std::string& hash(std::size_t)const;
    void authorize(const Authority&,const Policy&)const;
private:
    struct Part {std::string text,hash,asset;std::shared_ptr<const ContentPackage> package;};
    std::vector<Part> parts_;ResourceSnapshot resources_;std::set<std::string> capabilities_;
    std::uint64_t revision_;std::size_t bytes_=0;
};
using ProfileSnapshot=std::shared_ptr<const ProfileImage>;
// One controller-wide slot. All methods run on the owning session loop.
class ProfileTransfer {
public:
    Json receive(const std::string& connection,std::uint64_t lifetime,const Authority&,const Policy&,
                 ProfileSnapshot,const Json& request,std::uint64_t now);
    bool expired(const std::string&,std::uint64_t lifetime,std::uint64_t now)const;
    void disconnect(const std::string&,std::uint64_t lifetime);
    void invalidate();
private:
    struct Active {std::string connection,policy,policy_hash;std::uint64_t lifetime,id,generation,opened,last;
        ProfileSnapshot image;std::size_t part=0,offset=0;};
    std::optional<Active> active_;std::uint64_t counter_=0;
};
struct ProfileView {Authored documents;ResourceSnapshot resources;Policy policy;std::set<std::string> capabilities;};
// For an already authenticated native stream only. No wire value authenticates
// a controller. Invalidate on disconnect/epoch/policy loss, even after completion.
class ProfileDownload {
public:
    ProfileDownload(std::string connection,std::string epoch,std::set<std::string> local_capabilities);
    Json request(const std::string& query);
    void receive(const protocol::Message&);
    bool complete()const{return view_.has_value();}
    const ProfileView& view()const;
    void invalidate();
private:
    void finish();
    std::string connection_,epoch_,query_,transfer_,revision_,generation_,hash_;
    std::set<std::string> capabilities_;std::vector<std::string> parts_;
    std::size_t count_=0,part_=0,offset_=0,part_bytes_=0,bytes_=0;
    bool invalid_=false;std::optional<ProfileView> view_;
};
}
