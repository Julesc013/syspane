---
type: "SysPane Work Record"
title: "Synchronized data owner checkpoint"
description: "Bind atomic model admission, independent lease state and revocable presentation to portable execution evidence."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:01:36+11:00"}
sp_id: "SP-DATA-VIEW-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-DATA-VIEW", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Synchronized data owner checkpoint

From base `c676abe3f264a30a9ea519ba7a966ac4ad75dc49`, W-25 adds a typed data owner
joining model validation, producer leases and policy-controlled presentation. The
[package](packages/w-25-data-view.md) owns its behavior. W-25 and the campaign
remain in progress; no native telemetry subscription is enabled by this component.

## Implemented behavior

`syspane_data_view` validates a complete candidate in speculative model state before
publishing data and lease generation together. Invalid input retains the previous
coherent payload and requires a full snapshot. A reconnect to the same producer
epoch retains replay reservations and retired identities. A new epoch retains the
old payload explicitly until a valid full snapshot replaces it.

The consumer-only `Store::resynchronize` operation can confirm identical normalized
data at the current generation with a new full-publication identity. That identity
uses ordinary replay capacity. Altered same-generation data fails; ordinary
`Store::publish` still requires increasing generations. Old exact replay neither
rolls data backwards nor renews acceptance time. Data does not renew a lease, and
heartbeats do not refresh measurement timestamps or TTLs.

Each call is bound to an authenticated attachment and admitted policy revision.
Obsolete callbacks cannot advance the successor clock. Every observed policy
replacement drops this owner's payload, invalidates its attachment and advances
its local lifetime. A renewed grant requires a fresh attachment and full snapshot.
Unavailable or non-increasing available policy fails closed. Clock failure cannot
prevent removal. These reference-lifetime guarantees do not attest physical memory
zeroization, other components' caches, file deletion or exported data revocation.

Projection is a synchronous borrowed callback from a serialized trusted owner.
It carries explicit active/retained state and unchanged model observations; the
consumer must respect both lease state and measurement freshness. Reentry is
rejected and callback exceptions release the borrow guard. There is no asynchronous
renderer integration or hostile native-code isolation claim.

## Verification

Six fixed case families exercise atomic admission, replay/resynchronization,
reconnect, expiry/freshness, policy replacement and resource/clock/callback faults.
Inputs and expected values are literal test cases. Windows development profile
revision 10 passes all 65 CTest entries; Linux revision 11 passes all 66. Historical
toolset revision 4 passes 61 host checks, including PE/import inspection of six
executables. This is execution on the current development hosts, not XP/7 guest
runtime qualification. Existing native IPC, supervision, diagnostic, preservation
and Linux pixel-calibration regression families also pass within their recorded
scope. No failed build/test attempt was observed for this data-owner checkpoint;
previous native placement and preservation failures remain preserved separately.

All three profiles receive a fresh relocated unsigned model smoke package. The
package smoke covers the model executable, not a packaged data-view application or
desktop edition. Evidence is recorded in
`build-support/evidence/w-25-data-view-<profile>.json`, adjacent CTest/native records
and `.smoke.json` results. `w-25-data-view-attempts.json` binds source archives and
command attempts; `w-25-data-view-verification.json` records specification checks.
`data-view-handoff.json` is the machine-readable continuation record. Source
archives and package binaries remain under the bounded, owned, ignored roots.

## Next work

Close snapshot/delta subscription messages, decoding bounds and native ownership
before connecting this component to telemetry. Add actual collector/renderer data
recovery and cross-component policy invalidation with independent visible evidence.
Product failure-log retention and independent editor exit remain required W-25
work. Existing protected-policy deployment, external accessibility/input and
foreign-owner/filesystem qualification retain their separate admission needs.

Continue independently available host experiments. Linux composition still fails
its desktop-placement oracle; Windows/macOS capture remains unqualified. Existing
guest VMs have not been started or changed while their test scope is pending. No
privileged operation, public release, AIDE activation or human review is attested.
