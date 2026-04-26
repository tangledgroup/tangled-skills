# C/C++ API

## C99 Interface

All functions are prefixed with `sz_`. The library is header-only — include `<stringzilla/stringzilla.h>`.

```c
#include <stringzilla/stringzilla.h>

// String views (not necessarily null-terminated)
sz_string_view_t haystack = {your_text, your_text_length};
sz_string_view_t needle = {your_subtext, your_subtext_length};

// Substring search — auto-picks backend
sz_cptr_t ptr = sz_find(haystack.start, haystack.length, needle.start, needle.length);
sz_size_t pos = ptr ? (sz_size_t)(ptr - haystack.start) : SZ_SIZE_MAX;

// Backend-specific variants
sz_cptr_t ptr = sz_find_skylake(haystack.start, haystack.length, needle.start, needle.length);
sz_cptr_t ptr = sz_find_haswell(haystack.start, haystack.length, needle.start, needle.length);
sz_cptr_t ptr = sz_find_westmere(haystack.start, haystack.length, needle.start, needle.length);
sz_cptr_t ptr = sz_find_neon(haystack.start, haystack.length, needle.start, needle.length);

// Hashing
sz_u64_t hash = sz_hash(haystack.start, haystack.length, 42);
sz_u64_t checksum = sz_bytesum(haystack.start, haystack.length);

// Incremental hashing
sz_hash_state_t state;
sz_hash_state_init(&state, 42);
sz_hash_state_update(&state, haystack.start, 1);
sz_hash_state_update(&state, haystack.start + 1, haystack.length - 1);
sz_u64_t streamed_hash = sz_hash_state_digest(&state);

// SHA-256
sz_u8_t digest[32];
sz_sha256_state_t sha_state;
sz_sha256_state_init(&sha_state);
sz_sha256_state_update(&sha_state, haystack.start, haystack.length);
sz_sha256_state_digest(&sha_state, digest);

// Collection-level argsort
sz_sequence_t array = {your_handle, your_count, your_get_start, your_get_length};
sz_sorted_idx_t order[your_count];
sz_sequence_argsort(&array, NULL, order);
```

### LibC to StringZilla Mapping

Key differences from LibC: all strings have explicit length (not null-terminated), and every operation has a reverse-order counterpart.

- `memchr` / `strchr` → `sz_find_byte(haystack, haystack_length, needle)`
- `memrchr` → `sz_rfind_byte(haystack, haystack_length, needle)`
- `memcmp` / `strcmp` → `sz_order`, `sz_equal`
- `strlen` → `sz_find_byte(haystack, haystack_length, 0)`
- `strcspn` → `sz_find_byteset(haystack, haystack_length, reject_bitset)`
- `strspn` → `sz_find_byte_not_from(haystack, haystack_length, accept, accept_length)`
- `memmem` / `strstr` → `sz_find(haystack, haystack_length, needle, needle_length)`
- `memcpy` → `sz_copy(destination, source, destination_length)`
- `memmove` → `sz_move(destination, source, destination_length)`
- `memset` → `sz_fill(destination, destination_length, value)`

## C++11 Interface

Available in the `ashvardanian::stringzilla` namespace with two STL-like classes:

- `sz::string_view` — non-owning view of a string
- `sz::string` — mutable string with Small String Optimization (SSO)

```cpp
#include <stringzilla/stringzilla.hpp>

namespace sz = ashvardanian::stringzilla;

sz::string haystack = "some string";
sz::string_view needle = sz::string_view(haystack).substr(0, 4);

auto substring_position = haystack.find(needle);   // Or `rfind`
auto hash = std::hash<sz::string_view>{}(haystack); // STL-compatible

haystack.end() - haystack.begin() == haystack.size();
haystack.find_first_of(" \v\t") == 4;
haystack.starts_with(needle) == true;
haystack.ends_with(needle);
haystack.remove_prefix(needle.size());
haystack.contains(needle) == true;
haystack.compare(needle) == 1;
// C++20: haystack <=> needle (three-way comparison)
```

### String Literals

```cpp
using sz::literals::operator""_sv;
using std::literals::operator""sv;

auto a = "some string";    // char const *
auto b = "some string"sv;  // std::string_view
auto c = "some string"_sv; // sz::string_view
```

### Sorting

```cpp
std::vector<std::string> data({"c", "b", "a"});
std::vector<std::size_t> order = sz::argsort(data);

// With custom accessor:
sz::argsort(data.begin(), data.end(), order.data(),
    [](auto const &x) -> sz::string_view { return x; });
```

### Accelerating STL Containers

Override default comparator and hash for `std::string` keys:

```cpp
std::map<std::string, int, sz::less> sorted_words;
std::unordered_map<std::string, int, sz::hash, sz::equal_to> words;
```

Or use `sz::string` directly for better performance with short keys:

```cpp
std::map<sz::string, int> sorted_words;
std::unordered_map<sz::string, int> words;
```

### String Replace and Lookup

```cpp
haystack.replace_all(needle_string, replacement_string);
haystack.replace_all(sz::byteset(""), replacement_string);
haystack.try_replace_all(needle_string, replacement_string);
haystack.lookup(sz::look_up_table::identity());
haystack.lookup(sz::look_up_table::identity(), haystack.data());
```

## Compilation Flags

| Flag | Description |
|------|-------------|
| `SZ_DEBUG` | Enable aggressive bounds-checking (inferred from build type if not set) |
| `SZ_USE_GOLDMONT` / `SZ_USE_WESTMERE` / `SZ_USE_HASWELL` / `SZ_USE_SKYLAKE` / `SZ_USE_ICE` | Explicitly disable x86 SIMD families |
| `SZ_USE_NEON` / `SZ_USE_NEON_AES` / `SZ_USE_NEON_SHA` / `SZ_USE_SVE` / `SZ_USE_SVE2` / `SZ_USE_SVE2_AES` | Explicitly disable ARM SIMD families |
| `SZ_ENFORCE_SVE_OVER_NEON` | Force SVE everywhere when both available (default: selective) |
| `SZ_DYNAMIC_DISPATCH` | Pre-compile for all generations, dispatch at runtime (produces `.so`) |
| `SZ_USE_MISALIGNED_LOADS` | Enable unaligned loads (default: enabled on x86, disabled elsewhere) |
| `SZ_AVOID_LIBC` | Disable LibC usage in header-only mode |
| `SZ_OVERRIDE_LIBC` | Override `memcpy`/`memset` with StringZilla implementations (use with `LD_PRELOAD`) |
| `SZ_AVOID_STL` | Disable implicit conversions from/to `std::string` |
| `SZ_SAFETY_OVER_COMPATIBILITY` | Disable error-prone overloads for safer API |
| `STRINGZILLA_BUILD_SHARED` / `BUILD_TEST` / `BUILD_BENCHMARK` | CMake build options |
| `STRINGZILLA_TARGET_ARCH` | Synonymous to GCC `-march`, controls instruction sets |

## Dynamic Dispatch

Auto-detects best backend. Manual selection for guaranteed performance:

```c
sz_find(text, length, pattern, 3);           // Auto-dispatch
sz_find_westmere(text, length, pattern, 3);  // Intel Westmere+ SSE4.2
sz_find_haswell(text, length, pattern, 3);   // Intel Haswell+ AVX2
sz_find_skylake(text, length, pattern, 3);   // Intel Skylake+ AVX-512
sz_find_neon(text, length, pattern, 3);      // Arm NEON 128-bit
sz_find_sve(text, length, pattern, 3);       // Arm SVE variable width
```

Backend names use Intel and ARM CPU generation naming. StringZilla automatically picks the most advanced backend for the given CPU at runtime.

## CUDA Support

Parallel GPU algorithms available via `<stringzillas/stringzillas.cuh>` in CUDA C++ 17. Compile-time flags `SZ_USE_CUDA`, `SZ_USE_KEPLER`, `SZ_USE_HOPPER` control PTX instruction families.
