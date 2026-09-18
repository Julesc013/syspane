---
type: "SysPane Specification"
title: "Processor, memory and GPU semantics"
description: "Define denominators, units and support rather than importing ambiguous dashboard labels."
tags: ["telemetry"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-RESOURCES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Processor, memory and GPU semantics

## Processor

Publish logical/physical topology, applicable groups or scheduling domains, and total/per-domain utilization with an explicit denominator. Utilization is an interval measurement; the first sample is pending until a valid delta exists. Record actual elapsed time, counter reset and CPU hotplug. Large-server tests must establish that all intended processors contribute rather than silently reading one processor group.

Portable metric names represent comparable meanings only. A load average is not CPU utilization. Frequency, utilization, idle time and throttling are distinct. Where virtualization or OS policy limits visibility, show the scope.

## Memory

Separate physical total/available/used according to a documented OS-specific definition; commit charge and limit; swap/pagefile capacity and occupied pages; and paging I/O rates. Do not label commit as actual pagefile occupancy or call cached/reclaimable pages irretrievably used. Display byte units consistently and show unit definitions in the inspector.

Windows implementation must evaluate distinct memory and pagefile APIs; Linux swap/commit and macOS compressed memory have native meanings that need explicit descriptors. No universal percentage should conceal these differences. Rounding applies only in presentation. A zero byte count is a successful observation, not a fallback for missing privileges.

## Graphics

GPU identity, engine utilization, memory budgets/allocations and sensor data are distinct capabilities. Define any aggregate, such as busiest engine, rather than summing percentages across engines. Multi-GPU systems need stable adapter identity and per-engine/source support. An absent driver counter produces `unsupported` or source failure, not zero utilization.

Temperature/fan/voltage providers are optional, hardware-specific, separately reviewed and isolated where necessary. Do not silently include a kernel driver or probe low-level buses just to fill a field. Scope sensor accuracy and units; uncalibrated or vendor-specific values require explicit labels.

## Acquisition and display

Start with one-second CPU/memory demand while visible, slower static topology, and configurable optional GPU sampling. These are proposed defaults, bounded by target resource budgets and policy. Collection persists independently when a recorder requests it. Multiple widgets share one acquisition.

The inspector explains a metric's source, scope, denominator, observation interval, support and last error. Charts render gaps across unavailable intervals instead of interpolating healthy lines. Synthetic tests cover counter wraps, heterogeneous topology, missing counters, low memory and source loss. Real validation includes low-end and large-server environments; compilation is not metric verification.
