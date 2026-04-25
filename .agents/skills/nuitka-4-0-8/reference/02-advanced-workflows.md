# Nuitka Advanced Workflows

Platform-specific deployment strategies, icons, splash screens, and advanced distribution techniques.

## Windows Deployment

### Creating Executables with Icons

```bash
# Using ICO file (native Windows format)
python -m nuitka --onefile --windows-icon-from-ico=app.ico program.py

# Using PNG file (auto-converted)
python -m nuitka --onefile --windows-icon-from-ico=app.png program.py

# Using template executable's icon
python -m nuitka --onefile --windows-icon-template-exe=template.exe program.py
```

### Version Information

Add metadata to Windows executables:

```bash
python -m nuitka --standalone \
  --windows-company-name="My Company" \
  --windows-product-name="My Application" \
  --windows-copyright="Copyright 2024 My Company" \
  --windows-trademarks="MyApp is a trademark of My Company" \
  --windows-file-description="Description of the application" \
  --windows-internal-name=myapp \
  program.py
```

### Console Window Control

```bash
# Default: No console for GUI apps
python -m nuitka --onefile gui_app.py

# Force console window (for CLI tools or debugging)
python -m nuitka --console=force gui_app.py

# Explicitly no console
python -m nuitka --console=no cli_tool.py
```

### Splash Screens for Onefile

Add splash screen during onefile unpacking:

**In your Python file**:
```python
# nuitka-project: --onefile
# nuitka-project: --onefile-windows-splash-screen-image={MAIN_DIRECTORY}/splash.png

import time, tempfile, os

print("Initializing...")
time.sleep(3)  # Simulate slow startup

# Remove splash screen
if "NUITKA_ONEFILE_PARENT" in os.environ:
    splash_filename = os.path.join(
        tempfile.gettempdir(),
        "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
    )
    if os.path.exists(splash_filename):
        os.unlink(splash_filename)

print("Ready!")
# Rest of application...
```

### Windows Service Creation (Commercial)

Windows service support requires Nuitka Commercial license.

### Visual C++ Runtime Requirements

Target machines need appropriate VC++ redistributables:

| Python Version | VC++ Version | Redistributable |
|---------------|--------------|-----------------|
| 3.11-3.14     | 14.3         | Visual C++ 2022 |
| 3.5-3.10      | 14.2         | Visual C++ 2019 |
| 3.5-3.8       | 14.1         | Visual C++ 2017 |
| 3.5-3.8       | 14.0         | Visual C++ 2015 |
| 3.4           | 10.0         | Visual C++ 2010 |
| 2.6, 2.7      | 9.0          | Visual C++ 2008 |

**MinGW64**: Uses Visual C++ 2015 redistributable for Python 2.6-3.11.

On Windows 10+, `ucrt.dll` is included. For older systems, install redistributables first, then you can remove `api-ms-crt-*.dll` from distribution folder.

## macOS Deployment

### Application Bundles

```bash
# Create .app bundle with Tkinter
python -m nuitka --enable-plugin=tk-inter \
  --onefile=app \
  --macos-app-icon=app_icon.png \
  program.py

# Creates: program.app/Contents/MacOS/program
```

### App Icons

```bash
# PNG format (auto-converted to ICNS)
python -m nuitka --macos-app-icon=icon.png --onefile=app program.py

# ICNS format (native)
python -m nuitka --macos-app-icon=icon.icns --onefile=app program.py
```

### Entitlements and Protected Resources

Request access to protected resources:

```bash
python -m nuitka --onefile=app \
  --macos-app-protected-resource=NSMicrophoneUsageDescription:"This app needs microphone access" \
  --macos-app-protected-resource=NSCameraUsageDescription:"Camera access for video calls" \
  --macos-app-protected-resource=NSPhotoLibraryUsageDescription:"Access photos" \
  program.py
```

**Important**: Quote descriptions with spaces properly for shell parsing.

Available entitlements: https://developer.apple.com/documentation/bundleresources/information_property_list/protected_resources

### Code Signing (Not Automatic)

Nuitka does not automatically sign applications. Sign after compilation:

```bash
# Sign the app bundle
codesign --deep --force --sign "Developer ID Application: Your Name" program.app

# Notarize for Gatekeeper
xcrun notarytool submit program.app --apple-id your@email.com --password xxx --team-id XXXXXXXX
```

### Python Source Requirements

- **Use Homebrew Python**: `brew install python@3.11`
- **Avoid pyenv**: Known incompatibility with standalone mode
- **Static linking**: Install with `conda install libpython-static` (Anaconda)

## Linux Deployment

### Building for Maximum Compatibility

**Critical**: Build on the oldest target OS to ensure glibc compatibility.

```bash
# Example: Build CentOS 7 container for wide compatibility
docker run -v $(pwd):/work centos:7 /bin/bash
# Inside container:
# - Install Python (use deadsnakes PPA or compile from source)
# - Install Nuitka and build tools
# - Compile with --standalone
# - Copy .dist folder out
```

### Static Linking

For better portability, statically link libpython:

```bash
# Requires static libpython (Anaconda or self-compiled)
python -m nuitka --standalone --static-libpython=yes program.py
```

**Benefits**:
- Fewer runtime dependencies
- Better compatibility across distributions
- Smaller distribution size (sometimes)

### Including System Libraries

Some packages require system libraries:

```bash
# Include specific shared library
python -m nuitka --standalone \
  --include-dll-by-name=libssl.so.1.1,libcrypto.so.1.1 \
  program.py

# Or use plugin for known packages
python -m nuitka --standalone --enable-plugin=numpy program.py
```

### Finding Data Files

Use `__compiled__.containing_dir` for files near the executable:

```python
import os

try:
    # Works in standalone and onefile modes
    data_dir = __compiled__.containing_dir
except NameError:
    # Fallback for uncompiled execution
    data_dir = os.path.dirname(sys.argv[0])

config_path = os.path.join(data_dir, "config.ini")
```

## Cross-Platform Considerations

### Path Separators

Always use `os.path.join()` for paths:

```python
# Correct
config_path = os.path.join(os.path.dirname(__file__), "config.ini")

# Wrong (fails on Windows)
config_path = os.path.dirname(__file__) + "/config.ini"
```

### Line Endings in Data Files

Read text files with universal newline support:

```python
# Python 3 - default is universal newlines
with open("file.txt", "r") as f:
    content = f.read()

# Binary mode for non-text files
with open("image.png", "rb") as f:
    data = f.read()
```

### Platform Detection

```python
import sys

if sys.platform == "win32":
    # Windows-specific code
    exe_suffix = ".exe"
elif sys.platform == "darwin":
    # macOS-specific code
    exe_suffix = ""
else:
    # Linux/Unix
    exe_suffix = ""
```

## Onefile Advanced Options

### Temporary Directory Control

```bash
# Use specific temp directory pattern
python -m nuitka --onefile \
  --onefile-tempdir-spec=C:/Temp/MyApp-* \
  program.py

# Keep temp directory (don't delete after execution)
python -m nuitka --onefile \
  --onefile-keep-tempdir \
  program.py

# Use current directory as temp
python -m nuitka --onefile \
  --onefile-tempdir-spec=. \
  program.py
```

### Compression Control

```bash
# Disable compression (faster startup, larger file)
python -m nuitka --onefile --onefile-compression=no program.py

# Use specific compression (requires zstandard package)
python -m nuitka --onefile --onefile-compression=zstd program.py
```

### Original argv[0] Access

In onefile mode, `sys.argv[0]` is modified. Access original:

```python
# Get original invocation path
original = getattr(__compiled__, 'original_argv0', None)

# Example: /usr/local/bin/app (symlink) invoked as 'app'
# sys.argv[0] == "/usr/local/bin/app"
# __compiled__.original_argv0 == "app"
```

## Debugging GUI Applications

### Capturing Output from Windows GUI Apps

Windows GUI apps don't show console output by default:

```bash
# Force stdout/stderr to files
python -m nuitka --onefile \
  --force-stdout-spec=stdout.txt \
  --force-stderr-spec=stderr.txt \
  gui_app.py

# Run compiled app - output goes to files
./gui_app.exe
```

### Running from Terminal

On Windows, run from CMD or PowerShell to see output:
```bash
C:\> gui_app.exe
```

## Icon Formats and Conversion

Nuitka converts icons on-the-fly:

**Windows**:
- Input: PNG, ICO
- Output: Embedded as EXE resource

**macOS**:
- Input: PNG, ICNS
- Output: ICNS in app bundle

**Linux**:
- Input: PNG, XPM
- Output: Placed in dist folder (for desktop files)

```bash
# Cross-platform icon specification
python -m nuitka --standalone \
  --windows-icon-from-ico=icon.png \
  --macos-app-icon=icon.png \
  --linux-icon=icon.png \
  program.py
```

## Desktop Files (Linux)

Create `.desktop` file for application menu:

```ini
[Desktop Entry]
Name=My Application
Exec=/path/to/myapp.dist/myapp
Icon=/path/to/myapp.dist/icon.png
Type=Application
Categories=Utility;
```

Place in `~/.local/share/applications/` or `/usr/share/applications/`.

## Performance Tips by Platform

### Windows
- Use MinGW64 for fastest binaries (~20% faster than MSVC on pystone)
- Enable ccache automatically (downloaded by Nuitka)
- Exclude build directory from Windows Defender scanning

### macOS
- Use clang (faster than gcc)
- Install ccache via Homebrew: `brew install ccache`
- Static linking improves startup time

### Linux
- Use clang for slightly better performance
- LTO provides best optimization
- Build on target distribution for best compatibility

## Distribution Checklist

### Before Distributing

1. **Test with `--standalone` first** - easier to diagnose missing files
2. **Run compilation report** - check for failed imports
3. **Test on clean system** - verify all dependencies included
4. **Check data files** - ensure all resources accessible
5. **Verify plugins** - all required libraries have plugins enabled

### Testing Standalone Distribution

```bash
# Copy .dist folder to clean VM or container
scp -r program.dist user@clean-machine:/tmp/

# SSH and test
ssh user@clean-machine
cd /tmp/program.dist
./program  # Should run without Python installed
```

### Common Distribution Issues

| Issue | Solution |
|-------|----------|
| Missing DLLs | Enable appropriate plugin, don't copy manually |
| FileNotFoundError | Use `--include-data-files` or `__compiled__.containing_dir` |
| Import errors | Check compilation report, use `--include-module` |
| Slow startup | Test with standalone first, then try onefile |
| AV false positives | Commercial feature for signature mitigation |
