from pathlib import Path
from datetime import datetime,timezone
import json,re
r=Path.cwd();now=datetime.now(timezone.utc).isoformat()
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
write('spec/delivery/runtime-observation-handoff.md',f'''---
type: "SysPane Work Record"
title: "Image validation cost and native observation checkpoint"
description: "Preserve complete image validation while reducing parent work and retaining unexplained accessibility failures."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-RUNTIME-OBSERVATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-RUNTIME-OBSERVATION", "SP-FOCUS-IDLE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Image validation cost and native observation checkpoint

Source baseline: `330c9772c73928d83a974b051c599190006d60f8`. The
[package](packages/w-09-runtime-observation.md), original sources and acceptance
inputs were frozen before implementation. Existing deadlines, image bounds,
worker ownership, exact pixels, scene/storage outcomes and erasure remain fixed.

## Measured work and implementation

An isolated diagnostic links the existing development components and uses the
original maximum-image fixture. Three baseline trials measured complete pixel
validation at 33.84–34.07 ms and fitting a 32-by-16 output at 34.02–34.12 ms.
The final decoder poll took 35.14–38.53 ms. Parent polling and fitting both validate
the full 2048-by-2048 source, leaving limited margin inside the existing 100 ms
scene-paint assertion. The historical failing paint did not record its individual
phase durations, so its exact timing breakdown remains unknown.

A candidate compiled with the same development flags performs the identical
premultiplied-channel comparisons through a bounded pointer scan. Three trials
measured validation at 4.87–5.10 ms, fit at 4.94–5.12 ms and final polls at
5.97–16.79 ms. Every trial independently checks all decoded and fitted pixels.
The production loop now uses that scan after the existing dimension/length checks.
It still validates every pixel on every raw entry, including all three color
channels against alpha, with the same image.input error. No cache, trusted bypass,
new asynchronous state or acceptance threshold was introduced.

Independent added examples reject invalid first, middle and final pixels in each
color channel at maximum size, through validation, fitting and orientation, without
mutating input. Valid transparent and partially transparent rasters remain accepted.
These examples and the existing image/composition checks passed against the original
implementation before the production edit; the only subsequent source-input
difference is source/scene/image.cpp.

## Executed evidence

All six affected image/composition checks pass on Linux GCC13, Windows GCC15 and
v141_xp. Complete non-native suites pass 312, 309 and 306 checks respectively.
Windows development execution does not qualify historical Windows releases.

All fifteen native rendering checks pass, including the previously failing
scene-image nonblocking-paint assertion and inspector. Native refresh fairness
passes its three load/fault cases, and native binding authoring passes all fifteen
cases. Pixel/geometry, worker lifetime, erasure and current resource/policy checks
retain their existing acceptance. This is scoped evidence for the current sources
and pinned development environment, not full accessibility/performance qualification.

Three binding-selector and three translated-inspector diagnostics trace the original
role/selected-row convenience calls. All six pass, observing 6,252 calls without a
query error. The largest observed call took about 54 ms. The probe would record the
exact native address and make a separate explicit read only after failure, then
rethrow the original error; no failed result can become a successful observation.
The two historical accessibility timeouts remain unexplained. Neither these trials
nor the successful full matrices establish that the image change repaired them.

Records: `build-support/evidence/w-09-runtime-observation-attempts.json`,
`w-09-runtime-observation-native-index.json`, `w-09-runtime-observation-verification.json`,
`w-09-runtime-observation-staging.json` and `build-support/evidence/runtime-observation-handoff.json`.
They retain the frozen inputs, before/after diagnostic executables and measurements,
source archives, original query traces, CTest logs and exact artifact identities.
Original failures remain in the previous committed checkpoint.

The workspace maximum is unchanged. Cleanup verified 28 duplicate native folders
against committed archives before reclaiming 429,208,058 file bytes. The rendering
launch additionally reserved 400 MiB of measured growth; its recorded admission
and ordinary preflights passed. The earlier overrun remains a historical failure.

## Continuation

Preserve the unresolved native role/selected-row failures and use address/method/
reply evidence on recurrence. Do not infer absence, erasure or success from a failed
accessibility call. Continue explicit native observation contracts and remaining
conditional visibility/typography, clipboard/recovery drafts and installed ownership.
W-09/W-10, all five complete editions, historical laboratories and release gates
remain in progress. No public release or privileged action is admitted here.
''')
p=r/'README.md';s=p.read_text();pos=s.index('The [refresh-fairness checkpoint]');s=s[:pos]+'''The [image-validation checkpoint](spec/delivery/runtime-observation-handoff.md)
reduces measured validation cost from about 34 ms to 5 ms while retaining every
pixel check. All affected development and native rendering checks pass. The earlier
accessibility timeouts remain unexplained; complete editions remain in progress.

'''+s[pos:];s=s.replace('regression. Binding/inspector accessibility timeouts and a scene-image timing\nfailure keep full regression qualification open.','regression. Its preserved failures and the later image-validation evidence remain\nseparate records; full native qualification is still open.');write('README.md',s)
p=r/'TODO.md';s=p.read_text();s=s.replace('- [ ] W-09/W-10 regression qualification: explain the preserved binding tab-role and inspector selected-row timeouts and scene-image nonblocking-paint timing failure. Retain fixed expectations and admit the rendering matrix with its measured output growth. See the [handoff](spec/delivery/focus-idle-handoff.md).','- [x] W-09 image validation cost: retain complete pixel checks with a measured lower-cost scan, fixed early/middle/late rejection cases and passing original nonblocking/native rendering checks. See the [handoff](spec/delivery/runtime-observation-handoff.md).\n- [ ] W-09/W-10 native observation reliability: explain the preserved binding tab-role and inspector selected-row timeouts. Six traced trials and current matrices pass without establishing their cause. Retain fixed expectations and measured workspace admission; see the [handoff](spec/delivery/runtime-observation-handoff.md).');write('TODO.md',s)
p=r/'spec/delivery/current-state.md';s=p.read_text();s=re.sub(r'^updated: .+$',f'updated: {{"by": "codex", "at": "{now}", "scope": "Image validation optimization and unresolved native observations"}}',s,flags=re.M)
start=s.index('The latest [refresh-fairness checkpoint]');end=s.index('The earlier [edit-lock checkpoint]',start)
s=s[:start]+'''The latest [image-validation checkpoint](runtime-observation-handoff.md) reduces
complete validation cost from about 34 ms to 5 ms in the development profile.
Original image timing, exact pixels, worker lifetime and erasure checks now pass;
new first/middle/last rejection examples were verified before implementation.
All non-native suites pass (312 Linux, 309 Windows GCC15, 306 v141_xp), along with
15 native rendering checks and refresh/binding matrices. Six query diagnostics
did not reproduce the historical binding/inspector timeouts; their causes remain
open. Continue explicit native observation evidence and the remaining authoring,
clipboard/recovery drafts, installed ownership and five complete-edition tracks.

The earlier [refresh-fairness checkpoint](focus-idle-handoff.md) repairs GTK/ATK
focus starvation under sustained painting. Its original three regression failures
remain preserved; current passing runs above do not rewrite those outcomes or
explain the two historical accessibility timeouts.

'''+s[end:];write('spec/delivery/current-state.md',s)
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes())
for row in v['work_units']:
 if row['id'] in ('W-09','W-10'):
  row['package']='delivery/packages/w-09-runtime-observation.md';row['evidence']='delivery/runtime-observation-handoff.md';row['notes']+=' The image-validation checkpoint preserves all channel checks with a lower-cost scan, independently fixed rejection examples and passing image/native rendering/refresh/binding checks. Full non-native suites pass on all three development profiles. Six traced query trials do not explain the historical binding/inspector timeouts; preserve those open causes. Remaining authoring, installed ownership and all complete-edition gates stay open.'
write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
p=r/'docs/developers/build.md';write('docs/developers/build.md',p.read_text()+'''

### Complete image validation and observation evidence

`scene.IMAGE-VALIDATION` checks invalid first/middle/last color channels at maximum
size through validation, fitting and orientation. Existing raw-image checks remain
mandatory; a faster loop is not a trusted-input bypass. Use the existing image
and native rendering tests with their unchanged timing and pixel expectations.

Before the full native rendering matrix, admit at least 400 MiB of output growth
within the combined workspace bound in addition to running the ordinary preflight.
The earlier run exceeded its 64 MiB reservation; its failure is preserved.
The [handoff](../../spec/delivery/runtime-observation-handoff.md) records measured
validation cost, exact artifacts, six native query trials and remaining unexplained
accessibility timeouts. Successful unchanged queries do not establish a repair.
''')
p=r/'.gitattributes';write('.gitattributes',p.read_text()+'\n# Preserve exact image/observation diagnostics and frozen acceptance inputs.\nbuild-support/evidence/w-09-runtime-observation-history/** -text whitespace=cr-at-eol\n')
print('Updated image/observation handoff and repository entry points.')
