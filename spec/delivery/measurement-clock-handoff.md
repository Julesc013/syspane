---
type: "SysPane Work Record"
title: "Native measurement-clock checkpoint"
description: "Record causal clock brackets and peer-exit rejection without claiming measured telemetry or suspend qualification."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T08:39:00+11:00"}
sp_id: "SP-MEASUREMENT-CLOCK-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-MEASUREMENT-CLOCK", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native measurement-clock checkpoint

From base `e6dac7a16c489a19c79a43c567da9aba61374905`, the existing native stream gains
a bounded measurement-clock facility under the [investigation package](packages/w-25-measurement-clock.md).
W-25 remains in progress; no new telemetry schema or product capability is enabled.

## Observed result

Separate authenticated Windows and Linux processes pass two fixed external cases.
The server's reading lies within the client's causal before/after bracket. After
the client exits, the server's retained stream rejects sampling as peer-exited;
the next call reports permanently unavailable for that stream. The same exchange
imports synthetic inventory generation 1 without a measured tick. Its clock
readings are diagnostic log observations, not additional 0.1 wire fields.

Windows uses precise interrupt time. Linux uses BOOTTIME and checks current-thread
and peer time-namespace identity before/after the reading, retaining the first
successful namespace handle for later comparisons. Both adapters check the same
native peer handle used for stream identity around sampling, reject invalid/range/
regressed counts, and latch failure. Representation units remain distinct from
hardware resolution, physical accuracy and scheduling latency.

All current suites pass: 82 Windows, 83 Linux and 76 historical-toolset host checks.
Both modern suites include the two new native cases and the five unchanged native
inventory cases. Historical PE/import audits still cover nine executables; the
measurement adapter is disabled there. No XP/7 guest was started or modified.
Current profile revisions are Windows x64 14, Linux x64 15 and historical x86 7.

The first Windows link failed because the default import libraries did not resolve
`QueryInterruptTimePrecise`. The original attempt and source archive remain intact.
Explicitly linking the installed `mincore` library resolves it; the Windows lock
now pins that archive's SHA-256 and configure checks it. The tested probe imports
the precise-time API through the Windows realtime API set. The recorded direct
imports include other API sets selected by that archive; this is a modern-profile
dependency change, not inferred historical compatibility.

## Preserved evidence

`out/evidence/w-25-measurement-clock-<profile>.json` binds complete suites
to source and artifact hashes. Adjacent native reports retain exact process output,
native peer PIDs, causal counts, failures and cleanup. The attempts record preserves
the failed link and successful retries, with original source archives in owned
ignored output. Fresh model-only relocated smoke packages are recorded separately;
the development probes are not distribution payloads.

The machine handoff is `out/evidence/measurement-clock-handoff.json`;
the verification and attempts records share the `w-25-measurement-clock-` prefix.
Specification validation remains separate from product qualification. The current
2 GiB combined workspace allocation and preflight reservations apply; no further
allocation increase or evidence cleanup was needed.

## Remaining gates

Real suspend/resume, namespace mismatch/change/denial, native clock read/query
failure, conversion overflow and regression were not induced. The successful
bracket verifies this live laboratory run, not absolute accuracy or every clock
failure branch. No user clock, namespace, machine policy or power state was changed.

The next package must version measured-time documents and close exact negotiation,
producer epoch/domain binding, local clock continuity, future samples, retained and
replayed ages, TTL equality, rate intervals, reconnect and policy replacement.
Specify independent expected outputs before connecting an actual collector to the
native subscription and supervision path. Receipt time and heartbeat must never
become substitute measurement times. Product demand/policy distribution, real
renderers, failure retention, cross-component erasure and visible/editor recovery
remain open. Other host tracks continue independently within admitted laboratories.
