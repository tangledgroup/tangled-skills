---
name: fltk-1-4-5
description: Cross-platform C++ GUI toolkit with ~80 widget classes, OpenGL/GLUT integration, drawing primitives, image support (PNG/JPEG/SVG/GIF/BMP/ICO), printing, and FLUID visual builder. Supports X11, Wayland, Windows, macOS with HiDPI scaling. Use when building desktop GUI apps in C++, subclassing Fl_Widget for custom controls, embedding OpenGL with Fl_Gl_Window, implementing event-driven callback interfaces, or migrating from GLUT/FreeGLUT.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - fltk
  - gui
  - c++
  - desktop
  - widgets
  - opengl
category: library
external_references:
  - https://www.fltk.org/
  - https://github.com/fltk/fltk/releases/download/release-1.4.5/fltk-1.4.5-docs-html.tar.gz
  - https://github.com/fltk/fltk/tree/release-1.4.5
---

# FLTK 1.4.5

## Overview

Fast Light Toolkit (FLTK) is a cross-platform C++ GUI toolkit for UNIX/Linux (X11 and Wayland), Windows, and macOS. It provides modern GUI functionality with minimal footprint — suitable for static linking. FLTK includes ~80 widget classes, OpenGL/GLUT emulation, drawing primitives, image support (PNG, JPEG, SVG, GIF, BMP, ICO, XPM, PNM), printing to PDF/PostScript/EPS/SVG, and the FLUID visual UI builder.

Key features:
- **Small footprint**: ~1MB library, designed for static linking
- **HiDPI support**: Per-screen scale factors (1.0–2.5+), `FLTK_SCALING_FACTOR` env var
- **Wayland + X11 hybrid**: Automatic backend selection on Linux (`FLTK_BACKEND` env var)
- **Event-driven model**: `Fl::run()` main loop with callbacks, idle functions, timers
- **OpenGL integration**: `Fl_Gl_Window` for embedded OpenGL, GLUT compatibility via `<FL/glut.H>`

## When to Use

- Building desktop GUI applications in C++ across Linux, Windows, macOS
- Creating custom widgets by subclassing `Fl_Widget` or `Fl_Group`
- Embedding OpenGL rendering with `Fl_Gl_Window`
- Migrating from GLUT/FreeGLUT using `<FL/glut.H>` compatibility header
- Needing a lightweight toolkit suitable for static linking
- Building applications requiring printing (PDF, PostScript, EPS, SVG)
- Using FLUID for visual UI design

## Quick Start

Minimal "Hello World" program:

```cpp
#include <FL/Fl.H>
#include <FL/Fl_Window.H>
#include <FL/Fl_Box.H>

int main(int argc, char **argv) {
    Fl_Window *window = new Fl_Window(340, 180);
    Fl_Box *box = new Fl_Box(20, 40, 300, 100, "Hello, World!");
    box->box(FL_UP_BOX);
    box->labelfont(FL_BOLD + FL_ITALIC);
    box->labelsize(36);
    box->labeltype(FL_SHADOW_LABEL);
    window->end();
    window->show(argc, argv);
    return Fl::run();
}
```

Compile with CMake (recommended):

```cmake
cmake_minimum_required(VERSION 3.12)
project(myapp)
find_package(FLTK REQUIRED)
add_executable(myapp main.cxx)
target_link_libraries(myapp FLTK::Fltk)
```

Or directly: `g++ main.cxx -lfltk -o myapp`

## Core Concepts

**Widget hierarchy**: All widgets derive from `Fl_Widget`. Container widgets derive from `Fl_Group`. Windows derive from `Fl_Window` (which derives from `Fl_Group`). Widgets created between `group->begin()` and `group->end()` are automatically added to the group.

**Event loop**: `Fl::run()` processes events until all windows close. For custom loops, call `Fl::wait()` repeatedly. Events flow through widget `handle()` methods; return non-zero to claim an event.

**Coordinates**: Top-left origin (0,0). All positions relative to the enclosing window or group. FLTK 1.4+ uses scale-independent units (multiplied by screen scale factor for actual pixels).

**Resizing**: Set `group->resizable(widget)` on a child widget. That widget absorbs all size change; other widgets resize proportionally based on overlap with imaginary cross-lines from the resizable widget's edges.

## Advanced Topics

**Installation & Build**: CMake and autotools build, dependencies, platform-specific notes → [Installation & Build](reference/01-installation-build.md)

**Core Concepts**: Widget hierarchy, event loop, coordinates, resizing, show/hide lifecycle → [Core Concepts](reference/02-core-concepts.md)

**Widget Reference**: Buttons, inputs/outputs, valuators, browsers, groups, text widgets, tables, trees, charts → [Widget Reference](reference/03-widget-reference.md)

**Events & Callbacks**: Event types, `Fl::event_*` queries, callback signatures, shortcut handling, propagation → [Events & Callbacks](reference/04-events-and-callbacks.md)

**Drawing & Images**: Drawing primitives, colors, fonts, box types, image hierarchy (PNG/JPEG/SVG/GIF/BMP/ICO/XPM/PNM), offscreen drawing → [Drawing & Images](reference/05-drawing-and-images.md)

**OpenGL & GLUT**: `Fl_Gl_Window`, GLUT emulation via `<FL/glut.H>`, HiDPI OpenGL, context management → [OpenGL & GLUT](reference/06-opengl-and-glut.md)

**Custom Widgets**: Subclassing `Fl_Widget`/`Fl_Group`, `draw()` and `handle()` overrides, damage bits, FLUID integration → [Custom Widgets](reference/07-custom-widgets.md)

**Advanced Topics**: Multithreading (`Fl::lock/unlock/awake`), runtime options, Unicode/UTF-8, X11/Wayland backend, printing, `Fl_Preferences` → [Advanced Topics](reference/08-advanced-topics.md)

**FLUID & Migration**: FLUID UI builder, `.fl` file format, integrating generated code, FLTK 1.3 → 1.4 migration guide → [FLUID & Migration](reference/09-fluid-and-migration.md)
