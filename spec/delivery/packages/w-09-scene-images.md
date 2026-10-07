---
type: "SysPane Work Package"
title: "Policy-owned asynchronous scene images"
description: "Connect immutable image resources, bounded worker lifetime and native pixels to current scene authority."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T00:48:23Z"}
sp_id: "SP-W09-SCENE-IMAGES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-IMAGE-PIPELINE", "SP-W09-NATIVE-CHART"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-owned asynchronous scene images

Enable scene 0.3 image content only through SceneSurface's existing current-policy
owner. Supply a canonical pinned worker executable from trusted application setup,
never from authored documents. An absent worker remains explicit unsupported.
Resolve bytes only from the immutable ResourceSnapshot's selected closure. Match
the exact package id/version/manifest digest, path and asset digest; use its declared
media type. Do not open an authored path or search another package for similar bytes.
The catalog already verified media bytes; retain its immutable owner while queued.

Content hashing and durable resource verification must accept the declared 16 MiB
asset ceiling; retain the existing 1 MiB document/request digest limit separately.
Use fixed-block SHA256 without allocating a second padded media copy. Independently
verify padding boundaries and 1 MiB+1, 8 MiB and 16 MiB inputs, and recover a committed
asset over 1 MiB after its original import is removed and the controller restarts.

## Jobs, generations and budgets

Admit at most 32 image widgets and 32 distinct asset references, with at most 32 MiB
of distinct encoded bytes. Identical references share one decode within a scene.
One worker slot may be running or stopping; queue other assets in canonical pin-key
order. A stopping job retains the slot until actual termination is observed. Every
service call polls it once; it never waits for completion. Repeated paints do not
restart successful, failed or pending jobs. A failure remains latched until explicit
scene/resource replacement or a newer policy generation. No automatic retry storm.

Decoded cache pixels total at most 4194304. One active worker independently reserves
another 4194304 possible result pixels; its bounded encoded/reply buffers remain
subject to the pipeline limits. Reject a result that would exceed the cache limit,
without evicting another image or showing partial decoded bytes. The cache limit is
a whole-scene capacity alternative, with jobs cancelled and all image pixels erased.
The existing 8388608 scene construction-pixel budget covers display and fitted leaf
rasters; decoded cache and active-result reservations are additional named budgets.
This bounds logical payloads, not allocator or native-library overhead.

Policy changes (including regrant), scene/resource/topology replacement, disabled
display, close, clock faults and failed native clearing erase decoded caches and
invalidate all queued/result identities synchronously. Cancel the active job while
retaining its stop ownership. No old completion can populate a successor scene,
even if a widget id or asset reference repeats. Regrant may start a fresh decode of
still-authorized immutable authored content; it cannot reuse revoked decoded pixels.
Telemetry histories keep their existing reset rules and continue receiving while
an image is pending. Ordinary paint or telemetry callbacks do not cancel image jobs.

Expose nonblocking image-job polling so a native host can finish stopping children
after close before destroying its UI owner. Destruction retains Child's bounded
stop/reap-or-fatal fallback; normal rendering and shutdown integration must drain
first. Do not create a background owner with hidden process lifetime.

## Presentation

Use ceil(width_dip*scale) by ceil(height_dip*scale) as the image raster's minimum
and preferred size, using the exact finite binary64 authored dimension and rational
display scale without intermediate rounding. The authored layout box remains separate
and may be larger. Reject axes over 2048 or existing construction-budget overflow.
Keep this same extent while queued, decoding, ready or failed. Successful images use
the exact premultiplied contain/cover/stretch algorithm and existing scene OVER.
No theme background is added to a successful raster; transparent pixels stay clear.

Pending images show a one-device-pixel muted outline of that extent. Failed images
show the same outline in error color plus its two corner-to-corner diagonals using
the chart package's round-half-up discrete line rule. Apply each pixel's color once.
High contrast uses the effective foreground for these indicators. These shapes and
the accessible status distinguish unavailable content from a successful blank image.

The accessible string is exactly alt, newline, then `Image ready`, `Image loading`
or `Image failed (CODE)` using the bounded public worker/owner error code. The image
has no rendered caption. Preserve typed state, asset pin and source dimensions in
the synchronous frame, subject to its existing text/identity budget. Pending/failed
images make an otherwise usable frame degraded; other widgets still paint and chart
histories remain intact. Whole-scene authorization, resource, capacity and layout
failures continue selecting the established restricted/alternative outcome without
pixels, alt content or retained caches. Publication rechecks current authority.

## Fixed acceptance

Before implementation, preserve resource fixtures and independently specified pixel
and accessibility expectations. Exercise real decoder jobs for fit, alpha, scale,
shared assets and exact resource identity; controlled workers for pending replacement,
cancellation, late completion, failure latching and actual reaping. Prove that a pending
image does not erase chart history. Cover both disclosure channels, resource capability
denial, regrant, display disable, close, native-clear failure and aggregate limits.

Extend the owned Xvfb/GTK/AT-SPI experiment with fixed image pixels derived independently
from input samples, not the production renderer. Keep the existing 200 ms revocation
bound and separate deliberate old-pixel and old-name fault controls. Decode completion
may take up to its existing three-second deadline; do not use that deadline to relax
revocation. Record source, worker, oracle and runtime identities and preserve failures.
This qualifies the component in the owned Linux lab, not installed behind-icons hosting,
Windows/Mac image adapters or a full release. Continue those gates in the existing graph.
