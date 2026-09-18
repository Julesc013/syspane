---
type: "SysPane Specification"
title: "Accessibility, localization and cognitive load"
description: "Make all operational information available without relying on sight, colour or drag gestures."
tags: ["experience"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ACCESSIBILITY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-EDITOR", "SP-SETTINGS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Accessibility, localization and cognitive load

## Equivalent access

The passive wall is only one presentation. The native inspector exposes all information shown by supported widgets with useful accessible names, values, source states and logical grouping. Desktop editing has keyboard/property-panel equivalents for every gesture. Charts expose summaries and data views, not just a named bitmap.

Do not announce every one-second sample through assistive technology. Provide user-controlled summaries and prioritized meaningful state transitions. Focus is stable during updates and selection follows object identity. Copy actions expose the precise selected data and optionally include source/time context.

## Native adaptation

Use the platform's accessibility framework in the native adapter. Custom drawn controls require explicit semantic roles/patterns and keyboard behaviour; painted text alone is insufficient. The test harness can inspect programmatic properties but human usability/accessibility review remains separately recorded.

Support high contrast, scalable text, reduced motion, keyboard navigation and non-colour status labels. Critical conditions remain visible when theme colours are overridden. Density can increase but minimum readability is not sacrificed merely to fit every metric.

## Localization

Separate user text from keys and protocol values. Translate labels/help using stable message IDs; keep invariant JSON keys and export units. Handle bidirectional and non-Latin text, fallback fonts, localized numeric/date display, pluralization and longer translations. Device-provided strings are untrusted; sanitize control characters without corrupting legitimate names.

Do not infer language from a performance-counter display name. Native collectors must use documented invariant identifiers where available or an explicit localized mapping. Configuration remains portable between locales.

## Acceptance

Perform keyboard-only settings/editor tasks, accessibility-tree assertions, focus retention under telemetry updates, high-contrast/reduced-motion tests and representative screen-reader review on named platforms. Include long translated labels, right-to-left content and mixed-direction device identifiers. A screenshot existence check cannot count as accessibility qualification.
