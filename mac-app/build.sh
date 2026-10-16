#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p Stretch.app/Contents/MacOS Stretch.app/Contents/Resources
swiftc -O -swift-version 5 -target arm64-apple-macos13.0 -framework AppKit -framework QuartzCore -framework ImageIO Sources/*.swift -o Stretch.app/Contents/MacOS/Stretch
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' Stretch.app/Contents/Info.plist >/dev/null
codesign --force --deep --sign - Stretch.app
