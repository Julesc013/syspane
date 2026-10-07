from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();stamp=datetime.now(timezone.utc).isoformat()
def edit(n,old,new):
 p=r/n;s=p.read_text(encoding='utf-8');assert old in s,n;p.write_text(s.replace(old,new,1),encoding='utf-8',newline='\n')
def append(n,text):
 p=r/n;p.write_text(p.read_text(encoding='utf-8').rstrip()+'\n\n'+text+'\n',encoding='utf-8',newline='\n')
intro='''The [conditional-visibility evaluator](spec/delivery/visibility-handoff.md) now
compares policy-bound singleton values with exact numeric and unit semantics.
Missing, stale, denied and disconnected inputs remain explicit unresolved outcomes.
Versioned scene admission and native controls/rendering are the next required
integration; this checkpoint does not enable conditional widgets yet.

'''
edit('README.md','The [image-validation checkpoint]',intro+'The [image-validation checkpoint]')
edit('TODO.md','## First native campaign\n','''## First native campaign

- [x] W-09 shared conditional-visibility evaluator: bounded singleton comparisons, exact uint64/binary64 ordering, unit/type checks, current-policy borrowing and explicit unavailable outcomes. See the [handoff](spec/delivery/visibility-handoff.md).
- [ ] W-09/W-10 conditional-visibility integration: new scene/command capability admission, coherent resource/persistence/replay, atomic editor controls, group/status composition and independent native pixels/accessibility/erasure. The evaluator alone does not complete the feature.
''')
edit('spec/delivery/current-state.md','The latest [image-validation checkpoint]',intro.replace('spec/delivery/visibility-handoff.md','visibility-handoff.md')+'The earlier [image-validation checkpoint]')
edit('spec/delivery/current-state.md','No product controller, renderer, complete collector, settings/editor, saver, SDK,\nsetup adapter or complete product package exists. The independent diagnostic\nexecutable/inspector, with explicit policy-gated private preservation, is implemented on the two development profiles. No native desktop/saver/performance/\naccessibility/setup qualification ran. Test definitions stay `not_run`; concepts stay\ndraft/unreviewed and experimental contracts stay experimental. AIDE\'s binding remains\ninactive with no grants. USK and ScreenSave are not adopted runtime dependencies.\nLicense, contribution and release-identity decisions remain open.',
'''No complete installed desktop edition or qualified release package exists. The
component implementations and native experiments above have scoped executable
evidence; they do not establish full desktop, saver, performance, accessibility or
setup qualification. Inspect each acceptance definition and its linked evidence
for execution status. Concepts remain draft/unreviewed and experimental contracts
remain experimental. AIDE's binding remains inactive with no grants. USK and
ScreenSave are not adopted runtime dependencies. License, contribution and
release-identity decisions remain open.''')
append('spec/experience/scene-bindings.md','''## Conditional visibility prerequisite

The [visibility package](../delivery/packages/w-09-visibility.md) defines one bounded
comparison over a current policy-bound singleton, exact numeric/unit behavior and
explicit unresolved outcomes. The standalone [visibility schema](../contracts/visibility.schema.json)
and shared evaluator are a prerequisite, not an extension to existing scenes.
Versioned scene/command admission, native status/group composition and editor
controls remain required before enablement. The [handoff](../delivery/visibility-handoff.md)
records current execution scope.''')
append('spec/experience/editor.md','''## Conditional visibility admission

The [shared visibility package](../delivery/packages/w-09-visibility.md) closes
single-condition evaluation and fixes the next scene/native gates. Do not place
visibility properties into existing scenes or reinterpret unavailable as hidden.
Native private input, reversible draft edits, negotiated persistence, mandatory
status preservation and independent pixels/accessibility checks remain required.''')
append('docs/developers/build.md','''The [visibility evaluator](../../spec/delivery/packages/w-09-visibility.md) provides
`scene::project_visibility(rule, inputs, now_ms, sink, limits)` through syspane_scene.
The visibility 0.1 rule uses the existing singleton binding grammar and one typed
comparison with an explicit unit. The callback receives only a VisibilityCode
inside the existing policy-bound borrow; retain no operational decision or payload
and do not reenter DataView. Only shown/hidden are successful evaluations. Every
other outcome requires explicit unresolved handling by the future native owner.
Existing scene/command versions do not admit this property.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(scene[.](VISIBILITY-|BIND-)|composition[.])' --output-on-failure`, then the
affected ordinary non-native suite. The fixed inputs are
`tests/scene/visibility-cases.json`; the [handoff](../../spec/delivery/visibility-handoff.md)
records actual runs and the remaining native admission gates.''')
path=r/'spec/delivery/work-units.json';v=json.loads(path.read_bytes())
for row in v['work_units']:
 if row['id']=='W-09':
  row['package']='delivery/packages/w-09-visibility.md';row['evidence']='delivery/visibility-handoff.md';row['specs'].append('SP-W09-VISIBILITY')
  row['notes']+=' Shared conditional visibility now evaluates exact typed singleton predicates within current-policy borrows. Scene/command admission and native rendering/authoring remain the next gated integration; the feature is not enabled by this component checkpoint.'
 if row['id']=='W-10':
  row['notes']+=' Continue conditional-visibility scene/native integration from the shared W-09 visibility package; editor controls and full feature evidence are still required.'
path.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'.gitattributes';p.write_text(p.read_text().rstrip()+'\n\n# Preserve exact visibility attempts, fixed examples and execution helpers.\nbuild-support/evidence/w-09-visibility-history/** -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print('Updated documentation and work routing without changing fixed acceptance.')
