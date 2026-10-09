---
type: "SysPane Work Record"
title: "Recovery maximum-input qualification handoff"
description: "Measured backend success, installed GTK failures and a validation cost repair."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T04:09:28.374295+00:00"}
sp_id: "SP-RECOVERY-LIMITS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-RECOVERY-GUI-LIMITS", "SP-W11-INSTALLED-RECOVERY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Recovery maximum-input qualification handoff

Production recovery remains disabled. Six actual backend cases pass at the fixed
256-widget, 262144-byte scene, 327680-byte command and 786432-byte recovery bounds.
They preserve the controller epoch during preparation, observe acquired work before
closing, verify suppressed delivery and wait for native children to exit. They do
not qualify the complete GTK loop.

The installed experiment uses the actual Window, EditorForm, workers and relocated
verified bundle. An optional observer measures work in the existing 20 ms Window
tick and excess delay before the next tick. Only the separately compiled fixture
reads SYSPANE_TEST_TIMING=1 and writes numeric rows to its inherited nonblocking
stdout pipe. The independent observer drains it with bounded buffers and records.
Production does not read that variable. No extra timer, thread or scheduler exists.
Each sample must meet 100 ms; delays are never averaged away.

The [checkpoint](checkpoints/recovery-limits.json) preserves every source-bound run,
native archive, frozen input and failed case. The complete seven-case GUI run has
three passing cases: MAX-COMMAND-REJECT, OVER-RECORD-REJECT and CLOSE-PREPARING.
MAX-SCENE and MAX-RECORD complete exact Restore/capture/Undo/Redo/Apply/retirement,
then fail responsiveness. POLICY erases in about 135 ms after observed controller
loss, within its 200 ms bound, but also fails ordinary loop responsiveness.
MAX-WIDGETS finds Apply insensitive before submission in this run; a preceding run
completed exact persistence and retirement but still failed timing. Keep both facts.
All 30 observed native children in the complete family exit without forced
native-child teardown. Failed observers may kill their owned
frontend during cleanup; this is not a clean-close claim for failed cases.

## Measured cost and implemented repair

The original MAX-WIDGETS observation includes a 1.603173-second excess GUI interval,
controller replacement and an unretained draft. The restart cause remains unproven.
The stage diagnostic measures actual resource reconstruction, binding validation,
surface construction and paint. Before the repair, MAX-WIDGETS resource construction
takes about 246 ms and first paint 546 ms. Afterward they measure about 94 ms and
365 ms. These individual observations are not portable performance guarantees.
The diagnostic maximum-text scene returns the existing alternative-preview state;
its fast paint does not demonstrate that all maximum-length text fits that display.

The validator previously compiled fixed schema regexes for each authored value.
It now constructs the finite trusted pattern set once in an immutable map. User
input cannot grow it. Regex matching semantics, full schema/semantic/resource/policy
validation, input limits and all deadlines remain unchanged. Frozen expectations
are identical. This reduces cost but does not close the GUI qualification gate.

Selected portable regressions pass on all three development profiles:
linux-x64-gcc13: 319, windows-x64-gcc15: 319, windows-x86-v141-xp: 319. They cover schema,
transaction, editor/history, settings, scene/layout, protocol and component checks.
Seven Linux backend/UI regression families contain 83 passing named cases. The two
PE import/rejection checks also pass. Historical Windows runtime compatibility is
not inferred from a modern host v141_xp build. Earlier unexplained Windows resource-limit and AT-SPI focus
timeouts remain preserved independently.

## Next admitted work

Measure fixed schema evaluation and per-widget native text setup next. Compiling
trusted schema navigation or reusing native font state within one frame are candidates,
not measured repairs. Before moving validation or retaining authored data, close its
proof, ownership, invalidation and erasure boundary. Current preview reconstruction,
surface construction, layout resolution and Apply availability repeat structural validation; native text
rendering also constructs fresh font state per call. Measure focused changes, retain
complete validation and current-policy erasure, and preserve existing renderer
pixels/layout oracles. Do not remove validation, reduce the 256-widget limit, replace
the real preview with a simplified renderer or lengthen deadlines to pass.

Investigate the Apply state transition and controller replacement under the frozen
maximum inputs. Rerun all seven cases and original installed/backend/preparation
regressions after repair. Only complete qualification permits production enablement;
that enablement needs its own production/fixture regression run. W-11, native
inspector, desktop/provider/lifecycle work and every one of the five full SysPane
0.1.0 release editions remain unfinished.
