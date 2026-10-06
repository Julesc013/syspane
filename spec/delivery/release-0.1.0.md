---
type: "SysPane Release Scope"
title: "SysPane 0.1.0 release objective and unresolved admission"
description: "Preserve the requested complete desktop release across Windows 9x, Windows NT, X11, Wayland and Mac OS X."
tags: ["delivery", "release"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T14:23:41Z"}
sp_id: "SP-RELEASE-0-1-0"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-RELEASE", "SP-PLATFORMS", "SP-WORK-PACKAGES", "SP-TARGETS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# SysPane 0.1.0 release objective

The user's expanded objective requires a full SysPane 0.1.0 release for **Windows
9x, Windows NT, Linux X11, Wayland and Mac OS X**. This supersedes the earlier
foundation-only completion boundary. The foundation/native experiments remain
prerequisites; their success cannot complete this release objective. Version 0.1.0
here identifies the product release, not a rollback of the 0.2 specification bundle
or the existing versioned telemetry/document contracts.

This record supplies release scope and gates, not another work scheduler.
`work-units.json` remains the canonical implementation graph. Windows 9x and older
NT are now required release tracks within W-23, not optional follow-up ambitions.
X11 and Wayland are separate required host profiles within W-05/W-29/W-42/W-46.
Existing Windows and Mac native verticals, providers, assurance and package work
remain required. Other previously planned families remain in the product direction.

## Required result

Each required family needs its complete native desktop edition: real telemetry,
native inspector/settings, direct scene editing, validated common commands,
save/reload and interrupted persistence recovery, a qualified persistent passive
desktop surface, independent recovery and usable diagnostic entry. A conventional
window, headless collector, fixed public tile or model smoke is not that edition.

Retain all applicable mandatory specification requirements, including data identity,
freshness and absence/error semantics; resource/network/storage/device behavior;
admitted history/replay; authored scenes/themes/presets and migration; native saver
roles; policy, accessibility, privacy, latency and lifecycle acceptance. Optional
providers, integrations and genuinely capability-dependent fields keep their existing
admission rules. No mandatory behavior is silently deferred to make a target pass.
Any proposed edition limitation must be explicit and reconciled with this complete
desktop objective before it can satisfy a release gate.

Release outputs require actual target profiles, reproducible unsigned payloads,
native package closure, dependency/license notices and SBOM/provenance, installation/
upgrade/rollback/uninstall evidence for each admitted package form, documented user
flows, release notes and support/maintenance ownership. Shared document conformance
must hold across independently implemented native adapters. Signing, notarization,
privileged installation and public publication retain their corresponding authority
requirements; this objective does not manufacture those grants.

## Profile admission still required

| Required track | Missing concrete release identity/evidence |
|---|---|
| Windows 9x | Oldest exact release/service level, CPU/ISA, viable toolchain/runtime, native lab and complete host/provider/package evidence |
| Windows NT | Oldest exact NT release/service level and architectures; contemporary and XP/7 artifacts do not qualify every NT generation; designated native labs remain required |
| Linux X11 | Exact distribution/libc/toolkit/window manager/icon manager/display profiles and complete editable persistent desktop/package acceptance |
| Wayland | Exact compositor/protocol/toolkit/profile and independent behind-icons, input, reveal, recovery, permission and package evidence |
| Mac OS X | Exact deployment floor and architectures, admitted native compiler/SDK/runtime/lab, AppKit desktop/provider and bundle/lifecycle evidence |

The user has been asked for the legacy version/architecture floors because existing
specs do not settle them. Until resolved, no guessed minimum appears as a supported
release target. Shared implementation continues independently. Existing Windows lab
designation, historical guest scope and Mac runner gaps remain recorded; no real
user desktop, unrelated VM or privileged service is admitted by implication.

The C++17 development builds are not proof of Windows 9x, old NT or old OS X support.
The existing portability contract permits smaller native implementations consuming
the same canonical source inventory and shared conformance fixtures where a viable
modern runtime is absent. It does not permit a source-tree fork or semantic weakening.

## Completion test

The release is complete only when every required target is concrete and every
applicable mandatory case has an executable runner, actual native outcome and exact
source/artifact/environment identity; complete packages and lifecycle/release
authority evidence must also exist. Missing laboratories, unspecified floors,
unimplemented features, unexecuted cases and failed required acceptance keep the
release open. A green development suite cannot substitute for any of those gates.
