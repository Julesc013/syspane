---
type: "SysPane Work Record"
title: "Native GNOME surface producer-lease checkpoint"
description: "Independent expiry, native disconnect, retained drawing and full-snapshot replacement have source-bound evidence."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:38:00Z"}
sp_id: "SP-GNOME-SURFACE-LEASE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-GNOME-SURFACE-LEASE", "SP-W25-PACKAGE", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native GNOME surface producer-lease checkpoint

From `0c3b164ac1b1e9e875b9decfb8805cc3bfaef46c`, the optional native bridge now
observes producer expiry independently, marks the last public marker retained,
and requires a full snapshot before displaying a replacement epoch as active.
The [package](packages/w-25-gnome-surface-lease.md) defines this bounded experiment.
The repository guide `docs/developers/build.md`, under Native GNOME surface
producer lease, binds all three mandatory cases and their independent verifier.

| Native case | Required observation | Recorded result |
|---|---|---|
| `live` | Increasing heartbeat renews; duplicate/data traffic does not; timer expires and retains generation 6; late traffic is closed | Pass |
| `ignore-expiry` | Defective expiry leaves old pixels active and admits late messages | Failed acceptance, verified negative control |
| `disconnect` | Held producer exits 73; native bus-name loss retains generation 4 before the lease deadline | Pass |

Every case admits a second, prelaunched fixture after independently observed first
process exit. Its heartbeat leaves the previous epoch/generation and acceptance
time retained. Only its full snapshot establishes active generation 1. It is a
new-epoch attachment exercise, not automatic respawn or RestartGate qualification.

Two retained native process identities are bound to their unique bus connections.
The bridge obtains the sender's native PID asynchronously from the private daemon.
An observer connection and a fixture with the wrong epoch are denied; an already
live attachment rejects replacement. Separate producer receipt journals confirm
the exact admitted, duplicate, busy, unauthorized and closed outcomes.

The surface has its own 50 ms monotonic timer and three-second lease. External
root pixels show retained state before the next diagnostic call; the observer
does not call the bridge during the expiry interval. A passive badge distinguishes
active/retained state and keeps the last accepted epoch/generation visible. Marker,
badge, icon and background evidence are separate. The assertion covers badge
colors and marker identity, not text accessibility or typography qualification.

Disabling the adapter removes its sources and badge. The original changing-marker
trace then passes for 2,400 ms, after its existing 250 ms preparation delay.
The fixture has permission to retain its public marker; this does not authorize
retaining arbitrary telemetry after a policy change.

## Verification and preserved failures

All three native cases used identical source inputs and runtime identities.
**38 lease evidence checks, 46 default desktop checks and 47 optional-focus checks
passed: 131 desktop verifier checks in this checkpoint.** The optional-focus
checks include missing, changed and extra native module identities. The original
default Show Desktop focus-restoration failure remains failed; optional restoration
passes its existing guards and remains disabled by default.

Evidence uses `out/evidence/w-25-gnome-surface-lease-`: calibration,
execution, verification, ten raw native attempts, ten source archives and 31 raw
journals. The attempt manifest also hashes 16 verifier-history artifacts. All owned
process groups have confirmed cleanup. No user desktop, settings, system service,
existing guest or credentials changed. No package installation was needed.

Three failed verifier attempts remain preserved. The first incorrectly bounded
the existing post-marker preparation as a 50 ms call. The second substituted a
hypothetical maximum capture duration for the measured capture end when selecting
pre-query timer frames. The third omitted the new exact module from the focus
extension inventory. Corrections preserve the original lease, capture, focus and
pixel requirements. The initial negative badge test also changed marker bytes
without updating their digest; the final test changes only badge pixels and proves
the independent timer check rejects concealment even when later bad marker pixels
still produce a failed overall result. Its earlier source and passing run remain.
The initial specification check also rejected a link outside the standalone bundle;
the corrected repository-path reference and original failed record are preserved.

## Remaining boundary

Connect the tested native surface semantics to the existing measured C++ data
owner and authenticated transport/policy path. Define the full projection,
disclosure-revocation, queue and retained-payload rules before enabling real
telemetry. Then qualify actual renderer stalls, automatic recovery, native editor
exit and session lock/resume independently.

Clock regression, heartbeat/generation regressions, pending-peer disappearance
and legacy generation rejection are implemented guards whose native fault cases
remain unqualified here. The portable guard's earlier tests retain their original
scope. Full text/accessibility, general producer admission, real session-manager
supervision, other display/native profiles and complete host qualification remain
open. Continue other platform tracks independently. W-02/W-05/W-25 and the full
foundation/native campaign are incomplete; no release is qualified by this result.
