---
type: "SysPane Work Package Boundary"
title: "W-25 native GJS measured network consumer"
description: "Reuse the protocol, revocable data owner and measured network projection in the native shell process."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T08:00:00Z"}
sp_id: "SP-W25-GJS-NETWORK-VIEW"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-GNOME-CLOCK", "SP-W25-NETWORK-PRESENTATION", "SP-W25-DATA-VIEW"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 native GJS measured network consumer

Implement NetworkView in the existing SysPaneClock-0.1 native module, using the
shared Framer, telemetry decoder, DataView and network projection. GJS must not
define a second freshness or model implementation. This native consumer is a
prerequisite for operational live drawing; standalone synthetic evidence alone
does not enable or qualify operational network freshness on the desktop.

## Owned interface

`NetworkView.new_from_socket(fd, expected_pid, revision, permit)` duplicates and
authenticates the borrowed nonblocking connected Unix stream with the existing
native UID, held PID, POSIX-session and measurement-clock provenance checks.
The caller is the trusted serialized desktop owner. It supplies the current typed
development policy explicitly; peer JSON cannot grant authority. Revision is a
nonzero canonical uint64 string. This interface does not qualify installed policy.

The object owns one native stream, one bounded decoder and one revocable DataView;
it never performs a blocking read/write. GJS uses the original GIO socket for
asynchronous transport. `hello()` returns the existing framed telemetry 0.2 hello
as GLib.Bytes. `feed(bytes)` admits at most 16 KiB per call and at most 16 complete
messages per call, reusing the 1 MiB frame ceiling and incomplete-frame deadline.
The regular `project()` call also advances the decoder deadline and producer lease.
Welcome must complete within five seconds of object admission; both feed and
projection enforce that deadline, including a peer that sends no bytes.

One welcome must precede data, with console producer role, matching body/envelope
epoch, a valid connection ID and the existing required snapshot/measured-time
features and 0.2 document versions. Native sampling supplies the local clock scope;
it never comes from a wire string. Bind producer `producer:network`, subscription
`S`, desktop/operational disclosure and the admitted policy revision. The bridge
uses the negotiated frame ceiling before accepting later messages.

Snapshot/delta import uses the shared measured DataView. Heartbeats must have the
bound connection/epoch and renew only the producer lease; duplicate heartbeats do
not renew it. A gap marks snapshot-required without changing the last sample.
Shutdown disconnects the data owner. Unknown/directional messages, malformed
frames, a wrong envelope, invalid/future samples, replay conflicts or native clock
failure close the object and discard its payload. Public errors are fixed codes;
never include peer text in errors. Valid duplicate publication preserves age.

`policy(revision, permit)` rejects lower/conflicting revisions without mutation;
an identical revision/decision is duplicate. A new revision drops all native model
payload before returning. Regrant cannot revive the old binding: the old connection
cannot provide a fresh full for a new policy revision. Start a newly admitted owner
and negotiate a new source session instead. Policy denial precedes payload decode
and projection. JS must separately erase its native actors before acknowledging
visible-cache policy changes; the C++ return alone is not pixel erasure evidence.

`project()` invokes the shared measured network projection for the exact producer,
welcome epoch and explicit `network:interface:1` laboratory selection. It returns
one bounded process-local JSON projection, not a new transport schema. Preserve
all four values, original measured tick/UTC/interval, support, acquisition, presence,
origin, reported/effective freshness, error code and independent lease state/reason.
Represent uint64 counts/times as decimal strings. Scope provenance remains internal;
do not export it. No-payload results contain no identities or fields. Output is at
most 16 KiB; capacity failure never exposes a partial frame. Retention of returned
JSON is allowed only in the separately admitted bounded native cache/private test
sink, under the same current-policy erasure obligation.

`shutdown()` produces the existing bound normal-shutdown frame for asynchronous
delivery by GJS. `close()` is idempotent and releases all model/socket resources;
finalization also closes. Closed/faulted objects cannot reopen. A peer exit removes
measurement authority; do not silently reuse an earlier qualified clock sample.

## Fixed first acceptance and next integration

Use a standalone GJS client and one held same-session synthetic peer. Independently
bracket its native timestamps and verify exact counter strings, null first rates,
current-to-stale progression at the original three-second TTL, immutable replay
age, failed-acquisition metadata, lease expiry independent of measurement age, retained state after a gap,
revocation/regrant emptiness and final native resource release. Invalid sockets,
wrong expected PID, wrong epoch, future tick, replay conflict and malformed frame
must fail closed. Check negotiated frame limits, directional welcome rejection,
the empty-peer handshake deadline and the partial-frame deadline separately.
Bind exact source, library/typelib and runtime identities; preserve every failure.
Run the existing native clock and relevant portable/build regression checks.

Then connect actual native CollectorProbe delivery through this same owner. Its
present retained relay waits for collector exit and must not be relabelled live.
The live experiment must keep the supervised producer and authenticated forwarding
owner alive while the original sample ages, preserve native namespace/epoch
provenance across every hop, forward original messages unchanged and reuse this
native projection in the shell. Close the forwarding/teardown contract before that
implementation. Require independently decoded actual values and displayed age/
expiry, negative frozen-age/ignored-expiry controls, policy erasure, heartbeat loss
and actual native exit. The existing retained-cache and public-clock oracles stay
intact. Native suspend, installed policy and full product recovery remain open.
