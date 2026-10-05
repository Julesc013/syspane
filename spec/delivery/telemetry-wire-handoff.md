---
type: "SysPane Work Record"
title: "Bounded telemetry document checkpoint"
description: "Bind versioned delivery decoding and exact replay preservation to native-compiled portable cases without claiming a live subscription."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:19:35+11:00"}
sp_id: "SP-TELEMETRY-WIRE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-TELEMETRY-WIRE", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded telemetry document checkpoint

From base `00a551af82d564282f1f07d9b42c483df73c0aa1`, W-25 adds versioned
subscription and snapshot/delta delivery documents to the existing protocol library.
The [package](packages/w-25-telemetry-wire.md) and
[schema](../contracts/telemetry.schema.json) define this boundary. W-25 remains in
progress. Preview/health sessions still do not advertise telemetry subscriptions.

## Implemented and observed

The C++ codec enforces selected document versions/features, direction, exact
connection/producer/subscription/policy/channel/class bindings and a strictly older
delta base. It checks complete snapshot/observation 0.1 shapes, uint64 ranges,
calendar/offset syntax, graph references, unique IDs/observation fields and
generation/epoch consistency under existing frame/parser/count/text budgets.

It preserves the entire document and original body bytes, including entity identity,
reported retained values, partial/gap status, offset/fractional timestamp text and
inert extensions. Encoding revalidates the original bytes and their agreement with
the exposed JSON tree. Decoding is not model publication or policy authorization.
No field-patch language, timestamp conversion or synchronization claim is invented.

Six native-compiled portable case families pass within the complete 71-entry Windows
and 72-entry Linux suites. The historical v141_xp profile passes 67 host checks,
including PE/import audit of seven executables. Current profile revisions are
Windows x64 11, Linux x64 12 and historical x86 5. Native regression families retain
their existing IPC/supervision/diagnostic/preservation/private-X11 scope. None
executes native telemetry or a historical guest. Fresh relocated model smoke
packages pass for all three profiles; they remain model-only development archives.

The first historical run failed its import audit because C++ fixture-file streams
added mandatory Kernel32 `SetEndOfFile`. Every codec family already passed in that
run. The original attempt/source archive and complete failing import table remain
preserved. After checking Microsoft's documented XP minimum, the declaration adds
that single observed import. PE format, static CRT, exact DLL/name validation and
negative import cases remain enforced. This does not prove guest runtime behavior.
The package links the API reference and keeps actual XP/7 execution unqualified.

## Evidence and workspace

Records are `build-support/evidence/w-25-telemetry-wire-<profile>.json` with adjacent
native reports, CTest logs and smoke results. `telemetry-original-import-failure.json`
preserves the initial executable/import identities. `w-25-telemetry-wire-attempts.json`
binds command output and source archives; `w-25-telemetry-wire-verification.json`
records specification/tooling checks. `telemetry-wire-handoff.json` is the machine
handoff. Actual binaries and source archives stay in ignored owned output roots.

Before adding build output, the owned X11 APT metadata cache was archived losslessly:
50 files, 145,160,190 original bytes, a 41,019,315-byte gzip archive. Every member's
SHA-256 was checked against the original before individual cache files were removed.
`telemetry-cache-archive.json` records original paths/digests and archive identity.
Package archives, extracted runtime, source, tests and native evidence were unchanged.
The archive is local under the same owned root; restoring metadata, if needed, must
validate those identities and exact destination containment first. The checkpoint's
attempt record measures combined output against the campaign's 1 GiB ceiling.

## Next admitted implementation

Define and implement complete-state import into the data owner before attaching this
codec to a native subscriber. Preserve identity metadata, snapshot completeness,
observation generations and reported retention state. A received retained-denied
value cannot be treated as a fresh acquisition and overwritten from older local
history. Partial/gap records must not remove omitted entities or clear resync.
Producer-monotonic provenance and local freshness mapping also need closure: the
existing observation 0.1 document does not carry the model's measured tick.

Then connect native authenticated subscription/demand lifetimes, current policy,
resync/replay, queue invalidation and independent producer supervision. Complete
real collector/renderer data recovery, product retention and visible/editor-exit
evidence. Other host tracks retain their recorded limits: Linux placement fails,
Windows/macOS capture is unqualified and existing guest test scope remains pending.
No existing VM, protected policy or user configuration was changed; no privileged
operation, public release, AIDE activation or human review is attested.
