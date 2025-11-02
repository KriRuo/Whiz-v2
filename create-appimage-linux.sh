#!/bin/bash
# create-appimage-linux.sh
# Create Linux AppImage for Whiz

set -e  # Exit on any error

echo "🐧 Creating Linux AppImage..."
echo "=============================="

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: This script must be run on Linux"
    exit 1
fi

# Check if the executable exists
if [ ! -f "dist/Whiz" ]; then
    echo "❌ Error: Whiz executable not found in dist/"
    echo "Please run build-linux.sh first"
    exit 1
fi

# Create installers directory
mkdir -p installers

# Check for AppImage tools
if ! command -v appimagetool &> /dev/null; then
    echo "📦 Installing AppImage tools..."
    
    # Download AppImageTool
    wget -O appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool
    
    # Download AppRun
    wget -O AppRun https://github.com/AppImage/AppImageKit/releases/download/continuous/AppRun-x86_64
    chmod +x AppRun
else
    echo "✅ AppImage tools already available"
fi

# Create AppDir structure
echo "📁 Creating AppDir structure..."
mkdir -p Whiz.AppDir/usr/bin
mkdir -p Whiz.AppDir/usr/share/applications
mkdir -p Whiz.AppDir/usr/share/icons/hicolor/256x256/apps

# Copy executable
cp dist/Whiz Whiz.AppDir/usr/bin/

# Create desktop entry
cat > Whiz.AppDir/usr/share/applications/whiz.desktop << EOF
[Desktop Entry]
Name=Whiz Voice-to-Text
Comment=AI-powered voice transcription
Exec=whiz
Icon=whiz
Terminal=false
Type=Application
Categories=Utility;Audio;AudioVideo;
StartupWMClass=Whiz
EOF

# Create icon (placeholder - you can replace with actual icon)
echo "🎨 Creating placeholder icon..."
convert -size 256x256 xc:blue -fill white -pointsize 48 -gravity center -annotate +0+0 "W" Whiz.AppDir/usr/share/icons/hicolor/256x256/apps/whiz.png 2>/dev/null || {
    echo "⚠️  ImageMagick not available, creating simple icon..."
    # Create a simple text file as icon placeholder
    echo "Whiz Icon" > Whiz.AppDir/usr/share/icons/hicolor/256x256/apps/whiz.png
}

# Copy AppRun
cp AppRun Whiz.AppDir/
chmod +x Whiz.AppDir/AppRun

# Create AppImage
echo "📦 Creating AppImage..."
./appimagetool Whiz.AppDir installers/Whiz-v1.0.0-Linux.AppImage

# Check if AppImage was created successfully
if [ -f "installers/Whiz-v1.0.0-Linux.AppImage" ]; then
    echo ""
    echo "✅ [SUCCESS] AppImage created!"
    echo "📁 Location: installers/Whiz-v1.0.0-Linux.AppImage"
    echo "📏 Size: $(du -sh installers/Whiz-v1.0.0-Linux.AppImage | cut -f1)"
    echo ""
    echo "🚀 To test the AppImage:"
    echo "   chmod +x installers/Whiz-v1.0.0-Linux.AppImage"
    echo "   ./installers/Whiz-v1.0.0-Linux.AppImage"
    echo ""
    echo "📋 Installation instructions:"
    echo "   1. Download the AppImage"
    echo "   2. Make it executable: chmod +x Whiz-v1.0.0-Linux.AppImage"
    echo "   3. Run directly: ./Whiz-v1.0.0-Linux.AppImage"
    echo "   4. Optional: Move to /opt/ or ~/Applications/"
else
    echo "❌ [ERROR] AppImage creation failed!"
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -rf Whiz.AppDir
rm -f appimagetool AppRun

echo "✅ AppImage creation complete!"
