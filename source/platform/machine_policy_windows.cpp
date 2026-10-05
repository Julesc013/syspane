#ifdef _WIN32
#include "machine_policy.hpp"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <array>
#include <vector>

namespace syspane::platform {
namespace {
struct Key {
    HKEY value = nullptr;
    ~Key() { if (value) RegCloseKey(value); }
    Key() = default;
    Key(const Key&) = delete;
    Key& operator=(const Key&) = delete;
};
bool trusted(PSID sid) {
    return sid && IsValidSid(sid) && (IsWellKnownSid(sid, WinLocalSystemSid) || IsWellKnownSid(sid, WinBuiltinAdministratorsSid));
}
bool protected_key(HKEY key) {
    DWORD link_type = 0, link_size = 0;
    const auto link = RegQueryValueExW(key, L"SymbolicLinkValue", nullptr, &link_type, nullptr, &link_size);
    if (link != ERROR_FILE_NOT_FOUND) return false; // Includes registry links and unsupported lookalikes.
    DWORD count = 0;
    constexpr auto fields = OWNER_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION;
    if (RegGetKeySecurity(key, fields, nullptr, &count) != ERROR_INSUFFICIENT_BUFFER || count == 0 || count > 65536) return false;
    std::vector<unsigned char> bytes(count);
    auto sd = reinterpret_cast<PSECURITY_DESCRIPTOR>(bytes.data());
    if (RegGetKeySecurity(key, fields, sd, &count) != ERROR_SUCCESS || !IsValidSecurityDescriptor(sd)) return false;
    PSID owner = nullptr;
    BOOL defaulted = FALSE, present = FALSE;
    PACL acl = nullptr;
    if (!GetSecurityDescriptorOwner(sd, &owner, &defaulted) || !trusted(owner) ||
        !GetSecurityDescriptorDacl(sd, &present, &acl, &defaulted) || !present || !acl || !IsValidAcl(acl)) return false;
    constexpr DWORD mutation = KEY_SET_VALUE | KEY_CREATE_SUB_KEY | KEY_CREATE_LINK | DELETE | WRITE_DAC | WRITE_OWNER | GENERIC_WRITE | GENERIC_ALL | MAXIMUM_ALLOWED;
    for (DWORD i = 0; i < acl->AceCount; ++i) {
        void* entry = nullptr;
        if (!GetAce(acl, i, &entry)) return false;
        const auto header = static_cast<ACE_HEADER*>(entry);
        if (header->AceFlags & INHERIT_ONLY_ACE) continue;
        if (header->AceType == ACCESS_DENIED_ACE_TYPE) continue;
        if (header->AceType != ACCESS_ALLOWED_ACE_TYPE) return false;
        const auto ace = static_cast<ACCESS_ALLOWED_ACE*>(entry);
        if ((ace->Mask & mutation) && !trusted(&ace->SidStart)) return false;
    }
    return true;
}
bool open(Key& key, HKEY parent, const wchar_t* part) {
    return RegOpenKeyExW(parent, part, REG_OPTION_OPEN_LINK, KEY_READ | KEY_WOW64_64KEY, &key.value) == ERROR_SUCCESS && protected_key(key.value);
}
}
configuration::Policy machine_policy() {
    try {
        // HKLM itself is checked as an ancestor; pseudo handle is not closed.
        if (!protected_key(HKEY_LOCAL_MACHINE)) return {};
        Key software, policies, syspane;
        if (!open(software, HKEY_LOCAL_MACHINE, L"SOFTWARE") || !open(policies, software.value, L"Policies") || !open(syspane, policies.value, L"SysPane")) return {};
        std::array<char, 65536> bytes{};
        DWORD size = static_cast<DWORD>(bytes.size()), type = 0;
        if (RegQueryValueExW(syspane.value, L"PolicyJson", nullptr, &type, reinterpret_cast<BYTE*>(bytes.data()), &size) != ERROR_SUCCESS ||
            type != REG_BINARY || size == 0 || !protected_key(HKEY_LOCAL_MACHINE) || !protected_key(software.value) ||
            !protected_key(policies.value) || !protected_key(syspane.value)) return {};
        auto policy = configuration::decode_policy(std::string_view(bytes.data(), size));
        policy.available = true;
        return policy;
    } catch (const std::exception&) { return {}; }
}
}
#endif
