#if defined(_WIN32)
#include "local_ipc.hpp"
#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <aclapi.h>
#include <sddl.h>
#include <algorithm>
#include <chrono>
#include <limits>
#include <optional>
#include <utility>
#include <vector>

namespace syspane::platform {
namespace {
constexpr DWORD client_rights = FILE_GENERIC_READ | FILE_WRITE_DATA | FILE_WRITE_EA | FILE_WRITE_ATTRIBUTES;
constexpr std::size_t max_io = 1048580;
class Handle {
public:
    explicit Handle(HANDLE value = INVALID_HANDLE_VALUE) : value(value) {}
    ~Handle() { if (valid()) ::CloseHandle(value); }
    Handle(Handle&& other) noexcept : value(std::exchange(other.value, INVALID_HANDLE_VALUE)) {}
    Handle& operator=(Handle&& other) noexcept {
        if (this != &other) { if (valid()) ::CloseHandle(value); value = std::exchange(other.value, INVALID_HANDLE_VALUE); }
        return *this;
    }
    Handle(const Handle&) = delete;
    Handle& operator=(const Handle&) = delete;
    bool valid() const { return value && value != INVALID_HANDLE_VALUE; }
    HANDLE value;
};
struct LocalMemory {
    void* value = nullptr;
    ~LocalMemory() { if (value) ::LocalFree(value); }
};
struct Identity {
    std::string user, logon;
    DWORD session;
    LUID authentication;
};
std::vector<unsigned char> token_info(HANDLE token, TOKEN_INFORMATION_CLASS kind) {
    DWORD size = 0;
    ::GetTokenInformation(token, kind, nullptr, 0, &size);
    if (!size || size > 65536) throw IpcError("peer.token");
    std::vector<unsigned char> bytes(size);
    if (!::GetTokenInformation(token, kind, bytes.data(), size, &size)) throw IpcError("peer.token");
    return bytes;
}
std::string sid_string(PSID sid) {
    LPSTR text = nullptr;
    if (!::ConvertSidToStringSidA(sid, &text)) throw IpcError("peer.sid");
    LocalMemory memory{text};
    return text;
}
Identity identity(HANDLE token) {
    const auto user = token_info(token, TokenUser), groups = token_info(token, TokenGroups),
               session = token_info(token, TokenSessionId), stats = token_info(token, TokenStatistics);
    Identity result{sid_string(reinterpret_cast<const TOKEN_USER*>(user.data())->User.Sid), {},
        *reinterpret_cast<const DWORD*>(session.data()), reinterpret_cast<const TOKEN_STATISTICS*>(stats.data())->AuthenticationId};
    const auto* group = reinterpret_cast<const TOKEN_GROUPS*>(groups.data());
    for (DWORD i = 0; i < group->GroupCount; ++i) {
        if ((group->Groups[i].Attributes & SE_GROUP_LOGON_ID) == SE_GROUP_LOGON_ID) result.logon = sid_string(group->Groups[i].Sid);
    }
    if (result.logon.empty()) throw IpcError("peer.logon");
    return result;
}
Identity process_identity(HANDLE process) {
    HANDLE raw = nullptr;
    if (!::OpenProcessToken(process, TOKEN_QUERY, &raw)) throw IpcError("peer.process_token");
    Handle token(raw);
    return identity(token.value);
}
void compare(const Identity& peer, const Identity& own) {
    if (peer.user != own.user) throw IpcError("peer.user");
    if (peer.session != own.session || peer.logon != own.logon || peer.authentication.HighPart != own.authentication.HighPart ||
        peer.authentication.LowPart != own.authentication.LowPart) throw IpcError("peer.session");
}
std::string principal(const Identity& value) {
    return "windows:" + value.user + ":" + std::to_string(value.session) + ":" +
        std::to_string(static_cast<DWORD>(value.authentication.HighPart)) + ":" + std::to_string(value.authentication.LowPart);
}
std::wstring pipe_name(const std::string& endpoint) {
    const std::string prefix = "\\\\.\\pipe\\SysPane.Dev.";
    if (endpoint.size() <= prefix.size() || endpoint.size() > 200 || endpoint.compare(0, prefix.size(), prefix) != 0 ||
        !std::all_of(endpoint.begin() + static_cast<std::ptrdiff_t>(prefix.size()), endpoint.end(), [](char c) {
            return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-';
        })) throw IpcError("endpoint.path");
    return std::wstring(endpoint.begin(), endpoint.end());
}
DWORD remaining(std::uint64_t deadline) {
    const auto now = monotonic_ms();
    return now >= deadline ? 0 : static_cast<DWORD>(std::min<std::uint64_t>(deadline - now, 5000));
}
[[noreturn]] void fatal_lifetime() { ::TerminateProcess(::GetCurrentProcess(), 125); std::terminate(); }
void drain(HANDLE pipe, OVERLAPPED& operation) {
    ::CancelIoEx(pipe, &operation);
    if (::WaitForSingleObject(operation.hEvent, 1000) != WAIT_OBJECT_0) fatal_lifetime();
}
struct Io {
    DWORD bytes = 0;
    bool eof = false, timeout = false;
};
Io transfer(HANDLE pipe, void* data, DWORD size, bool writing, std::uint64_t deadline) {
    Handle event(::CreateEventW(nullptr, TRUE, FALSE, nullptr));
    if (!event.valid()) throw IpcError("io.event");
    OVERLAPPED operation{}; operation.hEvent = event.value;
    DWORD count = 0;
    const BOOL started = writing ? ::WriteFile(pipe, data, size, &count, &operation) : ::ReadFile(pipe, data, size, &count, &operation);
    if (started) return {count, count == 0 && !writing, writing && !remaining(deadline)};
    auto error = ::GetLastError();
    if (error == ERROR_BROKEN_PIPE || error == ERROR_PIPE_NOT_CONNECTED) {
        if (writing) throw IpcError("io.write");
        return {0, true, false};
    }
    if (error != ERROR_IO_PENDING) throw IpcError(writing ? "io.write" : "io.read");
    const auto wait = ::WaitForSingleObject(event.value, remaining(deadline));
    if (wait != WAIT_OBJECT_0) drain(pipe, operation);
    if (::GetOverlappedResult(pipe, &operation, &count, FALSE)) return {count, count == 0 && !writing, writing && !remaining(deadline)};
    error = ::GetLastError();
    if (error == ERROR_OPERATION_ABORTED && wait != WAIT_OBJECT_0) return {0, false, true};
    if ((error == ERROR_BROKEN_PIPE || error == ERROR_PIPE_NOT_CONNECTED) && !writing) return {0, true, false};
    throw IpcError(writing ? "io.write" : "io.read");
}
Peer process_peer(HANDLE pipe, bool server, const Identity& own, Handle& held_process, std::uint64_t expected) {
    ULONG pid = 0;
    const BOOL found = server ? ::GetNamedPipeClientProcessId(pipe, &pid) : ::GetNamedPipeServerProcessId(pipe, &pid);
    if (!found || !pid) throw IpcError("peer.process_id");
    held_process = Handle(::OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, FALSE, pid));
    if (!held_process.valid() || ::WaitForSingleObject(held_process.value, 0) != WAIT_TIMEOUT) throw IpcError("peer.exited");
    const auto token = process_identity(held_process.value);
    compare(token, own);
    if (expected && expected != pid) throw IpcError("peer.process");
    return {principal(token), pid};
}
void identify_client_token(HANDLE pipe, const Identity& own) {
    if (!::ImpersonateNamedPipeClient(pipe)) throw IpcError("peer.identification");
    // No file, network, policy or application action while identifying the token.
    try {
        HANDLE raw = nullptr;
        if (!::OpenThreadToken(::GetCurrentThread(), TOKEN_QUERY, TRUE, &raw)) throw IpcError("peer.thread_token");
        Handle token(raw);
        const auto peer = identity(token.value);
        compare(peer, own);
    } catch (...) {
        if (!::RevertToSelf()) fatal_lifetime();
        throw;
    }
    if (!::RevertToSelf()) fatal_lifetime();
}
struct PipeSlot {
    Handle pipe;
    bool busy = false;
    explicit PipeSlot(HANDLE handle) : pipe(handle) {}
};
}
std::uint64_t monotonic_ms() {
    return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
}
bool unprivileged_context() {
    HANDLE raw = nullptr;
    if (!::OpenProcessToken(::GetCurrentProcess(), TOKEN_QUERY, &raw)) return false;
    Handle token(raw);
    const auto elevation = token_info(token.value, TokenElevation);
    return reinterpret_cast<const TOKEN_ELEVATION*>(elevation.data())->TokenIsElevated == 0;
}
struct Stream::Impl {
    Handle client, peer_handle;
    std::shared_ptr<PipeSlot> server;
    Peer peer{};
    std::uint64_t connected = 0, first_observed = 0;
    std::optional<char> first_byte;
    std::optional<std::uint64_t> measurement_last;
    bool measurement_fault = false;
    HANDLE handle() const { return server ? server->pipe.value : client.value; }
    ~Impl() {
        if (server) { ::DisconnectNamedPipe(server->pipe.value); server->busy = false; }
    }
};
struct Listener::Impl {
    Identity own;
    std::shared_ptr<PipeSlot> slot;
    explicit Impl(Identity identity) : own(std::move(identity)) {}
};
Stream::Stream(std::unique_ptr<Impl> impl) : impl_(std::move(impl)) {}
Stream::~Stream() = default;
Stream::Stream(Stream&&) noexcept = default;
Stream& Stream::operator=(Stream&&) noexcept = default;
const Peer& Stream::peer() const { return impl_->peer; }
std::uint64_t Stream::connected_ms() const { return impl_->connected; }
MeasurementClock Stream::measurement_clock() {
    if (impl_->measurement_fault) throw IpcError("clock.unavailable");
    try {
        const auto require_peer = [&] {
            const auto state = ::WaitForSingleObject(impl_->peer_handle.value, 0);
            if (state == WAIT_OBJECT_0) throw IpcError("clock.peer_exited");
            if (state != WAIT_TIMEOUT) throw IpcError("clock.peer_unavailable");
        };
        require_peer();
        ULONGLONG tick = 0;
        ::QueryInterruptTimePrecise(&tick);
        if (tick > std::numeric_limits<std::uint64_t>::max() / 100) throw IpcError("clock.range");
        const auto count = static_cast<std::uint64_t>(tick) * 100;
        require_peer();
        if (impl_->measurement_last && count < *impl_->measurement_last) throw IpcError("clock.regressed");
        impl_->measurement_last = count;
        return {"windows.interrupt-precise", count, 100};
    } catch (...) { impl_->measurement_fault = true; throw; }
}
Stream Stream::connect(const std::string& endpoint, std::uint64_t expected) {
    const auto name = pipe_name(endpoint);
    const auto own = process_identity(::GetCurrentProcess());
    const auto deadline = monotonic_ms() + 5000;
    auto state = std::make_unique<Impl>();
    for (;;) {
        state->client = Handle(::CreateFileW(name.c_str(), client_rights, 0, nullptr, OPEN_EXISTING,
            FILE_FLAG_OVERLAPPED | SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION, nullptr));
        if (state->client.valid()) break;
        if (::GetLastError() != ERROR_PIPE_BUSY) throw IpcError("io.connect");
        if (!remaining(deadline) || !::WaitNamedPipeW(name.c_str(), remaining(deadline))) throw IpcError("io.timeout");
    }
    state->connected = monotonic_ms();
    state->peer = process_peer(state->handle(), false, own, state->peer_handle, expected);
    return Stream(std::move(state));
}
Read Stream::read(char* buffer, std::size_t capacity, unsigned timeout) {
    if (!buffer || !capacity || capacity > max_io || !timeout || timeout > 5000) throw IpcError("io.limit");
    if (impl_->first_byte) {
        *buffer = *impl_->first_byte; impl_->first_byte.reset();
        return {1, false, false, impl_->first_observed};
    }
    const auto result = transfer(impl_->handle(), buffer, static_cast<DWORD>(capacity), false, monotonic_ms() + timeout);
    return {result.bytes, result.eof, result.timeout, monotonic_ms()};
}
void Stream::write(std::string_view bytes, unsigned timeout) {
    if (bytes.empty() || bytes.size() > max_io || !timeout || timeout > 5000) throw IpcError("io.limit");
    const auto deadline = monotonic_ms() + timeout;
    while (!bytes.empty()) {
        if (!remaining(deadline)) throw IpcError("io.timeout");
        const auto result = transfer(impl_->handle(), const_cast<char*>(bytes.data()), static_cast<DWORD>(bytes.size()), true, deadline);
        if (result.timeout) throw IpcError("io.timeout");
        if (!result.bytes) throw IpcError("io.write");
        bytes.remove_prefix(result.bytes);
    }
}
Listener::Listener(const std::string& endpoint) {
    const auto name = pipe_name(endpoint);
    impl_ = std::make_unique<Impl>(process_identity(::GetCurrentProcess()));
    const auto sddl = "D:P(A;;0x0012019b;;;" + impl_->own.logon + ")";
    PSECURITY_DESCRIPTOR raw = nullptr;
    if (!::ConvertStringSecurityDescriptorToSecurityDescriptorA(sddl.c_str(), SDDL_REVISION_1, &raw, nullptr)) throw IpcError("endpoint.acl");
    LocalMemory descriptor{raw};
    SECURITY_ATTRIBUTES attributes{sizeof(SECURITY_ATTRIBUTES), raw, FALSE};
    Handle pipe(::CreateNamedPipeW(name.c_str(), PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE | FILE_FLAG_OVERLAPPED,
        PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS, 1, 4096, 4096, 5000, &attributes));
    if (!pipe.valid()) throw IpcError("endpoint.collision");
    impl_->slot = std::make_shared<PipeSlot>(std::exchange(pipe.value, INVALID_HANDLE_VALUE));
    if (!access_controls_verified()) throw IpcError("endpoint.acl");
}
Listener::~Listener() = default;
Stream Listener::accept(std::uint64_t expected) {
    if (impl_->slot->busy) throw IpcError("endpoint.busy");
    const auto deadline = monotonic_ms() + 5000;
    const auto pipe = impl_->slot->pipe.value;
    Handle event(::CreateEventW(nullptr, TRUE, FALSE, nullptr));
    if (!event.valid()) throw IpcError("io.event");
    OVERLAPPED operation{}; operation.hEvent = event.value;
    if (!::ConnectNamedPipe(pipe, &operation)) {
        const auto error = ::GetLastError();
        if (error == ERROR_IO_PENDING) {
            if (::WaitForSingleObject(event.value, remaining(deadline)) != WAIT_OBJECT_0) {
                drain(pipe, operation); ::DisconnectNamedPipe(pipe); throw IpcError("io.timeout");
            }
            DWORD bytes = 0;
            if (!::GetOverlappedResult(pipe, &operation, &bytes, FALSE)) throw IpcError("io.accept");
        } else if (error != ERROR_PIPE_CONNECTED) throw IpcError("io.accept");
    }
    auto state = std::make_unique<Stream::Impl>();
    state->server = impl_->slot; impl_->slot->busy = true;
    state->connected = monotonic_ms();
    char first = 0;
    const auto received = transfer(pipe, &first, 1, false, deadline);
    if (received.timeout) throw IpcError("io.timeout");
    if (received.eof || received.bytes != 1) throw IpcError("peer.closed");
    state->first_byte = first; state->first_observed = monotonic_ms();
    identify_client_token(pipe, impl_->own);
    state->peer = process_peer(pipe, true, impl_->own, state->peer_handle, expected);
    return Stream(std::move(state));
}
bool Listener::access_controls_verified() const {
    PSECURITY_DESCRIPTOR raw = nullptr; PACL acl = nullptr;
    if (::GetSecurityInfo(impl_->slot->pipe.value, SE_KERNEL_OBJECT, DACL_SECURITY_INFORMATION, nullptr, nullptr, &acl, nullptr, &raw) != ERROR_SUCCESS)
        return false;
    LocalMemory descriptor{raw};
    SECURITY_DESCRIPTOR_CONTROL control = 0; DWORD revision = 0;
    if (!::GetSecurityDescriptorControl(raw, &control, &revision) || !(control & SE_DACL_PROTECTED) || !acl || acl->AceCount != 1) return false;
    void* raw_ace = nullptr;
    if (!::GetAce(acl, 0, &raw_ace)) return false;
    const auto* ace = static_cast<const ACCESS_ALLOWED_ACE*>(raw_ace);
    return ace->Header.AceType == ACCESS_ALLOWED_ACE_TYPE && ace->Header.AceFlags == 0 && ace->Mask == client_rights &&
        sid_string(const_cast<DWORD*>(&ace->SidStart)) == impl_->own.logon;
}
} // namespace syspane::platform
#endif
