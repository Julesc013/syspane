---
type: "SysPane Work Package"
title: "Policy-bound conditional visibility"
description: "Close conditional visibility semantics before scene and native authoring admission."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T22:35:49.126710+00:00"}
sp_id: "SP-W09-VISIBILITY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-BINDINGS", "SP-W10-EDIT-LOCKS", "SP-RUNTIME-OBSERVATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-bound conditional visibility

Continue W-09/W-10 toward conditional visibility. The shared evaluator is the first
implementation boundary. Existing scene/command versions do not admit a visibility
property. Complete the subsequent versioned admission, rendering and authoring
boundaries below before enabling this feature in a scene or claiming W-09/W-10 done.

## Fixed evaluation contract

The experimental visibility 0.1 document contains exactly schema_version, binding,
op, value and unit. It selects one existing binding: singleton selector (limit 1),
direct pin, persistent pin or unresolved legacy pin. Collection selectors reject
even if their current result has one row. This is a bounded comparison, not a
general expression interpreter; no script, native call, implicit aggregation,
regular expression, locale collation or conversion is performed.

op is eq/ne/lt/le/gt/ge. value is a finite JSON number, boolean or plain UTF-8 string
of at most 512 Unicode scalars. Boolean and string literals admit only eq/ne and
unit "1". Numeric comparisons require an exact authored unit string (1..64 ASCII
characters from letters, digits, underscore, dot, slash, percent, colon, asterisk,
caret and hyphen). The entire rule is at most 64 KiB of canonical UTF-8 JSON.
Other binding grammar and limits remain unchanged. Invalid rule/context or missing
sink throws before any sink invocation, with the existing bounded schema/context
error. C++ non-finite literal input rejects, never becomes JSON null.

Use the current project_binding owner and policy-bound synchronous borrow. Deliver
one VisibilityResult containing only its code; no copied observation, identity,
literal, formatted value, revision cache or persistent state. The callback must
not retain derived operational output or reenter the participating views. Its
exception propagates once, including bad_alloc. Successful decisions occur inside
the original binding borrow; all owners remain protected against reentry. Current
permission is checked on every call. A regrant without a fresh attachment/full state
cannot restore an old decision. No additional collection demand or native cache is
created by this evaluator; those owners must integrate before native admission.

Map nonmatched binding codes to pending/empty/denied/unsupported/ambiguous/invalid/
capacity, respectively. A matched frame must have exactly one row and total 1 with
no truncation; otherwise invalid. A nonmatched row preserves the corresponding
code. For a matched row, use this precedence:

1. Denied acquisition => denied; unsupported support => unsupported.
2. Nonactive presentation => lease_lost, even if retained value/freshness looks usable.
3. Other nonsuccessful acquisition, unknown support, nonpresent or null value => unavailable.
4. Effective freshness other than current => stale. Unknown clock/age cannot imply current.
5. Non-finite measured numeric value => invalid. Exact unit mismatch => unit_mismatch.
6. Literal/observation category mismatch => type_mismatch, including ne. Never coerce.
7. Compare exactly: a true predicate => shown; false => hidden.

Numeric category includes uint64 observations and finite binary64 observations,
compared against signed/unsigned integer or finite binary64 literals without first
rounding integers to binary64. Preserve ordering around 2^53, signed minima and the
uint64 maximum. Negative zero equals zero. Text equality is exact Unicode content
without case folding/normalization; booleans compare only to booleans. Synthetic
entity metadata is eligible only with active presentation and current clock, uses
unit "1", and retains the same policy/lease rules. Unresolved is never hidden.

## Required scene/native integration after the evaluator

Admit an optional rule through a new scene version and explicitly negotiated
command/capability, preserving all existing schema and fixture bytes. Missing rule
means unconditional content; old consumers reject unsupported versions rather than
drop the rule. Resource closure, presets, persistence, replay/reconciliation,
explicit version promotion, undo/redo and locks must cover the new property.

Hidden content retains its authored layout space and remains selectable in the
editor's authored object list. A hidden group gates descendant content without
rewriting or losing their conditions. Layout, editing selection and collection
demand cannot jitter or permanently suppress the observations needed to reveal it.
An unresolved rule replaces its conditional content with an explicit diagnostic
inside the retained bounds. Core source-failure, replay, lease, host and policy
status remain outside the condition; no authored predicate suppresses them.

The native owner must erase conditional pixels/accessibility text and stop retaining
unauthorized derived decisions within the existing disclosure bounds. Preserve
independent current-policy checks for widget content and conditions. Before enabling
group gating, close ordered ancestor/child diagnostic composition, resource/history
lifetime and frozen-gesture behavior with exact fixtures. Native authoring supplies
the binding, comparison, typed literal and explicit unit through a private buffer,
then one ordinary atomic draft operation. Cancel, invalid input and no-op preserve
history; current policy, lock and pending-transaction guards remain authoritative.

## Verification and handoff

Freeze this package, schema and independently written comparison/state examples
before production changes. Shared tests cover every operator, exact numeric
boundaries, type/unit mismatch, selector ambiguity, missing fields, all observation
axes, stale/clock loss, lease expiry, disconnect/restart, revocation/regrant, limits,
strict grammar, callback/reentry and unchanged inputs. Exercise actual DataView
publications as well as fixed value examples. Check all three development profiles,
existing bindings/chart/layout/model/transaction suites and composition direction.
Record source/archive/artifact identity, attempted commands and failures in the
existing bounded workspaces. Historical-toolset host execution is not historical
OS qualification. Routine internal choices are delegated within these bounds.

The later native matrix must observe exact pixels, accessible diagnostic/absence,
unchanged space/selection, save/reopen, lost acknowledgement/restart and erasure,
including deliberate inverted-predicate and retained-content controls. These tests
remain required; passing the portable evaluator is not native feature completion.
Typography, clipboard/recovery drafts, installed ownership, all five complete
editions and full release qualification remain part of the active campaign.
