---
type: "SysPane Work Record"
title: "Theme typography and native font-role checkpoint"
description: "Versioned font roles with resource admission and native raster evidence; scene and authoring integration remain open."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T02:15:13.857835+00:00"}
sp_id: "SP-TYPOGRAPHY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-TYPOGRAPHY", "SP-VISIBILITY-CONTROLS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Theme typography and native font-role checkpoint

Source baseline: 952d90e80dd53d35bdfdbf50eb2e4e444585bd45. The
[package](packages/w-09-typography.md) closes versioned font meaning and native
text admission without changing existing theme, scene or command identities.

Theme 0.2 adds complete family/size/weight/style fonts and optional body, label,
value and diagnostic roles. Shared resolution returns an owned exact font;
absent roles use the base font. Theme 0.1 retains weight 400 and normal style.
Native setters treat the family as literal data and preserve current fallback,
contrast, alpha, scale, shaping and pixel limits. No new font download or cache
owner is introduced. Immutable content resolution derives theme.typography as
a required capability and applies existing policy authorization and exact pins.

The role-aware scene compositor and native theme-authoring controls remain open.
SceneSurface reports surface.typography_unavailable for theme 0.2 with empty
published caches, including when display is disabled. Current disclosure denial
keeps priority. Replacing it with a legacy theme resumes without old payloads.
This prevents a default body font from masquerading as complete role composition.

## Executed evidence

All 162 affected checks pass on each development profile. Full portable suites
pass 339 Linux GCC13, 336 Windows GCC15 and 333 v141_xp checks (1008 total).
The historical compiler runs on contemporary Windows; no historical qualification
is inferred. Portable tests exercise literal role results, all supported styles
and weights, invalid fonts and roles, ownership, exact theme pins and capability
omission/denial even when a manifest omitted the new required capability.

The new native oracle passes eleven cases. Raw raster observations verify legacy
equivalence, four literal role-to-base comparisons, bold/italic differences,
fractional-size scale invariance, literal missing-family fallback, light/dark
contrast and rejection without partial output. Ignoring a requested role or weight
produces a positive pixel difference. Existing text and scene tests, three native
editor matrices and fifteen rendering regressions also pass.

32 source-bound attempts and 28 native archives
preserve actual commands, fixed inputs, source bytes, runtime/artifact identities
and outcomes. 5 build/test attempts failed. Initial compilation caught
a missing namespace brace and misleading indentation in a test; both original
attempts remain recorded. v141_xp then accepted a family containing LF where GCC
rejected it through the regex. Explicit UTF-8 byte validation now enforces all
forbidden family controls, commas and edge spaces independently of native regex
behavior. Its unchanged invalid-font examples pass. A separate resource test
failure exposed null IDs produced by a temporary JSON reference inside the test
pin helper's conditional expression under this compiler. The preserved diagnostic
prints those malformed pins. Owning the parsed document and copying its ID before
constructing the pin fixes the fixture without changing the expected resource
identity or production resolver. Evidence lives in out/evidence under
w-09-typography-attempts.json, w-09-typography-native-index.json,
w-09-typography-verification.json, w-09-typography-staging.json and
typography-handoff.json.

The first package/schema/literal-case freeze preceded production additions.
Before builds, the schema assigned C1-control rejection to explicit Unicode
semantic validation because byte-based C++ regex cannot interpret Unicode ranges
portably. The literal invalid-font expectations and required rejection did not
change. Original and revised archives remain. The two standalone resolver files
had already been written when that refinement helper ran; changes to existing
production files followed the refinement. The freeze clarification records this
sequence rather than claiming the revised archive preceded every production byte.

All 176 baseline schema/fixture files remain unchanged. Cleanup verified committed
archives before removing 38 native folders and 49 attempt folders from owned
outputs. One build preflight stopped before launch when its standard reservation
did not fit. Commit a4673c4 preserves raw typography evidence before reclaiming
its duplicate outputs; it does not claim a finished feature. The attempt register
records both source bases. The original records remain in Git, cleanup receipts are retained, and
the development allocation stays 7 GiB with existing action reservations.

## Required continuation

Assign every scene text role, including tables, charts, images and mandatory source
or visibility diagnostics; preserve geometry/erasure/resource limits and test actual
pixels before enabling theme 0.2 in SceneSurface. Then add native theme-authoring
controls with exact immutable resource publication and the existing reversible
draft and durable transaction owners. Do not mutate packaged theme bytes in place.
Continue clipboard authority, recovery drafts, installed entry/restoration and the
remaining native adapters and laboratories. W-09/W-10 and all five editions remain
open; older unexplained accessibility timeouts remain unresolved.
