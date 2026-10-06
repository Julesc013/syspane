---
type: "SysPane Work Package"
title: "Versioned widget content and transactions"
description: "Carry explicit text, columns, chart settings and pinned images through authored validation and durable resource-bound transactions."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T22:05:00Z"}
sp_id: "SP-W09-SCENE-CONTENT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-TABLE-SURFACE", "SP-W08-RESOURCES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Versioned widget content and transactions

Preserve scene 0.2 and commands 0.2/0.3 unchanged. Scene 0.3 adds a required typed
`content` object to every widget while preserving hierarchy, bindings, layout,
identity, revision and inert extensions. Command 0.4 retains the resource-bound
command 0.3 envelope and accepts a scene 0.2 or 0.3 replacement. Old command
versions cannot carry a scene 0.3 document. Nothing is smuggled into extensions.

## Content meanings

- Text: `body` is plain text, at most 1024 Unicode scalars/4096 UTF-8 bytes and 64
  LF-delimited lines. Reject C0 controls except LF, DEL and C1 controls. It is the visible
  and accessible text. `title` remains the object's editor label. Bindings are empty.
- Value and status: empty content object and one singleton binding. Existing exact
  value/unit and mandatory state semantics remain; arbitrary formats are not enabled.
- Group: empty content and bindings; existing ordered children remain.
- Table: ordered `columns`, each with a nonempty plain `label` of at most 128
  Unicode scalars. Count equals bindings; all bindings are collection selectors
  equal after removing field, with distinct fields. Labels may repeat without
  changing field identity. Native headers use labels; accessible cells use
  `label [field]: content` when the label differs, otherwise the existing field
  form. Scoped row keys, ordering, truncation and rendering budgets remain.
- Chart: one singleton binding and explicit `window_ms` (1000..3600000),
  `max_points` (2..4096), `interpolation` (`linear` or `step`) and `axis`.
  Auto axis declares `include_zero`; fixed axis declares finite `minimum` strictly
  below finite `maximum`. Bounds are in the binding's reported unit. Window is
  measured time in the producer's qualified clock, not reception/wall-clock time;
  max_points bounds retained samples and never authorizes inventing continuity
  across missing data or producer epochs. Native sampling/decimation and chart
  accessibility remain a subsequent executable rendering contract.
- Image: no telemetry bindings. `asset` has an exact package manifest pin,
  canonical relative path and asset SHA256; `alt` is nonempty plain text of at most
  1024 scalars. Explicit width_dip/height_dip (1..4096) define its preferred box;
  `fit` is contain (preserve aspect inside), cover (preserve aspect and clip to the
  box), or stretch (fill box). Decoding is not enabled by document admission.

All content text (body, labels and alt) uses the same control-character and
64-line restrictions above. Their schema-specific scalar limits still apply.

An image must resolve within the selected immutable resource closure to an exact
manifest pin/path/digest with an image/png, image/jpeg or image/svg+xml declaration.
No external load, name fallback, case folding or source-directory read is admitted.
Use a separate dependency package for image bytes to avoid a self-referential scene
package digest. The existing verified asset-byte and closure limits remain. Missing,
wrong-media or mismatched references reject preparation, never create a partial
committed generation. A decoder must independently validate the declared media.

## Migration and authority

`upgrade_scene_content` returns a new scene 0.3 document without mutating its input.
Text copies the old title to body; table labels copy field identifiers; supported
value/status/group content becomes empty. Validate the result. Legacy chart/image
content has no recoverable authored meaning: return scene.content_required, without
guessing asset references, plot duration or dropping widgets. Already-0.3 input is
validated and copied unchanged. Keep the original document; no automatic downgrade.

Scene 0.3 resources automatically require `scene.content`; current capabilities and
policy are rechecked at native publication and presentation. Command 0.4 additionally
requires negotiated `configuration.scene-content`, command 0.4, command-result 0.1,
configuration.content and configuration.transactions. Required feature combinations
fail handshake; optional unsupported combinations are removed. Unnegotiated 0.4
commands return feature.unsupported before resource work. Existing role restrictions,
content.select, revision conflicts, request identities and 16 KiB command bound stay.

Preset previews selecting scene 0.3 produce a resource-bound command 0.4 with the
exact selection. Scene 0.2 previews preserve command 0.2 output. Explicit command
0.4 scene replacements may select either admitted scene version. Settings-only
command 0.3 edits preserve an existing scene 0.3 exactly; they do not reinterpret it.

Store the actual schema version and complete content in coherent generations.
Restart/reconciliation compares exact original request bytes and returns the
original committed revision. Activation remains pending until independently proved.
Corrupt or missing image closure cannot be repaired by silently dropping content.
Native generations containing scene 0.3 require the resource-bearing manifest.
Reject a rewritten legacy manifest even if its checksums and old command identity
are internally consistent. Bare initialization accepts scene 0.2 only; use a
resource-bound transaction to enter scene 0.3 after that baseline exists.

## Implementation and acceptance

Update the canonical schemas, fixture catalog, shared compiled validator and spec
tool together. Archive expected cases before implementation. Verify kind/content
agreement, binding counts, table shape, chart limits/order, image pins/paths/media,
plain text limits, reversible migration, old-version rejection and extension
round trips. Keep all old fixtures and schema bytes unchanged.

Run transaction/preset/session tests on all three development profiles and actual
Linux native commit/restart/reconcile/resource-loss cases with scene 0.3 text, table,
chart and image documents. Apply current capability denial before publication.
Connect native text bodies and table labels now; preserve explicit alternatives
for chart/image rendering until their respective native boundaries are implemented.
Run complete suites, historical artifact audits and spec/tool integrity checks.
Record all failures and exact source/artifact/runtime identities. W-09 and all
complete platform releases remain open.
