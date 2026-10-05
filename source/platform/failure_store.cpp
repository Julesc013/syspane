#include "failure_store.hpp"
#include <array>
#include <filesystem>
#include <cstring>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <sddl.h>
#include <shellapi.h>
#else
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace syspane::platform {
namespace {
std::filesystem::path selected(const std::string& text) {
    if (text.empty() || text.size() > 4096 || text.find('\0') != std::string::npos) throw protocol::Error("failure.path");
    (void)protocol::Json(text).dump(); // Strict UTF-8 validation, without interpreting file contents.
    const auto path = std::filesystem::u8path(text);
    if (!path.is_absolute() || path.filename().empty()) throw protocol::Error("failure.path");
    for (const auto& part : path) if (part == "." || part == "..") throw protocol::Error("failure.path");
#ifdef _WIN32
    const auto value = path.native();
    if (value.size() > 240 || value.size() < 4 || value[1] != L':' ||
        !((value[0] >= L'A' && value[0] <= L'Z') || (value[0] >= L'a' && value[0] <= L'z')) ||
        value.find(L':', 2) != std::wstring::npos) throw protocol::Error("failure.path");
#endif
    return path;
}
#ifdef _WIN32
struct File {
    HANDLE value = INVALID_HANDLE_VALUE;
    ~File() { if (value != INVALID_HANDLE_VALUE) CloseHandle(value); }
    File() = default;
    File(const File&) = delete;
    File& operator=(const File&) = delete;
};
struct Local {
    void* value = nullptr;
    ~Local() { if (value) LocalFree(value); }
};
std::vector<unsigned char> user() {
    File token;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token.value)) throw protocol::Error("failure.identity");
    DWORD size = 0;
    GetTokenInformation(token.value, TokenUser, nullptr, 0, &size);
    if (!size || size > 65536) throw protocol::Error("failure.identity");
    std::vector<unsigned char> data(size);
    if (!GetTokenInformation(token.value, TokenUser, data.data(), size, &size)) throw protocol::Error("failure.identity");
    return data;
}
bool private_file(HANDLE file, BY_HANDLE_FILE_INFORMATION& info) {
    if (GetFileType(file) != FILE_TYPE_DISK || !GetFileInformationByHandle(file, &info) ||
        info.dwFileAttributes & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT) || info.nNumberOfLinks != 1 ||
        info.nFileSizeHigh || info.nFileSizeLow > 8192) return false;
    DWORD length = 0;
    constexpr auto fields = OWNER_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION;
    GetKernelObjectSecurity(file, fields, nullptr, 0, &length);
    if (!length || length > 65536) return false;
    std::vector<unsigned char> bytes(length);
    auto sd = reinterpret_cast<PSECURITY_DESCRIPTOR>(bytes.data());
    if (!GetKernelObjectSecurity(file, fields, sd, length, &length) || !IsValidSecurityDescriptor(sd)) return false;
    const auto identity = user();
    auto sid = reinterpret_cast<const TOKEN_USER*>(identity.data())->User.Sid;
    PSID owner = nullptr; PACL acl = nullptr; BOOL defaulted = FALSE, present = FALSE;
    if (!GetSecurityDescriptorOwner(sd, &owner, &defaulted) || !owner || !EqualSid(owner, sid) ||
        !GetSecurityDescriptorDacl(sd, &present, &acl, &defaulted) || !present || !acl || !IsValidAcl(acl)) return false;
    for (DWORD i = 0; i < acl->AceCount; ++i) {
        void* entry = nullptr;
        if (!GetAce(acl, i, &entry)) return false;
        const auto header = static_cast<ACE_HEADER*>(entry);
        if (header->AceFlags & INHERIT_ONLY_ACE || header->AceType == ACCESS_DENIED_ACE_TYPE) continue;
        if (header->AceType != ACCESS_ALLOWED_ACE_TYPE) return false;
        const auto ace = static_cast<ACCESS_ALLOWED_ACE*>(entry);
        if (ace->Mask && !EqualSid(&ace->SidStart, sid) && !IsWellKnownSid(&ace->SidStart, WinLocalSystemSid) &&
            !IsWellKnownSid(&ace->SidStart, WinBuiltinAdministratorsSid)) return false;
    }
    return true;
}
bool same(const BY_HANDLE_FILE_INFORMATION& a, const BY_HANDLE_FILE_INFORMATION& b) {
    return a.dwVolumeSerialNumber == b.dwVolumeSerialNumber && a.nFileIndexHigh == b.nFileIndexHigh && a.nFileIndexLow == b.nFileIndexLow &&
        a.nFileSizeHigh == b.nFileSizeHigh && a.nFileSizeLow == b.nFileSizeLow &&
        CompareFileTime(&a.ftLastWriteTime, &b.ftLastWriteTime) == 0;
}
bool put(File& file, std::string_view bytes) {
    DWORD written = 0;
    return WriteFile(file.value, bytes.data(), static_cast<DWORD>(bytes.size()), &written, nullptr) &&
        written == bytes.size() && FlushFileBuffers(file.value);
}
#else
struct File {
    int value = -1;
    ~File() { if (value >= 0) ::close(value); }
    File() = default;
    File(const File&) = delete;
    File& operator=(const File&) = delete;
};
bool private_file(int file, struct stat& info) {
    return file >= 0 && ::fstat(file, &info) == 0 && S_ISREG(info.st_mode) && info.st_uid == ::geteuid() &&
        !(info.st_mode & 0077) && info.st_nlink == 1 && info.st_size >= 0 && info.st_size <= 8192;
}
bool same(const struct stat& a, const struct stat& b) {
    return a.st_dev == b.st_dev && a.st_ino == b.st_ino && a.st_size == b.st_size &&
        a.st_mtim.tv_sec == b.st_mtim.tv_sec && a.st_mtim.tv_nsec == b.st_mtim.tv_nsec &&
        a.st_ctim.tv_sec == b.st_ctim.tv_sec && a.st_ctim.tv_nsec == b.st_ctim.tv_nsec;
}
bool put(File& file, std::string_view bytes) {
    unsigned retries = 0;
    while (!bytes.empty()) {
        const auto count = ::write(file.value, bytes.data(), bytes.size());
        if (count < 0 && errno == EINTR && ++retries <= 16) continue;
        if (count <= 0) return false;
        bytes.remove_prefix(static_cast<std::size_t>(count));
    }
    return ::fsync(file.value) == 0;
}
#endif
}
bool failure_path_valid(const std::string& text) {
    try { (void)selected(text); return true; } catch (const std::exception&) { return false; }
}
std::vector<std::string> native_arguments(int argc, char** argv) {
    std::vector<std::string> result;
#ifdef _WIN32
    (void)argv;
    Local storage;
    storage.value = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (!storage.value || argc > 16) throw protocol::Error("arguments.invalid");
    const auto values = static_cast<wchar_t**>(storage.value);
    for (int i = 0; i < argc; ++i) {
        const auto size = WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, values[i], -1, nullptr, 0, nullptr, nullptr);
        if (size <= 0 || size > 4097) throw protocol::Error("arguments.invalid");
        std::string text(static_cast<std::size_t>(size), '\0');
        if (!WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, values[i], -1, text.data(), size, nullptr, nullptr)) throw protocol::Error("arguments.invalid");
        text.pop_back(); result.push_back(std::move(text));
    }
#else
    if (argc > 16) throw protocol::Error("arguments.invalid");
    for (int i = 0; i < argc; ++i) {
        if (std::strlen(argv[i]) > 4096) throw protocol::Error("arguments.invalid");
        result.emplace_back(argv[i]);
    }
#endif
    return result;
}
diagnostics::FailureHistory read_failure_file(const std::string& text) {
    try {
        const auto path = selected(text);
        File file;
        std::array<char, 8193> bytes{};
        std::size_t count = 0;
#ifdef _WIN32
        file.value = CreateFileW(path.c_str(), GENERIC_READ | READ_CONTROL, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
            nullptr, OPEN_EXISTING, FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
        if (file.value == INVALID_HANDLE_VALUE) return {GetLastError() == ERROR_FILE_NOT_FOUND ? "absent" : "unavailable", {}};
        BY_HANDLE_FILE_INFORMATION before{}, after{};
        if (!private_file(file.value, before)) return {};
        DWORD read = 0;
        if (!ReadFile(file.value, bytes.data(), static_cast<DWORD>(bytes.size()), &read, nullptr)) return {};
        count = read;
        if (count != before.nFileSizeLow || !private_file(file.value, after) || !same(before, after)) return {};
#else
        file.value = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
        if (file.value < 0) return {errno == ENOENT ? "absent" : "unavailable", {}};
        struct stat before{}, after{};
        if (!private_file(file.value, before)) return {};
        unsigned retries = 0;
        while (count < bytes.size()) {
            const auto read = ::read(file.value, bytes.data()+count, bytes.size()-count);
            if (read < 0 && errno == EINTR && ++retries <= 16) continue;
            if (read < 0) return {};
            if (!read) break;
            count += static_cast<std::size_t>(read);
        }
        if (count != static_cast<std::size_t>(before.st_size) || !private_file(file.value, after) || !same(before, after)) return {};
#endif
        return diagnostics::decode_failures(std::string_view(bytes.data(), count));
    } catch (const std::exception&) { return {}; }
}
struct FailureWriter::Impl {
    File file;
    bool ready = false;
    std::uint64_t count = 0, last = 0;
    std::size_t size = 0;
};
FailureWriter::FailureWriter(const std::string& text) : impl_(std::make_unique<Impl>()) {
    try {
        const auto path = selected(text);
#ifdef _WIN32
        const auto identity = user();
        Local sid_text, sd;
        LPWSTR sid = nullptr;
        if (!ConvertSidToStringSidW(reinterpret_cast<const TOKEN_USER*>(identity.data())->User.Sid, &sid)) return;
        sid_text.value = sid;
        const std::wstring sddl = L"O:" + std::wstring(sid) + L"D:P(A;;FA;;;" + sid + L")";
        PSECURITY_DESCRIPTOR descriptor = nullptr;
        if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl.c_str(), SDDL_REVISION_1, &descriptor, nullptr)) return;
        sd.value = descriptor;
        SECURITY_ATTRIBUTES attributes{sizeof(SECURITY_ATTRIBUTES), descriptor, FALSE};
        impl_->file.value = CreateFileW(path.c_str(), GENERIC_WRITE | READ_CONTROL, FILE_SHARE_READ, &attributes, CREATE_NEW,
            FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
        BY_HANDLE_FILE_INFORMATION info{};
        if (impl_->file.value == INVALID_HANDLE_VALUE || !private_file(impl_->file.value, info)) return;
#else
        impl_->file.value = ::open(path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK, 0600);
        struct stat info{};
        if (!private_file(impl_->file.value, info)) return;
#endif
        const std::string_view header(diagnostics::failure_header);
        impl_->ready = put(impl_->file, header); impl_->size = header.size();
    } catch (const std::exception&) { impl_->ready = false; }
}
FailureWriter::~FailureWriter() = default;
bool FailureWriter::ready() const { return impl_->ready; }
bool FailureWriter::append(std::uint64_t elapsed, const std::string& role, const std::string& reason, bool stopped) {
    if (!impl_->ready) return false;
    impl_->ready = false; // Any validation/I/O failure latches until a new explicit writer.
    try {
        if (elapsed < impl_->last || impl_->count >= 16) return false;
        const auto line = diagnostics::failure_line(impl_->count+1, elapsed, role, reason, stopped);
        if (impl_->size+line.size() > 8192 || !put(impl_->file, line)) return false;
        ++impl_->count; impl_->last = elapsed; impl_->size += line.size(); impl_->ready = true;
        return true;
    } catch (const std::exception&) { return false; }
}
}
