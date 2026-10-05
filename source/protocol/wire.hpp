#pragma once
#include <nlohmann/json.hpp>
#include <array>
#include <cstdint>
#include <functional>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace syspane::protocol {
using Json = nlohmann::json;
constexpr std::size_t frame_limit = 1048576;
constexpr std::uint64_t deadline_ms = 5000;
class Error : public std::runtime_error {
public:
    explicit Error(const char* code) : std::runtime_error(code) {}
};
bool identifier(std::string_view value);
std::optional<std::uint64_t> decimal(std::string_view value);
bool members(const Json& value, std::initializer_list<const char*> names);
Json parse(std::string_view bytes);
std::string frame(std::string_view payload, std::size_t limit = frame_limit);

// One owner, one monotonic clock domain. Callback must consume/copy synchronously.
class Framer {
public:
    explicit Framer(std::size_t limit = frame_limit);
    void feed(std::string_view bytes, std::uint64_t now_ms,
              const std::function<void(std::string_view)>& consume);
    void tick(std::uint64_t now_ms);
    void restrict_limit(std::size_t limit);
    void eof();
    std::size_t buffered() const { return prefix_size_ + payload_.size(); }
private:
    [[noreturn]] void fail(const char* code);
    std::size_t limit_, prefix_size_ = 0, expected_ = 0;
    std::array<unsigned char, 4> prefix_{};
    std::string payload_;
    std::optional<std::uint64_t> started_, last_;
    bool closed_ = false;
};

struct Message {
    std::string type, connection_id, producer_epoch, body_bytes;
    Json body;
};
Message decode(std::string_view payload);
struct Handshake {
    unsigned minor = 1;
    std::size_t max_frame_bytes = frame_limit;
    std::string role, epoch;
    std::set<std::pair<std::string, std::string>> documents;
    std::set<std::string> required, optional;
};
Handshake handshake(const Json& body);
struct Negotiated {
    unsigned minor;
    std::size_t max_frame_bytes;
    std::set<std::pair<std::string, std::string>> documents;
    std::set<std::string> features;
};
Negotiated negotiate(const Handshake& server, const Handshake& client,
                     const std::set<std::string>& native_role_grants);
} // namespace syspane::protocol
