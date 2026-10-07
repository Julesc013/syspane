---
type: "SysPane Work Package"
title: "Bounded rendering work and explicit native observations"
description: "Investigate the preserved image-paint and accessibility failures with fixed acceptance."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T22:10:00Z"}
sp_id: "SP-W09-RUNTIME-OBSERVATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-FOCUS-IDLE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded rendering work and explicit native observations

Start from the three failures preserved at 330c977. Do not extend the 100 ms
scene-image paint assertion, three-second native observation deadline, 200 ms
erasure bound, image ceilings or existing worker timeout. Retain exact pixel,
selection, scene, storage, fault-control and actual child-reaping expectations.

## Investigation

Measure maximum-image parent work separately from worker execution: receive/poll,
validation and fitting. Use the current development compiler/runtime and original
asset. Record per-call durations, source and binary identities and exact results.
At most three identical diagnostic trials establish a distribution; successful
reruns alone cannot explain the original failure. A private diagnostic program may
link the existing components but cannot redefine the acceptance oracle.

For binding tab-role and inspector selected-row timeouts, capture the native
object address, owner, interface/method, duration and explicit reply/error. Compare
the convenience call with an explicit read-only wire query if necessary. Preserve
the original failure and do not retry mutations, infer empty/absent state from an
error, force focus or increase observation deadlines. An observation correction
needs independent live/delayed/dead/denied/malformed calibration before use.

## Permitted implementation

Private caching and incremental work are delegated choices. Any image returned
as ready must have its entire bounded input validated, exact dimensions/pixels,
current resource/policy identity and an actually reaped worker. Cancellation,
timeout and failure must discard every pending result. Any reusable validated
image must prevent mutation from invalidating its proof; public raw-image entry
points retain validation. Optimization must preserve exact fit/orientation rules.

Do not add an unbounded synchronous phase to paint or polling. If work is split
across polls, define its per-call byte/pixel ceiling, deadline and pending/reaped
state meaning before implementation. Keep one owner and the existing component
dependency direction. Experimental evidence cannot qualify other platforms.

## Verification and continuation

Freeze original sources, fixtures and assertions first. Verify relevant shared
image tests on affected development profiles, native worker/scene-image cases,
and dependent rendering/erasure/editor checks. Record every attempted command and
failure. Change an oracle only for a demonstrated observation error, preserving
its original failure and unchanged product expectations.

Before launching the full rendering matrix, inspect both owned roots and admit
at least 400 MiB of measured growth within the existing workspace maximum; the
ordinary 64 MiB test reservation alone is insufficient. Reclaim only verified
committed duplicates. Preserve any overrun or stopped preflight. Continue unrelated
work if a laboratory is unavailable; keep unresolved qualification explicit.

W-09/W-10 remain part of the complete five-edition release. This package does not
replace the remaining authoring, installed ownership, native accessibility,
historical laboratory, packaging or release requirements.
