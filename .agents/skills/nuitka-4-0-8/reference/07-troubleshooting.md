# Nuitka Troubleshooting Guide

Comprehensive solutions for common issues, debugging techniques, and error resolution strategies.

## Common Error Patterns

### ModuleNotFoundError at Runtime

**Symptom**: Program runs fine with Python but fails after compilation with `ModuleNotFoundError`

**Causes**:
1. Missing plugin for third-party library
2. Dynamic import not detected
3. Conditional import not included

**Solutions**:

```bash
# 1. Enable required plugins
python -m nuitka --standalone --enable-plugin=numpy program.py

# 2. Include dynamically imported modules
python -m nuitka --standalone --include-module=dynamically_loaded program.py

# 3. Check compilation report for failed imports
python -m nuitka --standalone --report=compilation-report.xml program.py
grep "not found" compilation-report.xml

# 4. Use --follow-imports for recursive compilation
python -m nuitka --standalone --follow-imports program.py
```

**Debugging**: Add print statements to trace imports:

```python
import sys

original_import = __import__

def traced_import(name, *args, **kwargs):
    print(f"IMPORT: {name}", file=sys.stderr)
    return original_import(name, *args, **kwargs)

__import__ = traced_import
```

### FileNotFoundError for Data Files

**Symptom**: Program can't find data files in standalone/onefile mode

**Wrong Approach**:
```python
# Don't use relative paths from cwd
with open("data/config.ini") as f:  # Fails in standalone!
    config = f.read()
```

**Correct Approaches**:

1. **Use `__file__` for files near source**:
```python
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.ini")
with open(config_path) as f:
    config = f.read()
```

2. **Use `__compiled__.containing_dir` for standalone**:
```python
import os

try:
    # Works in both standalone and onefile
    base_dir = __compiled__.containing_dir
except NameError:
    # Fallback for uncompiled execution
    base_dir = os.path.dirname(sys.argv[0])

config_path = os.path.join(base_dir, "config.ini")
```

3. **Include data files properly**:
```bash
python -m nuitka --standalone \
  --include-data-files=config.ini=config.ini \
  program.py
```

### Fork Bombs with Multiprocessing

**Symptom**: Program spawns exponential processes and freezes system

**Cause**: Packages like `multiprocessing`, `joblib`, `loky` re-execute via `sys.executable`, which now points to compiled binary

**Solutions**:

1. **Use multiprocessing plugin**:
```bash
python -m nuitka --standalone --enable-plugin=multiprocessing program.py
```

2. **Disable self-execution protection** (if your app handles sys.argv):
```bash
python -m nuitka --no-deployment-flag=self-execution program.py
```

3. **Add fork bomb protection in code**:
```python
import os, sys

if "NUITKA_LAUNCH_TOKEN" not in os.environ:
    sys.exit("Error: Fork bomb suspected. Need launch token.")
else:
    del os.environ["NUITKA_LAUNCH_TOKEN"]

# Rest of program...
```

4. **Debug forking behavior**:
```bash
python -m nuitka --debug-self-forking program.py
```

### Missing DLLs on Windows

**Symptom**: "The code execution cannot proceed because X.dll was not found"

**Causes**:
1. Missing plugin for library that ships DLLs
2. System DLL not present on target machine
3. Manual DLL copying (doesn't work reliably)

**Solutions**:

1. **Enable appropriate plugins**:
```bash
# NumPy and scientific stack
python -m nuitka --standalone --enable-plugin=numpy program.py

# ZeroMQ
python -m nuitka --standalone --enable-plugin=pyzmq program.py

# GTK/GI libraries
python -m nuitka --standalone --enable-plugin=gi program.py
```

2. **Install Visual C++ Redistributable** on target:
   - Python 3.11-3.14: VC++ 2022 redistributable
   - Python 3.5-3.10: VC++ 2019 redistributable
   - Download from Microsoft website

3. **Check compilation report** for missing dependencies:
```bash
python -m nuitka --standalone --report=compilation-report.xml program.py
grep -i "dll\|dependency" compilation-report.xml
```

**Don't**: Manually copy DLLs to `.dist` folder - this rarely works correctly.

## Memory-Related Issues

### Compiler Out of Memory

**Symptoms**:
```
fatal error: error writing to -: Invalid argument
Killed signal terminated program
fatal error C1002: compiler is out of heap space in pass 2
fatal error C1001: Internal compiler error
```

**Solutions**:

1. **Enable low-memory mode**:
```bash
python -m nuitka --low-memory program.py
```

2. **Reduce parallel jobs**:
```bash
# Use single-threaded compilation
python -m nuitka --jobs=1 program.py

# Or reduce job count
python -m nuitka --jobs=2 program.py
```

3. **Disable LTO** (uses less memory):
```bash
python -m nuitka --lto=no program.py
```

4. **Use 64-bit compiler**: Don't use 32-bit Python/compilers on Windows

5. **Add swap space** (Linux):
```bash
# Create 8GB swap file
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

6. **Demote large packages**:
```bash
python -m nuitka --demote=pandas,tensorflow program.py
```

7. **Use minimal virtualenv**: Remove unnecessary packages before compiling

### Combined Low-Memory Approach

```bash
# Maximum memory reduction
python -m nuitka \
  --low-memory \
  --jobs=1 \
  --lto=no \
  --demote=pandas,numpy,scipy \
  program.py
```

**Trade-off**: Much slower compilation but uses ~90% less memory.

## Platform-Specific Issues

### Windows: Virus Scanner False Positives

**Symptom**: Windows Defender or third-party AV flags compiled binary as malware

**Causes**: Nuitka binaries can trigger heuristic detections (common with Python compilers)

**Solutions**:

1. **Add exclusion** for build directory:
   - Windows Security → Virus & threat protection → Exclusions
   - Add your project folder

2. **Sign your binaries** (commercial feature available)

3. **Submit to Microsoft** for analysis if false positive

4. **Exclude from real-time scanning** during development

**Note**: Commercial Nuitka has better AV signature mitigation.

### Windows: MinGW64 vs MSVC

**Issue**: MinGW64 doesn't work with Python 3.13+ on Windows

**Solution**: Use MSVC for Python 3.13+:
```bash
python -m nuitka --msvc=2022 program.py
```

**For older Pythons**: MinGW64 recommended (faster binaries):
```bash
python -m nuitka --mingw64 program.py
```

### macOS: pyenv Incompatibility

**Issue**: Nuitka doesn't work with pyenv-installed Python on macOS

**Solution**: Use Homebrew Python:
```bash
# Install Homebrew Python
brew install python@3.11

# Use it for Nuitka
/opt/homebrew/bin/python3.11 -m nuitka program.py
```

### macOS: App Bundle Won't Launch

**Symptom**: Double-clicking `.app` does nothing or shows error

**Solutions**:

1. **Check console log** for errors:
```bash
# Run from terminal to see errors
./MyApp.app/Contents/MacOS/MyApp
```

2. **Ensure correct plugin enabled**:
```bash
# For Tkinter apps
python -m nuitka --enable-plugin=tk-inter --onefile=app program.py

# For PyQt5 apps
python -m nuitka --enable-plugin=pyqt5 --include-qt-plugins=sensible --onefile=app program.py
```

3. **Code sign the app** (may be required on newer macOS):
```bash
codesign --deep --force --sign - MyApp.app
```

### Linux: glibc Version Too New

**Symptom**: Binary works on build machine but not on older Linux:
```
./program: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.34' not found
```

**Cause**: Built on newer distro with newer glibc than target

**Solutions**:

1. **Build on oldest target OS**: Use Docker container with target distro:
```bash
docker run -v $(pwd):/work centos:7 /bin/bash
# Inside container: install Python, Nuitka, compile
```

2. **Use static linking** (if available):
```bash
python -m nuitka --static-libpython=yes --standalone program.py
```

3. **Use commercial container builds**: Nuitka Commercial provides optimized build containers

### Linux: Missing Shared Libraries

**Symptom**: `error while loading shared libraries: libX.so.X: cannot open shared object file`

**Solutions**:

1. **Include required libraries**:
```bash
python -m nuitka --standalone \
  --include-dll-by-name=libssl.so.1.1,libcrypto.so.1.1 \
  program.py
```

2. **Use appropriate plugins**:
```bash
python -m nuitka --standalone --enable-plugin=numpy program.py
```

3. **Check with ldd**:
```bash
ldd program.dist/program
# Look for "not found" entries
```

## Compilation Errors

### SyntaxError During Compilation

**Symptom**: `SyntaxError` even though code runs fine with Python

**Cause**: Using wrong Python interpreter for compilation

**Solution**: Use explicit Python:
```bash
# Wrong (might use Python 2)
nuitka program.py

# Right (explicitly use Python 3.11)
python3.11 -m nuitka program.py
```

**Verify**: Check Nuitka version output:
```bash
python -m nuitka --version
# Should show correct Python version
```

### C Compiler Errors

**Symptom**: C compilation fails with various errors

**Common Causes and Solutions**:

1. **Missing C compiler**:
```bash
# Linux
sudo apt install build-essential  # Debian/Ubuntu
sudo dnf install gcc gcc-c++     # Fedora/RHEL

# macOS
xcode-select --install

# Windows
# Let Nuitka auto-download MinGW64, or install Visual Studio
```

2. **C compiler too old**:
```bash
# Check gcc version
gcc --version
# Need gcc 5.1+ or clang

# Update if necessary
```

3. **Path too long** (Windows):
   - Move project to shorter path (e.g., `C:\build\`)
   - Use short filenames

4. **Invalid characters in path**:
   - Avoid spaces, unicode, special characters
   - Use simple paths like `/home/user/project` or `C:\project`

### Import Errors During Compilation

**Symptom**: Module imports fail during compilation but work at runtime

**Causes**:
1. Module not installed in compilation environment
2. PYTHONPATH not set during compilation
3. Editable install (not supported)

**Solutions**:

1. **Install all dependencies**:
```bash
pip install -r requirements.txt
python -m nuitka program.py
```

2. **Set PYTHONPATH**:
```bash
export PYTHONPATH=/path/to/modules:$PYTHONPATH
python -m nuitka program.py
```

3. **Use regular install** (not editable):
```bash
# Wrong
pip install -e ./my_package

# Right
pip install ./my_package
```

## Runtime Issues

### Program Runs Slowly

**Diagnosis**:

1. **Check if actually compiled**:
```python
print(hasattr(__compiled__, '__name__'))  # Should be True
```

2. **Profile the application**:
```bash
# Compile with profiling
python -m nuitka --profile program.py

# Run and generate profile
./program.bin

# Analyze profile output
```

**Optimization Strategies**:

1. **Compile more modules**:
```bash
python -m nuitka --follow-imports program.py
```

2. **Enable LTO**:
```bash
python -m nuitka --lto=yes program.py
```

3. **Use PGO** (Profile-Guided Optimization):
```bash
# Pass 1
python -m nuitka --pgo-c program.py
./program.bin  # Run typical workload

# Pass 2
python -m nuitka --pgo-c=yes program.py
```

4. **Demote I/O-bound modules**:
```bash
python -m nuitka --demote=requests,urllib3 program.py
```

### GUI Application Shows No Output/Errors

**Symptom**: GUI app compiles but doesn't show errors when it crashes

**Solutions**:

1. **Windows: Force console**:
```bash
python -m nuitka --console=force gui_app.py
```

2. **Redirect output to files**:
```bash
python -m nuitka --onefile \
  --force-stdout-spec=stdout.txt \
  --force-stderr-spec=stderr.txt \
  gui_app.py
```

3. **Run from terminal**:
```bash
# Windows: Open CMD/PowerShell and run exe
./gui_app.exe

# Linux/macOS: Run from terminal
./gui_app.bin
```

4. **Add error logging in code**:
```python
import sys
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

try:
    main()
except Exception as e:
    logging.exception("Fatal error")
    raise
```

### Onefile Temp Directory Issues

**Symptom**: Onefile unpacking fails or temp directory problems

**Solutions**:

1. **Specify temp directory**:
```bash
python -m nuitka --onefile \
  --onefile-tempdir-spec=C:/Temp/MyApp-* \
  program.py
```

2. **Keep temp directory for debugging**:
```bash
python -m nuitka --onefile --onefile-keep-tempdir program.py
```

3. **Check temp directory permissions**: Ensure write access to temp location

4. **Disable compression** (if unpacking fails):
```bash
python -m nuitka --onefile --onefile-compression=no program.py
```

## Debugging Techniques

### Enable Verbose Output

```bash
# Show all compilation steps
python -m nuitka --verbose program.py

# Show module inclusion decisions
python -m nuitka --show-modules program.py

# Explain import behavior
python -m nuitka --explain-imports program.py

# Show memory usage
python -m nuitka --show-memory program.py

# Show progress
python -m nuitka --show-progress program.py
```

### Generate Compilation Report

```bash
# Create detailed XML report
python -m nuitka --standalone \
  --report=compilation-report.xml \
  program.py

# Search for issues
grep -i "error\|warning\|not found" compilation-report.xml

# View as HTML (if you have transformer)
xsltproc report.xsl compilation-report.xml > report.html
```

### Debug Mode Compilation

```bash
# Compile with debug information
python -m nuitka --debug program.py

# Run in debugger
python -m nuitka --debugger program.py
```

### Test Incrementally

```bash
# 1. Test acceleration mode first
python -m nuitka program.py
./program.bin

# 2. Then standalone
python -m nuitka --standalone program.py
./program.dist/program

# 3. Finally onefile
python -m nuitka --onefile program.py
./program.bin
```

## Getting Help

### Report Bugs Effectively

1. **Include Nuitka version**:
```bash
python -m nuitka --version
# Copy entire output
```

2. **Create minimal reproducible example**: Smallest code that demonstrates issue

3. **Provide compilation report**: `--report=compilation-report.xml`

4. **Describe expected vs actual behavior** clearly

5. **Test with latest Nuitka version**: Issue may be fixed

### Useful Information to Collect

```bash
# System information
python -m nuitka --version

# Plugin list
python -m nuitka --plugin-list

# Compilation with verbose output
python -m nuitka --verbose --report=report.xml program.py 2>&1 | tee compile.log
```

## Prevention Best Practices

### 1. Always Test with Standalone First

```bash
# Verify all dependencies work
python -m nuitka --standalone program.py
./program.dist/program  # Test thoroughly

# Then create onefile if needed
python -m nuitka --onefile program.py
```

### 2. Use Version Control for Compiled Projects

```bash
# Add dist folders to .gitignore
echo "*.dist/" >> .gitignore
echo "*.bin" >> .gitignore
echo "compilation-report.xml" >> .gitignore
```

### 3. Document Build Commands

```bash
# Create build script
cat > build.sh << 'EOF'
#!/bin/bash
python -m nuitka --standalone \
  --enable-plugin=numpy \
  --include-data-files=config.ini=config.ini \
  --report=compilation-report.xml \
  program.py
EOF

chmod +x build.sh
```

### 4. Use Virtual Environments for Compilation

```bash
# Create clean environment
python -m venv build_env
source build_env/bin/activate  # Linux/macOS
# build_env\Scripts\activate  # Windows

# Install exact dependencies
pip install -r requirements.txt
pip install Nuitka

# Compile
python -m nuitka --standalone program.py
```

### 5. Regular Updates

```bash
# Check for Nuitka updates
pip show nuitka
pip install --upgrade Nuitka
```
