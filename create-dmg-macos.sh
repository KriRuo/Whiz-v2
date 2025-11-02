#!/bin/bash
# create-dmg-macos.sh
# Create macOS DMG installer for Whiz

set -e  # Exit on any error

echo "🍎 Creating macOS DMG installer..."
echo "=================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script must be run on macOS"
    exit 1
fi

# Check if the app exists
if [ ! -d "dist/Whiz.app" ]; then
    echo "❌ Error: Whiz.app not found in dist/"
    echo "Please run build-macos.sh first"
    exit 1
fi

# Create installers directory
mkdir -p installers

# Create DMG
echo "📦 Creating DMG installer..."
hdiutil create -volname "Whiz" \
    -srcfolder dist/Whiz.app \
    -ov \
    -format UDZO \
    installers/Whiz-v1.0.0-macOS.dmg

# Check if DMG was created successfully
if [ -f "installers/Whiz-v1.0.0-macOS.dmg" ]; then
    echo ""
    echo "✅ [SUCCESS] DMG installer created!"
    echo "📁 Location: installers/Whiz-v1.0.0-macOS.dmg"
    echo "📏 Size: $(du -sh installers/Whiz-v1.0.0-macOS.dmg | cut -f1)"
    echo ""
    echo "🚀 To test the DMG:"
    echo "   open installers/Whiz-v1.0.0-macOS.dmg"
    echo ""
    echo "📋 Installation instructions:"
    echo "   1. Double-click the DMG file"
    echo "   2. Drag Whiz.app to Applications folder"
    echo "   3. Launch from Applications or Launchpad"
else
    echo "❌ [ERROR] DMG creation failed!"
    exit 1
fi