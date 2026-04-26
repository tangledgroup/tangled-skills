# Rust API

## Quick Start

```toml
[dependencies]
stringzilla = ">=3"                                      # serial algorithms
stringzilla = { version = ">=3", features = ["cpus"] }   # parallel multi-CPU
stringzilla = { version = ">=3", features = ["cuda"] }   # parallel GPU
```

Check installed version and capabilities:

```bash
cargo add stringzilla
cargo run --example version
```

## Core Functions

Interfaces familiar to `memchr` crate users:

```rust
use stringzilla::sz;

// Substring search — identical to memchr::memmem::find / rfind
sz::find("Hello, world!", "world")       // 7
sz::rfind("Hello, world!", "world")      // 7

// Character set search — generalizes memchr::memrchr[123]
sz::find_byte_from("Hello, world!", "world")     // 2
sz::rfind_byte_from("Hello, world!", "world")    // 11
```

No constraint on character set size (unlike `memchr` which allows only 1, 2, or 3 characters).

## StringZilla Extension Trait

```rust
use stringzilla::StringZilla;

let my_string = String::from("Hello, world!");
let my_str = my_string.as_str();
let my_cow_str = Cow::from(&my_string);

// Works with String, &str, and Cow<'_, str>
assert_eq!(my_string.sz_find("world"), Some(7));
assert_eq!(my_string.sz_rfind("world"), Some(7));
assert_eq!(my_string.sz_find_byte_from("world"), Some(2));
assert_eq!(my_string.sz_rfind_byte_from("world"), Some(11));
assert_eq!(my_string.sz_find_byte_not_from("world"), Some(0));
assert_eq!(my_string.sz_rfind_byte_not_from("world"), Some(12));
```

## Hash

Single-shot and incremental hashing:

```rust
let mut hasher = sz::Hasher::new(42);
hasher.write(b"Hello, ");
hasher.write(b"world!");
let streamed = hasher.finish();

let mut hasher = sz::Hasher::new(42);
hasher.write(b"Hello, world!");
assert_eq!(streamed, hasher.finish());
```

Integration with `std::collections`:

```rust
use std::collections::HashMap;
let mut map: HashMap<&str, i32, sz::BuildSzHasher> =
    HashMap::with_hasher(sz::BuildSzHasher::with_seed(42));
map.insert("a", 1);
assert_eq!(map.get("a"), Some(&1));
```

## SHA-256 Checksums

```rust
use stringzilla::sz;

// One-shot SHA-256
let digest = sz::Sha256::hash(b"Hello, world!");
assert_eq!(digest.len(), 32);

// Incremental SHA-256
let mut hasher = sz::Sha256::new();
hasher.update(b"Hello, ");
hasher.update(b"world!");
let digest = hasher.digest();

// HMAC-SHA256
let mac = sz::hmac_sha256(b"secret", b"Hello, world!");
```

## Unicode Case-Folding and Case-Insensitive Search

Output buffer must be at least 3x input length for worst-case expansion:

```rust
use stringzilla::stringzilla as sz;

let source = "Straße";
let mut dest = [0u8; 64];
let len = sz::utf8_case_fold(source, &mut dest);
assert_eq!(&dest[..len], b"strasse");
```

Case-insensitive search returns `Some((offset, matched_length))` or `None`:

```rust
use stringzilla::stringzilla::{utf8_case_insensitive_find, Utf8CaseInsensitiveNeedle};

// Single search
if let Some((offset, len)) = utf8_case_insensitive_find("Straße", "STRASSE") {
    assert_eq!(offset, 0);
    assert_eq!(len, 7);  // "Straße" is 7 bytes
}

// Repeated searches with pre-compiled needle
let needle = Utf8CaseInsensitiveNeedle::new(b"STRASSE");
for haystack in &["Straße", "STRASSE", "strasse"] {
    if let Some((offset, len)) = utf8_case_insensitive_find(haystack, &needle) {
        println!("Found at byte {} with length {}", offset, len);
    }
}
```

## Similarity Scores (StringZillas)

Via the `szs` module with `DeviceScope` for hardware selection:

```rust
use stringzilla::szs;

let cpu_scope = szs::DeviceScope::cpu_cores(4).unwrap();
let gpu_scope = szs::DeviceScope::gpu_device(0).unwrap();
let strings_a = vec!["kitten", "flaw"];
let strings_b = vec!["sitting", "lawn"];

let engine = szs::LevenshteinDistances::new(
    &cpu_scope, 0, 2, 3, 1  // match, mismatch, open, extend costs
).unwrap();
let distances = engine.compute(&cpu_scope, &strings_a, &strings_b).unwrap();
assert_eq!(distances[0], 3);
assert_eq!(distances[1], 2);
```

UTF-8 codepoint-level distances:

```rust
let engine = szs::LevenshteinDistancesUtf8::new(&cpu_scope, 0, 1, 1, 1).unwrap();
let distances = engine.compute(&cpu_scope, &vec!["café", "αβγδ"], &vec!["cafe", "αγδ"]).unwrap();
assert_eq!(distances, vec![1, 1]);
```

Needleman-Wunsch with substitution matrix:

```rust
let mut substitution_matrix = [-1i8; 256 * 256];
for i in 0..256 { substitution_matrix[i * 256 + i] = 0; }
let engine = szs::NeedlemanWunschScores::new(&cpu_scope, &substitution_matrix, -3, -1).unwrap();
let scores = engine.compute(&cpu_scope, &strings_a, &strings_b).unwrap();
```

Smith-Waterman for local alignment:

```rust
let engine = szs::SmithWatermanScores::new(&cpu_scope, &substitution_matrix, -3, -1).unwrap();
let local_scores = engine.compute(&cpu_scope, &strings_a, &strings_b).unwrap();
```

### Zero-Copy with StringTape

For high-performance applications, use the `StringTape` crate:

```rust
use stringzilla::{szs, StringTape};

let tape_a = StringTape::from_strings(&["kitten", "sitting", "flaw"]);
let tape_b = StringTape::from_strings(&["sitting", "kitten", "lawn"]);

let mut distances = szs::UnifiedVec::<u32>::from_elem(u32::MAX, tape_a.len());

let engine = szs::LevenshteinDistances::new(&gpu_scope, 0, 1, 1, 1).unwrap();
engine.compute_into(&gpu_scope, &tape_a, &tape_b, &mut distances).unwrap();

assert_eq!(distances[0], 3);  // kitten -> sitting
assert_eq!(distances[1], 3);  // sitting -> kitten
assert_eq!(distances[2], 2);  // flaw -> lawn
```

## Rolling Fingerprints

MinHashing for compact document representations:

```rust
use stringzilla::szs;

let texts = vec![
    "quick brown fox jumps over the lazy dog",
    "quick brown fox jumped over a very lazy dog",
];
let cpu = szs::DeviceScope::cpu_cores(4).unwrap();
let ndim = 1024;
let window_widths = vec![4u64, 6, 8, 10];

let engine = szs::Fingerprints::new(ndim, &window_widths, 256, &cpu).unwrap();
let (hashes, counts) = engine.compute(&cpu, &texts).unwrap();
assert_eq!(hashes.len(), texts.len() * ndim);
```

Zero-copy with StringTape and unified memory:

```rust
use stringzilla::{szs, StringTape};

let tape = StringTape::from_strings(&[
    "quick brown fox jumps over the lazy dog",
    "quick brown fox jumped over a very lazy dog",
]);

let mut hashes = szs::UnifiedVec::<u32>::from_elem(u32::MAX, tape.len() * ndim);
let mut counts = szs::UnifiedVec::<u32>::from_elem(u32::MAX, tape.len() * ndim);

let engine = szs::Fingerprints::new(ndim, &window_widths, 256, &cpu).unwrap();
engine.compute_into(&cpu, &tape, &mut hashes, &mut counts).unwrap();
```
