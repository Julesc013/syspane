---
type: "SysPane Work Package"
title: "Native creation of every scene primitive"
description: "Create bounded authored widgets through existing resource, draft and transaction owners."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T08:05:00.283712+00:00"}
sp_id: "SP-W10-WIDGET-CREATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-BINDING-AUTHORING", "SP-W10-EDITOR-DRAFT", "SP-W10-CONTENT-PROPERTIES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native creation of every scene primitive

Continue W-10 by admitting a portable creation projection and a lazily constructed
native Add widget dialog for scene 0.3. Reuse InsertWidget, EditorDraft, immutable
resource choices, current policy, SceneSurface and the existing transaction owner.
No schema, import path, provider discovery, implicit pin mapping or storage owner
is added. Existing Add text stays a compatible convenience action.

## Exact initial objects

Offer text, value, status, table, chart, image and group. Every fresh object has a
host-supplied ID, editable title, normal priority, a fixed base layout and no
extensions/breakpoints. Preserve every existing scene member and resource identity.
Root insertions copy the explicitly supplied display assignment. A group insertion
copies that group's authored display assignment exactly, including portable roles;
coordinates are explicitly parent-local, never converted from observed pixels.

Default x/y are 20/20 DIP. Default width/height: text 180/80, value 240/100,
status 240/120, table 420/180, chart 400/240, image 160/120 and group 320/240.
Title defaults to the capitalized kind. Text body defaults to Text. Value/status/
group content is empty; group children are initially empty. Images start with
alternative text Image, preferred size 160x120 DIP and contain fit, but have no
default asset. Require explicit selection of an exact image from the currently
admitted immutable closure; absent/unadmitted choices reject without insertion.

Value, status and chart initially expose an explicit local_host singleton selector
over editable entity type network.interface and editable field network.receive_bytes,
with no predicates/sort and limit 1. Table exposes two editable distinct fields,
network.receive_bytes and network.transmit_bytes, with labels Receive/Sent and the
same local_host collection selector, no predicates/sort and limit 8. These are
visible starting values, not inferred host identity. The existing resolver reports
missing or ambiguous sources; creating a widget never activates acquisition or
grants disclosure. Further filters, pins, labels and columns use their own authoring
contracts. Chart content starts at window_ms 60000, max_points 256, linear
interpolation, auto axis with include_zero true.

## Native input and atomic ownership

Open only from an editable scene 0.3 draft with clean basic property fields. Cancel
the active gesture. Capture the scene, current selection, display and immutable
resource choices. Choose Scene roots or an existing group in authored widget order;
preselect the sole selected group, otherwise roots. Append to the chosen ownership
array. No guessing about responsive transforms: explicit parent-local fixed input
is resolved by the existing layout engine and can produce its usual diagnostics.

Keep a separate private buffer for each kind while the dialog is open. Changing
kind restores that kind's buffer. Parent choice is shared. Title/body/alternative
text use the existing bounded private controls. Geometry uses the existing finite
decimal/exponent parser: at most 64 ASCII characters; x/y -100000..100000, width
32..32768 and height 16..32768 DIP. Reject invalid input without clamping. Images'
preferred size remains independent of authored geometry. Ignore inactive inputs.

Add validates the entire proposed candidate through EditorDraft. Allocate at most
one host ID per Add attempt; failed attempts may consume an ID but never publish
it. Invalid IDs, collisions, capacity/depth, bad fields, duplicate table columns,
policy/resource denial or invalid geometry preserve scene, selection, history and
request identity. Keep input available for correction. No intermediate blank widget
is inserted. Successful insertion and selection of its ID form one history entry:
Undo restores the exact prior scene/selection; Redo restores both the object and
its selection. Extend the typed InsertWidget with an opt-in select_inserted flag,
default false, preserving existing callers. The flag is not a new wire member.

Main selection, fields, history and submission are disabled while the dialog is
open. Add changes only the local draft; Apply commits separately through the existing
resource-aware request. Cancel/Escape/window close erase the buffer and preserve
the existing preview/history. Policy/topology replacement, reload, disconnect and
owner close erase all kind buffers, captured scene, resource references, list models,
errors and accessible text. Wipe native model text before removal. Disclosure loss
keeps the existing 200-ms bound; regrant cannot reconstruct the erased state.

## Verification

Before production edits, freeze this package, the unchanged content resource
fixture, complete default objects and full expected root/nested scenes. Portable
checks cover every kind, parent/display intent, numeric/asset bounds, atomic errors,
identity/depth/capacity, per-insertion selection history, exact command scenes and
policy/resource rejection. Use all three current development toolchains.

Owned Linux tests must create every kind through native controls, observe selected
geometry and rendered/accessibility content, Undo/Redo, compare actual stored
documents/resources, reopen, cancel private/transaction input, reconcile a lost
acknowledgement, and erase held accessible references. Include nested creation,
kind-buffer restoration, explicit image choice and invalid correction. Deliberate
wrong committed object, frozen preview and retained buffer faults need positive
distinguishing observations. Keep expected objects and acceptance unchanged.

Run affected editor/settings/configuration/composition/protocol checks and existing
native binding/content/snap/group/arrange/editor/large-command matrices; retain all
attempts with source, binary, oracle and environment identity. W-10 remains open for
responsive/flow authoring, lock/visibility/typography, clipboard/recovery drafts,
provider discovery, installed routing, full accessibility/performance and other
adapters. No complete edition or historical runtime is qualified by this component.
