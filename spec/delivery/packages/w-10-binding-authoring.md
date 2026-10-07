---
type: "SysPane Work Package"
title: "Native authored binding controls"
description: "Edit selectors and explicit pins through the existing scene draft and resolver."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T07:19:13.409999+00:00"}
sp_id: "SP-W10-BINDING-AUTHORING"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-CONTENT-PROPERTIES", "SP-W09-BINDINGS", "SP-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native authored binding controls

W-10 adds bounded private binding buffers to the existing editor. Reuse binding
0.1, scene 0.3, EditorDraft, the current-policy resolver and the resource-aware
transaction owner. No new binding grammar, live identity cache, implicit mapping,
acquisition, import or arbitrary expression evaluation is admitted.

## Closed behavior

The native Bindings action requires one selected value, status, chart or table in
a scene 0.3 draft. Scalar widgets retain exactly one descriptor. A table retains
its existing columns, labels and order; the selected column supplies its field.
Every column shares the edited selector query (all members except field) in one
atomic WidgetContentEdit. Changing a table column field changes only that column;
duplicate fields and invalid complete scenes reject atomically. Column insertion
and widget insertion remain separate authoring work.

Selectors expose explicit scope, optional registered asset, entity type, result
limit, up to sixteen ordered predicates and eight ordered sort keys. The widget
fixes mode: table collection, scalar singleton. Keep a scalar selector's admitted
limit, including values greater than one; singleton ambiguity never selects the
first match. Direct pins expose producer, epoch, entity and field. Persistent pins
expose scope, namespace, key, entity type and field. These are authored references,
not authorization to create persistent mappings. Missing providers/mappings remain
visible resolver outcomes. Never infer pin identity from a displayed name.

An existing unresolved legacy pin may be preserved or explicitly converted; new
unresolved pins cannot be fabricated by the editor. Preservation requires its
original descriptor exactly, including entity and field. Switching binding kind
ignores inactive buffers. Switching back may restore private input until closing;
only the active kind is serialized. Existing descriptors round-trip without loss.

Predicate values have explicit text, boolean or number type. Text is literal UTF-8
with no trimming/normalization/coercion. Boolean input is exactly true or false.
Number input is a JSON number token, at most 64 ASCII bytes: no leading plus,
whitespace, leading zero or non-finite value. Integral tokens use exact int64/uint64
storage; overflow rejects instead of silently rounding to binary64. Decimal or
exponent tokens use finite binary64. Existing numbers use round-trip formatting.
Identifier, string, list and scene limits remain those of the existing validator.
Limits use canonical unsigned decimal 1..256. Inactive buffers cannot make valid
active input fail. All active fields are validated together before mutation.

Native predicate/sort lists have explicit add/remove/move controls, preserve order
and privately retain invalid row text while switching rows. Add creates a visible
empty row requiring correction; never silently inserts a matching predicate.
Bounds disable Add and invalid end moves. Native controls expose accessible names,
roles and values; no JSON editing is required. Keep modal height within the owned
800x600 laboratory by using tabs and bounded row editors, not an unbounded form.

## Ownership and failure

Construct modal native chrome lazily. It owns only a snapshot of the selected
authored widget and private input. Disable selection, gestures, main property
edits, history and submission while open. Set projects one atomic draft edit and
creates at most one undo step. No-op Set and Cancel preserve preview/history.
Apply separately uses the existing durable request. Invalid Set preserves all
buffers, scene, selection, resource identities, history and accepted revision.

Cancel, close, disclosure/policy change, disconnect, topology change or reload
clear all input, list/choice models, snapshots and error text. Wipe model text
before removing native rows so held references cannot disclose it. Regrant cannot
restore erased input; fresh explicit reload is required. Current-policy validation
is never delegated to the UI. Do not let C++ exceptions cross GTK callbacks.

## Independent acceptance and execution

Freeze this package, the unchanged content resource fixture and literal descriptor
and complete expected-scene cases before production edits. Cover all binding kinds,
all scopes, numeric extremes, type distinctions, ordered rows, table query/field
coupling, inactive fields, no-op, invalid atomicity, undo/redo, command bytes and
policy rejection. Use all three development profiles and existing affected
editor/settings/configuration/composition/protocol checks.

The owned Linux native oracle must operate actual controls, compare resolver
accessible output and changed pixels, inspect coherent persisted scenes/resources,
reopen, exercise cancelled/unknown requests and disclosure loss with held native
references. Preserve fixed expected scenes and every failure. Deliberate incorrect
stored binding, frozen preview and retained-buffer controls need positive witnesses;
timeouts alone are not successful fault detection. Rerun existing native editor,
content, arrangement, grouping, snapping and large-command matrices after changes
to their shared native owner. Use the existing unprivileged workspace and preflights.

Record exact source/artifact/oracle identity and next work. Full provider/catalog
discovery, installed routing, clipboard/recovery drafts, responsive editing,
accessibility/performance and all complete editions remain open.
