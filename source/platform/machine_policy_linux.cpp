#ifndef _WIN32
#include "machine_policy.hpp"
#include <array>
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace syspane::platform {
namespace {
struct Fd {
    int value;
    ~Fd() { if (value >= 0) ::close(value); }
    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;
    explicit Fd(int fd) : value(fd) {}
};
bool protected_object(int fd, bool directory, struct stat& state) {
    if (fd < 0 || ::fstat(fd, &state) != 0 || state.st_uid != 0 || (state.st_mode & 0022)) return false;
    return directory ? S_ISDIR(state.st_mode) : (S_ISREG(state.st_mode) && state.st_nlink == 1 && state.st_size > 0 && state.st_size <= 65536);
}
bool same(const struct stat& a, const struct stat& b) {
    return a.st_dev == b.st_dev && a.st_ino == b.st_ino && a.st_size == b.st_size &&
        a.st_mtim.tv_sec == b.st_mtim.tv_sec && a.st_mtim.tv_nsec == b.st_mtim.tv_nsec &&
        a.st_ctim.tv_sec == b.st_ctim.tv_sec && a.st_ctim.tv_nsec == b.st_ctim.tv_nsec;
}
}
configuration::Policy machine_policy() {
    try {
        const int flags = O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW;
        Fd root(::open("/", flags));
        struct stat state{};
        if (!protected_object(root.value, true, state)) return {};
        Fd etc(::openat(root.value, "etc", flags));
        if (!protected_object(etc.value, true, state)) return {};
        Fd directory(::openat(etc.value, "syspane", flags));
        if (!protected_object(directory.value, true, state)) return {};
        Fd file(::openat(directory.value, "policy.json", O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
        struct stat before{}, after{};
        if (!protected_object(file.value, false, before)) return {};
        std::array<char, 65537> bytes{};
        std::size_t count = 0;
        unsigned interruptions = 0;
        while (count < bytes.size()) {
            const auto n = ::read(file.value, bytes.data() + count, bytes.size() - count);
            if (n < 0) {
                if (errno == EINTR && ++interruptions <= 16) continue;
                return {};
            }
            if (n == 0) break;
            count += static_cast<std::size_t>(n);
        }
        if (count != static_cast<std::size_t>(before.st_size) || !protected_object(file.value, false, after) || !same(before, after) ||
            !protected_object(root.value, true, state) || !protected_object(etc.value, true, state) || !protected_object(directory.value, true, state)) return {};
        auto policy = configuration::decode_policy(std::string_view(bytes.data(), count));
        policy.available = true;
        return policy;
    } catch (const std::exception&) { return {}; }
}
}
#endif
