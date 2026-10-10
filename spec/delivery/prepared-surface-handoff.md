---
type: "SysPane Handoff"
title: "Prepared authored snapshots for native editor previews"
description: "Measured preview admission repair with preserved native and portable evidence."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T03:16:44.963078+00:00"}
sp_id: "SP-PREPARED-SURFACE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-PREPARED-SURFACE", "SP-INSTALLED-TELEMETRY-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Prepared authored snapshots for native editor previews

Initial editor, undo/redo and recovery preparation now create an opaque,
fully validated authored snapshot on their existing workers. The current draft
adopts it with the exact candidate after the existing ownership and policy checks.
Editor previews can share this immutable structural owner. Selection preserves
it; edits, requests, policy changes, disconnect, reload, discard and close release
it. Detached preparation does not inherit a cached proof.

SurfaceConfig accepts one authored source: raw documents or a validated snapshot.
Mixed sources fail, including identical documents. A moved-from snapshot fails.
The prepared path still checks current resource binding, topology, text setup,
capabilities and policy. It keeps existing rendering, image lifetime, telemetry,
visibility and erasure behavior. Preview inputs without a prepared snapshot use
the original validation path. This does not cache permission or rendered frames.

The pre-change diagnostic measured raw surface construction at 42.304 ms for
MAX-WIDGETS and 38.565 ms for MAX-SCENE. In the post-change diagnostic, raw and
prepared construction measured 29.819 versus 5.438 ms and 38.858 versus 5.910 ms.
Creating the immutable proof took 19.478/28.739 ms, now assigned to the preparation
worker in the editor path. These are single diagnostic observations, not general
speed guarantees. MAX-WIDGETS remains degraded and MAX-SCENE remains an explicit
alternative in that diagnostic; an alternative is not successful scene rendering.

The subsequent ordinary RECOVERY-GUI-LIMITS run passes all seven unchanged cases.
MAX-WIDGETS measured 50.179 ms maximum delay and 43.329 ms maximum work;
MAX-RECORD measured 56.118/43.575 ms. The limit remains 100 ms. Policy erasure
measured 112.003 ms against 200 ms. Preserve the earlier 110.421-ms delay and
116.786-ms work failures in the installed telemetry checkpoint. This repair
removes a measured GUI cost; it does not retroactively establish every source of
contention in those earlier attempts.

## Oracle review

The original frozen new native test incorrectly expected a degraded surface for
one readable widget with a Waiting telemetry label. The existing surface contract
distinguishes layout status from source availability. The unchanged raw path
returned ready with a frame, consistent with that contract. The expectation was
corrected to exact ready on both raw and prepared paths. Literal Waiting text,
exact native pixel equality, rejection codes and policy erasure remain required.
Both failed attempts, the original frozen file and the correction rationale are
preserved. No original acceptance oracle was changed to fit the implementation.

The portable snapshot case passes exact adoption/history contents, selection,
mutation, stale preparation, disconnect, close and policy-loss assertions. Native
prepared-surface checks pass identical pixels, caller isolation, mixed sources,
moved-from owners, invalid topology/resource binding, failed replacement and
current-policy erasure.

## Evidence and continuation

Each of the Linux GCC 13, Windows GCC 15 and Windows v141_xp development profiles
passes 354 selected portable checks. The historical Windows profile also passes
both PE/import checks on this host.
The native regression run passes 253 named cases across 27 report families,
including the seven ordinary GUI cases, plus seven direct native CTest cases.
The separate preview-cost diagnostics are not counted as qualification cases.

The DevelopmentFrontend smoke install passes with exactly five files, matching
built, archived and relocated bytes. Its production network entry refuses the
local fixture grant with exit 2. The unchanged 8-GiB active-output cap admits a
223168492-byte package reservation: two full payload copies plus 1 MiB for archive
and observer overhead. Relocation is a same-filesystem rename, and the refusal
observer executes the relocated helper directly. No third payload copy is made.

Specification validation passes 51 schemas and 183 fixtures. The tooling suite
reports 62 tests: 60 passed and two existing Windows symlink-privilege skips.

The [checkpoint](checkpoints/prepared-surface.json) records exact commands, source archives, build artifacts, pinned
development profiles, native observations and retained failures. Raw recordings
remain in owned ignored out/evidence roots; they are not checkout dependencies.

W-11 remains in progress. Continue installed image and display-topology cases,
maximum-input inspector responsiveness and human accessibility, then compose the
verified owners with the actual desktop host and lifecycle. Extend the existing
installed inspector harness with authenticated image-resource fixtures and
independently observed monitor changes; its current fixed-row cases do not prove
those boundaries. Preserve independent
recovery and the behind-icons/reveal oracle. Windows 9x, Windows NT, Linux X11,
Wayland and Mac OS X still require complete native editions and release evidence.
Development toolchain success does not qualify historical OS execution. Positive
native policy remains an unprivileged compiled fixture; no protected deployment,
signing or public release is performed.
