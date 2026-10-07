#if defined(__linux__)
#include "child.hpp"
#include "local_ipc.hpp"
#include <cerrno>
#include <csignal>
#include <cstdlib>
#include <fcntl.h>
#include <poll.h>
#include <spawn.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
#include <utility>
#include <array>
#include <sys/stat.h>

extern char** environ;
namespace syspane::platform {
namespace {
struct Actions {
    posix_spawn_file_actions_t value;
    Actions() { if (posix_spawn_file_actions_init(&value)) throw ChildError("child.actions"); }
    ~Actions() { posix_spawn_file_actions_destroy(&value); }
};
}
struct Child::Impl {
    int pidfd = -1;
    pid_t pid = -1;
    std::optional<ChildExit> exited;
    ~Impl() { if (pidfd >= 0) ::close(pidfd); }
};
Child::Child(std::unique_ptr<Impl> impl) : impl_(std::move(impl)) {}
Child::Child(Child&&) noexcept = default;
std::uint64_t current_process_id() { return static_cast<std::uint64_t>(::getpid()); }
void arm_parent_lifetime(std::uint64_t expected_parent) {
    if (!expected_parent || ::prctl(PR_SET_PDEATHSIG, SIGKILL) || static_cast<std::uint64_t>(::getppid()) != expected_parent)
        throw ChildError("child.parent_lifetime");
}
[[noreturn]] void exec_program(const std::string& path,const std::vector<std::string>& arguments,
                              std::uint64_t parent) {
    check_child_arguments(arguments);
    std::array<char,4096> canonical{};
    if (path.empty() || path.size()>512 || path.front()!='/' ||
        !::realpath(path.c_str(),canonical.data()) || path!=canonical.data()) throw ChildError("child.program_path");
    struct File { int fd=-1; ~File(){if(fd>=0)::close(fd);} } file;
    file.fd=::open(path.c_str(),O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    struct stat info{};std::array<unsigned char,4> magic{};
    if(file.fd<0 || ::fstat(file.fd,&info) || !S_ISREG(info.st_mode) || (info.st_mode&(S_ISUID|S_ISGID)) ||
       !(info.st_mode&0111) || ::pread(file.fd,magic.data(),magic.size(),0)!=4 ||
       magic!=std::array<unsigned char,4>{0x7f,'E','L','F'}) throw ChildError("child.program_type");
    std::vector<std::string> storage{path};storage.insert(storage.end(),arguments.begin(),arguments.end());
    std::vector<char*> argv;for(auto& argument:storage)argv.push_back(argument.data());argv.push_back(nullptr);
    arm_parent_lifetime(parent);
    ::fexecve(file.fd,argv.data(),environ);
    throw ChildError("child.exec");
}
Child Child::launch_self(const std::vector<std::string>& arguments) {
    check_child_arguments(arguments);
    struct sigaction action{};
    if (::sigaction(SIGCHLD, nullptr, &action) || action.sa_handler != SIG_DFL || (action.sa_flags & SA_NOCLDWAIT))
        throw ChildError("child.reaper_policy");
    Actions actions;
    if (posix_spawn_file_actions_addopen(&actions.value, 0, "/dev/null", O_RDONLY, 0) ||
        posix_spawn_file_actions_addopen(&actions.value, 1, "/dev/null", O_WRONLY, 0) ||
        posix_spawn_file_actions_addopen(&actions.value, 2, "/dev/null", O_WRONLY, 0) ||
        posix_spawn_file_actions_addclosefrom_np(&actions.value, 3)) throw ChildError("child.actions");
    std::vector<std::string> storage{ "/proc/self/exe" };
    storage.insert(storage.end(), arguments.begin(), arguments.end());
    std::vector<char*> argv;
    for (auto& argument : storage) argv.push_back(argument.data());
    argv.push_back(nullptr);
    auto impl = std::make_unique<Impl>();
    if (::posix_spawn(&impl->pid, "/proc/self/exe", &actions.value, nullptr, argv.data(), environ))
        throw ChildError("child.launch");
    Child child(std::move(impl));
    child.impl_->pidfd = static_cast<int>(::syscall(SYS_pidfd_open, child.impl_->pid, 0));
    if (child.impl_->pidfd < 0) throw ChildError("child.pidfd"); // Destructor cleans only our unreaped child.
    return child;
}
std::uint64_t Child::id() const { return static_cast<std::uint64_t>(impl_->pid); }
Child Child::launch_program(const std::string& path,const std::vector<std::string>& arguments,int input,int output,int error){
    check_child_arguments(arguments);
    if(input<3||output<3||error<3)throw ChildError("child.descriptors");
    struct sigaction action{};
    if(::sigaction(SIGCHLD,nullptr,&action)||action.sa_handler!=SIG_DFL||(action.sa_flags&SA_NOCLDWAIT))throw ChildError("child.reaper_policy");
    std::array<char,4096> canonical{};
    if(path.empty()||path.size()>512||path.front()!='/'||!::realpath(path.c_str(),canonical.data())||path!=canonical.data())throw ChildError("child.program_path");
    struct File{int fd;~File(){if(fd>=0)::close(fd);}} file{::open(path.c_str(),O_RDONLY|O_CLOEXEC|O_NOFOLLOW)};
    struct stat info{};std::array<unsigned char,4> magic{};
    if(file.fd<3||::fstat(file.fd,&info)||!S_ISREG(info.st_mode)||(info.st_mode&(S_ISUID|S_ISGID))||!(info.st_mode&0111)||
       ::pread(file.fd,magic.data(),magic.size(),0)!=4||magic!=std::array<unsigned char,4>{0x7f,'E','L','F'})throw ChildError("child.program_type");
    Actions actions;
    if(posix_spawn_file_actions_adddup2(&actions.value,input,0)||posix_spawn_file_actions_adddup2(&actions.value,output,1)||
       posix_spawn_file_actions_adddup2(&actions.value,error,2)||posix_spawn_file_actions_adddup2(&actions.value,file.fd,3)||
       posix_spawn_file_actions_addclosefrom_np(&actions.value,4))throw ChildError("child.actions");
    std::vector<std::string> storage{path};storage.insert(storage.end(),arguments.begin(),arguments.end());std::vector<char*> argv;
    for(auto& argument:storage)argv.push_back(argument.data());
    argv.push_back(nullptr);char language[]="LANG=C.UTF-8";char* environment[]={language,nullptr};
    auto impl=std::make_unique<Impl>();
    if(::posix_spawn(&impl->pid,"/proc/self/fd/3",&actions.value,nullptr,argv.data(),environment))throw ChildError("child.launch");
    Child child(std::move(impl));child.impl_->pidfd=static_cast<int>(::syscall(SYS_pidfd_open,child.impl_->pid,0));
    if(child.impl_->pidfd<0)throw ChildError("child.pidfd");
    return child;
}
std::optional<ChildExit> Child::wait(unsigned milliseconds) {
    if (milliseconds > 5000) throw ChildError("child.wait_limit");
    if (impl_->exited) return impl_->exited;
    const auto started = monotonic_ms();
    for (;;) {
        if (impl_->pidfd < 0) {
            // Only launch-failure cleanup reaches this path. SIGCHLD default and
            // sole-reaper ownership prevent reuse until this exact waitpid reaps.
            int status = 0;
            const auto result = ::waitpid(impl_->pid, &status, WNOHANG);
            if (result == impl_->pid) {
                impl_->exited = ChildExit{WIFSIGNALED(status), static_cast<std::uint32_t>(WIFSIGNALED(status) ? WTERMSIG(status) : WEXITSTATUS(status))};
                return impl_->exited;
            }
            if (result < 0 && errno != EINTR) throw ChildError("child.wait");
        } else {
            siginfo_t info{};
            if (::waitid(P_PIDFD, static_cast<id_t>(impl_->pidfd), &info, WEXITED | WNOHANG)) {
                if (errno != EINTR) throw ChildError("child.wait");
            } else if (info.si_pid) {
                impl_->exited = ChildExit{info.si_code != CLD_EXITED, static_cast<std::uint32_t>(info.si_status)};
                return impl_->exited;
            }
        }
        const auto elapsed = monotonic_ms() - started;
        if (elapsed >= milliseconds) return {};
        const auto remaining = milliseconds - static_cast<unsigned>(elapsed);
        pollfd fd{impl_->pidfd, POLLIN, 0};
        const int result = ::poll(&fd, impl_->pidfd < 0 ? 0 : 1, static_cast<int>(impl_->pidfd < 0 ? 1 : remaining));
        if (result < 0 && errno != EINTR) throw ChildError("child.poll");
    }
}
void Child::request_stop() {
    if (impl_->exited) return;
    const int result = impl_->pidfd < 0 ? ::kill(impl_->pid, SIGKILL)
        : static_cast<int>(::syscall(SYS_pidfd_send_signal, impl_->pidfd, SIGKILL, nullptr, 0));
    if (result && errno != ESRCH) throw ChildError("child.terminate");
}
void Child::request_terminate() {
    if(impl_->exited)return;
    if(impl_->pidfd<0)throw ChildError("child.pidfd");
    if(::syscall(SYS_pidfd_send_signal,impl_->pidfd,SIGTERM,nullptr,0) && errno!=ESRCH)
        throw ChildError("child.terminate");
}
Child::~Child() {
    if (!impl_) return;
    try { if (!wait(0)) { request_stop(); if (!wait(2000)) std::_Exit(125); } }
    catch (...) { std::_Exit(125); }
}
} // namespace syspane::platform
#endif
