#if defined(_WIN32)
#include "child.hpp"
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <array>
#include <cstdlib>
#include <utility>

namespace syspane::platform {
namespace {
struct Handle {
    HANDLE value = nullptr;
    ~Handle() { if (value) CloseHandle(value); }
    Handle() = default;
    Handle(const Handle&) = delete;
    Handle& operator=(const Handle&) = delete;
};
std::wstring quoted(const std::wstring& argument) {
    std::wstring out = L"\"";
    unsigned slashes = 0;
    for (wchar_t c : argument) {
        if (c == L'\\') { ++slashes; continue; }
        out.append(c == L'"' ? slashes * 2 + 1 : slashes, L'\\');
        out += c; slashes = 0;
    }
    out.append(slashes * 2, L'\\'); out += L'"';
    return out;
}
}
struct Child::Impl {
    Handle process, job;
    DWORD pid = 0;
    std::optional<ChildExit> exited;
};
Child::Child(std::unique_ptr<Impl> impl) : impl_(std::move(impl)) {}
Child::Child(Child&&) noexcept = default;
std::uint64_t current_process_id() { return GetCurrentProcessId(); }
void arm_parent_lifetime(std::uint64_t expected_parent) {
    // The retained parent job, assigned before this process ran, owns this bound.
    BOOL in_job = FALSE;
    if (!expected_parent || !IsProcessInJob(GetCurrentProcess(), nullptr, &in_job) || !in_job)
        throw ChildError("child.parent_job");
}
Child Child::launch_self(const std::vector<std::string>& arguments) {
    check_child_arguments(arguments);
    std::array<wchar_t, 32768> path{};
    const auto length = GetModuleFileNameW(nullptr, path.data(), static_cast<DWORD>(path.size()));
    if (!length || length >= path.size()) throw ChildError("child.module_path");
    std::wstring command = quoted(std::wstring(path.data(), length));
    for (const auto& argument : arguments) command += L" " + quoted(std::wstring(argument.begin(), argument.end()));
    if (command.size() >= 32767) throw ChildError("child.arguments");
    auto impl = std::make_unique<Impl>();
    impl->job.value = CreateJobObjectW(nullptr, nullptr);
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};
    limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_ACTIVE_PROCESS;
    limits.BasicLimitInformation.ActiveProcessLimit = 1;
    if (!impl->job.value || !SetInformationJobObject(impl->job.value, JobObjectExtendedLimitInformation, &limits, sizeof(limits)))
        throw ChildError("child.job");
    STARTUPINFOW startup{}; startup.cb = sizeof(startup);
    PROCESS_INFORMATION info{};
    if (!CreateProcessW(path.data(), command.data(), nullptr, nullptr, FALSE,
                        CREATE_NO_WINDOW | CREATE_SUSPENDED, nullptr, nullptr, &startup, &info))
        throw ChildError("child.launch");
    impl->process.value = info.hProcess; impl->pid = info.dwProcessId;
    Handle thread; thread.value = info.hThread;
    Child child(std::move(impl));
    if (!AssignProcessToJobObject(child.impl_->job.value, child.impl_->process.value)) throw ChildError("child.job_assign");
    if (ResumeThread(thread.value) == static_cast<DWORD>(-1)) throw ChildError("child.resume");
    return child;
}
std::uint64_t Child::id() const { return impl_->pid; }
std::optional<ChildExit> Child::wait(unsigned milliseconds) {
    if (milliseconds > 5000) throw ChildError("child.wait_limit");
    if (impl_->exited) return impl_->exited;
    const auto status = WaitForSingleObject(impl_->process.value, milliseconds);
    if (status == WAIT_TIMEOUT) return {};
    DWORD code = 0;
    if (status != WAIT_OBJECT_0 || !GetExitCodeProcess(impl_->process.value, &code)) throw ChildError("child.wait");
    impl_->exited = ChildExit{false, code};
    return impl_->exited;
}
void Child::request_stop() {
    if (impl_->exited) return;
    if (!TerminateProcess(impl_->process.value, 137) && !wait(0)) throw ChildError("child.terminate");
}
Child::~Child() {
    if (!impl_) return;
    try { if (!wait(0)) { request_stop(); if (!wait(2000)) std::_Exit(125); } }
    catch (...) { std::_Exit(125); }
}
} // namespace syspane::platform
#endif
