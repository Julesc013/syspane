from pathlib import Path
from datetime import datetime,timezone
import json,re
r=Path(__file__).resolve().parents[2]
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
def prepend(p,heading,s):
    old=(r/p).read_text();assert heading in old;write(p,old.replace(heading,heading+'\n\n'+s,1))
stamp=datetime.now(timezone.utc).isoformat()
write('spec/delivery/snap-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native grid and alignment-guide checkpoint"
description: "Bounded shared snapping with independently observed native gesture feedback and persistence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
sp_id: "SP-SNAP-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-SNAP", "SP-GROUP-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native grid and alignment-guide checkpoint

Source baseline: `01bea41e2123f69b1d71285b5ab944122efeace7`. The
[package](packages/w-10-snap.md) closes deterministic grid/alignment-guide snapping
for the existing native editor's fixed-base pointer moves and resizes. W-10 remains
in progress; this component checkpoint does not complete an installed edition.

The shared projection accepts captured geometry in signed 1/64-DIP units and
returns deltas plus guide facts. It validates bounds before arithmetic, resolves
axes independently and chooses candidates by exact distance/source/coordinate/ID/
anchor order. Grid ties go away from its origin; zero-motion axes stay unchanged.
Sibling and parent/work-area guides use leading, center and trailing anchors.
Resize changes only trailing edges. Bypass returns the raw quantized delta.
The projection cannot mutate a scene; release still uses MoveWidgets/ResizeWidget
through the existing atomic draft and resource-aware transaction owner.

The native form captures selection, siblings, parent/work area, display origin,
scale and options at press. Live telemetry cannot retarget a drag. Native toggles
enable snapping and grid display independently; spacing cycles through 4/8/16/32 DIP.
Preferences stay local to the session and do not enter authored history or storage.
Snapped outlines, magenta guide lines and accessible coordinates agree while held.
Ctrl at release bypasses snapping; arrows/numeric fields remain precise alternatives.
Grid painting is bounded to 512 lines. Cancellation, focus/topology/policy changes
and close erase transient feedback; disclosure regrant cannot revive geometry.

## Verification

The package and 17 literal input/output cases were archived before production
changes. Four portable families cover coordinates and threshold ties, resize,
union movement, guide priority/order, bypass, integer extremes, invalid inputs,
capacity, atomic history, exact submission and policy rejection/erasure.
All 105 affected CTest entries pass on Linux GCC 13, Windows GCC 15 and v141_xp
on contemporary Windows.

Thirteen private Linux native cases exercise real check buttons and spacing,
held-gesture pixels and accessible guides, grid/sibling snapping, resize,
multi-selection, release-time bypass, precise keyboard movement, Escape, option
changes, cancellation, policy erasure, durable save/reopen and lost-result restart.
The deliberate altered-commit and frozen-preview controls are positively detected.
The unchanged grouping (11), arrangement (14), editor (20) and complete-scene/
storage/IPC (24) matrices also pass: 82 native cases across five final matrices.

The first native observer moved focus before GTK finished activating a check
button. It now awaits the externally observed checked state before dragging.
The second failure was fault calibration: freezing the native preview prevents
held guide lines from appearing, before the later moved-pixel check. The observer
now identifies that specific earlier failure only when live accessible coordinates
are correct, independently sampled original pixels remain exact and durable
documents remain unchanged. Both original failures and observers are archived;
neither correction changes the frozen geometry or product implementation.

Repository evidence paths (outside the standalone specification bundle):
`build-support/evidence/w-10-snap-attempts.json`,
`build-support/evidence/w-10-snap-native-index.json`,
`build-support/evidence/w-10-snap-verification.json`,
`build-support/evidence/w-10-snap-staging.json` and
`build-support/evidence/snap-handoff.json`.

## Next admitted boundary

Close remaining binding/content/theme, lock/visibility/typography properties and
responsive/flow transforms. Complete clipboard authority and recovery drafts, then
installed controller/catalog/policy ownership and scene-aligned entry/restoration
with independent escape before mapping. Continue other adapters and historical
native qualification independently.

These owned ext4/Xvfb/DBus checks do not qualify installed desktop behavior, physical
power-loss durability, historical Windows, full accessibility/performance or a
complete edition. Two existing Windows symlink tooling assertions remain skipped.
The Windows 9x, Windows NT, X11, Wayland and Mac OS X release scope is unchanged.
''')
prepend('README.md','These are development targets; supported versions and release qualification remain open.',
'''The [snapping checkpoint](spec/delivery/snap-handoff.md) adds deterministic grid
and alignment-guide snapping to the Linux native editor. Held-drag outlines,
visible guides and accessible coordinates share one captured geometry projection.
Ctrl bypass, precise keyboard movement, undo, save/reopen and policy erasure have
independent native evidence. Full authoring and installed editions remain open.''')
prepend('spec/delivery/current-state.md','# Current state and next admitted boundary',
'''The latest [snapping checkpoint](snap-handoff.md) adds bounded grid/alignment-guide
projection, native controls and independently observed held-gesture feedback.
Next close remaining authoring/property contracts and responsive/flow transforms,
then installed ownership and scene-aligned entry/restoration with independent
recovery. Complete editions and historical qualification remain open.''')
p='spec/delivery/current-state.md';s=(r/p).read_text().replace('The latest [grouping checkpoint]','The earlier [grouping checkpoint]',1).replace('Next close snapping/grid/guides, responsive/flow container transforms and remaining','Next close responsive/flow container transforms and remaining',1).replace('Next close snapping/grid/guides and remaining','Next close remaining',1);s=re.sub(r'^updated: .*$',f'updated: {{"by": "codex", "at": "{stamp}", "scope": "Native grid/alignment guides, independent gesture evidence and remaining editor boundaries"}}',s,flags=re.M);write(p,s)
prepend('docs/developers/build.md','# Developer setup and checks',
'''The [snapping package](../../spec/delivery/packages/w-10-snap.md) defines the
pure `snap(SnapInput)` projection in editor_snap.hpp. Provide validated captured
world geometry in 1/64-DIP units; consume deltas through existing typed draft edits.
Do not rebuild targets from live telemetry during a gesture. Native adapters own
temporary guides and must erase both accessible feedback and pixels on revocation.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure`. The declared non-root Linux laboratory additionally runs
`ctest --preset linux-x64-gcc13 -R '^native[.](EDITOR-SNAP|EDITOR-GROUP|EDITOR-ARRANGE|EDITOR-FORM|LARGE-COMMANDS)$'
--output-on-failure`. Frozen inputs are tests/editor/snap-cases.json. See the
[handoff](../../spec/delivery/snap-handoff.md) for executed evidence and limits.''')
prepend('docs/users/configuration.md','is tested in a private laboratory and is not yet an installed desktop edition.',
'''Use Snap to grid or Snap to guides while dragging or resizing fixed widgets.
Magenta lines and the guide text show the chosen positions before release.
Hold Ctrl when releasing to bypass snapping. Arrow keys and numeric fields remain
precise, unsnapped alternatives. Show grid is independent of snapping; the Grid
button cycles through 8, 16, 32 and 4 DIP spacing. These preferences last for this
editor session and do not change the saved scene. Escape cancels the current drag;
changing a grid option also cancels it. Release creates one reversible draft edit.''')
prepend('spec/experience/editor.md','## Operations',
'''The [snapping package](../delivery/packages/w-10-snap.md) defines grid/alignment
projection, deterministic candidate order, native snapshot ownership and transient
guide erasure. It extends fixed-base pointer gestures; arrows and numeric fields
remain precise, unsnapped alternatives. Native snapping preferences are session
state, not authored scene content or a separate mutation path.''')
for p in ('spec/delivery/packages/w-10-editor-draft.md','spec/delivery/packages/w-10-native-editor.md'):
    s=(r/p).read_text();pos=s.index('\n## ');s=s[:pos]+'''\nThe [snapping extension](w-10-snap.md) projects a captured native gesture into
the existing MoveWidgets/ResizeWidget operations. Its exact geometry rules and
transient guide lifetime apply alongside remaining authoring requirements.
'''+s[pos:];write(p,s)
p='spec/delivery/packages/w-10-native-editor.md';s=(r/p).read_text().replace('Larger-scene transport, remaining authoring contracts/panels, snap/align/\ndistribute, clipboard, recovery drafts,','Remaining authoring contracts/panels, responsive/flow\ntransforms, clipboard, recovery drafts,');write(p,s)
p='TODO.md';s=(r/p).read_text().replace('- [ ] W-10 complete editor:', '- [x] W-10 snapping: deterministic grid/alignment guides, captured pointer projection, visible/accessible feedback and native persistence/recovery evidence. See the [handoff](spec/delivery/snap-handoff.md).\n- [ ] W-10 complete editor:').replace('entry/restoration, snap/grid/guides, responsive/flow','entry/restoration, responsive/flow');write(p,s)
p='spec/delivery/work-units.json';v=json.loads((r/p).read_text());row=next(x for x in v.get('work_units',v.get('units')) if x['id']=='W-10');row['specs'].append('SP-W10-SNAP');row['package']='delivery/packages/w-10-snap.md';row['evidence']='delivery/snap-handoff.md';row['notes']=row['notes'].replace('Snap/grid/guides, responsive arrangement','Responsive arrangement')+' Grid/alignment-guide snapping now uses a bounded shared projection and captured native gesture geometry, with independent held-guide pixels, accessible text, cancellation, persistence and erasure evidence. Remaining properties, responsive/flow transforms and installed ownership remain open.';write(p,json.dumps(v,indent=2)+'\n')
p='.gitattributes';write(p,(r/p).read_text()+'# Preserve exact snapping attempts, original inputs and execution helpers.\nbuild-support/evidence/w-10-snap-history/** -text whitespace=cr-at-eol\n')
print('Updated specs, docs, README, TODO and existing W-10 route.')
