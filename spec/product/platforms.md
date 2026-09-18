---
type: "SysPane Specification"
title: "Platform and capability admission matrix"
description: "Keep broad native ambition without advertising untested parity."
tags: ["product"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-PLATFORMS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-ARCHITECTURE", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Platform and capability admission matrix

## Status axes

Each profile records intent, implementation, executed qualification and current availability independently. Initial entries are **planned / not implemented / not qualified**. Profiles name OS version/build, architecture, shell/compositor, renderer, display/DPI arrangement, permissions, toolchain and known limitations. These are populated by experiments, not inferred from a generic platform label.

## First campaign

| Family | Immediate target work | Required distinction |
|---|---|---|
| Windows 10/11 | contemporary Win32 controller, surface and native GUI | each build/architecture/shell configuration qualified |
| Windows XP/7 | native inspector/collector plus early host experiment | older transparent hosting is not solved by selecting GDI |
| Linux | kernel collectors, native GUI and separate X11/Wayland/GNOME/KDE paths | distribution, toolkit and shell are separate profiles |
| macOS/OS X | AppKit modern and pinned older Intel profiles | exact deployment targets chosen after build/run proof |

x86, x64 and ARM64 are distinct binaries where appropriate, not distinct product source forks. Servers with no desktop can qualify Console or Collector compositions without making a desktop-wall claim.

## Extended native family

BSD variants, Solaris/illumos, older Windows NT, Windows 9x, DOS, OS/2 and classic Mac remain planned native/reduced profiles. RHEL is a Linux distribution baseline. Windows RT needs an authorized execution/deployment feasibility result before a desktop promise; it is not equivalent to normal ARM64 Windows.

Constrained targets may implement a reduced native core/protocol or use a companion for advanced functions. That does not erase the goal of local native usefulness. C++17 is not imposed on a target lacking a viable runtime/toolchain; isolate a smaller implementation that passes the shared conformance fixtures. Do not prematurely constrain the entire modern core to C89.

## Minimum capability compositions

Desktop: local state, native inspector/settings/editor, persistent qualified surface. Console: local state and native text control. Collector: local state and export. Native capabilities can be partial but are never renamed to hide missing desktop persistence.

Historical security support and application compatibility are separate. No obsolete OS receives an implied security warranty because SysPane runs on it. Unsupported telemetry, limited isolation, encoding/filename constraints and transport/security limitations remain visible.

## Gate

Each new profile has a work unit, explicit build recipe and independent behavioural evidence. Reuse common fixtures; do not copy source into `modern/legacy` trees. Unqualified profiles appear in roadmap, not the public supported-platform list.
