---
type: "SysPane Work Package"
title: "Bounded native editor clipboard"
description: "Explicit authored Copy/Paste with revocable X11 transfers and independent peers."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:00:00+11:00"}
sp_id: "SP-W10-NATIVE-CLIPBOARD"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-SCENE-FRAGMENTS", "SP-W10-NATIVE-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded native editor clipboard

Connect the existing authored fragment and EditorDraft owners to explicit native
Copy/Paste. The first adapter is for the admitted GTK3/X11 development profile.
Other backends remain disabled until their bounded native adapters and independent
tests pass. This is an implementation boundary in W-10, not completion of any of
the five required editions. Do not enable private text field copying as a side effect.

## Observable editor behaviour

Copy requires a nonempty selection and all existing editor.clipboard and sensitive
clipboard permissions. It places only application/vnd.syspane.scene-fragment+json
on CLIPBOARD. Do not claim PRIMARY, export generic text, request SAVE_TARGETS,
persist clipboard bytes or ask a clipboard manager to keep them. X11 TARGETS and
TIMESTAMP expose only protocol metadata, after the same current permission check.

Paste inserts the fragment as roots at the end of the current scene. This initial
native command has an explicit root destination; selecting a group does not change
it to a guessed child destination. Generate one fresh ID per fragment record in
record order through the existing ID allocator. Preserve layout and destination
resources exactly as specified by the shared fragment package. One completed paste
is one undo step; it changes neither accepted revision nor storage until Apply.
Malformed input, a missing pin, a reused ID or failed permission changes nothing.

The toolbar exposes Copy, Paste and Cancel paste. Ctrl+C/Ctrl+V act only when the
canvas or authored object list owns keyboard focus. Private fields keep their own
existing restricted handling. A pending paste disables other draft editing and
submission; Cancel paste and Escape abandon it. No nested blocking clipboard wait
or secondary event loop is allowed. Existing live telemetry/painting may continue.

Policy update (including regrant), disconnect, reload, topology change, close and
request admission synchronously cancel pending paste. All shared snapshot erasure
boundaries relinquish this adapter's offer and abort its outgoing transfers. A late
reply never applies to a newer draft. Policy restoration does not recreate an offer.
Loss of clipboard ownership erases the copied snapshot; it does not clear a foreign
owner. Destroy this adapter's owner window to relinquish ownership atomically,
without a query-then-clear race against another application's claim.

## Native transfer contract

Use an owned X11 connection integrated with the existing GLib loop. Native callbacks
run on the serialized editor owner. Tear down all filters, timers and owned windows
before destroying the callback target. Do not retain a borrowed draft string across
a callback. Reborrow and reauthorize for each outgoing chunk; outgoing slots retain
only destination, offset, declared size and deadlines, not a second payload copy.
Replacing an offer terminates transfers of the previous snapshot.

At most one incoming transfer and eight outgoing incremental transfers coexist.
Each uses a five-second absolute deadline and one-second progress deadline from a
monotonic clock; progress cannot extend the absolute deadline. Duplicate requestor
window/property pairs and exhausted outgoing capacity are refused. Unresponsive or
destroyed peers release their slot. X11 errors from peer windows are handled without
terminating the editor. A live X server is an environment prerequisite; these peer
deadlines do not claim to recover a hung or disconnected display server.

The incoming UTF-8 payload ceiling is 262144 bytes, including whitespace. Accept
direct properties and ICCCM INCR; its size field is only a lower bound. Reject an
advertised lower bound above the ceiling, wrong type/format, malformed INCR header,
oversized direct property, cumulative overflow, changed owner or an incomplete
transfer. Inspect lengths and limit every property read before allocation. Keep at
most 262144 received bytes and bounded Xlib scratch (at most 524289 bytes, accounting
for native-long expansion if a malicious peer races a property format change).
Never delegate arbitrary incoming payload allocation to GtkClipboard request APIs.

Use a fresh receiving window for each paste so old replies cannot target a later
request. Check selection, target, property and request time before accepting its
notification. Delete consumed properties to acknowledge INCR and accept completion
only on its typed empty terminator. No bytes reach scene parsing before complete
bounded transfer and current authority verification. Empty direct content is invalid.

Send at most 16384 payload bytes per outgoing chunk. Larger snapshots use INCR;
the normal typed empty terminator finishes the transfer. Cancellation/revocation
stops future payload chunks and may send an empty terminator to release the peer.
Bytes already delivered cannot be recalled. Ignore unrelated display events and
never alter another application's clipboard selection or unrelated properties.

## Fixed acceptance and evidence

Freeze this package and tests/editor/native-clipboard-cases.json before production
changes. Independent X11 owner/requestor processes must exercise exact copied bytes,
TARGETS without text export, no PRIMARY changes, incoming direct and INCR payloads,
lying and oversize lengths, cumulative overflow, wrong type, malformed fragment,
missing resources, stalled transfers, cancellation and late replies, foreign owner
preservation, ownership loss, repeated policy revocation/regrant, per-chunk outgoing
revocation, destroyed requestors and exhausted/recovered outgoing capacity.

Use real editor actions and native input for copy/paste, verify one-step undo/redo,
and compare complete stored documents and resource bytes after Apply/reopen. Capture
a deliberately wrong fragment/scene witness and ensure exact fixed comparisons
reject it. Preserve every failed run and source/artifact identity. Do not change an
expected result merely to fit the adapter. Run shared fragment/affected portable
checks, all three portable suites and existing editor/visibility/font regressions.

Protocol references: the X Consortium ICCCM selection and INCR sections at
https://xorg.freedesktop.org/archive/X11R7.7/doc/xorg-docs/icccm/icccm.html and
the Xlib XGetWindowProperty contract at
https://www.x.org/releases/X11R7.5/doc/libX11/libX11.html. These describe the native
mechanism; the bounds and permission rules above remain SysPane requirements.
