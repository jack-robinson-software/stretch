#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p Pip.app/Contents/MacOS Pip.app/Contents/Resources
swiftc -O -swift-version 5 -target arm64-apple-macos13.0 -framework AppKit -framework QuartzCore -framework ImageIO Sources/*.swift -o Pip.app/Contents/MacOS/Pip
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' Pip.app/Contents/Info.plist >/dev/null
codesign --force --deep --sign - Pip.app
