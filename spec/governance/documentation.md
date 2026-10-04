---
type: "SysPane Specification"
title: "Documentation publishing and editorial ownership"
description: "Keep a readable public product story without duplicating specification authority."
tags: ["governance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-DOCS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-REPOSITORY", "SP-AUTHORITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Documentation publishing and editorial ownership

## Distinct jobs

`spec/` contains normative design, requirements, contracts, tests and development governance in OKF Markdown/JSON. `docs/` contains reviewed user/developer guides and publishable explanatory Markdown. Root README introduces the product and its actual stage. The optional website/wiki is a projection, not another writable source of requirements.

Do not blindly strip frontmatter and publish the entire spec as the user manual. A user guide is task-oriented: install, launch, inspect a network, edit desktop, choose a theme, manage history, export diagnostics, troubleshoot and uninstall. Developer guides explain build prerequisites, architecture, adding a provider and running tests. Normative details are linked by stable ID/path.

## Publication map

Maintain `governance/docs-map.json` mapping intended public pages to source concepts/requirements and audience. A change to a mapped source creates a documentation-review candidate. The mapping does not claim natural-language accuracy can be automatically proved. Generated API/reference tables carry input hashes and a regeneration command.

## Editorial constraints

Keep naming, tone and purpose stable. Do not replace the README with gate counts, latest work-unit names or internal orchestration language. Release changes belong in CHANGELOG/release notes. Architecture decisions belong in specs. Do not duplicate screenshots, tables and settings descriptions by hand across competing wiki/docs trees.

Use ordinary Markdown and relative links with stable headings. Include alt text and accessible tables in published documentation. Code samples are tested when executable; schematic examples are labelled. Avoid claims such as “supports all Windows versions” when only specific profiles have been executed.

## Maintenance

Documentation changes are reviewed alongside changed behaviour. Keep migration/deprecation guides for public contracts. A link rot repair does not rewrite technical meaning. Source citations record inspection date and scope; private workshop transcripts are not automatically published.

AIDE may generate a documentation patch, but deterministic checks establish only links/coverage, not human editorial acceptance. Required editorial review is recorded separately. A source-derived page cites its evidence and distinguishes proposed features from shipped ones.

## Published starting guides

Root README is now the product homepage and TODO is an implementation route. Initial
user, operator and developer pages explicitly distinguish planned controls/packages
from runnable specification tooling. Keep generated setting constraints/reference
data bound to descriptors and authored explanations bound through the publication map.
The wiki remains a navigation projection. Raw review transcripts are not published.
