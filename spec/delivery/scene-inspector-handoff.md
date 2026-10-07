---
type: "SysPane Work Record"
title: "Native scene inspector checkpoint"
description: "Identity-stable native navigation and independently observed inspector disclosure."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T01:44:55Z"}
sp_id: "SP-SCENE-INSPECTOR-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-SCENE-INSPECTOR", "SP-SCENE-IMAGES-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native scene inspector checkpoint

Source baseline: `1d25768390f7629d7a956c9ac945cffed884368c`. The
[package](packages/w-11-scene-inspector.md) admits the initial W-11 inspector using
the implemented W-08/W-09 components. Git history identifies the resulting commit.
W-11, W-09 and all five complete desktop editions remain in progress. Existing
document schemas, wire identities and acceptance deadlines remain unchanged.

Linux SceneInspector embeds a native GTK tree table in an application-owned window.
It owns an inspector-audience SceneSurface, current policy and native controls on
one serialized UI thread. Inspector-channel telemetry and disclosure are required;
desktop permission alone is insufficient. Accessibility, chart history and resource
checks remain independent. Policy/scene replacement, failed presentation and close
clear native strings, row identities, selection and requested summaries. Image jobs
retain their existing cancellation and actual-stop ownership.

Frames carry authored titles and exact typed chart identity/points within the
existing frame budget. The semantic tree exposes groups, complete scalar/status
content, table entities and fields, every retained chart point, and image alt/status.
Structured keys preserve scoped selection when rows are inserted or updated. Removing
the selected object selects its nearest surviving ancestor, never a replacement row
at its old position. Expansion and the focused column persist. An explicitly
requested Summary is a labelled snapshot, unchanged by ordinary telemetry updates.
Native theme and chrome translation hooks are used; full localization remains open.

## Evidence and corrections

`build-support/evidence/w-11-scene-inspector-attempts.json` binds 40 configure/build/
test attempts to exact source archives, commands, artifacts and retained logs.
Final affected scene, policy, DataView and component checks passed 84 entries on
Linux and 79 on each contemporary and historical-toolset Windows profile. The latter
ran on modern Windows and makes no historical OS support claim. The Linux-only
inspector target does not enter either Windows component graph.

The independent native runner passed seven modes: scalar, table, chart, image,
translated controls, retained-content fault and wrong-selection fault. It sends real
XTest keys to the owned window and reads native tree/table cells through AT-SPI.
It verifies exact data, collapse/expansion, selected identity after insertion,
ancestor fallback after removal, explicit summary retention, revoke/regrant and
close. References to old cells are held across revocation and queried again; old
text/names must be blank or the object definitively gone within the original 200 ms
bound. Both deliberate faults must be positively detected. Exact uint64 chart
content, group hierarchy, stream identity, permission separation and model bounds
also have component checks. All five existing external scene-erasure families
passed with their original intentional faults against the final scene artifact.

Seventeen completed native reports preserve original failures and final observations.
The original expected-content JSON and existing scalar/table/chart/image fixtures
were preserved before implementation and remain byte-identical. The first native
observer and fixture source were preserved before their first execution, after
implementation had started. Subsequent source snapshots record every correction.
Native screenshots support visual inspection; they are not a pixel-comparison or
representative human accessibility qualification.

The first compile failed strict indentation checks. Early observer failures exposed
the GTK leader window sharing the real window's name, a GI Text method-name collision,
and an invalid wrong-selection fault path. The observer now identifies the actual
window by PID/name/geometry, calls the explicit AT-SPI Text interface and requires
evidence of the deliberately wrong entity. An earlier control escaped and remains
recorded as a failure. Production reconciliation was corrected to expand new
containers in parent order, retain user expansion state and avoid expanding through
a collapsed ancestor.

The initial package assumed plain Left/Right would collapse/expand. The pinned GTK
binding-table trace and actual native key receipt showed these keys move columns;
Shift-Left/Shift-Right invokes native collapse/expansion. The package and stimulus
were corrected with the original assumption and failed traces preserved. Expected
content, selection outcomes, fault detection and revocation bounds were not relaxed.
Final review also tightened exception cleanup, deferred surface closure during a
presentation callback and translated the tree's accessible name.

Only hash-verified archived duplicates were reclaimed inside owned output roots.
The 6 GiB allocation and ordinary workspace preflights remain unchanged. Schema,
fixture, navigation and integrity checks accompany the machine handoff; tooling
tests retain the existing two Windows symlink skips.

## Next integration boundary

Continue W-11/W-10 with native settings and editing through the shared authored
transaction API: close the control-to-command contract, preserve independent
expected outcomes, then exercise conflicts, policy changes, cancellation and durable
results before connecting installed scene/resource/policy/producer routing. Keep the
inspector embeddable and preserve its current disclosure and keyboard contracts.

Clipboard/export authority, complete locale formatting, representative screen-reader
review, maximum-size responsiveness, installed desktop activation/recovery and
Windows/Mac adapters remain required. The owned Linux laboratory does not qualify
behind-icons placement, a complete edition or release packaging. Historical platform
floors and designated labs remain unresolved; independent tracks may continue.
