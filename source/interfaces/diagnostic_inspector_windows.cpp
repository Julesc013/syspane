#ifdef _WIN32
#include "diagnostic_inspector.hpp"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdexcept>

namespace syspane::interfaces {
namespace {
struct View { HWND label = nullptr; const std::function<std::string()>* text; int exit = 0; };
void refresh(View& view) {
    const auto text = (*view.text)(); // This boundary supplies ASCII literals/profile IDs only.
    const std::wstring wide(text.begin(), text.end());
    if (!SetWindowTextW(view.label, wide.c_str())) throw std::runtime_error("diagnostic.control");
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
    if (message == WM_CLOSE || (message == WM_COMMAND && LOWORD(wp) == IDCANCEL)) { DestroyWindow(window); return 0; }
    if (message == WM_DESTROY) { PostQuitMessage(view->exit); return 0; }
    return DefWindowProcW(window, message, wp, lp);
}
}
int diagnostic_inspector(const std::function<std::string()>& text, bool hidden) {
    const auto instance = GetModuleHandleW(nullptr);
    WNDCLASSW wc{};
    wc.lpfnWndProc = procedure;
    wc.hInstance = instance;
    wc.hCursor = LoadCursorW(nullptr, MAKEINTRESOURCEW(32512)); // IDC_ARROW, explicitly wide resource.
    wc.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);
    wc.lpszClassName = L"SysPane.Diagnostic.Window";
    if (!RegisterClassW(&wc)) return 69;
    View view{nullptr, &text, 0};
    const auto window = CreateWindowExW(WS_EX_CONTROLPARENT, wc.lpszClassName, L"SysPane Diagnostic", WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 600, 285, nullptr, nullptr, instance, &view);
    if (!window) return 69;
    view.label = CreateWindowExW(0, L"STATIC", L"", WS_CHILD | WS_VISIBLE | SS_LEFT, 16, 16, 550, 165, window, nullptr, instance, nullptr);
    const auto close = CreateWindowExW(0, L"BUTTON", L"&Close", WS_CHILD | WS_VISIBLE | WS_TABSTOP | BS_DEFPUSHBUTTON, 448, 190, 110, 30,
        window, reinterpret_cast<HMENU>(IDCANCEL), instance, nullptr);
    if (!view.label || !close) { DestroyWindow(window); return 69; }
    for (const auto control : {view.label, close}) SendMessageW(control, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
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
