# Data Loading

## Contents
- Dataset API
- DataLoader API
- Custom Datasets
- Transforms and Augmentation
- Sampling Strategies
- Multiprocessing Best Practices

## Dataset API

`torch.utils.data.Dataset` is the base class for all datasets. Implement `__len__` and `__getitem__`:

```python
from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, data_paths, labels):
        self.data_paths = data_paths
        self.labels = labels

    def __len__(self):
        return len(self.data_paths)

    def __getitem__(self, idx):
        sample = load_data(self.data_paths[idx])  # your loading logic
        label = self.labels[idx]
        return sample, label
```

`TensorDataset` for in-memory tensor data:

```python
from torch.utils.data import TensorDataset

dataset = TensorDataset(features_tensor, labels_tensor)
# features_tensor: (N, D), labels_tensor: (N,) or (N, C)
```

## DataLoader API

`DataLoader` wraps a Dataset and provides batching, shuffling, and parallel loading:

```python
from torch.utils.data import DataLoader

loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,           # only for training
    num_workers=4,          # parallel data loading processes
    pin_memory=True,        # faster CPU→GPU transfer
    drop_last=True,         # drop incomplete last batch
)

for batch_x, batch_y in loader:
    outputs = model(batch_x.to(device))
    loss = criterion(outputs, batch_y.to(device))
```

Key parameters:
- `batch_size` — samples per batch
- `shuffle` — randomize order each epoch
- `num_workers` — background processes for data loading (0 = main process)
- `pin_memory` — allocate in pinned memory for faster GPU transfer
- `collate_fn` — custom batching logic
- `drop_last` — discard incomplete final batch

## Custom Datasets

For file-based data, lazy-load samples in `__getitem__` to keep memory usage low:

```python
import os
from PIL import Image

class ImageDataset(Dataset):
    def __init__(self, img_dir, transform=None):
        self.img_paths = [
            os.path.join(img_dir, f) for f in os.listdir(img_dir)
            if f.endswith(('.png', '.jpg'))
        ]
        self.transform = transform

    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx):
        img = Image.open(self.img_paths[idx]).convert('RGB')
        if self.transform:
            img = self.transform(img)
        label = int(os.path.basename(self.img_paths[idx])[0])
        return img, label
```

## Transforms and Augmentation

Compose transforms with `torchvision.transforms`:

```python
from torchvision import transforms

train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])
```

## Sampling Strategies

Use custom samplers for weighted sampling or distributed training:

```python
from torch.utils.data import WeightedRandomSampler, DistributedSampler

# Oversample rare classes
weights = compute_class_weights(labels)
sampler = WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)
loader = DataLoader(dataset, batch_size=32, sampler=sampler)

# Distributed training — splits data across ranks
sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
loader = DataLoader(dataset, batch_size=32, sampler=sampler)
```

## Multiprocessing Best Practices

When using `num_workers > 0`:
- Use the `spawn` start method: `torch.multiprocessing.set_start_method('spawn', force=True)`
- Guard top-level code with `if __name__ == '__main__':`
- Avoid large objects in global scope that get pickled per worker
- Set `prefetch_factor` (default 2) to control how many batches each worker prepares ahead
- For I/O-bound data loading, 2–4 workers is typically sufficient; for compute-heavy transforms, increase proportionally
