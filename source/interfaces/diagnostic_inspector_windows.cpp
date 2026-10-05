#ifdef _WIN32
#include "diagnostic_inspector.hpp"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdexcept>

namespace syspane::interfaces {
namespace {
struct View {
    HWND label = nullptr, source = nullptr, destination = nullptr, preserve = nullptr, cancel = nullptr, status = nullptr;
    const std::function<std::string()>* text;
    const PreservationControls* controls;
    int exit = 0;
};
std::string path_text(HWND control) {
    const auto size = GetWindowTextLengthW(control);
    if (size < 0 || size > 4096) throw std::runtime_error("diagnostic.control");
    std::wstring wide(static_cast<std::size_t>(size) + 1, L'\0');
    const auto copied = GetWindowTextW(control, wide.data(), size + 1);
    if (!copied) return {};
    const auto bytes = WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, wide.data(), copied, nullptr, 0, nullptr, nullptr);
    if (bytes <= 0 || bytes > 4096) throw std::runtime_error("diagnostic.control");
    std::string text(static_cast<std::size_t>(bytes), '\0');
    if (!WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, wide.data(), copied, text.data(), bytes, nullptr, nullptr))
        throw std::runtime_error("diagnostic.control");
    return text;
}
void refresh(View& view) {
    const auto text = (*view.text)(); // This boundary supplies ASCII literals/profile IDs only.
    const std::wstring wide(text.begin(), text.end());
    if (!SetWindowTextW(view.label, wide.c_str())) throw std::runtime_error("diagnostic.control");
    const bool allowed = view.controls->permitted(), busy = view.controls->busy();
    if (!allowed) {
        view.controls->cancel();
        SetWindowTextW(view.source, L""); SetWindowTextW(view.destination, L"");
    }
    for (const auto control : {view.source, view.destination, view.preserve}) EnableWindow(control, allowed && !busy);
    EnableWindow(view.cancel, busy);
    const auto status = allowed ? view.controls->status() : "Configuration preservation is restricted by policy.";
    const std::wstring status_wide(status.begin(), status.end());
    SetWindowTextW(view.status, status_wide.c_str());
}
LRESULT CALLBACK procedure(HWND window, UINT message, WPARAM wp, LPARAM lp) {
    auto view = reinterpret_cast<View*>(GetWindowLongPtrW(window, GWLP_USERDATA));
    if (message == WM_NCCREATE) {
        view = static_cast<View*>(reinterpret_cast<CREATESTRUCTW*>(lp)->lpCreateParams);
        SetWindowLongPtrW(window, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(view));
    }
    if (!view) return DefWindowProcW(window, message, wp, lp);
    if (message == WM_TIMER) {
        try { if (wp == 2) throw std::runtime_error("diagnostic.timeout"); refresh(*view); }
        catch (...) { view->exit = 70; DestroyWindow(window); }
        return 0;
    }
    if (message == WM_COMMAND && (LOWORD(wp) == 103 || LOWORD(wp) == 104)) {
        try {
            if (LOWORD(wp) == 104) view->controls->cancel();
            else if (view->controls->permitted() && !view->controls->busy())
                view->controls->start(path_text(view->source), path_text(view->destination));
            refresh(*view);
        } catch (...) { view->exit = 70; DestroyWindow(window); }
        return 0;
    }
    if (message == WM_CLOSE || (message == WM_COMMAND && LOWORD(wp) == IDCANCEL)) { DestroyWindow(window); return 0; }
    if (message == WM_DESTROY) { view->controls->cancel(); PostQuitMessage(view->exit); return 0; }
    return DefWindowProcW(window, message, wp, lp);
}
}
int diagnostic_inspector(const std::function<std::string()>& text, bool hidden, const PreservationControls& controls) {
    const auto instance = GetModuleHandleW(nullptr);
    WNDCLASSW wc{};
    wc.lpfnWndProc = procedure;
    wc.hInstance = instance;
    wc.hCursor = LoadCursorW(nullptr, MAKEINTRESOURCEW(32512)); // IDC_ARROW, explicitly wide resource.
    wc.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);
    wc.lpszClassName = L"SysPane.Diagnostic.Window";
    if (!RegisterClassW(&wc)) return 69;
    View view{}; view.text = &text; view.controls = &controls;
    const auto window = CreateWindowExW(WS_EX_CONTROLPARENT, wc.lpszClassName, L"SysPane Diagnostic", WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 640, 495, nullptr, nullptr, instance, &view);
    if (!window) return 69;
    view.label = CreateWindowExW(0, L"STATIC", L"", WS_CHILD | WS_VISIBLE | SS_LEFT, 16, 16, 550, 165, window, nullptr, instance, nullptr);
    const auto source_label = CreateWindowExW(0, L"STATIC", L"&Source file", WS_CHILD | WS_VISIBLE, 16, 188, 110, 22, window, nullptr, instance, nullptr);
    view.source = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_TABSTOP | ES_AUTOHSCROLL,
        130, 185, 470, 26, window, reinterpret_cast<HMENU>(101), instance, nullptr);
    const auto destination_label = CreateWindowExW(0, L"STATIC", L"&New copy", WS_CHILD | WS_VISIBLE, 16, 228, 110, 22, window, nullptr, instance, nullptr);
    view.destination = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_TABSTOP | ES_AUTOHSCROLL,
        130, 225, 470, 26, window, reinterpret_cast<HMENU>(102), instance, nullptr);
    view.preserve = CreateWindowExW(0, L"BUTTON", L"&Preserve copy", WS_CHILD | WS_VISIBLE | WS_TABSTOP,
        16, 268, 140, 30, window, reinterpret_cast<HMENU>(103), instance, nullptr);
    view.cancel = CreateWindowExW(0, L"BUTTON", L"Cancel cop&y", WS_CHILD | WS_VISIBLE | WS_TABSTOP,
        176, 268, 140, 30, window, reinterpret_cast<HMENU>(104), instance, nullptr);
    view.status = CreateWindowExW(0, L"STATIC", L"", WS_CHILD | WS_VISIBLE | SS_LEFT,
        16, 316, 584, 70, window, reinterpret_cast<HMENU>(105), instance, nullptr);
    const auto close = CreateWindowExW(0, L"BUTTON", L"&Close", WS_CHILD | WS_VISIBLE | WS_TABSTOP | BS_DEFPUSHBUTTON, 490, 400, 110, 30,
        window, reinterpret_cast<HMENU>(IDCANCEL), instance, nullptr);
    for (const auto control : {view.label, close, source_label, destination_label, view.source, view.destination, view.preserve, view.cancel, view.status}) {
        if (!control) { DestroyWindow(window); return 69; }
        SendMessageW(control, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
    }
    SendMessageW(view.source, EM_SETLIMITTEXT, 4096, 0); SendMessageW(view.destination, EM_SETLIMITTEXT, 4096, 0);
    try { refresh(view); } catch (...) { DestroyWindow(window); return 70; }
    if (!SetTimer(window, 1, 1000, nullptr) || (hidden && !SetTimer(window, 2, 20000, nullptr))) { DestroyWindow(window); return 70; }
    if (!hidden) { ShowWindow(window, SW_SHOWNORMAL); SetFocus(close); }
    MSG message{};
    for (;;) {
        const auto result = GetMessageW(&message, nullptr, 0, 0);
        if (result == 0) return view.exit;
        if (result < 0) { DestroyWindow(window); return 70; }
        if (message.message == WM_KEYDOWN && message.wParam == VK_ESCAPE) { DestroyWindow(window); continue; }
        if (!IsDialogMessageW(window, &message)) { TranslateMessage(&message); DispatchMessageW(&message); }
    }
}
}
#endif
