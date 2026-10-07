---
type: "SysPane Work Package"
title: "Unavailable container preview and authored recovery"
description: "Distinguish renderer rejection from an absent display and retain usable authored controls."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T11:49:03.675771+00:00"}
sp_id: "SP-W10-CONTAINER-PREVIEW"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-CONTAINERS", "SP-W09-LAYOUT", "SP-W10-NATIVE-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Unavailable container preview and authored recovery

Extend the container package without changing its frozen scenes, transformation
semantics or renderer acceptance. A valid authored canvas can be too small to display
its flowing children. The renderer returns an alternative state with no frame;
that is not evidence that the selected object belongs to another display.

When the renderer reports alternative, show an accessible unavailable-preview
explanation alongside the existing dirty/request/durable status. Do not replace
those independent facts or report the selected object as absent from this display.
Keep the authored Scene objects list and permitted Layout/Undo actions usable so
the user can repair the draft. Do not show clipped content as a successful preview,
commit automatically, discard the draft or modify renderer thresholds.

Freeze a supplemental native case before the status correction. Wrap the two
existing flow children in a 180-by-80 canvas. Both 80-DIP children remain authored;
require a cleared preview, explicit unavailable status, correct selected identity,
no false display-absence message and unchanged storage. Undo must restore the
original pixels; Redo must reproduce unavailability. Use Layout to change the
container to the already frozen 400-by-180 canvas. Require the original exact
fitted pixels/scene, two-step undo/redo, durable save/reopen and unchanged resources.

Keep all original container cases and negative controls. Preserve the pre-correction
failure, new fixture/package identities and subsequent native evidence. This closes
status and authored recovery for rejected previews; complete inspector/desktop
alternatives and full accessibility qualification remain separate release gates.
