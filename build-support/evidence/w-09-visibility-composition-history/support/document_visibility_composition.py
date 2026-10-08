from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();now=datetime.now(timezone.utc).isoformat()
def write(p,text):p.write_text(text,encoding='utf-8',newline='\n')
paragraph="""The [borrowed visibility composition checkpoint](LINKvisibility-composition-handoff.md)
adds bounded batch reads and ordered group/child decisions under one protected
telemetry borrow. Hidden ancestors cannot suppress unresolved child diagnostics.
Native conditional pixels, accessibility and private controls remain the next gate;
this shared component does not enable the native feature or complete an edition.

"""
for name,prefix in [('README.md','spec/delivery/'),('spec/delivery/current-state.md','')]:
 p=r/name;s=p.read_text(encoding='utf-8');needle='The [visibility-admission checkpoint]';assert s.count(needle)==1
 s=s.replace(needle,paragraph.replace('LINK',prefix)+needle,1)
 if name.endswith('current-state.md'):
  lines=s.splitlines();lines=[('updated: '+json.dumps({'by':'codex','at':now,'scope':'Borrowed visibility composition; native feature and complete editions remain open'})) if l.startswith('updated:') else l for l in lines];s='\n'.join(lines)+'\n'
 write(p,s)
p=r/'TODO.md';s=p.read_text(encoding='utf-8');needle='- [ ] W-09/W-10 native conditional visibility:';assert s.count(needle)==1
s=s.replace(needle,'- [x] W-09 borrowed visibility composition: bounded shared reads, ordered group inheritance, unsuppressed unresolved diagnostics and fail-closed denial. See the [handoff](spec/delivery/visibility-composition-handoff.md).\n'+needle);write(p,s)
p=r/'docs/developers/build.md';s=p.read_text(encoding='utf-8')+"""

The [borrowed composition package](../../spec/delivery/packages/w-09-visibility-composition.md)
adds `scene::project_bindings` for ordered queries sharing one union of protected
DataView borrows. Its work/output limits apply to the whole batch. Use
`scene::project_scene_visibility` for authored preorder, inherited content gates
and independent unresolved diagnostics. Neither callback may retain payload or
decisions or reenter contributing views; these helpers create no native cache.
A content composer must also preserve current content authorization and mandatory
status. SceneSurface's refusal gate remains in force until that owner is verified.

Run `ctest --preset <profile> -R '^(scene[.]|editor[.]VIS-|composition[.])'
--output-on-failure`, followed by the full non-native suite. The new families are
VISIBILITY-BATCH-ORDER/ISOLATION/BOUNDS/LIFETIME and VISIBILITY-TREE-CASES/LIFETIME.
The frozen hierarchy examples are tests/scene/visibility-composition-cases.json.
Existing native SCENE-SURFACE, SCENE-INSPECTOR-MODEL, SCENE-ERASURE, EDITOR-LOCKS
and EDITOR-CONTAINERS remain regression checks; they do not qualify conditional
native pixels. The [handoff](../../spec/delivery/visibility-composition-handoff.md)
preserves the original failed fixture and the exact schema-based correction.
""";write(p,s)
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes());row=next(w for w in v['work_units'] if w['id']=='W-09');row['package']='delivery/packages/w-09-visibility-composition.md';row['evidence']='delivery/visibility-composition-handoff.md';row['notes']+=' Borrowed batch queries and visibility-tree composition now preserve same-view lifetime, inherited content gates and independent unresolved diagnostics. Native conditional pixels/accessibility/controls remain gated; complete editions stay open.';write(p,json.dumps(v,indent=2)+'\n')
p=r/'.gitattributes';write(p,p.read_text(encoding='utf-8')+'\n# Preserve borrowed-composition failures, fixed examples and execution helpers.\nbuild-support/evidence/w-09-visibility-composition-history/** -text whitespace=cr-at-eol\n')
p=r/'spec/delivery/visibility-composition-handoff.md';write(p,'---\ntype: "SysPane Work Record"\ntitle: "Borrowed visibility composition checkpoint"\ndescription: "Bounded shared telemetry reads and inherited condition decisions with native presentation still gated."\ntags: ["delivery", "experience", "assurance"]\nstatus: "draft"\ngenerated: {"by": "codex", "at": "STAMP"}\nsp_id: "SP-VISIBILITY-COMPOSITION-HANDOFF"\nsp_profile: "syspane-spec/0.1.0"\nsp_authority: "informative"\nsp_requires: ["SP-W09-VISIBILITY-COMPOSITION", "SP-VISIBILITY-ADMISSION-HANDOFF"]\nsp_review: "unreviewed"\nsp_sources: ["SRC-CONVERSATION"]\n---\n\n# Borrowed visibility composition checkpoint\n\nSource baseline: f4d888b9d4130eb701371f024daf3643f7c1bb65. The\n[package](packages/w-09-visibility-composition.md) and independently enumerated\nhierarchy outcomes were frozen before production changes.\n\n## Implemented boundary\n\nproject_bindings routes ordered queries through one union of DataView borrows.\nDuplicate same-source queries cannot reenter a view. Unavailable or denied inputs\nremain isolated to their queries; bounded work/output exhaustion returns atomic\ncapacity without partial payload. Every successful result is consumed inside its\noriginal protected lifetime. The existing single-query API keeps its behavior.\n\nproject_scene_visibility evaluates every own condition in authored preorder,\nprojects the first ancestor blocker and keeps unresolved diagnostics separate from\ncontent gating. A false ancestor cannot remove a child\'s diagnostic. Any denied\ncondition restricts the whole result. Revocation/regrant cannot restore prior data.\nNo native cache, collection demand or authored mutation is introduced.\n\nSceneSurface still refuses scene 0.5. The tree projection does not settle native\nwarning geometry, retained layout space, accessible absence or private editor input.\nThose remain required before renderer enablement; no native visibility qualification\nor complete-edition claim follows from these shared APIs.\n\n## Executed evidence and preserved failures\n\nAll 90 affected checks pass on each development profile. Full non-native suites\npass 331 Linux GCC13, 328 Windows GCC15 and 325 v141_xp checks (984 total).\nThe historical toolset ran on contemporary Windows, not on an XP laboratory.\nFive native regressions pass: SCENE-SURFACE, SCENE-INSPECTOR-MODEL, SCENE-ERASURE,\nEDITOR-LOCKS and EDITOR-CONTAINERS. Three native archives preserve 26 scenarios,\nincluding deliberate retained-pixel/accessibility and editor fault controls.\n\nThe first build rejected misleading indentation in a new test helper. The first\nhierarchy fixture omitted required empty group content objects. Independent\nJSON Schema validation identified precisely those two missing properties; their\naddition leaves every rule and expected output unchanged. The original fixture,\nfrozen hashes, failure output and correction record remain preserved. A subsequent\nboundary test incorrectly assumed 256 nested levels; it now exercises 256 widgets\nat the existing depth limit of 16 and explicitly rejects depth 17. No production\nschema or prior acceptance oracle was weakened.\n\nRecords: build-support/evidence/w-09-visibility-composition-attempts.json,\nw-09-visibility-composition-native-index.json, w-09-visibility-composition-verification.json,\nw-09-visibility-composition-staging.json and visibility-composition-handoff.json.\nThey bind source archives, commands, artifacts, failures and fixed examples.\nTwenty-five native folders and forty attempt folders were verified against the\nbaseline commit before reclaiming 130,456,560 bytes of duplicate evidence. The\n7 GiB combined workspace bound remains unchanged.\n\n## Required continuation\n\nUse these shared projections in the existing serialized native presentation owner.\nKeep content and condition authorization independent, retain authored layout space\nand selection, and preserve mandatory status outside predicates. Freeze diagnostic\nplacement, group masking, chart/image lifetime, held gestures and accessibility\noutcomes before enabling conditional pixels. Implement private native rule controls\nand independently observe save/reopen, lost acknowledgement, erasure and deliberate\ninverted/retained-content faults. W-09/W-10, typography, clipboard/recovery drafts,\ninstalled ownership, remaining adapters/laboratories and all five complete editions\nremain open. Historical accessibility timeout causes remain unresolved.\n'.replace('STAMP',now))
print('Documentation updated without changing frozen contracts or expected outcomes.')
