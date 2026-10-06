---
type: "SysPane Work Package"
title: "W-05 independent GNOME focus baseline"
description: "Compare native focus and keyboard delivery without the candidate and with the live bridge."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:25:00Z"}
sp_id: "SP-W05-GNOME-FOCUS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-REVEAL", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 independent GNOME focus baseline

The existing reveal case visibly restores its normal window but leaves the active
client on DING. Preserve that failed acceptance and its exact contract. Determine
whether the behavior requires the candidate, then whether it requires the icon
manager in this pinned laboratory. Do not infer a general GNOME defect or add a
focus-stealing workaround from a root-window property alone.

## Comparison and bounded method

Use the existing authenticated owned 800x600 Xvfb/GNOME 46 runtime, private buses,
fixed background, explicit Super+D binding and unchanged foreground GTK fixture.
Run three source-identical repetitions of each `--focus-baseline` mode:

| Mode | Enabled extensions | Meaning |
|---|---|---|
| `shell` | None | Native shell without icons or candidate; diagnostic only |
| `ding` | Exact pinned DING | Real icon desktop, candidate extension absent |
| `candidate` | Exact pinned DING and existing bridge | Live composition candidate |

The two baselines must not copy or enable the candidate extension. Record enabled
extensions before/after and the private extension-directory inventory. The shell
baseline must have no desktop-type client; the other modes bind DING through the
existing X-Resource/process lifetime contract. Removing icons is solely a causal
control, never an alternative product host. DING and candidate use the identical
owned folder/icon fixture. Keep all previous negative placement/reveal evidence.

After native bootstrap, dismiss the overview, verify the normal foreground window's
exact geometry/ownership and activate it with the same native click. Allow at most
five seconds for DING, when required. Capture three stable overlap/marker/background
frames before the native interval. A baseline's marker region must be the exact
background color; DING must display the four opaque icon quadrants. In candidate
mode, first run the complete existing live composition prerequisite and reveal
trace, including generations 4–6 and the unchanged acceptance oracle. The two
baselines use the same 2,400 ms native interval and Super+D actions at 400 and
2,000 ms, without issuing nonexistent marker methods. Capture the same foreground,
background and overlap regions and native state every 50 ms. Retain maximum 50 ms
combined observation duration, 150 ms coverage gaps, 200 ms visible transition
deadline and initial/restored foreground-active requirement. Do not extend the
interval to turn late restoration into a pass.

Observe input after that fixed interval without refocusing first: issue F9 using
native XTEST, wait 200 ms, and read the foreground process's private event journal.
Then click the foreground fixture explicitly, wait at most two seconds for exact
pixels and its active-client identity, issue F10 and observe for 200 ms. F10 must
arrive in the retained foreground process within 200 ms; otherwise the keyboard
observer is invalid. Record whether F9 arrived and when. Its absence is bounded
non-delivery, not proof that the icon manager consumed the key. Preserve native
active-client/input-focus facts before both keys and after the positive control.
No F9/F10 occurs inside the earlier acceptance interval or changes its verdict.

The GTK helper records only these two keys, native hardware code/state/time,
monotonic receipt time and process identity. Create the event file exclusively at
the exact private attempt path with mode 0600; cap it at 16 KiB/16 events. The
observer never writes or fabricates events. A missing, symlinked, changed-identity,
oversized or malformed event file is an invalid observation. Preserve its bytes.

## Evidence, decisions and completion

Use the existing 40-second observation and bounded retained-group cleanup limits.
Keep a separate baseline journal capped at 8 MiB/180 records, all raw captures,
source/runtime identities and all failed prefixes. Candidate mode reuses the
existing composition/reveal journals; baseline mode has no marker acceptance claim.
The command's successful diagnostic completion is distinct from the recorded
native focus/reveal acceptance, which may fail. No product qualification follows.

The recorder recomputes native visible transitions and focus deadlines from raw
samples, validates actual keyboard receipts, binds window/process ownership and
requires all nine source-identical runs. Compare stable normal/revealed/restored
active-client roles (foreground, icon manager, none or other), visible transition
results and F9 delivery across repetitions. Disagreement between repetitions is
inconclusive. Matching `ding` and `candidate` failures establish that this observed
failure does not require the bridge. A differing shell-only result additionally
localizes it to the tested DING integration, without proving a particular upstream
function or assigning blame. Otherwise retain the unresolved attribution.

Do not change product acceptance to match the baseline. A proposed contract
correction must preserve the original failure and be reviewed separately against
the desktop contract; a native integration fix needs its own independent evidence.
Taskbar/task-switcher behavior, icon input, image wallpaper and recovery remain
separate required boundaries. Ordinary builds and unrelated native tracks continue.
