---
type: "SysPane Work Package"
title: "Versioned theme typography and native font roles"
description: "Exact authored font roles, bounded resolution and capability-bound native text rendering."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T02:00:00Z"}
sp_id: "SP-W09-TYPOGRAPHY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-NATIVE-TEXT", "SP-W10-VISIBILITY-CONTROLS", "SP-SCENE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Versioned theme typography and native font roles

Continue the existing theme, immutable resource and native text owners. Theme 0.2
adds explicit font weight/style and named roles. Keep theme 0.1 and every existing
scene/command/schema meaning unchanged. Native theme-authoring controls, installed
ownership and the five full editions remain required after this boundary.

## Authored meaning and limits

Theme 0.2 retains theme 0.1 IDs, names, five color tokens, motion and optional
extensions. Its required font contains family, size_dip, weight and style. Family
is one UTF-8 font-family name, 1..128 Unicode scalars and at most 512 bytes, without
C0/C1 controls, comma, leading/trailing ASCII space, or an all-space value. It is
data, never Pango markup or a font-description expression. size_dip is finite,
9..72 inclusive. Weight is one of 100,200,300,400,500,600,700,800,900; style is
normal, italic or oblique. Unknown members and null are invalid.

Optional font_roles is a closed object containing any of body, label, value and
diagnostic. Every present role is a complete font with those four members; no
partial inheritance or null removal is admitted. An absent role uses font exactly.
An empty font_roles has the same rendering as absence, while authored bytes remain
distinct and are preserved. The document remains at most 256 KiB. Optional extension
content keeps its existing meaning and cannot introduce a font role.

The shared resolver accepts a validated theme and one of the four exact role names.
For theme 0.1, every role resolves its existing family/size plus weight 400 and style
normal. For theme 0.2 it selects the complete requested role or base font. No role
falls back to another role. Invalid roles reject even for theme 0.1. Resolution
returns an owned value and does not mutate or downgrade the authored document.

An unavailable requested family uses the native adapter's existing font fallback.
Keep the authored name and report actual selected families and missing glyphs.
No download, filesystem font import, embedding or new application cache is admitted.
Native adapters may substitute a nearest available weight/style; actual raster
evidence is target-specific. This is not cross-platform glyph equivalence.

## Resource and rendering admission

ContentCatalog accepts versioned theme documents through the existing immutable
package/asset hashes. A resolved theme 0.2 adds required capability theme.typography,
even when the package omitted that declaration. Resource authorization rejects a
missing or policy-denied capability before publication. Current policy is rechecked
by existing transaction and presentation owners; exact theme/package pins remain.
Theme 0.1 does not acquire the new capability. Existing command versions suffice
because they reference immutable content identities rather than inline theme edits.

TextRequest gains an explicit role, default body. The native adapter selects the
resolved family, DIP size, weight and style with separate native setters. All current
UTF-8, language, line, wrap, pixel, scale, color, alpha, fallback and contrast rules
remain. Never parse family as a combined font description. Contrast modes alter
colors through the existing contract and do not rewrite authored typography.

This package establishes font rendering and resource admission. SceneSurface must
refuse a theme 0.2 with alternative/surface.typography_unavailable before creating
text/image/chart caches until a following composition package assigns all text roles
and proves mandatory diagnostic preservation. Listing theme.typography alone cannot
enable that presentation. No generic default-body rendering may silently stand in
for complete role-aware composition. Existing themes continue rendering unchanged.

## Independent acceptance

Freeze this package, schema, literal complete fonts, role-resolution results and
negative examples before production changes. Independently validate schema cases.
Portable tests cover all four roles, base fallback, legacy equivalence, exact fractional
size, extreme weights/styles, invalid role/member/family/size/weight/style, owned
results, original document preservation and resource capability/policy admission.
Use exact immutable pins and verify returned resources preserve original bytes.

The non-root native text experiment uses the pinned runtime/fonts and retained raw
RGBA/metric records. Check legacy/base equivalence, each role against an independently
specified equivalent base font, bold/italic distinctions, fractional size/scale,
missing-family fallback, contrast colors, literal family handling and rejection
without partial raster output. Deliberately ignored-role and ignored-weight probes
must produce positive pixel differences from the expected raster. Missing output,
timeouts or errors never establish detection. Preserve native source/artifact/runtime
identities, failures and fixed inputs. Exercise the explicit SceneSurface refusal.

Run affected and full portable checks on Linux GCC13, Windows GCC15 and v141_xp;
run native text and relevant scene/editor regressions on the owned Linux laboratory.
Historical toolset execution remains contemporary-host evidence only. Reclaim only
verified committed output duplicates within the existing 7 GiB allocation.

Then implement role-aware scene composition and native theme authoring through the
existing draft, resource and durable transaction owners. Close their own input,
role mapping, failure, erasure and acceptance boundaries before enabling them.
This package does not complete W-09/W-10 or any release edition.

Native API references: [family](https://docs.gtk.org/Pango/method.FontDescription.set_family.html),
[weight](https://docs.gtk.org/Pango/method.FontDescription.set_weight.html),
and [style](https://docs.gtk.org/Pango/method.FontDescription.set_style.html).
Use the pinned installed headers; current web documentation does not update the toolchain.
