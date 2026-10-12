---
type: "SysPane Work Package Boundary"
title: "Bounded native inspector retirement owner"
description: "Clear data immediately and preserve every original native notification through explicitly polled ownership."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T01:45:00+00:00"}
sp_id: "SP-W11-NATIVE-RETIREMENT-OWNER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-GTK-CELL-LIFETIME", "SP-W11-BACKGROUND-INSPECTOR", "SP-ACCESSIBILITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded native inspector retirement owner

Continue W-11 from eff857c4. The preceding synchronous FIFO proves immediate
cache erasure and valid late original calls while the window/root is owned. It
does not qualify asynchronous lifetime/shutdown or any GUI limit. Preserve every
source-bound failure and the original 100-ms GUI/200-ms erasure limits.

## Ownership and calls

One GTK-thread retirement owner is shared by the two inspector text renderers.
Each renderer retains that owner through GObject-owned internal data; no global
scene pointer, copied row cache or competing work scheduler is introduced. A
retired cell's text/name/count/layout is physically cleared before returning
from its unset hook. Retain its exact original inherited-unset call, then its
widget-property dispatch call, in a FIFO. Nonretirement/creation/property calls
continue synchronously. Preserve each original argument and every parameter
specification; invoke once in order without coalescing or dropping an event.

Each queued operation strongly owns the cell, its exact accessible parent/root
and referenced parameter specifications until invocation and cleanup. Original
class slots are immutable captured parent operations. GTK/bridge remains enabled.
There is no idle source or retained borrowed observer: explicit refresh/delivery,
policy/replacement/close boundaries and poll_image_jobs own measured drainage.
Borrowed phase observers remain synchronous and are never stored in the owner.

Poll at most 256 operations or 5000 us, stopping after the current operation.
Record complete poll count/elapsed/max and accepted/delivered/pending counts;
one unpreemptible slow callback remains a recorded failure, never an excluded
sample. All actual work stays within an existing measured GUI call. Do not
interpret total drainage as a single callback or omit it from evidence.

The projection admits at most 65536 rows, two native cells per row and two
retirement operations per cell. Queue at most 262144 operations, parameter arrays
at most 8, and enforce a 128-byte operation-size ceiling (32 MiB maximum fixed
operation storage plus declared container/reference overhead). Allocate lazily;
this is bounded native notification ownership, not changed frame/model limits.
Capacity/allocation/thread failure records owner failure and forwards the affected
original call synchronously rather than dropping it; it cannot become successful
qualification. No privileged operation or product resource limit is relaxed.

## Adoption, interaction and closure

Physically empty native rows/summary/selection before deferred notifications.
Pause new nonempty row adoption while retirement remains pending; keep the bounded
renderer result owned by its existing producer until it can be taken and checked
against current profile/policy/source/topology/clocks. A rapid regrant does not
rebind old cells or acknowledge an unadopted result. Partial active updates retain
their existing semantics. Native expand/collapse admission may refuse additional
structural changes while old retirement is pending, preventing repeated native
cell creation from evading the bound; selection/ordinary data handling is retained.
Internal expansion within the current admitted presentation batch retains the
existing partial-update behavior even when that batch retires old cells. This
does not admit a new nonempty result while a prior batch's retirement is pending.

Drain a bounded slice at public operation boundaries, including native collapse
completion when outside an existing batch. Small existing lifetime cases can
complete in that slice; large scopes retain truthful pending ownership. Explicit
close erases data and requests producer/renderer closure. poll_image_jobs returns
true only after image/renderer and native retirement have actually drained.
Frontend replacement/destruction retains its existing close/poll protocol.

Destructor teardown must never abandon an original call or leave borrowed data.
After close, synchronous terminal cleanup drains any remaining operations before
widget/reference destruction; normal GUI callers must first use close/poll.
Record unexpected terminal-cleanup duration rather than claiming bounded GUI
qualification for destruction that bypasses that protocol. Forced parent/widget
destruction retains saved accessible roots until queued original calls finish.
No stopped/closed completion record precedes actual drainage.

## Acceptance before qualification

Verify actual held cells with the bridge enabled: data empty immediately, normal
defunct once after drainage, precise supported replies/verified withdrawal, active
and fresh rows unchanged, no old-path reuse, FIFO and owned-reference cleanup.
Include rapid revoke/regrant, two independent owners, pending close, parent
destruction and current-policy rejection before late adoption. Preserve fixed
oracles; any legitimate deferred event completion is explicitly polled, not an
arbitrary sleep or invented pass.

Run ordinary configure/build/graph, real native lifetime/model/renderer/background/
frame/erasure, installed/table and maximum history suites. Every queued GUI slice
must be covered by actual caller timing, with total work/pending/actual stop also
recorded. No unavailable native laboratory is inferred as support. W-11 and full
Windows 9x, Windows NT, X11, Wayland and Mac OS X release gates remain required.
