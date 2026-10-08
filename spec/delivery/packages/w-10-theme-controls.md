---
type: "SysPane Work Package"
title: "Native font controls and draft resource preview"
description: "Lossless base/role editing, current immutable preview and independent durable native evidence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T05:19:40.545038+00:00"}
sp_id: "SP-W10-THEME-CONTROLS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-THEME-HISTORY", "SP-W10-THEME-AUTHORING", "SP-W09-ROLE-COMPOSITION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native font controls and draft resource preview

Connect the existing lossless font input and atomic resource history to EditorForm.
Preserve theme 0.2, command 0.8, generation 0.4 and all limits. This is native
component integration; installed ownership, other adapters and complete editions
remain separate requirements.

## Controls and exact input

Fonts is a scene-wide action, independent of selected widgets. Enable it only when
EditorDraft.theme_fonts_available permits edits, properties are clean and no modal,
pending request or conflict is active. It does not override widget edit locks or
modify geometry. A lazy native modal fits the owned 800x600 laboratory and exposes
names, roles, values, keyboard activation and explicit validation feedback.

Target selects Base, Body, Label, Value or Diagnostic. Each complete font exposes
literal family, size in DIP, weight and normal/italic/oblique style. Reuse the
existing lossless parser; family input is bounded to 512 UTF-8 bytes, numeric fields
to 64 bytes. Existing 128-codepoint family, finite size and weight constraints apply.
No installed-font substitution, trimming or locale coercion is allowed.

Role overrides offers Use base font for all roles or Customize roles. The first
omits font_roles and ignores inactive private role values. Customize stores an
explicit map, including an empty map when no individual role is enabled. Each role
has a Use this role font toggle; disabled roles inherit the base font. A newly
enabled role starts from the base font captured on open unless a private value
already exists from this modal. Switching target or mode retains raw private values,
including invalid input, until Set or erasure. Inactive fields cannot invalidate Set.

Hydration preserves source values. An unchanged Set returns the exact original
theme, including schema version, omitted defaults, numeric representation and
absent versus empty role map. A changed Set validates a complete theme 0.2, keeping
all non-font values and source license unchanged, and invokes existing atomic font
authoring once. Invalid input leaves the modal and draft unchanged with actionable
feedback. Set changes the draft; Apply saves it. Cancel changes nothing.

Use settings theme performs existing SceneThemeEdit(null), ignoring private invalid
font values. It restores scene-level inheritance from settings, not a guessed font.
Undo/redo retains exact scene/selection/resources and the existing count/byte limits.

## Lifetime, preview and admission

While Fonts is open, main selection, gestures, properties, history, reload and
submission are disabled. Wipe all private field/model/snapshot/error values on
Cancel, successful Set/reset, close, any policy change, command disconnection,
topology change or reload. Held native references must observe erasure within the
existing 200-ms bound. Regrant alone never restores private buffers. Keep exceptions
inside GTK callbacks. Private text must not export either clipboard selection.

Preview, content choices and widget creation must consume the current draft's
matching borrowed resources. Never resolve an authored override through the original
settings catalog. SceneSurface receives its own validated snapshot sharing immutable
packages; no unsafe borrowed pointer may outlive the draft. Do not retain a redundant
catalog in EditorForm after the shared draft owns it. Current policy/resource loss
clears draft, private modal and preview state together.

Trusted EditorForm may enable typography only with the existing explicit large
command/context admission (all seven theme/history capabilities) and current policy.
Font edit permission is distinct from permission to display a retained theme.
Direct SceneSurface defaults remain unchanged. A disabled Fonts action explains
missing capability, current edit unavailability or pending private properties.
Preserve mandatory diagnostics and the established visibility/edit-lock gates.

## Durable and independent acceptance

Apply emits existing command 0.8 against the accepted source; accepted generations
advance once. Lost results reconcile the original identity across epochs. Fresh
reopen restores exact artifacts, font values and role membership. Durability,
activation and external visibility remain distinct facts. Theme reset and ordinary
content/image operations after a font edit retain coherent resources.

Freeze this package and independent artifact/scene/selection/font examples before
production edits. Portable cases cover unchanged hydration, explicit empty versus
omitted roles, every role, inactive invalid values, invalid active values, one undo
step, reset, admission, policy and pending state. Run affected/full suites on all
three development profiles.

Owned non-root Linux cases must operate actual GTK/AT-SPI controls, compare literal
font requests through the independent text probe with observed canvas pixels, and
verify exact stored generation/artifact bytes and fresh reopen. Exercise base and
all role fonts, no-op, null/empty roles, invalid correction, undo/redo, reset,
pending cancellation, lost acknowledgement/restart, denial and modal erasure on
each lifetime boundary. Show positive witnesses for wrong committed font intent,
retained private text and frozen preview; a timeout is not fault detection.
Preserve accessibility diagnostics and current source-status rendering. Regress
native editor/content/visibility, theme history/commands and role composition.
Preserve all failures with source/artifact/environment identity within 7 GiB.
This evidence cannot qualify a whole edition or a historical OS.
