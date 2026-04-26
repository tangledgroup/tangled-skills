---
name: semver-2-0-0
description: Implement and validate Semantic Versioning 2.0.0 to manage software version numbers, determine compatibility, compare version precedence, and validate version strings against the official specification. Use when bumping versions, writing version constraints for dependency managers, comparing release ordering, or validating that a version string conforms to SemVer.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.0.0"
tags:
  - versioning
  - semver
  - semantic-versioning
  - releases
  - dependency-management
category: specification
external_references:
  - https://semver.org/spec/v2.0.0.html
---

# Semantic Versioning 2.0.0

## Overview

Semantic Versioning (SemVer) is a specification for assigning and incrementing version numbers in a meaningful, machine-parseable way. Given a version number `MAJOR.MINOR.PATCH`, changes to the number communicate the nature and impact of code modifications to consumers and dependency managers.

The spec was originally authored by Tom Preston-Werner (inventor of Gravatar, cofounder of GitHub) and is licensed under Creative Commons CC BY 3.0.

## When to Use

- Bumping a project version after making changes
- Validating that a version string conforms to SemVer 2.0.0
- Comparing two versions to determine ordering (precedence)
- Writing dependency constraints for package managers
- Deciding whether a change is a patch, minor, or major bump
- Communicating API stability and backward-compatibility guarantees

## Version Format

A normal version number takes the form `X.Y.Z` where:

- **X** — MAJOR version
- **Y** — MINOR version
- **Z** — PATCH version

Each element is a non-negative integer with no leading zeroes. Elements increase numerically (e.g., `1.9.0` → `1.10.0` → `1.11.0`).

Optional extensions follow the core:

- Pre-release: appended with a hyphen, e.g., `1.0.0-alpha.1`
- Build metadata: appended with a plus sign, e.g., `1.0.0+20130313144700`
- Both: `1.0.0-beta+exp.sha.5114f85`

Full format: `[MAJOR.MINOR.PATCH][-PRERELEASE][+BUILD]`

## Version Increment Rules

### MAJOR version (X.y.z, X > 0)

Increment when you introduce **backward incompatible** changes to the public API. May also include minor and patch level changes. Minor and patch versions MUST be reset to 0.

```
3.2.1 → 4.0.0    # removed a public function
2.5.3 → 3.0.0    # changed return type of a public method
```

### MINOR version (x.Y.z, X > 0)

Increment when you add **backward compatible** functionality to the public API. MUST also be incremented when any public API functionality is marked as deprecated. MAY include patch level changes. Patch version MUST be reset to 0.

```
1.2.3 → 1.3.0    # added a new public function
2.0.1 → 2.1.0    # added an optional parameter
1.5.0 → 1.6.0    # deprecated oldEndpoint() in favor of newEndpoint()
```

### PATCH version (x.y.Z, X > 0)

Increment when you make **backward compatible bug fixes**. A bug fix is an internal change that fixes incorrect behavior.

```
1.2.3 → 1.2.4    # fixed null pointer exception
3.1.0 → 3.1.1    # corrected off-by-one error in pagination
```

### Major version zero (0.y.z)

Initial development. Anything MAY change at any time. The public API SHOULD NOT be considered stable. Start at `0.1.0` and increment the minor version for each subsequent release.

### Version 1.0.0

Defines the public API. After this release, version increments depend on how the public API changes. If your software is used in production with a stable API, it should probably already be `1.0.0`.

## Pre-release Versions

Appended with a hyphen and a series of dot-separated identifiers immediately following the patch version.

- Identifiers MUST comprise only ASCII alphanumerics and hyphens: `[0-9A-Za-z-]`
- Identifiers MUST NOT be empty
- Numeric identifiers MUST NOT include leading zeroes

Examples:

```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-0.3.7
1.0.0-x.7.z.92
1.0.0-x-y-z--
```

Pre-release versions have **lower precedence** than the associated normal version:

```
1.0.0-alpha < 1.0.0
```

Pre-release indicates instability — the version might not satisfy the intended compatibility requirements of its associated normal version.

## Build Metadata

Appended with a plus sign and a series of dot-separated identifiers immediately following the patch or pre-release version.

- Identifiers MUST comprise only ASCII alphanumerics and hyphens: `[0-9A-Za-z-]`
- Identifiers MUST NOT be empty

Examples:

```
1.0.0+20130313144700
1.0.0-alpha+001
1.0.0-beta+exp.sha.5114f85
1.0.0+21AF26D3----117B344092BD
```

Build metadata **MUST be ignored** when determining version precedence. Two versions that differ only in build metadata have the same precedence.

## Precedence Rules

Precedence determines how versions compare when ordered. Calculated by separating the version into major, minor, patch, and pre-release identifiers (build metadata does not figure into precedence).

1. **Major, minor, patch** are compared numerically, left to right. The first difference determines ordering.

   ```
   1.0.0 < 2.0.0 < 2.1.0 < 2.1.1
   ```

2. **Pre-release vs normal**: When major, minor, and patch are equal, a pre-release has lower precedence than the normal version.

   ```
   1.0.0-alpha < 1.0.0
   ```

3. **Pre-release vs pre-release**: Compare each dot-separated identifier from left to right until a difference is found:

   - Identifiers consisting of only digits are compared **numerically**
   - Identifiers with letters or hyphens are compared **lexically** in ASCII sort order
   - Numeric identifiers always have **lower precedence** than non-numeric identifiers
   - A larger set of pre-release fields has **higher precedence** than a smaller set, if all preceding identifiers are equal

   Full ordering example:

   ```
   1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0
   ```

## Validation

### Regular Expression

ECMAScript-compatible pattern with numbered capture groups (cg1=major, cg2=minor, cg3=patch, cg4=prerelease, cg5=buildmetadata):

```regex
^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
```

Live demo: https://regex101.com/r/vkijKf/1/

### Python Validation (stdlib only)

```python
import re

SEMVER_RE = re.compile(
    r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
    r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
    r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
    r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
)

def is_valid_semver(version: str) -> bool:
    return SEMVER_RE.match(version) is not None

# Examples
is_valid_semver("1.0.0")          # True
is_valid_semver("0.1.0")          # True
is_valid_semver("1.0.0-alpha")    # True
is_valid_semver("1.0.0+build")    # True
is_valid_semver("v1.2.3")         # False — "v" prefix not part of SemVer
is_valid_semver("1.0")            # False — missing patch
is_valid_semver("01.0.0")         # False — leading zero
```

### Bash Validation

```bash
semver_regex='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)([-]((?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)(\.(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*))?([+]([0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*))?$'

version="1.2.3-beta.1+build.42"
if [[ "$version" =~ $semver_regex ]]; then
    echo "Valid SemVer: $version"
else
    echo "Invalid SemVer: $version"
fi
```

## Backus-Naur Form Grammar

```
<valid semver> ::= <version core>
                 | <version core> "-" <pre-release>
                 | <version core> "+" <build>
                 | <version core> "-" <pre-release> "+" <build>

<version core> ::= <major> "." <minor> "." <patch>

<major> ::= <numeric identifier>
<minor> ::= <numeric identifier>
<patch> ::= <numeric identifier>

<pre-release> ::= <dot-separated pre-release identifiers>
<build> ::= <dot-separated build identifiers>

<dot-separated pre-release identifiers> ::= <pre-release identifier>
                                          | <pre-release identifier> "." <dot-separated pre-release identifiers>
<dot-separated build identifiers> ::= <build identifier>
                                    | <build identifier> "." <dot-separated build identifiers>

<pre-release identifier> ::= <alphanumeric identifier> | <numeric identifier>
<build identifier> ::= <alphanumeric identifier> | <digits>

<numeric identifier> ::= "0"
                       | <positive digit>
                       | <positive digit> <digits>

<identifier character> ::= <digit> | <non-digit>
<non-digit> ::= <letter> | "-"
<digit> ::= "0" | <positive digit>
<positive digit> ::= "1" | "2" | ... | "9"
<letter> ::= "A" | "B" | ... | "Z" | "a" | "b" | ... | "z"
```

## Common Practices

### Declaring a Public API

Software using SemVer MUST declare a public API. This API may be documented or enforced by the code itself. It should be precise and comprehensive — version numbers only convey meaning when there is a clear boundary between public and private.

### Immutability

Once a versioned package has been released, the contents of that version MUST NOT be modified. Any modifications MUST be released as a new version.

### Dependency Specifications

With SemVer you can write flexible dependency ranges. For example, if your library requires `Ladder >= 3.1.0` but is incompatible with `4.0.0`, specify:

```
>= 3.1.0, < 4.0.0
```

This allows consumers to receive compatible minor and patch updates (3.1.1, 3.2.0, etc.) without breaking changes.

### Deprecating Functionality

When deprecating part of your public API:

1. Update documentation to inform users
2. Issue a new **minor** release with the deprecation in place
3. Before completely removing the functionality in a new major release, there should be at least one minor release containing the deprecation so users can transition smoothly

### Accidental Breaking Changes

If you accidentally release a backward incompatible change as a minor or patch version, fix the problem and release a new minor version that restores backward compatibility. Never modify an already-published versioned release. Document the offending version and inform users.

### Internal Dependency Updates

Updating your own dependencies without changing the public API is considered compatible. Whether it is a patch or minor increment depends on whether you updated dependencies to fix a bug (patch) or introduce new functionality (minor).

### The "v" Prefix

`"v1.2.3"` is **not** a semantic version. However, prefixing with `"v"` is a common convention (e.g., `git tag v1.2.3`). The tag name is `"v1.2.3"` but the semantic version is `"1.2.3"`.

## FAQ

**How do I know when to release 1.0.0?** If your software is used in production with a stable API on which users depend, it should be `1.0.0`. If you worry about backward compatibility, you probably already should be.

**Doesn't this discourage rapid development?** Major version zero (`0.y.z`) is designed for rapid development. If you're changing the API daily, stay in `0.y.z` or work on a separate branch for the next major version.

**Won't I end up at version 42.0.0 rapidly?** Incompatible changes should not be introduced lightly to software with many dependents. The cost of bumping major versions encourages thoughtful evaluation of change impact.

**Does SemVer have a size limit on the version string?** No, but use good judgment. A 255-character version string is probably overkill. Specific systems may impose their own limits.
