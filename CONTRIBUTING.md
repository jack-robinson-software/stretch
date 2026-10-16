# Contributing to Stretch

Thanks for helping make small movement breaks feel friendly. Stretch is the app; Pip is its first character. Issues and pull requests are welcome.

## Get started

1. Fork and clone the repository.
2. On an Apple Silicon Mac with macOS 13+ and Apple Command Line Tools, run:

   ```sh
   cd mac-app
   ./build.sh
   ./Stretch.app/Contents/MacOS/Stretch --self-test
   open Stretch.app
   ```

3. Try the invitation, seated and standing pauses, Another, All done, Not now and the menu-bar settings. Check that showing Pip does not take keyboard focus and that clicks outside the bubble reach the app underneath.

The browser preview at `mac-app/preview.html` can be opened directly. It demonstrates the experience; it does not schedule desktop reminders.

## Making changes

- Keep pull requests focused. Describe the problem, resulting behaviour and how you checked it. Include a screenshot or short video for visible or animation changes.
- Keep reminders optional, quiet and easy to dismiss. Preserve the seated flow for people who want to remain in their chair.
- Keep app identity separate from character identity. Additional characters should come with their editable source assets and movement exports.
- Ask in an issue before substantially changing Pip's approved appearance, the asset format or the app architecture.
- For Blender and animation changes, include the authoring source and appropriate validation results. See `animations/README.md` and `seated/README.md`. Avoid committing local build products, caches or logs.
- Only contribute code and assets you have permission to share under the project's MIT licence.

## Bugs and ideas

Open an issue with your macOS version, steps to reproduce, expected behaviour and what happened. Movement and character ideas are welcome too. This is an early prototype, so some product features are still being explored.

## Optional financial support

Maintainers can enable Buy Me a Coffee using [the support setup guide](SUPPORT.md). Contributions and use of Stretch never require a donation.
