---
type: "SysPane Work Package Boundary"
title: "W-25 native retained network cache and policy erasure"
description: "Bind real projected network values to an owned native cache, explicit retained presentation and independently observed revocation."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T06:15:00Z"}
sp_id: "SP-W25-NATIVE-NETWORK-CACHE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-NETWORK-PRESENTATION", "SP-W25-GNOME-SURFACE-LEASE", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 native retained network cache and policy erasure

Investigate native ownership and erasure before enabling a general live renderer.
The admitted source is the existing real Linux CollectorProbe and its shared C++
projection. A finite Python laboratory relay owns one private native bus connection;
it is test infrastructure, not a product controller. Operational values may enter
the owned GNOME surface only under this explicit mode. They must remain in private
attempt files; public records contain identities, hashes, counts and outcomes.

## Contract and authority

`--network-cache live|ignore-clear|wrong-value|owner-loss` runs after the existing
live DING composition prerequisite. Before GNOME launch the parent retains one
relay PID. The bridge's `org.syspane.NetworkCache` interface at
`/org/syspane/NetworkCache` authenticates `Attach()` asynchronously using the private
bus daemon's native PID. Bind its unique sender name, admit only that retained PID
once, reject all other peers and remove callbacks on disable. The observer's
independent connection must fail attach, policy and frame operations.

One serialized owner may call `Policy(s revision, b permit)`, `Frame(s revision,
s sequence, s payload)`, `Heartbeat(u sequence)`, `Disable()`. `GetState()` reports
only public status, revision, entry/actor counts and sequence; never operational
values or selected source identities. Revision and frame sequences are canonical
uint64 decimal strings, compared without binary floating-point conversion. Zero is
invalid. No wrap or silent reset. An equal policy revision is idempotent only for
the same permit value; older/conflicting revisions are rejected. Frame sequences
strictly increase within a policy revision; equal sequences are rejected, never
redrawn. Policy replacement always clears the old cache, including a new grant.

An allowed frame contains exactly `producer`, `epoch`, `entity`, `generation` and
`values` (four strings or null, receive bytes, transmit bytes, receive rate,
transmit rate). IDs retain the model's ASCII grammar and 256-byte bound. Generation
is canonical nonzero uint64. Counters are canonical uint64; rates are canonical
nonnegative decimal with exactly three fractional digits. The whole JSON is at
most 4,096 UTF-8 bytes. The initial native tile admits at most 32 characters per
value; oversized values return capacity and clear the tile atomically, rather than
silently truncate. No partial field prefix, arbitrary text, labels or error messages.
Unknown keys, types, invalid values, invalid policy and stale revision/sequence
cannot modify an accepted cache. Denial takes precedence over payload parsing.

This native input is a private adapter call, not a new telemetry document or
portable protocol version. The relay explicitly selects the final real C++ frame
after the finite collector has exited normally. Its contents are a retained copy:
all non-null values are displayed under **Retained sample — age unknown**. Original
producer/epoch/entity/generation remain private cache metadata. No heartbeat, grant
or receipt rebases age, infers current freshness, or relabels the selected producer.
This intentionally enables retained presentation only. Live measured freshness
requires a separate qualification linking the C++ CLOCK_BOOTTIME domain to the
native renderer; GLib monotonic time must not be subtracted from it.

## Lifetimes and limits

The cache owns at most one frame and 128 character actors plus four row containers
and a public caption. All actors are passive and cannot focus or intercept input.
Replacing or clearing the frame empties label strings and destroys their actors,
drops the selected identities and values, and leaves no pending delivery object.
This is reachable application-state and visible-pixel erasure, not a memory-forensic
or display-server-buffer sanitization claim. No history, disk cache or export.

Attach starts a three-second owner lease. An increasing heartbeat renews it;
duplicates do not, regression closes. Frame/policy traffic does not renew. A 50 ms
native timer independently clears on expiry or clock regression. Native bus-name
loss clears immediately and permanently closes the attachment. Loss of the policy
owner cannot preserve operational pixels merely because source values are retained.

Policy revocation replies `cleared` only after local payload references and native
actors are removed; this acknowledgement does not assert presentation. External
root pixels must show no old tile within 200 ms and remain clear despite a queued
old-revision frame, duplicate grant or a new grant without a full frame. Disable
clears first and unexports/removes timer/signal callbacks. A later marker regression
must pass and the tile area must match its original background.

The laboratory uses synchronous serial calls, one outstanding call, no retry, at
most 40 calls, 8 KiB control messages and a 16 MiB private evidence limit. The native
bus may allocate a method argument before JS validation; this experiment is not a
general untrusted-client IPC memory-budget qualification. Attach has a 1 s native
lookup deadline; owner calls have a 1 s observer bound. Retain the existing 40 s
whole-attempt limit and native cleanup. No privilege, installation or user desktop.

## Independent native acceptance

The initial public digit/null calibration uses the same tile under admitted fixture
values: `1234567890`, null, `1234567890.000`, null. Capture 14x26 native glyph cells;
require distinct nonempty templates for all ten digits, dot and dash. The independent
observer then decodes real value pixels against those public templates and compares
the full strings to the independently verified native documents/C++ projection.
No operational frame may define its own oracle. A wrong-value control changes the
first displayed digit only and must fail value acceptance while calibration,
composition and erasure remain valid. This establishes the named font/tile only,
not general typography, localization or accessibility.

For live/ignore-clear/wrong-value: attach, grant 7, calibrate, run the real collector
and publish its final projection, then deny revision 8. Capture at 50 ms cadence for
400 ms. Send the old revision and an equal-revision conflicting grant; both must be
rejected. Grant 9 and require an empty tile until a new collector run/new full is
explicitly selected. Verify its digits, revoke 10, disable, and run the original
marker trace. The ignore-clear control deliberately leaves old actors during denial
and must fail the erasure oracle. It is never enabled by default.

Before real collection, additionally reject a pre-grant frame, accept an idempotent
grant without redrawing, reject an older policy, invalid generation, extra key and
zero frame sequence. A syntactically valid rate longer than the tile's 32-character
limit must return capacity with zero cached entries/character actors. It must not
consume the next accepted frame sequence or display a partial replacement.

For owner-loss: after real values are visible, terminate the retained relay with
its typed Exit(73) command. Hold a pidfd and independently observe actual exit;
capture the old tile's disappearance within 200 ms without querying bridge state
during that interval. Verify permanent closure, then disable from the parent
extension teardown. An unresponsive owner/renderer and suspend remain separate
qualification cases; no timeout is substituted for native exit.

Preserve source archives, exact collector artifact/source identity, raw private
documents/pixels, native peer/process lifetimes, monotonic call/capture times,
failures and cleanup. A verifier must reject tampered values, masked residual
pixels, missing captures, wrong policy/sequence, native owner substitution and
unbound private evidence. The existing desktop/focus verifiers remain applicable.
W-25 and the full live renderer remain open after this bounded cache experiment.

Native calls use the existing [GJS D-Bus API](https://gjs.guide/guides/gio/dbus.html).
Rendering acknowledgement is deliberately separate from visibility: Clutter's
[after-paint signal](https://gnome.pages.gitlab.gnome.org/mutter/clutter/class.Stage.html)
itself precedes display of the painted result.
