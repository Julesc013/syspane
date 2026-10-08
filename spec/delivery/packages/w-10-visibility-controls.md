---
type: "SysPane Work Package"
title: "Native conditional editing and enablement"
description: "Private rule input, hidden-object selection and durable conditional editing through the existing native owner."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T00:42:29.343682+00:00"}
sp_id: "SP-W10-VISIBILITY-CONTROLS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-VISIBILITY-ADMISSION", "SP-W09-NATIVE-VISIBILITY", "SP-W10-BINDING-AUTHORING", "SP-W10-NATIVE-OBSERVATION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native conditional editing and enablement

Connect the existing typed visibility edit and native renderer in EditorForm.
Keep visibility 0.1, scene 0.5, command 0.7, resources, history and transaction
identities unchanged. This package covers all seven primitive kinds and 1..256
selected authored IDs, including groups and hidden objects. It completes the
native component integration; installed ownership and complete editions remain open.

## Private rule input

Visibility is enabled only when EditorDraft.visibility_available permits it, every
selected target is unprotected, property buffers are clean and no modal, pending
request or conflict is active. The private modal snapshots the selected IDs and
own rules. Do not treat an inherited rule as the object's own editable value.

Modes are Always show (remove own rules), When condition matches (set one rule on
all selected IDs), and Keep unchanged for initially mixed own rules. Equal own
rules hydrate exactly; all absent rules start at Always show. Mixed mode never
serializes a replacement. Set creates at most one existing typed draft operation;
no-op and Keep unchanged create no history entry. Cancel changes nothing.

A new conditional buffer starts with a local_host selector for network.interface,
network.receive_bytes, singleton mode, limit 1, no filters/sort, and comparison
number 0, operator gt, unit byte. These visible defaults match the existing network
creation direction; a rule is not authored until the user selects conditional mode
and Set. Existing rules never receive inferred defaults or unit conversion.

Use the existing private Bindings dialog for source edits, nested under Visibility.
Its Set changes only the outer private source; its Cancel preserves that source.
All admitted binding kinds, scope, filters/sort and lossless values remain supported.
A selector must retain singleton mode and limit 1; reject a larger limit at source
Set without mutating either scene or outer source. Legacy unresolved pins may only
be preserved exactly or explicitly converted through the existing controls.

Comparison controls expose eq/ne/lt/le/gt/ge, text/boolean/number, literal/escaped
text, value and unit. Reuse exact binding-value parsing: uint64/int64 do not round
through double, decimals/exponents must be finite, booleans are true/false, and text
is lossless. Text/boolean require eq/ne and unit 1. Invalid combinations report an
error without silently coercing fields. Inactive comparison/source buffers do not
prevent Always show or Keep unchanged. Existing rule/document/string limits apply;
private value entry is bounded at 4096 bytes, unit at 64 and numeric tokens at 64.

Modal construction remains lazy and fits the existing owned 800x600 laboratory.
Expose native names, roles and values; no JSON document editing is required.
Main selection, gestures, properties, history and submission are disabled while
Visibility or its nested Bindings dialog is open. All field/model/snapshot/error
text is wiped on Cancel, successful Set, close, disclosure/policy change, command
disconnection, topology change or reload. Nested held native references must erase
too. Regrant alone cannot restore buffers. Keep C++ exceptions inside GTK callbacks.

## Preview, selection and held gestures

EditorForm may explicitly enable the tested SceneSurface path only with the trusted
large-command context and configuration.visibility/configuration.edit-locks plus
scene.content/scene.edit-locks/scene.visibility capabilities. Authored scene flags
alone cannot enable it. Current authorization still gates every presentation and edit.
Direct SceneSurface default refusal remains; native component admission is not
installed-host admission. Older scene/command contexts keep existing behavior.

The authored object list retains hidden IDs/titles and selection. Canvas hit testing
skips not-presented objects but permits diagnostic objects; hidden selection can be
recovered from the object list and retains ordinary geometry/property/keyboard edits.
Hidden nodes remain geometry/snap targets. Selection outlines are editor chrome and
may outline selected hidden objects without rendering their hidden payload. Status
identifies hidden or diagnostic selected content and does not reinterpret either as
an off-display object. Multi-selection never mixes its rules without explicit Set.

For scene 0.5, paint current conditional content and mandatory diagnostics during
held gestures. Capture geometry/variant/snap targets at gesture start as before;
telemetry transitions cannot move that captured outline or alter the authored draft.
A show/hide transition does not cancel the gesture. Release commits the captured
geometric delta once, even if its selected content became hidden. Escape cancels;
policy/topology change retains existing cancellation/erasure. No old pixels or rule
decisions are retained merely to stabilize a gesture. Legacy held-preview behavior
remains unchanged for older scenes.

Group/Wrap preserve child rules under an unconditional new parent. Own-rule
Ungroup/Unwrap still rejects with an actionable clear-rule explanation. This package
adds no new reparent operation; later native reparent input must explain inherited
condition changes. Renderer warning overflow remains an explicit unavailable preview
with Layout, Visibility, rule removal and Undo available for recovery.

## Durable and independent acceptance

Apply uses the existing negotiated command 0.7 and exact resource-aware request.
Pending/unknown outcomes disable rule mutation. Lost acknowledgement and controller
restart reconcile the same request/revision once; no revision 42 may be invented.
Saved status keeps durability, activation and external visibility separate. Reopen
hydrates the exact stored rules, numeric/text values and package selection.

Freeze this package and literal input/expected-scene cases before production edits.
Portable tests cover defaults/equal/mixed input, all comparison value types, exact
numeric extremes, inactive fields, invalid source/type/unit combinations, one atomic
bulk edit, no-op/history, locks, current policy, pending state and command bytes.

Independent owned-X11/AT-SPI cases operate real controls and observe exact scenes,
resource identity, hidden pixels/names, authored-list selection, held show/hide and
mandatory diagnostics, undo/redo, save/reopen, source editing, nested erasure and
lost-acknowledgement/restart. Keep positive witnesses for wrong stored rule, frozen
preview and retained private input controls; a timeout is not fault detection.
Use explicit native observation replies and existing 200 ms erasure/update bounds.

Run affected and full portable suites on all three development profiles and the
existing binding/editor/layout/container/lock/native-visibility regressions. Preserve
failures, source/artifact/environment identities and fixed expectations. Use ordinary
commands and non-root WSL; reclaim only verified committed duplicates within 7 GiB.
Do not claim W-10, full accessibility/performance, installed ownership, other native
adapters or any of the five release editions complete from this component work.
