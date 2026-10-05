#if defined(__linux__)
#include "local_ipc.hpp"
#include <algorithm>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <filesystem>
#include <fcntl.h>
#include <linux/capability.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/un.h>
#include <unistd.h>
#include <utility>

namespace syspane::platform {
namespace {
constexpr std::size_t max_io = 1048580;
class Fd {
public:
    explicit Fd(int fd = -1) : value(fd) {}
    ~Fd() { if (value >= 0) ::close(value); }
    Fd(Fd&& other) noexcept : value(std::exchange(other.value, -1)) {}
    Fd& operator=(Fd&& other) noexcept {
        if (this != &other) { if (value >= 0) ::close(value); value = std::exchange(other.value, -1); }
        return *this;
    }
    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;
    int value;
};
unsigned remaining(std::uint64_t deadline) {
    const auto now = monotonic_ms();
    return now >= deadline ? 0 : static_cast<unsigned>(std::min<std::uint64_t>(deadline - now, 5000));
}
bool wait(int fd, short events, std::uint64_t deadline) {
    for (;;) {
        const auto left = remaining(deadline);
        if (!left) return false;
        pollfd item{fd, events, 0};
        const int ready = ::poll(&item, 1, static_cast<int>(left));
        if (ready < 0 && errno == EINTR) continue;
        if (ready < 0 || (ready > 0 && (item.revents & POLLNVAL))) throw IpcError("io.poll");
        if (ready) return true; // HUP/ERR are interpreted by recv/send/accept.
    }
}
void check_timeout(unsigned value) {
    if (value == 0 || value > 5000) throw IpcError("io.limit");
}
sockaddr_un address(const std::string& path) {
    sockaddr_un result{};
    result.sun_family = AF_UNIX;
    if (path.empty() || path.find('\0') != std::string::npos || path.size() >= sizeof(result.sun_path)) throw IpcError("endpoint.path");
    std::memcpy(result.sun_path, path.c_str(), path.size() + 1);
    return result;
}
Fd directory(const std::string& endpoint) {
    const std::filesystem::path path(endpoint);
    std::error_code error;
    const auto parent = path.parent_path();
    if (!path.is_absolute() || path.filename() != "s" || std::filesystem::canonical(parent, error) != parent || error)
        throw IpcError("endpoint.path");
    Fd fd(::open(parent.c_str(), O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC));
    struct stat info{};
    if (fd.value < 0 || ::fstat(fd.value, &info) || !S_ISDIR(info.st_mode) || info.st_uid != ::geteuid() ||
        (info.st_mode & 0777) != 0700) throw IpcError("endpoint.directory");
    return fd;
}
Fd socket_fd() {
    Fd fd(::socket(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0));
    if (fd.value < 0) throw IpcError("io.socket");
    return fd;
}
bool alive(int fd) {
    pollfd item{fd, POLLIN, 0};
    int result;
    do { result = ::poll(&item, 1, 0); } while (result < 0 && errno == EINTR);
    return result == 0;
}
Peer identify(int socket, Fd& peer_handle, std::uint64_t expected_process) {
    ucred credentials{};
    socklen_t size = sizeof(credentials);
    if (::getsockopt(socket, SOL_SOCKET, SO_PEERCRED, &credentials, &size) || size != sizeof(credentials) || credentials.pid <= 0)
        throw IpcError("peer.credentials");
    int pidfd = -1; size = sizeof(pidfd);
    if (::getsockopt(socket, SOL_SOCKET, SO_PEERPIDFD, &pidfd, &size) || pidfd < 0 || size != sizeof(pidfd))
        throw IpcError("peer.pidfd_unavailable");
    peer_handle = Fd(pidfd);
    if (::fcntl(pidfd, F_SETFD, FD_CLOEXEC) < 0) throw IpcError("peer.handle");
    if (!alive(pidfd)) throw IpcError("peer.exited");
    const auto session = ::getsid(credentials.pid), own_session = ::getsid(0);
    if (session < 0 || own_session < 0 || !alive(pidfd)) throw IpcError("peer.exited");
    if (credentials.uid != ::geteuid()) throw IpcError("peer.user");
    if (session != own_session) throw IpcError("peer.session");
    if (expected_process && expected_process != static_cast<std::uint64_t>(credentials.pid)) throw IpcError("peer.process");
    return {"linux:" + std::to_string(credentials.uid) + ":" + std::to_string(session), static_cast<std::uint64_t>(credentials.pid)};
}
}
std::uint64_t monotonic_ms() {
    return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
}
bool unprivileged_context() {
    __user_cap_header_struct header{_LINUX_CAPABILITY_VERSION_3, 0};
    __user_cap_data_struct data[2]{};
    return ::geteuid() != 0 && ::getuid() == ::geteuid() && ::getgid() == ::getegid() &&
        ::syscall(SYS_capget, &header, &data) == 0 && data[0].effective == 0 && data[1].effective == 0;
}
struct Stream::Impl {
    Fd socket, peer_handle;
    Peer peer;
    std::uint64_t connected;
    Impl(Fd value, std::uint64_t expected) : socket(std::move(value)), peer{}, connected(monotonic_ms()) {
        peer = identify(socket.value, peer_handle, expected);
    }
};
struct Listener::Impl {
    Fd directory, socket;
    struct stat owned{};
    bool bound = false;
    explicit Impl(Fd dir) : directory(std::move(dir)), socket(socket_fd()) {}
    ~Impl() {
        struct stat current{};
        if (bound && !::fstatat(directory.value, "s", &current, AT_SYMLINK_NOFOLLOW) &&
            S_ISSOCK(current.st_mode) && current.st_dev == owned.st_dev && current.st_ino == owned.st_ino && current.st_uid == ::geteuid())
            ::unlinkat(directory.value, "s", 0);
    }
};
Stream::Stream(std::unique_ptr<Impl> impl) : impl_(std::move(impl)) {}
Stream::~Stream() = default;
Stream::Stream(Stream&&) noexcept = default;
Stream& Stream::operator=(Stream&&) noexcept = default;
const Peer& Stream::peer() const { return impl_->peer; }
std::uint64_t Stream::connected_ms() const { return impl_->connected; }
Stream Stream::connect(const std::string& endpoint, std::uint64_t expected) {
    auto dir = directory(endpoint);
    struct stat node{};
    if (::fstatat(dir.value, "s", &node, AT_SYMLINK_NOFOLLOW) || !S_ISSOCK(node.st_mode) ||
        node.st_uid != ::geteuid() || (node.st_mode & 0777) != 0600) throw IpcError("endpoint.socket");
    const auto addr = address("/proc/self/fd/" + std::to_string(dir.value) + "/s");
    auto fd = socket_fd();
    const auto deadline = monotonic_ms() + 5000;
    if (::connect(fd.value, reinterpret_cast<const sockaddr*>(&addr), sizeof(addr)) < 0) {
        if (errno != EINPROGRESS && errno != EAGAIN) throw IpcError("io.connect");
        if (!wait(fd.value, POLLOUT, deadline)) throw IpcError("io.timeout");
        int error = 0; socklen_t size = sizeof(error);
        if (::getsockopt(fd.value, SOL_SOCKET, SO_ERROR, &error, &size) || error) throw IpcError("io.connect");
    }
    return Stream(std::make_unique<Impl>(std::move(fd), expected));
}
Read Stream::read(char* buffer, std::size_t capacity, unsigned timeout) {
    check_timeout(timeout);
    if (!buffer || capacity == 0 || capacity > max_io) throw IpcError("io.limit");
    const auto deadline = monotonic_ms() + timeout;
    for (;;) {
        const auto n = ::recv(impl_->socket.value, buffer, capacity, 0);
        if (n >= 0) return {static_cast<std::size_t>(n), n == 0, false, monotonic_ms()};
        if (errno == EINTR) { if (!remaining(deadline)) return {0, false, true, monotonic_ms()}; continue; }
        if (errno != EAGAIN && errno != EWOULDBLOCK) throw IpcError("io.read");
        if (!wait(impl_->socket.value, POLLIN, deadline)) return {0, false, true, monotonic_ms()};
    }
}
void Stream::write(std::string_view bytes, unsigned timeout) {
    check_timeout(timeout);
    if (bytes.empty() || bytes.size() > max_io) throw IpcError("io.limit");
    const auto deadline = monotonic_ms() + timeout;
    while (!bytes.empty()) {
        if (!remaining(deadline)) throw IpcError("io.timeout");
        const auto n = ::send(impl_->socket.value, bytes.data(), bytes.size(), MSG_NOSIGNAL);
        if (n > 0) { bytes.remove_prefix(static_cast<std::size_t>(n)); continue; }
        if (n < 0 && errno == EINTR) continue;
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            if (!wait(impl_->socket.value, POLLOUT, deadline)) throw IpcError("io.timeout");
            continue;
        }
        throw IpcError("io.write");
    }
    if (!remaining(deadline)) throw IpcError("io.timeout");
}
Listener::Listener(const std::string& endpoint) {
    address(endpoint); // Validate the advertised path, even though bind uses the held directory.
    impl_ = std::make_unique<Impl>(directory(endpoint));
    const auto addr = address("/proc/self/fd/" + std::to_string(impl_->directory.value) + "/s");
    if (::bind(impl_->socket.value, reinterpret_cast<const sockaddr*>(&addr), sizeof(addr))) throw IpcError("endpoint.collision");
    if (::fstatat(impl_->directory.value, "s", &impl_->owned, AT_SYMLINK_NOFOLLOW)) throw IpcError("endpoint.stat");
    impl_->bound = true;
    if (::fchmodat(impl_->directory.value, "s", 0600, 0) || ::listen(impl_->socket.value, 1)) throw IpcError("endpoint.listen");
}
Listener::~Listener() = default;
Stream Listener::accept(std::uint64_t expected) {
    const auto deadline = monotonic_ms() + 5000;
    for (;;) {
        Fd fd(::accept4(impl_->socket.value, nullptr, nullptr, SOCK_NONBLOCK | SOCK_CLOEXEC));
        if (fd.value >= 0) return Stream(std::make_unique<Stream::Impl>(std::move(fd), expected));
        if (errno == EINTR) { if (!remaining(deadline)) throw IpcError("io.timeout"); continue; }
        if (errno != EAGAIN && errno != EWOULDBLOCK) throw IpcError("io.accept");
        if (!wait(impl_->socket.value, POLLIN, deadline)) throw IpcError("io.timeout");
    }
}
bool Listener::access_controls_verified() const {
    struct stat dir{}, node{};
    return !::fstat(impl_->directory.value, &dir) && !::fstatat(impl_->directory.value, "s", &node, AT_SYMLINK_NOFOLLOW) &&
        (dir.st_mode & 0777) == 0700 && dir.st_uid == ::geteuid() && S_ISSOCK(node.st_mode) &&
        (node.st_mode & 0777) == 0600 && node.st_uid == ::geteuid() && node.st_ino == impl_->owned.st_ino && node.st_dev == impl_->owned.st_dev;
}
} // namespace syspane::platform
#endif
