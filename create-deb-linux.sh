#!/bin/bash
# create-deb-linux.sh
# Create Linux DEB package for Whiz

set -e  # Exit on any error

echo "🐧 Creating Linux DEB package..."
echo "================================="

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

# Check for fpm (Ruby gem for creating packages)
if ! command -v fpm &> /dev/null; then
    echo "📦 Installing fpm..."
    echo "This requires Ruby and gem. Installing dependencies..."
    
    # Install Ruby and gem
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y ruby ruby-dev build-essential
    elif command -v yum &> /dev/null; then
        sudo yum install -y ruby ruby-devel gcc make
    elif command -v pacman &> /dev/null; then
        sudo pacman -S ruby
    else
        echo "❌ Error: Cannot install Ruby automatically"
        echo "Please install Ruby and gem manually, then run:"
        echo "  gem install fpm"
        exit 1
    fi
    
    # Install fpm
    gem install fpm
else
    echo "✅ fpm already available"
fi

# Create installers directory
mkdir -p installers

# Create package structure
echo "📁 Creating package structure..."
mkdir -p whiz-package/opt/whiz
mkdir -p whiz-package/usr/share/applications
mkdir -p whiz-package/usr/share/icons/hicolor/256x256/apps
mkdir -p whiz-package/usr/bin

# Copy executable
cp dist/Whiz whiz-package/opt/whiz/

# Create desktop entry
cat > whiz-package/usr/share/applications/whiz.desktop << EOF
[Desktop Entry]
Name=Whiz Voice-to-Text
Comment=AI-powered voice transcription
Exec=/opt/whiz/Whiz
Icon=whiz
Terminal=false
Type=Application
Categories=Utility;Audio;AudioVideo;
StartupWMClass=Whiz
EOF

# Create launcher script
cat > whiz-package/usr/bin/whiz << EOF
#!/bin/bash
# Whiz launcher script
exec /opt/whiz/Whiz "\$@"
EOF
chmod +x whiz-package/usr/bin/whiz

# Create icon (placeholder)
echo "🎨 Creating placeholder icon..."
convert -size 256x256 xc:blue -fill white -pointsize 48 -gravity center -annotate +0+0 "W" whiz-package/usr/share/icons/hicolor/256x256/apps/whiz.png 2>/dev/null || {
    echo "⚠️  ImageMagick not available, creating simple icon..."
    echo "Whiz Icon" > whiz-package/usr/share/icons/hicolor/256x256/apps/whiz.png
}

# Create DEB package
echo "📦 Creating DEB package..."
fpm -s dir -t deb \
    -n whiz \
    -v 1.0.0 \
    --description "AI-powered voice transcription tool" \
    --url "https://github.com/yourusername/whiz" \
    --license "MIT" \
    --category "Utility" \
    --maintainer "Whiz Development Team <dev@whiz.app>" \
    --vendor "Whiz Development Team" \
    --depends "python3" \
    --depends "libasound2" \
    --depends "libx11-6" \
    --depends "libqt5core5a" \
    --depends "libqt5gui5" \
    --depends "libqt5widgets5" \
    -C whiz-package \
    -p installers/

# Check if DEB was created successfully
deb_file=$(ls installers/*.deb | head -1)
if [ -f "$deb_file" ]; then
    echo ""
    echo "✅ [SUCCESS] DEB package created!"
    echo "📁 Location: $deb_file"
    echo "📏 Size: $(du -sh "$deb_file" | cut -f1)"
    echo ""
    echo "🚀 To install the DEB package:"
    echo "   sudo dpkg -i $deb_file"
    echo ""
    echo "🚀 To test the installation:"
    echo "   whiz"
    echo ""
    echo "📋 Installation instructions:"
    echo "   1. Download the DEB package"
    echo "   2. Install: sudo dpkg -i whiz_1.0.0_amd64.deb"
    echo "   3. Fix dependencies if needed: sudo apt-get install -f"
    echo "   4. Launch: whiz"
else
    echo "❌ [ERROR] DEB package creation failed!"
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -rf whiz-package

echo "✅ DEB package creation complete!"