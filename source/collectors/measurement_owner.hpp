#pragma once
#include "state.hpp"
#include <functional>
#include <mutex>
#include <stdexcept>
#include <utility>

namespace syspane::collectors {
// One native facility per connection. Worker callables share this owner; callers
// keep the provider alive through every invocation. No clock/policy semantics
// are implemented here, and blocked native work still needs a process guardian.
class MeasurementOwner {
public:
    explicit MeasurementOwner(std::function<model::Tick()> read):read_(std::move(read)) {
        if (!read_) throw std::invalid_argument("measurement.reader");
    }
    model::Tick operator()() const {
        const std::lock_guard<std::mutex> guard(mutex_);
        return read_();
    }
private:
    std::function<model::Tick()> read_;
    mutable std::mutex mutex_;
};
}
