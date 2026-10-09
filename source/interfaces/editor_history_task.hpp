#pragma once
#include "editor_draft.hpp"

namespace syspane::interfaces {
struct HistoryPreparationStatus {bool ready=false,stopped=false;std::string error;bool running=false;};
// GUI-owned handle to detached work. stopped acknowledges input destruction;
// taking a result never authorizes adoption into a changed or replaced draft.
class HistoryPreparationTask {
public:
    virtual ~HistoryPreparationTask()=default;
    virtual HistoryPreparationStatus status()const=0;
    virtual std::unique_ptr<HistoryPrepared> take()=0;
    virtual void cancel()=0;
};
using HistoryPreparationFactory=std::function<std::unique_ptr<HistoryPreparationTask>(std::unique_ptr<HistoryWork>)>;
}
