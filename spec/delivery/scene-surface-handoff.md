---
type: "SysPane Work Record"
title: "Policy-owned scalar scene surface checkpoint"
description: "Native composed scene pixels and accessible names follow current policy, source lifetime and pinned authored resources."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T21:20:00Z"}
sp_id: "SP-SCENE-SURFACE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-SCENE-SURFACE", "SP-NATIVE-TEXT-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-owned scalar scene surface checkpoint

Source baseline: `d4eb38101cd144f00c84ec821c0c8cbe46ee781f`. Git history identifies
the resulting commit. The [package](packages/w-09-scene-surface.md) connects authored
scene 0.2, pinned immutable resources, scoped singleton bindings, shared layout and
native text. It preserves the full product direction and unsupported documents.
W-09 and all complete platform editions remain in progress.

SceneSurface exclusively owns its DataViews, current policy, provider declarations
and one frame. Native clear callbacks erase copied accessibility names and queue
blank drawing before another frame can be accepted. Policy grant/revocation,
source changes, close and clock failure discard prior presentation. Regrant needs
fresh attach/full state. Native clear failure closes permanently. Synchronous
borrows reject reentry and do not allow queued prepared frames to resurrect data.

The initial scalar capability renders text, labelled values, status and ordered
groups. Exact uint64, bool, string and round-trip binary64 values preserve null,
unit and source/freshness meaning. Native readable metrics precede common layout;
multi-display pixel buffers use bounded premultiplied OVER composition. Unsupported
widgets, missing glyphs, exhausted bounds and unreadable geometry return a whole-
scene alternative. This is an explicit integration capability limit, not deletion
of the required tables, charts, images, collection rendering or richer styling.

## Verification and preserved failure

The package, public interface and sixteen initial component families were archived
before implementation. The first run exposed a shared binding bug: at the exact
measurement tick, the code used the rate interval helper, which rejects zero
duration, and returned unknown age. The binding age calculation now accepts equal
compatible ticks and returns zero. Preserve the original failure; neither the
surface assertion nor the existing rate-interval contract was weakened. The shared
binding suite also contains a direct zero-age regression assertion.

Twenty-two surface families cover real DataView wire admission, typed values,
policy ordering/regrant, both disclosure channels, retained/restarted sources,
native clear failure/reentry, bounds, group order, resource identity, multiple
scaled displays, alpha composition and forced display values. Review added an
assertion that mandatory enable overrides an authored disable, then preserved its
failure before correcting that native branch. Both forced values now take priority.

The full suites passed 223 Linux, 202 contemporary Windows and 189 historical-toolset
checks on their archived inputs. The last group ran on the modern Windows host;
18 executable/header/import/linker-input audits also passed. The subsequent forced-
enable correction changes only the Linux surface implementation and its component
test. Final focused checks rerun all 22 surface families and all three native modes.
Evidence records those two source differences explicitly; it does not claim that
the earlier full suites ran against the final native branch.

The independent native oracle observes public synthetic telemetry in an owned
authenticated 800x600 Xvfb window and private D-Bus session. It derives expected
text from fixed values, renders reference glyphs with the already tested TextProbe,
and compares external root pixels. It discovers the actual GTK accessible object
through AT-SPI and checks its process identity and names. Seven normal checkpoints
cover initial/replaced data, revocation, stale delivery, empty-data regrant, fresh
reattachment and retained source loss. Two deliberate controls retain old pixels
or accessibility names; each must fail its corresponding erasure observation.
The normal 200 ms deadline is measured from the native acknowledgement, not from
completion of reference generation. Raw synthetic captures and negative controls
are preserved; ephemeral X authorization cookies are excluded.

`build-support/evidence/w-09-surface-attempts.json` indexes complete source/oracle
archives, attempts, native captures and final regression runs. The machine handoff
is `surface-handoff.json`; `w-09-surface-staging.json` binds final staged inputs and
artifact identities. Selected installed accessibility/observer identities are in
`build-support/surface-runtime.json`; font/runtime pins remain separately checked.
No dependencies were installed or redistributed. The previous unexplained content-
command timeout remains in the binding handoff; later passes do not erase it.

## Next integration

Native qualification here is a finite synthetic GTK/X11 window experiment. It is
not behind-icons placement, installed policy/catalog ownership, full AT-SPI widget
structure/navigation, suspend handling, hard-failure erasure or a real-network
scene vertical. A native clear failure closes the component; independent host
teardown/recovery still has to remove an unresponsive native surface.

Implement missing primitive content contracts and renderers without hiding new
behavior in extensions. Connect the owned scene surface to actual authenticated
producer discovery, persistent pin ownership, committed configuration generations,
native controls/direct editing and the independently supervised desktop host.
Complete other native adapters and all five platform/package/lifecycle tracks.
