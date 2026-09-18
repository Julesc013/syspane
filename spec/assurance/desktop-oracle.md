---
type: "SysPane Specification"
title: "Independent desktop persistence oracle"
description: "Observe real pixels over time instead of trusting window flags."
tags: ["assurance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ORACLE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-DESKTOP", "SP-TESTING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Independent desktop persistence oracle

## Test scene

Use a synthetic scene with a spatial marker and generation value that changes under external harness control. Place it in a known test region over a test wallpaper with independently recorded configuration. The stimulus source is independent of SysPane's renderer and controller success flags.

## Reveal scenario

Establish baseline capture. Trigger the named desktop-reveal action through the platform's external input mechanism. Continue capture during the action, change the marker while revealed and verify the new value appears. Check every observed frame/interval for visibility, location and readability within declared tolerances. Before/after screenshots alone can miss a disappearance or frozen image.

Record capture cadence, dropped frames, latency and uncertainty. Unobserved gaps make temporal results inconclusive where they exceed the scenario's budget. Never fill missing frames from a SysPane screenshot and call them external evidence.

## Input and wallpaper

Test real icon selection, double-click, drag selection, context menus and focus ownership. Verify the configured wallpaper/file and relevant settings are unchanged. On an approved synthetic lab desktop, pixel comparisons can distinguish surface content from wallpaper modifications. Do not capture a user's unrelated desktop without consent.

## Recovery scenario

Terminate/restart the shell only on a leased test environment with recovery access. Record collection continuity separately from surface outage, shell-ready instant and surface recovery. This allows a recoverable shell-restart outage without weakening the “no disappearance” desktop-reveal test.

Test monitor/DPI changes, sessions, sleep/resume and device reset using controlled platform adapters. Destructive or connection-disrupting operations require a recovery plan independent of the interface being changed. Never disable the only remote-management interface during an unattended test without a safe out-of-band path.

## Result

Store structural findings, instrumented generation flow and external observations separately with cross-references. The oracle reports pass/fail/inconclusive and the exact profile. No application-emitted success bit can override a missing marker. Performance evidence also records capture overhead so it is not falsely attributed entirely to SysPane.
