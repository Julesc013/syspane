---
type: "SysPane Work Package"
title: "Deterministic native alignment and spacing"
description: "Close fixed-base arrange operations through shared drafts and independent native evidence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T04:10:00Z"}
sp_id: "SP-W10-ARRANGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-EDITOR-DRAFT", "SP-W10-NATIVE-EDITOR", "SP-W08-LARGE-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Deterministic native alignment and spacing

Continue W-10 with typed AlignWidgets and DistributeWidgets in the existing
EditorDraft, plus native GTK controls. A user can arrange a selection, undo it,
redo it, cancel the session or submit one scene.replace through the current owner.
This adds no storage format, wire operation, policy authority or second resolver.
Selection, pins, extensions, widget order and untouched properties remain exact.

## Shared geometry contract

Each operation names 2..256 distinct widgets for alignment, or 3..256 for spacing.
They must be disjoint siblings with the same ownership array and structurally equal
authored display assignment. Input order is irrelevant. Resolve IDs in ownership
array order, independently of the scene's widget-record order. Missing/duplicate IDs,
ancestor overlap, mixed parents/displays, flow bases and unknown enum values reject
the entire batch. Finite coordinates remain within the existing scene schema.
These operations affect fixed base geometry only; breakpoint documents remain exact.
They do not promise to align an inactive base or a future responsive variant.

Use signed 64-bit units of 1/64 DIP. Convert each origin with nearest rounding,
ties away from zero; convert each extent with ceiling, matching scene layout.
Reject out-of-range/nonfinite values before integer conversion, including invalid
intermediate property edits in the same batch. Final scene validation is authoritative.
Only the selected axis origin changes. Extents, the other origin and every other
field remain byte-value-equivalent. Generated origins are integer units / 64.

Alignment supports left, horizontal center, right, top, vertical center and bottom.
Let L be the minimum selected origin and R the maximum origin + extent on that
axis. Start alignment assigns L; end assigns R minus the widget's extent. Center
assigns (L + R - extent) / 2, rounded to an integer unit with ties away from zero.
All targets use the original bounding interval, not sequentially modified values.

Spacing supports horizontal or vertical equal nonnegative edge gaps. Stable-sort
targets by quantized origin, ties in ownership order. Keep the first and last
origins exactly as authored, including their original fractional values. Let G be
last origin minus first origin minus the sum of every extent except the last.
If G < 0, reject without overlap, clamping, resizing or moving endpoints. Otherwise,
divide G by N-1 with quotient q and remainder r; the first r gaps in sorted order
are q+1 units and the rest q units. Assign each interior origin from the first
quantized origin, preceding extents and gaps. Zero gaps are valid. Endpoint
quantization affects the calculation but does not rewrite endpoint values.

The existing batch limit (128), scene limit (256 KiB), history limits (64 entries,
8 MiB), policy validation and pending/unknown/conflict gates apply. At most 256
targets and a bounded sort are needed; no paths, external resources or callbacks
are consulted. A failed operation after another edit changes nothing, including
selection/history/request identity. One successful batch creates one history entry;
selection is preserved. A value-identical result creates none and preserves redo.

## Native behavior and authority

Expose six labeled alignment buttons and two spacing buttons with stable accessible
descriptions editor.align-left/hcenter/right/top/vcenter/bottom and
editor.space-horizontal/vertical. Native list or canvas multiselection supplies IDs.
Buttons require the appropriate count and the ordinary editable/clean-fields state;
the handler rechecks current policy and geometry before the typed operation.

Use the shared renderer's freshly resolved nodes. Each selected node must use its
fixed base (variant -1), the same resolved parent/display, and have resolved width
and height equal to the ceiling-quantized authored extents. This prevents arranging
an unseen variant or misrepresenting a metric-expanded widget. The shared operation
additionally checks authored ownership/display. Ineligible selections show a native
explanation and leave scene, selection, history and storage untouched. This initial
fixed-base scope does not satisfy all responsive authoring requirements.

Cancel an in-progress gesture before arrangement. Arrange changes preview immediately
but never saves by itself. Pending fields block arrangement; pending/unknown commits
freeze it. Undo/redo, cancellation, disclosure erasure (200 ms), current-policy
commit, exact resource pins and reconciliation use the existing owners. Retain the
independent editor escape owner before installed mapping. Buttons use existing GTK
controls; no authored strings are exported to clipboard or new native caches.

Private helper names, algorithms meeting these results and button layout are
delegated choices. Contract changes, responsive semantics and additional authority
must be recorded explicitly. No privilege, publication or release grant is added.

## Execution and completion

Freeze tests/editor/arrange-cases.json before production edits. It contains complete
expected scenes for all eight actions and literal fractional/tie cases. Add portable
invalid, atomic rollback, hierarchy/order, history, policy and submission checks.
Expected values must not call implementation geometry helpers. Preserve failed
attempts before fixes and never alter an oracle to accommodate a nonconforming result.

After workspace preflight, configure/build each existing development profile and
run ctest --preset <profile> -R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure. Linux additionally runs native.EDITOR-ARRANGE, native.EDITOR-FORM
and native.LARGE-COMMANDS in the non-root private ext4/Xvfb/DBus workspace.

The new native observer must select via native controls, activate all eight actions,
compare independent pixels and exact stored documents, exercise undo/redo, save and
reopen, cancellation, current-policy denial, disclosure erasure and lost-result
restart. Deliberately frozen pixels and altered committed geometry must be detected.
Reports bind source/fixture/oracle/binary identities and preserve failed attempts.

Implemented means these checks actually ran and their artifacts are preserved.
It does not qualify installed editing, historical Windows, other adapters, all
accessibility/localization or the complete release. Snapping/grid/guides, grouping,
remaining properties, responsive arrangement, clipboard, recovery drafts and
installed controller/catalog/policy ownership remain explicit W-10 work.
