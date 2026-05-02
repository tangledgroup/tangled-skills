# Advanced Topics

## Contents
- Multithreading
- Runtime Options
- Unicode and UTF-8
- Platform-Specific Interfaces
- Printing and Surface Devices
- Preferences

## Multithreading

FLTK supports multithreaded applications with a locking mechanism. Must be compiled with `--enable-threads` (default since 1.3) or `-DFLTK_ENABLE_THREADS=ON` (CMake).

**Rules**:
- Only the main thread may create/destroy windows and draw to the display
- Worker threads must use `Fl::lock()` / `Fl::unlock()` when accessing FLTK widgets
- Hold the lock for the shortest time possible to avoid blocking the UI

**Basic pattern**:
```cpp
int main(int argc, char **argv) {
    // Create windows and widgets
    Fl::lock();  // Enable multithreading support (call once before showing windows)
    main_win->show(argc, argv);
    // Start worker threads
    int result = Fl::run();
    return result;
}

void worker_thread() {
    while (running) {
        // Do computation...
        Fl::lock();
        my_widget->value(new_value);
        my_widget->redraw();
        Fl::unlock();
        Fl::awake();  // Wake up the main thread to process redraw
    }
}
```

**Thread messages**: Send data from worker to main thread:
```cpp
// Worker thread
void *msg = compute_result();
Fl::awake(msg);

// Main thread (using Fl::wait loop)
while (Fl::wait() > 0) {
    void *msg = Fl::thread_message();
    if (msg) process_message(msg);
}
```

**Callback messages**: Execute a function in the main thread:
```cpp
typedef void (*Fl_Awake_Handler)(void *);
Fl::awake((Fl_Awake_Handler)my_function, userdata);
```

**Lockless programming**: For high-performance apps, avoid `Fl::lock()` by using lock-free data structures and only locking for final UI updates. See FLTK docs for detailed strategies.

## Runtime Options

FLTK maintains user interface settings in a system-wide database. Users can override defaults.

**Query options**:
```cpp
bool val = Fl::option(Fl::OPTION_VISIBLE_FOCUS);  // Get current setting
Fl::option(Fl::OPTION_VISIBLE_FOCUS, false);       // Temporarily override
```

**Common options**:
- `OPTION_VISIBLE_FOCUS` — Show dotted rectangle around focused widget
- `OPTION_SHOW_TOOL_TIPS` — Enable tooltip display
- `OPTION_USE_SYSTEM_TITLEBAR` — Use OS-native title bars
- `OPTION_NATIVE_FILE_CHOOSER` — Use OS-native file dialogs

**Administrative tool**: `fltk-options` — GUI tool to view and change system/user options. Run without arguments for interactive mode, or with `-S` (system) / `-U` (user) flags.

Options stored via `Fl_Preferences` with signature `"fltk.org", "fltk"` under `CORE_SYSTEM` (system-wide) or `CORE_USER` (per-user).

## Unicode and UTF-8

FLTK uses UTF-8 internally since version 1.3. All label strings, input text, and file paths should be valid UTF-8.

**Key points**:
- Full Unicode range supported (21 bits), except binary shortcuts (`Fl_Shortcut`) limited to BMP (16 bits)
- `Fl::compose()` — translate individual keystrokes into composed characters (for accented input)
- Text widgets handle multi-byte UTF-8 sequences correctly
- Font selection: system fonts that support the required Unicode range

**Character iteration**: Use `fl_utf8` functions for safe UTF-8 string handling. Do not assume 1 byte = 1 character.

## Platform-Specific Interfaces

Include `<FL/platform.H>` (replaces deprecated `<FL/x.H>` from FLTK 1.3).

**Wayland/X11 hybrid** (Linux):
- Auto-detected at `fl_open_display()` time
- `FLTK_BACKEND=wayland` or `FLTK_BACKEND=x11` to force
- `FL_EXPORT bool fl_disable_wayland = true;` in source to always use X11
- After display opens, exactly one of `fl_wl_display()` or `fl_x11_display()` is non-NULL

**X11 access**:
```cpp
#if defined(FLTK_USE_X11)
#include <FL/platform.H>
Display *disp = fl_x11_display();
Window win_id = fl_x11_xid(my_window);
Fl_Window *found = fl_x11_find(win_id);
#endif
```

**Global X event handler**:
```cpp
static int my_handler(int event) {
    // fl_xevent contains the raw XEvent
    return 0;  // Return non-zero to claim
}
Fl::add_handler(my_handler);
```

**Windows/macOS**: Platform-specific headers define appropriate interfaces. Use `#if defined(FLTK_USE_WIN32)` or `#if defined(FLTK_USE_APPLE_EVENTS)`.

## Printing and Surface Devices

FLTK supports printing to multiple output formats via the surface device system.

**Surface device hierarchy**:
- `Fl_Surface_Device` — base class
- `Fl_Display_Device` — screen display (default)
- `Fl_Widget_Surface` — capture widget to image
- `Fl_Copy_Surface` — copy drawing operations
- `Fl_Image_Surface` — render to `Fl_RGB_Image`
- `Fl_Paged_Device` — base for paged output
  - `Fl_Printer` — send to system printer
  - `Fl_PDF_File_Surface` — write PDF file
  - `Fl_PostScript_File_Device` — write PostScript
  - `Fl_EPS_File_Surface` — write EPS
  - `Fl_SVG_File_Surface` — write SVG

**Usage pattern**:
```cpp
Fl_PDF_File_Surface pdf("output.pdf");
pdf.begin();
Fl_Surface_Device::push_current(&pdf);
  // FLTK drawing calls here
Fl_Surface_Device::pop_current();
pdf.end();
```

**Page formats**: `Fl_Paged_Device::page_format` — A4, Letter, Legal, etc. Set with `scale()` for custom scaling.

## Preferences

`Fl_Preferences` provides persistent key-value storage across application runs.

**Root types**:
- `Fl_Preferences::SYSTEM` — system-wide (read-only for most)
- `Fl_Preferences::USER` — per-user (writable)
- `Fl_Preferences::SYSTEM_L` / `Fl_Preferences::USER_L` — locale-independent (use for floating-point data)
- `Fl_Preferences::APPDIR` — application-specific directory

**Usage**:
```cpp
Fl_Prefs prefs(Fl_Preferences::USER, "mycompany", "myapp");
prefs.set("/settings/width", 800);
int w = prefs.get("/settings/width", 640);  // Default 640 if not set
prefs.set("/settings/name", "User Name");    // String values
```

**Path**: On Unix/Linux, user preferences stored in `$HOME/.config/fltk.org/` (XDG Base Directory). Old location `$HOME/.fltk/fltk.org/` still supported for backward compatibility.

**UTF-8 encoding**: All text entries stored as UTF-8 since FLTK 1.3.
