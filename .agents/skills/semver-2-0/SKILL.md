---
name: semver-2-0
description: A skill for implementing and validating Semantic Versioning 2.0.0 (SemVer) to manage software version numbers, determine compatibility, compare version precedence, and validate version strings against the official specification.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - semantic-versioning
  - semver
  - versioning
  - software-versions
  - dependency-management
category: development

external_references:
  - https://semver.org/spec/v2.0.0.html
---

# Semantic Versioning 2.0.0 (SemVer)


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for implementing and validating Semantic Versioning 2.0.0 (SemVer) to manage software version numbers, determine compatibility, compare version precedence, and validate version strings against the official specification.

A comprehensive toolkit for implementing, validating, and working with Semantic Versioning 2.0.0 as defined in the official specification. This skill covers version format rules, precedence comparison, pre-release versions, build metadata, and validation patterns.

## When to Use

- Validating version strings against the SemVer 2.0.0 specification
- Comparing version precedence to determine which version is newer
- Incrementing version numbers correctly (major, minor, patch)
- Understanding when to bump major vs minor vs patch versions
- Parsing and generating valid SemVer strings with pre-release and build metadata
- Implementing dependency resolution based on version ranges
- Designing public APIs with clear versioning strategies

## Quick Start

### Basic Version Format

A normal version number MUST take the form `X.Y.Z` where:
- `X` is the major version (non-negative integer, no leading zeros)
- `Y` is the minor version (non-negative integer, no leading zeros)
- `Z` is the patch version (non-negative integer, no leading zeros)

Example: `1.2.3`, `2.0.0`, `0.1.0`

### Version Increment Rules

| Change Type | Version to Increment | When to Use |
|-------------|---------------------|-------------|
| **PATCH** (`x.y.Z`) | Patch | Backward compatible bug fixes |
| **MINOR** (`x.Y.0`) | Minor | New backward compatible functionality, or deprecating existing API |
| **MAJOR** (`X.0.0`) | Major | Backward incompatible API changes |

See [Version Increment Rules](references/01-version-rules.md) for detailed guidance on when to increment each version component.

### Comparing Versions

Versions are compared by precedence: major, minor, patch (numerically), then pre-release identifiers.

Example: `1.0.0 < 2.0.0 < 2.1.0 < 2.1.1`

See [Precedence Comparison](references/02-precedence-rules.md) for complete comparison algorithms and examples.

## Reference Files

- [`references/01-version-rules.md`](references/01-version-rules.md) - Detailed version increment rules, public API requirements, and major version zero semantics
- [`references/02-precedence-rules.md`](references/02-precedence-rules.md) - Complete precedence comparison algorithm with pre-release handling
- [`references/03-validation-patterns.md`](references/03-validation-patterns.md) - Regular expressions, BNF grammar, and validation examples
- [`references/04-faq-and-best-practices.md`](references/04-faq-and-best-practices.md) - Common questions, migration strategies, and real-world scenarios

## Troubleshooting

### Common Issues

**Leading zeros**: Version components must not have leading zeros. `1.02.3` is invalid; use `1.2.3`.

**Pre-release numeric identifiers**: Numeric pre-release identifiers cannot have leading zeros. `1.0.0-01` is invalid; use `1.0.0-1`.

**Build metadata ignored in comparison**: Two versions differing only in build metadata have equal precedence. `1.0.0+abc` equals `1.0.0+def` for comparison purposes.

**Pre-release has lower precedence**: `1.0.0-alpha < 1.0.0`. Pre-release versions are always less than the associated normal version.

See [FAQ and Best Practices](references/04-faq-and-best-practices.md) for more common scenarios and solutions.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
