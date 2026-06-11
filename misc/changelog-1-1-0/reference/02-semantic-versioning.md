# Semantic Versioning 2.0.0

## Summary

Given a version number `MAJOR.MINOR.PATCH`, increment the:

1. **MAJOR** version when you make incompatible API changes
2. **MINOR** version when you add functionality in a backward compatible manner
3. **PATCH** version when you make backward compatible bug fixes

Additional labels for pre-release and build metadata are available as extensions to the `MAJOR.MINOR.PATCH` format.

## Introduction

Semantic Versioning (SemVer) provides a simple set of rules that dictate how version numbers are assigned and incremented. It solves "dependency hell" by making version numbers convey meaningful information about compatibility.

Consider a version format of `X.Y.Z` (Major.Minor.Patch). Bug fixes not affecting the API increment the patch version, backward compatible API additions increment the minor version, and backward incompatible API changes increment the major version.

## Specification

### Public API Declaration

Software using Semantic Versioning MUST declare a public API. This API could be declared in the code itself or exist strictly in documentation. It SHOULD be precise and comprehensive.

### Version Format

A normal version number MUST take the form `X.Y.Z` where X, Y, and Z are non-negative integers, and MUST NOT contain leading zeroes. Each element MUST increase numerically.

- `1.9.0` → `1.10.0` → `1.11.0` (correct numeric increment)
- `1.09.0` is invalid (leading zero)

Once a versioned package has been released, the contents of that version MUST NOT be modified. Any modifications MUST be released as a new version.

### Major Version Zero (`0.y.z`)

Major version zero is for initial development. Anything MAY change at any time. The public API SHOULD NOT be considered stable.

The simplest approach: start your initial development release at `0.1.0` and increment the minor version for each subsequent release.

### Version `1.0.0`

Version `1.0.0` defines the public API. If your software is being used in production, it should probably already be `1.0.0`. If you have a stable API on which users have come to depend, you should be `1.0.0`.

### Patch Version (`x.y.Z`, where `x > 0`)

MUST be incremented if only backward compatible bug fixes are introduced. A bug fix is defined as an internal change that fixes incorrect behavior.

```
1.0.1 → 1.0.2 → 1.0.3
```

### Minor Version (`x.Y.z`, where `x > 0`)

MUST be incremented if new, backward compatible functionality is introduced to the public API. It MUST be incremented if any public API functionality is marked as deprecated. Patch version MUST be reset to 0 when minor version is incremented.

```
1.0.3 → 1.1.0 (not 1.1.3)
```

### Major Version (`X.y.z`, where `X > 0`)

MUST be incremented if any backward incompatible changes are introduced to the public API. Patch and minor versions MUST be reset to 0 when major version is incremented.

```
1.5.2 → 2.0.0 (not 2.1.0 or 2.0.1)
```

### Pre-release Versions

A pre-release version MAY be denoted by appending a hyphen and a series of dot-separated identifiers immediately following the patch version.

- Identifiers MUST comprise only ASCII alphanumerics and hyphens `[0-9A-Za-z-]`
- Identifiers MUST NOT be empty
- Numeric identifiers MUST NOT include leading zeroes
- Pre-release versions have lower precedence than the associated normal version

Examples:

```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-beta
1.0.0-beta.2
1.0.0-rc.1
1.0.0-x.7.z.92
```

### Build Metadata

Build metadata MAY be denoted by appending a plus sign and a series of dot-separated identifiers immediately following the patch or pre-release version.

- Identifiers MUST comprise only ASCII alphanumerics and hyphens `[0-9A-Za-z-]`
- Build metadata MUST be ignored when determining version precedence

Examples:

```
1.0.0-alpha+001
1.0.0+20130313144700
1.0.0-beta+exp.sha.5114f85
```

### Version Precedence

Precedence refers to how versions are compared when ordered:

- Major, minor, and patch are always compared numerically
- When major, minor, and patch are equal, a pre-release version has lower precedence than a normal version
- Numeric identifiers are compared numerically; alphanumeric identifiers are compared lexically in ASCII sort order
- Numeric identifiers always have lower precedence than non-numeric identifiers
- A larger set of pre-release fields has higher precedence if all preceding identifiers are equal

Example precedence chain:

```
1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0
```

### Version Regex

Valid SemVer pattern (ECMAScript-compatible):

```regex
^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
```

Named groups version (Python, PCRE):

```regex
^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
```

### SemVer and Changelog Mapping

When writing changelog entries, the change type determines which version component to increment:

- `Added` (new feature) → increment MINOR
- `Changed` (backward compatible) → increment MINOR
- `Changed` (breaking) → increment MAJOR
- `Deprecated` → increment MINOR (deprecation is part of the public API)
- `Removed` (of deprecated feature) → increment MAJOR
- `Fixed` (bug fix) → increment PATCH
- `Security` → depends on whether it changes the public API; typically PATCH for fixes, MAJOR if it introduces breaking behavior changes

### Common SemVer Questions

**How should I handle deprecating functionality?**

When you deprecate part of your public API: (1) update documentation, (2) issue a new minor release with the deprecation. Before completely removing the functionality in a major release, there should be at least one minor release that contains the deprecation so users can transition smoothly.

**What if I accidentally release a breaking change as a minor version?**

Fix the problem and release a new minor version that restores backward compatibility. It is unacceptable to modify versioned releases. Document the offending version and inform users.

**What if I update my own dependencies without changing the public API?**

That is considered compatible since it does not affect the public API. Whether it is a patch or minor increment depends on whether you updated dependencies to fix a bug (patch) or introduce new functionality (minor).

**Is `v1.2.3` a semantic version?**

No. "v1.2.3" is not a semantic version. However, prefixing with "v" is a common convention in tag names (e.g., `git tag v1.2.3`). The actual semantic version is `1.2.3`.
