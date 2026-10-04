---
type: "SysPane Specification"
title: "Product charter and non-negotiable boundaries"
description: "Define the complete native operational-desktop product family."
tags: ["product"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-CHARTER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: []
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Product charter and non-negotiable boundaries

## Mission

Make ordinary desktop space an accurate, persistent operational instrument for technicians, without replacing corporate wallpaper or requiring a separate monitoring window. SysPane is also called **System Panel**. The product is host-first with explicitly authorized workshop extensions; it is not redefined as a fleet-monitoring service.

The engineering maxim is: **Observe precisely. Preserve transitions. Render persistently. Explain uncertainty. Recover automatically.** Preserve transitions means preserve received/observed evidence within declared limits and mark gaps, not claim lossless knowledge of events never delivered by the OS.

## Complete vertical product

SysPane owns collection, semantic state, source health, desktop hosting, rendering, layout, settings, direct desktop editing, inspector, local history, structured output and test automation. Desktop Info, Rainmeter, an embedded browser, a required web server, a database service, a model provider and AIDE are not runtime foundations. Normal use is unelevated, offline-capable and native to each target.

The initial families are Windows NT (including Windows XP and 7 investigations alongside 10/11), Linux and macOS/OS X. No family is pronounced fully compatible before running its declared profile. BSD, Solaris/illumos, RHEL profiles, older NT, RT, Win9x, DOS, OS/2 and classic Mac OS remain intentional routes, not forgotten wishes or promises of binary parity.

## Primary experience

A technician reveals the desktop and sees machine identity, physical and virtual network state, resources, storage and connected devices at a glance. A state change becomes visible without manual refresh. A failure is shown as a failure, never a healthy zero. The inspector explains source, timing and uncertainty and lets the technician copy details.

Entering Edit Desktop provides a temporary, native interactive surface: add, remove, resize, move, group, bind and theme widgets directly, then apply or cancel. Native settings, the editor, CLI and local automation share typed validated operations. Ordinary users must not need to edit a configuration file to use supported settings.

## Product boundaries

The product is a diagnostic observer, not a partition editor, firmware flasher, arbitrary remote shell, keystroke recorder or default subnet scanner. Active probes and low-level providers are separately admitted. A service, custom kernel driver, cloud sync, browser UI, central manager and unrestricted plugins are not initial dependencies. A headless build is a supported composition where appropriate, not an excuse to abandon native user interfaces on required desktop targets.

## Quality claim discipline

“Native”, “portable”, “small” and “Microsoft-grade” are goals with measurable criteria, not certifications. Potential upstream adoption is an aspiration. Do not imply endorsement, promise perfect behaviour on unknown future shells, or fabricate microsecond latency and universal memory figures. Publish exact capabilities, profiles and limitations.

## Authority and recovery

Observation, SysPane configuration, maintenance and any future OS management action
have distinct authority. Ordinary launch performs no installation. Denied telemetry
leaves unrelated information usable; optional failures preserve an independent
diagnostic path within OS/session limits. The [role contract](../architecture/composition.md)
adds a companion saver, preview/configuration and maintenance without a product fork.
No saver role owns credentials or replaces OS locking.
