# OpenGL & GLUT

## Contents
- Fl_Gl_Window
- OpenGL in Normal Windows
- HiDPI OpenGL
- GLUT Compatibility
- Mixing GLUT and FLTK

## Fl_Gl_Window

Subclass `Fl_Gl_Window` to create an OpenGL rendering area. Must implement `draw()` with OpenGL calls.

```cpp
#include <FL/Fl_Gl_Window.H>

class MyGLWindow : public Fl_Gl_Window {
    void draw() override {
        if (!valid()) {
            // Setup called once per resize
            glViewport(0, 0, w(), h());
            glMatrixMode(GL_PROJECTION);
            glLoadIdentity();
            gluPerspective(60, double(w())/h(), 0.1, 100);
            valid(1);
        }
        // OpenGL drawing here
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        // ... render scene ...
    }

    int handle(int event) override {
        switch (event) {
            case FL_PUSH:
                // Mouse down — position in Fl::event_x(), Fl::event_y()
                return 1;
            case FL_DRAG:
                // Mouse drag
                return 1;
            case FL_RELEASE:
                // Mouse up
                return 1;
            case FL_KEYBOARD:
                // Key pressed — Fl::event_key(), Fl::event_text()
                return 1;
            default:
                return Fl_Gl_Window::handle(event);
        }
    }

public:
    MyGLWindow(int x, int y, int w, int h, const char *l = 0)
        : Fl_Gl_Window(x, y, w, h, l) {}
};
```

**Important**: OpenGL context is NOT current inside `handle()`. Use `make_current()` before any non-drawing OpenGL calls (hit detection, texture loading). Never call OpenGL drawing from `handle()` — call `redraw()` instead.

## OpenGL in Normal Windows

Use `gl_start()` and `gl_finish()` to draw OpenGL into regular FLTK windows:

```cpp
#include <FL/gl.h>

void MyWidget::draw() {
    glstart();
    // OpenGL calls here
    glfinish();
}
```

Include `<FL/gl.h>` which wraps `<GL/gl.h>` (or `<OpenGL/gl.h>` on macOS) and defines FLTK-specific OpenGL helpers.

## HiDPI OpenGL

On HiDPI displays, `Fl_Gl_Window::w()/h()` return FLTK units, not pixels. Use pixel-aware APIs for viewport:

```cpp
void MyGLWindow::draw() {
    if (!valid()) {
        // Use pixel dimensions for viewport on HiDPI
        glViewport(0, 0, pixel_w(), pixel_h());
        valid(1);
    }
}
```

`pixel_w()` and `pixel_h()` return actual pixel dimensions. Regular `w()/h()` return FLTK units.

## GLUT Compatibility

FLTK provides `<FL/glut.H>` as a drop-in replacement for `<GL/glut.h>`. Based on GLUT 3.7 and FreeGLUT 2.4.0.

**Migration**: Replace `#include <GL/glut.h>` with `#include <FL/glut.H>`. Compile with C++ (not C). Link with FLTK library.

```cpp
#include <FL/glut.H>  // Instead of <GL/glut.h>

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    glutSwapBuffers();  // Note: does NOT work inside display function
}

int main(int argc, char **argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
    glutCreateWindow("GLUT in FLTK");
    glutDisplayFunc(display);
    glutMainLoop();
    return 0;
}
```

**Known limitations**:
- `glutGet(GLUT_ELAPSED_TIME)`, `glutGet(GLUT_SCREEN_*_MM)` — missing
- `glutKeyboardUpFunc` — missing
- `glutWarpPointer()`, `glutVideoResize()` — missing
- Spaceball, buttonbox, dials, tablet functions — missing
- `glutPostRedisplay()` does not work inside display function — use `glutIdleFunc()` instead
- `glutSwapBuffers()` does not work from inside display function (FLTK swaps automatically)
- Symbol values differ from standard GLUT (only true/false pairs and mouse buttons guaranteed same)
- Menu label strings are not copied — ensure lifetime

## Mixing GLUT and FLTK

Embed a GLUT window inside an `Fl_Window`:

```cpp
Fl_Window *parent = new Fl_Window(400, 400);
// Add FLTK widgets first
Fl_Button *btn = new Fl_Button(10, 10, 80, 25, "Button");

parent->show(argc, argv);  // Must show parent first!
parent->begin();

glutInitWindowSize(300, 300);
glutInitWindowPosition(10, 45);
// GLUT window creation here
glutCreateWindow("Embedded GLUT");

parent->end();
Fl::run();
```

Use `Fl_Glut_Window` class for programmatic GLUT window management within FLTK.
