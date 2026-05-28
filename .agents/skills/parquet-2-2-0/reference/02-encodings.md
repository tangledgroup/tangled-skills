# Encodings

## Contents
- PLAIN Encoding
- Dictionary Encoding
- RLE / Bit-Packing Hybrid
- Delta Binary Packed
- Delta Length Byte Array
- Delta Strings
- Byte Stream Split
- Deprecated Encodings

## Supported Encodings

| Encoding | Enum | Supported Types |
|---|---|---|
| PLAIN | `PLAIN = 0` | All physical types |
| Dictionary | `RLE_DICTIONARY = 8` (data), `PLAIN = 0` (dict page) | All physical types |
| RLE/Bit-Packing | `RLE = 3` | BOOLEAN, dictionary indices |
| Delta Binary Packed | `DELTA_BINARY_PACKED = 5` | INT32, INT64 |
| Delta Length Byte Array | `DELTA_LENGTH_BYTE_ARRAY = 6` | BYTE_ARRAY |
| Delta Strings | `DELTA_BYTE_ARRAY = 7` | BYTE_ARRAY, FIXED_LEN_BYTE_ARRAY |
| Byte Stream Split | `BYTE_STREAM_SPLIT = 9` | FLOAT, DOUBLE, INT32, INT64, FIXED_LEN_BYTE_ARRAY |

## PLAIN Encoding (`PLAIN = 0`)

Simplest encoding — values stored back-to-back. Fallback when more efficient encodings cannot be used.

| Type | Format |
|---|---|
| BOOLEAN | Bit-packed, LSB first |
| INT32 | 4 bytes little-endian |
| INT64 | 8 bytes little-endian |
| INT96 | 12 bytes little-endian (deprecated) |
| FLOAT | 4 bytes IEEE little-endian |
| DOUBLE | 8 bytes IEEE little-endian |
| BYTE_ARRAY | 4-byte length (little-endian) + bytes |
| FIXED_LEN_BYTE_ARRAY | Raw bytes (no length prefix) |

## Dictionary Encoding (`RLE_DICTIONARY = 8`)

Builds a dictionary of distinct values encountered in a column. Dictionary stored in a dictionary page using PLAIN encoding. Data pages store integer indices encoded with RLE/Bit-Packing.

**Format**:
- **Dictionary page**: Entries stored using PLAIN encoding.
- **Data page**: 1 byte for bit width of entry IDs, followed by values encoded with RLE/Bit-Packing at that bit width.

If the dictionary grows too large (by size or distinct count), fall back to PLAIN encoding. Use `RLE_DICTIONARY` enum in data pages and `PLAIN` in dictionary pages for new files. The older `PLAIN_DICTIONARY = 2` enum is deprecated.

## RLE / Bit-Packing Hybrid (`RLE = 3`)

Combines bit-packing and run-length encoding for repeated values. Fixed bit-width known in advance.

**Grammar**:
```
rle-bit-packed-hybrid: <length?> <encoded-data>
encoded-data := <run>*
run := <bit-packed-run> | <rle-run>
bit-packed-run := varint-encode((bit-packed-run-len / 8) << 1 | 1) <bit-packed-values>
rle-run := varint-encode(rle-run-len << 1) <repeated-value>
```

- Bit-packing order: least significant bit of each byte first (optimized for little-endian hardware).
- Values packed in multiples of 8.
- `varint-encode()` uses ULEB-128.
- Run lengths must be in range [1, 2^31 - 1].

**Length prefix rules** (4-byte length prepended?):

| Page Kind | Data Kind | Prepend Length? |
|---|---|---|
| Data page v1 | Definition levels | Yes |
| Data page v1 | Repetition levels | Yes |
| Data page v1 | Dictionary indices | No |
| Data page v1 | Boolean values | Yes |
| Data page v2 | Definition levels | No |
| Data page v2 | Repetition levels | No |
| Data page v2 | Dictionary indices | No |
| Data page v2 | Boolean values | Yes |

**Only supported for**: repetition/definition levels, dictionary indices, and boolean values in data pages.

## Delta Binary Packed (`DELTA_BINARY_PACKED = 5`)

Adapted from Lemire and Boytsov's binary packing. Designed for INT32/INT64 columns with sequential or slowly-changing values.

**Header**:
```
<block size in values> <miniblock count per block> <total value count> <first value>
```
- Block size: multiple of 128 (ULEB128).
- Miniblock count: divisor of block size; quotient (values per miniblock) must be multiple of 32.
- Total value count: ULEB128.
- First value: zigzag ULEB128.

**Each block**:
```
<min delta> <list of miniblock bit widths> <miniblocks>
```

**Encoding process**:
1. Compute deltas between consecutive elements (first element uses last from previous block, or the header's first value).
2. Compute min delta (frame of reference). Subtract from all deltas → all non-negative.
3. Encode min delta as zigzag ULEB128, then bit widths per miniblock, then bit-packed values.

Multiple blocks allow adapting to data changes by shifting the frame of reference. Arithmetic overflow wraps in 2's complement — implementations must handle this correctly.

**Example**: `[1, 2, 3, 4, 5]` → deltas `[1, 1, 1, 1]`, min delta = 1, relative deltas all 0 → encoded as just the header plus a zero-bit-width miniblock.

## Delta Length Byte Array (`DELTA_LENGTH_BYTE_ARRAY = 6`)

Preferred over PLAIN for BYTE_ARRAY columns. Encodes lengths using Delta Binary Packed, then concatenates raw byte array data.

**Format**:
```
<Delta Encoded Lengths> <Byte Array Data (concatenated)>
```

Example: `["Hello", "World", "Foobar", "ABCDEF"]` → DeltaEncoding(5, 5, 6, 6) + `"HelloWorldFoobarABCDEF"`.

## Delta Strings (`DELTA_BYTE_ARRAY = 7`)

Incremental encoding (front compression). For each string, stores the prefix length shared with the previous string plus the new suffix.

**Format**:
```
<Delta Encoded Prefix Lengths> <Delta Length Byte Array of Suffixes>
```

Example: `["axis", "axle", "babble", "babyhood"]` → DeltaEncoding(0, 2, 0, 3) + DeltaEncoding(4, 2, 6, 5) + `"axislebabbleyhood"`.

Works for both BYTE_ARRAY and FIXED_LEN_BYTE_ARRAY (all lengths encoded even for fixed-length).

## Byte Stream Split (`BYTE_STREAM_SPLIT = 9`)

Does not reduce data size but improves compression ratios when a compressor follows. Splits values into K byte-streams where K is the type's byte size.

**Process**: Scatter bytes of each value to corresponding streams. Concatenate streams in order: stream 0, stream 1, ..., stream K-1.

Example for three FLOAT32 values:
```
Original:  AA BB CC DD | 00 11 22 33 | A3 B4 C5 D6
Split:     AA 00 A3 | BB 11 B4 | CC 22 C5 | DD 33 D6
```

Supported types: FLOAT, DOUBLE, INT32, INT64, FIXED_LEN_BYTE_ARRAY. No padding allowed inside data page.

## Deprecated Encodings

### BIT_PACKED (`BIT_PACKED = 4`)

Bit-packed only (no RLE). Values packed from most significant bit to least significant bit. Superseded by RLE/Bit-Packing hybrid which is a strict superset with better packing order. Only supported for repetition and definition levels.
