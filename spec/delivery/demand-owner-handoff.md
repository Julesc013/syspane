---
type: "SysPane Work Record"
title: "Shared controller demand ownership checkpoint"
description: "Bounded authorized leases merge into fair source jobs, with cancellation distinct from confirmed stop."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T14:23:41Z"}
sp_id: "SP-DEMAND-OWNER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W07-DEMAND-OWNER", "SP-RELEASE-0-1-0"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Shared controller demand ownership checkpoint

Source baseline: `2e697150799d603958308ae290d5d17bc6cfc715`. Git history identifies
the resulting commit; each build/test attempt retains its original source archive.

The [closed component contract](packages/w-07-demand-owner.md) implements one
serialized typed controller demand owner. Authenticated role/channel policy admits
bounded field/entity/age/priority/recording requests. Compatible requests share source
work; wildcard scope subsumes exact entities without rebinding their identity.
Independent leases preserve recorder demand when a saver leaves. Duplicate heartbeat,
exact expiry, regressed sequence, policy invalidation and fresh regrant have explicit
outcomes. No request grants another channel or native provider permission.

Source cadence and worker caps come from fixed descriptors and applicable forced
settings. The returned plan exposes when a requested maximum age is infeasible.
Priority ages while work remains eligible; deterministic ties prevent equal-priority
starvation. A changed plan invalidates its old job; identical merged demand does not.
Timeout, demand loss and revocation cancel work without releasing its occupied slot.
Only exact completion or stop confirmation allows replacement. Clock regression and
identity exhaustion fault the owner and retain cancelled slots for explicit drain.

Nine fixed demand families and two component dependency checks pass on all three
existing development profiles: Linux GCC 13, Windows GCC 15 and v141_xp/static CRT
on the Windows host. The new historical executable passes the existing PE/header/
mandatory-import closure. These are component and host-toolset results, not Windows
9x, old NT, XP/7 guest, Wayland or Mac execution evidence. No full regression suite
is claimed for this checkpoint; unchanged native components were not requalified.

The initial Linux build rejected a global test named `clock`, which collided with
the standard function. The initial Windows build rejected temporary expected-value
expressions under `-Werror=dangling-pointer`. The tests now use a distinct function
name and explicit literal selection comparisons. Both failures, compiler diagnostics
and source versions are preserved. Warning policy and expected behavior are unchanged.

The first specification-tool run exposed two context-packet tests that assumed the
growing network route would fit 65,000 characters; mandatory content required
65,708. That failed run and the original tests are preserved separately. Fixed small
fixtures now test budgeting, source hashes and whole-file omission independently
of delivery-history size, with an added exact-limit/one-character-short boundary.
The tool still rejects insufficient budgets without truncating mandatory content.
The network-context example now supplies an explicit sufficient budget.

Evidence is indexed in `build-support/evidence/w-07-demand-owner-attempts.json`,
including commands, source archives, target records, executable/library hashes and
the historical import audit. Specification/tooling/integrity results are in
`build-support/evidence/w-07-demand-owner-verification.json`; the source-bound
handoff is `build-support/evidence/demand-owner-handoff.json`.

The user's expanded [0.1.0 objective](release-0.1.0.md) now requires full desktop
releases for Windows 9x, Windows NT, Linux X11, Wayland and Mac OS X. It is recorded
as required scope, not inferred support. Exact legacy floors/architectures and native
labs remain unresolved. Full settings/editing/persistence, providers, qualified hosts,
packages and release authority remain necessary.

W-07 and W-25 remain open. Next connect these leases and exact job/stop identities
to the real collector/controller executor, replacing fixed demand while preserving
existing measured data and recovery behavior. Add native revocation/cancellation/
recorder-independence evidence, then finish event invalidation/coalescing and the
installed session/policy distribution boundary. The current component owns no native
handle or telemetry payload and does not claim native cancellation by itself.
