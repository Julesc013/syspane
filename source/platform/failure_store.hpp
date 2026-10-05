#pragma once
#include "failure_history.hpp"
#include <memory>

namespace syspane::platform {
// Explicit caller-selected paths only. No policy/configuration discovery or overwrite.
diagnostics::FailureHistory read_failure_file(const std::string& utf8_path);
bool failure_path_valid(const std::string& utf8_path);
std::vector<std::string> native_arguments(int argc, char** argv);
class FailureWriter {
public:
    explicit FailureWriter(const std::string& utf8_path);
    ~FailureWriter();
    FailureWriter(const FailureWriter&) = delete;
    FailureWriter& operator=(const FailureWriter&) = delete;
    bool ready() const;
    bool append(std::uint64_t elapsed_ms, const std::string& role, const std::string& reason, bool stopped);
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};
}
