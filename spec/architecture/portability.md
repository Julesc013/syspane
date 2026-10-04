---
type: "SysPane Specification"
title: "Language and portability boundary"
description: "Separate shared semantics from compiler, ABI and runtime compatibility."
tags: ["architecture"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-PORTABILITY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PLATFORMS", "SP-COMPOSITION"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Language and portability boundary


The principal hosted engine baseline is C++17 with a small, reviewed dependency
set. This is a language choice, not an OS-support claim. Native boundaries may use
Win32 C++, AppKit/Objective-C++ and admitted GTK/Qt/KDE bindings. No browser or
managed application runtime is mandatory for the wall.

Each target records its compiler, SDK, CRT/libc/STL, flags, exception/RTTI policy,
threading/atomic support, deployment minimum and dependency imports. Modern
filesystem, locale, TLS and synchronization facilities require explicit endpoint
evidence. Never infer XP/7 compatibility from a language flag or renderer choice.
Probe historical toolchains and a second native family early.

Use explicit integer widths and endian conversions at wire/ABI boundaries. UTF-8
interchange is separate from native path/string representation; report lossy legacy
conversion rather than corrupting identity. Durations use monotonic clocks within
one epoch; wall times carry offsets. No native struct dumps or process-local handles
cross the wire. Allocator ownership, thread affinity and cancellation are explicit.

A constrained target can substitute a small conforming component or reduced
composition when a real build experiment proves the need. Do not lower the entire
engine to the oldest compiler or copy the whole product into modern/legacy trees.
Publish reduced functionality and isolation limits. Toolchain availability and
redistribution rights remain release inputs requiring evidence.
