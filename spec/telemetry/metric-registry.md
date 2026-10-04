---
type: "SysPane Specification"
title: "Metric and provider descriptors"
description: "Describe units, source semantics, cost and sensitivity once for every advertised field."
tags: ["telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-METRICS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE", "SP-SCHEDULER"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Metric and provider descriptors


Every implemented metric has a stable ID, value kind, unit, entity/scope, gauge or
counter temporality, denominator, reset/wrap rules, derivation, sample interval,
freshness, source coverage, required permissions, sensitivity and acquisition cost.
The initial [descriptor schema](../contracts/metric-descriptor.schema.json) provides
that shape; [metrics.json](metrics.json) contains experimental examples, not live
provider support. Expand it with implemented fields rather than invent all future
metrics before a first slice.

Counters encode uint64 decimal strings. The first rate sample is pending. A reset,
unknown wrap or changed producer epoch invalidates the interval; never infer a
negative or huge healthy rate. Use actual elapsed sample time and source semantics.
Late device results cannot attach to a replacement identity. CPU utilization names
its denominator and capacity scope; committed memory is not pagefile occupancy.

Wall, inspector, saver and recorder demand leases share acquisition. Exit releases
only the exiting consumer's lease. Enforce source interval floors, concurrency,
cost and cancellation bounds; reserve policy/health progress during event storms.
Disclose measured source-to-surface latency separately from notification latency.

Exports map descriptors to external standards through versioned adapters. Privacy
classification follows fields into tooltips, accessibility, caches and exports.
Future process/service/event, power/thermal/UPS, virtualization, richer history and
vendor fields are separately admitted domains. Inferred explanations are labelled
as inferences; a cloud model is not required for ordinary interpretation.
