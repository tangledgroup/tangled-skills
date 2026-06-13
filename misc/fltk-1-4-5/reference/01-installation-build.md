# Installation & Build

## Contents
- CMake Build (Recommended)
- Autotools Build (Deprecated)
- Dependencies
- Platform-Specific Notes
- Using FLTK in Your Project

## CMake Build (Recommended)

CMake is the recommended build system since FLTK 1.4. Autotools support is deprecated and will be removed in FLTK 1.5.

```bash
cd fltk-1.4.5
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .
sudo cmake --install .
```

Key CMake options:
- `-DFLTK_ENABLE_OPENGL=ON` — OpenGL support (default ON)
- `-DFLTK_ENABLE_CAIRO=ON` — Cairo graphics backend
- `-DFLTK_ENABLE_DOCS=ON` — Build documentation
- `-DFLTK_BUILD_TEST=ON` — Build test/demo programs
- `-DFLTK_BUILD_EXAMPLES=ON` — Build example programs
- `-DFLTK_STATIC=ON` — Build static libraries
- `-DFLTK_SHARED=ON` — Build shared libraries (default)
- `-DUSE_WAYLAND=ON` — Enable Wayland backend on Linux
- `-DUSE_X11=ON` — Enable X11 backend on Linux
- `-DFLTK_ENABLE_THREADS=ON` — Multithreading support (`Fl::lock/unlock`)

## Autotools Build (Deprecated)

```bash
cd fltk-1.4.5
./autogen.sh
./configure --enable-shared --enable-pkgconfig
make
sudo make install
```

## Dependencies

**Required**:
- C++ compiler (C++11 or later)
- X11 development libraries (`libx11-dev`, `libxext-dev`) on Linux
- pkg-config

**Optional but commonly needed**:
- **OpenGL**: `libgl1-mesa-dev` — for `Fl_Gl_Window`
- **Cairo**: `libcairo2-dev` — for `Fl_Cairo_Window` and enhanced rendering
- **PNG**: `libpng-dev` — bundled by default, system lib optional
- **JPEG**: `libjpeg-dev` — bundled by default
- **Zlib**: `zlib1g-dev` — bundled by default
- **Wayland**: `wayland-protocols`, `libwayland-dev` — for Wayland backend on Linux

**Debian/Ubuntu prerequisites**:
```bash
sudo apt install build-essential cmake libx11-dev libxext-dev libgl1-mesa-dev libpng-dev libjpeg-dev zlib1g-dev
```

## Platform-Specific Notes

### Linux (X11 + Wayland)
FLTK 1.4 builds as a Wayland/X11 hybrid by default. At runtime, the backend is auto-detected:
- Set `FLTK_BACKEND=wayland` to force Wayland
- Set `FLTK_BACKEND=x11` to force X11
- Define `FL_EXPORT bool fl_disable_wayland = true;` in source to always use X11

### Windows
- Visual Studio or MinGW supported
- CMake generates `.sln` or Makefiles respectively
- No special display server configuration needed

### macOS
- Xcode or command-line build
- Uses native macOS windowing (not X11)
- HiDPI/Retina support automatic via scale factors
- GUI scaling shortcuts: `cmd+/+/-/0` to enlarge/shrink/reset

## Using FLTK in Your Project

**CMakeLists.txt**:
```cmake
cmake_minimum_required(VERSION 3.12)
project(myapp)
find_package(FLTK REQUIRED)
add_executable(myapp main.cxx)
target_link_libraries(myapp FLTK::Fltk)
```

**Direct compilation**:
```bash
g++ main.cxx -lfltk -o myapp
```

**With OpenGL**:
```bash
g++ main.cxx -lfltk_gl -lfltk -lGL -lGLU -o myapp
```
