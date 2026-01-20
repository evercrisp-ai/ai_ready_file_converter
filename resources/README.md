# Resources

This directory contains resources for the macOS desktop app.

## App Icon

To add a custom app icon, create `icon.icns` in this directory.

### Creating an .icns file from a PNG:

1. Create a 1024x1024 PNG image
2. Use the following command to convert it:

```bash
# Create iconset directory
mkdir icon.iconset

# Generate required sizes
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# Create icns file
iconutil -c icns icon.iconset -o icon.icns

# Clean up
rm -rf icon.iconset
```

Or use an online converter like [cloudconvert.com](https://cloudconvert.com/png-to-icns).
