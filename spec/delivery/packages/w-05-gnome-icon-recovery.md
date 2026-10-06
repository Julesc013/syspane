---
type: "SysPane Work Package"
title: "W-05 native GNOME icon-manager recovery"
description: "Confirm one owned DING lifetime ends, observe native replacement and pixels, then exercise input on the replacement."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T03:09:09Z"}
sp_id: "SP-W05-GNOME-ICON-RECOVERY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-COMPOSITION", "SP-W05-GNOME-INPUT", "SP-DESKTOP", "SP-ORACLE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 native GNOME icon-manager recovery

The named experiment replaces the icon-manager process while the owned GNOME shell,
bridge, Xvfb and private buses remain alive. It does not qualify shell/compositor
replacement, real renderer/collector continuity or the separately failed Show
Desktop focus restoration. Use the existing pinned DING supervisor unchanged.
`--icon-recovery live|frozen-surface|no-stop` owns the live composition prerequisite
and private PCManFM/accessibility input setup; it excludes other experiment flags.

## Ownership and native failure

After the unchanged initial composition interval, bind the old DING desktop window
through XRes to the exact owned script, shell group/session and process start time.
Hold pidfds for that process and the shell before the fault. Record original mapped
files before exit. Recheck the original binding and non-exited pidfd before signaling.
At 250 ms into the separate recovery interval, use `pidfd_send_signal(SIGKILL)` on
that descriptor only. Never signal a numeric PID selected after the observation,
the whole shell group, a user session or an inherited display.

Independently observe the held old pidfd becoming readable within two seconds.
The pinned native DING extension decides whether and when to launch its replacement;
the harness must not launch, patch or enable another icon manager. Observe a new
desktop-window/process lifetime through XRes, exact script/group/session/executable
and start time, then hold its own pidfd. Numeric XIDs may be reused; the full native
process/resource binding, not the XID alone, identifies replacement. Accept at most
one replacement within five seconds of the stop request. Keep the shell's original
window-manager resource and held process alive throughout the measured interval.
Treat transient BadWindow queries as not-ready; other native query errors fail.

The initial composition verifier normally requires its icon manager to remain alive
through cleanup. Only this recovery family may instead supply the independently
recorded old-process exit. Its initial pixel/source checks remain unchanged; the
recovery verifier must separately prove that exit and the replacement lifetime.

## Temporal recovery and calibrated controls

Paint generation 4 and allow the existing 250 ms setup interval. Start a new trace
at generation 4. Confirm at least three pre-fault captures. After confirmed old exit,
request generation 5. Record replacement readiness as soon as it is observed;
do not delay or manufacture that timestamp. Request generation 6 once replacement
is ready and at least 350 ms has elapsed since old exit, then capture another 750 ms.
Keep the independent marker decoder, 200 ms generation deadline, 50 ms capture
cadence, 50 ms combined observation duration and 150 ms maximum coverage gap.

Each paired sample records marker pixels, the original icon/transparent-overlap
region, the unchanged background witness and the native icon-manager binding.
Preserve all outage samples. Require exact original opaque icon anchors and clean
rectangle pixels in every sample beginning 200 ms after generation 6, with at least
three such samples. Do not recalibrate masks or move icons after recovery. Record
first observed icon absence when captured; a short unsampled absence is not zero
outage. Process exit/replacement evidence is independent of sampled visibility.

The recovery trace is bounded to six seconds, 120 frames and an 8 MiB/180-record
journal. A missing old exit ends the no-stop control at 2,500 ms; it cannot claim
replacement even if the unchanged desktop remains visible. A missing replacement
ends with failed/inconclusive evidence. Never turn a timed-out process into a pass.

- `live`: deliver the exact owned stop; require old exit, new native identity,
  generations 4/5/6, restored icon composition and unchanged background/settings.
- `frozen-surface`: freeze the laboratory marker at generation 4 immediately before
  the same stop. Its private method exists only under this explicit control and
  ignores later generation requests through the whole trace. Native replacement
  and restored icon/rectangle pixels must pass, while the independent progress
  oracle must fail. Do not repair the freeze to erase that failure.
- `no-stop`: omit the signal. Issue a separate generation-5 liveness stimulus at
  500 ms (within 50 ms) so the unchanged temporal oracle receives two actual
  generations. Require the original process and advancing marker to remain live
  and correctly identified, with no generation 6, replacement or post-recovery
  input claim. The first single-generation control failed the existing oracle's
  trace-count requirement; preserve that invalid fixture instead of relaxing the
  oracle or treating static pixels as live progress.

## Input after successful recovery

Only after all live recovery prerequisites pass, bind the existing full native
input sequence to the new DING identity and original independently calibrated
coordinates. Require selection, clear, drag selection, visible menu/dismissal,
actual owned folder contents/open/close, restored clear selection and final live
composition. Use the existing fresh clipboard replies, private accessibility
peer/PID binding and pinned PCManFM. The original owner must not satisfy a new
clipboard or accessibility observation. Retain the new pidfd through the sequence.
Failed recovery controls list this dependent input sequence as unexecuted.

Preserve fixture/configuration identities, stimulus/exit/readiness timestamps,
raw frames/journals, sources/runtime, every failure and confirmed process cleanup.
The ordinary 40-second attempt and owned cleanup bounds remain. This is separate
from the no-disappearance reveal contract: a crash outage is expected and measured,
not hidden by a later successful frame. W-02, W-05 and full desktop qualification
remain open after this finite recovery experiment.
