#pragma once
#include "entry.hpp"
#include "preservation.hpp"
#include <memory>
#include <thread>

namespace syspane::diagnostics {
// Single GUI-thread owner. Destroy only when the diagnostic entry is about to exit.
// A worker owns copies of its policy callback and immutable paths; never GUI objects.
class PreservationJob {
public:
    using PolicyReader = std::function<configuration::Policy()>;
    explicit PreservationJob(PolicyReader policy);
    ~PreservationJob();
    PreservationJob(const PreservationJob&) = delete;
    PreservationJob& operator=(const PreservationJob&) = delete;
    bool permitted() const;
    bool busy() const;
    bool start(std::string source, std::string destination);
    void cancel();
    std::string status() const;
private:
    struct State;
    PolicyReader policy_;
    std::shared_ptr<State> state_;
    std::thread worker_;
};
}
