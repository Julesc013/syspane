#include "outbox.hpp"
#include "wire.hpp"

namespace syspane::protocol {
bool Outbox::can_control(std::size_t size) const {
    return !closed_ && size > 0 && size <= frame_limit && control_.size()+reserved_ < 16 &&
        size + 4 <= 65536 - control_bytes_ - reserved_*(reply_capacity+4);
}
bool Outbox::reserve_reply(){if(reserved_>=8||!can_control(reply_capacity))return false;++reserved_;return true;}
void Outbox::release_reply(){if(!reserved_)throw Error("queue.reservation");--reserved_;}
void Outbox::close() {
    closed_ = true;
    control_.clear(); data_.clear();
    control_bytes_ = data_bytes_ = reserved_ = 0;
}
bool Outbox::control(std::string payload) {
    if (!can_control(payload.size())) { close(); return false; }
    control_bytes_ += payload.size() + 4;
    control_.push_back(std::move(payload));
    return true;
}
bool Outbox::data(std::string payload, std::string gap) {
    if (closed_) return false;
    if (payload.empty() || payload.size() > frame_limit) { close(); return false; }
    if (data_.size() >= 16 || payload.size() + 4 > 2097152 - data_bytes_) {
        revoke(std::move(gap));
        return false;
    }
    data_bytes_ += payload.size() + 4;
    data_.push_back(std::move(payload));
    return true;
}
void Outbox::revoke(std::string gap) {
    discard_data();
    control(std::move(gap));
}
void Outbox::discard_data() { data_.clear(); data_bytes_ = 0; }
std::optional<std::string> Outbox::pop() {
    auto& queue = control_.empty() ? data_ : control_;
    auto& bytes = control_.empty() ? data_bytes_ : control_bytes_;
    if (queue.empty()) return {};
    auto result = std::move(queue.front());
    queue.pop_front(); bytes -= result.size() + 4;
    return result;
}
} // namespace syspane::protocol
