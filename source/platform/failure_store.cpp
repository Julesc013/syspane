#include "failure_store.hpp"
#include "preservation.hpp"
#include <algorithm>
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
#include <sys/syscall.h>
#include <linux/fs.h>
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
bool private_file(HANDLE file, BY_HANDLE_FILE_INFORMATION& info, std::size_t limit = 8192, bool allow_readers = false) {
    if (GetFileType(file) != FILE_TYPE_DISK || !GetFileInformationByHandle(file, &info) ||
        info.dwFileAttributes & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT) || info.nNumberOfLinks != 1 ||
        info.nFileSizeHigh || info.nFileSizeLow > limit) return false;
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
        constexpr DWORD mutation = FILE_WRITE_DATA | FILE_APPEND_DATA | FILE_WRITE_EA | FILE_WRITE_ATTRIBUTES |
            DELETE | WRITE_DAC | WRITE_OWNER | GENERIC_WRITE | GENERIC_ALL | MAXIMUM_ALLOWED;
        if ((allow_readers ? (ace->Mask & mutation) : ace->Mask) && !EqualSid(&ace->SidStart, sid) && !IsWellKnownSid(&ace->SidStart, WinLocalSystemSid) &&
            !(allow_readers && IsWellKnownSid(&ace->SidStart, WinCreatorOwnerRightsSid)) &&
            !IsWellKnownSid(&ace->SidStart, WinBuiltinAdministratorsSid)) return false;
    }
    return true;
}
bool same(const BY_HANDLE_FILE_INFORMATION& a, const BY_HANDLE_FILE_INFORMATION& b) {
    return a.dwVolumeSerialNumber == b.dwVolumeSerialNumber && a.nFileIndexHigh == b.nFileIndexHigh && a.nFileIndexLow == b.nFileIndexLow &&
        a.nFileSizeHigh == b.nFileSizeHigh && a.nFileSizeLow == b.nFileSizeLow &&
        CompareFileTime(&a.ftLastWriteTime, &b.ftLastWriteTime) == 0;
}
bool write_bytes(File& file, std::string_view bytes) {
    DWORD written = 0;
    return WriteFile(file.value, bytes.data(), static_cast<DWORD>(bytes.size()), &written, nullptr) &&
        written == bytes.size();
}
bool flush(File& file) { return FlushFileBuffers(file.value) != FALSE; }
bool create_private(File& file, const std::filesystem::path& path, bool copy) {
    const auto identity = user();
    Local sid_text, sd;
    LPWSTR sid = nullptr;
    if (!ConvertSidToStringSidW(reinterpret_cast<const TOKEN_USER*>(identity.data())->User.Sid, &sid)) return false;
    sid_text.value = sid;
    const std::wstring sddl = L"O:" + std::wstring(sid) + L"D:P(A;;FA;;;" + sid + L")";
    PSECURITY_DESCRIPTOR descriptor = nullptr;
    if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl.c_str(), SDDL_REVISION_1, &descriptor, nullptr)) return false;
    sd.value = descriptor;
    SECURITY_ATTRIBUTES attributes{sizeof(SECURITY_ATTRIBUTES), descriptor, FALSE};
    file.value = CreateFileW(path.c_str(), GENERIC_WRITE | READ_CONTROL | (copy ? GENERIC_READ | DELETE : 0), FILE_SHARE_READ,
        &attributes, CREATE_NEW, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
    return file.value != INVALID_HANDLE_VALUE;
}
#else
struct File {
    int value = -1;
    ~File() { if (value >= 0) ::close(value); }
    File() = default;
    File(const File&) = delete;
    File& operator=(const File&) = delete;
};
bool private_file(int file, struct stat& info, std::size_t limit = 8192, bool allow_readers = false) {
    return file >= 0 && ::fstat(file, &info) == 0 && S_ISREG(info.st_mode) && info.st_uid == ::geteuid() &&
        !(info.st_mode & (allow_readers ? 0022 : 0077)) && info.st_nlink == 1 && info.st_size >= 0 &&
        static_cast<std::uint64_t>(info.st_size) <= limit;
}
bool same(const struct stat& a, const struct stat& b) {
    return a.st_dev == b.st_dev && a.st_ino == b.st_ino && a.st_size == b.st_size &&
        a.st_mtim.tv_sec == b.st_mtim.tv_sec && a.st_mtim.tv_nsec == b.st_mtim.tv_nsec &&
        a.st_ctim.tv_sec == b.st_ctim.tv_sec && a.st_ctim.tv_nsec == b.st_ctim.tv_nsec;
}
bool write_bytes(File& file, std::string_view bytes) {
    unsigned retries = 0;
    while (!bytes.empty()) {
        const auto count = ::write(file.value, bytes.data(), bytes.size());
        if (count < 0 && errno == EINTR && ++retries <= 16) continue;
        if (count <= 0) return false;
        bytes.remove_prefix(static_cast<std::size_t>(count));
    }
    return true;
}
bool flush(File& file) { return ::fsync(file.value) == 0; }
bool create_private(File& file, const std::filesystem::path& path, bool copy) {
    file.value = ::open(path.c_str(), (copy ? O_RDWR : O_WRONLY) | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK, 0600);
    return file.value >= 0;
}
#endif
bool put(File& file, std::string_view bytes) { return write_bytes(file, bytes) && flush(file); }
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
        if (!create_private(impl_->file, path, false)) return;
#ifdef _WIN32
        BY_HANDLE_FILE_INFORMATION info{};
        if (!private_file(impl_->file.value, info)) return;
#else
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
namespace {
constexpr std::size_t preserve_limit = 8 * 1024 * 1024, transfer_limit = 64 * 1024;
struct SecretBytes {
    std::vector<char> data;
    explicit SecretBytes(std::size_t size) : data(size) {}
    ~SecretBytes() {
        volatile char* bytes = data.data();
        for (std::size_t i = 0; i < data.size(); ++i) bytes[i] = 0;
    }
};
bool rewind_file(File& file) {
#ifdef _WIN32
    LARGE_INTEGER zero{};
    return SetFilePointerEx(file.value, zero, nullptr, FILE_BEGIN) != FALSE;
#else
    return ::lseek(file.value, 0, SEEK_SET) == 0;
#endif
}
// One bounded transfer. Short reads are legal; callers check total length and EOF.
bool read_bytes(File& file, char* bytes, std::size_t size, std::size_t& count) {
#ifdef _WIN32
    DWORD read = 0;
    if (!ReadFile(file.value, bytes, static_cast<DWORD>(size), &read, nullptr)) return false;
    count = read;
#else
    unsigned retries = 0;
    ssize_t read;
    do { read = ::read(file.value, bytes, size); } while (read < 0 && errno == EINTR && ++retries <= 16);
    if (read < 0) return false;
    count = static_cast<std::size_t>(read);
#endif
    return true;
}
bool exists_leaf(const std::filesystem::path& path) {
    std::error_code error;
    const auto status = std::filesystem::symlink_status(path, error);
    if (error && error != std::errc::no_such_file_or_directory) throw protocol::Error("preserve.path");
    return status.type() != std::filesystem::file_type::not_found;
}
}
PreserveResult preserve_file(const std::string& input, const std::string& output, const PreserveGuard& guard) {
    PreserveResult result;
    auto allowed = [&](PreservePhase phase) {
        PreserveCheck check = PreserveCheck::deny;
        try { if (guard) check = guard(phase); } catch (...) {}
        if (check == PreserveCheck::permit) return true;
        result.outcome = check == PreserveCheck::cancel ? "cancelled" : "denied";
        return false;
    };
    if (!allowed(PreservePhase::before_read)) return result;
    std::filesystem::path source, destination, partial;
    try { source = selected(input); destination = selected(output); partial = selected(output + ".partial"); }
    catch (const std::exception&) { result.outcome = "invalid_path"; return result; }
    try {
        if (exists_leaf(destination) || exists_leaf(partial)) { result.outcome = "conflict"; return result; }
        File original, staging;
#ifdef _WIN32
        original.value = CreateFileW(source.c_str(), GENERIC_READ | READ_CONTROL, FILE_SHARE_READ, nullptr, OPEN_EXISTING,
            FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
        BY_HANDLE_FILE_INFORMATION initial{}, current{};
        if (original.value == INVALID_HANDLE_VALUE || !private_file(original.value, initial, preserve_limit, true)) {
            result.outcome = "source_unavailable"; return result;
        }
        const std::size_t size = initial.nFileSizeLow;
#else
        original.value = ::open(source.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
        struct stat initial{}, current{};
        if (!private_file(original.value, initial, preserve_limit, true)) { result.outcome = "source_unavailable"; return result; }
        const auto size = static_cast<std::size_t>(initial.st_size);
#endif
        SecretBytes content(size + 1), scratch(transfer_limit);
        std::size_t offset = 0;
        while (offset < content.data.size()) {
            if (!allowed(PreservePhase::reading)) return result;
            std::size_t count = 0;
            if (!read_bytes(original, content.data.data() + offset, std::min(transfer_limit, content.data.size() - offset), count)) return result;
            if (!count) break;
            offset += count;
        }
        if (offset != size || !private_file(original.value, current, preserve_limit, true) || !same(initial, current)) {
            result.outcome = "source_changed"; return result;
        }
        if (!allowed(PreservePhase::after_read) || !allowed(PreservePhase::before_create)) return result;
        if (!create_private(staging, partial, true)) {
            if (exists_leaf(partial)) result.outcome = "conflict";
            return result;
        }
        result.partial = true;
        if (!private_file(staging.value, current, preserve_limit)) return result;
        for (offset = 0; offset < size;) {
            if (!allowed(PreservePhase::writing)) return result;
            const auto count = std::min(transfer_limit, size - offset);
            if (!write_bytes(staging, std::string_view(content.data.data() + offset, count))) return result;
            offset += count;
        }
        if (!allowed(PreservePhase::verifying) || !flush(staging)) return result;
        auto matches = [&](File& file) {
            if (!rewind_file(file)) return false;
            std::size_t position = 0;
            for (;;) {
                if (!allowed(PreservePhase::verifying)) return false;
                std::size_t count = 0;
                if (!read_bytes(file, scratch.data.data(), scratch.data.size(), count)) return false;
                if (!count) return position == size;
                if (count > size - position || std::memcmp(content.data.data() + position, scratch.data.data(), count)) return false;
                position += count;
            }
        };
        if (!matches(staging) || !private_file(staging.value, current, preserve_limit)) return result;
        if (!matches(original) || !private_file(original.value, current, preserve_limit, true) || !same(initial, current)) {
            if (result.outcome == "io_error") result.outcome = "source_changed";
            return result;
        }
        if (!allowed(PreservePhase::before_publish)) return result;
#ifdef _WIN32
        const auto& name = destination.native();
        // Win32's path conversion also consumes a NUL-terminated string. Keep that
        // terminator inside the supplied buffer even though FileNameLength excludes it.
        const auto length = offsetof(FILE_RENAME_INFO, FileName) + (name.size() + 1) * sizeof(wchar_t);
        std::vector<std::uint64_t> storage((length + sizeof(std::uint64_t) - 1) / sizeof(std::uint64_t));
        const auto rename = reinterpret_cast<FILE_RENAME_INFO*>(storage.data());
        rename->ReplaceIfExists = FALSE;
        rename->RootDirectory = nullptr;
        rename->FileNameLength = static_cast<DWORD>(name.size() * sizeof(wchar_t));
        std::memcpy(rename->FileName, name.data(), rename->FileNameLength);
        const bool published = SetFileInformationByHandle(staging.value, FileRenameInfo, rename, static_cast<DWORD>(length)) != FALSE;
#else
        const bool published = ::syscall(SYS_renameat2, AT_FDCWD, partial.c_str(), AT_FDCWD, destination.c_str(), RENAME_NOREPLACE) == 0;
#endif
        if (!published) {
            if (exists_leaf(destination)) result.outcome = "conflict";
            return result;
        }
        result.outcome = "preserved";
        result.partial = false;
        return result;
    } catch (const std::exception&) { return result; }
}
}
