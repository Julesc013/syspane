#pragma once
#include <cstddef>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>

namespace syspane::platform {
class IpcError : public std::runtime_error {
public:
    explicit IpcError(const char* code) : std::runtime_error(code) {}
};
std::uint64_t monotonic_ms();
bool unprivileged_context();
struct Peer {
    std::string principal; // Native user/session identity; never log the raw key.
    std::uint64_t process_id;
};
struct Read {
    std::size_t bytes;
    bool eof, timeout;
    std::uint64_t observed_ms;
};
class Listener;
class Stream {
public:
    ~Stream();
    Stream(Stream&&) noexcept;
    Stream& operator=(Stream&&) noexcept;
    Stream(const Stream&) = delete;
    Stream& operator=(const Stream&) = delete;
    static Stream connect(const std::string& endpoint, std::uint64_t expected_process = 0);
    Read read(char* buffer, std::size_t capacity, unsigned wait_ms = 100);
    void write(std::string_view bytes, unsigned wait_ms = 5000);
    const Peer& peer() const;
    std::uint64_t connected_ms() const;
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
    explicit Stream(std::unique_ptr<Impl> impl);
    friend class Listener;
};
class Listener {
public:
    explicit Listener(const std::string& endpoint);
    ~Listener();
    Listener(const Listener&) = delete;
    Listener& operator=(const Listener&) = delete;
    Stream accept(std::uint64_t expected_process = 0);
    bool access_controls_verified() const;
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};
} // namespace syspane::platform
