#pragma once
#include "transaction.hpp"
#include <memory>

namespace syspane::platform {
// Explicit private development store. Ext-family primitive gate; the caller must
// admit its exact filesystem profile. Current native evidence covers ext4 only.
class LinuxGenerationStore final:public configuration::GenerationStore {
public:
    explicit LinuxGenerationStore(const std::string& directory,std::function<void(const char*)> transition={});
    ~LinuxGenerationStore()override;
    LinuxGenerationStore(const LinuxGenerationStore&)=delete;
    LinuxGenerationStore& operator=(const LinuxGenerationStore&)=delete;
    void initialize(const configuration::Authored& documents);
    // Explicit resource-backed revision zero, for an unpublished private profile stage.
    void bootstrap(const configuration::Committed&,const std::function<void()>& guard);
    configuration::Committed load()const override;
    // Identity of the verified loaded selecting record; unavailable for empty,
    // indeterminate or read-only recovery states. Not a fresh filesystem read.
    std::string generation_token()const;
    std::vector<configuration::CommitReceipt> receipts()const override;
    std::optional<configuration::Committed> reconcile(const std::string&,const std::string&,const std::string&)const override;
    configuration::Publication publish(const configuration::Committed&,const std::function<void()>&)override;
    bool recovered_previous()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
