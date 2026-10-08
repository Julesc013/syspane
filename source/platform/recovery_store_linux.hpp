#pragma once
#include "transaction.hpp"
#include <memory>

namespace syspane::platform {
struct RecoveryVersion {
    std::string instance;
    std::uint64_t sequence=0;
    std::optional<std::string> digest;
};
struct RecoverySnapshot {
    RecoveryVersion version;
    std::optional<std::string> bytes;
    bool pending=false;
};
struct RecoveryPublication {
    configuration::Publication outcome=configuration::Publication::unchanged;
    std::string error;
};
// One serialized worker thread, private caller-selected ext4 development root.
// Bytes remain untrusted until EditorDraft inspects them with current authority.
class LinuxRecoveryStore {
public:
    using Guard=std::function<bool()>;
    static constexpr std::size_t maximum_bytes=786432;
    explicit LinuxRecoveryStore(const std::string& directory,std::function<void(const char*)> transition={});
    ~LinuxRecoveryStore();
    LinuxRecoveryStore(const LinuxRecoveryStore&)=delete;
    LinuxRecoveryStore& operator=(const LinuxRecoveryStore&)=delete;
    RecoverySnapshot snapshot(const Guard&)const;
    RecoveryPublication replace(const RecoveryVersion&,std::string_view,const Guard&);
    RecoveryPublication retire(const RecoveryVersion&,const Guard&);
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
