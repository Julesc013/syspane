---
type: "SysPane Work Record"
title: "Native collection continuity checkpoint"
description: "Real acquisition survives separately owned consumer failures and bounded replacement."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T11:00:00Z"}
sp_id: "SP-CONSUMER-CONTINUITY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-CONSUMER-CONTINUITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native collection continuity checkpoint

Source baseline: `fd1535380c3b13e025d9d8cedf078db0de283f1e`. Git history identifies
the resulting commit; the checkpoint's archived source digests identify each run.

The existing CollectorProbe now owns one continuous real network worker separately
from replaceable native model consumers. It keeps its own collection demand and
health loop active during consumer exit waiting and retry backoff. Linux adds one
nonblocking listener admission attempt using the existing exact native peer checks.
Each replacement gets a fresh connection and imports the original full snapshot
through DataView. Producer epoch, record identity, generation and original measured
counter/rate timestamps remain unchanged by relay or reattachment.

Five fixed cases cover normal operation, held-child kill, stopped-consumer lease
expiry, typed consumer-policy revocation before retry and four crashes opening the
existing three-replacement circuit. The independent observer holds every PID
lifetime, confirms old exit before replacement, checks 1/2/4-second retry delays,
and brackets real counters against native reads. Source acquisitions advance while
the consumer is absent. Private originals prove exact snapshot/measurement equality
and independently recomputed rates. Public records disclose lifecycle facts and
hashes, not operational values.

The final checks and exact commands are in
`build-support/evidence/w-25-consumer-continuity-compiled-attempts.json`; complete
114-entry Linux and 105-entry Windows records use the same prefix and profile name.
Specification validation and integrity are recorded in the prefixed verification
file. The initial successful focused experiment is retained with its earlier
source identity; final shutdown explicitly exchanges the existing normal-shutdown
message before closing the stream, avoiding an EOF/write race.

One existing GNOME live render-watch case also passes on the rebuilt probe/library.
Its original private pixels and watcher/source journals are revalidated by the
unchanged case oracle. This is a live regression only; the earlier eight-case
supervision matrix keeps its original source/artifact identity. Both development
model packages pass relocated smoke execution. Specification tooling passes 55
checks with the two existing Windows symlink-privilege skips.

The first complete runs passed their runtime assertions but captured two versions
of an unrelated recovery-package navigation paragraph. Evidence recording refused
those mixed inputs. Both original reports and the intermediate document are
preserved; final suites reran after restoring the exact original package.

The original 4 GiB build preflight stop is preserved. The admitted development
allocation is now 5 GiB, with unchanged reservations and product limits. Existing
artifacts and earlier failures were retained. No active user desktop, guest,
installed service, privileged operation or public release was changed.

## Remaining boundary

W-25 and the campaign remain incomplete. This finite native consumer is not a
desktop renderer. The current GNOME experiment makes its shell the POSIX session
owner; a persistent external controller needs an admitted same-session composition
before shell replacement can use this transport. Retain exact peer/session checks.
Next close that composition, integrate automatic current-policy reattachment, and
observe actual visible recovery independently. Editor recovery, installed policy,
general product demand/distribution and complete native editions remain required.
Windows synthetic lab designation, historical guest scope and a Mac endpoint remain
unresolved independently. The default GNOME focus failure remains recorded.
