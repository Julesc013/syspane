---
type: "SysPane Specification"
title: "Terminology and measurable definitions"
description: "Use precise nouns and distinguish observation, presentation and development state."
tags: ["foundation"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-GLOSSARY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: []
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Terminology and measurable definitions

| Term | Definition |
|---|---|
| Entity | Identified subject within a producer, scope and lifetime |
| Observation | Typed value or explicit absence, with source, attempt, freshness and presence |
| Relationship | Typed directed edge between entities; not necessarily a tree |
| Indication | OS/provider notification that something may have changed |
| Transition | Difference between accepted observations, not necessarily every physical event |
| Snapshot | Coherent application generation; sources may have different observation times |
| Scene | Authored widget/layout/binding document, independent of current telemetry |
| Projection | Derived view of state for a consumer |
| Surface | Passive window/render target hosted in a desktop environment |
| Editor | Temporary interactive application surface for reversible scene changes |
| Profile | Named OS/ABI/shell/toolchain/capability composition |
| Capability | Declared, implemented, qualified and currently available feature, on separate axes |
| Work unit | Bounded development objective with dependencies, authority and evidence |
| Evidence | Actual results bound to artifacts, inputs and environment |
| Proposal | Candidate intended design, not an implemented feature or execution grant |
| OEM+ | Recognizably platform-native interaction with richer SysPane capabilities |

A **live** field declares its maximum age and acquisition class. **Instant** is not used as a mathematical promise. The flagship network target is a visible update within one second of a relevant delivered indication under the declared workload, with source-detection latency reported separately and a separate physical-stimulus acceptance measurement.

**Persistent** means visible throughout ordinary desktop reveal in a qualified profile, not hidden then restored. Shell restart is a recovery event with a measured outage. A secure desktop is not an ordinary desktop reveal.

**Standalone** means the distributed native package does not require a separately installed non-OS application framework for normal operation. It does not prohibit several isolated native processes or OS-native packaging.

**Read-only** includes side effects of querying. Merely opening a serial port or invoking a repair-triggering inventory query may disturb equipment; those operations are not silently justified by the absence of explicit writes.

**Backward compatible** specifies a public contract and supported versions. It never means one executable runs on every instruction set and operating-system generation. **Reproducible** refers to named artifacts and build inputs, not the ability of unrelated people to recreate the maintainer's private signing operation.
