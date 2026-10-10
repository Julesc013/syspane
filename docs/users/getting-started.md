# Getting started

SysPane is still in development. The Linux development frontend has native
settings, scene editing, draft recovery and saved-scene inspection. No complete
desktop edition or qualified release package is available yet. Use
[developer setup](../developers/build.md) for the development build and its checks.
Maximum-size recovery inputs currently exceed the required responsiveness limit
in two test cases; that qualification remains open.

Choose Inspect scene to browse the saved arrangement. The Item and Information
columns show each group and widget; Summary displays the selected row's requested
snapshot. Apply or discard unsaved edits before switching views. When current
policy permits collection and disclosure, the network table shows received/sent
bytes and rates while inspection is open. Switching views stops that collection.
Without an admitted provider, the table reports Unsupported field.

If the source disconnects, previously displayed values may remain marked retained
with unknown age. They are not current measurements. A replacement source supplies
fresh state; revoked disclosure clears the old values. Positive policy is currently
tested through the development fixture; production deployment remains unqualified.

The planned first-use journey is to launch a native package, inspect host and
network state, enter Edit Desktop, move or resize a pane, choose a theme, apply,
reveal the desktop, observe a real change and reopen the saved arrangement.
Unavailable information will carry its source status rather than a healthy zero.

Windows, Linux and macOS editions must qualify named native profiles. XP/7 and
older OS X investigations remain in the first campaign. A useful inspector does
not establish persistent desktop support. The optional screensaver will have
separate preview, configuration, privacy and host qualification.

See [configuration](configuration.md), [recovery](troubleshooting.md) and
[platform intent](../../spec/product/platforms.md). These guides identify available
development controls and the remaining planned product behaviour.
