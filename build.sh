#!/bin/bash
# PhyloForester Build Script (Linux/macOS)
# Usage: ./build.sh

set -e

echo "======================================"
echo "Building PhyloForester..."
echo "======================================"
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller is not installed."
    echo "Install it with: pip install pyinstaller"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/
echo ""

# Run PyInstaller
echo "Running PyInstaller..."
pyinstaller --clean PhyloForester.spec
echo ""

# Check if build was successful
if [ -d "dist/PhyloForester" ]; then
    echo "======================================"
    echo "Build complete!"
    echo "======================================"
    echo ""
    echo "Output directory: dist/PhyloForester/"
    echo ""
    echo "To run the application:"
    echo "  cd dist/PhyloForester"
    echo "  ./PhyloForester"
    echo ""
else
    echo "======================================"
    echo "Build failed!"
    echo "======================================"
    exit 1
fi
