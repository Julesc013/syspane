---
type: "SysPane Work Record"
title: "Historical Windows shared-subset build checkpoint"
description: "Record the pinned v141_xp build, unchanged shared behavior, resolved runtime inputs and pending guest qualification."
tags: ["delivery", "assurance", "platforms"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:25:00+11:00"}
sp_id: "SP-HISTORICAL-BUILD-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W04-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Historical Windows shared-subset build checkpoint

From base `ce251955cab0d83c961ddf3d96708de743c52d5f`, W-04 now has a concrete
`windows-x86-v141-xp` build experiment. The existing shared implementation compiled
without C++ source or behavioral-oracle changes. W-04 remains in progress: this
checkpoint does not establish execution on XP/7 or native desktop conformance.

## Implemented and measured

The root CMake project now selects explicit component sets. The new profile builds
eleven existing portable targets: model, protocol/policy, recovery, diagnostic
projection and their tests. Modern native IPC, supervision, protected-policy and UI
adapters remain on their existing Windows/Linux profiles until historical contracts
are closed. There is one source tree and no substitute legacy implementation.

The installed Visual Studio 2017 v141_xp compiler is 19.16.27054.0, with tool directory
14.16.27023, SDK 7.1A and UCRT 10.0.10240.0. The profile selects Win32, C++17, static
Release runtime and SSE2. Thirty-four key installed inputs are pinned. Actual MSBuild
compiler commands and resolved external libraries are audited; the SDK 10.0.26100
selection banner from CMake does not override the evaluated v141_xp SDK 7.1A inputs.
MSBuild warning MSB8051 about XP-toolset deprecation is retained, not suppressed.

All 51 selected checks pass on Windows 10 x64/WOW64: 49 existing portable/build
checks and two PE audit entries, including nine independent mutation cases. The five
executables are PE32/x86 with OS/subsystem 5.01, static runtime and declared named
KERNEL32 imports. The auditor rejects newer header floors, another architecture,
unclosed function/DLL imports, delay imports, invalid RVAs and truncation. This is
an import-closure check; guest exports and dynamic runtime fallbacks remain untested.

The local model smoke archive passes relocated execution with an empty PATH and
the original literal JSON oracle. It is an unsigned development artifact, not a
product package or release. The existing modern profiles also pass their full
regressions: 53 Windows and 54 Linux CTest entries. Their native capabilities and
acceptance criteria were preserved.

## Evidence

`build-support/evidence/w-04-historical-build.json` binds the exact source/profile,
five executable identities, actual linker inputs, all 51 cases and relocated smoke.
The raw CTest log and smoke record are adjacent. Modern regression records use the
`w-04-regression-` prefix; their captured native reports remain separately scoped.
The build-attempt record retains the initial 49-case run, later audit integration,
actual commands and the vendor deprecation warning. Source archives for these
attempts remain in the owned campaign cache with recorded hashes.

Specification checks are in `w-04-verification.json`. No test result is converted
into a supported XP or Windows 7 profile. Full vendor archives and complete compiler
header closure are not preserved, so bit-for-bit reproduction is not established.

## Laboratory discovery and next step

Read-only inventory found VirtualBox 7.2.6 outside PATH, with powered-off Windows XP
and Windows 7 registrations, and an off Hyper-V Windows 10 registration. The XP
base disk reports 768 MiB allocated; Windows 7 reports only 2 MiB. Neither has a
VirtualBox snapshot. These facts do not establish a bootable or designated test OS.
No VM was started, snapshotted, modified or captured. The user's guest-scope answer
is pending because existing guest desktops are not automatically synthetic data.

After the relevant guest is admitted and shown usable, run the four C++ test
binaries' 44 existing case IDs and the model smoke binary there. CMake/Python and
six build/tooling checks remain on the modern build host. Record OS/service-pack/CPU/runtime identity and
native results independently for XP and Windows 7. Then run real host candidates
with the unchanged W-02 external reveal/input/wallpaper criteria. Do not infer
compatibility from this host's successful WOW64 execution or PE metadata.

Current Windows capture and historical/macOS native host work remain open. A macOS
endpoint has not been identified in the admitted environment. Independently advance
W-25's recent-failure metadata, explicit configuration preservation and real
renderer/data/editor recovery, and the unresolved Linux composition strategy.
