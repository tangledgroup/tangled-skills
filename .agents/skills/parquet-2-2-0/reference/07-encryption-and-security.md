# Encryption and Security

## Contents
- Encryption Overview
- AES/GCM Mode
- AES/S2E Mode
- Footer Encryption
- Key Management

## Encryption Overview

Parquet 2.1+ supports column-level encryption, enabling sensitive data to be stored encrypted while keeping non-sensitive columns readable. Two encryption modes are defined:

- **AES/GCM**: Encrypts both data and metadata (column statistics). Provides confidentiality and integrity.
- **AES/S2E** (Silent Transparent Encryption): Encrypts only data values. Metadata (min/max statistics, null counts) remains in plaintext, enabling query optimization without decryption.

## AES/GCM Mode

Uses AES-256 in Galois/Counter Mode with a 96-bit nonce and 128-bit authentication tag.

### Data Encryption

Each page's data block is encrypted independently:
- Nonce derived from the column path, row group ID, and page number.
- Each encrypted page includes the authentication tag appended after the ciphertext.
- Dictionary pages are also encrypted.

### Metadata Encryption

Column chunk statistics (min/max values) are encrypted, preventing data leakage through metadata. This means readers must decrypt to perform predicate pushdown.

### Integrity

GCM mode provides authenticated encryption — tampered data is detected during decryption.

## AES/S2E Mode (Silent Transparent Encryption)

Designed for cloud storage scenarios where query engines need to scan statistics without access to encryption keys.

### Data Encryption

- Uses AES-256 in S2E mode with a column-specific key.
- Each page is encrypted independently with deterministic nonces.
- Dictionary pages are encrypted the same way as data pages.

### Metadata in Plaintext

Column chunk statistics remain **unencrypted**, allowing:
- Predicate pushdown without decryption keys.
- Partition pruning based on column values.
- Query planning using histogram data.

This trades off some confidentiality (statistics reveal value ranges) for query performance.

## Footer Encryption

The file footer can be encrypted separately from the data pages. The encryption footer contains:

- **`encryption_type`**: `UNENCRYPTED`, `AES_GCM_V1`, or `AES_S2E_V1`.
- **`encryption_footer`**: Encrypted version of the file metadata (schema, row group info).
- **`key_metadata`**: Implementation-specific key material or references.

For encrypted files, the footer structure is:
```
<encrypted data pages>
<encrypted footer>
4-byte length of encrypted footer (little-endian)
4-byte magic "PAR1"
```

The file header and footer length/magic remain unencrypted so readers can locate and identify the file.

## Key Management

Parquet does not define a key management system. Key handling is implementation-specific:

- **Key metadata**: The `key_metadata` field in column chunk and file footer stores implementation-specific key references or material.
- Common approaches:
  - Key IDs referencing external KMS (AWS KMS, HashiCorp Vault).
  - Encrypted keys wrapped with a master key.
  - Application-managed key rotation.

Implementations should document their key management strategy and ensure keys are never stored in plaintext within the Parquet file unless explicitly intended.
