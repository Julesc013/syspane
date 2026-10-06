---
type: "SysPane Work Package"
title: "W-25 independent native surface producer lease"
description: "Observe producer expiry, disconnect, retained pixels and new-epoch resynchronization on the owned GNOME surface."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:16:00Z"}
sp_id: "SP-W25-GNOME-SURFACE-LEASE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-PACKAGE", "SP-RECOVERY", "SP-W05-GNOME-COMPOSITION", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 independent native surface producer lease

Connect the existing three-second producer-lease semantics to the actual GNOME
bridge. This is the native surface half of recovery: its owner observes elapsed
time independently of a stopped producer and renders retained state. It does not
replace the C++ model/data owner, general transport, render watchdog or supervisor.
The only payload here is a public synthetic marker, never real telemetry.

## Interface, authority and ownership

`--surface-lease live|ignore-expiry|disconnect` owns the existing live composition
prerequisite. Before shell launch, the parent retains two fixture children and
records their exact PIDs in the bridge's private environment. They are separate
sessions/process groups, with bounded control sockets and private journals. The
Linux abstract socket uses the unique attempt ID; both ends verify native UID and
the observer verifies the retained fixture PID. No external listener is created. Neither
is a product controller or an automatic respawn. The second is an already-running
fixture; its connection exercises new-epoch admission, not RestartGate qualification.

Only this explicit mode adds `org.syspane.SurfaceLease` at
`/org/syspane/SurfaceLease` on the private shell connection. `Attach(s epoch)`, `Heartbeat(u sequence)` and `Snapshot(u
generation)` return a bounded status string. `GetState()` returns bounded auxiliary
JSON; `Disable()` removes this experiment's sources/objects. The uint32 stimulus
subset is laboratory-only and does not change the existing uint64 product contracts.

Attach asynchronously obtains the sender's native PID from the private bus daemon
and matches the two retained fixture PIDs. The permitted pairs are first PID with
`lease:1`, second PID with `lease:2`; an epoch string or bus name alone grants nothing.
Bind the admitted unique connection name. At most one authentication is pending;
no synchronous bus wait blocks the compositor. A slot attaches at most once.
Reject replacement while an attachment is alive. Deny other peers, wrong epochs,
old/retired connections and legacy generation mutation after lease activation.
Name loss closes the matching current attachment; old-owner events cannot close
its replacement. Keep all callbacks bounded and remove them on disable.

Attach starts a 3,000 ms lease on the shell's monotonic clock and requires a full
snapshot. Every incoming operation first advances expiry; a 50 ms native timer
also advances it without producer traffic. Equality is expired. An increasing
heartbeat renews liveness only; duplicates do not renew, regression closes. Snapshot
traffic never renews liveness. Reject zero/regressing snapshot generations; exact
generation replay is duplicate without changing last-accepted time. A new epoch
may start at a lower generation but only a full snapshot replaces retained state.
Clock regression closes the attachment. No late message resurrects it.

Retain the last accepted epoch, generation and acceptance time across expiry,
disconnect and new attachment. A heartbeat in a new epoch cannot relabel or refresh
it. Before the first full there is no accepted marker. This fixed public fixture
has permission to retain; arbitrary telemetry/disclosure-policy integration remains
disabled. The passive badge at (460,200,120,80) has a solid status region and readable
state/epoch/generation text. Active uses RGB (32,160,64), retained uses (208,144,32),
waiting uses (32,96,192). It cannot receive input/focus. Last accepted marker pixels
remain present when retained. The existing icon overlap/background stay unchanged.

## Fixed native exercise

After original composition passes, attach the first producer, send heartbeat 0
and snapshot 4. Capture externally every 50 ms with 50 ms paired-capture, 150 ms
coverage and 200 ms visible-transition bounds. Marker decoding, badge status pixels,
native icon ownership and background pixels are independent of bridge diagnostics.
Do not poll diagnostic methods during the expiry interval: observation must not
advance the bridge's lease in place of its own timer.

At 800 ms, send increasing heartbeat 1 and snapshot 5. At 1,600 ms, send duplicate
heartbeat 1 and snapshot 6. The active surface expires at last heartbeat receipt
plus 3,000 ms despite the later snapshot/duplicate. It must retain generation 6
and show retained state within 200 ms. At 4,100 ms, heartbeat 2 and snapshot 7 are
closed, leaving generation/epoch/accepted time unchanged. At 4,400 ms the first
fixture exits 73. The observer holds a pidfd and records actual exit; a timeout
alone cannot supply that fact.

For `disconnect`, the first fixture instead exits 73 at 800 ms, before the lease
deadline. Name loss must render retained generation 4 within 200 ms of observed
exit. It must not wait for expiry or hide/remove the old drawing.

For `ignore-expiry`, only the bridge's timer/operation expiry branch is disabled.
The same live stimuli expose active pixels past the lease deadline and admission
of the late messages. This must fail lease acceptance while capture, native
ownership, marker rendering and original composition remain valid. Disconnect
still works; this control cannot excuse a broken laboratory or missing captures.

After first-child exit and at least 1,000 ms, attach the second fixture and send
heartbeat 0. For 400 ms the old epoch/generation stays visibly retained. Snapshot 1
then establishes the new epoch and active generation 1 within 200 ms. Observe it
for 400 ms; disable the lease adapter and run the original 2,400 ms marker trace.
Its old timer/owner callbacks must no longer alter drawing or leave a badge.

The full exercise is bounded to 9 seconds before the final marker trace. The
existing 40-second overall attempt limit and owned process cleanup remain. Each
fixture accepts at most 32 typed control commands, 4 KiB per command/response and
64 KiB of journal. The observer flushes at most 260 records/12 MiB. Preserve exact
sources, native peer/PID lifetimes, command/receipt timing, raw pixels, all replies,
auxiliary state, failures and cleanup. Do not retry failed measured intervals.

## Completion and remaining work

Require all three source-identical native modes with independently recomputed
outcomes, negative evidence checks, unchanged default desktop regressions and
specification integrity. Native authority and callback behavior derive from the
[GJS D-Bus API](https://gjs.guide/guides/gio/dbus.html); elapsed-time behavior uses
[GLib monotonic time](https://docs.gtk.org/glib/func.timeout_add.html), not an assumed
exact timer schedule. Qualification uses actual recorded gaps and transitions.

Real telemetry, full transport/policy distribution, arbitrary producer admission,
render stalls, editor/native exit, session lock/resume and full host qualification
remain open. Do not claim those from this public-marker native lease experiment.
