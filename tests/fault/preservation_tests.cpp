#include "preservation_job.hpp"
#include "diagnostic_inspector.hpp"
#include "failure_store.hpp"
#include <atomic>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <gtk/gtk.h>
#endif

namespace p = syspane::platform;
namespace d = syspane::diagnostics;
using namespace std::chrono_literals;
void require(bool value) { if (!value) throw std::runtime_error("fixed preservation oracle failed"); }
struct Shared {
    std::atomic<bool> release{false}, entered{false}, available{true};
    std::atomic<unsigned> starts{0};
};
struct UiTest {
    std::string mode, source, destination;
    std::shared_ptr<Shared> shared;
    unsigned stage = 0;
    bool failed = false, finished = false;
    std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
#ifdef _WIN32
    HWND window = nullptr;
    static BOOL CALLBACK locate(HWND window, LPARAM data) {
        auto& test = *reinterpret_cast<UiTest*>(data);
        DWORD pid = 0; GetWindowThreadProcessId(window, &pid);
        wchar_t name[128]{}; GetClassNameW(window, name, 128);
        if (pid == GetCurrentProcessId() && std::wstring(name) == L"SysPane.Diagnostic.Window") test.window = window;
        return TRUE;
    }
    HWND control(int id) { return GetDlgItem(window, id); }
    void set(int id, const std::string& text) {
        const auto wide = std::filesystem::u8path(text).native();
        DWORD_PTR result = 0;
        require(SendMessageTimeoutW(control(id), WM_SETTEXT, 0, reinterpret_cast<LPARAM>(wide.c_str()), SMTO_ABORTIFHUNG, 1000, &result) && result);
    }
    std::string text(int id) {
        wchar_t value[1024]{}; DWORD_PTR count = 0;
        require(SendMessageTimeoutW(control(id), WM_GETTEXT, 1024, reinterpret_cast<LPARAM>(value), SMTO_ABORTIFHUNG, 1000, &count));
        return std::string(value, value + count); // Status literals and empty-path checks only.
    }
    bool enabled(int id) { return IsWindowEnabled(control(id)) != FALSE; }
    void click(int id) {
        DWORD_PTR result = 0;
        require(SendMessageTimeoutW(control(id), BM_CLICK, 0, 0, SMTO_ABORTIFHUNG, 1000, &result));
    }
    void close() { require(PostMessageW(window, WM_CLOSE, 0, 0) != FALSE); }
    bool find() { EnumWindows(locate, reinterpret_cast<LPARAM>(this)); return window && control(105); }
#else
    GtkWidget* window = nullptr;
    std::map<int, GtkWidget*> widgets;
    void visit(GtkWidget* widget) {
        const std::map<std::string, int> ids{{"preserve-source",101},{"preserve-destination",102},{"preserve-start",103},{"preserve-cancel",104},{"preserve-status",105}};
        const auto it = ids.find(gtk_widget_get_name(widget));
        if (it != ids.end()) widgets[it->second] = widget;
        if (GTK_IS_CONTAINER(widget)) {
            auto children = gtk_container_get_children(GTK_CONTAINER(widget));
            for (auto item = children; item; item = item->next) visit(GTK_WIDGET(item->data));
            g_list_free(children);
        }
    }
    bool find() {
        auto windows = gtk_window_list_toplevels();
        for (auto item = windows; item; item = item->next) {
            const auto title = gtk_window_get_title(GTK_WINDOW(item->data));
            if (title && std::string(title) == "SysPane Diagnostic") window = GTK_WIDGET(item->data);
        }
        g_list_free(windows);
        if (window) visit(window);
        return widgets.size() == 5;
    }
    void set(int id, const std::string& value) { gtk_entry_set_text(GTK_ENTRY(widgets.at(id)), value.c_str()); }
    std::string text(int id) { return id == 105 ? gtk_label_get_text(GTK_LABEL(widgets.at(id))) : gtk_entry_get_text(GTK_ENTRY(widgets.at(id))); }
    bool enabled(int id) { return gtk_widget_get_sensitive(widgets.at(id)); }
    void click(int id) { gtk_button_clicked(GTK_BUTTON(widgets.at(id))); }
    void close() { gtk_widget_destroy(window); }
#endif
    void tick() {
        try {
            require(std::chrono::steady_clock::now() - start < 12s);
            if (!find()) return;
            if (stage == 0) {
                require(enabled(101) && enabled(103));
                set(101, source); set(102, destination); click(103); ++stage;
            } else if (stage == 1 && shared->entered.load()) {
                require(!enabled(101) && !enabled(102) && !enabled(103) && enabled(104));
                click(103); require(shared->starts.load() == 1);
                if (mode == "ui-close") { close(); finished = true; return; }
                if (mode == "ui-revoke") shared->available.store(false);
                else { if (mode == "ui-cancel") click(104); shared->release.store(true); }
                ++stage;
            } else if (stage == 2) {
                if (mode == "ui-revoke") {
                    if (enabled(101) || !text(101).empty() || !text(102).empty()) return;
                    require(text(105) == "Configuration preservation is restricted by policy.");
                    shared->release.store(true);
                    close(); finished = true;
                } else if (text(105).find(mode == "ui-cancel" ? "Copy outcome: cancelled." : "Private copy preserved.") == 0) {
                    require(enabled(101) && enabled(103) && !enabled(104));
                    close(); finished = true;
                }
            }
        } catch (...) { failed = true; shared->release.store(true); if (window) close(); finished = true; }
    }
};
int ui(const std::string& mode, const std::string& source, const std::string& destination) {
    auto shared = std::make_shared<Shared>();
    const auto owner = std::this_thread::get_id();
    d::PreservationJob job([shared, owner] {
        if (std::this_thread::get_id() != owner) {
            shared->entered.store(true);
            while (!shared->release.load()) std::this_thread::sleep_for(10ms); // Bounded externally by parent test, never shipped in product.
        }
        syspane::configuration::Policy policy;
        policy.available = shared->available.load(); policy.revision = 9;
        policy.disclosure[{"diagnostic", "inspector"}] = {"public", "operational"};
        policy.disclosure[{"diagnostic", "accessibility"}] = {"public", "operational"};
        return policy;
    });
    syspane::interfaces::PreservationControls controls{[&] { return job.permitted(); }, [&] { return job.busy(); },
        [&](std::string a, std::string b) { ++shared->starts; return job.start(std::move(a), std::move(b)); },
        [&] { job.cancel(); }, [&] { return job.status(); }};
    UiTest test{}; test.mode = mode; test.source = source; test.destination = destination; test.shared = shared;
#ifdef _WIN32
    std::thread observer([&] { while (!test.finished) { test.tick(); std::this_thread::sleep_for(20ms); } });
#else
    const auto timer = g_timeout_add(20, [](gpointer data) -> gboolean {
        auto& test = *static_cast<UiTest*>(data); test.tick(); return !test.finished;
    }, &test);
#endif
    const auto result = syspane::interfaces::diagnostic_inspector([] { return "Typed policy fixture; native control binding only."; }, true, controls);
#ifdef _WIN32
    observer.join();
#else
    if (g_main_context_find_source_by_id(nullptr, timer)) g_source_remove(timer);
#endif
    require(!result && test.finished && !test.failed && test.stage >= 1);
    std::cout << "ui: pass\n";
    return 0; // Job destruction cancels without joining a blocked worker; process ends here.
}
int main(int argc, char** argv) {
    try {
        const auto args = p::native_arguments(argc, argv);
        if (args.size() != 4) return 64;
        if (args[1].find("ui-") == 0) return ui(args[1], args[2], args[3]);
        const std::map<std::string, p::PreservePhase> phases{{"before-read",p::PreservePhase::before_read}, {"after-read",p::PreservePhase::after_read},
            {"before-create",p::PreservePhase::before_create}, {"writing",p::PreservePhase::writing}, {"verifying",p::PreservePhase::verifying},
            {"before-publish",p::PreservePhase::before_publish}};
#ifdef _WIN32
        HANDLE writer = INVALID_HANDLE_VALUE;
        if (args[1] == "writer") writer = CreateFileW(std::filesystem::u8path(args[2]).c_str(), GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, nullptr, OPEN_EXISTING, 0, nullptr);
#endif
        bool changed = false;
        unsigned writes = 0;
        const auto result = p::preserve_file(args[2], args[3], [&](p::PreservePhase phase) {
            for (const auto& pair : phases) {
                if (phase == pair.second && args[1] == "deny-" + pair.first) return p::PreserveCheck::deny;
                if (phase == pair.second && args[1] == "cancel-" + pair.first) return p::PreserveCheck::cancel;
            }
            if (args[1] == "block" && phase == p::PreservePhase::writing && ++writes == 2) {
                std::cout << "checkpoint\n" << std::flush;
                for (;;) std::this_thread::sleep_for(1s);
            }
            if (args[1] == "race" && phase == p::PreservePhase::before_publish) {
                std::ofstream(std::filesystem::u8path(args[3]), std::ios::binary) << "racing destination";
            }
            if (args[1] == "race-partial" && phase == p::PreservePhase::before_create) {
                std::ofstream(std::filesystem::u8path(args[3] + ".partial"), std::ios::binary) << "racing partial";
            }
            if (args[1] == "change" && phase == p::PreservePhase::after_read && !changed) {
                std::ofstream(std::filesystem::u8path(args[2]), std::ios::binary) << "changed by fixture"; changed = true;
            }
            return p::PreserveCheck::permit;
        });
#ifdef _WIN32
        if (writer != INVALID_HANDLE_VALUE) CloseHandle(writer);
#endif
        std::cout << syspane::protocol::Json({{"outcome", result.outcome}, {"partial", result.partial}, {"durable", false}}).dump() << '\n';
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
