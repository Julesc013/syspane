---
type: "SysPane Specification"
title: "History, durability and replay"
description: "Keep bounded evidence separate from current state and make gaps impossible to hide."
tags: ["telemetry"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-HISTORY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# History, durability and replay

## Record kinds

Record received indications, accepted observation transitions, source-health changes, configuration activation, host-health changes, bookmarks and explicit gaps. Do not record every repaint as a system event. Events contain a producer epoch, strictly increasing sequence within that epoch, UTC timestamp, monotonic observation time, entity/source IDs, record kind and bounded payload.

A counter sample series and a transition journal have different retention and compression needs. Initial runtime storage is a bounded local segmented journal plus optional indexed summaries; a database service is not required. NDJSON is the first portable export. A different internal storage backend must retain the same semantics.

## Proposed operational defaults

Start with an in-memory recent ring; persistent recording is explicitly configured. Proposed default persistent policy when enabled: 10 MiB segments, five retained segments, byte and age caps, bounded flush cadence. These values are user-configurable within policy and are not a guarantee of lossless recording. High-rate sampling is not recorded indefinitely by default.

Record the durability policy and last confirmed durable sequence. On crash, a final partial record can be discarded with a recovery marker; do not silently treat it as valid JSON. Flush and rotation errors expose recorder failure without blocking collection or presentation. History on removable or network locations is an explicit choice with failure consequences.

## Replay

Replay uses a distinct producer/session and a visible **REPLAY** indicator that themes cannot suppress. The replay clock supports pause, step and rate control without affecting the host's real clock. It emits recorded values and gaps; no active probe or device query is launched by replay. Unavailable data remains unavailable.

A snapshot checkpoint plus subsequent ordered records reconstructs accepted application state only when all required records are present. Gaps bound the reconstruction claim. Replay must not imply that it recreates every physical event on the original system.

## Export and privacy

Exports use a versioned schema, redaction policy and provenance manifest. Redact host/device/user/network identifiers consistently across related records so joins remain meaningful. Raw crash dumps and capture images can contain sensitive content; they are opt-in and separately classified. No automatic upload.

## Acceptance

Test rotation at boundaries, out-of-space, permission loss, partial writes, corruption, sequence gaps, duplicate delivery, clock changes, crash recovery and replay/real-source separation. Timing tests use a fake monotonic clock. Native durability guarantees require filesystem-specific qualification, not just a successful Python fixture.
