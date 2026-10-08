---
type: "SysPane Work Record"
title: "Native editor recovery controls checkpoint"
description: "Verified generation binding, native recovery decisions and matching capture retirement."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T16:18:32+00:00"}
sp_id: "SP-RECOVERY-CONTROLS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-RECOVERY-CONTROLS", "SP-RECOVERY-QUEUE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native editor recovery controls checkpoint

Baseline 44348702b3d710d47f8df084cd6e7a17bfe33b26. The
[controls package](packages/w-10-recovery-controls.md) connects EditorForm to the
existing draft encoder, native operation queue and private file store. This is
explicitly admitted Linux development functionality. Installed directory/profile/
policy ownership and every complete desktop edition remain open.

The host supplies a verified session/profile/generation, current policy revision
and erase authority separately from the record. Startup loads asynchronously and
requires an explicit Restore, Discard recovery draft or Keep for later decision.
Invalid and stale records cannot restore. Restore enters the existing preview as
one undo step; opening an offer never commits or activates the scene. Keep releases
the in-memory offer and prevents later edits from overwriting it for that binding.

Atomic authored changes capture immediately through the coalescing queue. Private
property fields and held gestures do not capture. Apply waits for an outstanding
capture but remains usable when recovery is unavailable. Recovery status is separate
from saved configuration and activation status. Undo to the clean baseline and
Cancel session fence the matching capture; cancelling an undecided offer preserves
that record. Input is disabled while cancellation retires a record.

An accepted Apply closes the old queue and retains only its matching digest as
request metadata. A new verified generation opens a fresh owner; only that matching
record may retire. An external replacement remains an explicit offer. A change of
session/profile clears the previous scope's cleanup intent. Lost-result reconciliation
uses the existing transaction path. No recovery-file I/O executes in GTK callbacks.

Policy/disconnect/reload erases offer buffers and closes the old owner. Regrant alone
does not restart capture or restore. Close is nonblocking; the host continues its
loop and calls EditorForm::stopped until the held recovery child is reaped, then
destroys the form. Ordinary native host teardown follows that path.

## Evidence

Fourteen native scenarios pass through actual GTK keyboard/pointer input and AT-SPI.
They inspect exact recovery bytes against independent literals, real selecting-record
digests, committed scenes/resources, private file permissions and native process exit.
They cover crash/reopen, Restore/Undo/Redo/Apply, Keep through later editing and Apply,
Discard without authored changes, private fields, clean Undo, Cancel, invalid/stale
records, policy denial/regrant, lost-result reconciliation, external replacement,
worker failure, held-child close and a changed profile after Apply.

A wrong expected record is rejected. Recovery buttons/status are independently
checked within the 800 by 600 display and captured as pixels. This visibility check
applies to the recovery strip; it is not full editor layout/accessibility qualification.

Existing native checks cover clipboard (6), editor form (20), visibility controls
(16), content properties (15), recovery storage (74), queue (31), Apply (11) and
stored Apply (11). Shared recovery checks pass ten cases per development profile;
all three profiles configure/build and pass both component graph checks. These are
host development results, not historical Windows or other-platform qualification.

Specification validation passes 46 schemas and 158 fixtures. Tooling runs 62 tests:
60 pass and two existing Windows symlink-privilege assertions skip. Generated
projections and the unchanged settings resource fixture also pass. The 8 GiB
development workspace allocation remains unchanged; archives are measured separately.

The [compact checkpoint](checkpoints/recovery-controls.json) preserves exact source
archives, executables, commands, outcomes and later changes. Raw recordings and
screenshots remain ignored local out/evidence content. The initial package, scene
and command literals remain unchanged; the profile-change supplement was frozen
before its production guard. No acceptance condition was removed.

Four failed native attempts remain preserved:

- The initial Python expected-byte encoder used integer spelling for coordinates.
  Existing MoveWidgets produces doubles; the decoded command exactly matched the
  frozen expected command. Correcting that encoder preserved the literal values
  and original failure, without changing production serialization.
- Native host destruction called through an already reset form. The destruction
  callback now checks whether the form still exists; ordinary exit waits for reaping.
- The held-worker observer attempted a restricted proc executable link. It now
  checks the actual parent's child list, exact argument vector and stopped state,
  then holds a pidfd. No privilege or observation deadline was changed.
- The independent visibility assertion found a recovery label five pixels wider
  than the display. The recovery strip now precedes the canvas and its label has
  bounded wrapping and start alignment. The original failed observation remains.

The earlier 13-case passes preceded the additional scope guard. Prior unrelated
native timeouts and private-text shutdown warnings remain open; this checkpoint
does not explain or erase those historical failures.

## Next dependency-ready work

Keep W-10 in progress. Connect the tested editor to installed controller, catalog
and mandatory-policy ownership, including private profile/recovery directory creation,
verified generation handoff, scene-aligned entry and independent exit/restoration.
Close native accessibility, layout and performance qualification against real target
profiles. Continue non-Linux adapters and all five complete desktop editions through
the existing graph. No release, privileged operation, hardware power-loss claim,
secure erasure or Git history rewrite occurred.
