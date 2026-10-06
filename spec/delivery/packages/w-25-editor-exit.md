---
type: "SysPane Work Package"
title: "Independent X11 editor lifetime experiment"
description: "Close and investigate an independent native escape from an owned obstructing editor process."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T12:50:00Z"}
sp_id: "SP-W25-EDITOR-EXIT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-RECOVERY", "SP-EDITOR", "SP-W25-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent X11 editor lifetime experiment

This bounded W-25 investigation establishes whether an independent native owner
can release an obstructing editor lifetime when that child stops processing input.
It does not implement W-10 scene editing, Apply/Cancel transactions, persistence,
installed controller discovery or general desktop qualification. The candidate
surface uses public fixed pixels only. No operational data or document is opened.

## Fixed boundary

One independent recovery process owns one isolated editor child through the existing
held-pidfd Child adapter. It owns an X11 passive Ctrl+Alt+Escape grab and a separate
GTK native Close editor control. The guard is acquired before child launch; a grab
conflict prevents launch. The owner never depends on the main application controller,
renderer, data stream or child event loop. No command accepts a caller-supplied PID
or executable. The child arms parent-death protection before opening its display.

The keyboard adapter uses the current X11 keymap's Control/Alt assignments and
Caps/Num Lock variants. Held pointer buttons do not prevent emergency exit. It requires the admitted ControlMask/Mod1Mask mapping;
unsupported or changed relevant mappings fail closed. A notification with unchanged
escape/modifier assignments preserves the grab; changed assignments request release.
Ordinary keys, extra Shift and XSendEvent key messages do not request exit.
Both grab modes are asynchronous: no keyboard or pointer freeze is introduced.
The editor candidate makes no active pointer/keyboard grab. Such grabs, an unresponsive
X server and Wayland global shortcuts remain outside this experiment's capability.

Native exit is an emergency release of transient UI, not Save, Apply, or a successful
Cancel transaction. It writes no authored state and never asserts draft restoration.
The future editor must preserve committed state independently and label any separately
recoverable draft. Exit permission cannot depend on policy disclosure or optional data.

## Lifetime and bounds

The single-threaded keyboard adapter services at most 32 events per 20 ms GTK tick.
A keyboard exit, native button/window close, mapping loss or 15-second laboratory
deadline requests SIGTERM on only the held child. After 250 ms without confirmed
exit, send SIGKILL to that same lifetime. Record termination only after waitid proves
exit; a further 2,000 ms without proof yields an unconfirmed failure, never success
or replacement. The original Child destructor remains a final bounded cleanup path.
Normal child exit releases the guard. Owner loss kills its protected child without
requiring a functioning child event loop. No child replacement is admitted here.

The executable is a development-test target, not installed or enabled on login.
The ordinary tests use the existing authenticated owned Xvfb recipe only; no user
desktop or shell is signaled. The caller explicitly selects the laboratory mode.
The GTK window occupies a reserved recovery strip above the obstructing candidate.
This proves separate input ownership; discovery over a genuinely fullscreen editor
and integration into GNOME's actual desktop remain additional acceptance work.

## Independent acceptance, fixed before implementation

`native.EDITOR-EXIT` / `tests/desktop/native_editor_exit.py` owns a separate underlying
green input witness. It sees red candidate pixels and blocked witness clicks before
exit, then requires restored green pixels and a native pointer click received by the
witness within 1,500 ms of the exit stimulus. It holds pidfds before faults and checks
the native parent and executable. Owner reports alone cannot establish success.

| Case | Stimulus and expected observation |
|---|---|
| KEY-LIVE | Focus candidate, ordinary Escape and shifted emergency chord leave it alive for 200 ms each; Ctrl+Alt+Escape releases it cooperatively with code 0. |
| KEY-FROZEN | SIGSTOP only the held editor, then emergency chord; exact editor exits by SIGKILL and witness recovers. |
| BUTTON-FROZEN | Same stopped child; native pointer click on the GTK Close editor button releases it. |
| LOCKS-FROZEN | Enable Caps and Num Lock, freeze candidate, then emergency chord; recovery is unchanged. |
| DRAG-FROZEN | Hold the primary pointer button over the stopped editor, then emergency chord; release the pointer and require restored input. |
| MAPPING-LOSS | Replace the private display's Escape mapping; owner reports unavailable and cooperatively removes the child. Unchanged mappings during ordinary input must not abort editing. |
| OWNER-LOSS | Kill only the held recovery owner; parent-death protection removes its child and restores witness access. |
| EDITOR-CRASH | Kill only the held editor; the independent owner observes exit and releases native resources. |
| GRAB-CONFLICT | Independent observer already owns one required shortcut variant; owner exits unavailable, creates no editor, and witness stays usable. |

All positive cases require both held native exit and external pixels/input. After
each case, an independent connection must be able to acquire the shortcut, proving
release. The observer has a 25-second per-case process bound and always destroys
its owned display/processes. Public evidence records hashes, timings and fixed pixel
digests, never display credentials. CTest allows 300 seconds for the nine cases and
their bounded cleanup, without changing any per-case recovery deadline. Preserve
every attempted result and source archive.

## Execution and decision authority

Prerequisites are the pinned Linux development profile, GTK/X11/XTest/Xvfb and the
existing Child adapter. Source ownership: `source/interfaces/editor_exit_x11.*` and
`source/application/editor_exit_probe.cpp`; observer ownership: `tests/desktop/`.
Configure/build with the ordinary Linux commands; execute
`ctest --preset linux-x64-gcc13 -R '^native[.]EDITOR-EXIT$' --output-on-failure` after
the required workspace preflight. Expected output is `SysPane.EditorExitProbe` and
an immutable `EDITOR-EXIT-01-<attempt>.json` native report with source/artifact hashes.

Private implementation choices are delegated. Changed acceptance, use of user
desktop/shell resources, global installation and product transactions are not.
The handoff must distinguish a passing lifetime experiment from qualified editing,
identify failures and the next integration prerequisite, and retain W-25 as open.

API semantics: [XGrabKey](https://xorg.freedesktop.org/archive/X11R6.8.2/doc/XGrabKey.3.html),
[parent-death signal](https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html),
[held-pidfd signaling](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html).
