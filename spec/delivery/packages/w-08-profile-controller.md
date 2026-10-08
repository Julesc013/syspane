---
type: "SysPane Work Package"
title: "Supervised native profile controller entry"
description: "Authenticate startup, keep native policy current at disclosure and retain transaction recovery."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T06:00:00+11:00"}
sp_id: "SP-W08-PROFILE-CONTROLLER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-PROFILE-WORKER", "SP-W08-SUPERVISION", "SP-POLICY", "SP-ARTIFACTS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Supervised native profile controller entry

Implement the Linux profile/command process entry in source/application. Its
private helper basename is syspane-configuration-host; it is not the syspane
controller/inspector frontend or a complete desktop edition. Use LinuxProfileWorker,
AsyncCommands, Sessions, native local IPC, parent lifetime and HealthLink with the
existing transaction-watch profile. No test waits, fixture policy arguments or
finite campaign deadlines enter the production entry point.

## Authenticated startup

The helper accepts exactly one argument: the positive canonical parent PID. Require
the existing unprivileged native context, arm the parent-death signal and close
the held-executable descriptor 3 before other work. Descriptor 0 must be a connected
nonblocking native Unix stream inherited only from that parent. Duplicate and verify
it through Stream::from_connected_socket, including peer user/session and the held
native peer identity. Standard output is the same private channel; diagnostics on
stderr contain only a fixed non-sensitive failure code.

Before the health handshake, read exactly one four-byte-length-prefixed JSON
bootstrap frame, at most 32768 bytes, within the existing five-second startup
deadline. Reject incomplete, multiple, trailing, malformed and unknown fields.
The object has exactly these fields:

| Field | Meaning |
|---|---|
| format | Literal SysPane.ProfileController |
| schema_version | Literal 0.1.0 |
| producer_epoch | Existing identifier grammar; immutable for this child |
| client_pid | Positive canonical uint64 decimal string; exact admitted console peer |
| endpoint | Existing private native listener path contract |
| create | Boolean profile creation intent; never policy authority |
| profile | Exact object: id, home, config_home, data_home, state_home, portable_root |

Profile id uses existing identifier rules. The five location strings use the
existing ProfileLocation contract; portable_root is null or a string. No cwd,
environment policy override, caller policy document or arbitrary helper path is
accepted. A trusted parent resolves XDG/portable selection and installation identity
before launch. The bootstrap carries location, identity and intent, not permissions.
Parent-side launch/restart ownership remains the existing exact Child/restart-gate
contract; the independent native oracle may implement the parent separately.

Create the profile worker with fixed machine_policy by default and the existing
six capabilities for selectors, content, edit locks, visibility, typography and theme
overrides. Capture the first native effective Policy as the immutable baseline;
normal store verification continues through LinuxProfileStore. Construct the command
owner and receipt snapshot before starting its session loop. No imports are inferred
from cwd or test catalogs. Initial/retained resources resolve through the store.

Only after coherent profile startup create the private client listener and start
the existing console-role health handshake. Require the negotiated epoch to equal
the bootstrap epoch. Do not accept client traffic before that handshake completes.
No visibility or activation is inferred from readiness. The parent's five-second
startup deadline covers native initialization; a blocked startup cannot be rescued
by an unqualified ready claim.

## Loop, native policy and independent deadlines

One serialized loop owns Sessions, the authenticated client stream, framing,
connection lifetime, request ledger and output. Admit only the exact configured
console PID in the same native user/session. Reconnect can replace a disconnected
connection, retaining admitted work and original-epoch receipt semantics. A wrong
peer, malformed frame or saturated input closes that peer, not the profile owner.
Bound pending decoded input to eight frames and 2 MiB, in addition to the existing
1 MiB framer and Sessions bounds. Disconnect clears those bytes. Limit each output
batch to four existing control frames; each native write retains its 100 ms bound.

Run native policy sampling on a separate joined worker, never the session loop.
Refresh before dispatching queued application frames or releasing command results,
and at least once per second while idle. Compare availability, revision, forced
values, denied capabilities and disclosure against the captured baseline. A throw,
unavailable snapshot or any semantic change invalidates command admission and exits
the child without sending queued results. Same-revision drift also invalidates.
A new policy requires a fresh controller lifetime and producer epoch. A sample is
consumed by one bounded dispatch/output batch; it is not an indefinitely cached
permission. Native publication guards independently read current policy as before.

Every policy-only batch and transaction batch is armed through transaction-watch
before starting its native work. Watch tickets are a monotonic controller counter,
distinct from command request IDs and AsyncCommands dispatch tickets. One watch is
active. During a command watch, policy refreshes for queries/cancellation/output
share that same absolute deadline; they never renew it. Finish the watch only after
all of its native threads have been joined and its authorized output batch finished.
Take the next queued transaction after that boundary. Policy-only work cannot hang
indefinitely while healthy heartbeats conceal it.

The existing supervisor arms an absolute 5000 ms watch before replying armed.
Heartbeats, query activity and policy refresh do not extend it. On fault it
quarantines, stops the exact child and waits for native exit before replacement,
with existing bounded restart/circuit rules. The controller continues independent
guardian heartbeats while native threads block. Guardian loss/expiry exits without
joining an uncooperative thread. Never terminate an individual C++ thread.

Actual command thread join still precedes AsyncCommands::finish. Expose its latched
storage-fault state read-only to the native composition: indeterminate storage
requires process replacement and a fresh native open, not another mutation in the
same owner. Do not replay on restart. Existing durability/activation and current
result-disclosure semantics remain unchanged.

## Stop and errors

A guardian shutdown invalidates admission, drops client disclosure and allows up
to two seconds for cooperative workers to stop. Join completed workers, close the
profile worker off the UI loop and return zero only after normal closure. A blocked
shutdown exits the whole child with code 125; it asserts no cancellation or
non-commit. Guardian loss returns process code 124 through immediate process exit;
policy invalidation uses 126; other active-loop faults use 125. Invalid startup
returns 2 with a fixed diagnostic. Actual process wait is still required for any
stop claim; kernel-delayed exit is not overridden by these return conventions.

The production main exposes no injection. A separate native test executable may
call the same process-entry function with a trusted thread-safe PolicySource and
transition observer. Its file-controlled fixtures are test inputs, not protected
policy provenance or a product command surface.

## Fixed acceptance and continuation

Freeze this package and profile-controller-cases.json before implementation.
An independent native parent speaks bootstrap/health framing, holds the child by
pidfd, enforces startup/watch deadlines and proves actual exit. A separate client
authenticates on the ordinary Unix endpoint and validates existing message schemas.
Compare files against the earlier literal startup defaults/commands, never child
success logs. Preserve wrong-output/deadline controls and failed runs.

Cover exact cold startup, default native policy refusal, invalid bootstrap/parent,
no work before arm, responsive heartbeat/cancel during held storage, sequential
commits and replay, reconnect, policy changes before disclosure, same-revision
drift, held policy deadlines, post-durable lost results and new-epoch reconciliation,
guardian loss, cooperative shutdown, blocked shutdown and foreign client refusal.
Run the new native family, profile/command/reconciliation/supervision regressions,
shared command tests and all component graphs with exact source/artifact identities.

Next integrate the private process with the real controller frontend and verified
installation lookup, native profile projection/settings/editor startup, telemetry,
import catalog and packaging. Positive protected-policy deployment remains
unqualified in this lab. Complete native lifecycle, all five editions and the
original release gates remain required; a command helper is not a desktop release.
