#pragma once
#include <cstddef>
#include <deque>
#include <optional>
#include <string>

namespace syspane::protocol {
// Payloads are already encoded and policy-filtered. Budgets include frame prefixes.
class Outbox {
public:
    bool can_control(std::size_t payload_bytes) const;
    static constexpr std::size_t reply_capacity=5120;
    bool reserve_reply();
    void release_reply();
    bool control(std::string payload);
    bool data(std::string payload, std::string encoded_gap);
    void revoke(std::string encoded_gap);
    void discard_data();
    std::optional<std::string> pop();
    void close();
    bool closed() const { return closed_; }
    std::size_t data_size() const { return data_.size(); }
private:
    std::deque<std::string> control_, data_;
    std::size_t control_bytes_ = 0, data_bytes_ = 0;
    std::size_t reserved_ = 0;
    bool closed_ = false;
};
} // namespace syspane::protocol
