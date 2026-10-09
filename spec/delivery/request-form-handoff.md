---
type: "SysPane Handoff"
title: "Native form request preparation handoff"
description: "Asynchronous Apply, exact recovery digest and complete exit acknowledgement, with original GUI evidence."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T12:42:46.558856+00:00"}
sp_id: "SP-REQUEST-FORM-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-REQUEST-FORM", "SP-REQUEST-WORKER-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native form request preparation handoff

The [form package](packages/w-11-request-form.md) now connects installed Apply to
the existing request worker. Capture retains the final request identifier and
exact optional recovery digest. Authoring is disabled while preparation is held.
The existing form timer polls recovery before consuming the prepared request;
current digest and draft-owner authority must still agree before adoption.
Only adoption allocates a live ticket, and the exact request is submitted once.

Cancellation before submission clears the recovery marker without sending a
transport cancellation or inventing a durable outcome. Reload, policy/topology,
disconnect, rebind and close invalidate delivery; even a malicious late result
cannot submit. A callback failure after submission retains the existing unknown
outcome and reconciliation behavior. No additional worker, timer or queue exists.
Forms without a request factory keep their original synchronous entry path.

Exit acknowledgement now waits for request, history, recovery and image work.
The new held-image oracle failed before this repair: the callback ran while an
image still required acknowledgement. Both fixed exit cases now pass, including
a late cancelled request completing before the held image. Callback delivery is
one-shot after all required work stops.

## Verification and preserved failures

The [checkpoint](checkpoints/request-form.json) binds commands, exact source and
artifact identities, local archives and original failures. Linux revision 74,
Windows GCC revision 43 and v141_xp revision 34 build successfully. Each passes
19 request/history/component checks; the historical profile also passes its two
artifact/import checks. These are development environments, not XP qualification.

The final implementation passes 123 native cases across nine families: 23 request
form, two exit, 17 history, 11 reply lifetime, 14 recovery controls, 20 form,
14 installed recovery, 15 installed editor and the seven original ordinary GUI
timing/erasure cases. Initial input and both prepared-editor families also passed
28 cases on the intermediate candidate; their source identities remain separate.
The final ordinary GUI run includes MAX-RECORD and preserves the unchanged limits.
Earlier failed GUI attempts remain historical evidence, not overwritten results.
MAX-RECORD records 73650 us maximum excess delay and 66503 us maximum callback
work in this run, both below the existing 100-ms limits.

The form cases observed maximum capture 184 us and adoption 130 us,
below their fixed 100-ms callback bounds. These controlled cases are separate from
the installed maximum-input GUI checks and do not establish a latency distribution.
Raw recordings are byte-verified before duplicate active outputs are reclaimed.
The 8-GiB active workspace allowance and product resource limits are unchanged.

Three failures from this package are preserved: a compiler indentation diagnostic,
a recovery-rebind fixture that accidentally created a different factory, and the
product's early exit acknowledgement. The fixture correction reuses the original
factory required by the existing location contract. Its original source and failed
attempt remain; case expectations and limits did not change. The held-image
expectations were frozen before the product repair and remain unchanged.

Specification validation passes 51 schemas and 183 fixtures. The tooling suite
reports 62 tests: 60 passed and two existing Windows symlink-privilege skips.
Generated projections and integrity verification are recorded separately; these
checks are not native qualification.

## Next boundary

Production recovery/history admission remains disabled. Revalidate the existing
[ordinary-entry admission package](packages/w-11-production-recovery.md) against
the final implementation, including original installed recovery/settings/GUI cases,
observer isolation, compiled entry comparison and exact helper/current-policy
authority. Preserve its earlier failures and distinguish development qualification
from protected deployment, which needs its corresponding authority.

Continue general authoring/preview responsiveness, native inspector, telemetry and
desktop composition. W-11 and the complete Windows 9x, Windows NT, Linux X11,
Wayland and Mac OS X editions remain unfinished. No privileged action or public
release was performed.
