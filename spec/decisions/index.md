# decisions index

Generated navigation; edit the referenced source documents, then run `specctl.py generate`.

- [Own the complete native vertical stack](001-native-product.md) — Decision proposal: No Desktop Info or other display engine is a required component.
- [Keep spec, docs and source distinct](002-canonical-bundle.md) — Decision proposal: Root spec/ owns intent/contracts; docs/ owns audience-oriented explanation; source/ owns implementation.
- [Use pinned OKF v0.2 with a local authoring profile](003-okf-profile.md) — Decision proposal: Use Markdown, YAML-frontmatter JSON-flow values and stable sp_id metadata.
- [Share meaning and operations, not every binary or pixel](004-native-adapters.md) — Decision proposal: Portable C++17 engine with native platform adapters and reduced profiles where justified.
- [Isolate the Windows surface process](005-surface-isolation.md) — Decision proposal: Controller state/history/inspector survive a failed desktop host or renderer.
- [Use one validated operation system](006-transactions.md) — Decision proposal: GUI, desktop editor, CLI and API submit the same typed revisioned transactions.
- [Separate specification success from product qualification](007-evidence.md) — Decision proposal: Planning and schema checks never produce a native compatibility pass.
- [Treat AIDE as a replaceable development control plane](008-aide-boundary.md) — Decision proposal: Pin real upstream contracts before admitting a consumer adapter.
