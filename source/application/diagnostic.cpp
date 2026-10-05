#include "entry.hpp"
#include "machine_policy.hpp"
#include "diagnostic_inspector.hpp"
#include "failure_store.hpp"
#include <iostream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

int main(int argc, char** argv) {
#ifdef _WIN32
    if (_setmode(_fileno(stdout), _O_BINARY) < 0 || _setmode(_fileno(stderr), _O_BINARY) < 0) return 70;
#endif
    try {
        std::vector<std::string> arguments;
        try { arguments = syspane::platform::native_arguments(argc, argv); }
        catch (const syspane::protocol::Error&) { std::cerr << "diagnostic.arguments\n"; return 64; }
        const std::string mode = arguments.size() == 1 ? "--inspect" : arguments[1];
        const bool selected = arguments.size() == 4 && arguments[2] == "--failures" && mode != "--help" &&
            syspane::platform::failure_path_valid(arguments[3]);
        if ((arguments.size() > 2 && !selected) || (mode != "--inspect" && mode != "--inspect-hidden" && mode != "--report" && mode != "--help")) {
            std::cerr << "diagnostic.arguments\n"; return 64;
        }
        if (mode == "--help") { std::cout << "SysPane diagnostic: --inspect | --report | --help; optional --failures <absolute-path>\n"; return 0; }
        syspane::diagnostics::FailureReader failures;
        if (selected) failures = [&] { return syspane::platform::read_failure_file(arguments[3]); };
        if (mode == "--report") {
            const auto report = syspane::diagnostics::report(syspane::platform::machine_policy(), SYSPANE_PROFILE_ID, failures);
            if (!report) { std::cerr << "diagnostic.denied\n"; return 77; }
            std::cout << report->dump() << '\n';
            return std::cout ? 0 : 70;
        }
        const auto result = syspane::interfaces::diagnostic_inspector([&] {
            return syspane::diagnostics::inspector_text(syspane::platform::machine_policy(), SYSPANE_PROFILE_ID, failures);
        }, mode == "--inspect-hidden");
        if (result) std::cerr << (result == 69 ? "diagnostic.ui_unavailable\n" : "diagnostic.internal\n");
        return result;
    } catch (const std::exception&) { std::cerr << "diagnostic.internal\n"; return 70; }
}
