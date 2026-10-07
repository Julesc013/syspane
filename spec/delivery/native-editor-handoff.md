---
type: "SysPane Work Record"
title: "Native scene editor checkpoint"
description: "Real GTK editing, resource-aware persistence, policy erasure and independent recovery."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T03:55:11Z"}
sp_id: "SP-NATIVE-EDITOR-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-NATIVE-EDITOR", "SP-EDITOR-DRAFT-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native scene editor checkpoint

Subsequent checkpoint: [complete-scene commands](large-commands-handoff.md) closes
the larger-scene transport limitation recorded below. This page preserves the
original checkpoint and its remaining independent gates.


Source baseline: `c225a32823682b904e624d295b694d233accb773`. The
[package](packages/w-10-native-editor.md) admits the initial Linux GTK EditorForm.
W-10 remains in progress. This is an embeddable native component and owned laboratory
fixture, not an installed desktop edition or behind-icons qualification.

EditorForm combines the existing EditorDraft, SceneSurface and resource-aware
command owner. Actual rendered geometry drives stable-ID selection, reverse-order
hit testing, fixed-base drag/resize and pointer-to-DIP conversion. Arrow keys and
typed property changes reach the same atomic draft operations. A drag commits one
history entry on release; Escape, focus loss, topology or policy change cancels the
gesture. Geometry-only feedback prevents live pixels from retargeting a held drag.

Title, plain text and fixed geometry fields remain buffered until Set properties.
Invalid numeric syntax retains the text and disables Apply. Topology changes retain
buffered edits and authored display identity. Duplicate selects the new roots;
Delete therefore removes the copies. Add/Delete, Undo/Redo, Apply, Cancel session,
Cancel request and explicit Reload use the common draft/transaction state machine.
Pending and unknown requests disable further editing and preserve their identity.
Saved, pending activation and unconfirmed visibility are separate displayed facts.

Settings and editor fields share one bounded native plain-text component. It
retains the existing settings limits and prevents clipboard, PRIMARY, drag and
AT-SPI copy/cut export. Disclosure loss erases fields, list cells, held accessible
content, gesture state and native preview resources; permission regrant requires a
fresh reload. SceneSurface close now also releases its authored/resource config.

The existing independent editor-exit owner can exec the actual editor fixture as
its held child, preserving parent lifetime. It acquires the shortcut before child
admission and keeps its own GTK recovery button. Frozen editors, held pointer
gestures and owner loss release the obstructing lifetime without committing local
edits. This is emergency release, not a successful transaction Cancel claim.

## Evidence and corrections

Literal scenes, resources, expected movement/properties and timing limits were
archived before production edits. Those fixture bytes remain unchanged. Independent
XTest input, AT-SPI queries, actual pixel translation and coherent generation-store
bytes agree. The twenty-case matrix includes save/reopen, burst keyboard movement,
resize, multi-selection, structural operations, property validation/history, request
cancellation, revision conflict, denied retrieval, policy erasure, restart without
duplicate publication, topology replacement, three deliberate faults and five
recovery cases. It checks the existing 200 ms erasure and 1,500 ms recovery bounds.

Deliberate frozen pixels, incorrect stored geometry and retained disclosed text
must fail their specific observation while positive distinguishing facts hold.
Shortcut conflict must deny admission before any editor child or authored store.
The original fixture images also permit direct review of the native controls.

Preserved failures exposed a C++ name collision/strict indentation warnings,
duplicate retaining the wrong selection, and queued keyboard edits rejected while
awaiting GTK's next paint. Resolve current geometry through the same renderer before
accepting the next edit. The independent structural expectation was retained; the
package now explicitly states native post-duplicate selection. Native observer
corrections distinguish destroyed accessibility cells from stale text and tolerate
an indexed child disappearing during list traversal. They do not accept timeouts,
connection failures or changed pixel/storage expectations as success.

The repository's `build-support/evidence/w-10-native-editor-attempts.json`
binds exact source archives, commands, binary identities, logs, original failures
and native reports. Sixty-nine affected checks pass on each development toolchain.
Existing native settings, independent exit, inspector and renderer erasure checks
cover the shared changes. Historical-toolset tests execute on contemporary Windows;
they are not historical OS tests. The machine handoff records exact counts and
specification/tool/staging verification separately from product qualification.

The original build reservation stop is preserved. After reclaiming only fifteen
verified duplicate source archives, the new native binaries exhausted the remaining
6 GiB reservation headroom. The measured, reversible development allocation is now
7 GiB; product runtime limits are unchanged. No user desktop or public release was
modified by the private Xvfb/DBus experiment.

## Next required boundary

Close the versioned larger-scene command envelope and remaining authoring/property
contracts, then connect installed controller/catalog/policy state and scene-aligned
desktop entry/restoration. Keep the permanent wall passive and require independent
escape before mapping the editor. Reuse this component's ordinary build/test path.

The 256 KiB local scene contract still exceeds the existing 16 KiB wire command
ceiling; oversized Apply remains explicit rejection with the draft retained.
Snap/grid/guides, align/distribute, complete binding/content/theme/group panels,
persistent lock/visibility/typography, clipboard authority, recovery drafts,
maximum-size responsiveness, full localization and representative accessibility
review remain required. Native Windows/AppKit adapters, all complete editions,
historical OS floors/labs and release lifecycle/authority gates remain open.
