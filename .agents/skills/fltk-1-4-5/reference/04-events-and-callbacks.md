# Events & Callbacks

## Contents
- Event Types
- Event Query Methods
- Callback Signatures
- Shortcut Handling
- Event Propagation

## Event Types

FLTK sends integer event codes to widget `handle()` methods. Return non-zero to claim the event; return zero to let it propagate.

### Mouse Events

| Event | Description |
|-------|-------------|
| `FL_PUSH` | Mouse button pressed. Widget claims by returning non-zero, then receives `FL_DRAG` and `FL_RELEASE`. |
| `FL_DRAG` | Mouse moved while button held. Continues until last button released. |
| `FL_RELEASE` | Mouse button released. Only received if widget claimed the `FL_PUSH`. |
| `FL_MOVE` | Mouse moved without buttons held. Sent to `Fl::belowmouse()` widget. Widget must claim `FL_ENTER` first. |
| `FL_MOUSEWHEEL` | Scroll wheel. Use `Fl::event_dx()` (horizontal) and `Fl::event_dy()` (vertical). Shift+scroll = horizontal on single-wheel mice. |

FLTK handles up to 5 mouse buttons (1=primary, 2=middle/wheel, 3=secondary, 4=back, 5=forward).

### Focus Events

| Event | Description |
|-------|-------------|
| `FL_ENTER` | Mouse entered widget. Return non-zero to receive `FL_MOVE` and `FL_LEAVE`. |
| `FL_LEAVE` | Mouse left widget. Only received if widget claimed `FL_ENTER`. |
| `FL_FOCUS` | Widget is being given keyboard focus. Return non-zero to receive keyboard events. |
| `FL_UNFOCUS` | Widget is losing keyboard focus. Sent to previous `Fl::focus()` widget. |

### Keyboard Events

| Event | Description |
|-------|-------------|
| `FL_KEYDOWN` / `FL_KEYBOARD` | Key pressed (synonyms). Check `Fl::event_key()` for key code, `Fl::event_text()` for text. |
| `FL_KEYUP` | Key released. Sent to current focus widget. |
| `FL_SHORTCUT` | Unhandled keyboard event propagated to all widgets. First to `Fl::belowmouse()`, then parent chain, then all windows. |

### Other Events

| Event | Description |
|-------|-------------|
| `FL_PASTE` | Paste from clipboard. |
| `FL_COPY` | Copy to clipboard. |
| `FL_CLEAR` | Clear selection. |
| `FL_MENU` | Menu key pressed (context menu). |
| `FL_SCROLL` | Scroll event (from window manager). |
| `FL_SHOW` / `FL_HIDE` | Widget shown/hidden. |
| `FL_CLOSE` | Window close request. Return non-zero to prevent closing. |
| `FL_FULLSCREEN` | Fullscreen toggle. |

## Event Query Methods

All `Fl::event_*()` methods return information about the most recent event. Valid until next event is processed.

| Method | Returns |
|--------|---------|
| `Fl::event()` | Current event type (integer) |
| `Fl::event_x()`, `Fl::event_y()` | Mouse position relative to target window |
| `Fl::event_x_root()`, `Fl::event_y_root()` | Absolute screen coordinates |
| `Fl::event_dx()`, `Fl::event_dy()` | Delta from last event (scroll wheel, drag) |
| `Fl::event_button()` | Which mouse button (1-5) |
| `Fl::event_buttons()` | All currently pressed buttons (bitmask) |
| `Fl::event_state()` | Modifier state bitmask (`FL_SHIFT`, `FL_CTRL`, `FL_ALT`, `FL_META`) |
| `Fl::event_key()` | Key code for keyboard events |
| `Fl::event_text()` | Text string for keypress |
| `Fl::event_length()` | Length of event text |
| `Fl::event_click()` | Click type: `FL_NO_CLICK`, `FL_SINGLE_CLICK`, `FL_DOUBLE_CLICK`, `FL_TRIPLE_CLICK` |
| `Fl::event_is_click()` | Returns true if current event is a click (push matching release at same position) |

**Modifier constants**: `FL_SHIFT`, `FL_CTRL`, `FL_ALT`, `FL_META`, `FL_BUTTON1`–`FL_BUTTON5`.

## Callback Signatures

Three callback types:

```cpp
// C-style callback
typedef void Fl_Callback_p(void *);
void widget->callback(Fl_Callback_p *func, void *data = nullptr);

// Member function callback
typedef void (Class::*Fl_Callback1)(void *);
void widget->callback(Fl_Callback1 *func, void *data = nullptr);

// Reason-aware callback (recommended)
typedef void (*Fl_Callback_Reason)(void *, Fl_Callback_Reason);
enum Fl_Callback_Reason {
    FL_CHANGED,      // User changed value
    FL_RELEASE,       // Button released
    FL_ACTIVATE,      // Widget activated/deactivated
    FL_DEACTIVATE,
    FL_ENTER,         // Mouse enter
    FL_LEAVE,         // Mouse leave
    FL_FOCUS,         // Focus gained
    FL_UNFOCUS,       // Focus lost
    FL_SELECT,        // Browser/menu item selected
    FL_DOUBLE_CLICK,
    FL_PUSH,          // Mouse push
    FL_MENU_CHOICE,   // Menu item chosen
    FL_SHORTCUT,      // Keyboard shortcut
    FL_OUTPUT_CHANGED, // Output widget changed
    FL_WHEN_ENTER_KEY, // Return key in input
    FL_RELEASE        // Mouse release
};
```

**Member function callback**:
```cpp
class MyWindow : public Fl_Window {
public:
    void button_cb(Fl_Widget *w, void *) { /* handle */ }
};
btn->callback((Fl_Callback1 *)&MyWindow::button_cb, this);
```

**Lambda/callback with reason**:
```cpp
btn->callback([](Fl_Widget *w, void *) {
    // handle callback
});
```

Call `widget->do_callback()` to trigger callback programmatically.

## Shortcut Handling

Shortcuts are triggered by `FL_SHORTCUT` events when the focused widget ignores a keypress.

**Label-based shortcuts**: Set `SHORTCUT_LABEL` flag (default on buttons). Label `&Open` underlines 'O' and activates on 'O' keypress. Test with `widget->test_shortcut()`.

**Menu shortcuts**: Define in `Fl_Menu_Item`:
```cpp
{"Open", FL_CTRL+'o', callback},  // Ctrl+O
{"Copy", FL_CTRL+'c', callback},  // Ctrl+C
```

**Prevent Escape from closing windows**: Install a global handler:
```cpp
static int esc_handler(int event) {
    if (event == FL_SHORTCUT && Fl::event_key() == FL_Escape) return 1;
    return 0;
}
Fl::add_handler(esc_handler);
```

## Event Propagation

1. **Direct target**: Event sent to widget under mouse or with focus
2. **Parent chain**: If unhandled, sent up through parent groups
3. **Shortcut broadcast**: `FL_SHORTCUT` sent to `Fl::belowmouse()`, then its parents, then all windows
4. **Global handlers**: `Fl::add_handler()` functions called for unrecognized events

Override `handle(int event)` in custom widgets. Return non-zero to claim, zero to propagate. Call base class `handle(event)` for default behavior on unhandled events.
