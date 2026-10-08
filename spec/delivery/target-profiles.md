---
type: "SysPane Specification"
title: "Build targets and qualification profiles"
description: "Bind concrete runtime floors to evidence instead of inferring support from platform names."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-TARGETS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PLATFORMS", "SP-RELEASE"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04", "SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-05T23:39:47+11:00", "scope": "Admitted model foundation; executed development checks, no desktop qualification or human review attested"}
---

# Build targets and qualification profiles


The [target-profile schema](../contracts/target-profile.schema.json) describes exact
OS/API minimum, architecture/ISA/word width/endianness, ABI/libc/runtime, compiler/SDK,
dependencies, native toolkit, renderer, shell host, roles and isolation. Authored
build profiles live in `source/build/targets/`. Windows/Linux foundation development
profiles are populated and exercised; no supported desktop product profile exists
yet. Synthetic fixtures remain explicitly examples, never download rows.

Build intent is separate from runtime availability and executed qualification.
Qualification binds the exact target revision, source, artifact hashes, harness,
oracle, policy, configuration, host/driver/display environment and test outcome.
Compiled-only and emulated-only checks are labelled and cannot become native support.
Capability failure affects the named capability, not unrelated inspector usefulness.

First tracks are contemporary Windows, XP/7, Linux and macOS/older OS X. XP x86/x64,
Win7 x86/x64, modern Windows x64/ARM64 and authorized RT feasibility are distinct.
Linux records libc/toolkit/distribution/shell independently. A macOS universal package
contains separately qualified architecture slices and helper closure; it does not
establish older OS X, PowerPC or classic Mac compatibility.

Before compiling, record exact reproducible recipes and dependency floors. Audit
imports/loader requirements, then launch a smoke package on the actual target early.
Do not use build-host instruction tuning in distributed artifacts. A smaller native
edition can remain useful with explicit limits. Native package formats and sandboxed
distribution choices need independent telemetry/IPC/host feasibility evidence.

No profile containing unknown minima, unowned dependencies or missing mandatory
evidence is publishable. A failed/blocked lab remains visible; unrelated profile
integration proceeds under its own acceptance. Resource budgets are profile-specific
measurements, separate from fixed protocol safety bounds.

A development-only profile is allowed before product support is qualified. It
records an actual toolchain, host/runtime floor and concrete configure/build/test/
smoke commands, expected outputs and reproduction limitations. It may deliberately
support only its measured host; it must not infer older OS support. W-01 populates
the initial records under its [package contract](packages/w-01-foundation.md).
Personal paths belong in local presets/environment, not the checked-in recipe.
