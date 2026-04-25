# Multi-Language Bindings

> **Source:** https://github.com/unum-cloud/usearch
> **Loaded from:** SKILL.md (via progressive disclosure)

## Supported Languages

USearch provides native bindings for: C++11, Python 3, C99, Java, JavaScript/Node.js, Rust, Go, Swift, C#, Wolfram, Objective-C. All bindings share the same core engine and file format (`.usearch`).

## Feature Matrix

| Feature | C++ | Python | C | Java | JS | Rust | Go | Swift |
|---------|-----|--------|---|------|----|----|----|-------|
| Add, search, remove | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Save, load, view | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| User-defined metrics | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Batch operations | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Filter predicates | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Joins | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Variable-length vectors | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 4B+ capacities | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## C++

### Installation

Copy `include/usearch/*` headers or use CMake FetchContent:

```cmake
FetchContent_Declare(usearch GIT_REPOSITORY https://github.com/unum-cloud/USearch.git)
FetchContent_MakeAvailable(usearch)
```

### Quickstart

```cpp
#include <usearch/index.hpp>
#include <usearch/index_dense.hpp>

using namespace unum::usearch;

metric_punned_t metric(3, metric_kind_t::l2sq_k, scalar_kind_t::f32_k);
index_dense_t index = index_dense_t::make(metric);
float vec[3] = {0.1, 0.3, 0.2};

index.reserve(10);
index.add(42, &vec[0]);
auto results = index.search(&vec[0], 5);

for (std::size_t i = 0; i != results.size(); ++i)
    std::printf("Found: %zu\n", results[i].member.key);
```

### Parallel Indexing

```cpp
#pragma omp parallel for
for (std::size_t i = 0; i < n; ++i)
    native.add(key, span_t{vector, dims});
```

### Error Handling

USearch uses result objects instead of exceptions:

```cpp
bool success = (bool)index.try_reserve(10);
success = (bool)index.add(42, &vec[0]);
success = (bool)index.search(&vec[0], 5);
```

### Low-Level Template Interface

```cpp
template <
    typename distance_at = default_distance_t,        // float
    typename key_at = default_key_t,                  // int64_t, uuid_t
    typename compressed_slot_at = default_slot_t,     // uint32_t, uint40_t
    typename dynamic_allocator_at = std::allocator<byte_t>,
    typename tape_allocator_at = dynamic_allocator_at>
class index_gt;
```

## C99

### Quickstart

```c
#include <usearch/usearch.h>

usearch_init_options_t opts = {
    .metric_kind = usearch_metric_cos_k,
    .scalar_kind = usearch_scalar_f16_k,
    .dimensions = 128,
    .expansion_add = 0,
    .expansion_search = 0
};
usearch_error_t error = NULL;
usearch_index_t index = usearch_init(&opts, &error);

usearch_reserve(index, 1000, &error);
float vector[128]; // fill with data
usearch_add(index, 42, &vector[0], usearch_scalar_f32_k, &error);

usearch_key_t found_keys[10];
usearch_distance_t found_distances[10];
size_t found_count = usearch_search(
    index, &vector[0], usearch_scalar_f32_k, 10,
    &found_keys[0], &found_distances[0], &error);

usearch_free(index, &error);
```

### Buffer Serialization

```c
size_t bytes = usearch_serialized_length(index, &error);
void* buffer = malloc(bytes);
usearch_save_buffer(index, buffer, bytes, &error);
usearch_load_buffer(index, buffer, bytes, &error);
usearch_view_buffer(index, buffer, bytes, &error);

// Metadata from file or buffer
usearch_init_options_t opts;
usearch_metadata("index.usearch", &opts, &error);
usearch_metadata_buffer(buffer, bytes, &opts, &error);
```

## Java

### Installation (Gradle)

Maven Central is not supported. Download fat JAR from GitHub releases:

```groovy
repositories {
    mavenCentral()
    flatDir { dirs 'lib' }
}

task downloadUSearchJar {
    doLast {
        def usearchVersion = '2.25.1'
        def usearchUrl = "https://github.com/unum-cloud/USearch/releases/download/v${usearchVersion}/usearch-${usearchVersion}.jar"
        def usearchFile = file("lib/usearch-${usearchVersion}.jar")
        usearchFile.parentFile.mkdirs()
        if (!usearchFile.exists()) {
            new URL(usearchUrl).withInputStream { i ->
                usearchFile.withOutputStream { it << i }
            }
        }
    }
}

compileJava.dependsOn downloadUSearchJar

dependencies {
    implementation name: 'usearch', version: '2.25.1', ext: 'jar'
}
```

### Quickstart

```java
import cloud.unum.usearch.Index;

try (Index index = new Index.Config()
        .metric(Index.Metric.COSINE)
        .quantization(Index.Quantization.FLOAT32)
        .dimensions(3)
        .capacity(100)
        .build()) {

    float[] vector = {0.1f, 0.2f, 0.3f};
    index.add(42L, vector);

    long[] keys = index.search(new float[]{0.1f, 0.2f, 0.3f}, 10);
    for (long key : keys) {
        System.out.println("Found key: " + key);
    }
}
```

### Batch Operations

```java
// Batch add: 3 vectors in one call
float[] batchVectors = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f};
index.add(100L, batchVectors); // Keys 100, 101, 102
```

### Concurrent Operations

```java
ExecutorService executor = Executors.newFixedThreadPool(8);
CompletableFuture<Void>[] tasks = new CompletableFuture[4];
for (int t = 0; t < 4; t++) {
    final int threadId = t;
    tasks[t] = CompletableFuture.runAsync(() -> {
        for (int i = 0; i < 1000; i++) {
            long key = threadId * 1000L + i;
            float[] vector = generateRandomVector(4);
            index.add(key, vector);
        }
    }, executor);
}
CompletableFuture.allOf(tasks).join();
```

## Go

### Installation

```sh
go get github.com/unum-cloud/usearch/golang
```

Native library required — download from GitHub releases for Linux (`.deb`), macOS (`.zip`), or Windows (`winlibinstaller.bat`).

### Quickstart

```go
package main

import (
    "fmt"
    usearch "github.com/unum-cloud/usearch/golang"
)

func main() {
    conf := usearch.DefaultConfig(3)
    conf.Quantization = usearch.F32
    index, err := usearch.NewIndex(conf)
    if err != nil { panic(err) }
    defer index.Destroy()

    err = index.Reserve(100)
    for i := 0; i < 100; i++ {
        err = index.Add(usearch.Key(i), []float32{float32(i), float32(i+1), float32(i+2)})
    }

    keys, distances, err := index.Search([]float32{0, 1, 2}, 3)
    fmt.Println(keys, distances)
}
```

### Concurrency

```go
index.ChangeThreadsAdd(8)
index.ChangeThreadsSearch(16)

var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        keys, distances, _ := index.Search(queryVector, 10)
    }()
}
wg.Wait()
```

## Python Batch Operations

```python
n = 100
keys = np.arange(n)
vectors = np.random.uniform(0, 0.3, (n, index.ndim)).astype(np.float32)

index.add(keys, vectors, threads=0, copy=True)
matches: BatchMatches = index.search(vectors, 10, threads=0)

# Access individual results
first_matches = matches[0]
print(first_matches.key, first_matches.distance)

# Check counts for valid results
print(matches.counts)  # Number of valid results per query
```

## JavaScript Batch Operations

```js
const keys = new BigUint64Array([15n, 16n]);
const vectors = new Float32Array([10, 20, 10, 25]);
index.add(keys, vectors);

const batchResults = index.search(vectors, 2, 0); // 0 threads = auto
const firstMatch = batchResults.get(0);
```

## Serialization Across Languages

All bindings use the same `.usearch` binary format, enabling cross-language interoperability:

```python
# Build in Python
index.save('shared.usearch')
```

```rust
// Load in Rust
let index = Index::load("shared.usearch").unwrap();
```

```js
// View in JavaScript
const index = new usearch.Index();
index.view('shared.usearch');
```

## Performance Tuning (All Languages)

```python
# Check hardware acceleration
print(index.hardware_acceleration)  # CPU codename (e.g. 'sapphire')

# Check memory usage
print(index.memory_usage)  # bytes

# Tune expansion parameters
index.change_expansion_add(32)
index.change_expansion_search(32)
```
