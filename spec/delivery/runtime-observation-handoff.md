---
type: "SysPane Work Record"
title: "Image validation cost and native observation checkpoint"
description: "Preserve complete image validation while reducing parent work and retaining unexplained accessibility failures."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T22:23:18.128931+00:00"}
sp_id: "SP-RUNTIME-OBSERVATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-RUNTIME-OBSERVATION", "SP-FOCUS-IDLE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Image validation cost and native observation checkpoint

Source baseline: `330c9772c73928d83a974b051c599190006d60f8`. The
[package](packages/w-09-runtime-observation.md), original sources and acceptance
inputs were frozen before implementation. Existing deadlines, image bounds,
worker ownership, exact pixels, scene/storage outcomes and erasure remain fixed.

## Measured work and implementation

An isolated diagnostic links the existing development components and uses the
original maximum-image fixture. Three baseline trials measured complete pixel
validation at 33.84–34.07 ms and fitting a 32-by-16 output at 34.02–34.12 ms.
The final decoder poll took 35.14–38.53 ms. Parent polling and fitting both validate
the full 2048-by-2048 source, leaving limited margin inside the existing 100 ms
scene-paint assertion. The historical failing paint did not record its individual
phase durations, so its exact timing breakdown remains unknown.

A candidate compiled with the same development flags performs the identical
premultiplied-channel comparisons through a bounded pointer scan. Three trials
measured validation at 4.87–5.10 ms, fit at 4.94–5.12 ms and final polls at
5.97–16.79 ms. Every trial independently checks all decoded and fitted pixels.
The production loop now uses that scan after the existing dimension/length checks.
It still validates every pixel on every raw entry, including all three color
channels against alpha, with the same image.input error. No cache, trusted bypass,
new asynchronous state or acceptance threshold was introduced.

Independent added examples reject invalid first, middle and final pixels in each
color channel at maximum size, through validation, fitting and orientation, without
mutating input. Valid transparent and partially transparent rasters remain accepted.
These examples and the existing image/composition checks passed against the original
implementation before the production edit; the only subsequent source-input
difference is source/scene/image.cpp.

## Executed evidence

All six affected image/composition checks pass on Linux GCC13, Windows GCC15 and
v141_xp. Complete non-native suites pass 312, 309 and 306 checks respectively.
Windows development execution does not qualify historical Windows releases.

All fifteen native rendering checks pass, including the previously failing
scene-image nonblocking-paint assertion and inspector. Native refresh fairness
passes its three load/fault cases, and native binding authoring passes all fifteen
cases. Pixel/geometry, worker lifetime, erasure and current resource/policy checks
retain their existing acceptance. This is scoped evidence for the current sources
and pinned development environment, not full accessibility/performance qualification.

Three binding-selector and three translated-inspector diagnostics trace the original
role/selected-row convenience calls. All six pass, observing 6,252 calls without a
query error. The largest observed call took about 54 ms. The probe would record the
exact native address and make a separate explicit read only after failure, then
rethrow the original error; no failed result can become a successful observation.
The two historical accessibility timeouts remain unexplained. Neither these trials
nor the successful full matrices establish that the image change repaired them.

Records: `build-support/evidence/w-09-runtime-observation-attempts.json`,
`w-09-runtime-observation-native-index.json`, `w-09-runtime-observation-verification.json`,
`w-09-runtime-observation-staging.json` and `build-support/evidence/runtime-observation-handoff.json`.
They retain the frozen inputs, before/after diagnostic executables and measurements,
source archives, original query traces, CTest logs and exact artifact identities.
Original failures remain in the previous committed checkpoint.

The workspace maximum is unchanged. Cleanup verified 28 duplicate native folders
against committed archives before reclaiming 429,208,058 file bytes. The rendering
launch additionally reserved 400 MiB of measured growth; its recorded admission
and ordinary preflights passed. The earlier overrun remains a historical failure.

## Continuation

Preserve the unresolved native role/selected-row failures and use address/method/
reply evidence on recurrence. Do not infer absence, erasure or success from a failed
accessibility call. Continue explicit native observation contracts and remaining
conditional visibility/typography, clipboard/recovery drafts and installed ownership.
W-09/W-10, all five complete editions, historical laboratories and release gates
remain in progress. No public release or privileged action is admitted here.
