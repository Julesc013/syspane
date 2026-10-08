---
type: "SysPane Work Package"
title: "Native configuration process supervision"
description: "Own controller startup, absolute watches, exact exit proof and bounded replacement."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T18:57:22+00:00"}
sp_id: "SP-W08-PROFILE-SUPERVISOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-PROFILE-CONTROLLER", "SP-W08-SUPERVISION", "SP-RECOVERY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native configuration process supervision

Implement LinuxProfileSupervisor in source/application. It composes the existing
Child, HealthLink, ProducerLease, TransactionWatch and RestartGate around the real
configuration-host bootstrap. It owns one exact native child at a time. It does not
own the command connection, retry mutations, declare activation or publish a release.

## Inputs and ownership

A trusted native caller supplies the admitted canonical helper ELF, one existing
empty private runtime directory, ProfileLocation, profile creation intent and the
positive console PID. These are native API inputs, never command/session messages,
policy authority or an environment-based executable lookup. Validate pure profile
selection before launch. The caller must resolve and admit installation identity;
the existing Child held-ELF checks alone are not an installation trust mechanism.
Installed lookup, the frontend and native profile projection remain subsequent
integration requirements, not implicit capabilities of this API.

Construct, poll, drain events, inspect and close on one serialized supervisory owner.
Reject calls from other threads and reentry without mutating ownership. Filesystem
setup, launch and cleanup belong off the GUI/event-delivery thread. The caller must
schedule this owner independently of transaction/storage workers, at least every
100 ms. Socket transfers and native wait in poll do not block. Never call a blocking
wait or join on the frontend thread. Close, continue polling until stopped, then
destroy. Misuse destruction retains Child's fail-closed cleanup, not a claim that
an uncooperative kernel operation has stopped.

Require the existing unprivileged native context. Open and exclusively flock the
canonical runtime directory, owned by the current uid, mode 0700, on ext4 or tmpfs.
Its full path is at most 70 bytes. Hold its native identity and reject replacement,
changed permissions, symlinks or initial contents. The caller retains the empty
root; the supervisor creates only g<generation> subdirectories, mode 0700. Use the
existing endpoint basename s and retain the advertised Unix-path limit. Generate
one 128-bit native random owner nonce; each attempt has a new epoch containing that
nonce and a strictly increasing generation. Do not reuse an epoch across owners.

Each child gets only the parent PID argument, a fresh exclusive nonblocking Unix
socketpair on stdin/stdout and bounded stderr. Child supplies exact pidfd ownership,
held executable launch and a clean environment. Close parent copies of child-side
descriptors immediately. Send the existing exact bootstrap, at most 32768 bytes,
before health traffic. The exclusive inherited channel plus held Child authenticates
the parent's child identity; socketpair creator credentials are not evidence that
the peer is the child. The helper independently authenticates its parent as before.

## State, deadlines and limits

The snapshot distinguishes starting, ready, quarantined, waiting, circuit_open,
unavailable, closing and closed. Publish a connectable endpoint only in ready, after
the matching-epoch health handshake and verification of the child's native socket.
Readiness does not attest to policy deployment, desktop activation or visibility.
Retain exact child PID/generation while it is unreaped, including quarantine/close.

The startup deadline is 5000 ms from before native launch. Health readiness never
resets restart counts. Renew the existing producer lease only with valid, ordered
heartbeats; send guardian heartbeats every 1000 ms. Check deadlines before consuming
events and again after I/O. Each transaction.started arms the existing independent
absolute 5000 ms TransactionWatch before transaction.armed is queued. Heartbeats,
finished messages observed at the deadline, queries and later starts cannot extend
that deadline. Wrong epoch, direction, framing or ordering fails closed.

Per poll read at most sixteen 4096-byte guardian chunks and one 1025-byte stderr
chunk. Retain at most 65536 output bytes in addition to the bounded health framer;
use nonblocking partial sends and preserve frame order. Stderr is never disclosed;
more than 1024 bytes in a child lifetime is a fault. Retain at most 64 native events,
reserving four positions for terminal observations. Undrained ordinary events at
the 60-event limit fault and stop the child. Taking events transfers and clears the
queue. Snapshot fault/exit facts remain available independently of event draining.

Any unexpected exit, even zero, or startup/health/watch/channel fault withdraws
readiness and quarantines immediately. Request SIGKILL only through the held Child.
Poll native wait without blocking. No signal result, elapsed stop interval, guardian
EOF or child diagnostic counts as exit proof. Only successful native wait permits
cleanup and RestartGate::confirm_stopped. A still-live child remains quarantined
indefinitely, with no replacement. Use the existing 1/2/4-second backoff, zero
optional jitter and three replacements per 60 seconds; never reset the gate on
readiness. Circuit-open requires a new explicitly admitted supervisor lifetime.

After actual exit, remove only the owned generation directory and its recorded
socket inode. A missing socket is acceptable. A socket not previously observed at
readiness, changed socket/directory identity or unexpected entry blocks cleanup;
preserve it and stop automatic replacement as unavailable. Do not recursively
delete, repair or adopt anything. Verify held root identity/permissions first.

Close is terminal and idempotent. Withdraw the endpoint immediately and cancel
future launches, including waiting/circuit states. A ready healthy child gets a
shutdown frame and up to 2000 ms to exit; if a partial outbound frame cannot safely
be replaced, or the child was already faulty/not ready, stop it directly. At two
seconds request exact SIGKILL and keep polling until native wait succeeds. Closed
means no live owned child; preserve its actual exit code and cleanup failures.
Close never claims a mutation failed to commit or resets the profile's receipts.

## Independent verification

Freeze this package and profile-supervisor-cases.json before production edits.
The native oracle drives a separate C++ supervisor process, observes child lifetimes
through independent pidfds and checks stored files against the existing literal
startup/command expectations. Separate test-only helpers may supply current policy,
hold storage, omit health, corrupt frames or ignore shutdown. No injection enters
the production supervisor or configuration-host executable.

Cover cold startup and real commit; closed-before-launch; wrong-thread refusal;
startup/heartbeat/operation timeouts; matching epoch; malformed health; stderr bound;
unexpected zero exit and fresh epoch; repeated ready failures opening the circuit;
cooperative and forced close; durable lost-result reconciliation with no revision 2;
native policy invalidation; runtime permission/contents refusal; substituted socket
preservation; parent-death termination; and undrained event exhaustion. A deliberately
wrong stored-output oracle must fail. Use fixed timing inequalities with measurement
tolerance for scheduling, never altered product deadlines.

Run native.PROFILE-SUPERVISOR and PROFILE-CONTROLLER, the existing native command/
reconciliation/transaction-supervision families and component graph checks on all
three development profiles. Keep exact source/artifact identities and failures.
Document prerequisites, commands, results and the next installed integration step
in the existing W-08 row and delivery handoff. The full five-edition release scope
and unavailable target qualification remain unchanged.
