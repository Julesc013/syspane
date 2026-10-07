from pathlib import Path
from datetime import datetime,timezone
import json,re,subprocess
r=Path.cwd();stamp=datetime.now(timezone.utc).isoformat();base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
def change(p,old,new):
 s=(r/p).read_text();assert old in s,p;write(p,s.replace(old,new,1))
change('README.md','The [content-properties checkpoint]', '''The [binding-authoring checkpoint](spec/delivery/binding-authoring-handoff.md)
adds native selectors, explicit pins, ordered filters/sort keys and atomic table
query edits. Exact integer predicates and escaped control-character text survive
save/reopen. Independent native tests cover preview, persistence, cancellation,
restart and erasure. Installed routing and complete editions remain open.

The [content-properties checkpoint]''')
change('README.md','cancellation and disclosure erasure have independent native evidence. Binding\nauthoring, remaining editor controls and installed editions remain open.','cancellation and disclosure erasure have independent native evidence. Binding\nauthoring now has the checkpoint above; remaining controls and installed editions remain open.')
change('TODO.md','- [ ] W-10 complete editor:', '- [x] W-10 native binding authoring: exact typed selectors/pins, ordered predicates/sort keys, atomic table queries, lossless text and independent native save/recovery/erasure evidence. See the [handoff](spec/delivery/binding-authoring-handoff.md).\n- [ ] W-10 complete editor:')
change('docs/users/configuration.md','These controls currently run in the owned Linux development editor. Binding\ncreation, new non-text widgets, remaining properties and installed desktop routing\nare still pending.', 'These controls currently run in the owned Linux development editor. New non-text\nwidgets, remaining properties and installed desktop routing are still pending.')
with (r/'docs/users/configuration.md').open('a',encoding='utf-8',newline='\n') as f:f.write('''
## Bindings in the development editor

Select one value, status, chart or table and choose **Bindings**. Target controls
edit a selector, a direct producer/epoch/entity pin or a persistent namespace/key.
Selectors use an explicit host, session or registered-asset scope. Filter and Order
tabs add, remove and reorder predicates and sort keys. Numbers retain exact whole
values within signed/unsigned 64-bit limits. Text and boolean are distinct types.
For tables, choose the column to change its value field; target/filter/order changes
apply to every column together, preserving labels and order. Duplicate fields reject.

**Set bindings** creates one reversible draft change; **Apply** saves it. Invalid
input stays available for correction. Cancel bindings discards private input only.
Missing sources stay missing; entering a persistent key does not create a mapping
or grant access. Existing legacy pins stay inert until explicitly rebound.

Text normally uses literal format. Escaped format accepts one quoted string, such
as `"a\\tb"` for a tab or `"a\\\\tb"` for a literal backslash and t. Existing control
characters automatically open in escaped format. The saved value remains the
decoded text; choosing a format determines how the current buffer is interpreted.
The existing 512-character limit applies after decoding. Policy/owner changes
erase all input, including hidden rows. See the [recorded scope](../../spec/delivery/binding-authoring-handoff.md).
''')
with (r/'docs/developers/build.md').open('a',encoding='utf-8',newline='\n') as f:f.write('''
### Native binding authoring

`source/interfaces/editor_binding.*` projects bounded private fields into existing
binding descriptors and one WidgetContentEdit. The lazily created GTK dialog owns
no DataView, persistent mapping or transaction ledger. The shared validator and
EditorDraft remain authoritative. Private text allows a caller-supplied 4096-character
editing buffer for escaped strings; all existing controls retain their own limits.

After ordinary preflight and profile build, run `ctest --preset <profile> -R "^editor[.]BINDING-" --output-on-failure`.
The seven families use fixed complete scenes and exact text/number values. In the
unprivileged Linux laboratory run `ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-BINDING-AUTHORING$" --output-on-failure`.
Fifteen cases operate actual controls, compare pixels/accessibility and coherent
stored resources, reopen and challenge deliberate storage/preview/retention faults.
The original binding cases and supplemental escaped-text cases remain separate
frozen inputs. Rerun existing content, snap, group, arrange, editor, settings and
large-command matrices when changing shared native ownership or private controls.
See the [handoff](../../spec/delivery/binding-authoring-handoff.md) for exact evidence.
''')
with (r/'spec/experience/editor.md').open('a',encoding='utf-8',newline='\n') as f:f.write('''
## Native binding-authoring boundary

The [binding-authoring package](../delivery/packages/w-10-binding-authoring.md)
defines typed selectors/pins, private ordered predicate/sort buffers and atomic
table query edits. The [text extension](../delivery/packages/w-10-binding-text.md)
preserves control characters through an explicit escaped format. Existing resolver,
policy, history and persistence owners remain authoritative. The
[checkpoint](../delivery/binding-authoring-handoff.md) records scoped evidence;
provider discovery, installed routing and complete editions remain open.
''')
change('spec/delivery/current-state.md','# Current state and next admitted boundary\n', '''# Current state and next admitted boundary

The latest [binding-authoring checkpoint](binding-authoring-handoff.md) adds native
selectors and explicit pins, ordered predicates/sort keys, exact integer values,
lossless text and atomic table queries. Next close non-text insertion, responsive/
flow transforms and remaining property controls, then installed controller/catalog/
policy ownership and independent entry/restoration. W-10 and all complete editions
remain in progress.
''')
change('spec/delivery/current-state.md','Next close binding authoring, non-text insertion,','Binding authoring now has the checkpoint above. Next close non-text insertion,')
p='spec/delivery/current-state.md';s=(r/p).read_text();s=re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=stamp,scope='Native binding authoring, exact text/number input and remaining editor boundaries')),s,flags=re.M);write(p,s)
p='spec/delivery/work-units.json';v=json.loads((r/p).read_text());w=next(w for w in v['work_units'] if w['id']=='W-10');w['specs']+=['SP-W10-BINDING-AUTHORING','SP-W10-BINDING-TEXT'];w['package']='delivery/packages/w-10-binding-authoring.md';w['evidence']='delivery/binding-authoring-handoff.md';w['notes']+=' Native binding authoring now edits typed selectors/pins and ordered filter/sort rows through atomic table/scalar content edits. Exact integers, escaped control text and native persistence/erasure checks preserve existing semantics. Provider discovery, non-text insertion and remaining editor/installed boundaries remain open.';write(p,json.dumps(v,indent=2)+'\n')
write('spec/delivery/binding-authoring-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native binding-authoring checkpoint"
description: "Typed selectors and explicit pins through the existing native draft and resolver."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
sp_id: "SP-BINDING-AUTHORING-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-BINDING-AUTHORING", "SP-W10-BINDING-TEXT", "SP-CONTENT-PROPERTIES-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native binding-authoring checkpoint

Source baseline: `{base}`. The
[package](packages/w-10-binding-authoring.md) adds bounded native binding controls
through the existing EditorDraft, validator, resolver and resource transaction.
W-10 remains in progress. Table columns keep their labels/order and distinct fields
while sharing one edited query. Scalar selectors retain singleton ambiguity rules;
direct and persistent pins never acquire name-based fallback or mapping authority.

Typed predicates preserve exact int64/uint64 integers, finite binary64 numbers,
booleans and literal text. Review found that the existing private text widget rejects
some valid binding characters. The separately frozen
[text extension](packages/w-10-binding-text.md) adds explicit escaped input and
lossless opening/reopening without changing binding schemas or decoded limits.
Modal buffers remain outside history; one validated Set changes the draft and
Apply separately commits it. Cancellation/no-op Set preserve the preview. Owner and
policy changes erase fields, hidden row buffers and choice models.

## Verification

Original descriptors, resource bytes, full expected scenes and supplemental text
cases were frozen before their production changes. Seven portable families cover
all descriptor forms, scopes, exact numbers, control text, limits, table coupling,
invalid atomicity, history, request bytes and policy rejection. All 118 affected
checks pass on each of Linux GCC 13, Windows GCC 15 and v141_xp on contemporary
Windows. This is not an XP runtime qualification.

Fifteen owned Linux binding cases operate actual controls, verify resolver output
and pixels, compare coherent stored scene/resource bytes, reopen, cancel requests,
recover lost acknowledgements and erase held accessible references. Incorrect stored
bindings, frozen pixels and retained private text have positive distinguishing
witnesses. Existing content (15), snapping (13), grouping (11), arrangement (14),
editor (20), settings (18) and large-command/storage/IPC (24) matrices also pass:
130 native cases across eight matrices. The display remains the previously admitted
640x560 DIP at 3/4 scale for content/binding cases; authored scenes remain unchanged.

Preserved failures include misleading-indentation compilation warnings, a test
incorrectly trying to reopen a permanently closed draft, and omission of the new
test source from the component ownership manifest. The native observer needed the
exported PAGE_TAB role, positive completion of asynchronous row additions/moves,
and tolerance for an empty accessible description before the next paint. The settings
observer encountered a child destroyed between its count and indexed retrieval; it
now skips that absent child while still requiring positive live controls and values.
Its original failure is preserved. Only this nested settings observation routine
changed after the other successful checks; imported storage/resource helpers and
all product code remained identical. The rerun uses the corrected observer. Corrections
retain exact expected scenes, binding values and deadlines. The earlier isolated
held-focus failure is still recorded in the previous checkpoint; these passing
matrices do not establish its original cause.

Repository evidence paths (outside the standalone specification bundle):
`build-support/evidence/w-10-binding-authoring-attempts.json`,
`build-support/evidence/w-10-binding-authoring-native-index.json`,
`build-support/evidence/w-10-binding-authoring-verification.json`,
`build-support/evidence/w-10-binding-authoring-staging.json` and
`build-support/evidence/binding-authoring-handoff.json`.

The workspace guard stopped a build before its reservation exceeded 7 GiB. Only
verified duplicates of committed native archives were removed; original archives,
source identities and failures remain. Cleanup records accompany the attempts.

## Next admitted boundary

Close non-text insertion, responsive/flow transforms, lock/visibility/typography,
clipboard authority and recovery drafts. Complete provider/catalog discovery and
installed controller/policy ownership, scene-aligned entry/restoration and independent
escape. Continue other adapters and historical labs independently. Owned ext4/Xvfb/
DBus checks do not qualify installed editing, physical power-loss durability,
full accessibility/performance or any complete edition. Two existing Windows
symlink tooling assertions remain skipped. Windows 9x, Windows NT, X11, Wayland and
Mac OS X release scope is unchanged.
''')
with (r/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n# Preserve exact native binding attempts, frozen inputs and helpers.\nbuild-support/evidence/w-10-binding-authoring-history/** -text whitespace=cr-at-eol\n')
print('Updated binding checkpoint documentation.')
