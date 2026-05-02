# Widget Reference

## Contents
- Buttons
- Inputs and Outputs
- Valutors
- Browsers
- Groups and Layout
- Text Widgets
- Tables, Trees, Charts
- Menus and Choices
- Miscellaneous

## Buttons

All buttons derive from `Fl_Button`. Constructor: `(x, y, w, h, label)`.

| Widget | Description |
|--------|-------------|
| `Fl_Button` | Standard push button. Callback on click. |
| `Fl_Check_Button` | Checkbox with check mark. |
| `Fl_Light_Button` | Push button with indicator light. |
| `Fl_Repeat_Button` | Repeats callback while held down. |
| `Fl_Return_Button` | Activated by Enter key in addition to click. |
| `Fl_Round_Button` | Radio circle button. |
| `Fl_Toggle_Button` | Push/toggle between on/off states. |
| `Fl_Radio_Button` | Exclusive radio button (setonly turns off siblings). |
| `Fl_Radio_Light_Button` | Radio button with light indicator. |
| `Fl_Radio_Round_Button` | Round radio button. |
| `Fl_Shortcut_Button` | Button activated by keyboard shortcut from label (`&Key`). |

**Button types**: Set behavior via `type()`:
- `FL_NORMAL_BUTTON` — standard push (default)
- `FL_TOGGLE_BUTTON` — toggle on/off
- `FL_RADIO_BUTTON` — exclusive radio group

**State methods**: `value()` gets/sets state (0=off, 1=on). `set()`, `clear()`, `setonly()` for toggles/radios.

## Inputs and Outputs

All derive from `Fl_Input_`. Constructor: `(x, y, w, h, label)`.

| Widget | Description |
|--------|-------------|
| `Fl_Input` | Single-line text input. |
| `Fl_Output` | Single-line text output (read-only, copyable). |
| `Fl_Multiline_Input` | Multi-line text input. |
| `Fl_Multiline_Output` | Multi-line text output. |
| `Fl_File_Input` | File path input with browse button. |
| `Fl_Secret_Input` | Password input (characters hidden). |
| `Fl_Value_Input` | Floating-point numeric input. |
| `Fl_Value_Output` | Floating-point numeric output. |
| `Fl_Int_Input` | Integer input. |
| `Fl_Float_Input` | Float input. |
| `Fl_Spinner` | Input with up/down arrow buttons for incrementing. |

**Key methods**:
- `value()` — get/set text content (copied internally)
- `textsize()`, `textfont()`, `textcolor()` — text formatting
- `size(int)` — maximum text length
- `insertchar()`, `deletechar()` — cursor-based editing

## Valutors

All derive from `Fl_Valuator`. Constructor: `(x, y, w, h, label)`.

| Widget | Description |
|--------|-------------|
| `Fl_Slider` | Horizontal slider with knob. |
| `Fl_Hor_Slider` / `Fl_Vert_Slider` | Explicit direction sliders. |
| `Fl_Value_Slider` / `Fl_Hor_Value_Slider` | Slider displaying current value. |
| `Fl_Nice_Slider` / `Fl_Hor_Nice_Slider` | Slider with tick marks. |
| `Fl_Fill_Slider` / `Fl_Hor_Fill_Slider` | Slider with filled track. |
| `Fl_Scrollbar` | Standard scrollbar widget. |
| `Fl_Dial` | Round knob dial. |
| `Fl_Line_Dial` / `Fl_Fill_Dial` | Dial variants. |
| `Fl_Roller` | SGI-style dolly widget. |
| `Fl_Counter` | Arrow buttons with displayed value. |
| `Fl_Simple_Counter` | Counter without display. |
| `Fl_Adjuster` | Compact up/down arrows. |
| `Fl_Positioner` | 2D position selector (x,y). |
| `Fl_Progress` | Progress bar. |
| `Fl_Timer` / `Fl_Clock` / `Fl_Round_Clock` | Clock displays. |

**Key methods**:
- `value()` — get/set current value (double)
- `minimum()` / `maximum()` — value range
- `step()` — increment step size
- `precision()` — decimal places for display

## Browsers

| Widget | Description |
|--------|-------------|
| `Fl_Browser` | Scrollable list of text items. |
| `Fl_File_Browser` | File browser with directory listing. |
| `Fl_Check_Browser` | Browser with checkboxes per item. |

**Key methods**: `add(text)`, `remove(n)`, `replace(n, text)`, `size()`, `top()`, `value()` (selected index). Types: `FL_NORMAL_BROWSER`, `FL_SELECT_BROWSER`, `FL_MULTISELECT_BROWSER`.

## Groups and Layout

| Widget | Description |
|--------|-------------|
| `Fl_Group` | Base container. Manual layout with x,y,w,h per child. |
| `Fl_Pack` | Children packed in row or column. `spacing()` between items. |
| `Fl_Flex` | Flexible row/column layout. Supports nesting, fixed-size children via `resize()`. `type(FL_HORIZONTAL/FL_VERTICAL)`. |
| `Fl_Tile` | All children resize proportionally to fill area. |
| `Fl_Grid` | Grid layout with rows/columns, auto-layout, nested grids. |
| `Fl_Scroll` | Scrollable container with scrollbars. `type(FL_HOR_SCROLLBAR/FL_VERT_SCROLLBAR/FL_BOTH_SCROLLBARS)`. |
| `Fl_Tabs` | Child widgets displayed as tabs. |
| `Fl_Wizard` | Displays one child group at a time (wizard pages). `show_page(n)`. |

**Layout notes**: `Fl_Flex` is the modern replacement for `Fl_Pack`. Unlike `Fl_Pack`, `Fl_Flex` resizes its children to fill available space. Set fixed sizes with `child->resize(x, y, w, h)` and `flex(0)` to inhibit resizing of specific children.

## Text Widgets

| Widget | Description |
|--------|-------------|
| `Fl_Text_Display` | Multi-line text display with scrolling, selection, syntax highlighting via style tables. Uses `Fl_Text_Buffer`. |
| `Fl_Text_Editor` | Editable text widget. Inherits from `Fl_Text_Display`. Supports key bindings (`Key_Binding`). |
| `Fl_Help_View` | HTML text display (subset of HTML). Supports links, images, fonts, colors. |
| `Fl_Terminal` | Terminal emulator widget with PTY support. |

**`Fl_Text_Buffer`**: Shared text buffer for `Fl_Text_Display` and `Fl_Text_Editor`. Methods: `text()`, `textlength()`, `append()`, `insert()`, `remove()`, `select()`.

**Style tables** (`Fl_Text_Display`): Register `Style_Table_Entry` with regex patterns, colors, fonts for syntax highlighting.

## Tables, Trees, Charts

| Widget | Description |
|--------|-------------|
| `Fl_Table` | Virtual table widget. Subclass to implement `cell()`, `size()`, `rowh()`, `width()`. Supports sorting, selection. |
| `Fl_Table_Row` | Row-based table with built-in row management. |
| `Fl_Tree` | Expandable tree widget. Items via `Fl_Tree_Item`. Preferences via `Fl_Tree_Prefs`. |
| `Fl_Chart` | Bar/line chart widget. Add entries with `add()`. Supports scrolling, zooming. |

## Menus and Choices

| Widget | Description |
|--------|-------------|
| `Fl_Choice` | Dropdown menu (pop-up or down-arrow style). |
| `Fl_Menu_Bar` | Horizontal menu bar. |
| `Fl_Sys_Menu_Bar` | System-native menu bar (macOS menubar, Windows top-level). |
| `Fl_Input_Choice` | Input field with dropdown choice button. |
| `Fl_Color_Chooser` | Color selection dialog. |
| `Fl_Scheme_Chooser` | Visual scheme/theme chooser. |

**Menu items**: `Fl_Menu_Item` array — null-terminated, supports labels, shortcuts, icons, callbacks, user data, menu types (`FL_NORMAL_MENUITEM`, `FL_RADIO_MENUITEM`, `FL_CHECKMENUITEM`, `FL_SEPARATOR_MENUITEM`).

```cpp
static Fl_Menu_Item menu[] = {
    {"File", 0, 0, 0, FL_SUBMENU},
      {"Open", FL_CTRL+'o', my_callback, 0},
      {"Save", FL_CTRL+'s', my_callback, 0},
      {"-", 0, 0, 0, FL_SEPARATOR_MENUITEM},
      {"Exit", FL_Escape, my_callback, 0},
    {0}
};
```

## Miscellaneous

| Widget | Description |
|--------|-------------|
| `Fl_Box` | Simple box with optional label. Set `box()` type for border style. |
| `Fl_Free` | Free-form container — manually manage child positions without automatic layout. |
| `Fl_Native_File_Chooser` | OS-native file open/save dialog. Supports filters, directories, multiple selection. |
| `Fl_File_Chooser` | FLTK-style file chooser dialog. |

**Native dialogs**: `fl_message()`, `fl_alert()`, `fl_choice()`, `fl_input()`, `fl_hold()`, `fl_ask()` — modal dialog functions (include `<FL/fl_ask.H>`).
