# Drawing & Images

## Contents
- Drawing Primitives
- Colors
- Fonts and Text
- Box Types
- Image Hierarchy
- Offscreen Drawing

## Drawing Primitives

Include `<FL/fl_draw.H>`. Only call drawing functions inside `draw()` methods, custom box/label types, or with `Fl_Window::make_current()`.

**Lines and shapes**:
```cpp
fl_line(x1, y1, x2, y2);           // Line segment
fl_rect(x, y, w, h);               // Rectangle outline
fl_rectf(x, y, w, h);              // Filled rectangle
fl_circle(x, y, r);                // Circle outline
fl_pie(cx, cy, r, start_angle, sweep_angle);  // Pie slice
fl_arc(cx, cy, r, start_angle, sweep_angle);  // Arc
```

**Vertices** (complex shapes):
```cpp
fl_begin_vertices(type, n);
  fl_vertex(x, y);
  fl_vertex(x, y);
fl_end_vertices();
```

Types: `FL_POLYGON`, `FL_CLOSED`, `FL_LINES`, `FL_LINE_STRIP`, `FL_POINTS`.

**Clipping**: `fl_push_clip(x,y,w,h)` / `fl_pop_clip()` — nested clip regions.

**Line properties**:
```cpp
fl_line_style(style, width = 1);   // FL_SOLID, FL_DASH, FL_DOT, FL_DASHDOT
flLineWidth(float);                 // Line thickness
```

## Colors

FLTK colors are 32-bit values: indices 0–255 use the internal palette; values >255 are 24-bit RGB.

**Named constants**: `FL_BLACK`, `FL_RED`, `FL_GREEN`, `FL_YELLOW`, `FL_BLUE`, `FL_MAGENTA`, `FL_CYAN`, `FL_WHITE`, `FL_FOREGROUND_COLOR`, `FL_BACKGROUND_COLOR`, `FL_INACTIVE_COLOR`, `FL_SELECTION_COLOR`.

```cpp
fl_color(Fl_Color);                // Set drawing color
Fl_Color fl_contrast(fg, bg);      // High-contrast color for text on background
Fl_Color fl_rgb_color(r, g, b);    // Create RGB color (each 0-255)
void fl_get_color(Fl_Color c, uchar &r, uchar &g, uchar &b);
```

**Widget colors**: `widget->color()` for background, `widget->selection_color()` for selected state.

## Fonts and Text

**Built-in fonts**:
```cpp
FL_HELVETICA     // Default sans-serif
FL_BOLD          // Add to Helvetica, Courier, or Times
FL_ITALIC        // Add to Helvetica, Courier, or Times
FL_BOLD_ITALIC   // Add to Helvetica, Courier, or Times
FL_COURIER       // Monospace
FL_TIMES         // Serif
FL_SYMBOL        // Symbol font (not available on X11 for UTF-8)
FL_ZAPF_DINGBATS // Dingbats (not available on X11 for UTF-8)
```

**Drawing text**:
```cpp
fl_font(Fl_Font, Fl_Fontsize);     // Set current font
fl_draw(const char *text, x, y, w = 0, h = 0);  // Draw text
int fl_width(const char *text);    // Text width in pixels
int fl_descent();                   // Descent below baseline
int fl_height();                    // Total font height
```

**Measure text**: `widget->measure_label(label)` — get label dimensions.

## Box Types

Standard box types for widget borders. Set with `widget->box(type)`.

| Category | Types |
|----------|-------|
| No box | `FL_NO_BOX` |
| Flat | `FL_FLAT_BOX`, `FL_THIN_UP_BOX`, `FL_THIN_DOWN_BOX` |
| Up/Down | `FL_UP_BOX`, `FL_DOWN_BOX`, `FL_UP_FRAME`, `FL_DOWN_FRAME` |
| Engrave/Emboss | `FL_ENGRAVED_BOX`, `FL_EMBOSSED_BOX` |
| Thin/Groove | `FL_THIN_UP_BOX`, `FL_THIN_DOWN_BOX`, `FL_GROOVE_UP_BOX`, `FL_GROOVE_DOWN_BOX` |
| Rounded | `FL_ROUND_UP_BOX`, `FL_ROUND_DOWN_BOX` |
| Oval | `FL_OVAL_UP_BOX`, `FL_OVAL_DOWN_BOX` |
| Plastic (modern) | `FL_PLASTIC_UP_BOX`, `FL_PLASTIC_DOWN_BOX`, `FL_PLASTIC_FRAME`, etc. |

Draw boxes: `fl_draw_box(type, x, y, w, h, color)`.

## Image Hierarchy

All images derive from `Fl_Image`. Key subclasses:

| Class | Format | Header |
|-------|--------|--------|
| `Fl_RGB_Image` | Raw RGB data | `<FL/Fl_RGB_Image.H>` |
| `Fl_PNG_Image` | PNG files | `<FL/Fl_PNG_Image.H>` |
| `Fl_JPEG_Image` | JPEG files | `<FL/Fl_JPEG_Image.H>` |
| `Fl_SVG_Image` | SVG vector graphics | `<FL/Fl_SVG_Image.H>` |
| `Fl_GIF_Image` | GIF (animated via `Fl_Anim_GIF_Image`) | `<FL/Fl_GIF_Image.H>` |
| `Fl_BMP_Image` | Windows BMP | `<FL/Fl_BMP_Image.H>` |
| `Fl_ICO_Image` | Windows ICO | `<FL/Fl_ICO_Image.H>` |
| `Fl_XPM_Image` | XPM (X PixMap) | `<FL/Fl_XPM_Image.H>` |
| `Fl_PNM_Image` | PNM/PPM/PGM | `<FL/Fl_PNM_Image.H>` |
| `Fl_Bitmap` | C array bitmap | `<FL/Fl_Bitmap.H>` |
| `Fl_Pixmap` | X pixmap (X11) | `<FL/Fl_Pixmap.H>` |
| `Fl_XBM_Image` | X Bitmap | `<FL/Fl_XBM_Image.H>` |
| `Fl_Shared_Image` | Shared/cached images by path | `<FL/Fl_Shared_Image.H>` |
| `Fl_Tiled_Image` | Repeated tile pattern | `<FL/Fl_Tiled_Image.H>` |

**Usage**:
```cpp
Fl_PNG_Image *img = new Fl_PNG_Image("image.png");
img->draw(x, y, w, h);  // Draw at specified size
// Or set as widget image:
widget->image(img);
widget->deimage(img);    // Image for deactivated state
```

**Image scaling** (FLTK 1.4+): `img->scale(s)` controls drawing size independently of data dimensions. `img->w()/h()` give display size in FLTK units; `img->data_w()/data_h()` give pixel dimensions.

**Direct reading**: `Fl_Image::read(const char *filename)` — auto-detect format and load.

## Offscreen Drawing

**`Fl_Offscreen`**: Create an offscreen buffer for double-buffering or pre-rendering.
```cpp
Fl_Offscreen buf = fl_create_offscreen(w, h);
fl_push_offscreen(buf);
  // drawing calls here go to offscreen buffer
fl_pop_offscreen();
// Later, blit to screen:
fl_draw_image(offscreen, x, y, w, h, ...);
```

**`Fl_Image_Surface`**: Render to an `Fl_RGB_Image` for saving or reuse.
```cpp
Fl_Image_Surface surface(w, h);
Fl_Surface_Device::push_current(&surface);
  // drawing calls
Fl_Surface_Device::pop_current();
Fl_RGB_Image *img = surface.image();
```

**`Fl_Widget_Surface`**: Capture a widget's drawing to an image.
