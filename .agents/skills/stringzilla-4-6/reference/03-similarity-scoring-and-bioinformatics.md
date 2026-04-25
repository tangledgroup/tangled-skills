# Similarity Scoring and Bioinformatics

Compute edit distances and alignment scores at scale:

```python
import stringzilla as sz
import stringzillas as szs
import numpy as np

# Levenshtein edit distance (byte-level)
strings_a = sz.Strs(["kitten", "flaw"])
strings_b = sz.Strs(["sitting", "lawn"])

cpu_scope = szs.DeviceScope(cpu_cores=4)  # Use 4 CPU cores

engine = szs.LevenshteinDistances(
    match=0, mismatch=2,   # Custom costs
    open=3, extend=1,      # Gap penalties (for bioinformatics)
    capabilities=("serial",)  # Or omit for auto-detection
)

distances = engine(strings_a, strings_b, device=cpu_scope)
print(distances)  # [3, 2] — kitten→sitting=3 edits, flaw→lawn=2 edits

# UTF-8 codepoint-level distances (for Unicode text)
strings_unicode_a = sz.Strs(["café", "αβγδ"])
strings_unicode_b = sz.Strs(["cafe", "αγδ"])
engine_utf8 = szs.LevenshteinDistancesUTF8(capabilities=("serial",))
distances_utf8 = engine_utf8(strings_unicode_a, strings_unicode_b, device=cpu_scope)
print(distances_utf8)  # [1, 1]

# Needleman-Wunsch alignment scoring with substitution matrix
substitution_matrix = np.zeros((256, 256), dtype=np.int8)
substitution_matrix.fill(-1)                # Mismatch penalty
np.fill_diagonal(substitution_matrix, 0)    # Match score

engine_nw = szs.NeedlemanWunsch(
    substitution_matrix=substitution_matrix,
    open=1, extend=1
)

scores = engine_nw(strings_a, strings_b, device=cpu_scope)
print(scores)  # Alignment scores
```

### BioPython Integration Example

Convert BioPython alignment matrices to StringZilla format:

```python
import numpy as np
from Bio import Align
from Bio.Align import substitution_matrices
import stringzillas as szs

# Original BioPython setup
aligner = Align.PairwiseAligner()
aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
aligner.open_gap_score = 1
aligner.extend_gap_score = 1

# Convert matrix to NumPy array
subs_packed = np.array(aligner.substitution_matrix).astype(np.int8)
subs_reconstructed = np.full((256, 256), 127, dtype=np.int8)  # Max penalty for invalid chars

for row_idx, row_aa in enumerate(aligner.substitution_matrix.alphabet):
    for col_idx, col_aa in enumerate(aligner.substitution_matrix.alphabet):
        subs_reconstructed[ord(row_aa), ord(col_aa)] = subs_packed[row_idx, col_idx]

# Compare results
glutathione = "ECG"
trh = "QHP"  # Thyrotropin-releasing hormone

score_biopython = aligner.score(glutathione, trh)

engine = szs.NeedlemanWunsch(substitution_matrix=subs_reconstructed, open=1, extend=1)
score_stringzilla = int(engine(sz.Strs([glutathione]), sz.Strs([trh]))[0])

assert score_biopython == score_stringzilla  # Both equal 6
# StringZilla: 7.8s vs BioPython: 25.8s for 100 pairs of 10k-char proteins
```

### Rolling Fingerprints (MinHash)

Generate compact document fingerprints for similarity detection:

```python
import numpy as np
import stringzilla as sz
import stringzillas as szs

texts = sz.Strs([
    "quick brown fox jumps over the lazy dog",
    "quick brown fox jumped over a very lazy dog",
])

cpu = szs.DeviceScope(cpu_cores=4)
ndim = 1024  # Fingerprint dimensionality
window_widths = np.array([4, 6, 8, 10], dtype=np.uint64)

engine = szs.Fingerprints(
    ndim=ndim,
    window_widths=window_widths,    # Optional n-gram windows
    alphabet_size=256,              # Default for byte strings
    capabilities=("serial",),
)

hashes, counts = engine(texts, device=cpu)

print(hashes.shape)  # (2, 1024) — 2 documents, 1024-dim fingerprints
print(counts.shape)  # (2, 1024) — Hash collision counts
print(hashes.dtype)  # uint32
```
