# C++ API

## Contents
- Loading Documents
- Document Operations
- Page Operations
- Rendering Pages
- Text Extraction
- Table of Contents
- Embedded Files
- Fonts
- Destinations and Links
- Images
- Utility Types

---

## Loading Documents

The `poppler::document` class is the entry point. Use static factory methods — never construct directly.

```cpp
#include <poppler-document.h>

// From file
auto *doc = poppler::document::load_from_file("file.pdf");
auto *doc_pw = poppler::document::load_from_file("file.pdf", "owner_pw", "user_pw");

// From memory buffer
auto *doc = poppler::document::load_from_data(byte_array_ptr);

// From raw bytes
auto *doc = poppler::document::load_from_raw_data(data_ptr, length);
```

Always check for null return (file not found, corrupted PDF, wrong password). Delete with `delete doc` when done.

---

## Document Operations

### Metadata Access and Modification

```cpp
ustring title     = doc->get_title();
ustring author    = doc->get_author();
ustring subject   = doc->get_subject();
ustring keywords  = doc->get_keywords();
ustring creator   = doc->get_creator();
ustring producer  = doc->get_producer();
time_t created    = doc->get_creation_date_t();
time_t modified   = doc->get_modification_date_t();

// Set metadata
doc->set_title(ustring("New Title"));

// Arbitrary info keys
std::vector<std::string> keys = doc->info_keys();
ustring val = doc->info_key("CustomKey");
doc->set_info_key("CustomKey", ustring("value"));

// Remove all metadata
doc->remove_info();
```

### Document Properties

```cpp
bool encrypted    = doc->is_encrypted();
bool locked       = doc->is_locked();     // Password-protected, not yet unlocked
bool linearized   = doc->is_linearized(); // Web-optimized
int page_count    = doc->pages();

// PDF version
int major, minor;
doc->get_pdf_version(&major, &minor);

// Form type
auto form = doc->form_type(); // none, acro, xfa

// JavaScript presence
bool has_js = doc->has_javascript();

// Metadata stream (XMP)
ustring meta = doc->metadata();

// PDF IDs
std::string perm_id, update_id;
doc->get_pdf_id(&perm_id, &update_id);

// Page mode and layout
auto mode  = doc->page_mode();   // use_none, use_outlines, use_thumbs, fullscreen, use_oc, use_attach
auto layout = doc->page_layout(); // no_layout, single_page, one_column, two_column_left/right, two_page_left/right

// Permissions (for encrypted documents)
bool can_print = doc->has_permission(poppler::print);
```

### Unlocking Encrypted Documents

```cpp
if (doc->is_locked()) {
    bool ok = doc->unlock("owner_password", "user_password");
    if (!ok) { /* wrong password */ }
}
```

### Saving Documents

```cpp
doc->save("output.pdf");              // Overwrite original
doc->save_a_copy("copy.pdf");         // Save as new file
```

---

## Page Operations

Create page objects from a document. The caller owns the returned pointer — delete after use.

```cpp
#include <poppler-page.h>

// By index (0-based)
auto *page = doc->create_page(0);

// By label (e.g., "i", "1", "A")
auto *page = doc->create_page(ustring("1"));
```

### Page Properties

```cpp
double width  = page->width();    // Points
double height = page->height();   // Points

int rotation = page->rotation();  // 0, 90, 180, 270 degrees
// Rotation enums: rotate_0, rotate_90, rotate_180, rotate_270

poppler::rectangle media_box = page->media_box();
poppler::rectangle crop_box  = page->crop_box();

ustring label = page->label(); // Page label as displayed in PDF viewers

// Text extraction
std::vector<poppler::text_box> text = page->text();

// Media content
auto *media = page->media();
```

### Text Boxes

Each `text_box` represents a run of text with position and formatting info:

```cpp
for (const auto &tb : text) {
    ustring str   = tb.text();
    rectf bbox    = tb.bbox();          // x1, y1, x2, y2
    int rot       = tb.rotation();      // 0, 90, 180, 270
    bool space    = tb.has_space_after();
    double fsize  = tb.get_font_size();
    std::string fname = tb.get_font_name();
    auto wmode   = tb.get_wmode();     // horizontal_wmode / vertical_wmode

    // Per-glyph bounding boxes
    rectf glyph_bbox = tb.char_bbox(0);
}
```

---

## Rendering Pages

The `page_renderer` class configures rendering parameters and produces `image` objects.

```cpp
#include <poppler-page-renderer.h>
#include <poppler-image.h>

poppler::page_renderer renderer;

// Configure render hints
renderer.set_render_hint(poppler::page_renderer::antialiasing, true);
renderer.set_render_hint(poppler::page_renderer::text_antialiasing, true);
renderer.set_render_hint(poppler::page_renderer::text_hinting, true);

// Paper color (ARGB uint32)
renderer.set_paper_color(0xFFFFFFFF); // White

// Image format
renderer.set_image_format(poppler::image::format_png);
// Formats: format_png, format_jpeg, format_tiff, format_ppm

// Line rendering mode
renderer.set_line_mode(poppler::page_renderer::line_default);
// Modes: line_default, line_solid, line_shape

// Render full page at 150 DPI
auto img = renderer.render_page(page, 150.0, 150.0);

// Render cropped region
auto img = renderer.render_page(page, 72.0, 72.0, 0, 0, 500, 700, poppler::rotate_0);

// Check if rendering backend is available
if (!poppler::page_renderer::can_render()) {
    // Poppler built without cairo — rendering not available
}
```

### Image Operations

```cpp
// Save rendered image
img.save_to_file("output.png");

// Get pixel data
int w = img.width();
int h = img.height();
const unsigned char *data = img.data();
// Data is in BGRA format, row-major, no padding between rows
```

---

## Table of Contents

```cpp
#include <poppler-toc.h>

auto *toc = doc->create_toc();
// toc is a tree of toc_item objects
struct toc_item {
    ustring title;
    int     page_num;        // 1-based
    bool    is_open;         // Whether outline item is expanded
    std::vector<toc_item> children;
};

// Walk the TOC recursively
void walk(const poppler::toc &t) {
    for (const auto &item : t) {
        // item.title, item.page_num, item.is_open
        walk(item.children);
    }
}

delete toc;
```

---

## Embedded Files

```cpp
#include <poppler-embedded-file.h>

bool has_files = doc->has_embedded_files();
std::vector<poppler::embedded_file *> files = doc->embedded_files();

for (auto *ef : files) {
    ustring name = ef->file_name();
    ustring description = ef->description();
    ustring mime_type = ef->mime_type();
    time_t mtime = ef->mod_date_t();
    int size = ef->size();
    const char *data = ef->data();

    // Save to disk
    ef->save_to_file("extracted_file");
}
// embedded_file pointers are owned by the document — don't delete
```

---

## Fonts

```cpp
#include <poppler-font.h>

// All fonts in document
std::vector<poppler::font_info> all_fonts = doc->fonts();

// Iterator for incremental access (useful for large documents)
auto *iter = doc->create_font_iterator(0); // start from page 0
while (iter->has_next()) {
    auto fi = iter->next();
    // fi.name, fi.type, fi.encoding, fi.embedded, fi.subset,
    // fi.unichar_map, fi.object_id, fi.flags
}
delete iter;

struct font_info {
    std::string name;
    std::string type;        // "Type1", "TrueType", "Type1C", "CID Type0", etc.
    std::string encoding;
    bool embedded;
    bool subset;
    bool unichar_map;
    int  object_id;
    int  flags;
};
```

---

## Destinations and Links

Named destinations map string names to page locations:

```cpp
#include <poppler-destination.h>

std::map<std::string, poppler::destination> dests = doc->create_destination_map();

struct destination {
    int page_num;           // 0-based
    enum type_enum {
        fit, fit_horizontal, fit_vertical,
        fit_rect, fit_width, fit_height
    } type;
    // For fit_rect:
    double left, bottom, right, top;
    // Zoom (for fit types that support it)
    double zoom;
};
```

---

## Images

The `poppler::image` class holds raster pixel data from rendering:

```cpp
struct image {
    enum format_enum {
        format_png,
        format_jpeg,
        format_tiff,
        format_ppm
    };

    int width() const;
    int height() const;
    const unsigned char *data() const;  // BGRA, row-major
    bool save_to_file(const std::string &path) const;
};
```

---

## Utility Types

### ustring

UTF-16BE string wrapper used throughout the API:

```cpp
#include <poppler-global.h>

poppler::ustring s("hello");
std::string utf8 = s.to_std();
// Construct from UTF-8
poppler::ustring s2 = poppler::ustring::from_utf8(utf8_bytes);
```

### rectangle / rectf

Bounding box types:

```cpp
#include <poppler-rectangle.h>

struct rectangle {
    double x1, y1, x2, y2;
};

// rectf is a float variant used by text_box::bbox()
struct rectf {
    float x1, y1, x2, y2;
};
```

### page_transition

```cpp
#include <poppler-page-transition.h>

auto *transition = page->transition();
// transition type: replace, split, blind, box, wipe, dissolve,
//                  cover, uncover, fly, push, shuffle, fade,
//                  extract, fly_in, symbols
delete transition;
```
