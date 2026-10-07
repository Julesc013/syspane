---
type: "SysPane Work Package"
title: "Native scene inspector navigation and disclosure"
description: "Expose scene semantics through native controls with identity-stable navigation and current inspector authority."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T01:10:45Z"}
sp_id: "SP-W11-SCENE-INSPECTOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-ACCESSIBILITY", "SP-SETTINGS", "SP-W09-SCENE-IMAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native scene inspector navigation and disclosure

W-11 now admits the native scene inspector boundary under the user's complete
desktop release instruction. Its prerequisites are the implemented scene/content,
binding, native chart/image and policy components, not completion of every platform
adapter in W-08/W-09. Keep those work units and the rest of W-11 open. Implement in
`source/interfaces/`, using the existing renderer; no competing model, scheduler,
document schema or private edit path. This package does not qualify installed
controller routing, settings/editing, clipboard/export, a screen reader's usability,
or Windows/Mac adapters.

## Authority and lifetime

Add a typed desktop/inspector audience to SceneSurface, defaulting to desktop for
existing callers. It selects the DataView/telemetry channel and operational policy
check; accessibility and chart-history checks remain independently required. The
existing authenticated native role is unchanged (normally desktop). A desktop
grant or desktop-bound connection alone cannot authorize inspector delivery.
Resources, lease, image worker and measured-time semantics remain unchanged.

SceneInspector owns one inspector-audience SceneSurface and its GTK controls on
one serialized UI thread. Expose its embeddable widget and typed attach/receive,
heartbeat/gap/disconnect, refresh, policy, replace, close and image-drain operations.
No public method exposes an unchecked mutable SurfaceFrame or stores a borrowed
pointer. The caller supplies the same current tick context as SceneSurface. The
host owns its window/main loop and drains cancelled workers before destruction.

Ordinary telemetry/refresh operations are one synchronous native presentation
transaction: SceneSurface's clear request is deferred only within that operation,
then a newly authorized frame replaces the affected native rows before returning.
Do not enter the main loop or deliver user callbacks inside it. Any error clears
the model before propagating. Policy, scene/resource/topology replacement, close,
owner-clock failure and unusable frames clear native strings, row identities,
selection and requested summary. These are never deferred past the owning call.
Regrant requires the existing fresh attachment/full state; it cannot resurrect
cached observations, points or decoded images. No automatic clipboard publication.

## Semantic projection

Extend the synchronous frame with authored widget title and chart identity/points,
including the exact typed number, measurement nanoseconds, generation and segment
continuity. Keep existing rendered and accessible strings unchanged. Include added
identity/string storage in the existing 262144-byte frame budget and bounded chart
point storage; do not raise prior limits.

Use a native two-column tree table, labelled Item and Information. Authored groups
preserve hierarchy and scene order. Scalar/text/status/image rows expose their
complete accessible content, including source states and image alt/status. Table
roots expose the summary, child rows identify producer/epoch/entity and generation,
and their children expose every selected column label, invariant field and complete
cell value/status. Chart roots expose the complete accessible summary; child rows
expose every retained point's exact value/unit, measured time, generation and
start/join state. No point decimation or parsing of rendered text to recover data.

Keys are structured tuples, not delimiter concatenation: scene id + widget id;
table keys additionally include producer, epoch, entity and field (generation is
content, not row identity); chart keys include the full ChartIdentity and measured
nanoseconds (generation is content). A reused entity name in another epoch or an
equal timestamp in a different chart stream is a different row.

Reconcile native rows by these keys. Update only changed cells, retain expansion
and the selected object when unrelated rows are inserted, removed or reordered,
and retain its focused column. If the selected row disappears, select its nearest
surviving ancestor; if none survives, leave selection empty. Do not select the new
occupant of an old row number. Ordinary value refresh does not rebuild the tree,
grab focus, request speech, or update a live summary. A native Summary button
provides the selected row's last presented information on explicit activation; subsequent
ordinary updates retain that requested snapshot until another request, selected-row
removal, policy/resource/scene replacement or close. Label it as a requested summary,
not current telemetry. Clear removed rows' strings before removing native objects.

Use native Left/Right column navigation, Shift-Left/Shift-Right collapse/expand,
and Up/Down row navigation, Tab/Shift-Tab between tree and Summary, Space/Enter
button activation. The pinned GTK binding-table experiment corrected the initial
plain-arrow expansion assumption; preserve that original package and failed key
trace. The required observed collapse/expansion and selection outcomes are unchanged.
No new global key grabs. Controls
follow native theme/high contrast and text scaling; scene styling does not restyle
the inspector. Chrome labels have stable translation IDs with bounded UTF-8 text;
authored/device text is plain text, never markup. Broader locale formatting and
human review remain required in W-11/W-22.

Prepare a complete semantic tree before changing GTK. Admit at most 65536 rows,
2 MiB total UTF-8 key/label/information bytes and 258 levels; reject invalid UTF-8,
duplicate keys or malformed frame hierarchy without partial disclosure. These are
separate native-model limits, not image/pixel budgets. Existing renderer limits
still govern obtaining a frame. Native controls may have additional measured memory
overhead; product performance remains a qualification gate.

## Executable acceptance and evidence

Before implementation preserve exact fixture/oracle inputs. Bind child cases under
T-ACCESSIBILITY: CHANNEL, TREE, KEYBOARD, IDENTITY, SUMMARY, TABLE, CHART, IMAGE,
REVOKE, REGRANT, OLD-REFERENCE, CLOSE and BOUNDS. Exercise real admitted wire frames,
typed chart points and decoded images. Independent AT-SPI traversal must see the
native tree/table roles and exact expected content; real XTest keys must navigate
the owned window. Retain references to old native cells across revoke and confirm
that they no longer disclose the old value. Check disabled inspector/accessibility,
history and resource grants independently, including desktop-only authority and
the wrong telemetry channel. Keep the 200 ms post-revocation observation bound.

Use separate deliberate retained-content and wrong-selection controls to prove
the observer rejects the corresponding failure. Test public non-Latin/RTL content
and long translated chrome without changing data identities. Programmatic checks
cannot count as representative human screen-reader review.

Run ordinary workspace preflight/configure/build in the pinned linux-x64-gcc13
profile, then `ctest --preset linux-x64-gcc13 -R 'native.SCENE-INSPECTOR' --output-on-failure`.
Keep affected scene/policy/component regressions on all development profiles and
the external scene erasure families. Preserve commands, source/artifact/runtime and
oracle hashes, failures and the concrete next integration step in a handoff. GTK
TreeStore and TreeView use the pinned GTK 3.24.41 runtime; the relevant native APIs
are documented in [TreeStore](https://docs.gtk.org/gtk3/class.TreeStore.html) and
[TreeView accessibility](https://docs.gtk.org/gtk3/class.TreeViewAccessible.html).
