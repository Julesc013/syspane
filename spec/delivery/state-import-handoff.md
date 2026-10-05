---
type: "SysPane Work Record"
title: "Complete remote state import checkpoint"
description: "Connect bounded telemetry documents to a revocable complete model without changing reported retention or inventing measurement freshness."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:50:25+11:00"}
sp_id: "SP-STATE-IMPORT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-STATE-IMPORT", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Complete remote state import checkpoint

From base `46c3ea131026a403d061e4b53763c12233b1f94d`, W-25 connects the
existing telemetry codec to the synchronized data owner through the
[complete-state import package](packages/w-25-state-import.md). W-25 remains in
progress. No native session advertises a new telemetry feature.

## Implemented and observed

The owner fixes a locally supplied authenticated binding before receipt. It checks
attachment and policy revision before parsing or advancing time, validates delivery
identity, and publishes complete reported state atomically with replay/tombstone and
lease state. Malformed/wrong-binding input disconnects this attachment; domain and
capacity failures retain coherent data and require a full resynchronization. A
native stream owner must act on the disconnect when that integration is implemented.

Remote retained observations preserve their supplied value and observation time,
including the first received denied result and values newer than local history.
They are not local acquisition attempts. Each store fixes its acquisition/import
mode on first accepted publication. Partial/gap documents cannot remove entities,
reserve a record ID, advance generation or clear a gap. Reconnect preserves replay
and retired-identity reservations; policy replacement removes this owner's payload,
binding and history. Native queues and other components still need equivalent rules.

Entity identity maps, capture time and observation generation are typed fields;
the opaque validated snapshot preserves extensions and original timestamp spelling.
Exact body bytes remain replay identity. UTC conversion is independent of local
timezone, preserves subnanosecond digits and creates no producer-monotonic tick.
Existing TTL evaluation therefore remains conservative despite heartbeat progress.
Metadata and replay bytes count against the existing admission/storage ceilings.
The shared model retains its JSON-independent dependency boundary.

Six import families pass within the complete 77-entry Windows and 78-entry Linux
CTest suites. The historical v141_xp profile passes 73 host checks, including
PE/import audits of eight executables; the allowed import set is unchanged in this
checkpoint. All three configurations and builds pass, and fresh relocated model
smoke packages pass. Profile revisions are Windows x64 12, Linux x64 13 and
historical x86 6. Native regression families retain their existing synthetic
IPC/supervision, diagnostic/preservation and private-X11 calibration scope. No
XP/7 guest or actual collector/renderer is exercised by these checks.

## Evidence and workspace

Profile records are `build-support/evidence/w-25-state-import-<profile>.json`, with
adjacent CTest logs, native reports and smoke results. `w-25-state-import-attempts.json`
binds command output, exact source archives and package identities.
`w-25-state-import-verification.json` records specification/tooling checks;
`state-import-handoff.json` is the machine handoff. Source archives and artifacts
remain under ignored owned output roots. Final recorders include the completed
documentation/build metadata; original build/test attempts retain their own input
hashes. Recorder/documentation updates did not change compiled code or test oracles.

Builds approached the campaign's combined 1 GiB output ceiling. Before native tests,
completed synthetic preservation fixtures were archived locally and every member's
bytes verified before individual ordinary files were removed. The two
`state-import-fixture-archive-<profile>.json` records bind 18,878,926 original bytes
to 151,186 archive bytes. Markers, symlinks/reparse points, multiply linked files,
native reports and active binaries remain. Archives preserve bytes and recorded
metadata, not historical ACLs, handles or link relationships.

The `state-import-smoke-dedup-windows.json` and `state-import-smoke-dedup-linux.json`
records account for another 52,068,888 bytes of redundant relocated smoke binaries.
Each removed duplicate exactly matched its original retained package archive,
manifest and result hash; package archives, results and active build binaries
remain. Restoring a payload does not attest its original permissions or a new run.
The attempt record measures final combined output against the unchanged ceiling.

## Next admitted implementation

Close native subscription/demand ownership, admission and withdrawal, current-policy
queue invalidation, disconnect/reconnect/resync and saturation before connecting
the receive owner to authenticated transport. Define producer-clock provenance and
mapping before claiming local TTL freshness. Then connect independently supervised
real data production and rendering, product failure retention, cross-component
revocation and external visible/editor-exit recovery evidence.

Other host tracks retain their recorded limitations: Linux placement fails,
Windows/macOS capture is unqualified and guest test scope remains pending. No
protected policy, user configuration or existing VM was changed; no privileged
operation, public release, AIDE activation or human review is attested.
