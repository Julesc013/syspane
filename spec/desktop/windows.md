---
type: "SysPane Specification"
title: "Windows native host and presentation profiles"
description: "Investigate contemporary and XP/7 hosts in parallel without assuming a universal shell trick."
tags: ["desktop"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-WINDOWS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-SETPARENT", "SRC-WINDOWS", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}, {"id": "SRC-SETPARENT", "resource": "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setparent", "title": "Win32 SetParent"}, {"id": "SRC-WINDOWS", "resource": "https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features", "title": "Win32 window features"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Windows native host and presentation profiles

## Contemporary Windows candidate

An isolated surface process owns its rendering HWNDs. A small Explorer adapter identifies the wallpaper/icon arrangement, validates process identity and creation instance, and attaches only after checking the expected relationship. `WorkerW` is a candidate private-shell mechanism, not a guaranteed Windows API contract. Track the strategy version and exact shell environment in evidence.

`SetParent` has documented cross-process DPI consequences. The surface process boundary contains that risk; it is not evidence that every parenting combination works.[^SRC-SETPARENT] Keep the ordinary native inspector and configuration windows in an unaffected controller process. Do not call shell-private messages repeatedly or infer their return values to be valid window handles without verification.

Use a notification receiver capable of receiving required broadcasts. A message-only window does not receive broadcast messages.[^SRC-WINDOWS] Register source/session/display listeners with explicit shutdown and cancellation ownership; do not leave callbacks pointing at destroyed objects.

## Graphics candidates

DirectWrite/Direct2D is the contemporary text/drawing choice. The presentation backend chooses an owned-window composition path or tightly bounded bitmap/layered path after tests. Renderer selection, alpha transport and shell attachment are separate capabilities. Device loss recreates graphics resources without discarding accepted telemetry or the authored scene.

Straight versus premultiplied alpha, grayscale text on transparent surfaces, DPI conversion and pixel snapping are explicit backend responsibilities. Native surfaces should be bounded to useful regions, not an enormous transparent virtual-desktop bitmap. Do not assume a semantic dirty row translates into a partial compositor transfer.

## XP and Windows 7 admission

Layered child-window support begins with Windows 8.[^SRC-WINDOWS] A GDI renderer therefore does not by itself solve transparent-child placement on XP/7. Their initial work unit must experiment with actual desktop hosts, input and wallpaper behaviour. The result can qualify a native inspector/collector before qualifying the wall; do not quietly replace the requirement with a wallpaper rewrite.

Pin compiler, SDK, CRT, import audit and runtime requirements separately by profile. The C++17 source baseline is provisional until the shared subset runs on the admitted XP compiler/runtime; isolate target-specific facilities instead of duplicating the whole product. Optional APIs require actual dynamic resolution and error handling, not just version macros.

## Qualification dimensions

Include x86/x64 where required, ARM64 where admitted, composition mode, multiple monitors, negative monitor coordinates, mixed scaling, Explorer restart, RDP, virtual desktops, full-screen applications and device resets. XP/7 and 10/11 have separate evidence records. OS strings and successful compilation do not establish behaviour.

[^SRC-SETPARENT]: Microsoft SetParent documentation, especially cross-process DPI behaviour.
[^SRC-WINDOWS]: Microsoft Window Features documentation, layered children and message-only windows.

## Profile-specific admission

Use [typed target profiles](../delivery/target-profiles.md) for exact build, native
host, dependency and isolation identity. Keep renderer success separate from shell
placement/input/reveal evidence. [Screensaver roles](screensaver.md) require their
own preview/configuration, architecture, power and privacy qualification.
