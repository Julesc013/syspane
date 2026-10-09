#pragma once
#include "editor_draft.hpp"

namespace syspane::interfaces {
struct RequestPreparationStatus {bool ready=false,stopped=false;std::string error;bool running=false;};
// GUI-owned handle. stopped acknowledges computation and input destruction;
// taking a result grants no authority to adopt or submit it.
class RequestPreparationTask {
public:
    virtual ~RequestPreparationTask()=default;
    virtual RequestPreparationStatus status()const=0;
    virtual std::unique_ptr<RequestPrepared> take()=0;
    virtual void cancel()=0;
};
using RequestPreparationFactory=std::function<std::unique_ptr<RequestPreparationTask>(std::unique_ptr<RequestWork>)>;
}
