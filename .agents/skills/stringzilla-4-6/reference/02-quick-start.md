# Quick Start

### Python Basic Usage

StringZilla's `Str` class provides a `str`-like interface to byte arrays without copies:

```python
from stringzilla import Str, File

# Create from various sources (no copies, just views)
text_from_str = Str('some-string')
text_from_bytes = Str(b'some-array')
text_from_file = Str(File('large-file.txt'))  # Memory-mapped file

import numpy as np
alphabet_array = np.arange(ord("a"), ord("z"), dtype=np.uint8)
text_from_array = Str(memoryview(alphabet_array))
```

### Core Operations

```python
from stringzilla import Str

text = Str('The quick brown fox jumps over the lazy dog')

# Basic operations
len(text)                    # Length
text[42]                     # Indexing -> str
text[4:8]                    # Slicing -> Str
'quick' in text              # Substring check -> bool
hash(text)                   # Hashing -> int (stable 64-bit across platforms)
str(text)                    # Convert to Python str

# Advanced search operations
import sys
contains = text.contains('substring', start=0, end=sys.maxsize)
offset = text.find('fox', start=0, end=sys.maxsize)      # First occurrence
count = text.count('o', start=0, end=sys.maxsize)        # Non-overlapping count

# Splitting (memory-efficient vs Python's str.split)
lines = text.split(separator='\n', maxsplit=sys.maxsize, keepseparator=False)
words = text.split_byteset(separator=' \t\n', keepseparator=False)  # Character set split

# Reverse operations
last_fox = text.rfind('fox')
rsplit_lines = text.rsplit(separator='\n')
```

### Character Set Operations

StringZilla provides native character set operations without regex overhead:

```python
from stringzilla import Str

text = Str('hello   world\n\ntest')

# Find first/last occurrence of any character from a set
first_ws = text.find_first_of(' \t\n\r', start=0, end=sys.maxsize)
last_ws = text.find_last_of(' \t\n\r', start=0, end=sys.maxsize)
first_alnum = text.find_first_not_of(' \t\n', start=0, end=sys.maxsize)

# Split by character sets (much faster than re.split)
tokens = text.split_byteset(separator=' \t\n\r')
tokens_rev = text.rsplit_byteset(separator=' \t\n\r')

# Trimming
stripped = text.strip(' \t\n')      # Both ends
lstripped = text.lstrip(' \t\n')    # Leading only
rstripped = text.rstrip(' \t\n')    # Trailing only
```

### Hashing

Single-shot and incremental hashing with stable 64-bit output:

```python
import stringzilla as sz

# One-shot hash (stable across all platforms)
one_shot = sz.hash(b"Hello, world!", seed=42)

# Incremental hashing (streaming)
hasher = sz.Hasher(seed=42)
hasher.update(b"Hello, ").update(b"world!")
streamed = hasher.digest()  # Same as one_shot
hex_digest = hasher.hexdigest()

assert one_shot == streamed

# SHA-256 cryptographic checksums
digest_bytes = sz.sha256(b"Hello, world!")  # 32 bytes
assert len(digest_bytes) == 32

# Incremental SHA-256 (faster for large files)
hasher = sz.Sha256()
hasher.update(b"Hello, ").update(b"world!")
digest_bytes = hasher.digest()
digest_hex = hasher.hexdigest()  # 64-char lowercase hex string

# HMAC-SHA-256 for message authentication
mac = sz.hmac_sha256(key=b"secret", message=b"Hello, world!")
```

### Large File Processing with Memory Mapping

Process gigabyte-scale files without loading into RAM:

```python
from stringzilla import Sha256, File

# Traditional approach (slow, loads file into memory)
import hashlib
with open("xlsum.csv", "rb") as f:
    hasher = hashlib.sha256()
    while chunk := f.read(4096):
        hasher.update(chunk)
checksum_old = hasher.hexdigest()

# StringZilla approach (3x faster, memory-mapped)
mapped_file = File("xlsum.csv")
checksum_new = Sha256().update(mapped_file).hexdigest()

assert checksum_old == checksum_new  # Same result: 7278165ce01a4ac1e8806c97f32feae908036ca3d910f5177d2cf375e20aeae1
```

### Unicode Case-Folding and Case-Insensitive Search

Full Unicode support for 1M+ codepoints (not just ASCII):

```python
import stringzilla as sz

# Case-folding with character expansion (ß → ss, ﬃ → ffi)
sz.utf8_case_fold('HELLO')       # b'hello'
sz.utf8_case_fold('Straße')      # b'strasse' — ß expands to "ss"
sz.utf8_case_fold('eﬃcient')     # b'efficient' — ﬃ ligature expands to "ffi"

# Case-insensitive search (handles expansions correctly)
offset1 = sz.utf8_case_insensitive_find('Der große Hund', 'GROSSE')  # 4 — finds "große"
offset2 = sz.utf8_case_insensitive_find('Straße', 'STRASSE')         # 0 — ß matches "SS"
offset3 = sz.utf8_case_insensitive_find('eﬃcient', 'EFFICIENT')      # 0 — ﬃ matches "FFI"

# Find ALL matches with iterator
haystack = 'Straße STRASSE strasse'
for match in sz.utf8_case_insensitive_find_iter(haystack, 'strasse'):
    print(match, match.offset_within(haystack))  # Yields: 'Straße', 'STRASSE', 'strasse'

# With overlapping matches
matches = list(sz.utf8_case_insensitive_find_iter('aaaa', 'aa'))              # ['aa', 'aa'] — 2 non-overlapping
matches_overlap = list(sz.utf8_case_insensitive_find_iter('aaaa', 'aa', include_overlapping=True))  # 3 matches
```

### Memory-Efficient Collections and Iterators

Avoid materializing lists for large datasets:

```python
from stringzilla import Str, Strs

text = Str(open("enwik9.txt", "r").read())  # 1 GB file

# Python's split() creates a full list in memory (8670 MiB)
# words_python = text.split()  # DON'T DO THIS FOR LARGE FILES

# StringZilla Strs uses 4 bytes per chunk overhead (530 MiB for same data)
words = Sz.split(text)  # Memory-efficient collection

# Lazy iterators use virtually zero memory
word_count = sum(1 for _ in Sz.split_iter(text))  # 0.00 MiB increment

# Collection operations on Strs
lines: Strs = text.split(separator='\n')
batch: Strs = lines.sample(seed=42)           # 10x faster than random.choices
shuffled: Strs = lines.shuffled(seed=42)      # Shuffle all lines
sorted_lines: Strs = lines.sorted()           # Return new Strs in sorted order
order: tuple = lines.argsort()                # Like numpy.argsort

# Slice operations for sharding between workers
every_third = lines[::3]
odd_lines = lines[1::1]
last_100_reversed = lines[:-100:-1]
```

### String Transformation with Lookup Tables

High-throughput character mapping for binary data processing:

```python
import stringzilla as sz

# Create identity lookup table (256 bytes)
lut = bytes(range(256))

# Transform image data in-place (useful for bioinformatics, image processing)
image = open("/path/to/image.jpeg", "rb").read()
sz.translate(image, lut, inplace=True)

# Custom transformation: uppercase ASCII letters
lut_custom = bytes([ord('A') + (i - ord('a')) if 97 <= i <= 122 else i for i in range(256)])
text = Str('hello world')
transformed = text.translate(lut_custom, inplace=False)  # b'HELLO WORLD'
```

### Random String Generation

Fast random string generation from custom alphabets:

```python
import stringzilla as sz

# Generate random DNA sequence
dna = sz.random(length=1000, seed=42, alphabet='ACGT')
print(dna[:50])  # b'GATCGAATCT...

# Generate UUID-like hex string
hex_str = sz.random(length=36, seed=12345, alphabet='0123456789abcdef-')

# Fill mutable buffer in-place
buffer = bytearray(1024)
sz.fill_random(buffer, seed=42, alphabet=None)  # Random bytes (0-255)
```
