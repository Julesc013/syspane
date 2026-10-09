#pragma once
#include <cstddef>
#include <cstdint>
#include <string>
#include <functional>
#include <memory>
#include <optional>

namespace syspane::interfaces {
constexpr std::size_t recovery_record_limit=786432;
// The native owner derives these from its private profile and verified committed
// selector/manifest. Values read from a recovery record are never trusted inputs.
struct RecoveryIdentity {std::string profile,generation;};
struct RecoveryDescription {
    std::string scene_id;
    std::uint64_t revision=0;
    std::size_t widgets=0;
    bool theme_changed=false;
};
class EditorDraft;
class RecoveryPrepared {
public:
    ~RecoveryPrepared();
    RecoveryPrepared(const RecoveryPrepared&)=delete;
    RecoveryPrepared& operator=(const RecoveryPrepared&)=delete;
private:
    friend class EditorDraft;friend class RecoveryWork;
    struct Impl;explicit RecoveryPrepared(std::unique_ptr<Impl>);
    std::unique_ptr<Impl> impl_;
};
class RecoveryWork {
public:
    ~RecoveryWork();
    RecoveryWork(const RecoveryWork&)=delete;
    RecoveryWork& operator=(const RecoveryWork&)=delete;
    std::unique_ptr<RecoveryPrepared> run(); // One detached, pure computation.
private:
    friend class EditorDraft;
    struct Impl;explicit RecoveryWork(std::unique_ptr<Impl>);
    std::unique_ptr<Impl> impl_;
};
struct RecoveryPreparationStatus {bool ready=false,stopped=false;std::string error;bool running=false;};
class RecoveryPreparationTask {
public:
    virtual ~RecoveryPreparationTask()=default;
    virtual RecoveryPreparationStatus status()const=0;
    virtual std::unique_ptr<RecoveryPrepared> take()=0;
    virtual void cancel()=0;
};
using RecoveryPreparationFactory=std::function<std::unique_ptr<RecoveryPreparationTask>(std::unique_ptr<RecoveryWork>)>;
}
