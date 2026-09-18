---
type: "SysPane Specification"
title: "Performance, energy and freshness budgets"
description: "Measure useful work and end-to-end latency without zero-overhead claims."
tags: ["assurance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-PERFORMANCE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-SCHEDULER", "SP-RENDERING", "SP-TESTING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Performance, energy and freshness budgets

## User-facing timing

Discrete network conditions should appear within one second when the operating system exposes a timely signal and the named workload/profile permits it. Measure both stimulus-to-visible and notification-to-visible. Initial engineering objectives are notification-to-visible p95 ≤250 ms and p99 ≤1 s; these percentile targets do not excuse a failed strict scenario or hide unavailable source detection.

Link connected/configuring can appear before DHCP or connectivity assessment. Fields have individual freshness/coverage policies. A slow DNS reconciliation must not be advertised as one-second DNS freshness. Continuous rates include their sampling interval; instantaneous CPU utilization is not a meaningful replacement for interval measurement.

## Resource accounting

Measure controller, surface and provider processes; attribute compositor/provider overhead where possible. Record CPU time, wake frequency, working/private memory, graphics allocations, disk writes, network traffic and source-query counts. Report hardware, OS, display topology, enabled fields and history settings. Do not round Task Manager CPU to zero and call it zero energy.

Use shared demand planning: several widgets/inspector/history requests for one field share collection. Invisible projections stop drawing while independent recording demands can remain. Coalescable ordinary timers are preferred; high-resolution timestamps do not require high-frequency wakeups.

## Proposed limits versus measured baselines

Initial configurable caps include collection concurrency, callback queue size, history retention, chart points and scene complexity. Choose default values through named-profile experiments rather than asserting a universal memory ceiling. A single 3840×2160 RGBA buffer is about 31.64 MiB; multiple buffers/displays need explicit accounting.

Store measured baselines and allowed regression bands in release evidence, not this narrative. Changes to thresholds require rationale and review independent of the change being measured. Do not raise a budget just to make a candidate pass without product approval.

## Scenarios

Measure idle static wall, one-second resource widgets, network/device storms, large adapter/address lists, long history, multi-display mixed DPI, editor interaction, lock/display-off, source timeout and replay. Include collector-only and renderer-only isolation runs. Publish tail latency and failures as well as averages.
