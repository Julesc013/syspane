---
type: "SysPane Specification"
title: "Persistent desktop host contract"
description: "Define visible behaviour independently of a shell attachment technique."
tags: ["desktop"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-DESKTOP"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PROCESSES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Persistent desktop host contract

## The observable contract

A qualified desktop profile SHALL show a live SysPane surface behind desktop icons and in front of the unchanged configured wallpaper whenever the ordinary desktop is revealed. On Windows this includes Win+D, taskbar Show Desktop and Peek. Persistence is temporal: a disappearance followed by repair does not pass these reveal actions. A supported equivalent on another desktop has its own named scenario.

The passive surface does not activate, steal focus, appear as an ordinary taskbar or task-switcher entry, or obstruct icon selection, launch, drag selection and context menus. No wallpaper file, configuration, organization logo or wallpaper policy is changed. The user can designate exclusion regions; detection of icon positions is optional and must not rearrange them.

Secure desktops, sign-out and powered-off displays are not surfaces on which SysPane bypasses security. When the shell exits, collection and history can remain active while presentation is unavailable. Recovery begins after a viable shell/session host is available; record the outage and recovery interval. This is a different criterion from reveal persistence.

## Host state machine

`detached → discovering → validating → attaching → attached`. Failure branches lead to `degraded` or `unavailable`; a changed shell identity leads to bounded rediscovery. Display changes lead to reconfiguration, and graphics loss to renderer recreation. Every transition carries a reason, host strategy, process/window generation and observation time.

Use event notifications and bounded reconciliation rather than continuous Z-order re-sinking. Bound discovery attempts, query timeouts and retries. Never loop indefinitely at high priority. The host's health model must remain accessible through the ordinary inspector even when no wall is visible.

## Isolation and replacement

A desktop host interface exposes discover, attach, validate, reposition, suspend, detach and diagnostics. It consumes a surface/scene projection, not collector implementation objects. Its platform-owned resources have explicit lifetimes. The private Windows shell adapter can be replaced by an official future API without changing data contracts.

Only SysPane-owned rendering windows/objects may receive drawing commands. No Explorer/DWM injection, foreign window subclassing, direct painting to another process's desktop DC, or global disabling of desktop reveal behaviour is an approved baseline mechanism.

## Failure classification

A conventional inspector remains useful on an unsupported desktop. An ordinary floating/bottom-Z-order fallback is explicitly **not wall-conformant**. The UI reports the reason and capability, not a false “supported” state. Stable release claims list the exact profile and enabled host strategy.

## Acceptance

Use an independent temporal observer with a synthetic marker changing while desktop reveal is active. Verify both its visibility and value. Test icon interaction, wallpaper preservation, ordinary applications, full-screen transitions, shell restart, session reconnect, display/DPI changes and host-handle reuse. A successful graphics submission or visible HWND flag is not sufficient evidence.
