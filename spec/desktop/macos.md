---
type: "SysPane Specification"
title: "macOS and OS X native profiles"
description: "Preserve an AppKit path for modern systems and older Intel OS X."
tags: ["desktop"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-MACOS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# macOS and OS X native profiles

## Native composition

Use AppKit and Objective-C++ around the portable engine for the initial inspector, settings and desktop-host application. Modern-only SwiftUI enhancements are optional later, not a dependency that removes the older OS X path. Cocoa/Objective-C objects stay inside platform interfaces; the portable core remains independent of them.

The desktop surface, ordinary inspector and temporary editor share scene projection but have separate focus/activation policies. Desktop-level window ordering and collection behaviours are candidate mechanisms requiring execution tests; this specification does not assert that window-level flags alone satisfy every Spaces/Mission Control/desktop-reveal combination.

## Session and display lifecycle

Qualify Finder restart, desktop reveal, Mission Control/Spaces, supported full-screen/window-management modes, display insertion/removal, scaling, lid changes, sleep/resume and lock/unlock. Current and older OS X behaviours may differ. A removed display retains its authored scene assignment; temporary relocation is not destructive document editing.

Surface recovery must not steal focus or become an ordinary app window on each space. Menu/status-item control remains available when the desktop surface is unavailable. The editor has an explicit exit and safe-layout recovery route.

## Collection

Use system-native notification and inventory facilities available on each exact target. Capability discovery distinguishes absence, denied access and provider failure. Do not request broad accessibility or screen-recording permissions merely to collect normal host/network state. The independent test harness may need separate capture permissions; those are not automatically production requirements.

Memory and network quantities retain their platform-specific semantics. Do not translate them into Windows labels without a defined mapping. Driver/vendor sensors are optional approved providers, not mandatory private-API probing.

## Build and deployment

Admit a contemporary macOS architecture profile and a separately pinned older Intel OS X profile early. Exact deployment targets, SDK, compiler, C++ runtime and dependencies are recorded after a successful native build/run investigation. Old toolchains and SDKs are external prerequisites, not redistributed in this archive.

An application bundle is the native deployable unit; it may contain helpers and resources while remaining one user-facing application. Signing/notarization for applicable releases and local offline use are separately documented. Reproducible payloads do not require a user to possess the publisher's signing identity.

## Acceptance

Same document/command semantics as Windows/Linux; platform-specific visual baselines and text layout tolerances. Exercise native menu shortcuts, keyboard editing, accessible property values, input pass-through and configuration migrations on both admitted profiles.
