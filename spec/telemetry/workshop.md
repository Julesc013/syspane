---
type: "SysPane Specification"
title: "Authorized workshop assets and active probes"
description: "Keep remote equipment observation explicitly configured and separate from local telemetry."
tags: ["telemetry"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-WORKSHOP"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Authorized workshop assets and active probes

## Asset versus observation

An asset registry is configured information: asset ID, approved address, bench/rack label, expected device type and links to procedures. A probe result is an observation: target, method, family, source/interface context, timeout and result time. A technician's “quarantined” or “candidate spare” label is an annotation, not a measured health state.

Local and remote entities keep distinct producer/scope identities even when shown in one scene. Do not join solely on a reused IP or assume that a DNS name identifies the same physical device forever. Suspected identity drift is visible.

## Network authority

No default subnet sweep, broadcast discovery, unauthorized port enumeration or cloud connection. Each target and probe class is allowlisted under policy. Resolve hostnames according to policy and validate each resulting address against target constraints; redirects or rebinding cannot expand a grant. Proxy behaviour and source interface are explicit.

ICMP/TCP reachability does not establish service correctness, device health or Internet access for another adapter. Credentials are obtained through native secure storage only when needed, never embedded in themes, examples or logs. Legacy insecure protocols require explicit lab risk policy; never label them secure because they are supported.

## Load and failure

Use bounded concurrency, deadlines, backoff and jitter. Record retry counts; avoid synchronized storms across workstations. A missing reply may be filtering rather than a failed device. UI labels express that uncertainty. A transient probe result cannot overwrite the asset's operator status.

Optional remote agents negotiate schema/capabilities and authenticate; identity and encryption limits are part of the profile. There is no general remote shell or write-control API. Device-specific providers must be reviewed for operational effects, not merely byte-level read-only requests.

## Growth path

Later adapters may read authorized management endpoints, hardware test logs and explicit inventory exports. Correlation can connect a bench event to local interface changes without claiming causation. Before/after inventory comparisons, test bookmarks and redacted bundles are product extensions, not an excuse to build a fleet platform before the local wall works.
