# Custom Widgets

## Contents
- Subclassing Fl_Widget
- Subclassing Fl_Group
- The draw() Method
- The handle() Method
- Damage Bits
- FLUID Integration

## Subclassing Fl_Widget

New widgets subclass `Fl_Widget` (for controls) or `Fl_Group` (for containers).

**Constructor pattern** (required for FLUID compatibility):
```cpp
class MyWidget : public Fl_Widget {
public:
    MyWidget(int x, int y, int w, int h, const char *label = 0)
        : Fl_Widget(x, y, w, h, label) {
        // Initialization
        type(42);  // Unique type ID (< FL_RESERVED_TYPE = 100)
    }

    void draw() override;
    int handle(int event) override;
};
```

**Base class initialization**: `Fl_Widget` constructor sets defaults:
- `box(FL_NO_BOX)`, `color(FL_BACKGROUND_COLOR)`
- `labeltype(FL_NORMAL_LABEL)`, `labelsize(FL_NORMAL_SIZE)`
- `labelcolor(FL_FOREGROUND_COLOR)`, `align(FL_ALIGN_CENTER)`
- `callback(default_callback, 0)`, flags: ACTIVE | VISIBLE

**Type identification**: Set unique `type()` value (< 100). FLTK does not use RTTI. For `Fl_Window` subclasses, use `FL_WINDOW + n` (1–7).

## Subclassing Fl_Group

Container widgets subclass `Fl_Group`. Override `resize()` for custom layout:

```cpp
class MyGroup : public Fl_Group {
public:
    MyGroup(int x, int y, int w, int h, const char *l = 0)
        : Fl_Group(x, y, w, h, l) {}

    void resize(int x, int y, int w, int h) override {
        Fl_Group::resize(x, y, w, h);
        // Position child widgets based on new size
        if (child(0)) child(0)->resize(x + 5, y + 5, w/2 - 10, h - 10);
        if (child(1)) child(1)->resize(x + w/2 + 5, y + 5, w/2 - 10, h - 10);
    }
};
```

## The draw() Method

Called by FLTK when the widget needs redrawing. Only call drawing functions here (or via `make_current()`).

```cpp
void MyWidget::draw() {
    draw_box();           // Draw widget's box type and background color

    // Custom drawing
    fl_color(FL_RED);
    fl_rect(x() + 5, y() + 5, w() - 10, h() - 10);

    draw_label();         // Draw widget's label (respects align)
}
```

**Protected helpers**:
- `draw_box()` — draws widget's box with current color
- `draw_box(type, color)` — draws specific box type
- `draw_label()` — draws label respecting alignment (skips if label is outside box)
- `draw_label(x, y, w, h, align)` — draws label in specified area
- `draw_focus()` — draws focus indicator rectangle

## The handle() Method

Process events. Return non-zero to claim, zero to propagate.

```cpp
int MyWidget::handle(int event) {
    switch (event) {
        case FL_PUSH:
            // Mouse click at Fl::event_x(), Fl::event_y()
            if (Fl::event_button() == 1) {
                // Left click handling
                return 1;
            }
            break;

        case FL_DRAG:
            // Drag handling
            return 1;

        case FL_RELEASE:
            // Button release
            do_callback();  // Trigger callback
            return 1;

        case FL_FOCUS:
        case FL_UNFOCUS:
            draw();  // Redraw to show/hide focus indicator
            return 1;

        case FL_KEYUP:
        case FL_SHORTCUT:
            if (Fl::event_key() == FL_Escape) {
                // Handle escape
                return 1;
            }
            break;

        case FL_ENTER:
            return 1;  // Accept mouse tracking

        default:
            return Fl_Widget::handle(event);  // Default handling
    }
    return 0;
}
```

## Damage Bits

Control partial redrawing with damage masks. Bits 0–3 are reserved by FLTK; use bits 4+ for custom regions.

```cpp
// In handle() — mark specific region as damaged
int MyWidget::handle(int event) {
    if (event == FL_PUSH) {
        damage(16);  // Bit 4 = custom region changed
        return 1;
    }
    return 0;
}

// In draw() — only redraw what's needed
void MyWidget::draw() {
    if (damage() & FL_DAMAGE_ALL) {
        draw_box();  // Redraw box on full damage
    }
    if (damage() & (FL_DAMAGE_ALL | 16)) {
        // Redraw custom region
    }
    draw_label();
}
```

**Damage constants**: `FL_DAMAGE_ALL` (everything), `FL_DAMAGE_EXPOSE` (window manager expose), `FL_DAMAGE_CHILD` (child moved/resized).

**Public redraw**: `widget->redraw()` — calls `damage(FL_DAMAGE_ALL)`. `widget->redraw_label()` — label-only redraw.

## FLUID Integration

To use custom widgets in FLUID:

1. **Constructor signature must match**: `(int x, int y, int w, int h, const char *label = 0)`
2. **Header file**: Place class definition in a `.H` file
3. **In FLUID**:
   - Create an `Fl_Box` widget as placeholder
   - Set the "class" field to your custom class name
   - Add `#include "MyWidget.H"` in the "Extra Code" field
4. **Generated code**: FLUID produces `new MyWidget(...)` constructors automatically

FLUID outputs `.cxx` files that include the widget headers and construct the UI hierarchy. Link with your custom widget implementation.
