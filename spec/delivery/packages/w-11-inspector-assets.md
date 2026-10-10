---
type: "SysPane Work Package"
title: "Installed inspector image and topology qualification"
description: "Exercise pinned saved images, exact native child ownership and actual monitor changes."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T03:56:11+00:00"}
sp_id: "SP-W11-INSPECTOR-ASSETS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INSTALLED-INSPECTOR", "SP-W09-IMAGE-PIPELINE", "SP-W11-INSPECTOR-TELEMETRY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installed inspector image and topology qualification

Continue W-11 with the ordinary Linux frontend and its installed, verified image
worker. Reuse the installed editor harness, private Xvfb/DBus laboratory and actual
profile owner. No new product executable, protocol or diagnostic admission switch
is required. This qualifies image semantics and logical monitor changes in that
environment; it does not qualify physical hotplug, desktop pixels, human screen
reader use, maximum-input inspector latency or any complete release edition.

## Inputs and fixed behavior

After the ordinary frontend creates and cleanly closes its private profile, the
observer installs a separate coherent revision-zero bootstrap generation. Keep
the original generation. The synthetic generation contains exact settings, scene,
theme/preset/scene manifests, pinned image bytes and resource closure, with a
digest-bound selecting record. It is offline test input, not an acknowledged
product mutation. Verify every selected file against the independently generated
recipe after execution; inspection must not write or create a revision.

Use one essential image widget, primary display, fixed rectangle (20,20,700,32),
700 by 16 DIP content and contain fit. At 800 by 600 it must report the exact title
and public alternative text followed by Image ready. A malformed PNG reports
Image failed (image.decode). The maximum 8-MiB PNG is a valid two-by-two raster
with one CRC-correct inert text chunk; it must finish within the existing job
deadline. An 8-MiB-plus-one asset remains catalog-valid but reports
Image failed (image.capacity). Keep the 8-MiB input, 256-KiB per-poll transfer,
3-second job deadline, raster budgets and 100-ms presentation cadence unchanged.
The frontend may service bounded job progress on its existing 20-ms timer between
presentations. No spinning, synchronous decode or deadline extension is allowed.

Verify open, decode failure, maximum input, over-limit refusal, keyboard summary,
navigation, clean reopen and policy withdrawal. The requested summary is an
explicit snapshot; replacement/withdrawal clears it. On confirmed controller loss,
rows and summary must clear within the existing 200-ms observer limit.

For held navigation and held close, identify the frontend's image child by its
exact arguments and parent, open its pidfd, stop that exact child and confirm its
stopped state while the row says Image loading. Independently hash the parent's
held sealed image descriptor against the relocated installation and check all
four immutable seals. The worker disables dumpability before reading input;
record an unavailable child executable hash honestly. Identity then relies on the
separately qualified sealed-launch contract, rather than a privileged observation.
Then navigate or quit. Completion requires that child's exit and cleared old
inspection; do not substitute elapsed time for actual stop proof. SIGKILL can
terminate a stopped process immediately, so no artificial delayed-reap interval
is required. Preserve failure if the observer cannot establish the hold.

The observer allows the existing 60-second total profile-download contract (plus
two seconds for presentation), not the small default fixture's 12-second wait.
Its 160-second case bound covers two downloads and teardown. This does not extend
any product deadline or the image decoding/erasure limits.

For topology, request a ready summary, then create a named RandR monitor attached
to the private Xvfb output, 400 by 600. Independently confirm RandR and GDK
geometry. The essential 700-DIP widget cannot fit: rows and summary must clear and
the ordinary frontend must report scene/display unavailability. Delete the manual
monitor to restore the automatic 800-by-600 monitor. The same saved profile must
reconstruct ready rows; stale summary must stay empty until requested again.
This is an actual server/GTK monitor transition, not a mocked product callback.

## Execution, authority and completion

Freeze the case table, generation recipe and observer before product edits.
An intentionally incorrect row must fail the same row oracle. Preserve each
attempt's source, fixture, artifact, environment, log and result identities.
Observer repairs must identify their reason and retain original failures; product
repairs retain the original behavior expectations. Ordinary bounded implementation
choices are delegated; privileged deployment and publication remain reserved.

Run workspace preflight, normal configure/build and:

```sh
ctest --preset linux-x64-gcc13 -R '^native[.]INSTALLED-INSPECTOR-ASSETS$' --output-on-failure
```

Run affected native image, inspector, installed consumer and unchanged GUI timing
regressions for any product repair. Run component checks on all development
profiles if build composition changes. Archive each finished native family before
the next workspace reservation. Link the evidence and remaining work from the
existing W-11 row and current-state page; keep W-11 in progress.
