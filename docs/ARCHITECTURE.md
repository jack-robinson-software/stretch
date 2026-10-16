# How Stretch fits together

Stretch is a small native AppKit app, compiled directly with `swiftc`. There is no package manager or web runtime in the desktop app.

## Desktop app

| File | Responsibility |
| --- | --- |
| [`main.swift`](../mac-app/Sources/main.swift) | Application entry point and bundled self-test |
| [`AppModel.swift`](../mac-app/Sources/AppModel.swift) | Product/character metadata, movement choices, session states, reminder scheduling and local preferences |
| [`StretchApp.swift`](../mac-app/Sources/StretchApp.swift) | Menu bar, floating panel, settings window and interaction flow |
| [`AppViews.swift`](../mac-app/Sources/AppViews.swift) | Speech bubble, native buttons, progress indicator and transparent frame player |

The normal flow is **hidden → invitation → movement → completion → leaving → hidden**. A person can dismiss an invitation or finish a movement early. “Another” cycles through movements of the same kind. Seated completion keeps Pip in the chair; standing completion plays a celebration and walk-off.

The borderless nonactivating panel sits near the top right of the current screen. The character and transparent area pass clicks through; the bubble accepts them. Opening Settings is an explicit activation. The frame player uses elapsed time at 30 fps, a limited image cache and short crossfades, and stops its rendering timer while hidden.

Preferences use UserDefaults. The reminder timer follows the selected interval and daily work hours. No usage or activity data is stored. Existing preferences from the earlier Pip-named prototype migrate on first launch.

## Assets and preview

The app bundle template contains `Resources/Clips/<clip>/<frame>.png`, at 300 × 360. Full-resolution source sequences remain alongside the Blender scenes, at 600 × 720. [`package_assets.py`](../mac-app/package_assets.py) creates the smaller app frames; [`make_web_assets.py`](../mac-app/make_web_assets.py) creates animated WebP files for the independent HTML preview.

The bundle identifier is `dev.jackrobinsonsoftware.stretch.prototype`. `build.sh` creates the executable and signs the local bundle ad hoc; it does not produce a notarised distribution build.

## Product and character identity

`AppIdentity` describes Stretch. `CompanionCharacter` describes Pip. The prototype has one character and one packaged clip set; it does not yet have a character plug-in format, dynamic asset loader or picker. Keep new character work independent of the product name, and discuss a shared asset contract before adding another complete library.

## Optional support links

The app always exposes its source repository. A donation menu item appears only when `StretchSupportURL` is configured. [`configure_support.py`](../scripts/configure_support.py) updates that setting, the README and GitHub funding configuration together. See [support setup](../SUPPORT.md).
