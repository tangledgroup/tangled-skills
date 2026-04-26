# Other Languages

## Go

### Installation

Download precompiled binaries from [GitHub releases](https://github.com/unum-cloud/USearch/releases):

- **Linux**: `.deb` package
- **macOS**: `.zip` archive (move `libusearch_c.dylib` to `/usr/local/lib`, `usearch.h` to `/usr/local/include`)
- **Windows**: Run `winlibinstaller.bat` from the repository

```sh
go get github.com/unum-cloud/usearch/golang
```

### Quickstart

```go
package main

import (
    "fmt"
    usearch "github.com/unum-cloud/usearch/golang"
)

func main() {
    conf := usearch.DefaultConfig(uint(vectorSize))
    conf.Quantization = usearch.F32 // or BF16, F16, E5M2, E4M3, etc.
    index, err := usearch.NewIndex(conf)
    if err != nil { panic(err) }
    defer index.Destroy()

    err = index.Reserve(uint(vectorsCount))
    _ = index.ChangeThreadsAdd(uint(runtime.NumCPU()))
    _ = index.ChangeThreadsSearch(uint(runtime.NumCPU()))

    for i := 0; i < vectorsCount; i++ {
        err = index.Add(usearch.Key(i), []float32{float32(i), float32(i+1), float32(i+2)})
    }

    keys, distances, err := index.Search([]float32{0.0, 1.0, 2.0}, 3)
    fmt.Println(keys, distances)
}
```

### Filtered Search

```go
handler := &usearch.FilteredSearchHandler{
    Callback: func(key usearch.Key, handler *usearch.FilteredSearchHandler) int {
        if key % 2 == 0 { return 1 } // Accept
        return 0                      // Reject
    },
}
keys, distances, err := index.FilteredSearch(queryVector, 10, handler)
```

### Exact Search

```go
keys, distances, err := usearch.ExactSearch(
    dataset, queries,
    datasetSize, queryCount,
    vectorDims*4, vectorDims*4,  // Strides in bytes
    vectorDims, usearch.Cosine,
    maxResults, 0,  // 0 threads = auto-detect
)
```

### Index Operations

```go
dimensions, _ := index.Dimensions()
size, _ := index.Len()
capacity, _ := index.Capacity()
containsKey, _ := index.Contains(42)
count, _ := index.Count(42)
version := usearch.Version()

index.Remove(42)    // Remove a vector
index.Clear()       // Clear all vectors, preserve structure
index.Rename(oldKey, newKey)
```

## Java

### Installation

Download the fat JAR from GitHub releases (supports Linux, Windows, macOS, Android):

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

public class Main {
    public static void main(String[] args) {
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
    }
}
```

### Multiple Data Types

```java
// Double precision
try (Index index = new Index.Config()
        .metric("cos").dimensions(3).quantization("f64").build()) {
    double[] vector = {0.1, 0.2, 0.3};
    index.add(42L, vector);

    double[] buffer = new double[3];
    index.getInto(42L, buffer); // Memory-efficient retrieval
}

// Byte precision (i8)
try (Index index = new Index.Config()
        .metric("cos").dimensions(3).quantization("i8").build()) {
    byte[] vector = {10, 20, 30};
    index.add(42L, vector);
}
```

### Batch and Concurrent Operations

```java
// Batch add: 3 vectors in one call
float[] batchVectors = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f};
index.add(100L, batchVectors); // Keys: 100, 101, 102

// Concurrent operations
ExecutorService executor = Executors.newFixedThreadPool(8);
CompletableFuture<Void>[] tasks = new CompletableFuture[4];
for (int t = 0; t < 4; t++) {
    final int threadId = t;
    tasks[t] = CompletableFuture.runAsync(() -> {
        for (int i = 0; i < 1000; i++) {
            index.add(threadId * 1000L + i, generateRandomVector(4));
        }
    }, executor);
}
CompletableFuture.allOf(tasks).join();
```

## C

### Quickstart

```c
#include <usearch/usearch.h>

int main() {
    usearch_error_t error = NULL;
    usearch_init_options_t opts = {
        .metric_kind = usearch_metric_cos_k,
        .scalar_kind = usearch_scalar_f16_k,
        .dimensions = 128,
        .expansion_add = 0,
        .expansion_search = 0
    };
    usearch_index_t index = usearch_init(&opts, &error);

    usearch_reserve(index, 1000, &error);

    float vector[128];
    usearch_add(index, 42, &vector[0], usearch_scalar_f32_k, &error);

    usearch_key_t found_keys[10];
    usearch_distance_t found_distances[10];
    size_t found_count = usearch_search(
        index, &vector[0], usearch_scalar_f32_k, 10,
        &found_keys[0], &found_distances[0], &error);

    usearch_free(index, &error);
    return error ? 1 : 0;
}
```

### Serialization

```c
usearch_save(index, "index.usearch", &error);
usearch_load(index, "index.usearch", &error);
usearch_view(index, "index.usearch", &error);

// Buffer-based
size_t bytes = usearch_serialized_length(index, &error);
void* buffer = malloc(bytes);
usearch_save_buffer(index, buffer, bytes, &error);
usearch_load_buffer(index, buffer, bytes, &error);
usearch_view_buffer(index, buffer, bytes, &error);

// Metadata
usearch_init_options_t opts;
usearch_metadata("index.usearch", &opts, &error);
```

### User-Defined Metrics

```c
usearch_distance_t callback(void const* a, void const* b, void* state) {
    // Custom metric implementation
}

usearch_change_metric(index, callback, NULL, usearch_metric_unknown_k, &error);
usearch_change_metric_kind(index, usearch_metric_cos_k, &error); // Revert
```

### Filtering with Predicates

```c
int is_odd(usearch_key_t key, void* state) {
    return key % 2;
}

usearch_filtered_search(
    index, &query[0], usearch_scalar_f32_k, 10,
    &is_odd, NULL,
    &found_keys[0], &found_distances[0], &error);
```

### Exact Search

```c
// Single distance
usearch_distance_t dist = usearch_distance(
    &vec_a[0], &vec_b[0], usearch_scalar_f32_k, dimensions,
    usearch_metric_cos_k, &error);

// Batch exact search
usearch_exact_search(
    &dataset[0][0], dataset_count, dimensions * sizeof(nk_f16_t),
    &queries[0][0], queries_count, dimensions * sizeof(nk_f16_t),
    usearch_scalar_f16_k, top_k, threads,
    &result_keys[0][0], sizeof(usearch_key_t) * top_k,
    &result_distances[0][0], sizeof(usearch_distance_t) * top_k,
    &error);
```

## Language Feature Matrix

Feature availability varies by language binding:

- **Add/search/remove**: All languages (C++11, Python, C99, Java, JavaScript, Rust, Go, Swift)
- **Save/load/view**: All languages
- **User-defined metrics**: C++, Python, C, Rust
- **Batch operations**: Python, Java, JavaScript
- **Filter predicates**: C++, C, Rust, Go, Swift
- **Joins**: C++, Python
- **Variable-length vectors**: C++ only
- **4B+ capacities**: C++ only
