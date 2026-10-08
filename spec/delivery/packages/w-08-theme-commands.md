---
type: "SysPane Work Package"
title: "Durable authored theme commands"
description: "Negotiated font edits, versioned resource generations and exact restart reconciliation."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T03:37:39.534067+00:00"}
sp_id: "SP-W08-THEME-COMMANDS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-THEME-OVERRIDES", "SP-W08-LARGE-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Durable authored theme commands

Connect the immutable theme/override contracts to the existing serialized transaction,
async admission, IPC and Linux generation owners. Native controls and editor resource
history remain a subsequent integration. Do not create a new mutation service or
claim stored settings are already activated or visible.

## Command 0.8

Retain command 0.7 operations and result 0.1. Require content in resource-selection
0.2 format and theme_edit, which is either null or exactly {source, font, font_roles}.
source is the exact currently selected theme document pin. font is a complete theme
0.2 font. font_roles is null (remove the property) or a complete map of explicit
theme 0.2 roles, including an empty map. Only font fields travel in this section;
there is no uploaded manifest, path, dependency, license, color or extension change.
The controller copies the source theme, sets schema_version to 0.2.0, replaces font
and applies the exact font_roles presence, then invokes the existing canonical author.
Semantically validate font families and the resulting whole theme independently.
An exact unchanged resulting theme rejects with theme.no_change; elide theme_edit
for ordinary scene/settings edits. Candidate settings/scene determine the effective
theme ID and must match the exact resulting content selection.

The current generation must already have resources. Both original package/preset
pins must equal the current selection; initial import or a different preset uses
the established content-selection path first. Check current source policy before
construction. A source pin mismatch rejects with theme.source. Recompute the artifact
from the current theme and its preserved license, then replace the single override.
The resulting selection must equal command.content exactly; mismatches reject with
resource.selection. No catalog import callback is invoked for command 0.8.

With null theme_edit, resolve content against only the current immutable packages:
retain an existing canonical override, select a canonical artifact already in base,
or reset to the base theme using null theme_override. Resolution drops an unused
external override and retains every original base dependency/image. No fallback to
imports, renamed source or unreferenced external theme is permitted. Current source
and result capability checks, exact revisions and existing capacity limits apply.

Command 0.8 retains the 327680-byte original/canonical body ceiling, 18432-node and
depth-below-40 command profile, 262144-byte/16384-node/depth-below-32 scene and theme
limits, 328704-byte negotiated frame floor and global 1-MiB ceiling. Five bounded
font records fit the existing scene-envelope allowance; independently validate the
extracted font fields and resulting theme rather than increasing limits. The existing
128/1024 request counts, 16-MiB ledger reservation and ten-minute retention apply.
Original body bytes, including whitespace, remain the replay identity.

## Admission and authority

Negotiate exact command 0.8/result 0.1 and configuration.theme-overrides, with the
existing transactions, content, scene-content, large-commands, edit-locks and visibility
features. A supporting command owner requires resource preparation, scene.content,
scene.edit-locks, scene.visibility, theme.typography and configuration.theme-overrides
capabilities. Optional incompatible features are removed; required incompatibility
fails negotiation. Unsupported requests reject before admission/preparation.

Current policy must allow configuration.theme-overrides and theme.typography for
every 0.8 request, including reset and result retrieval. Existing settings/scene/content
authority still applies. A non-null theme_edit additionally requires theme.edit and
the console or desktop role (not saver_settings). Existing role checks for scene
replacement remain. Repeat these policy checks at publication, retained-result lookup
and cross-epoch reconciliation. Reject unavailable policy or changed policy/revision;
an already committed exact request may be reconciled, never blindly executed again.

Resource preparation and optional trusted after_prepare callback run on the serialized
transaction worker. Existing cancellation, bounded async jobs and commit permit apply.
Construction/validation failure never changes the selecting record. The draft remains
the caller's responsibility until the later native/editor integration is admitted.

## Generation manifest 0.4 and resource index 0.2

Command 0.8 requires manifest 0.4 with resources and separate request.json using the
existing hash-bound identity fields. Resource index 0.2 has the old index members,
but requires resource selection 0.2. Manifest 0.1/0.2/0.3 retain their original command
and index versions. A mismatched manifest, index, request version or selection rejects;
an old format cannot smuggle in the new meaning. The new writer also supports reset
with a null override without silently downgrading the generation.

Retain exact expected files, private ownership, no-follow/single-link rules, immutable
resource bytes, sorted manifest hashes, shared asset hashes, size limits, write/flush
order, selecting-record guard and coherent current/previous recovery. A generation
contains only its base closure and selected override; prior generations keep their
own bytes and the existing 32-generation ceiling is unchanged. No old generation is
deleted to make a test pass. The request body and all document/resource hashes bind
one revision; acknowledgements distinguish durable from pending activation/visibility.

During decode, validate content selection against resources and candidate, canonical
artifact identity, and, for non-null theme_edit, exact stored font/font_roles values
and presence against the request. A correct file hash alone does not prove that a
font request was fulfilled. Source authorization is established by the commit path;
recovery does not invent the previous source or replay the edit to reconstruct bytes.
Lost acknowledgement after selection recovers one coherent new revision, reports its
original request, and produces no extra revision. Corrupt/missing current data falls
back coherently to the previous generation under the existing read-only recovery rule.

## Fixed acceptance and next integration

Freeze this contract, command schema and literal requests/expected selections/fonts
before production edits. Portable families cover structural/semantic rejection,
maximum original bytes and overflow, exact source/result mismatch, no-op refusal,
commit/preview/reset/repeated replacement, current policy at prepare/publication/replay,
authorization, async cancellation and negotiation of every dependency/frame/document.
Retain old fixtures and their meaning; test on all three development profiles.

An independent owned ext4/IPC oracle inspects exact request, generation, index and
asset bytes; exercise save/reopen, repeated edits/reset without imports, cross-epoch
reconciliation, interruption before/after resource/selector publication, current-policy
revocation, missing/corrupt override/request and wrong stored font intent. Preserve
actual stopped/terminated process evidence and a deliberate wrong-output witness.
Run native generation/content-command regressions and specification/integrity checks.
Keep exact source/artifact/environment identities and all failed attempts.

Next connect immutable resource contexts to atomic editor history, Apply/unknown-result
reconciliation and reload, accounting for resource storage as well as scene history.
Then complete native base/role font controls, independent pixels/accessibility,
save/reopen and private-input erasure before trusted EditorForm typography admission.
Installed ownership, other storage/native adapters and all five full editions remain
required. Historical toolchain execution on contemporary Windows is not XP qualification.
