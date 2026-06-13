# Core Concepts

## Contents
- Widget Hierarchy
- Event Loop
- Coordinates and Units
- Resizing
- Show/Hide Lifecycle
- Labels and Alignment

## Widget Hierarchy

All FLTK widgets derive from `Fl_Widget`. The hierarchy has three main branches:

**Base**: `Fl_Widget` — base class for all widgets. Provides `x/y/w/h`, `label()`, `color()`, `box()`, `callback()`, `draw()`, `handle()`.

**Containers** (derive from `Fl_Group`):
- `Fl_Window` / `Fl_Double_Window` / `Fl_Single_Window` — top-level windows
- `Fl_Gl_Window` — OpenGL window
- `Fl_Cairo_Window` — Cairo graphics window
- `Fl_Overlay_Window` — window with overlay plane
- `Fl_Group` — generic container
- `Fl_Pack` — widgets packed in a row or column
- `Fl_Flex` — flexible row/column layout (modern alternative to Fl_Pack)
- `Fl_Tile` — tiled area where all children resize proportionally
- `Fl_Grid` — grid layout with auto-layout features
- `Fl_Scroll` — scrollable container
- `Fl_Tabs` — tabbed child widgets
- `Fl_Wizard` — wizard-style page navigation

**Controls** (derive from `Fl_Widget` or intermediate classes):
- `Fl_Button` and subclasses (`Fl_Check_Button`, `Fl_Round_Button`, `Fl_Light_Button`, `Fl_Repeat_Button`, `Fl_Return_Button`, `Fl_Toggle_Button`, `Fl_Radio_Button`)
- `Fl_Input_` and subclasses (`Fl_Input`, `Fl_Output`, `Fl_Multiline_Input`, `Fl_Multiline_Output`, `Fl_File_Input`, `Fl_Value_Input`, `Fl_Value_Output`, `Fl_Secret_Input`, `Fl_Int_Input`, `Fl_Float_Input`)
- `Fl_Valuator` and subclasses (`Fl_Slider`, `Fl_Scrollbar`, `Fl_Dial`, `Fl_Counter`, `Fl_Roller`, `Fl_Jobbar`)
- `Fl_Browser_` and subclasses (`Fl_Browser`, `Fl_File_Browser`, `Fl_Check_Browser`)
- `Fl_Menu_` and subclasses (`Fl_Choice`, `Fl_Menu_Bar`, `Fl_Sys_Menu_Bar`)
- `Fl_Text_Display`, `Fl_Text_Editor`, `Fl_Help_View`, `Fl_Terminal`
- `Fl_Table`, `Fl_Table_Row`, `Fl_Tree`, `Fl_Chart`
- `Fl_Progress`, `Fl_Timer`, `Fl_Clock`, `Fl_Positioner`
- `Fl_Spinner`, `Fl_Input_Choice`, `Fl_Color_Choice`

**Automatic grouping**: Widgets created between `group->begin()` and `group->end()` are automatically added to the group. Windows implicitly call `begin()` in their constructor.

```cpp
Fl_Window *win = new Fl_Window(400, 300);
// These are automatically added to win:
Fl_Button *btn = new Fl_Button(10, 10, 100, 30, "Click");
Fl_Input *inp = new Fl_Input(10, 50, 200, 25, "Name:");
win->end(); // No more auto-add
```

## Event Loop

**`Fl::run()`** — Main event loop. Processes events until all windows are closed. Returns when no windows remain.

**`Fl::wait(float seconds = -1)`** — Waits for events, optionally with a timeout (returns 0 on timeout). Used for custom event loops or integrating with other frameworks.

```cpp
// Custom loop with timeout
while (running) {
    if (Fl::wait(0.1) == 0) {
        // Timeout elapsed — do periodic work
    }
}
```

**Idle callbacks**: Functions called when no events are pending. Register with `Fl::add_idle(callback, data)`.

**Timer callbacks**: Functions called after a specified interval. Register with `Fl::add_timeout(seconds, callback, data)` or `Fl::repeat_timeout()` for repeating timers. Since FLTK 1.4, timers require the event loop to fire (no system timer fallback).

## Coordinates and Units

**Origin**: Top-left corner of each window is (0, 0).

**FLTK units** (since 1.4): All API quantities are in scale-independent FLTK units. Internally multiplied by `Fl::screen_scale(n)` to get drawing units (pixels). Default scale is 1.0 on standard displays, ~2.0 on HiDPI/Retina.

- Set `FLTK_SCALING_FACTOR` environment variable to override auto-detection
- Runtime zoom: `ctrl+/+/-/0` (X11/Windows/Wayland), `cmd+/+/-/0` (macOS)
- `Fl::screen_scale(screen_num)` — get current scale factor
- `Fl::screen_w()/Fl::screen_h()` — screen dimensions in FLTK units

**Relative positioning**: Widget coordinates are relative to the enclosing window or group, not the screen. Sub-windows have their own coordinate space.

## Resizing

Set `group->resizable(widget)` to define resizing behavior:

- **`resizable(nullptr)`** — No resizing (default for `Fl_Window`, `Fl_Pack`)
- **`resizable(group)`** — All children resize proportionally (default for `Fl_Group`)
- **`resizable(child)`** — Complex resizing. The child absorbs all size change. Other widgets resize based on overlap with imaginary cross-lines from the resizable widget's edges:
  - Widgets overlapping the vertical bars → width changes proportionally
  - Widgets overlapping the horizontal bars → height changes proportionally
  - Widgets not overlapping → size stays fixed

For complex layouts, nest groups with independent `resizable()` settings. Put fixed-size widgets in their own group with `resizable(invisible_box)` to absorb size changes.

## Show/Hide Lifecycle

- **`widget->show()`** — Shows the widget (and its parent window if not already shown)
- **`window->show(argc, argv)`** — Shows window and processes command-line arguments (`-fx`, `-f`, `-bg`, `-fg`, etc.)
- **`widget->hide()`** — Hides the widget
- **`widget->visible(0/1)`** — Programmatic show/hide without events
- **`Fl::first_window()` / `Fl::next_window()`** — Iterate over all windows

Widgets receive `FL_SHOW` and `FL_HIDE` events when shown/hidden. Override `handle()` to respond.

## Labels and Alignment

All widgets support labels via `label(const char*)`. Key methods:
- **`labelfont(Fl_Font)`** — Font family + style (`FL_HELVETICA`, `FL_BOLD`, `FL_ITALIC`, `FL_SYMBOL`)
- **`labelsize(int)`** — Font size in FLTK units
- **`labelcolor(Fl_Color)`** — Text color
- **`labeltype(Fl_Labeltype)`** — Rendering style (`FL_NORMAL_LABEL`, `FL_ENGRAVED_LABEL`, `FL_SHADOW_LABEL`, `FL_BOLD_LABEL`)
- **`align(Fl_Align)`** — Label position (`FL_ALIGN_CENTER`, `FL_ALIGN_LEFT`, `FL_ALIGN_TOP`, etc.)
- **`tooltip(const char*)`** — Hover tooltip text

Labels use static storage — the string pointer is stored, not copied. Use string literals or ensure lifetime.
