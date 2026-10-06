---
type: "SysPane Work Package"
title: "Authenticated session demand ownership"
description: "Bind controller-selected acquisition requests to authoritative session lifetimes without changing existing wire documents."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T15:10:00Z"}
sp_id: "SP-W07-SESSION-DEMAND"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W07-DEMAND-OWNER", "SP-W25-SUBSCRIPTIONS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Authenticated session demand ownership

The existing 0.1/0.2 subscription bodies remain fixed. Introduce one reusable
composition of Sessions and DemandOwner, not a second wire/session implementation.
The controller supplies one immutable bounded field/entity/age/priority request
when opening each native-authenticated connection. A peer document cannot change
that request, the catalog, policy or granted authority. External arbitrary selection
still needs a separately negotiated contract; this package does not claim that API.
These requests drive acquisition and are not a replacement for channel disclosure
or a promise that a complete source snapshot contains only requested fields.

Only an admitted active wire subscription acquires a demand lease. Use the session's
negotiated role and native role grants, not the role originally suggested by its
caller or any payload assertion. The requested channel must equal the admitted
subscription channel. DemandOwner enforces fields, scope, capability and policy.
A rejected local plan closes that session and clears queued data before collection
or publication; it must not retain a successful subscription with no authorized work.
Controller requests are bounded before storing them; at most 16 session entries
and the existing demand limits remain in force.

All admission, dequeue, publication, dispatch and completion operations reconcile
session expiry, close state and demand ownership first. Only a newly accepted
heartbeat sequence renews demand; repeated subscribe, duplicate heartbeat, data,
dequeue and polling do not. Clarify the previously unspecified decreasing wire
heartbeat: close with `heartbeat.regressed`, discard queues and retire demand.
Exact duplicate sequences retain their existing no-renewal behavior.

An identical repeated subscribe still rotates the session callback ticket and
requests a full snapshot. It does not extend the demand lease or cancel compatible
in-progress acquisition. An old session ticket is rejected before observing callback
time or payload. A valid shared job may supply a full result to the new ticket after
current-policy checks; actual acquisition time and replay history remain intact.
Different connections' compatible requests merge, and removing one does not remove
another's demand. Disconnect and connection-ID reuse cannot revive an old ticket.

Policy replacement first invalidates shared acquisition, then session state. Any
exception while reconciling admitted sessions or replacing policy leaves both sides
closed or unavailable, with native jobs cancelled but still occupying their slots.
Invalid local open arguments create no entry; a rejected or already closed peer
cannot close another healthy session merely by sending another frame. A later
valid policy does not revive old connections or leases. Stop confirmation remains
available to drain held jobs after faults. No mutable Sessions or DemandOwner escape
the composition, and no callback or worker thread owns its policy or queues.

The Linux collector must consume this adapter in place of parsing heartbeat bodies
and manually mirroring demand. Preserve its real measurements and existing native
recovery/oracle expectations. Fixed portable cases cover negotiated authority,
field/capability/channel rejection, merging and independent release, duplicate and
exact-expiry renewal, decreasing heartbeat, resubscribe/old callback identity,
connection reuse, policy failure/regrant and clock fault with held-job drain.
Build/test the shared adapter on all three development toolsets; historical host
execution is not historical operating-system qualification. Rerun affected native
collector/IPC/continuity cases. W-07/W-25 remain open for installed policy,
invalidation/coalescing, general consumer selection and complete product composition.
