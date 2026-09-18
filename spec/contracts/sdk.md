---
type: "SysPane Specification"
title: "Extension SDK and embedding boundaries"
description: "Make extensions useful without making the trusted application an arbitrary code host."
tags: ["contracts"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-SDK"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PROTOCOL", "SP-SECURITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Extension SDK and embedding boundaries

## Three first consumers

The initial SDK serves external providers, local control clients and declarative widget/theme authors. Native embedding is a separate advanced consumer. Deliver examples, contracts, lifecycle rules, a conformance runner and compatibility documentation together; a header alone is not an SDK.

Provider processes publish typed observations, health and capability information. They receive explicit collection requests and quotas, not arbitrary access to the desktop editor's internals. Core provenance identifies the provider; plugins cannot self-declare trusted built-in status.

## Extension classes

Declarative layouts/themes/widgets have no executable permissions. Bounded expressions cannot call a shell or network. External providers run out of process with explicit admission, resource budgets and actual OS-enforced permissions. Native custom rendering is isolated or constrained to bounded scene fragments. Privileged providers are independently installed and authorized.

Out-of-process means crash isolation, not automatic sandboxing. The capability profile records real controls available on each OS. On historical systems, do not advertise modern isolation that is absent. No arbitrary in-process DLL/shared-library plugins are admitted in the first stable runtime.

## C interface policy

When embedding is justified, use opaque handles, explicit ownership and free functions, length-delimited UTF-8, sized/versioned structures, error codes, allocator compatibility, callback lifetime and cancellation contracts. No exceptions, STL objects, Objective-C references or toolkit types cross the boundary. Version negotiation precedes operations.

The included header is an interface sketch, not ABI v1. Compile it as a header sanity test when native builds exist, then stabilize only after real consumers exercise it. Old compilers may need a documented integer-width abstraction; do not claim the sketch builds on every historical target.

## Package and supply chain

An extension manifest declares identity, version, contract ranges, architecture, permissions, data classification, resource caps and asset hashes. Installation/import validates paths, signatures where applicable, ownership and policy. Disabling a provider drains outstanding work and marks its observations appropriately. An extension update cannot expand permissions silently.

## Acceptance

Test provider crash/hang, restart, malformed messages, stale results, spoofed identity, permission escalation attempts, incompatible versions, size limits, untrusted assets and deterministic declarative rendering. At least one independent consumer and multiple native implementations should exercise contracts before a stable public SDK promise.
