---
type: "SysPane Handoff"
title: "Consistent child identity and preserved installed qualification"
description: "Correct incomplete identity caching while preserving actual native acceptance."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-11T19:23:38.227441+00:00"}
sp_id: "SP-CHILD-IDENTITY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-CHILD-IDENTITY-OBSERVATION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Consistent child identity and preserved installed qualification

The installed observer now caches only consistent complete child identity, with
identical argument samples around executable observation and live pidfd checks.
Incomplete/changing/disappearing/exited samples release their fd and resample
through the existing pump/deadline. Exact image role/media/parent checks apply to
verified and sandboxed observations. A sandboxed classification never claims a
directly observed executable hash.

The [package](packages/w-11-child-identity-observation.md) reviews this as an oracle
collection correction. Product artifacts remain byte-for-byte equal to the
7dd12f9a image-adoption source. Fixed case definitions, values, seal checks, real
stopped/exit states, deadlines and timing limits are unchanged. The preceding
[checkpoint](checkpoints/inspector-image-adoption.json) retains the original
HELD-CLOSE failure, old harness hash and all earlier failures. No human review is
attested; this is an engineering correction within the admitted campaign.

## Reproduction and component evidence

Controlled replay of the actual old pump caches empty argv permanently, ignoring
the next complete sample. It is explicitly model evidence, not native execution.
The new actual-pump replay proves that empty identity releases its fd and the next
complete identity is admitted. Twelve portable test methods cover literal positive
and negative traces, including disappearance, changing arguments, exit boundaries,
wrong image tuples and resource limits.

The native probe creates a sealed memfd from the existing pinned image worker,
observes exact live arguments, verifies literal 2-by-2 pixels and actual pidfd
exit. It passes with directly observed worker SHA-256
65b38c368c9472405163a244c7f1b0ddf2c8702bb5e7945e147cb4a5935e777c
and seals 15. This is component evidence; it does not substitute for installed
qualification. Linux development profile 82 remains the native environment.

## Installed results and continuation

All twelve installed image/topology cases pass under the revised collector,
including HELD-CLOSE and HELD-NAVIGATION with literal loading rows, parent-held
sealed image verification, actual stopped child state and exit before completion.
Navigation also records two unqualified early-argv samples without caching them.
Previous failures remain failed results of their original sources/oracles.

Installed inspector, editor, recovery and telemetry regressions pass. The authored
family passes seven of eight cases and fails MAX-FRAME at 458.801 ms of GUI delay
against the unchanged 100-ms limit; work peaks at 31.142 ms in that case. The
recording does not establish the delay's cause. Preserve it and keep authored
qualification open. Seven ordinary and seven complete-phase table cases,
seven recovery GUI cases,
two phase-refusal cases and three table-erasure cases pass. All 147 selected
shared checks pass on Linux profile 82, Windows profile 46 and historical
Windows host profile 37; two legacy PE audits pass. The latter are host/shared
checks, not historical guest or full native Windows qualification.
Keep W-11 in progress. Investigate the new timing failure and
continue maximum GTK chart/mixed histories, actual installed
history accumulation, human accessibility/long text and independent desktop/
lifecycle composition. Windows 9x, Windows NT, Linux X11, Wayland and Mac OS X
still require complete editions and release evidence. Shared tooling stays in
source/build; generated evidence and machine bindings stay in ignored out/.

The [checkpoint](checkpoints/child-identity.json) binds 17 executions and 11 verified
native archives, exact source/oracle/artifact/environment identities,
the controlled original-pump reproduction and the native component proof.
Ordinary table work/delay peak at 72.506/74.522 ms; complete-phase
work/delay at 69.102/63.944 ms. Policy erasure is
99.307/93.504 ms respectively, with strict complete journals
and the unchanged GUI/erasure limits. No passing run establishes the cause of
the preserved intermittent AT-SPI or current authored-delay failure.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.
