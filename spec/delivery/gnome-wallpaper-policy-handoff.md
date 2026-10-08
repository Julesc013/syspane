---
type: "SysPane Work Record"
title: "Native GNOME wallpaper policy checkpoint"
description: "Native dconf locks, immutable policy identity and independent live composition have separate evidence."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:07:50.665783+00:00"}
sp_id: "SP-GNOME-WALLPAPER-POLICY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-WALLPAPER-POLICY", "SP-GNOME-WALLPAPER-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native GNOME wallpaper policy checkpoint

From `61b315b6cce12755521b6a488956fb34becbe147`, the existing GNOME/DING bridge
preserves three native dconf wallpaper locks and their private policy database
during the unchanged changing-marker and icon-composition interval. The bridge
implementation is unchanged. The [package](packages/w-05-gnome-wallpaper-policy.md)
defines this finite native policy experiment and its separate qualification limits.

| Native mode | Locks and attempted write | Background settings | Policy identity | Live composition |
|---|---|---|---|---|
| Locked | Pass: write rejected | Unchanged | Unchanged | Pass |
| Unlocked control | Fail: write accepted | URI changed | Unchanged | Pass |
| Identical-byte replacement | Pass: write rejected | Unchanged | Fail: replaced lifetime | Pass |

Each attempt uses an absolute private dconf profile, a compiled initial user
database, a compiled policy database and one retained session writer on the owned
bus. Native writability and the exact write rejection are recorded for the locked
case. A successful write/readback of an unrelated private preference establishes
that an unavailable writer cannot masquerade as policy enforcement.

The unlocked control admits an owned URI change while `picture-options='none'`
keeps the synthetic background pixels identical. The verifier therefore rejects
the policy requirement despite successful drawing. The replacement control
atomically substitutes identical database bytes; path/held-descriptor inode and
link observations expose the new lifetime. Equal hashes and unchanged settings
cannot conceal that policy-file mutation. No control is repaired during observation.

Three source-identical native policy attempts completed with the declared isolated
outcomes. Thirty-five verifier tests pass, including consistent false records for
foreign owners, writable policy files, omitted native settings, missing locks,
unavailable writers and replacement lifetimes. The independent original marker,
icon and background expectations remain unchanged.

Forty-six default reveal/composition/marker regression checks also pass, for
**81 desktop verifier checks passed** in this checkpoint.
The original default focus-restoration failure remains a failed acceptance result;
its calibrated controls are not converted into product passes. The evidence prefix
is `out/evidence/w-05-gnome-wallpaper-policy-`; raw journals, policy bytes,
source archives, runtime identities and execution records are retained there:
eight attempts, 13 journals, 18 policy artifacts and two runtime artifacts.

Only the matching 28,022-byte dconf CLI package was downloaded and extracted into
an owned cache; no package was installed and no package script ran. The existing
backend, library, service and GSettings CLI identities are pinned. The policy writer
is an explicitly launched private session child, not an activated system service.
No user desktop, user settings or organization policy changed. All owned process
groups have confirmed cleanup in the verification record.

## Remaining work

This laboratory user owns its simulated policy. The result qualifies neither
protected machine-policy provenance nor resistance to a malicious local owner.
It covers three locked URI/layout keys with solid-color composition. Locked image
wallpaper, live organization-policy updates, disclosure revocation, other keys,
sessions, displays and native profiles require their own evidence.

Continue the independent focus/session, real session-manager and product continuity
boundaries, together with the other platform tracks. The optional focus controller
remains disabled by default. W-02, W-05 and the full campaign remain incomplete;
no complete desktop host or release is qualified by this checkpoint.
