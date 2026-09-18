---
type: "SysPane Specification"
title: "Process composition and failure containment"
description: "Separate the Windows desktop surface where shell and graphics behaviour require isolation."
tags: ["architecture"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-PROCESSES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-ARCHITECTURE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-SETPARENT"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}, {"id": "SRC-SETPARENT", "resource": "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setparent", "title": "Win32 SetParent"}]
---

# Process composition and failure containment

## Proposed Windows composition

`SysPane.exe` owns session lifecycle, semantic state, settings, history and the native inspector. `SysPane.Surface.exe` owns SysPane-created desktop windows, the host state machine, graphics resources and passive presentation. Its crashes do not discard collection history. A separate diagnostic entry point remains usable without successful wall startup.

Cross-process parenting can change DPI-awareness behaviour. Isolating the surface is a design response to this documented hazard, not proof that a chosen host strategy works on any particular release.[^SRC-SETPARENT]

A provider worker is added when a vendor or device call can hang or crash. A privileged helper is optional, narrowly scoped and explicitly installed. It has no renderer, arbitrary command execution or general remote-control interface. Do not assume every storage query requires administrator rights; record actual capability/permission checks per provider.

Other platforms may compose differently. A small GNOME shell bridge must keep blocking work outside the compositor. An AppKit interface runs native UI work on the appropriate application thread. Reduced historical profiles may lack equivalent process isolation and must disclose that limitation.

## Startup order

Load bounded configuration; validate syntax, semantics and policy; establish producer identity; publish source capability state; subscribe before enumerating mutable sources; create the inspector/control endpoint; start the surface with a generation-specific handshake; send a snapshot; then send ordered deltas. Display startup and pending states rather than a fabricated complete zero snapshot.

Surface readiness and telemetry readiness are independent. A bad theme falls back to a built-in readable theme. A bad host leaves a useful inspector and explicit host failure. An unavailable provider does not block unrelated panes.

## Shutdown and restart

Stop accepting new work; revoke consumer demand; unregister notifications using valid thread/lifetime rules; cancel cooperatively; flush history within a declared deadline; mark unfinished evidence; close IPC; release graphics and windows; join owned workers. No detached threads or forced unsafe in-process cancellation.

A timeout does not prove that a blocked system call was cancelled. Quarantine a stuck worker or terminate an isolated child only under its lifecycle contract. Restart policy is bounded with jitter/backoff, attempt counts and a circuit breaker. A repeated crashing surface must not turn into a rapid respawn loop.

## IPC boundary

Use bounded, versioned messages over access-controlled native local IPC. Peers authenticate to the current user/session and negotiated protocol. Names are not credentials. A surface accepts scene/projection data, never instructions to execute arbitrary code. A worker returns observations; the controller assigns provenance and rejects spoofed source/entity authority.

No listener is bound to an external interface by default. Multi-user hosts have per-session surface state and explicitly scoped machine collectors; do not let one user's preferences control another user's UI or disclose their private fields.

[^SRC-SETPARENT]: [Win32 SetParent documentation](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setparent).
