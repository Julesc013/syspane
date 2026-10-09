---
type: "SysPane Work Package Boundary"
title: "W-11 installed inspector telemetry delivery"
description: "Connect supervised measured network acquisition to the saved-scene inspector."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T02:00:00+11:00"}
sp_id: "SP-W11-INSPECTOR-TELEMETRY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INSTALLED-INSPECTOR", "SP-W25-NETWORK-SERVICE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installed inspector telemetry

Use the ordinary Linux frontend, existing network service, DataView and
SceneInspector. Preserve the four measured fields, native peer checks, original
timestamps, epoch/source identities and independent policy/health/demand owners.
No authored document, telemetry wire version or installed helper is added.

## Ownership and delivery

Inspection requests collection only for the exact currently loaded profile and
only while that inspector is active. Navigation, reload, pending edits, policy
withdrawal and shutdown invalidate that request and its queued payload immediately.
The existing supervisor worker owns a second private runtime directory and a
network-mode supervisor. A separate client worker performs native connection,
framing, clock checks and model validation; GTK performs no native network I/O.
Close waits for both service owners, all clients and existing image/editor work.

The client negotiates telemetry/snapshot/observation 0.2, console role, inspector
channel and operational classification. Profile policy supplies the revision and
requires inspector/accessibility disclosure, telemetry subscription and network
collection. Only an authenticated welcome supplies connection/producer identity.
The client validates complete frames through DataView at their actual native
receipt tick. It never exposes malformed/future-measured snapshots to the UI.

Keep one immutable latest complete frame of at most 1 MiB, plus the existing
bounded model and at most 16 pending frames/2 MiB. A newer accepted complete frame
may replace an older undelivered frame; no delta or partial-table merge is invented.
Each frame retains the original bytes, receipt time and receipt measurement tick.
Queue access carries the exact profile and supervisor generation; stale producers
cannot publish into a replacement profile. No operational payload is logged by
production. Raw test observations stay in ignored private evidence.

Heartbeat receipt renews the native consumer lease for exactly 3000 ms; data does
not renew it. Publish that absolute deadline with the latest independently sampled
native clock. UI delivery time is a distinct event-loop clock: it must not replace
the source measurement or native receipt identity. The UI may validate already
accepted bytes again against a later qualified tick. It must check the absolute
native lease deadline before every delivery/refresh, regardless of its local
DataView lease. A delayed heartbeat cannot extend that deadline. A GUI pause may
resynchronize only from a current complete frame and still-live native lease.

Sample the native clock on the client worker; do not extrapolate nanoseconds from
GUI milliseconds. A clock sample older than 250 ms cannot supply measured age or
admit newly queued data. Retained display then has unknown age. Clock regression,
scope mismatch or peer loss invalidates the clock. Polling and transfer use bounded
native I/O; handshake/connect retains the existing five-second bound.

Batch attachment, full-state import, latest heartbeat and rendering into one
inspector update at its existing 100-ms cadence. An unavailable or disconnected
source retains only previously displayed data while profile policy still permits
it. Replacement requires a full snapshot and a new authenticated binding; original
entity/source epochs are never relabeled. Requested summary and policy clearing
retain their current native ownership rules.

The network service's loop-time policy withdrawal has native exit code 126,
distinct from ordinary crash/protocol failure (125). Its supervisor reports that
held-child result; the frontend invalidates the current profile and reloads through
the configuration owner. This control contains no payload. Startup refusal remains
exit 2. Ordinary configuration-controller loss also erases the inspector under
the existing 200-ms observer deadline. A subsequent grant requires a fresh profile
and connection, never reuse of the revoked queue.

## Fixed acceptance

Before enabling the UI path, freeze concrete queue/lease/clock cases and a native
installed exercise. Assert latest-full coalescing, original frame/receipt identity,
future-measurement refusal, deadline equality, delayed delivery, missing/stale clock,
disconnect retention, changed epoch, obsolete profile and policy erasure. Test the
unchanged installed entry with real counters independently bracketed from the OS,
native rows, navigation/no-background-demand, crash/restart, policy withdrawal and
shutdown. A deliberately wrong expected counter must fail the same oracle.

The older saved-scene inspector cases explicitly cover an absent producer. Preserve
their exact row/input/deadline expectations using a compiled fixture whose network
collection policy is denied by default; the new live exercise explicitly grants
collection. Production has no fixture file or feature switch. Positive and negative
cases must use the same ordinary application entry and delivery implementation.

Run the original installed settings/editor/recovery/inspector, GUI timing/erasure,
native network service/supervisor and affected component tests. Keep failed attempts.
Use ordinary preflight, build and CTest commands; bind actual source/artifact/oracle
identities in a handoff. Protected deployment, maximum-size inspector performance,
other native editions and public release remain separate required gates.

## Executable receiver prerequisite

The [receiver checkpoint](../inspector-telemetry-handoff.md) implements the native
consumer and bounded transfer object. Its actual target is
`syspane_network_consumer`; `syspane_telemetry_delivery` supplies the portable
receiver. Run the ordinary workspace preflight and profile configure/build, then
`ctest --preset <profile> -R '^(delivery|data|measured|telemetry|composition)[.]'
--output-on-failure` on all three development profiles. On Linux also run
`ctest --preset linux-x64-gcc13 -R '^native[.]NETWORK-(CONSUMER|SERVICE|SUPERVISOR)$'
--output-on-failure`. Native tests use the compiled nonprivileged policy fixture
and owned runtime/evidence directories. They do not install production policy.

These runners prove the receiver boundary only. The installed UI cases above are
mandatory before enabling ordinary inspector consumption; a passing receiver
does not complete W-11. Preserve existing service/supervisor, native collector,
demand, helper identity and runtime-directory regression evidence after changing
their shared boundary.
