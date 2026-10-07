---
type: "SysPane Work Package"
title: "Native observation error and focus boundary"
description: "Distinguish inaccessible observations from actual absent state without weakening native acceptance."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T09:06:32.957615+00:00"}
sp_id: "SP-W10-NATIVE-OBSERVATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-WIDGET-CREATION", "SP-W10-NATIVE-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native observation error and focus boundary

Continue W-10 from the preserved native focus/interface failures. Keep production
behavior, authored fixtures, mutation expectations, held-key requirements, erasure
limits, request ownership and qualification gates unchanged. First investigate
with the existing editor binary and owned unprivileged ext4/Xvfb/DBus laboratory.

## Bounded experiment

Record the installed accessibility library identities. Compare the existing
AT-SPI convenience APIs with explicit D-Bus replies/errors and X11 keyboard focus.
The upstream 2.52.0 sources are explanatory evidence, not proof of this failure.
Capture exact source, binary, script and environment identities for each run.

Use a live ordinary editor, a live large-scene editor, a short (50 ms) process stop,
a longer (350 ms) process stop, and a terminated owned editor. Stop only the owned
PID; a separate timed continuation and finally cleanup must resume a stopped child.
Never use a user desktop or unrelated process. Each child retains its existing
lifetime deadline; each observer attempt must finish within 40 seconds. At most
three baseline diagnostic repetitions may precede a changed experiment.

Record X11 input focus, accessible object identity, method, result or explicit
error, duration and process state. A successful live reply proves only its returned
state. Missing replies, timeouts and disconnected calls prove no empty text,
missing interface, loss of focus, completed mutation or disclosure erasure. An
unsupported interface is distinct from an unavailable interface query.

If X11 focus leaves the owned editor, investigate activation/ownership. If it stays
with the editor but accessibility state is unavailable or contradictory, investigate
the query and GTK export boundary. No reproduced failure means inconclusive; do
not call an unchanged rerun a fix. Preserve all failures and observed distinctions.

## Admitted correction and fixed acceptance

An observer correction may use error-reporting native queries and bounded reads.
It must never infer success from no reply, keep stale state as a fresh observation,
retry a mutation blindly, force focus during a held-focus assertion, or widen the
existing 200-ms disclosure bound. Ordinary observations retain their original
overall deadlines. A transient unavailable read may be retried only within that
same deadline and only when the predicate still requires positive evidence.

If production causes the failure, close the relevant behavior and failure contract
before changing it. Routine diagnostic instrumentation is delegated. Changes to
acceptance meaning, privilege, user desktop scope and release authority are reserved.

For any corrected observer, calibrate live positive reads, explicit missing/denied
or dead-object results, delayed calls, and genuinely unfocused or frozen controls.
Show that unavailable observations cannot pass an erasure/focus check. Verify
the original native creation, binding, content, snap, group, arrangement, editor
and large-command matrices with their fixed inputs; retain prior failures. Run
additional consumers if a shared helper changes. Do not manufacture product or
historical qualification from laboratory results. Record the next boundary in
the existing work graph and current-state entry point.
