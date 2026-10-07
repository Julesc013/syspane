from pathlib import Path
from datetime import datetime,timezone
import json,re
r=Path.cwd();stamp=datetime.now(timezone.utc).isoformat()
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
def change(p,old,new):
    s=(r/p).read_text();assert old in s,p;write(p,s.replace(old,new,1))
change('README.md','The [widget-creation checkpoint]', '''The [native observation checkpoint](spec/delivery/native-observation-handoff.md)
strengthens editor verification: unavailable accessibility calls cannot count as
empty text, lost focus or completed erasure. Seven calibrated error/delay cases
and the existing native matrices retain the same product expectations. The earlier
intermittent focus failures remain unexplained; full editions remain in progress.

The [widget-creation checkpoint]''')
change('TODO.md','- [ ] W-10 complete editor:', '''- [x] W-10 native observation: explicit accessibility errors, bounded positive reads, seven calibration cases and fixed native regressions. See the [handoff](spec/delivery/native-observation-handoff.md).
- [ ] W-10 recurring focus failures: preserve X11 ownership and explicit accessibility evidence if reproduced; earlier intermittent failures do not yet have a proven cause.
- [ ] W-10 complete editor:''')
change('spec/delivery/current-state.md','The latest [widget-creation checkpoint]', '''The latest [native observation checkpoint](native-observation-handoff.md) replaces
ambiguous accessibility fallbacks with explicit text/state/interface/geometry and
selection replies. Delays, denial and disconnection cannot pass negative checks;
destroyed objects need an explicit missing-object reply and live owner. Seven
calibrations and 129 existing native cases pass with unchanged production bytes.
The earlier intermittent focus/interface failures are still unproven. Continue
responsive/flow transforms and remaining properties; use the new failure snapshots
if focus failures recur. Installed ownership and all complete editions remain open.

The earlier [widget-creation checkpoint]''')
change('spec/delivery/current-state.md','Investigate the preserved\nnative focus/interface observation failures, then close responsive/flow transforms and remaining property controls, then installed controller/catalog/policy', 'Native observation now has the checkpoint above. Close responsive/flow transforms\nand remaining property controls, then installed controller/catalog/policy')
p=r/'spec/delivery/current-state.md';write('spec/delivery/current-state.md',re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=stamp,scope='Explicit native observation and unresolved historical focus cause')),p.read_text(),count=1,flags=re.M))
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_text());w=next(w for w in v['work_units'] if w['id']=='W-10');assert w['status']=='in_progress'
w['specs'].append('SP-W10-NATIVE-OBSERVATION');w['evidence']='delivery/native-observation-handoff.md';w['notes']+=' Native observation now requires explicit wire replies for state/text/geometry/interfaces/selection, with bounded read-only recovery and seven independent live/delay/dead/denied/removed controls. The 129 existing native cases retain fixed expectations and unchanged production bytes. Historical focus-failure cause remains unproven; retain X11 and explicit query diagnostics on recurrence. Continue responsive/flow transforms and remaining properties, then installed ownership.'
write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
write('spec/delivery/native-observation-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native observation checkpoint"
description: "Explicit native evidence distinguishes unavailable observations from absent content or state."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
sp_id: "SP-NATIVE-OBSERVATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-NATIVE-OBSERVATION", "SP-WIDGET-CREATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native observation checkpoint

Source baseline: `066657a89472b0476e3d30a1a1d51a944c88789b`. The
[package](packages/w-10-native-observation.md) investigates the preceding native
focus/interface failures. Production source, binary and existing expected scenes
are unchanged. W-10 and all five complete desktop editions remain in progress.

## Findings and correction

Two bounded diagnostic matrices compare convenience APIs, explicit D-Bus replies
and X11 input focus with ordinary/large editors, 50/350-ms stops and terminated
owned children. The first probe used an initially empty field and its cleanup
resumed a timed-out call early. The corrected probe reads `Editable pane` and
records the full stop interval. Both attempts and their exact scripts are preserved.

After child exit, the old text helper reports empty text for that nonempty field;
explicit queries report ServiceUnknown. During the 350-ms stop, explicit calls
time out at approximately 200 ms while X focus stays with the editor. Convenience
API calls return successfully after approximately 350–360 ms despite their nominal
200-ms setting. The reason for that duration is not established. Neither experiment
reproduces the earlier intermittent live focus/interface failure; its cause remains
unproven. An unchanged successful matrix does not explain a historical failure.

The installed 2.52.0 upstream [state API source](https://raw.githubusercontent.com/GNOME/at-spi2-core/AT_SPI2_CORE_2_52_0/atspi/atspi-accessible.c)
contains error-suppressing state/interface paths. This explains why those APIs alone
cannot distinguish unavailable observations from absent state; it does not prove
the historical failure's cause. Pinned runtime identities and source hashes accompany
the records. The [wire interfaces](https://raw.githubusercontent.com/GNOME/at-spi2-core/AT_SPI2_CORE_2_52_0/xml/Accessible.xml)
provide explicit replies/errors for the observer boundary.

The editor harness now reads text, state, interfaces, geometry and selection through
error-reporting native calls. Only addresses are cached. Successful negative checks
require explicit replies. Removed-object erasure requires UnknownObject plus a fresh
accessible live owner; ServiceUnknown, denial, timeout and local DEFUNCT fallbacks
cannot prove it. A selection replaced between count/child/text reads is unavailable,
not empty. This race was exposed by the first stricter binding matrix, whose failure
and source snapshot remain preserved.

Read-only retries stay within the existing overall deadline. Each explicit call is
capped at 200 ms and the remaining wait budget; late replies cannot satisfy a wait.
The 200-ms disclosure deadline, held-key focus assertion, mutation count, exact
scene/storage/pixel outcomes and original fault controls remain fixed. No mutation
is retried and no held-focus assertion reactivates the control. Focus failures record
X11 ownership, accessible identity and explicit query outcomes.

## Executed evidence

Seven native calibrations pass: live, genuinely unfocused, 50-ms stop, 350-ms frozen
owner, dead owner, explicitly removed object and a separate denied D-Bus service.
The denial service calibrates protocol error handling; it is not a product policy
qualification. Nonempty retained text cannot pass erasure, and a frozen/disconnected
owner cannot provide a focus or empty-text witness.

The unchanged native matrices pass: creation 17, binding 15, content 15, snap 13,
group 11, arrangement 14, editor 20 and large-command 24. Together with calibration,
this checkpoint has 136 native cases in nine CTest families. Product binaries are
identical to the previous checkpoint; no new Windows or historical execution claim
is made. Schema/fixture, specification-tool and integrity results are recorded
separately from native evidence.

Records: `build-support/evidence/w-10-native-observation-attempts.json`,
`build-support/evidence/w-10-native-observation-native-index.json`,
`build-support/evidence/w-10-native-observation-verification.json`,
`build-support/evidence/w-10-native-observation-staging.json` and
`build-support/evidence/native-observation-handoff.json`. Source archives retain
each original attempt and frozen product/calibration inputs. Twenty duplicate native
folders (246,621,430 bytes) were removed only after matching their already committed
creation-checkpoint archives. The existing 7 GiB output budget remains in force.

## Next boundary

Close responsive/flow transforms and remaining property controls, then installed
controller/catalog/policy ownership and scene-aligned entry/restoration with independent
escape. Preserve the new snapshots if focus failures recur; do not claim their cause
has been repaired. Complete accessibility, performance, other native adapters,
historical laboratories, packaging and release gates remain open. Owned ext4/Xvfb/
D-Bus tests do not qualify an installed desktop or physical power-loss durability.
Continue Windows 9x, Windows NT, X11, Wayland and Mac OS X independently.
''')
p=r/'docs/developers/build.md';write('docs/developers/build.md',p.read_text()+'''
### Native observation calibration

After Linux workspace preflight and ordinary configure, run `ctest --preset
linux-x64-gcc13 -R "^native[.]EDITOR-OBSERVATION$" --output-on-failure`. Seven owned
cases verify explicit live, unfocused, delayed, disconnected, missing-object and
denied replies. Existing `EDITOR-WIDGET-CREATION`, `EDITOR-BINDING-AUTHORING`,
`EDITOR-CONTENT-PROPERTIES`, `EDITOR-SNAP`, `EDITOR-GROUP`, `EDITOR-ARRANGE`,
`EDITOR-FORM` and `LARGE-COMMANDS` remain required consumers of the shared observer.

`tests/editor/native_observation.py` caches addresses only. Calls have a 200-ms
ceiling and inherit any smaller remaining wait budget. Read-only retries never
repeat user input or persistence commands. No unavailable read counts as empty,
unfocused, unsupported or erased; held-key checks require positive focus throughout.
UnknownObject erasure additionally checks a live accessible owner. Per child, the
observer bounds retained addresses at 4096 and error records at 128. Reopening clears
addresses. Error records include method, unique owner, object path, duration and
explicit error; focus failures additionally record X11 ownership.

See the [handoff](../../spec/delivery/native-observation-handoff.md) for preserved
diagnostics and unresolved historical focus failures. These are native laboratory
checks, not installed-desktop or historical-platform qualification.
''')
p=r/'.gitattributes';write('.gitattributes',p.read_text()+'\n# Preserve exact native observation attempts, frozen inputs and diagnostic helpers.\nbuild-support/evidence/w-10-native-observation-history/** -text whitespace=cr-at-eol\n')
print('Updated documentation and existing W-10 entry point.')
