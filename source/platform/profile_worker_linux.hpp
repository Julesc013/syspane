#pragma once
#include "profile_store_linux.hpp"

namespace syspane::platform {
// Blocking facade for controller startup and serialized transaction workers.
// Owns one storage thread for the entire profile lifetime. Never call from GTK
// or a running session loop. Independent process supervision is still required.
class LinuxProfileWorker final:public configuration::GenerationStore {
public:
    LinuxProfileWorker(ProfileLocation,bool create,std::set<std::string> capabilities,
                       LinuxProfileStore::PolicySource={},LinuxProfileOwner::Transition={});
    ~LinuxProfileWorker()override;
    LinuxProfileWorker(const LinuxProfileWorker&)=delete;
    LinuxProfileWorker& operator=(const LinuxProfileWorker&)=delete;
    configuration::Committed load()const override;
    std::vector<configuration::CommitReceipt> receipts()const override;
    std::optional<configuration::Committed> reconcile(const std::string&,const std::string&,const std::string&)const override;
    configuration::Publication publish(const configuration::Committed&,const std::function<void()>&)override;
    ProfilePaths verified_paths()const;
    std::string generation_token()const;
    bool recovered_previous()const;
    // Call only after all transaction callers have stopped. Joins; never detaches.
    void close();
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
