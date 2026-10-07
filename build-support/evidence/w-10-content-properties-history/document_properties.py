from pathlib import Path
from datetime import datetime,timezone
import json
r=Path(__file__).resolve().parents[2];now=datetime.now(timezone.utc).isoformat()
def write(path,s):(r/path).write_text(s,encoding='utf-8',newline='\n')
def before(path,needle,text):
 s=(r/path).read_text();assert needle in s;write(path,s.replace(needle,text+needle,1))
before('README.md','The [snapping checkpoint]', '''The [content-properties checkpoint](spec/delivery/content-properties-handoff.md)
adds a native dialog for table labels/order, chart controls, immutable image choices
and scene themes. Buffered edits apply as one undoable change; save/reopen,
cancellation and disclosure erasure have independent native evidence. Binding
authoring, remaining editor controls and installed editions remain open.

''')
before('TODO.md','- [ ] W-10 complete editor:', '- [x] W-10 native content properties: bounded table/chart/image/theme buffers, atomic history, immutable resource choices and independent native persistence/erasure checks. See the [handoff](spec/delivery/content-properties-handoff.md).\n')
before('spec/delivery/current-state.md','The latest [snapping checkpoint]', '''The latest [content-properties checkpoint](content-properties-handoff.md) adds
bounded table, chart, image and scene-theme input through the existing atomic
draft and resource owners. Next close binding authoring, non-text insertion,
responsive/flow transforms and remaining property controls, then installed
controller ownership and independent entry/restoration. W-10 remains in progress;
complete editions and historical qualification remain open.

''')
p=r/'spec/delivery/current-state.md';s=p.read_text().replace('The latest [snapping checkpoint]','The earlier [snapping checkpoint]');s='\n'.join('updated: '+json.dumps(dict(by='codex',at=now,scope='Native content properties, independent persistence/erasure evidence and remaining editor boundaries')) if line.startswith('updated:') else line for line in s.split('\n'));write(p.relative_to(r),s)
p=r/'spec/delivery/work-units.json';d=json.loads(p.read_text());rows=next(v for v in d.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'id' in v[0]);row=next(x for x in rows if x['id']=='W-10');row['specs'].append('SP-W10-CONTENT-PROPERTIES');row['package']='delivery/packages/w-10-content-properties.md';row['evidence']='delivery/content-properties-handoff.md';row['notes']+=' Native content properties now buffer table labels/order, chart options, exact image choices and scene themes, with one atomic draft operation and independent persistence/erasure evidence. Binding authoring, non-text insertion and remaining editor/installed boundaries stay open.';write(p.relative_to(r),json.dumps(d,indent=2)+'\n')
for path,text in {
 'spec/experience/editor.md':'''\n## Native content-property boundary

The [content-properties package](../delivery/packages/w-10-content-properties.md)
defines table-label/binding permutations, active chart-axis serialization, exact
image choices and scene-theme inheritance. Modal input stays outside authored
history. One validated batch changes content/theme; Cancel and value-identical Set
preserve the preview. Disclosure loss erases fields and native choice models.
The [checkpoint](../delivery/content-properties-handoff.md) records executed scope
and remaining binding/authoring/installed acceptance.
''',
 'docs/users/configuration.md':'''\n## Content properties in the development editor

Choose **Content** with clean basic property fields. For a table, select a source
column, edit its label and use Move column up/down to move the label and source
together. Chart controls set the history window (1,000–3,600,000 ms), point limit
(2–4,096), interpolation and automatic/fixed axis. Image controls choose an admitted
asset, alternative text, preferred dimensions (1–4,096 DIP) and fit. Scene theme
offers an admitted theme or Inherit settings, even with no selected widget.

**Set content** applies one undoable draft change; **Apply** saves it. Cancel content
discards only the dialog buffer. Invalid values leave the draft unchanged and stay
available for correction. A policy change closes and clears the dialog; disclosure
regrant requires Reload. Text body remains in the basic property fields.

These controls currently run in the owned Linux development editor. Binding
creation, new non-text widgets, remaining properties and installed desktop routing
are still pending. See the [recorded scope](../../spec/delivery/content-properties-handoff.md).
''',
 'docs/developers/build.md':'''\n### Native content properties

The shared content projection lives in `source/interfaces/editor_content.*` and
uses EditorDraft for atomic validation/history. The private GTK dialog owns only
bounded input and admitted resource-choice buffers. Frozen scenes, package bytes
and pins are in `tests/editor/content-properties-{cases,fixture}.json`.

After the ordinary profile build, run `ctest --preset <profile> -R "^editor[.]CONTENT-" --output-on-failure`.
In the unprivileged Linux laboratory, run `ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-CONTENT-PROPERTIES$" --output-on-failure`.
The native observer records a 640×560 DIP display at ¾ scale, live synthetic
telemetry, actual input, pixels, held accessible references and stored resource
bytes. Deliberate wrong-content, frozen-preview and retained-content faults must
be positively distinguished. Run the existing snap/group/arrange/editor/large-command
matrices after changes to the shared native owner. See the
[handoff](../../spec/delivery/content-properties-handoff.md) for source-bound evidence.
'''
}.items():write(path,(r/path).read_text()+text)
header=f'''---
type: "SysPane Work Record"
title: "Native content-properties checkpoint"
description: "Bounded native table, chart, image and scene-theme buffers through existing atomic owners."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-CONTENT-PROPERTIES-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-CONTENT-PROPERTIES", "SP-SNAP-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native content-properties checkpoint

Source baseline: `ce7731133431029d72d6d39f149d59f4663e66af`. The
[package](packages/w-10-content-properties.md) adds strict portable content-input
projection and a modal native dialog. W-10 remains in progress.

Table labels stay paired with their original source bindings under a complete
permutation. Charts serialize only the active axis mode. Image choices retain exact
manifest/path/asset identity within the admitted immutable closure; theme IDs remain
subject to the existing resolver. No schema, protocol, persistence or resource-owner
replacement is introduced. Input remains private until one EditorDraft batch
validates. Cancel/no-op preserve the current preview; successful edits use normal
undo/redo and resource-aware Apply. Policy/owner changes clear text and choice models.

## Verification

The contract, immutable packages and full expected scenes were archived before
production changes. Six portable families cover mappings, inactive fields, numeric
syntax/round trips, permutations, bounds, atomic rejection, history, request bytes,
resource identity and policy rejection. All 111 affected checks pass on each of
Linux GCC 13, Windows GCC 15 and v141_xp on contemporary Windows.

Fifteen owned Linux cases cover table labels/order, both chart axes, image
replacement/fit/alt, theme/inheritance, invalid correction, buffer and request
cancellation, undo/redo, save/reopen, lost-acknowledgement restart and disclosure
erasure. Wrong committed content, stale pixels and retained content are deliberate
faults with positive distinguishing observations. Existing snapping (13), grouping
(11), arrangement (14), editor (20) and large-command/storage/IPC (24) matrices pass:
97 native cases across six final matrices.

Original failures are preserved with their source snapshots. Compilation found a
missing digest include and range-loop/signedness warnings in the new test. Native setup required the
inspector telemetry channel and a 500-ms heartbeat interval. The display is recorded
as 640×560 logical DIP at ¾ scale; the immutable authored scene remains unchanged.
The resource observer now accepts the explicit fixture while retaining its original
default. GTK observation waits for mapped controls and visible menu items, handles
duplicate exports of the same popup and retries destroyed rows after reordering.
Erasure accepts detached menu references only with a defunct object and a still-live,
accessible owner; a process or accessibility-service failure cannot count as erasure.
Theme pixels preserve cyan channel equality under glyph antialiasing. These observer
corrections do not alter frozen scene, asset or policy outcomes.

Repository evidence paths (outside the standalone specification bundle):
`build-support/evidence/w-10-content-properties-attempts.json`,
`build-support/evidence/w-10-content-properties-native-index.json`,
`build-support/evidence/w-10-content-properties-verification.json`,
`build-support/evidence/w-10-content-properties-staging.json` and
`build-support/evidence/content-properties-handoff.json`.

Only verified duplicates of committed native archives were removed to retain the
existing 7 GiB workspace budget. Cleanup identity records accompany the attempts.

## Next admitted boundary

Close binding authoring, non-text insertion, responsive/flow transforms,
lock/visibility/typography, clipboard authority and recovery drafts. Complete
installed controller/catalog/policy ownership and scene-aligned entry/restoration
with independent escape; continue other adapters and historical labs independently.

Owned ext4/Xvfb/DBus checks do not qualify installed desktop behavior, physical
power-loss durability, historical Windows, full accessibility/performance or a
complete edition. Two existing Windows symlink tooling assertions remain skipped.
The Windows 9x, Windows NT, X11, Wayland and Mac OS X release scope is unchanged.
'''
write('spec/delivery/content-properties-handoff.md',header)
write('.gitattributes',(r/'.gitattributes').read_text()+'\n# Preserve exact native content-property attempts, frozen inputs and helpers.\nbuild-support/evidence/w-10-content-properties-history/** -text whitespace=cr-at-eol\n')
print('Updated native content-property guidance and resumption records.')
