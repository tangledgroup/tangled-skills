# Nuitka Plugin System

Comprehensive guide to Nuitka's plugin architecture, standard plugins for third-party libraries, and creating custom user plugins.

## Plugin Overview

### What Are Plugins?

Plugins modify how Nuitka compiles Python programs:
- Automatically include data files and shared libraries
- Import modules not detectable by static analysis
- Modify or extend source code during compilation
- Gather statistics and change parameter defaults
- Handle package-specific requirements

### Plugin Types

| Type | Location | Activation |
|------|----------|------------|
| **Mandatory Standard** | `nuitka/plugins/standard/` | Always enabled, invisible |
| **Optional Standard** | `nuitka/plugins/standard/` | `--enable-plugin=name` |
| **User Plugins** | Custom location | `--user-plugin=path/to/script.py` |

### Plugin Activation Order

1. User plugins (loaded first)
2. Mandatory standard plugins
3. Optional standard plugins (if enabled)

**Important**: User plugins can enable optional standard plugins, but not vice versa.

## Listing Available Plugins

```bash
# List all optional standard plugins
python -m nuitka --plugin-list

# Example output:
# anti-bloat            Patch stupid imports out of widely used library modules
# data-files            Include data files
# numpy                 Required for numpy, scipy, pandas, matplotlib
# pyqt5                 Required by the PyQt5 package
# ...
```

## Standard Plugins Reference

### Scientific Computing

#### NumPy Plugin

**Required for**: numpy, scipy, pandas, matplotlib, and many scientific packages

```bash
python -m nuitka --standalone --enable-plugin=numpy program.py
```

**What it does**:
- Includes NumPy runtime files
- Handles NumPy's dynamic import patterns
- Copies required DLLs/shared libraries
- Enables ufunc compilation optimizations

**Common issues**:
- Forgetting plugin causes "module not found" errors at runtime
- Works with scipy, pandas, matplotlib automatically (they depend on numpy)

#### SciPy Plugin

Usually handled by numpy plugin, but can be explicit:

```bash
python -m nuitka --standalone --enable-plugin=numpy program.py
# SciPy support included automatically
```

### GUI Frameworks

#### PyQt5 Plugin

**Required for**: PyQt5 applications

```bash
# Basic PyQt5 support
python -m nuitka --standalone --enable-plugin=pyqt5 gui_app.py

# Include Qt plugins (sensible default set)
python -m nuitka --standalone --enable-plugin=pyqt5 \
  --include-qt-plugins=sensible gui_app.py

# Include all Qt plugins (large, but complete)
python -m nuitka --standalone --enable-plugin=pyqt5 \
  --include-qt-plugins=all gui_app.py

# Selective Qt plugins
python -m nuitka --standalone --enable-plugin=pyqt5 \
  --include-qt-plugins=platforms,styles,imageformats gui_app.py
```

**Qt plugin categories**:
- `platforms` - Required for display (qt.qpa.platform)
- `styles` - Visual styles (qt.style)
- `imageformats` - Image loading (JPEG, PNG, etc.)
- `sql` - Database drivers
- `printsupport` - Printing support
- `qml` - Qt Quick/QML support

**Important**: Without proper Qt plugins, GUI may crash or have inferior appearance.

#### PySide6 Plugin

**Required for**: PySide6 (Qt for Python) applications

```bash
python -m nuitka --standalone --enable-plugin=pyside6 \
  --include-qt-plugins=sensible app.py
```

Same `--include-qt-plugins` options as PyQt5.

#### PySide2 Plugin

**Required for**: PySide2 (Qt5 for Python) applications

```bash
python -m nuitka --standalone --enable-plugin=pyside2 \
  --include-qt-plugins=sensible app.py
```

#### Tkinter Plugin

**Required for**: Python's tkinter module

```bash
python -m nuitka --standalone --enable-plugin=tk-inter program.py

# Custom Tcl/Tk directories (rarely needed)
python -m nuitka --standalone --enable-plugin=tk-inter \
  --tk-library-dir=/usr/lib/tcl8.6 \
  --tcl-library-dir=/usr/lib/tk8.6 \
  program.py
```

**What it does**:
- Automatically detects Tcl and Tk installation
- Copies required shared libraries to `.dist` folder
- Handles platform-specific library names

### Networking and Async

#### ZeroMQ Plugin

**Required for**: pyzmq (ZeroMQ bindings)

```bash
python -m nuitka --standalone --enable-plugin=pyzmq zmq_app.py
```

**What it does**:
- Includes ZeroMQ shared libraries
- Handles platform-specific library locations

#### Eventlet Plugin

**Required for**: eventlet package

```bash
python -m nuitka --standalone --enable-plugin=eventlet app.py
```

**What it does**:
- Includes eventlet dependencies
- Handles DNS package monkey patching requirements

#### Gevent Plugin

**Required for**: gevent package

```bash
python -m nuitka --standalone --enable-plugin=gevent app.py
```

### Machine Learning

#### TensorFlow Plugin

**Required for**: tensorflow package

```bash
python -m nuitka --standalone --enable-plugin=tensorflow \
  --enable-plugin=numpy  # Also need numpy!
  model.py
```

**Important**: Must enable both `tensorflow` AND `numpy` plugins.

#### PyTorch Plugin

**Required for**: torch, torchvision packages

```bash
python -m nuitka --standalone --enable-plugin=torch \
  --enable-plugin=numpy  # Also need numpy!
  model.py
```

### GIS and Graphics

#### GI Plugin (GObject Introspection)

**Required for**: GTK, GdkPixbuf, and GI-based libraries

```bash
python -m nuitka --standalone --enable-plugin=gi gtk_app.py
```

**What it does**:
- Handles GI dependency discovery
- Includes required shared libraries

#### GLFW Plugin

**Required for**: glfw (OpenGL windowing)

```bash
python -m nuitka --standalone --enable-plugin=glfw opengl_app.py
```

### Compatibility Plugins

#### Dill Compatibility

**Required for**: dill module (extended pickle)

```bash
python -m nuitka --standalone --enable-plugin=dill-compat program.py
```

#### Enum Compatibility

**Required for**: Older enum usage patterns

```bash
python -m nuitka --standalone --enable-plugin=enum-compat program.py
```

#### PBR Compatibility

**Required for**: packages using pbr (Python Build Reed)

```bash
python -m nuitka --standalone --enable-plugin=pbr-compat program.py
```

### Utility Plugins

#### Anti-Bloat Plugin

**Purpose**: Remove unnecessary imports from widely used libraries

```bash
# Enable anti-bloat
python -m nuitka --standalone --enable-plugin=anti-bloat program.py

# Block pytest imports (common in scientific packages)
python -m nuitka --standalone \
  --noinclude-pytest-mode=nofollow \
  program.py

# Block setuptools
python -m nuitka --standalone \
  --noinclude-setuptools-mode=nofollow \
  program.py

# Custom module blocking
python -m nuitka --standalone \
  --noinclude-custom-mode=setuptools:error \
  program.py
```

**Benefits**:
- Reduces compilation time
- Smaller output size
- Faster startup (fewer imports)

#### Data Files Plugin

**Purpose**: Include data files in standalone distributions

```bash
# Using plugin option
python -m nuitka --standalone \
  --enable-plugin=data-files \
  --data-files-config=files.yml \
  program.py

# Or use direct options (preferred)
python -m nuitka --standalone \
  --include-data-files=config.ini=config.ini \
  --include-data-dir=assets=assets \
  program.py
```

#### Implicit Imports Plugin

**Purpose**: Handle implicit import patterns

```bash
python -m nuitka --standalone --enable-plugin=implicit-imports program.py
```

#### Multiprocessing Plugin

**Required for**: Python's multiprocessing module in standalone mode

```bash
python -m nuitka --standalone --enable-plugin=multiprocessing program.py
```

**What it does**:
- Handles `sys.executable` re-execution patterns
- Prevents fork bombs from self-launching
- Configures proper child process spawning

#### Pkg-Resources Plugin

**Purpose**: Resolve version numbers at compile time

```bash
python -m nuitka --standalone --enable-plugin=pkg-resources program.py
```

Helps with `pkg_resources` and `importlib.metadata` version queries.

#### PyLint Warnings Plugin

**Purpose**: Support PyLint/PyDev linting markers

```bash
python -m nuitka --standalone --enable-plugin=pylint-warnings program.py
```

Recognizes `# pylint: disable=` and similar comments.

## Plugin Options

### Specifying Plugin Options

```bash
# Enable plugin with options
python -m nuitka --enable-plugin=plugin_name=option1,option2 program.py

# Example with PyQt5
python -m nuitka --enable-plugin=pyqt5 \
  --include-qt-plugins=qml,platforms gui_app.py
```

### Getting Plugin Option Help

```bash
python -m nuitka --help | grep -A 5 "plugin"
```

## User Plugins

### Creating a Simple User Plugin

Create `my_plugin.py`:

```python
import os
from nuitka.plugins.PluginBase import NuitkaPluginBase

class NuitkaPluginMine(NuitkaPluginBase):
    plugin_name = __name__.split(".")[-1]
    
    def onModuleSourceCode(self, module_name, source_filename, source_code):
        # Process source code before compilation
        if module_name == "__main__":
            self.info(f"Processing main module: {source_filename}")
        
        # Return modified (or original) source code
        return source_code
```

Use it:
```bash
python -m nuitka --user-plugin=my_plugin.py program.py
```

### User Plugin with Options

```python
from nuitka.plugins.PluginBase import NuitkaPluginBase

class NuitkaPluginWithOptions(NuitkaPluginBase):
    plugin_name = __name__.split(".")[-1]
    
    def __init__(self, trace_imports, include_pattern):
        self.trace_imports = trace_imports
        self.include_pattern = include_pattern
        self.info(f"Plugin initialized: trace={trace_imports}, pattern={include_pattern}")
    
    @classmethod
    def addPluginCommandLineOptions(cls, group):
        group.add_option(
            "--trace-my-plugin",
            action="store_true",
            dest="trace_imports",
            default=False,
            help="Trace all imports"
        )
        group.add_option(
            "--include-pattern=",
            dest="include_pattern",
            default=None,
            help="Pattern for modules to include"
        )
    
    def onModuleSourceCode(self, module_name, source_filename, source_code):
        if self.trace_imports:
            self.info(f"Import: {module_name}")
        
        # Check pattern
        if self.include_pattern and self.include_pattern in module_name:
            self.info(f"Matched pattern: {module_name}")
        
        return source_code
```

Use with options:
```bash
python -m nuitka --user-plugin=my_plugin.py=trace_imports,include_pattern program.py
```

### Plugin Hook Methods

Available hook methods in `NuitkaPluginBase`:

| Method | Purpose |
|--------|---------|
| `onModuleSourceCode()` | Process source code before compilation |
| `onAfterModuleCompiled()` | After module is compiled to C |
| `onFork()` | When Nuitka forks for compilation |
| `onPluginEarlyInit()` | Early initialization |
| `onPluginInit()` | Normal initialization |
| `onCreateCachedFiles()` | Create additional cached files |

### Accessing Nuitka Options in Plugins

```python
from nuitka import Options

class MyPlugin(NuitkaPluginBase):
    def onPluginInit(self):
        # Check compilation mode
        if Options.isStandaloneMode():
            self.info("Running in standalone mode")
        
        # Get enabled plugins
        plugins = Options.getPluginsEnabled()
        
        # Get include modules
        includes = Options.getMustIncludeModules()
        
        # Check flags
        if Options.isLto():
            self.info("LTO is enabled")
```

See [UserPlugin-Creation.rst](https://github.com/Nuitka/Nuitka/blob/4.0.8/UserPlugin-Creation.rst) for complete API reference.

## Plugin Interdependencies

### Common Plugin Combinations

#### Scientific Stack

```bash
python -m nuitka --standalone \
  --enable-plugin=numpy \
  --enable-plugin=pkg-resources \
  scientific_app.py
```

#### PyQt5 with SQLite

```bash
python -m nuitka --standalone \
  --enable-plugin=pyqt5 \
  --include-qt-plugins=sensible \
  --include-module=sqlite3 \
  gui_app.py
```

#### TensorFlow Complete

```bash
python -m nuitka --standalone \
  --enable-plugin=tensorflow \
  --enable-plugin=numpy \
  --enable-plugin=pkg-resources \
  model.py
```

### Plugin Conflict Resolution

**PyQt5 vs PySide**: Only one Qt binding plugin at a time:

```bash
# Wrong - don't enable both
python -m nuitka --enable-plugin=pyqt5 --enable-plugin=pyside6 app.py

# Right - choose one
python -m nuitka --enable-plugin=pyqt5 app.py
```

## Debugging Plugin Issues

### Verbose Plugin Output

```bash
# Show plugin loading
python -m nuitka --verbose --enable-plugin=numpy program.py

# Show module inclusion decisions
python -m nuitka --show-modules --enable-plugin=numpy program.py
```

### Check Plugin Detection

Nuitka warns if it detects missing plugins:

```
Nuitka:WARNING: You seem to be using numpy, but did not enable the plugin.
Nuitka:WARNING: Use --enable-plugin=numpy to fix this.
```

**Action**: Always heed these warnings for standalone mode.

### Disable Plugin Detection

```bash
# Suppress plugin detection warnings
python -m nuitka --plugin-no-detection program.py
```

Use only when you know plugins are not needed.

## Commercial Plugins

These plugins require Nuitka Commercial license:

| Plugin | Purpose |
|--------|---------|
| `data-hiding` | Hide constant Python data from inspection |
| `datafile-inclusion-ng` | Load trusted file contents at compile time |
| `ethereum` | Ethereum package support |
| `traceback-encryption` | Encrypt tracebacks (de-Jong-Stacks) |
| `windows-service` | Create Windows Service files |

See https://nuitka.net/doc/commercial.html for details.

## Best Practices

### 1. Always Use Plugins for Third-Party Libraries

```bash
# Wrong
python -m nuitka --standalone program_using_numpy.py

# Right
python -m nuitka --standalone --enable-plugin=numpy program_using_numpy.py
```

### 2. Test with Standalone Before Onefile

```bash
# First verify all dependencies work
python -m nuitka --standalone --enable-plugin=numpy program.py
./program.dist/program  # Test this works

# Then create onefile
python -m nuitka --onefile --enable-plugin=numpy program.py
```

### 3. Document Required Plugins

In your project README:

```markdown
## Compilation

Requires Nuitka with numpy plugin:

```bash
python -m nuitka --standalone --enable-plugin=numpy app.py
```
```

### 4. Use Anti-Bloat for Large Dependencies

```bash
python -m nuitka --standalone \
  --enable-plugin=anti-bloat \
  --noinclude-pytest-mode=nofollow \
  --noinclude-setuptools-mode=nofollow \
  large_app.py
```
