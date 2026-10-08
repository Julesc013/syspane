#pragma once
#include "profile_owner_linux.hpp"
namespace syspane::platform {
// Trusted controller worker composition. Returned authored data is not an external projection.
class LinuxProfileStore final:public configuration::GenerationStore {
public:
    using PolicySource=std::function<configuration::Policy()>;
    LinuxProfileStore(const ProfileLocation&,bool create,std::set<std::string> capabilities,
                      PolicySource={},LinuxProfileOwner::Transition={});
    ~LinuxProfileStore()override;
    LinuxProfileStore(const LinuxProfileStore&)=delete;
    LinuxProfileStore& operator=(const LinuxProfileStore&)=delete;
    configuration::Committed load()const override;
    std::vector<configuration::CommitReceipt> receipts()const override;
    std::optional<configuration::Committed> reconcile(const std::string&,const std::string&,const std::string&)const override;
    configuration::Publication publish(const configuration::Committed&,const std::function<void()>&)override;
    ProfilePaths verified_paths()const;
    std::string generation_token()const;
    bool recovered_previous()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
