---
type: "SysPane Specification"
title: "Network domain record and schema extension process"
description: "Make multiple addresses and assessments explicit without flattening provenance."
tags: ["contracts"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-NETWORK-CONTRACT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-NETWORK", "SP-PROTOCOL"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Network domain record and schema extension process

## Domain record

`network-interface.schema.json` is a projection-oriented domain record for the first network slice. It complements the generic observation envelope; it does not replace per-field acquisition/freshness metadata in the semantic store. It includes device-kind classification, separate administrative/media/operational state, multiple IPv4/IPv6 addresses with readiness/zone, resolver/gateway sets, source-specific assessments and lossless link-speed values.

The synthetic positive fixture intentionally includes a global IPv6 address and a scoped link-local address alongside IPv4. Prefix lengths are family-specific. The example addresses are synthetic documentation values, not workshop targets. An assessment is associated with its family, source and observation time rather than a universal `has_internet` boolean.

## Extension boundary

Routes, DHCP state, DNS policy, metrics, tunnels, namespaces and vendor fields grow through explicitly reviewed domain structures or typed entity relationships. The 0.1 projection is deliberately experimental and does not claim to express every final provider field. The owning telemetry spec remains the intended behaviour; an absent schema field is a work item, not permission to erase a requirement.

When a native vertical slice needs additional structure, add the minimum typed field/relationship with positive, negative, migration and semantic tests. Preserve generic observation provenance and declared unknown/unsupported values. Do not insert arbitrary unbounded formatted text as a substitute for missing model structure.

## Acceptance

Schema validation catches family/prefix shape errors. Runtime tests also join source identities, verify complete address enumeration, handle duplicate address lifecycle and retain disabled adapters. Export/GUI tests compare the same underlying accepted observations. No fixture here is a claim that a native Windows/Linux/macOS provider already exists.
