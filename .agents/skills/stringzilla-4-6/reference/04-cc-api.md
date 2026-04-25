# C/C++ API

### Basic C Usage (C99+)

```c
#include <stringzilla/stringzilla.h>

// Initialize string views (not necessarily null-terminated)
sz_string_view_t haystack = {your_text, your_text_length};
sz_string_view_t needle = {your_subtext, your_subtext_length};

// Substring search (auto-dispatch to best SIMD backend)
sz_cptr_t ptr = sz_find(haystack.start, haystack.length, needle.start, needle.length);
sz_size_t position = ptr ? (sz_size_t)(ptr - haystack.start) : SZ_SIZE_MAX;  // SZ_SIZE_MAX if not found

// Manual backend dispatch for specific CPU features
sz_cptr_t ptr_skylake = sz_find_skylake(haystack.start, haystack.length, needle.start, needle.length);
sz_cptr_t ptr_neon = sz_find_neon(haystack.start, haystack.length, needle.start, needle.length);

// Hashing
sz_u64_t hash = sz_hash(haystack.start, haystack.length, 42);  // Seed=42
sz_u64_t checksum = sz_bytesum(haystack.start, haystack.length);

// Incremental hashing
sz_hash_state_t state;
sz_hash_state_init(&state, 42);
sz_hash_state_update(&state, haystack.start, 1);  // First char
sz_hash_state_update(&state, haystack.start + 1, haystack.length - 1);  // Rest
sz_u64_t streamed_hash = sz_hash_state_digest(&state);

// SHA-256
sz_u8_t digest[32];
sz_sha256_state_t sha_state;
sz_sha256_state_init(&sha_state);
sz_sha256_state_update(&sha_state, haystack.start, haystack.length);
sz_sha256_state_digest(&sha_state, digest);

// Collection operations (sorting)
sz_sequence_t array = {your_handle, your_count, your_get_start, your_get_length};
sz_sorted_idx_t order[your_count];
sz_sequence_argsort(&array, NULL, order);  // NULL uses default allocator
```

### LibC to StringZilla Mapping

| LibC Function | StringZilla Equivalent |
|--------------|------------------------|
| `memchr(haystack, needle, len)` | `sz_find_byte(haystack, len, needle)` |
| `memrchr(haystack, needle, len)` | `sz_rfind_byte(haystack, len, needle)` |
| `strcmp`, `memcmp` | `sz_order`, `sz_equal` |
| `strlen(haystack)` | `sz_find_byte(haystack, len, '\0')` |
| `strcspn(haystack, reject)` | `sz_find_byteset(haystack, len, reject_bitset)` |
| `strspn(haystack, accept)` | `sz_find_byte_not_from(haystack, len, accept, accept_len)` |
| `strstr`, `memmem` | `sz_find(haystack, h_len, needle, n_len)` |
| `memcpy(dest, src, len)` | `sz_copy(dest, src, len)` |
| `memmove(dest, src, len)` | `sz_move(dest, src, len)` |
| `memset(dest, val, len)` | `sz_fill(dest, len, val)` |

### C++ API (C++11+)

```cpp
#include <stringzilla/stringzilla.hpp>

namespace sz = ashvardanian::stringzilla;

// String types with Small String Optimization (SSO)
sz::string haystack = "some string";
sz::string_view needle = sz::string_view(haystack).substr(0, 4);

// STL-like operations
auto position = haystack.find(needle);  // Or rfind, contains, starts_with, ends_with
auto hash = std::hash<sz::string_view>{}(haystack);  // Compatible with std::hash

// Iterators
haystack.begin(), haystack.end();  // Forward iterators
haystack.rbegin(), haystack.rend();  // Reverse iterators

// Character set operations
auto first_ws = haystack.find_first_of(" \v\t");  // Or find_last_of, find_first_not_of, find_last_not_of

// In-place modifications
haystack.remove_prefix(needle.size());  // Why is this in-place?!

// Comparison
haystack.compare(needle);  // Returns sz_ordering_t
haystack <=> needle;  // C++20 spaceship operator

// String literals for type resolution
using sz::literals::operator""_sv;
auto view = "some string"_sv;  // sz::string_view (not std::string_view)
```
