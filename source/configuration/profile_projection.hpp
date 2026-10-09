#pragma once
#include "transaction.hpp"
#include "profile.hpp"

namespace syspane::configuration {
struct ProfileRecoveryDirectory {
    std::string path;
    std::uint64_t uid,state_device,state_inode,recovery_device,recovery_inode;
};
struct ProfileRecoveryData {
    std::string profile,generation;ProfileRecoveryDirectory directory;
    std::uint64_t policy_revision;bool erase;
};
struct ProfileRecoveryScope {std::string profile,editor_session;};
// Bound observations from an authenticated stream, never native filesystem authority.
struct ProfileRecoveryView {
    ProfileRecoveryData admission;std::string connection,epoch,editor_session;
    std::uint64_t transfer,revision;
};
// Prepare only on the supervised storage/command worker. Validated package bytes
// remain shared and immutable; a transfer does no filesystem work or media hashing.
class ProfileImage {
public:
    ProfileImage(const Committed&,std::set<std::string> capabilities,std::optional<ProfileRecoveryData> recovery={});
    std::uint64_t revision()const{return revision_;}
    std::size_t count()const{return parts_.size();}
    std::size_t bytes()const{return bytes_;}
    const std::string& part(std::size_t)const;
    const std::string& hash(std::size_t)const;
    const std::string& recovery_header()const{return recovery_header_;}
    const std::string& recovery_header_hash()const{return recovery_header_hash_;}
    Json context(const Authority&,const Policy&,const std::string& connection,const std::string& epoch,
                 const ProfileRecoveryScope&,std::uint64_t transfer)const;
    void authorize(const Authority&,const Policy&)const;
private:
    struct Part {std::string text,hash,asset;std::shared_ptr<const ContentPackage> package;};
    std::vector<Part> parts_;ResourceSnapshot resources_;std::set<std::string> capabilities_;
    std::uint64_t revision_;std::size_t bytes_=0;
    std::optional<ProfileRecoveryData> recovery_;std::string recovery_header_,recovery_header_hash_;
};
using ProfileSnapshot=std::shared_ptr<const ProfileImage>;
// One controller-wide slot. All methods run on the owning session loop.
class ProfileTransfer {
public:
    Json receive(const std::string& connection,std::uint64_t lifetime,const Authority&,const Policy&,
                 ProfileSnapshot,const Json& request,std::uint64_t now,const std::string& epoch={});
    bool expired(const std::string&,std::uint64_t lifetime,std::uint64_t now)const;
    void disconnect(const std::string&,std::uint64_t lifetime);
    void invalidate();
private:
    struct Active {std::string connection,policy,policy_hash,version;std::uint64_t lifetime,id,generation,opened,last;
        ProfileSnapshot image;std::size_t part=0,offset=0;};
    std::optional<Active> active_;std::uint64_t counter_=0;
};
struct ProfileView {Authored documents;ResourceSnapshot resources;Policy policy;std::set<std::string> capabilities;std::optional<ProfileRecoveryView> recovery;};
// For an already authenticated native stream only. No wire value authenticates
// a controller. Invalidate on disconnect/epoch/policy loss, even after completion.
class ProfileDownload {
public:
    ProfileDownload(std::string connection,std::string epoch,std::set<std::string> local_capabilities,std::optional<ProfileRecoveryScope> scope={});
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
    std::optional<ProfileRecoveryScope> scope_;
};
}
