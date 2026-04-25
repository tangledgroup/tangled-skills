# scipy.ndimage - N-Dimensional Image Processing

The `scipy.ndimage` module provides functions for filtering, smoothing, and processing n-dimensional arrays as images. It's particularly useful for image analysis, volume processing, and multi-dimensional data manipulation.

## Filtering and Smoothing

### Gaussian Filtering

```python
from scipy import ndimage
import numpy as np

# Create sample 2D image
image = np.random.rand(100, 100)

# Gaussian smoothing with sigma=1
smoothed = ndimage.gaussian_filter(image, sigma=1)

# Different sigma for each axis (2D)
smoothed_aniso = ndimage.gaussian_filter(image, sigma=(1, 2))

# 3D volume smoothing
volume = np.random.rand(50, 50, 50)
volume_smoothed = ndimage.gaussian_filter(volume, sigma=2)

# Gaussian derivative (for edge detection)
dx = ndimage.gaussian_filter(image, sigma=1, order=(1, 0))  # Derivative in x
dy = ndimage.gaussian_filter(image, sigma=1, order=(0, 1))  # Derivative in y
```

### Other Linear Filters

```python
from scipy import ndimage

# Uniform filter (boxcar/mean filter)
uniform_filtered = ndimage.uniform_filter(image, size=5)

# Correlate with custom kernel
kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]]) / 16
correlated = ndimage.correlate(image, kernel, mode='reflect')

# Convolve (correlate with flipped kernel)
convolved = ndimage.convolve(image, kernel, mode='reflect')

# Minimum and maximum filters
min_filtered = ndimage.minimum_filter(image, size=3)
max_filtered = ndimage.maximum_filter(image, size=3)

# Rank filter (nth value in neighborhood)
rank_filtered = ndimage.rank_filter(image, rank=5, size=11)  # 5th smallest in 11x11 window
```

### Edge Detection Filters

```python
from scipy import ndimage

# Sobel filters
sobel_x = ndimage.sobel(image, axis=0)  # Horizontal edges
sobel_y = ndimage.sobel(image, axis=1)  # Vertical edges

# Prewitt filters (similar to Sobel)
prewitt_x = ndimage.prewitt(image, axis=0)

# Roberts cross operator
roberts_x = ndimage.roberts(image, axis=0)

# Combine for edge magnitude
edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
```

## Morphological Operations

### Basic Morphology

```python
from scipy import ndimage
import numpy as np

# Binary image
binary_image = (image > 0.5).astype(np.uint8)

# Structuring element (neighborhood definition)
structure = np.ones((3, 3), dtype=int)  # 3x3 square

# Erosion (shrinks bright regions)
eroded = ndimage.binary_erosion(binary_image, structure=structure)

# Dilation (expands bright regions)
dilated = ndimage.binary_dilation(binary_image, structure=structure)

# Opening (erosion followed by dilation - removes small objects)
opened = ndimage.binary_opening(binary_image, structure=structure)

# Closing (dilation followed by erosion - fills small holes)
closed = ndimage.binary_closing(binary_image, structure=structure)
```

### Distance Transform

```python
from scipy import ndimage

# Binary image with objects
binary_image = np.zeros((50, 50), dtype=int)
binary_image[15:35, 15:35] = 1  # Square object

# Distance transform (distance to nearest zero)
distance = ndimage.distance_transform_edt(binary_image)

# Distance to nearest background pixel
distance_bg = ndimage.distance_transform_cdt(binary_image)

# Find skeleton (centerline)
skeleton = ndimage.morphology.thin(binary_image)
```

### Skeletonization and Thinning

```python
from scipy import ndimage

# Thin binary objects to 1-pixel width
thinned = ndimage.morphology.thin(binary_image, iterations=2)

# Alternative: Use skimage.morphology.skeletonize for better results
```

## Measurements and Analysis

### Labeling Connected Components

```python
from scipy import ndimage
import numpy as np

# Binary image with multiple objects
binary_image = np.zeros((100, 100), dtype=int)
binary_image[20:40, 20:40] = 1  # Object 1
binary_image[60:80, 60:80] = 1  # Object 2

# Label connected components
labeled_image, num_features = ndimage.label(binary_image)

print(f"Number of objects: {num_features}")

# Structure for connectivity (default is touching in any direction)
structure = np.ones((3, 3), dtype=int)  # 8-connectivity in 2D
labeled_image, num_features = ndimage.label(binary_image, structure=structure)
```

### Object Properties

```python
from scipy import ndimage

# Get properties of each labeled object
properties = ndimage.measurements.sum(image, labeled_image, index=np.arange(1, num_features+1))

# Calculate statistics for each object
means = ndimage.mean(image, labeled_image, index=np.arange(1, num_features+1))
stds = ndimage.standard_deviation(image, labeled_image, index=np.arange(1, num_features+1))

# Center of mass for each object
centers = ndimage.center_of_mass(image, labeled_image, index=np.arange(1, num_features+1))

# Extent (bounding box) of each object
minima = ndimage.minimum_position(labeled_image, axis=0)
maxima = ndimage.maximum_position(labeled_image, axis=0)
```

### Histograms and Statistics

```python
from scipy import ndimage

# Histogram of labeled regions
hist, bin_edges = np.histogram(image[labeled_image > 0], bins=50)

# Variance within each region
variances = ndimage.variance(image, labeled_image, index=np.arange(1, num_features+1))

# Minimum and maximum values in each region
mins = ndimage.minimum(image, labeled_image, index=np.arange(1, num_features+1))
maxs = ndimage.maximum(image, labeled_image, index=np.arange(1, num_features+1))
```

## Interpolation and Geometric Transformations

### Shift and Translate

```python
from scipy import ndimage
import numpy as np

# Shift image by (dx, dy)
shifted = ndimage.shift(image, shift=(5, -3), order=1)  # order: interpolation order

# Different interpolation orders:
# 0: nearest neighbor
# 1: linear (default)
# 2-5: cubic and higher-order spline
```

### Rotation

```python
from scipy import ndimage

# Rotate 2D image by angle (degrees)
rotated = ndimage.rotate(image, angle=45, reshape=False)  # Keep same size

# Rotate with reshaping to fit entire rotated image
rotated_full = ndimage.rotate(image, angle=45, reshape=True)

# 3D rotation around axes
volume_rotated = ndimage.rotate(volume, angle=30, axes=(1, 2))  # Rotate in y-z plane
```

### Scaling and Resizing

```python
from scipy import ndimage

# Scale image (zoom in/out)
scaled = ndimage.zoom(image, zoom=1.5)  # 1.5x larger

# Different zoom for each axis
scaled_aniso = ndimage.zoom(image, zoom=(1.5, 0.8))  # Stretch x, compress y

# Resize to specific dimensions
new_shape = (200, 300)
zoom_factors = np.array(new_shape) / image.shape
resized = ndimage.zoom(image, zoom_factors)
```

### Affine Transformations

```python
from scipy import ndimage

# Define affine transformation matrix
# For 2D: [[a, b], [c, d]] applied to coordinates
transform_matrix = np.array([[1.0, 0.1], [-0.1, 1.0]])  # Shear + scale

# Apply affine transform
offset = 0  # Additional offset
transformed = ndimage.affine_transform(image, transform_matrix, offset=offset)

# Inverse transform (for mapping output to input coordinates)
inverse_matrix = np.linalg.inv(transform_matrix)
```

### Coordinate Mapping

```python
from scipy import ndimage

# Create coordinate grid
grid_y, grid_x = np.meshgrid(np.arange(image.shape[0]), np.arange(image.shape[1]))

# Define custom coordinate mapping (warping)
new_x = grid_x + 10 * np.sin(grid_y / 20 * np.pi)
new_y = grid_y

# Map coordinates to input space
coordinates = np.vstack([new_x.ravel(), new_y.ravel()])
indices = coordinates.T.astype(int)

# Use map_coordinates for arbitrary interpolation
mapped = ndimage.map_coordinates(image, [grid_y, grid_x], order=3)
```

## Edge Handling Modes

```python
from scipy import ndimage

# Different modes for handling array boundaries
filtered_clipped = ndimage.gaussian_filter(image, sigma=1, mode='constant', cval=0.0)  # Pad with constant
filtered_reflect = ndimage.gaussian_filter(image, sigma=1, mode='reflect')  # Reflect at boundary
filtered_nearest = ndimage.gaussian_filter(image, sigma=1, mode='nearest')  # Nearest value
filtered_wrap = ndimage.gaussian_filter(image, sigma=1, mode='wrap')  # Wrap around (periodic)
filtered_mirror = ndimage.gaussian_filter(image, sigma=1, mode='mirror')  # Mirror at boundary

# Available modes: 'reflect', 'nearest-neighbor', 'constant', 'wrap', 'mirror'
```

## Peak and Feature Detection

### Finding Local Extrema

```python
from scipy import ndimage
import numpy as np

# Find local maxima
structure = np.ones((3, 3), dtype=int)
local_max = ndimage.maximum_filter(image, size=1) == image
maxima_coords = np.where(local_max)

# Find local minima
local_min = ndimage.minimum_filter(image, size=1) == image
minima_coords = np.where(local_min)

# Label maxima as separate objects
labeled_max, num_max = ndimage.label(local_max)
```

### Blob Detection (Laplacian of Gaussian)

```python
from scipy import ndimage

# Laplacian of Gaussian for blob detection
log_filtered = ndimage.laplace(image)  # First approximation

# Better: Apply Gaussian then Laplacian
gauss_blur = ndimage.gaussian_filter(image, sigma=2)
log_filtered = ndimage.laplace(gauss_blur)

# Find zero crossings or local extrema in LoG response
```

## 3D and Higher-Dimensional Processing

### Volume Processing

```python
from scipy import ndimage
import numpy as np

# 3D volume (e.g., medical imaging, scientific data)
volume = np.random.rand(100, 100, 100)

# Smooth 3D volume
volume_smoothed = ndimage.gaussian_filter(volume, sigma=2)

# Label 3D objects
binary_volume = (volume > 0.5).astype(int)
labeled_volume, num_objects = ndimage.label(binary_volume)

# Calculate 3D object properties
volumes = ndimage.sum(binary_volume, labeled_volume, index=np.arange(1, num_objects+1))
centroids = ndimage.center_of_mass(volume, labeled_volume, index=np.arange(1, num_objects+1))

# 3D morphological operations
structure_3d = np.ones((3, 3, 3), dtype=int)
eroded_3d = ndimage.binary_erosion(binary_volume, structure=structure_3d)
```

### Time Series in Images (4D)

```python
from scipy import ndimage

# 4D array: (time, z, y, x)
video_data = np.random.rand(100, 50, 50, 50)

# Smooth across time dimension
video_smoothed_time = ndimage.gaussian_filter(video_data, sigma=(2, 0, 0, 0))

# Smooth spatially but not temporally
video_smoothed_space = ndimage.gaussian_filter(video_data, sigma=(0, 1, 1, 1))
```

## Troubleshooting

### Memory Issues with Large Arrays

```python
# Process in chunks for large images
chunk_size = 100
for i in range(0, image.shape[0], chunk_size):
    for j in range(0, image.shape[1], chunk_size):
        chunk = image[i:i+chunk_size, j:j+chunk_size]
        processed_chunk = ndimage.gaussian_filter(chunk, sigma=1)
        # Save or combine processed chunks
```

### Boundary Artifacts

```python
# Use appropriate mode to minimize edge effects
filtered = ndimage.gaussian_filter(image, sigma=2, mode='reflect')

# Or pad image before processing
padded = np.pad(image, pad_width=10, mode='reflect')
filtered_padded = ndimage.gaussian_filter(padded, sigma=2)
filtered = filtered_padded[10:-10, 10:-10]  # Crop back to original size
```

### Interpolation Artifacts

```python
# Use higher interpolation order for smoother results
resized = ndimage.zoom(image, zoom=2.0, order=4)  # Quartic spline

# For binary images, use nearest neighbor (order=0)
binary_resized = ndimage.zoom(binary_image, zoom=2.0, order=0)
```

## See Also

- [`scipy.signal`](references/06-signal.md) - Signal processing filters
- [`skimage`](https://scikit-image.org/) - Comprehensive image analysis library
- [`opencv-python`](https://opencv.org/) - Computer vision and image processing
