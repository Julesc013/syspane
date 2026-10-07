---
type: "SysPane Work Record"
title: "Policy-owned native scene images checkpoint"
description: "Asynchronous pinned image presentation, native erasure and declared-size content hashing."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T00:48:23Z"}
sp_id: "SP-SCENE-IMAGES-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-SCENE-IMAGES", "SP-IMAGE-PIPELINE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-owned native scene images checkpoint

Source baseline: `ab2642454d562704bf5fac9666b4362ef3370b79`. The
[package](packages/w-09-scene-images.md) connects the earlier image pipeline to
SceneSurface. Git history identifies the resulting commit. No existing document
schema or wire identity changes; W-09 and all five complete desktop editions remain open.

SceneSurface now resolves image bytes from the exact immutable package manifest,
path and asset digest. A trusted application supplies the worker path. Identical
references share one decode, with one running/stopping slot, bounded queue/encoded
bytes and a bounded decoded cache. Pending and failed images retain their extent
and expose status; unrelated widgets and chart histories continue updating.

Ready images use exact contain/cover/stretch, premultiplied alpha and rational
display scaling, including fractional binary64 dimensions. The synchronous frame
contains typed image state, source dimensions, asset identity and exact accessible
alt/status text. Policy, scene/resource/topology replacement, disabled display,
close and failed native clearing invalidate caches and queued work. Old results,
including completed but unobserved output, cannot populate a successor. Native hosts
can poll stopping children after close and drain before destroying the UI owner.

The aggregate-input test exposed a pre-existing mismatch: SHA256 accepted only
1 MiB even though content assets admit 16 MiB and image jobs admit 8 MiB. The content
digest entry point now follows the declared asset ceiling, using fixed-block
processing without a padded copy. Document/request hashing retains its 1 MiB cap.
Catalog validation, image-job identity and durable resource write/recovery use the
content entry point. This repairs an implementation limit; no schema limit is raised.

## Evidence and corrections

The evidence index `build-support/evidence/w-09-scene-images-attempts.json` records
commands, exact source snapshots, artifacts and final affected test results. Separate
native archives retain observations and original failures. Fixed Fraction-derived
image pixels remain unchanged. Final affected CTest runs passed 114 cases on Linux,
107 on contemporary Windows and 108 with the historical Windows toolchain on the
modern host. All five external scene-erasure families passed with both deliberate
fault controls. Six native content/configuration families passed; their executable
and oracle hashes match the final artifacts despite the later rendering-only fix.
The 18 historical PE/import audits passed without claiming historical OS execution.
Shared digest expectations independently cover
padding boundaries, 1 MiB+1, 8 MiB and 16 MiB; a real image job carries over 1 MiB of
encoded PNG bytes with unchanged pixels. The native content transaction trace adds
an asset over 1 MiB, removes the import, restarts the controller and verifies exact
durable resource bytes and reconciliation.

Native component cases cover fit/alpha/scale, shared references, queued replacement,
unobserved completion, latched failure, both disclosure channels, resource denial,
regrant, close/reaping, display disable, failed clearing, exact resource identity,
encoded/decoded limits and chart retention during a stalled image job. The owned
Xvfb/GTK/AT-SPI observer compares independent pixels and exact names through all fit
modes, resource replacement, revoke/regrant and stale callbacks. Its deliberate
old-pixel and old-name faults retain the existing 200 ms revocation criterion.

The first fixture used a fixed layout smaller than the existing schema minimum;
the fixture now uses the required 32x16 box around the unchanged 9x5 image raster.
The external observer initially shadowed its image-mode flag, and its replacement
fixture used contain where the fixed expected green rectangle required stretch.
The unobserved-completion fixture initially waited before sending its worker
request; it now performs the nonblocking send before observing child exit. A final
strict-compiler failure corrected the diagnostic string conversion. The capacity
failure path also now preserves closed state if native clearing itself fails, with
a dedicated executable case. Those corrections and failed runs remain preserved.
The digest-limit failure is preserved with its implementation fix. No expected pixel array or
revocation deadline was relaxed. Workspace preflight stops are retained; only
verified archived duplicates were reclaimed under the unchanged 6 GiB allocation.

## Remaining release work

These are owned Linux component windows with public synthetic content, not installed
behind-icons hosting or a complete edition. Installed scene/resource/policy routing,
native editing, full accessibility navigation, localization, performance qualification,
Windows/Mac rendering adapters, target laboratories and release packaging remain.
Continue the existing work graph; preserve unanswered legacy-floor/lab questions
without blocking independent implementation. Public release and privileged operations
still require their corresponding authority.
