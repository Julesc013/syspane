#pragma once
#include <cstdint>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace syspane::platform {
class ChildError : public std::runtime_error {
public:
    explicit ChildError(const char* code) : std::runtime_error(code) {}
};
struct ChildExit { bool signaled; std::uint32_t code; };
std::uint64_t current_process_id();
void arm_parent_lifetime(std::uint64_t expected_parent);
#if defined(__linux__)
// Called only inside an owned self child. PID/session and armed parent lifetime
// survive exec; the caller supplies the admitted canonical native ELF and args.
[[noreturn]] void exec_program(const std::string& path, const std::vector<std::string>& arguments,
                              std::uint64_t expected_parent);
#endif
class Child {
public:
    static Child launch_self(const std::vector<std::string>& arguments);
    ~Child();
    Child(Child&&) noexcept;
    Child& operator=(Child&&) = delete;
    Child(const Child&) = delete;
    Child& operator=(const Child&) = delete;
    std::uint64_t id() const;
    std::optional<ChildExit> wait(unsigned milliseconds = 0);
    void request_stop(); // Does not assert termination. Only wait() supplies proof.
#if defined(__linux__)
    void request_terminate(); // Exact held child SIGTERM; still requires wait().
    // Executes a held canonical ELF with only the supplied stdio, fd 3 holding
    // that ELF, and a clean environment. Borrowed descriptors must be >= 3.
    // The child entry point must close fd 3 and arm its parent lifetime.
    static Child launch_program(const std::string& path,const std::vector<std::string>& arguments,
                                int input,int output,int error);
    // Borrow an executable memfd sealed against writes/resizing/additional seals.
    // Name is diagnostic argv[0], not a path to reopen or an authority claim.
    static Child launch_sealed(int file,const std::string& name,const std::vector<std::string>& arguments,
                               int input,int output,int error);
#endif
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
    explicit Child(std::unique_ptr<Impl> impl);
#if defined(__linux__)
    static Child launch_held(int file,const std::string& name,const std::vector<std::string>& arguments,
                             int input,int output,int error,bool sealed);
#endif
};
inline void check_child_arguments(const std::vector<std::string>& arguments) {
    if (arguments.empty() || arguments.size() > 16) throw ChildError("child.arguments");
    std::size_t total = 0;
    for (const auto& argument : arguments) {
        if (argument.size() > 512) throw ChildError("child.arguments");
        for (unsigned char c : argument) if (c < 32 || c > 126) throw ChildError("child.arguments");
        total += argument.size() + 1;
    }
    if (total > 4096) throw ChildError("child.arguments");
}
} // namespace syspane::platform
