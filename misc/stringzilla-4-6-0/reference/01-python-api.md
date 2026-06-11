# Python API

## Str Class

The `Str` class is a hybrid of Python's `str`, `bytes`, `bytearray`, and `memoryview`. It provides a `str`-like interface to byte arrays with zero-copy views.

```python
from stringzilla import Str, File

text_from_str = Str('some-string')      # no copies, just a view
text_from_bytes = Str(b'some-array')    # no copies, just a view
text_from_file = Str(File('file.txt'))  # memory-mapped file

import numpy as np
alphabet_array = np.arange(ord("a"), ord("z"), dtype=np.uint8)
text_from_array = Str(memoryview(alphabet_array))
```

The `File` class memory-maps a file from persistent storage without loading a copy into RAM. Contents remain immutable and the mapping can be shared across multiple Python processes simultaneously.

### Basic Operations

- Length: `len(text) -> int`
- Indexing: `text[42] -> str`
- Slicing: `text[42:46] -> Str`
- Substring check: `'substring' in text -> bool`
- Hashing: `hash(text) -> int`
- String conversion: `str(text) -> str`

### Advanced Operations

```python
import sys

x: bool = text.contains('substring', start=0, end=sys.maxsize)
x: int = text.find('substring', start=0, end=sys.maxsize)
x: int = text.count('substring', start=0, end=sys.maxsize, allowoverlap=False)
x: str = text.decode(encoding='utf-8', errors='strict')
x: Strs = text.split(separator=' ', maxsplit=sys.maxsize, keepseparator=False)
x: Strs = text.rsplit(separator=' ', maxsplit=sys.maxsize, keepseparator=False)
x: Strs = text.splitlines(keeplinebreaks=False, maxsplit=sys.maxsize)
```

The `splitlines` behavior differs slightly from Python's native version. StringZilla matches `\n`, `\v`, `\f`, `\r`, `\x1c`, `\x1d`, `\x1e`, `\x85` — avoiding two-byte-long runes that the native version includes (`\u2028`, `\u2029`).

### Character Set Operations

Python strings lack native character set operations, forcing use of slow regular expressions. StringZilla provides:

```python
x: int = text.find_first_of('chars', start=0, end=sys.maxsize)
x: int = text.find_last_of('chars', start=0, end=sys.maxsize)
x: int = text.find_first_not_of('chars', start=0, end=sys.maxsize)
x: int = text.find_last_not_of('chars', start=0, end=sys.maxsize)
x: Strs = text.split_byteset(separator='chars', maxsplit=sys.maxsize, keepseparator=False)
x: Strs = text.rsplit_byteset(separator='chars', maxsplit=sys.maxsize, keepseparator=False)
```

### Trimming and Random Generation

```python
x: str = text.lstrip('chars')  # Strip leading characters
x: str = text.rstrip('chars')  # Strip trailing characters
x: str = text.strip('chars')   # Strip both ends

import stringzilla as sz
x: bytes = sz.random(length=100, seed=42, alphabet='ACGT')
sz.fill_random(buffer, seed=42, alphabet=None)  # Fill mutable buffer
```

### Look-Up Table Transforms

```python
x: str = text.translate('chars', {}, start=0, end=sys.maxsize, inplace=False)
x: bytes = text.translate(b'chars', {}, start=0, end=sys.maxsize, inplace=False)
```

Pass the LUT as a string or bytes object (not a dictionary) for efficiency. Useful in high-throughput binary data processing including bioinformatics and image processing:

```python
import stringzilla as sz
look_up_table = bytes(range(256))  # Identity LUT
image = open("/image/path.jpeg", "rb").read()
sz.translate(image, look_up_table, inplace=True)
```

### Low-Level API

Global functions work directly on `str` and `bytes`:

```python
import stringzilla as sz
import sys

contains: bool = sz.contains("haystack", "needle", start=0, end=sys.maxsize)
offset: int = sz.find("haystack", "needle", start=0, end=sys.maxsize)
count: int = sz.count("haystack", "needle", start=0, end=sys.maxsize, allowoverlap=False)
```

## Hash

Single-shot and incremental hashing with stable 64-bit output across all platforms:

```python
import stringzilla as sz

# One-shot
one = sz.hash(b"Hello, world!", seed=42)

# Incremental — digest does not consume state
hasher = sz.Hasher(seed=42)
hasher.update(b"Hello, ").update(b"world!")
streamed = hasher.digest()       # or `hexdigest()` for string
assert one == streamed
```

## SHA-256 Checksums

```python
import stringzilla as sz

# One-shot SHA-256
digest_bytes = sz.sha256(b"Hello, world!")
assert len(digest_bytes) == 32

# Incremental SHA-256
hasher = sz.Sha256()
hasher.update(b"Hello, ").update(b"world!")
digest_bytes = hasher.digest()
digest_hex = hasher.hexdigest()  # 64 character lowercase hex string

# HMAC-SHA256 for message authentication
mac = sz.hmac_sha256(key=b"secret", message=b"Hello, world!")
```

### Memory-Mapped File Checksums

StringZilla simplifies large file checksums with memory mapping:

```python
from stringzilla import Sha256, File

mapped_file = File("xlsum.csv")
checksum = Sha256().update(mapped_file).hexdigest()
```

This avoids file I/O overhead and Python abstraction layers — 3x faster than `hashlib.sha256` for end-to-end processing.

## Unicode Case-Folding and Case-Insensitive Search

Covers over 1M+ Unicode codepoints with full expansion support:

```python
import stringzilla as sz

sz.utf8_case_fold('HELLO')       # b'hello'
sz.utf8_case_fold('Straße')      # b'strasse' — ß (1 char) → "ss" (2 chars)
sz.utf8_case_fold('eﬃcient')    # b'efficient' — ﬃ ligature (1 char) → "ffi" (3 chars)
```

Case-insensitive search returns byte offset, handling expansions correctly:

```python
sz.utf8_case_insensitive_find('Der große Hund', 'GROSSE')   # 4
sz.utf8_case_insensitive_find('Straße', 'STRASSE')          # 0
sz.utf8_case_insensitive_find('eﬃcient', 'EFFICIENT')       # 0

# Iterator for finding ALL matches
haystack = 'Straße STRASSE strasse'
for match in sz.utf8_case_insensitive_find_iter(haystack, 'strasse'):
    print(match, match.offset_within(haystack))

# With overlapping matches
list(sz.utf8_case_insensitive_find_iter('aaaa', 'aa'))                      # 2 non-overlapping
list(sz.utf8_case_insensitive_find_iter('aaaa', 'aa', include_overlapping=True))  # 3 matches
```

## Collection-Level Operations (Strs)

Once split into a `Strs` object, sort, shuffle, and reorganize with minimal memory footprint — as low as 4 bytes per chunk when strings are in consecutive memory:

```python
lines: Strs = text.split(separator='\n')  # 4 bytes/line overhead under 4 GB
batch: Strs = lines.sample(seed=42)       # 10x faster than random.choices
lines_shuffled: Strs = lines.shuffled(seed=42)
lines_sorted: Strs = lines.sorted()
order: tuple = lines.argsort()            # similar to numpy.argsort
```

Slicing supports navigation and sharding:

```python
lines[::3]      # every third line
lines[1::1]     # every odd line
lines[:-100:-1] # last 100 lines in reverse order
```

## Lazy Iterators

Save memory with lazily evaluated iterators instead of materializing full lists:

```python
x = text.split_iter(separator=' ', keepseparator=False)
x = text.rsplit_iter(separator=' ', keepseparator=False)
x = text.split_byteset_iter(separator='chars', keepseparator=False)
x = text.rsplit_byteset_iter(separator='chars', keepseparator=False)
```

Memory comparison for 1 GB text (mean word length 7.73 bytes):

- `text.split()`: increment 8670.12 MiB
- `sz.split(text)`: increment 530.75 MiB
- `sum(1 for _ in sz.split_iter(text))`: increment 0.00 MiB

## Similarity Scores (StringZillas)

Batch-oriented similarity via the `stringzillas` module with `DeviceScope` for hardware selection:

```python
import stringzilla as sz
import stringzillas as szs

cpu_scope = szs.DeviceScope(cpu_cores=4)    # force CPU-only
gpu_scope = szs.DeviceScope(gpu_device=0)   # pick GPU 0

strings_a = sz.Strs(["kitten", "flaw"])
strings_b = sz.Strs(["sitting", "lawn"])

engine = szs.LevenshteinDistances(
    match=0, mismatch=2,
    open=3, extend=1,
    capabilities=("serial",)  # avoid SIMD if desired
)
distances = engine(strings_a, strings_b, device=cpu_scope)
assert int(distances[0]) == 3 and int(distances[1]) == 2
```

For UTF-8 codepoint-level distances:

```python
engine = szs.LevenshteinDistancesUTF8(capabilities=("serial",))
distances = engine(sz.Strs(["café", "αβγδ"]), sz.Strs(["cafe", "αγδ"]), device=cpu_scope)
assert int(distances[0]) == 1 and int(distances[1]) == 1
```

Needleman-Wunsch alignment with substitution matrix:

```python
import numpy as np

substitution_matrix = np.zeros((256, 256), dtype=np.int8)
substitution_matrix.fill(-1)                # mismatch score
np.fill_diagonal(substitution_matrix, 0)    # match score

engine = szs.NeedlemanWunsch(substitution_matrix=substitution_matrix, open=1, extend=1)
scores = engine(strings_a, strings_b, device=cpu_scope)
```

Performance comparison for proteins ~10k chars, 100 pairs:

- JellyFish: 62.3s
- EditDistance: 32.9s
- StringZilla: 0.8s

## Rolling Fingerprints

MinHashing for compact document representations:

```python
import numpy as np
import stringzilla as sz
import stringzillas as szs

texts = sz.Strs([
    "quick brown fox jumps over the lazy dog",
    "quick brown fox jumped over a very lazy dog",
])

cpu = szs.DeviceScope(cpu_cores=4)
ndim = 1024
window_widths = np.array([4, 6, 8, 10], dtype=np.uint64)
engine = szs.Fingerprints(
    ndim=ndim,
    window_widths=window_widths,
    alphabet_size=256,
    capabilities=("serial",),
)

hashes, counts = engine(texts, device=cpu)
assert hashes.shape == (len(texts), ndim)
assert hashes.dtype == np.uint32 and counts.dtype == np.uint32
```

## Serialization

### Filesystem

```python
web_archive = Str("<html>...</html><html>...</html>")
_, end_tag, next_doc = web_archive.partition("</html>")
next_doc_offset = next_doc.offset_within(web_archive)
web_archive.write_to("next_doc.html")  # no GIL, no copies
```

### PyArrow

Zero-copy conversion to PyArrow buffers:

```python
from pyarrow import foreign_buffer
from stringzilla import Strs

strs = Strs(["alpha", "beta", "gamma"])
arrow = foreign_buffer(strs.address, strs.nbytes, strs)
```

## Dynamic Backend Control

```python
import stringzilla as sz

sz.reset_capabilities(('serial',))          # Force SWAR backend
sz.reset_capabilities(('haswell',))         # Force AVX2 backend
sz.reset_capabilities(('neon',))            # Force NEON backend
sz.reset_capabilities(sz.__capabilities__)  # Reset to auto-dispatch
```
