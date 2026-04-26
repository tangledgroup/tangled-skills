# Animations

## Overview

Matplotlib provides two main approaches for creating animations:

- **FuncAnimation** — calls a function repeatedly to generate each frame (recommended)
- **ArtistAnimation** — pre-generates all frames as lists of Artists

Both produce `matplotlib.animation.Animation` objects that can be displayed interactively or saved to video/GIF files.

## FuncAnimation

The recommended approach. You provide an update function that modifies the plot for each frame.

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

fig, ax = plt.subplots()
xdata, ydata = [], []
line, = ax.plot([], [], 'r-', linewidth=2)
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1, 1)

def init():
    """Initialize the animation (first frame)."""
    line.set_data([], [])
    return line,

def update(frame):
    """Update function called for each frame."""
    xdata.append(frame)
    ydata.append(np.sin(frame))
    line.set_data(xdata, ydata)
    return line,

ani = animation.FuncAnimation(
    fig, update,
    frames=np.linspace(0, 2*np.pi, 100),
    init_func=init,
    blit=True,       # Use blitting for faster rendering
    interval=50,     # Milliseconds between frames
    cache_frame_data=False
)
plt.show()
```

### Key Parameters

- `fig` — the Figure to animate
- `func` — update function called per frame
- `frames` — iterable of frame data (int, array, or generator)
- `init_func` — function to draw the blank frame
- `blit` — if True, only redrawn changed artists (faster)
- `interval` — delay between frames in milliseconds
- `repeat` — whether to loop (default True)
- `cache_frame_data` — cache frame data for replay

## ArtistAnimation

Pre-generate all frames as lists of Artists:

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

fig, ax = plt.subplots()
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1, 1)

# Pre-generate all frames
ims = []
for i in range(50):
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x + i * 0.1)
    im = [ax.plot(x, y, 'r-')]
    ims.append(im)

ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat=True)
plt.show()
```

## Saving Animations

### PillowWriter (GIF and other formats)

```python
# Save as GIF
ani.save('animation.gif', writer='pillow', fps=30)

# Save as MP4
ani.save('animation.mp4', writer='pillow', fps=30)
```

### FFMpegWriter

```python
# Requires ffmpeg installed on the system
ani.save('animation.mp4', writer='ffmpeg', fps=30, bitrate=-1)
```

### ImageMagickWriter

```python
ani.save('animation.gif', writer='imagemagick', fps=30)
```

### HTMLWriter (for Jupyter notebooks)

```python
from matplotlib.animation import HTMLWriter

writer = HTMLWriter(fps=20)
ani.save('animation.html', writer=writer)
```

### PillowWriter Options

```python
ani.save('output.gif', writer='pillow', fps=15, dpi=100)
ani.save('output.mp4', writer='pillow', fps=30, codec='libx264')
```

## Blitting for Performance

Blitting redraws only the changed parts of the figure instead of the entire canvas. This dramatically improves performance for animations.

```python
def init():
    line.set_data([], [])
    scat.set_offsets(np.empty((0, 2)))
    return line, scat

def update(frame):
    line.set_data(x[:frame], y[:frame])
    scat.set_offsets(np.column_stack([x[:frame], y[:frame]]))
    return line, scat

ani = animation.FuncAnimation(fig, update, init_func=init,
                              blit=True, frames=200, interval=20)
```

**Important**: When using `blit=True`, the update function must return a tuple of all Artists that were modified. The `init_func` must also return the same Artists.

## Common Animation Patterns

### Moving Data Window

```python
fig, ax = plt.subplots()
line, = ax.plot([], [], linewidth=2)
ax.set_xlim(0, 100)
ax.set_ylim(-1, 1)

def update(frame):
    start = max(0, frame - 50)
    line.set_data(x[start:frame+1], y[start:frame+1])
    ax.set_xlim(start, frame)
    return line,

ani = animation.FuncAnimation(fig, update, frames=len(x), interval=30, blit=True)
```

### Growing Plot

```python
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', linewidth=2)
ax.set_xlim(0, 10)
ax.set_ylim(0, 1)

def update(frame):
    line.set_data(x[:frame+1], y[:frame+1])
    return line,

ani = animation.FuncAnimation(fig, update, frames=len(x), interval=50)
```

### Multiple Artists

```python
fig, ax = plt.subplots()
line1, = ax.plot([], [], 'r-', label='sin')
line2, = ax.plot([], [], 'b-', label='cos')

def update(frame):
    x_vals = np.linspace(0, 2*np.pi, frame+1)
    line1.set_data(x_vals, np.sin(x_vals))
    line2.set_data(x_vals, np.cos(x_vals))
    return line1, line2

ani = animation.FuncAnimation(fig, update, frames=100, blit=True, interval=30)
```

## Movie Writers

Available writers:

- **PillowWriter** — GIF, MP4 (requires Pillow)
- **FFMpegWriter** — MP4, MKV (requires ffmpeg)
- **ImageMagickWriter** — GIF (requires ImageMagick)
- **HTMLWriter** — HTML5 video for notebooks

List available writers:

```python
from matplotlib.animation import writers
print(writers.list())
```
