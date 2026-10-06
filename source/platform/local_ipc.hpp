#pragma once
#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
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
struct MeasurementClock {
    const char* clock_id;
    std::uint64_t nanoseconds;
    std::uint32_t representation_unit_ns; // Not hardware resolution or accuracy.
    std::string local_scope; // In-memory consumer provenance; never a wire field.
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
#if defined(__linux__)
    // Borrow a caller-authorized, connected nonblocking AF_UNIX stream. Duplicate
    // it and authenticate the native peer; never alter or close the input FD.
    static Stream from_connected_socket(int fd, std::uint64_t expected_process);
#endif
    Read read(char* buffer, std::size_t capacity, unsigned wait_ms = 100);
    void write(std::string_view bytes, unsigned wait_ms = 5000);
    const Peer& peer() const;
    std::uint64_t connected_ms() const;
    // Serialized owner only. Native provenance is checked per call; any failure
    // permanently disables this stream's measurement facility, not inventory I/O.
    MeasurementClock measurement_clock();
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
#if defined(__linux__)
    // One nonblocking admission attempt; authenticate exactly as accept().
    // Empty on no connection or interrupted attempt; caller owns its deadline.
    std::optional<Stream> accept_ready(std::uint64_t expected_process);
#endif
    bool access_controls_verified() const;
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};
} // namespace syspane::platform
