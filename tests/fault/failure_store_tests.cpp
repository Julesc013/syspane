#include "failure_store.hpp"
#include <iostream>

namespace p = syspane::platform;
int main(int argc, char** argv) {
    try {
        const auto args = p::native_arguments(argc, argv);
        if (args.size() != 3) return 64;
        if (args[1] == "read") {
            std::cout << syspane::diagnostics::failure_projection(p::read_failure_file(args[2])).dump() << '\n';
            return 0;
        }
        p::FailureWriter writer(args[2]);
        if (!writer.ready()) return 73;
        if (args[1] == "create") {
            if (!writer.append(100, "collector", "producer_expired", false) || !writer.append(200, "desktop", "render_stalled", true)) return 70;
        } else if (args[1] == "limit") {
            for (unsigned i = 0; i < 16; ++i) if (!writer.append(i, "desktop", "crashed", true)) return 70;
            if (writer.append(17, "desktop", "crashed", true) || writer.ready()) return 70;
        } else if (args[1] == "regression") {
            if (!writer.append(100, "collector", "operation_timeout", false) || writer.append(99, "collector", "crashed", false) ||
                writer.ready() || writer.append(101, "collector", "crashed", false)) return 70;
        } else if (args[1] == "live-read") {
            if (!writer.append(100, "desktop", "crashed", true)) return 70;
            const auto current = p::read_failure_file(args[2]);
            if (current.status != "complete" || current.records.size() != 1) return 70;
        } else return 64;
        return 0;
    } catch (const std::exception&) { return 70; }
}
