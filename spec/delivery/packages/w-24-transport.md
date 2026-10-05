---
type: "SysPane Work Package"
title: "W-24 authenticated transport and policy boundary"
description: "Close the initial local protocol, admission and preview boundary before native integration."
tags: ["delivery", "contracts"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T00:26:58+11:00"}
sp_id: "SP-W24-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WORK-PACKAGES", "SP-TRANSPORT", "SP-POLICY"]
sp_review: "unreviewed"
sp_sources: ["SRC-READINESS-2026-10-05", "SRC-JSON"]
sources: [{"id": "SRC-READINESS-2026-10-05", "resource": "User-supplied readiness review, 2026-10-05", "title": "Implementation closure review"}]
updated: {"by": "codex", "at": "2026-10-06T01:04:36+11:00", "scope": "Native W-24 implementation gate; cross-user/logon and desktop qualification not claimed"}
---

# W-24 authenticated transport and policy boundary

W-01's Windows/Linux model evidence is the prerequisite. The
[campaign admission](../campaign-admission.md) covers ordinary implementation.
W-24's implemented gate requires passing native peer, stream/state and policy
integration checks, including the mandatory cases below. Portable helpers alone do
not satisfy W-24 or release its dependent work. No service, external listener,
elevation, privileged policy installation or release is admitted here.
The [native handoff](../native-transport-handoff.md) records the current development
gate and separates blocked cross-user/logon qualification from executed cases.

## Scope and ownership

Own `source/protocol/`, `source/configuration/`, local stream adapters in
`source/platform/`, the test composition root in `source/application/`, and
`tests/protocol/`. The model remains independent of JSON and native handles.
The controller thread owns connection states, request records, policy revision,
subscriptions and output queues. Callers supply monotonic milliseconds within one
controller epoch; decreasing clock input fails instead of extending a lease.
No concurrent mutation is supported by the initial portable helpers.

The native adapter supplies an authenticated user/session/installation scope and
server-assigned allowed roles. Neither an envelope nor a command can manufacture
this context. Windows uses a private local named pipe, an explicit logon-SID ACL,
remote-client rejection and OS peer identity. Linux uses a private owned directory,
a pathname Unix socket and kernel peer credentials. The initial Linux development
profile also requires the same POSIX session; this is a launched-process experiment,
not proof of a desktop login-session boundary. Close native adapter details and
case bindings before implementing that adapter. Missing historical/Mac labs leave
their qualification blocked independently.

The first enabled command capability is `settings.preview`: validate the eleven
registered `settings.set` descriptors, revision, policy and draft without changing
authored state. `settings.commit`, scene replacement, persistence, real telemetry
subscriptions and surface liveness are not advertised until their owners supply
the necessary integration. A valid but unavailable operation returns `invalid`
with `feature.unsupported`, never accepted/stored/durable. Preview returns
`preview`, the unchanged revision, false stored/durable/visible and no activation.
W-08 will connect the commit boundary to durable publication. Typed ledger tests
may simulate that boundary but cannot attest persistent storage.

## Wire and state contract

Preserve [wire 0.1](../../contracts/transport.md). The frame decoder consumes bytes
incrementally and emits one completed frame at a time. It holds at most one payload
plus four prefix bytes. The five-second incomplete-frame clock starts at the first
prefix byte and is not extended by trickled input. A poisoned decoder never emits
later input; clean EOF closes it, partial EOF is `frame.truncated`. At the exact
deadline it is `frame.timeout`. Unknown/invalid lengths fail before allocation.

JSON has at most 32 nested containers and 16,384 value/key nodes per frame. Reject
duplicate decoded keys (including escaped equivalents), invalid UTF-8, non-finite
numbers, BOM and final LF. The root and body are objects. Errors expose stable safe
codes; parser exception text and rejected values do not cross the boundary.

Envelope members are exactly `type`, `body` for hello; welcome and all subsequent
messages additionally require `connection_id`, `producer_epoch`. IDs use the
existing opaque-ID syntax. The welcome assigns both values; subsequent envelopes
must match them. The producer epoch is the server's epoch, not client authority.
An envelope may not add an approval or policy field. Unknown optional handshake
features are inert; they do not enable extra envelope members or operations.

| Type | Direction and state | Exact body / result |
|---|---|---|
| hello | Client to server, authenticated/unnegotiated only | Handshake 0.1; requested role must be allowed by the native context. |
| welcome | Server to client, once in reply to hello | Handshake 0.1; negotiated minor/frame limit, exact shared document versions and supported features. |
| command | Client to server, negotiated console/desktop/saver_settings | Command 0.2; initial subset is settings preview. Body bytes, not reserialized JSON, define replay identity. |
| result | Server to client, negotiated | Command-result 0.1; identity belongs to the request, with independent storage/activation facts. |
| result.get, cancel | Client to server, negotiated | Exactly `{request_id: ID}`; current policy and authenticated request scope still apply. Unknown retrieval/cancel returns unknown with null facts and reconciliation required. |
| heartbeat | Either direction, negotiated | Exactly `{sequence: uint64-decimal-string}`. Carries health only; surface leases belong to W-25. |
| shutdown | Either direction, negotiated | Exactly `{reason: "normal" | "policy_changed" | "protocol_error" | "resource_limit"}`. Closes this connection, never the controller or OS. |
| gap | Server to client, negotiated | Exactly `{reason: "policy_changed" | "queue_overflow" | "resync_required"}`. Discards incremental state; no data is implied by this control message. |
| subscribe, unsubscribe, snapshot, delta | Feature-gated | Disabled in the initial preview slice; fail closed with `feature.unsupported`. Their versioned body and lifecycle closure is required before advertisement. |

The codec can recognize an envelope without admitting its sender, state or feature.
The connection state machine must perform those additional checks. A second hello,
client result/welcome/gap, wrong connection/epoch or unadvertised feature closes the
connection. A well-framed command rejection returns a bounded result and permits
the connection to continue. Authentication/negotiation failure closes without
revealing policy. No request executes before both succeed.

Handshake fields use the existing schema with semantic checks: no repeated
document/version pair, no duplicate feature IDs and no unknown required feature
on either side. Major 0 must agree; minor and frame limit use the minimum. Required
features must be supported by both peers; only shared optional features activate.
Each exact common document/version pair is retained; no automatic version upgrade.
If there is no shared document version, negotiation fails. Client role grants are
separate from the server's declared role.

## Admission, lifetime and budgets

The ledger is scoped to one controller installation/session/epoch. A native
principal key is an opaque server-owned value. Disconnect never deletes its
records. At most 128 active requests per connection and 128 unfinished plus
unexpired terminal records per principal are admitted. Initial controller limits
are 16 connections, 16 principals and 1,024 total records. Empty principals can be
reclaimed; an unexpired record cannot. The ledger reserves the full 4 KiB result
allowance together with each body before execution, under a global 16 MiB byte
budget. Command bodies are at most 16 KiB; results at most 4 KiB. Scope/connection/
request identifiers are each bounded by the existing 256-byte ASCII ID rule.

An identical in-flight replay reports pending without executing again; an identical
terminal replay returns the recorded result. Reusing an ID with any changed body
byte, including whitespace, conflicts. Terminal expiry is exactly completion time
plus 600 seconds; replay/get do not renew it. Expiry is reclaimed before admission.
Unknown/expired results require journal/revision reconciliation, never blind retry.
The initial preview slice also retains preview request identities in these same
128-record reservations; this conservative tightening prevents previews from
forming an unbounded second cache. Preview/get/replay still recheck current policy.
The scoped changed-body conflict is returned even if the changed setting is invalid;
an unauthorized peer receives denial rather than access to a retained request.
Cancellation before the in-memory commit boundary records a terminal cancelled
result; after that boundary it leaves the committed result intact. Preparation
must recheck current policy and revision immediately before a later W-08 commit.

Each connection has a data queue of 16 frames / 2 MiB and a separately reserved
control queue of 16 frames / 64 KiB. Control precedes data between complete frames;
it cannot bypass a blocked kernel write. Policy revocation clears pending data and
subscriptions before another data dequeue. Data overflow clears queued data and
emits a gap; control overflow closes the connection. Reserve reply capacity before
admitting a command. A write that makes no progress for five seconds closes the
stream; retained results remain available on an authenticated reconnect. The 16
connection bound applies before accepting another parser/input allocation. These
are fixed initial limits, not measured performance claims.

## Policy contract

Use server-owned immutable policy snapshots. An unreadable required policy or
missing native role grant denies restricted operations. Public health remains
available. The preview checker rejects unknown settings, wrong types, duplicate
paths, out-of-range values, forged extra fields and stale policy/config revisions.
Forced values allow only the same value; denied capabilities cannot be restored by
a user command. A preview does not reserve permission for a later commit.

Disclosure is evaluated before serialization and again before dequeue with current
policy. Unknown classification is sensitive; secret data is never projected.
Without an explicit role/channel grant, only public data may pass. Saver defaults
are public. Denied roles and unreadable required policy cannot receive restricted
data. A less restrictive caller-provided policy document has no effect. Revocation
must cancel uncommitted work, clear queued projections and revoke connection demand;
it does not erase committed generations or authorize purging retained files.

## Execution and acceptance

### Native adapter closure

The initial native test composition is `SysPane.IpcProbe`, not a product service.
It runs one connection at a time and at most two sequential clients per invocation;
the portable controller retains its 16-connection bound for later composition.
The one-connection native limit is a declared development-profile tightening.
The listener remains owned across reconnects; an existing endpoint is never removed
or adopted. All native handles/descriptors are non-inheritable and RAII-owned.
No thread mutates a live stream concurrently. Authentication failures close the
stream before a protocol session/subscription or request record exists.

Windows creates a byte-mode named pipe under `\\.\pipe\SysPane.Dev.<case-id>`
with `FILE_FLAG_FIRST_PIPE_INSTANCE`, `PIPE_REJECT_REMOTE_CLIENTS`, one instance,
overlapped I/O, and an explicit protected DACL for the current logon SID. The DACL
grants only individual read/write/synchronize/query rights; client write access
does not include `FILE_CREATE_PIPE_INSTANCE`. The first listener retains the object
and disconnects/reuses it after each client. Client opens request identification
SQOS, never delegation/impersonation authority. The server reads at most the first
frame-prefix byte before identifying the pipe client token, immediately reverts
the thread, and preserves that byte for the frame decoder. Failure to revert or
drain cancelled kernel I/O is fatal to the probe process, not permission to continue
with unsafe token/buffer lifetime. No privilege is enabled or account switched.

Both Windows peers compare OS token user SID, token session ID and authentication
LUID to their own context. Process IDs come from the named-pipe API, not the hello;
a held process handle and identity query bind any expected-process restriction.
Server-side client-token identification also checks the actual pipe security
context, including impersonated client threads. The client verifies the server
process token before writing. Any expected PID is supplied by the trusted launcher,
and requested protocol roles can only narrow that launcher's role grants.

Linux creates an AF_UNIX/SOCK_STREAM socket named `s` in a new private mode-0700
directory under `~/.cache/syspane/ipc-w24/`; the socket is mode 0600 before listen.
The harness owns that bounded directory. Native code verifies ownership, modes,
absolute canonical paths and no final directory/socket symlink. It binds/cleans
relative to a held directory descriptor and removes only the socket inode it
created, never an existing entry. The public endpoint path must fit `sun_path`.
Nonblocking I/O uses poll and MSG_NOSIGNAL, retrying EINTR within the same deadline.
Both peers compare SO_PEERCRED UID and the peer POSIX session to their own. The
current development profile requires SO_PEERPIDFD: keep that peer handle and check
it is live around the session query so a recycled numeric PID cannot authenticate
a different process. Missing support is an explicit unavailable adapter, not a
fallback to caller-supplied credentials. This raises no claim for older Linux.

Connect, accept/authentication and each complete write have absolute five-second
deadlines; writes tighten the stalled-progress rule to a total operation bound.
Read polling is at most 100 ms, and does not reset the frame or handshake clock.
The server preserves connection/first-byte monotonic times through authentication.
The decoder adopts the negotiated frame limit before consuming a coalesced next
prefix. EOF and timeouts close only the current session; principal request records
remain for a later authenticated reconnect within the controller epoch. Windows
cancelled overlapped operations must finish before their buffers/events are freed;
a one-second cancellation-drain guard terminates the probe if the OS fails to drain.
An independent harness imposes a further process deadline and records termination.

The native runner checks an unelevated Windows token or a non-root Linux identity
with no effective capabilities before opening the probe endpoint. This is a
read-only context check; it does not remove, enable or switch privileges.
The native runner launches hidden finite probe processes, uses synthetic commands
only, records exit codes and exact observed replies, and removes only its empty
runtime directory after socket cleanup. It must retain failure logs before cleanup.
NATIVE-01 covers real fragmented/coalesced hello/preview, reconnect/result retrieval
including a client that closes before reading the preview result,
partial EOF, malformed frame, handshake/frame/write timeouts and negotiated bounds.
Its saturation case completes 128 distinct previews, requires the 129th to return
busy, then retrieves/cancels the first retained request and exchanges a heartbeat
without another reservation. Thus native control progress is tested while new
requests are blocked, in addition to testing a stalled kernel writer.
NATIVE-02 covers kernel-derived identity on both peers, endpoint collision without
replacement, expected-process mismatch and protocol role/authority spoof rejection.
Linux additionally launches a same-UID client in a new POSIX session and requires
actual session denial. Windows validates the created DACL and current user/logon/
session checks; another user's/logon session's execution needs its own laboratory
and must remain blocked if unavailable. A synthetic mismatch is not that evidence.
Cross-user/logon and desktop-session qualification must remain separate from the
implemented adapter gate; do not report them passed from same-user tests.

API basis: [Microsoft named-pipe access rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights),
[pipe client identification](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient),
[overlapped cancellation lifetime](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex),
and [Linux Unix-domain sockets](https://man7.org/linux/man-pages/man7/unix.7.html).
These are implementation inputs, not executed SysPane evidence.

Use the existing Windows/Linux development configure/build/CTest commands in the
W-01 package. New cases use the `protocol.` CTest prefix. The model cases must still
pass. The vendored JSON dependency must have a fixed version, upstream identity,
license and verified digest; builds do not fetch it. Register targets and dependency
edges in `build-support/components.json`, and record new source/artifact hashes and
actual case results without overwriting historical W-01 evidence.

| Case | Fixed observable expectation |
|---|---|
| FRAME-01 | Every split of two coalesced frames emits exactly their original bytes once, in order. |
| FRAME-02 | Zero/oversize length fails before payload; EOF in prefix/body fails; poisoned/closed decoders reject further input. |
| FRAME-03 | Start at t=10, trickle at t=5009, tick at t=5010: timeout; a complete frame at t=5009 succeeds. |
| JSON-01 | Escaped duplicate keys, invalid UTF-8, NaN, overflow, BOM, final LF, excess depth/node count are rejected; boundary-depth valid object passes. |
| WIRE-01 | Envelope body byte spans retain internal whitespace exactly; unknown type, forged members and wrong envelope shape fail. |
| NEGOTIATE-01 | Lower minor/frame bound and exact shared versions/features selected; role spoofing, unsupported required feature and no common document fail. |
| IPC-BUDGET-01..04 | Execute the unchanged cases in [acceptance traces](../../assurance/acceptance-traces.md#request-budget-cases), including t=599s busy and t=600s reclaimed. |
| LEDGER-01 | Cancellation before/after simulated commit, scope separation, disconnect, result size reservation, global capacity and decreasing time preserve invariants. |
| POLICY-01 | Preview accepts explicit valid bounds for all eleven descriptors; invalid types/ranges/paths, duplicate settings, forged authority and stale revisions fail atomically. |
| POLICY-02 | Forced setting and denied capability cannot be overridden; unavailable commit returns unsupported with false storage facts; no state changes. |
| DISCLOSURE-01 | Public/operational/sensitive/secret and unknown fields, role/channel boundaries and revocation have fixed expected inclusion results. |
| QUEUE-01 | Data exhaustion emits a gap, controls retain capacity, revocation drops queued data, control exhaustion closes, reply reservation precedes admission. |
| SESSION-01 | Authentication before hello, five-second hello deadline, message direction/state/epoch checks and reconnect request retrieval. |
| NATIVE-01 | Real local client/server exchange on both development profiles with fragmented/coalesced input and bounded disconnect. |
| NATIVE-02 | OS peer identity, endpoint collision, role spoofing and session denial; independently record which cross-user/logon laboratory cases actually ran. |

Portable helper tests close only their own cases. Native and session cases remain
mandatory before declaring W-24 implemented. Qualification on other systems,
subscriptions, persistent commits and GUI behaviour remain separate gates. Preserve
failed runs and consequential assumptions in the source-bound handoff. Private C++
types and parser choice are delegated; changing observable cases requires a recorded
contract change, not editing expected outputs to fit the implementation.
