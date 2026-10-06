---
type: "SysPane Work Package Boundary"
title: "W-03 contemporary Windows host investigation"
description: "Establish native Explorer topology and an admitted desktop laboratory before attachment, pixels and shell recovery."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:40:00Z"}
sp_id: "SP-W03-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WINDOWS", "SP-W02-PACKAGE", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-03 contemporary Windows host investigation

The initial campaign requires a real contemporary Windows host experiment,
independently of XP/7, Linux and macOS. The existing modern Windows profile supplies
native process/IPC/recovery components but has no desktop-host evidence. Complete
this investigation in phases; read-only topology cannot complete the host gate.

## Native observation boundary, ready to implement

Own `tests/desktop/windows_host_inventory.py` and its fixed decision tests. The
observer runs under the existing interactive account without elevation. It may
read shell window classes, handles, owning thread/process IDs, process creation
time, executable identity, session and its own window-station/desktop identity.
It must not read window titles, icon labels, user files, wallpaper or pixels, send
window messages, create/reparent shell windows, activate input, or restart Explorer.
This read-only phase needs no disposable guest and does not designate the current
desktop as a test lab.

`GetShellWindow` selects the native shell, not a process-name search. Open that
exact process with query/synchronization rights; keep its handle across two complete
observations and require it to remain live. Record creation FILETIME as decimal
text, session and full executable path. Compare the image with the canonical system
`explorer.exe`; a matching name alone is insufficient. Record its SHA-256 and the
actual host build. This identifies observed ownership, not code-signing trust or
permission to attach. No credentials, tokens or arbitrary process image paths are
included in the public result.

Enumerate at most 4,096 top-level windows, retaining only Progman/WorkerW windows
owned by the selected shell. Enumerate at most 512 descendants per retained root
and retain only SHELLDLL_DefView/SysListView32. Cap retained roots at 32. Record
their native parent, class, owner PID and thread. Enumeration may change while it
runs; retain both observations 100 ms apart. Changed topology/ownership produces
`changed`, never a stable candidate. Identical polls do not establish HWND creation
identity or eliminate an ABA race; event-bound lifetime validation remains mandatory
before later attachment.

Fixed decisions are `absent` (no native shell), `owner_unverified` (unverified image,
session or live held process), `changed`, `ambiguous` (more than one icon hierarchy),
`incomplete` (missing required parent/child chain), or `observed`. `observed` requires
exactly one direct Progman/WorkerW → SHELLDLL_DefView → SysListView32 chain under the
held shell. It records possible WorkerW roots without asserting their visible
stacking, transparency, suitability, or behind-icons success.

Run native calls in one owned Python child, with an eight-second outer timeout,
no descendants and bounded 1 MiB output. Preserve errors/timeouts and confirm child
exit. Keep source hashes, a source archive, exact command, runtime/OS identity,
both observations, decision and cleanup in an owned `out/campaign/` attempt.
Unit fixtures independently specify missing/foreign owners, changed shell/graph,
duplicate icon chains, absent icons, and a valid literal hierarchy. Each negative
case must retain its specific decision. No fixture manufactures a native pass.

## Desktop experiment boundary, laboratory pending

The registered Hyper-V Windows 10 VM is an available registration, not an admitted
or verified guest. Its designation and usability must be established before guest
boot, mutation, capture or shell recovery. Existing XP/7 and Mac laboratory gates
remain independent. A noninteractive window station cannot establish visible
desktop/input acceptance; do not relabel its buffers as compositor output.

Once a synthetic Windows desktop is admitted, close its transfer, child launch,
external capture, recovery and cleanup commands before running the host candidate.
Use one isolated surface process and a separately held observer/recovery owner.
Bind the exact OS/Explorer build, architecture, session, display/DPI and composition
mode. Validate native HWND/process creation/lifetime around any WorkerW attachment;
private shell messages require a named, bounded candidate strategy. The inspector
and recovery path remain independent of cross-process parenting and DPI effects.

The fixed host gate uses the existing marker/time oracle and independent synthetic
icon targets: behind-icons composition, uninterrupted marker progression through
actual Win+D/Show Desktop, icon click/drag/context menu and focus behavior, unchanged
wallpaper, and recovery after controlled Explorer exit/replacement. Ordinary-window,
frozen and disappearing candidates must fail their corresponding dimensions.
Preserve failures and qualify only the exact passing dimensions/environment.
No normal window, structural tree or acknowledged paint substitutes for these tests.

Native observer command: after the Windows workspace test preflight, run
`.venv/Scripts/python.exe -X utf8 tests/desktop/windows_host_inventory.py`.
Its decision tests run with
`.venv/Scripts/python.exe -X utf8 tests/desktop/test_windows_host_inventory.py -v`.
No product binary, supported target or public package is enabled by this phase.

Primary references: [shell window](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getshellwindow),
[top-level enumeration](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumwindows),
[descendant enumeration](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumchildwindows),
and [window stations](https://learn.microsoft.com/en-us/windows/win32/winstation/window-stations).
