---
type: "SysPane Work Record"
title: "Native Linux text checkpoint"
description: "Bounded native shaping, readable metrics and semantic-color raster output with preserved independent checks."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T20:47:00Z"}
sp_id: "SP-NATIVE-TEXT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-NATIVE-TEXT", "SP-BINDINGS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native Linux text checkpoint

Source baseline: `d79da0b9cf2077c85a505b5f5304cd59e7e7c247`. Git history identifies
the resulting commit. The [package](packages/w-09-native-text.md) closes a Linux
Pango/Cairo text prerequisite without changing authored scene/theme versions.
W-09 and all five complete release tracks remain open.

The adapter measures plain UTF-8 text with an explicit language, absolute DIP font
size and wrap width. It returns native ink/logical bounds, their readable union,
unwrapped preferred extent, baseline, actual font families and missing-glyph count.
Rational output scale preserves DIP metrics. Negative bearings and RTL origins
remain explicit. Bounded premultiplied RGBA pixels use theme colors or explicit
contrast overrides. The caller owns the bytes; there is no application text cache.
This package admits authored/public or synthetic text, not retention of live
policy-bound values. No display or user desktop is opened by the raster oracle.

## Evidence and preserved failure

The original package and 25 independent Python cases were archived before native
implementation. Those cases passed on the first build. Two additional cases cover
malformed UTF-8 reaching the native API and color-font semantic color. The latter
failed: embedded emoji colors bypassed the selected foreground. Preserve its raw
pixels, input, executable identity and source snapshot. The correction rasterizes
glyph coverage into an alpha mask before applying the selected foreground; the
original assertion passes without changing its expectation. No prior case was
relaxed. Package timestamp and explicit color-font wording were clarified after
the original archive; the original bytes remain preserved.

`out/evidence/w-09-text-attempts.json` indexes exact source/oracle archives,
commands, native input/output archives and final full suites. The native oracle
checks 27 families. `w-09-text-staging.json` verifies final staged source/evidence
identities; `text-handoff.json` is the machine-readable continuation record.
The environment record pins selected installed libraries/packages and 358 font/
configuration/library files. It does not claim a complete transitive build closure,
cross-platform glyph equality or packaged font redistribution.

The earlier binding checkpoint's content-command receive timeout remains preserved
with undetermined cause. A later successful suite cannot erase that failure.
Historical-toolset execution remains on the modern host, not a historical OS.

## Next implementation

Close widget content semantics where scene 0.2 has no primitive-specific payload;
do not hide text/table/chart/image behavior in optional extensions. Compose immutable
resources, bindings and shared geometry with native metrics. Implement the current-
policy owner for retained text/pixels and accessibility, then independently verify
actual host activation/recovery and native editing. Complete Windows/Mac text
adapters and all remaining native platform/package/lifecycle release requirements.
An offscreen raster pass does not qualify those boundaries.
