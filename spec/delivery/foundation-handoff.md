---
type: "SysPane Work Record"
title: "Foundation implementation handoff"
description: "Resume the admitted campaign from tested model builds and local smoke packages."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T23:15:42+11:00"}
sp_id: "SP-FOUNDATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W26-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Foundation implementation handoff

The full campaign remains active. The base is
`229a49850a657a76b0201532b4ea61ddfd92a3aa`; the containing commit identifies the
integration. Per-profile records in `out/evidence/` bind actual artifact
hashes and source input hashes without guessing a future commit hash.

## Delivered and verified

W-00's runtime admission and root routing are present. W-01 delivers C++17 typed
state, immutable snapshots, retired identities, replay/conflict handling, explicit
measurement states, epoch-aware intervals, metric TTL and bounded admission.
Targets and dependency ownership are enforced by CMake plus a graph check whose
negative case introduces a forbidden model dependency. Native UI types never enter
the model. The API remains experimental and single-writer.

Both `windows-x64-gcc15` and `linux-x64-gcc13` passed 18 executable checks: the nine
original model/validity/clock cases, six additional boundary cases, independent
smoke-output comparison and two component-graph checks. Test discovery is nonempty
and unknown case IDs fail. Windows runs on Windows 10 x64 build 19045; Linux ELF
runs under Ubuntu 24.04 WSL2 with GCC 13.3, glibc 2.39 and libstdc++6 14.2. The
compiler, CMake, Ninja, frontend and static runtime archive fingerprints are pinned.
Complete vendor/header provenance and bit-for-bit build reproducibility are unproven.

W-26's initial local smoke slice packages the selected model executable, identity
manifest and explanatory README. Both archives pass relocated execution with empty
PATH and fixed expected JSON. Windows imports only KERNEL32 and UCRT API sets;
Linux direct imports are libstdc++, libgcc_s and libc. These are local development
artifacts, not usable desktop editions, installers or public releases.

Case/artifact records: `out/evidence/w-01-windows-x64-gcc15.json` and
`out/evidence/w-01-linux-x64-gcc13.json`. Package records use the matching
`w-26-<profile>.json` names. Remaining family-wide T-TARGETS/T-CLOCK/native package
qualification is not promoted by these bounded synthetic results.

## Preserved failures and laboratory limits

The first Linux configure failed because unprivileged chmod is denied on the
Windows mount. A direct write/chmod probe reproduced it. Build products now use an
owned native cache; the source checkout remains shared. An initial WSL package
invocation expanded a build-root variable too early, then a later run encountered
Git's shared-checkout ownership check. A shell script now owns Linux expansion;
the read-only Git query trusts only this exact admitted checkout for that command.
No global Git trust, credentials, user identities or filesystem privileges changed.
Failures are recorded in `out/evidence/foundation-attempts.json`.

The installed WinLibs UCRT toolchain is not an XP candidate: its own package record
excludes pre-Windows-7-SP1 UCRT support, and the built PE imports UCRT API sets.
The PE subsystem version alone does not prove compatibility. XP/7 native labs and
an alternative historical toolchain have not been admitted/located for execution.
Linux currently exposes WSLg display endpoints, with no GNOME/KDE desktop shell
found in the inspected environment. That is sufficient for model builds, not a
behind-icons Linux host test. No macOS/older OS X laboratory has been admitted.
Keep these tracks pending/blocked where their required evidence is unavailable.

## Next dependency-ready work

Close W-24's message body/state/role tables, authentication and mutable ownership,
controller-wide/control-queue limits and executable acceptance before implementing
its transport/policy boundary. W-02 can develop its independent oracle against the
foundation; W-25 additionally consumes W-24. Then run each native-host candidate
against the actual available environment, preserving failed/inconclusive outcomes.

The model's 128 retained publication records and 64 MiB retained-data ceiling are
intentional foundation admission limits. W-07 must close long-running telemetry
retention before enabling continuous sampling; no silent eviction or epoch churn
may conceal exhausted identity bookkeeping. The model is not yet a production
collector, controller, renderer, recovery service or native desktop host.

Do not re-request routine campaign authority. Do not mark the whole campaign
complete from these foundation results. Continue ordinary local commands and
record evidence for each remaining package. Release, privileged operations and
weakened acceptance remain outside the admitted instruction.
