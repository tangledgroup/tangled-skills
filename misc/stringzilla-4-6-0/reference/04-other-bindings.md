# Other Bindings

## JavaScript (Node.js)

Install via npm, uses zero-copy `Buffer` APIs. Returns `BigInt` offsets:

```bash
npm install stringzilla
```

```js
import sz from 'stringzilla';

const haystack = Buffer.from('Hello, world!');
const needle = Buffer.from('world');

// Substring search
const firstIndex = sz.find(haystack, needle);       // 7n
const lastIndex = sz.findLast(haystack, needle);    // 7n

// Character / charset search
const firstOIndex = sz.findByte(haystack, 'o'.charCodeAt(0));        // 4n
const firstVowelIndex = sz.findByteFrom(haystack, Buffer.from('aeiou'));   // 1n
const lastVowelIndex = sz.findLastByteFrom(haystack, Buffer.from('aeiou')); // 8n

// Counting (optionally overlapping)
const lCount = sz.count(haystack, Buffer.from('l'));               // 3n
const llOverlapCount = sz.count(haystack, Buffer.from('ll'), true); // 1n

// Equality/ordering
const isEqual = sz.equal(Buffer.from('a'), Buffer.from('a'));
const order = sz.compare(Buffer.from('a'), Buffer.from('b')); // -1, 0, or 1

// Byte sum
const byteSum = sz.byteSum(haystack);
```

### Unicode Case-Folding

```js
import sz from "stringzilla";

console.log(sz.utf8CaseFold(Buffer.from("Straße")).toString("utf8"));  // "strasse"
console.log(sz.utf8CaseFold(Buffer.from("ofﬁce")).toString("utf8"));   // "office" (U+FB01 ligature)

// Case-insensitive search
const text = Buffer.from(
    "Die Temperaturschwankungen im kosmischen Mikrowellenhintergrund sind ein Maß von etwa 20 µK.\n" +
    "Typografisch sieht man auch: ein Maß von etwa 20 μK."
);
const patternBytes = Buffer.from("EIN MASS VON ETWA 20 μK");

const first = sz.utf8CaseInsensitiveFind(text, patternBytes);
console.log(first); // { index: 69n, length: ... }

// Reuse needle efficiently
const pattern = new sz.Utf8CaseInsensitiveNeedle(patternBytes);
const again = pattern.findIn(text);
```

### Hash and SHA-256

```js
import sz from 'stringzilla';

// One-shot hash (stable 64-bit, returns BigInt)
const hash = sz.hash(Buffer.from('Hello, world!'), 42);

// Incremental hash
const hasher = new sz.Hasher(42);
hasher.update(Buffer.from('Hello, '));
hasher.update(Buffer.from('world!'));
const streamedHash = hasher.digest(); // BigInt

// SHA-256
const digest = sz.sha256(Buffer.from('Hello, world!'));  // Buffer (32 bytes)

const sha = new sz.Sha256();
sha.update(Buffer.from('Hello, '));
sha.update(Buffer.from('world!'));
const hex = sha.hexdigest();  // 64 char hex string
```

## Swift

Add to `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/ashvardanian/stringzilla")
]
```

Core string operations as extensions:

```swift
var s = "Hello, world! Welcome to StringZilla. 👋"
s[s.findFirst(substring: "world")!...]        // "world! Welcome to StringZilla. 👋"
s[s.findLast(substring: "o")!...]             // "o StringZilla. 👋"
s[s.findFirst(characterFrom: "aeiou")!...]    // "ello, world! Welcome to StringZilla. 👋"
s[s.findLast(characterFrom: "aeiou")!...]     // "a. 👋"
s[s.findFirst(characterNotFrom: "aeiou")!...] // "Hello, world! Welcome to StringZilla. 👋"
```

### Unicode Case-Folding

```swift
import StringZilla

let folded = "Straße".utf8CaseFoldedBytes()
print(String(decoding: folded, as: UTF8.self)) // "strasse"

let haystack = "Die Temperaturschwankungen im kosmischen Mikrowellenhintergrund sind ein Maß von etwa 20 µK.\n" +
    "Typografisch sieht man auch: ein Maß von etwa 20 μK."
let needle = "EIN MASS VON ETWA 20 μK"

if let range = haystack.utf8CaseInsensitiveFind(substring: needle) {
    print(haystack[range]) // "ein Maß von etwa 20 µK"
}

// Reuse needle efficiently
let compiledNeedle = Utf8CaseInsensitiveNeedle(needle)
if let range = compiledNeedle.findFirst(in: haystack) {
    print(haystack[range])
}
```

### Hash and SHA-256

```swift
import StringZilla

// One-shot hash (stable 64-bit)
let hash = "Hello, world!".hash(seed: 42)

// Incremental hash
var hasher = StringZillaHasher(seed: 42)
hasher.update("Hello, ")
hasher.update("world!")
let streamedHash = hasher.digest()
assert(hash == streamedHash)

// SHA-256
let digest = "Hello, world!".sha256()           // [UInt8] (32 bytes)

var sha = StringZillaSha256()
sha.update("Hello, ")
sha.update("world!")
let hex = sha.hexdigest()  // String (64 hex chars)
```

## Go

```bash
go get github.com/ashvardanian/stringzilla/golang@latest
```

Build the shared C library first:

```bash
cmake -B build_shared -D STRINGZILLA_BUILD_SHARED=1 -D CMAKE_BUILD_TYPE=Release
cmake --build build_shared --target stringzilla_shared --config Release
export LD_LIBRARY_PATH="$PWD/build_shared:$LD_LIBRARY_PATH"
```

### Core Operations

```go
package main

import (
    "fmt"
    sz "github.com/ashvardanian/stringzilla/golang"
)

func main() {
    s := "the quick brown fox jumps over the lazy dog"

    // Substrings
    fmt.Println(sz.Contains(s, "brown"))        // true
    fmt.Println(sz.Index(s, "the"))             // 0
    fmt.Println(sz.LastIndex(s, "the"))         // 35

    // Single bytes
    fmt.Println(sz.IndexByte(s, 'o'))           // 12
    fmt.Println(sz.LastIndexByte(s, 'o'))       // 41

    // Byte sets
    fmt.Println(sz.IndexAny(s, "aeiou"))        // 2  (first vowel)
    fmt.Println(sz.LastIndexAny(s, "aeiou"))    // 43 (last vowel)

    // Counting
    fmt.Println(sz.Count("aaaaa", "aa", false)) // 2
    fmt.Println(sz.Count("aaaaa", "aa", true))  // 4 (overlapping)
    fmt.Println(sz.Count("abc", "", false))     // 4
    fmt.Println(sz.Bytesum("ABC"), sz.Bytesum("ABCD"))
}
```

### Unicode Case-Folding

```go
package main

import (
    "fmt"
    sz "github.com/ashvardanian/stringzilla/golang"
)

func main() {
    folded, _ := sz.Utf8CaseFold("Straße", true)
    fmt.Println(folded) // "strasse"

    haystack := "Die Temperaturschwankungen im kosmischen Mikrowellenhintergrund sind ein Maß von etwa 20 µK.\n" +
        "Typografisch sieht man auch: ein Maß von etwa 20 μK."
    needle := "EIN MASS VON ETWA 20 μK"

    start64, len64, _ := sz.Utf8CaseInsensitiveFind(haystack, needle, true)
    start, end := int(start64), int(start64+len64)
    fmt.Println(haystack[start:end]) // "ein Maß von etwa 20 µK"

    // Reuse needle
    compiled, _ := sz.NewUtf8CaseInsensitiveNeedle(needle, true)
    start64, len64, _ = compiled.FindIn(haystack, true)
    start, end = int(start64), int(start64+len64)
    fmt.Println(haystack[start:end])
}
```

### Hash and SHA-256

The `Hasher` type implements Go's standard `hash.Hash64` and `io.Writer` interfaces:

```go
import (
    "io"
    sz "github.com/ashvardanian/stringzilla/golang"
)

// One-shot
one := sz.Hash("Hello, world!", 42)

// Streaming (implements hash.Hash64 and io.Writer)
hasher := sz.NewHasher(42)
hasher.Write([]byte("Hello, "))
hasher.Write([]byte("world!"))
streamed := hasher.Digest()  // or hasher.Sum64()
fmt.Println(one == streamed) // true

// Works with io.Copy
file, _ := os.Open("data.txt")
hasher.Reset()
io.Copy(hasher, file)
fileHash := hasher.Sum64()
```

SHA-256 implements `hash.Hash` and `io.Writer`:

```go
// One-shot
digest := sz.HashSha256([]byte("Hello, world!"))
fmt.Printf("%x\n", digest)

// Streaming
hasher := sz.NewSha256()
hasher.Write([]byte("Hello, "))
hasher.Write([]byte("world!"))
digestHex := hasher.Hexdigest()  // string (64 hex chars)

// Standard hash.Hash interface
sum := hasher.Sum(nil)           // []byte with 32 bytes
size := hasher.Size()            // 32
blockSize := hasher.BlockSize()  // 64
```
