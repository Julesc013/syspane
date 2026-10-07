---
type: "SysPane Work Package"
title: "Lossless native binding text"
description: "Preserve binding strings that native text buffers cannot represent literally."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T07:33:52.457113+00:00"}
sp_id: "SP-W10-BINDING-TEXT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-BINDING-AUTHORING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Lossless native binding text

This extension closes the native-buffer representation boundary discovered while
implementing binding authoring. Keep the original package and fixed scenes intact.
Binding 0.1 permits control characters in predicate text and persistent keys; the
shared private text widget deliberately rejects tabs, carriage returns and NUL.
Never load such a value as an empty buffer and later serialize that empty buffer.

Predicate text and persistent keys therefore offer literal and escaped formats.
Literal remains the default and preserves bytes without trimming or coercion.
Escaped format is one quoted JSON string token, including its quotes: for example
`"a\tb"` denotes a tab; `"a\\tb"` denotes a literal backslash followed by t.
No descriptor/object editing is required. Reject malformed escapes, non-string
JSON, surrounding whitespace and lone surrogates. Format is private input metadata;
the authored document stores only the decoded string. Boolean/number predicates
ignore the inactive text format.

When opening an existing value, use escaped format if it contains C0 controls
other than LF, or DEL; otherwise use literal. Encode using compact UTF-8 JSON
string serialization. The native field permits 4096 input characters/bytes per
insertion, enough for a quoted token representing 512 fully escaped C0 scalars.
The existing 512-decoded-scalar binding limit still applies. Other private text
controls keep their supplied limits; no product input limit is enlarged.

Choosing a format interprets the current buffer in that format; it does not guess
or normalize the user's text. Invalid intermediate escaped input remains private
across row switches. Set validates all active decoded values atomically. Native
erasure clears encoded buffers and format models just like literal input.

Freeze exact text cases and a complete expected control-character scene before
implementing this extension. Verify quoted/backslash/control/Unicode distinctions,
512-scalar boundaries and invalid tokens portably. The native case must author,
save, reopen and no-op Set an escaped predicate without losing the original bytes.
