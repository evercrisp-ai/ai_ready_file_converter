#!/bin/bash
#
# Build script for AI Ready File Converter macOS desktop app
#
# Usage:
#   ./scripts/build_macos.sh [options]
#
# Options:
#   --dev       Build in development/alias mode (faster, for testing)
#   --clean     Clean build directories before building
#   --dmg       Create a DMG disk image after building
#   --notarize  Notarize the app (requires Apple Developer credentials)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Parse arguments
DEV_MODE=false
CLEAN=false
CREATE_DMG=false
NOTARIZE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --dmg)
            CREATE_DMG=true
            shift
            ;;
        --notarize)
            NOTARIZE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

cd "$PROJECT_DIR"

echo -e "${GREEN}=== AI Ready File Converter - macOS Build ===${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "Python version: ${YELLOW}$PYTHON_VERSION${NC}"

# Check for virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Not running in a virtual environment${NC}"
    echo "It's recommended to use a virtual environment for building."
    echo ""
fi

# Clean if requested
if $CLEAN; then
    echo -e "${YELLOW}Cleaning build directories...${NC}"
    rm -rf build dist
    echo "Done."
    echo ""
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements-desktop.txt --quiet
echo "Done."
echo ""

# Create resources directory if it doesn't exist
mkdir -p resources

# Check for app icon
if [[ ! -f "resources/icon.icns" ]]; then
    echo -e "${YELLOW}Note: No app icon found at resources/icon.icns${NC}"
    echo "The app will use the default Python icon."
    echo "To add a custom icon, create resources/icon.icns"
    echo ""
fi

# Build the app
echo -e "${YELLOW}Building macOS app...${NC}"
if $DEV_MODE; then
    echo "(Development/alias mode - faster but not redistributable)"
    python3 setup_desktop.py py2app -A
else
    echo "(Production mode - fully bundled)"
    python3 setup_desktop.py py2app
fi
echo ""

# Check if build succeeded
if [[ ! -d "dist/AI Ready File Converter.app" ]]; then
    echo -e "${RED}Error: Build failed - app bundle not found${NC}"
    exit 1
fi

APP_PATH="dist/AI Ready File Converter.app"
APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)

echo -e "${GREEN}Build successful!${NC}"
echo -e "App location: ${YELLOW}$APP_PATH${NC}"
echo -e "App size: ${YELLOW}$APP_SIZE${NC}"
echo ""

# Create DMG if requested
if $CREATE_DMG; then
    echo -e "${YELLOW}Creating DMG disk image...${NC}"
    
    DMG_NAME="AIReadyFileConverter"
    DMG_PATH="dist/$DMG_NAME.dmg"
    
    # Remove existing DMG
    rm -f "$DMG_PATH"
    
    # Create DMG
    hdiutil create -volname "$DMG_NAME" \
        -srcfolder "$APP_PATH" \
        -ov -format UDZO \
        "$DMG_PATH"
    
    DMG_SIZE=$(du -sh "$DMG_PATH" | cut -f1)
    echo -e "${GREEN}DMG created: ${YELLOW}$DMG_PATH${NC} ($DMG_SIZE)"
    echo ""
fi

# Notarize if requested
if $NOTARIZE; then
    echo -e "${YELLOW}Notarizing app...${NC}"
    
    if [[ -z "$APPLE_ID" ]] || [[ -z "$APPLE_TEAM_ID" ]]; then
        echo -e "${RED}Error: APPLE_ID and APPLE_TEAM_ID environment variables required${NC}"
        echo "Set these before running with --notarize:"
        echo "  export APPLE_ID='your-apple-id@email.com'"
        echo "  export APPLE_TEAM_ID='XXXXXXXXXX'"
        exit 1
    fi
    
    # Create a zip for notarization
    ZIP_PATH="dist/AIReadyFileConverter-notarize.zip"
    ditto -c -k --keepParent "$APP_PATH" "$ZIP_PATH"
    
    # Submit for notarization
    echo "Submitting to Apple for notarization..."
    xcrun notarytool submit "$ZIP_PATH" \
        --apple-id "$APPLE_ID" \
        --team-id "$APPLE_TEAM_ID" \
        --wait
    
    # Staple the ticket
    echo "Stapling notarization ticket..."
    xcrun stapler staple "$APP_PATH"
    
    rm -f "$ZIP_PATH"
    echo -e "${GREEN}Notarization complete!${NC}"
    echo ""
fi

echo -e "${GREEN}=== Build Complete ===${NC}"
echo ""
echo "To run the app:"
echo "  open \"$APP_PATH\""
echo ""
if ! $DEV_MODE; then
    echo "To distribute:"
    echo "  1. Zip the app: zip -r dist/AIReadyFileConverter.zip \"$APP_PATH\""
    echo "  2. Or create a DMG: ./scripts/build_macos.sh --dmg"
    echo ""
fi
