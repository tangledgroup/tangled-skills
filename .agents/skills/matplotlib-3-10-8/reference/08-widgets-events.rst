# Widgets & Events Reference

## Widget Types

### Slider

```python
from matplotlib.widgets import Slider

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.15)

line, = plt.plot(x, y)

slider_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
freq_slider = Slider(slider_ax, 'Freq', 0.1, 30.0, valinit=1.0)

def update(val):
    freq = freq_slider.val
    line.set_ydata(np.sin(2 * np.pi * freq * x))
    fig.canvas.draw_idle()

freq_slider.on_changed(update)
plt.show()
```

### Button

```python
from matplotlib.widgets import Button

button_ax = fig.add_axes([0.8, 0.05, 0.1, 0.075])
button = Button(button_ax, 'Reset')

def reset(event):
    line.set_data([], [])
    fig.canvas.draw_idle()

button.on_clicked(reset)
```

### CheckButtons

```python
from matplotlib.widgets import CheckButtons

ax_check = plt.axes([0.7, 0.05, 0.1, 0.15])
labels = ['Line 1', 'Line 2']
lines = [line1, line2]
check = CheckButtons(ax_check, labels, [True, True])

def func(label):
    idx = labels.index(label)
    lines[idx].set_visible(not lines[idx].get_visible())
    fig.canvas.draw_idle()

check.on_clicked(func)
```

### RadioButtons

```python
from matplotlib.widgets import RadioButtons

ax_radio = plt.axes([0.02, 0.5, 0.15, 0.3])
radio = RadioButtons(ax_radio, ('red', 'green', 'blue'))

def func(label):
    line.set_color(label)
    fig.canvas.draw_idle()

radio.on_clicked(func)
```

### RangeSelector (RectangleSelector)

```python
from matplotlib.widgets import RectangleSelector

def on_select(eclick, erelease):
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    print(f'Selected: ({x1}, {y1}) to ({x2}, {y2})')

rs = RectangleSelector(ax, on_select,
                       drawtype='box',
                       button=[1, 3],   # Left and right mouse buttons
                       minspanx=5, minspany=5,
                       interactive=True)
```

### Lasso Selector

```python
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path

def on_select(eclick, erelease):
    path = Path(eclick.ind)
    print(f'Selected points: {eclick.ind}')

lasso = LassoSelector(ax, on_select)
```

### Span Selector

```python
from matplotlib.widgets import SpanSelector

def on_span(xmin, xmax):
    print(f'Span: {xmin} to {xmax}')

span = SpanSelector(ax, on_span, 'horizontal',
                    useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))
```

### Cursor

```python
from matplotlib.widgets import Cursor

cursor = Cursor(ax, useblit=True, color='red', linewidth=1)
```

### EventPlot

```python
ax.eventplot(positions, orientation='vertical', lineoffsets=1, colors='C0')
```

## Event Handling

### Connecting to Canvas Events

```python
def on_press(event):
    if event.inaxes is None:
        return
    print(f'pressed button {event.button} at x={event.xdata}, y={event.ydata}')

def on_release(event):
    print(f'released at x={event.xdata}, y={event.ydata}')

def on_motion(event):
    if event.inaxes is not None:
        print(f'motion at ({event.xdata:.2f}, {event.ydata:.2f})')

def on_key(event):
    print(f'key {event.key} pressed')

cid1 = fig.canvas.mpl_connect('button_press_event', on_press)
cid2 = fig.canvas.mpl_connect('button_release_event', on_release)
cid3 = fig.canvas.mpl_connect('motion_notify_event', on_motion)
cid4 = fig.canvas.mpl_connect('key_press_event', on_key)
cid5 = fig.canvas.mpl_connect('key_release_event', lambda e: None)
cid6 = fig.canvas.mpl_connect('resize_event', lambda e: print('Resized'))
cid7 = fig.canvas.mpl_connect('figure_close_event', lambda e: print('Closed'))

# Disconnect handlers
fig.canvas.mpl_disconnect(cid1)
```

### Event Attributes

| Attribute | Description |
|-----------|-------------|
| `event.inaxes` | Axes the event occurred in (or None) |
| `event.xdata`, `event.ydata` | Data coordinates of event |
| `event.x`, `event.y` | Pixel coordinates |
| `event.button` | Mouse button (1=left, 2=middle, 3=right) |
| `event.key` | Key pressed (e.g., 'escape', 'ctrl+c') |
| `event.name` | Event name string |
| `event.canvas` | The canvas that generated the event |

### Available Events

| Event Name | Triggered When |
|------------|---------------|
| `button_press_event` | Mouse button pressed |
| `button_release_event` | Mouse button released |
| `motion_notify_event` | Mouse moved |
| `key_press_event` | Key pressed |
| `key_release_event` | Key released |
| `resize_event` | Figure resized |
| `draw_event` | Figure drawn |
| `figure_enter_event` | Mouse enters figure |
| `figure_leave_event` | Mouse leaves figure |
| `axes_enter_event` | Mouse enters axes |
| `axes_leave_event` | Mouse leaves axes |
| `pick_event` | Artist is picked (via picker) |
| `close_event` | Figure is being closed |

### Pick Events

```python
# Enable picking on an artist
line, = ax.plot(x, y, picker=5)   # 5 pixel tolerance

def on_pick(event):
    artist = event.artist
    if isinstance(artist, Line2D):
        thisx = artist.get_xdata()
        thisy = artist.get_ydata()
        ind = event.ind
        print(f'Points selected: {list(zip(thisx[ind], thisy[ind]))}')

fig.canvas.mpl_connect('pick_event', on_pick)
```

## Jupyter Integration

### Interactive Widgets (ipywidgets)

```python
from ipywidgets import interact, FloatSlider
import matplotlib.pyplot as plt

@interact(freq=(0.1, 30.0, 0.1))
def plot_sine(freq):
    x = np.linspace(0, 10, 200)
    plt.plot(x, np.sin(2 * np.pi * freq * x))
    plt.show()
```

### %matplotlib Inline (Jupyter magic)

```python
%matplotlib inline          # Static images in notebook
%matplotlib widget          # Interactive (requires ipympl)
%matplotlib notebook        # Legacy interactive
%matplotlib qt              # Separate Qt window
```
