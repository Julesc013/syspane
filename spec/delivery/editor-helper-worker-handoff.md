---
type: "SysPane Handoff"
title: "Native editor helper worker bridge"
description: "Bounded GUI task handles, independently owned native helpers and exact consumer results."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T23:18:00+00:00"}
sp_id: "SP-EDITOR-HELPER-WORKER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-EDITOR-HELPER-WORKER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native editor helper worker bridge

EditorHelperClient owns GUI task handles and trusted factories. LinuxEditorHelperOwner
uses the existing shared installation on one separate serialized native worker;
it creates no thread. Only this owner constructs, polls and destroys ImageJob and
LinuxRecoveryQueue. Installation verification, hashing, native I/O and child
supervision occur outside the shared mutex and outside GUI calls.

ImageTask and RecoveryTask preserve the original native owner interfaces. SceneImages,
SceneSurface, EditorForm and EditorRecoverySession accept the factories while keeping
their path-based experimental callers. EditorForm shutdown now awaits both image
and recovery work. Factory possession grants no policy or storage authority.

Four retained image handles share two active native jobs in admission order. A
cancelled or abandoned task retains its slot until native closure is acknowledged.
Cancellation immediately erases queued input and deliverable pixels; native exit
must precede reaped status. One recovery handle owns an immutable context, consumes
load before admitting writes, coalesces pending captures, translates public/native
tickets and fences retirement behind active work. Client closure refuses admission,
erases deliverable data and drains exact children before reporting stopped.

## Evidence and limits

All 21 fixed EDITOR-HELPER-WORKER cases pass using a relocated five-file development
payload and actual sealed production helpers. The independent observer checks
PNG/JPEG/SVG pixels, recovery file bytes and exact child identity/exit through pidfds.
It holds children at kernel exec stops before worker instructions, with no production
pause hooks. Cases cover GUI work while pumping is held, queued/active cancellation,
capacity including abandoned slots, FIFO/concurrency, result erasure, recovery
coalescing/retirement/denial, context/client closure, installation changes and
wrong-thread access. Incorrect pixel/file expectations are independently rejected.

The real SceneSurface produces the pre-existing literal fitted-image raster through
the factory. EditorRecoverySession offers the pre-existing recovery record and
restores its exact scene as one undoable edit. Factory decorators time the actual
task calls made by these consumers, including construction, polling, consumption,
cancellation and destruction, under the fixed 100 ms development bound. Complete
consumer timings are recorded separately: document validation and rasterization
also run in those calls. This does not qualify whole-editor responsiveness.

The successful run records 453 task calls with a maximum of 55 microseconds.
Full recovery-offer processing took 169311 microseconds and Restore took 368741
microseconds; those observations remain integration work, not a passing UI budget.
Existing IMAGE-JOB, RECOVERY-QUEUE, EDITOR-RECOVERY, EDITOR-FORM, IMAGE-ERASURE,
SCENE-IMAGE and INSTALLED-SETTINGS regressions also pass. Six recorded native
families contain 101 named cases; IMAGE-JOB and SCENE-IMAGE have separate C++
CTest evidence.
All six component graph checks pass across Linux GCC13, Windows GCC15 and Windows
v141_xp. These graph checks do not execute historical guests.

The [checkpoint](checkpoints/editor-helper-worker.json) records all commands, frozen
inputs, source snapshots, built artifacts, native archives and regression outcomes.
Raw evidence and machine bindings remain under ignored out/. Completed owned
recordings were archived and byte/node verified before duplicate reclamation;
the original workspace ceiling and reservations remain unchanged.

## Preserved failures

The first probe build exposed a missing explicit dependency for the existing image
fixture's network publication header. Its component dependency was added. The first
native observer injected a stop signal at a non-signal-delivery exec event; this did
not hold the workers. That assertion and the subsequent trace-cleanup failure remain
in their source-bound CTest record. The observer now retains and verifies exec stops,
drains every traced thread during cleanup and persists observations before assertions.
The test host initializes synchronization state before launching its thread.

The next run measured 179475 microseconds for recovery-offer validation. That timing
included the existing synchronous document reconstruction, not only helper operations.
The observer now measures the task interface inside each consumer and retains full
consumer timings separately. The failed observation remains a performance issue for
installed-editor integration; it was not converted into whole-UI qualification.
No frozen package, pixel/file expectation, task bound or native deadline was changed.
One recorder invocation also stopped before CTest because it used a CMake target name
instead of the executable output name SysPane.TextProbe; the coordinator records it.

## Next admitted boundary

W-11 and W-26 remain in progress. Connect the bridge to the existing frontend
supervisory worker and native editor/inspector, then bind recovery directory,
profile, session, committed generation and current policy from authenticated owners.
Address the observed synchronous recovery validation before qualifying installed UI
latency. Keep protected-policy refusal and the current three-file settings payload
until the composed five-file frontend and its authority/lifetime tests are admitted.

Finish real telemetry, desktop activation/visibility, independent escape/recovery,
imports, lifecycle and all complete Windows 9x, Windows NT, Linux X11, Wayland and
Mac OS X editions. Component graphs do not qualify historical operating systems;
the native evidence here covers the pinned unprivileged Linux development laboratory.
No protected-policy deployment or public release is authorized by this checkpoint.
