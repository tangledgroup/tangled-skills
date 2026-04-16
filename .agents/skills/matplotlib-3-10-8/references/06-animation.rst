# Animation Reference

## FuncAnimation

The primary animation API for creating animations in matplotlib.

### Basic Animation

```python
from matplotlib.animation import FuncAnimation
import numpy as np

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = ax.plot([], [], 'ro')           # Note: comma unpacks list
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1, 1)

def init():
    ln.set_data([], [])
    return ln,

def animate(i):
    xdata.append(i * 0.1)
    ydata.append(np.sin(i * 0.1))
    ln.set_data(xdata, ydata)
    return ln,

ani = FuncAnimation(fig, animate, init_func=init,
                    frames=100, interval=50, blit=True)
plt.show()
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `fig` | Figure object to animate | Required |
| `func` | Animation function (frame_number → list of artists) | Required |
| `init_func` | Optional initialization function | None |
| `frames` | Number of frames or iterable | 100 |
| `interval` | Delay between frames in milliseconds | 200 |
| `repeat` | Whether to repeat animation | True |
| `blit` | Optimize by only redrawing changed artists | False |
| `repeat_delay` | Delay before repeating (ms) | None |

### Blitting for Performance

```python
# With blitting, only changed artists are redrawn (much faster)
ani = FuncAnimation(fig, animate, init_func=init,
                    frames=200, interval=20, blit=True)

# init_func must return tuple of all artists that will change
def init():
    ln.set_data([], [])
    text.set_text('')
    return ln, text
```

### Saving Animations

```python
# Save as GIF (requires pillow)
ani.save('animation.gif', writer='pillow', fps=30)

# Save as MP4 (requires ffmpeg or avconv)
ani.save('animation.mp4', writer='ffmpeg', fps=30,
         extra_args=['-vcodec', 'libx264'])

# Save as WebM
ani.save('animation.webm', writer='ffmpeg', fps=30)

# Save as HTML5 video (requires ffmpeg)
ani.save('animation.mp4', writer='ffmpeg')
```

### Available Writers

| Writer | Output Format | Dependency |
|--------|--------------|------------|
| `'pillow'` | GIF, PNG sequence | pillow |
| `'ffmpeg'` | MP4, WebM, OGG | ffmpeg |
| `'avconv'` | MP4, WebM | avconv |
| `'matplotlib.animation.PillowWriter'` | GIF | pillow |

Check available writers: `FFMpegWriter.all_available_methods()`.

### Example: 3D Rotation Animation

```python
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
z = np.linspace(-2, 2, 100)
r = z**2 + 1
x = r * np.sin(theta)
y = r * np.cos(theta)
line, = ax.plot(x, y, z)

def animate(i):
    line.set_data(x[:i], y[:i])
    line.set_3d_properties(z[:i])
    ax.view_init(elev=10., azim=45+i)
    return line,

ani = FuncAnimation(fig, animate, frames=len(theta), interval=50, blit=False)
plt.show()
```

### Example: Particle Simulation

```python
import numpy as np
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
circle = plt.Circle((0, 0), 0.2)
ax.add_patch(circle)

def init():
    circle.center = (0, 0)
    return circle,

def animate(i):
    angle = i * 0.1
    radius = np.sin(i * 0.05)
    circle.center = (radius * np.cos(angle), radius * np.sin(angle))
    circle.set_facecolor(plt.cm.viridis(i / 50))
    return circle,

ani = FuncAnimation(fig, animate, init_func=init, frames=100, interval=30, blit=True)
plt.show()
```

### HTML5 Embedding in Jupyter

```python
# In a Jupyter notebook:
from IPython.display import HTML
HTML(ani.to_jshtml())        # JavaScript-based (no ffmpeg needed)
HTML(ani.to_html5_video())   # HTML5 video (requires ffmpeg writer)
```

### TimedAnimation (Low-level API)

```python
from matplotlib.animation import TimedAnimation

class MyAnimation(TimedAnimation):
    def __init__(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        self.line, = ax.plot([], [])
        TimedAnimation.__init__(self, fig, interval=50)

    def draw_frame(self, frame_number):
        # Called for each frame
        self.line.set_data(range(frame_number), range(frame_number))
```
