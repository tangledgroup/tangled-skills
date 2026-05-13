# glib and Qt Frontends

## Contents
- glib (GObject) API
- Qt5 API
- Qt6 API
- Frontend Comparison

---

## glib (GObject) API

The glib frontend wraps Poppler's C++ core with GObject types, making it accessible from C, Python (via pygobject), Vala, and other GNOME languages. Header: `<poppler.h>`. Library: `libpoppler-glib`.

### Core Types

| Type | Description |
|------|-------------|
| `PopplerDocument` | PDF document, loaded from file or data |
| `PopplerPage` | Single page with text, links, annotations |
| `PopplerAction` | PDF action (GoTo, URI, Launch, etc.) |
| `PopplerAnnot` | Annotation (text, link, widget, popup, caret, ink, line, square, circle, polygon, polyline, highlight, underline, squiggly, strikeout, stamp, caret, free-text, sound, movie, screen, printer-mark, trap-net, watermarks, 3D-annotation) |
| `PopplerAttachment` | Embedded file |
| `PopplerFormField` | Form field (push-button, text, checkbox, radio-button, list-box, combo-box, signature) |
| `PopplerLayer` | Optional content group (layer) |
| `PopplerMedia` | Page media content |
| `PopplerMovie` | Embedded movie |
| `PopplerStructureElement` | Logical structure tree element |
| `PopplerColor` | Color space and value |
| `PopplerTextSpan` | Text span with font info |

### Loading Documents

```c
#include <poppler.h>

GError *error = NULL;

// From file
PopplerDocument *doc = poppler_document_new_from_file("file.pdf", NULL, NULL, &error);
if (error) {
    g_print("Error: %s\n", error->message);
    g_error_free(error);
    return;
}

// With passwords
PopplerDocument *doc = poppler_document_new_from_file("file.pdf", "owner_pw", "user_pw", &error);

// From memory
GBytes *data = g_bytes_new(buf, len);
PopplerDocument *doc = poppler_document_new_from_data(data, NULL, NULL, &error);
```

### Document Properties

```c
int pages = poppler_document_get_n_pages(doc);

const char *title     = poppler_document_get_title(doc);
const char *author    = poppler_document_get_author(doc);
const char *subject   = poppler_document_get_subject(doc);
const char *keywords  = poppler_document_get_keywords(doc);
const char *creator   = poppler_document_get_creator(doc);
const char *producer  = poppler_document_get_producer(doc);

gboolean encrypted    = poppler_document_is_encrypted(doc);
GBytes *metadata     = poppler_document_get_metadata(doc);

// Page mode
PopplerPageMode mode = poppler_document_get_page_mode(doc);
// POPPLER_PAGE_MODE_USE_NONE, USE_OUTLINES, USE_THUMBS, FULLSCREEN, USE_OC, USE_ATTACH

// Page layout
PopplerPageLayout layout = poppler_document_get_page_layout(doc);
```

### Page Operations

```c
PopplerPage *page = poppler_document_get_page(doc, 0); // 0-based index
// Returns a ref'd object — unref when done

double width  = poppler_page_get_width(page);
double height = poppler_page_get_height(page);
int rotation  = poppler_page_get_rotation(page); // 0, 90, 180, 270
const char *label = poppler_page_get_label(page);

// Text extraction
const char *text = poppler_page_get_text(page);
g_free((char *)text);

// Text within a rectangle
const char *rect_text = poppler_page_get_text_in_rect(page, x1, y1, x2, y2);
g_free((char *)rect_text);

// Word bounding boxes
GPtrArray *words = poppler_page_get_text_layout(page);
// Each element is a PopplerTextWord with text, bbox, font info

// Links
GPtrArray *links = poppler_page_get_links(page);
// Each element is a PopplerAction

// Annotations
GPtrArray *annots = poppler_page_get_annotations(page);

poppler_page_unref(page);
```

### Rendering to Image (glib)

```c
// Render page to cairo surface
CairoSurface *surface = poppler_page_render(page);
// Use cairo_surface_write_to_png(surface, "output.png");
// Then g_object_unref(surface);
```

### Layers (Optional Content)

```c
GPtrArray *layers = poppler_document_get_layers(doc);
// Each element is a PopplerLayer
gboolean visible = poppler_layer_get_is_visible(layer);
poppler_layer_set_is_visible(layer, TRUE);
```

### Error Handling

All glib functions that can fail accept a `GError **` parameter. Always check for non-null error after calls and free with `g_error_free()`.

---

## Qt5 API

Namespace: `Poppler`. Library: `poppler-qt5`. Header: `<poppler-qt5.h>`. Requires Qt 5.15+.

### Document Loading

```cpp
#include <poppler-qt5.h>

auto *doc = Poppler::Document::load("file.pdf");
if (!doc) { /* handle error */ }

// With password
auto *doc = Poppler::Document::load("file.pdf", QByteArray("owner_pw"), QByteArray("user_pw"));

// From data
auto *doc = Poppler::Document::loadFromData(QByteArray(data));
```

### Page Access and Rendering

```cpp
int pages = doc->numPages();
auto *page = doc->page(0); // 0-based, returns QSharedPointer<Poppler::Page>

// Render to QImage
QImage img = page->renderToImage(200, 200); // width, height in pixels
// Or with resolution:
QImage img = page->renderToImage(0, 0, 0, 0, 200, 200); // x,y,w,h at DPI

// Render cropped region
QImage img = page->renderToImage(0, 0, 100, 100, 200, 200, Poppler::Page::Rotate0);
```

### Document Properties

```cpp
QDateTime created = doc->docData(Poppler::Document::CreationDate).value<QDateTime>();
QDateTime modified = doc->docData(Poppler::Document::ModDate).value<QDateTime>();
QString title = doc->docData(Poppler::Document::Title).toString();
QString author = doc->docData(Poppler::Document::Author).toString();
QString subject = doc->docData(Poppler::Document::Subject).toString();
QString keywords = doc->docData(Poppler::Document::Keywords).toString();
QString creator = doc->docData(Poppler::Document::Creator).toString();
QString producer = doc->docData(Poppler::Document::Producer).toString();

bool encrypted = doc->isEncrypted();
bool locked = doc->isLocked();

// Unlock
doc->unlock(QByteArray("owner_pw"), QByteArray("user_pw"));

// Form type
auto formType = doc->formType(); // Poppler::Document::FormNone, FormAcro, FormXfa

// JavaScript
bool hasJs = doc->hasJavaScript();
```

### Page Properties

```cpp
QSizeF size = page->pageSize();
int rotation = page->rotation();
QString label = page->label();
QString text = page->text(); // Full page text
QString rectText = page->text(QRectF(x1, y1, w, h));

// Links
auto links = page->links();
// QVector of Poppler::Action

// Annotations
auto annots = page->annotations();
// QVector of Poppler::Annotation

// Media
auto media = page->media();
```

---

## Qt6 API

Namespace: `Poppler`. Library: `poppler-qt6`. Header: `<poppler-qt6.h>`. Requires Qt 6.4+.

The Qt6 API is nearly identical to Qt5 with the same class structure (`Poppler::Document`, `Poppler::Page`). The primary differences are header includes and Qt6 type compatibility (`QImage`, `QRectF`, etc.).

```cpp
#include <poppler-qt6.h>

auto *doc = Poppler::Document::load("file.pdf");
auto *page = doc->page(0);
QImage img = page->renderToImage(200, 200);
QString text = page->text();
```

---

## Frontend Comparison

| Feature | C++ | glib | Qt5 | Qt6 |
|---------|-----|------|-----|-----|
| Language | C++23 | C (GObject) | C++ (Qt5) | C++ (Qt6) |
| Rendering | `page_renderer` → `image` | cairo surface | `QImage` | `QImage` |
| Text extraction | `vector<text_box>` with bbox | `get_text()` / `get_text_layout()` | `QString` | `QString` |
| Memory management | Manual (`delete`) | Reference counting (`g_object_unref`) | `QSharedPointer` | `QSharedPointer` |
| Embedded files | Yes | Yes | Yes | Yes |
| Annotations | No (core only) | Yes | Yes | Yes |
| Form fields | No (core only) | Yes | Yes | Yes |
| Layers/OCG | No (core only) | Yes | Yes | Yes |
| Dependencies | None extra | glib ≥ 2.80 | Qt5 ≥ 5.15 | Qt6 ≥ 6.4 |
| Best for | C++ applications, minimal deps | GNOME/GTK apps, Python via pygobject | Qt5 desktop apps | Qt6 desktop apps |

The C++ frontend has the fewest dependencies and is suitable for any C++ application. The glib and Qt frontends add annotation, form field, layer, and media support not available in the raw C++ wrapper.
