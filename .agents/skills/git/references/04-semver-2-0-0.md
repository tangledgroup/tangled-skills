# Semantic Versioning 2.0.0

This reference covers the full Semantic Versioning specification (SemVer 2.0.0), which provides a standardized system for assigning and incrementing version numbers to communicate meaningful changes to software.

## Summary

Given a version number **MAJOR.MINOR.PATCH**, increment the:

1. **MAJOR** version when you make incompatible API changes
2. **MINOR** version when you add functionality in a backward compatible manner
3. **PATCH** version when you make backward compatible bug fixes

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

## Introduction

In systems with many dependencies, releasing new package versions can become a nightmare. Two common problems:

- **Version lock:** The inability to upgrade a package without having to release new versions of every dependent package (dependencies specified too tightly).
- **Version promiscuity:** Assuming compatibility with more future versions than is reasonable (dependencies specified too loosely).

Semantic Versioning solves this by giving version numbers a clear, standardized meaning. Once you identify your public API, you communicate changes to it with specific increments to your version number.

**You must declare a public API** — this may consist of documentation or be enforced by the code itself. Regardless, it should be precise and comprehensive.

## Specification Rules (RFC 2119)

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

### Rule 1 — Public API

Software using Semantic Versioning **MUST** declare a public API. This API could be declared in the code itself or exist strictly in documentation. However it is done, it **SHOULD** be precise and comprehensive.

### Rule 2 — Version Form

A normal version number **MUST** take the form `X.Y.Z` where X, Y, and Z are non-negative integers, and **MUST NOT** contain leading zeroes. X is the major version, Y is the minor version, and Z is the patch version. Each element **MUST** increase numerically. For instance: `1.9.0 → 1.10.0 → 1.11.0`.

### Rule 3 — Immutable Releases

Once a versioned package has been released, the contents of that version **MUST NOT** be modified. Any modifications **MUST** be released as a new version.

### Rule 4 — Major Zero (0.y.z)

Major version zero (`0.y.z`) is for initial development. Anything **MAY** change at any time. The public API **SHOULD NOT** be considered stable.

### Rule 5 — Version 1.0.0

Version 1.0.0 defines the public API. The way in which the version number is incremented after this release is dependent on this public API and how it changes.

### Rule 6 — Patch Version (x.y.Z \| x > 0)

Patch version Z **MUST** be incremented if only backward compatible bug fixes are introduced. A bug fix is defined as an internal change that fixes incorrect behavior.

### Rule 7 — Minor Version (x.Y.z \| x > 0)

Minor version Y **MUST** be incremented if new, backward compatible functionality is introduced to the public API. It **MUST** be incremented if any public API functionality is marked as deprecated. It **MAY** be incremented if substantial new functionality or improvements are introduced within the private code. It **MAY** include patch level changes. Patch version **MUST** be reset to 0 when minor version is incremented.

### Rule 8 — Major Version (X.y.z \| X > 0)

Major version X **MUST** be incremented if any backward incompatible changes are introduced to the public API. It **MAY** also include minor and patch level changes. Patch and minor versions **MUST** be reset to 0 when major version is incremented.

### Rule 9 — Pre-release Versions

A pre-release version **MAY** be denoted by appending a hyphen and a series of dot separated identifiers immediately following the patch version. Identifiers **MUST** comprise only ASCII alphanumerics and hyphens `[0-9A-Za-z-]`. Identifiers **MUST NOT** be empty. Numeric identifiers **MUST NOT** include leading zeroes. Pre-release versions have a **lower precedence** than the associated normal version. A pre-release version indicates that the version is unstable and might not satisfy the intended compatibility requirements.

**Examples:**
```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-0.3.7
1.0.0-x.7.z.92
1.0.0-x-y-z.--.
```

### Rule 10 — Build Metadata

Build metadata **MAY** be denoted by appending a plus sign and a series of dot separated identifiers immediately following the patch or pre-release version. Identifiers **MUST** comprise only ASCII alphanumerics and hyphens `[0-9A-Za-z-]`. Identifiers **MUST NOT** be empty. Build metadata **MUST be ignored when determining version precedence**. Thus two versions that differ only in the build metadata have the same precedence.

**Examples:**
```
1.0.0-alpha+001
1.0.0+20130313144700
1.0.0-beta+exp.sha.5114f85
1.0.0+21AF26D3----117B344092BD
```

### Rule 11 — Precedence

Precedence refers to how versions are compared to each other when ordered.

#### 11a. Separate Identifiers

Precedence **MUST** be calculated by separating the version into major, minor, patch and pre-release identifiers in that order (build metadata does not figure into precedence).

#### 11b. Compare Left to Right

Precedence is determined by the first difference when comparing each of these identifiers from left to right as follows: major, minor, and patch versions are always compared numerically.

```
Example: 1.0.0 < 2.0.0 < 2.1.0 < 2.1.1
```

#### 11c. Pre-release Has Lower Precedence

When major, minor, and patch are equal, a pre-release version has lower precedence than a normal version:

```
Example: 1.0.0-alpha < 1.0.0
```

#### 11d. Pre-release Identifier Comparison

Precedence for two pre-release versions with the same major, minor, and patch version **MUST** be determined by comparing each dot separated identifier from left to right until a difference is found:

1. Identifiers consisting of **only digits** are compared **numerically**.
2. Identifiers with **letters or hyphens** are compared **lexically in ASCII sort order**.
3. **Numeric identifiers always have lower precedence** than non-numeric identifiers.
4. A **larger set** of pre-release fields has a **higher precedence** than a smaller set, if all of the preceding identifiers are equal.

```
Example: 1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0
```

### BNF Grammar for Valid SemVer Versions

```
<valid semver>       ::= <version core>
                       | <version core> "-" <pre-release>
                       | <version core> "+" <build>
                       | <version core> "-" <pre-release> "+" <build>

<version core>       ::= <major> "." <minor> "." <patch>

<major>              ::= <numeric identifier>

<minor>              ::= <numeric identifier>

<patch>              ::= <numeric identifier>

<pre-release>        ::= <dot-separated pre-release identifiers>

<build>              ::= <dot-separated build identifiers>
```

## Version Bump Summary

| Change Type | Rule | Example |
|-------------|------|---------|
| Bug fix (backward compatible) | Increment PATCH | `1.2.3 → 1.2.4` |
| New feature (backward compatible) | Increment MINOR, reset PATCH | `1.2.3 → 1.3.0` |
| Breaking change | Increment MAJOR, reset MINOR and PATCH | `1.2.3 → 2.0.0` |
| Deprecation | Increment MINOR (at least) | `1.2.3 → 1.3.0` |
| Pre-release | Append `-alpha`, `-beta`, `-rc`, etc. | `1.0.0 → 1.0.0-rc.1` |

## Why Use Semantic Versioning

Without compliance to some sort of formal specification, version numbers are essentially useless for dependency management. By giving a name and clear definition to the above ideas, it becomes easy to communicate your intentions to the users of your software.

**Example:** A library called "Firetruck" requires a Semantically Versioned package named "Ladder." At the time that Firetruck is created, Ladder is at version 3.1.0. Since Firetruck uses some functionality that was first introduced in 3.1.0, you can safely specify the Ladder dependency as `>= 3.1.0 < 4.0.0`. Now, when Ladder version 3.1.1 and 3.2.0 become available, they will be compatible with existing dependent software automatically.

## FAQ

### How should I deal with revisions in the 0.y.z initial development phase?

Start your initial development release at `0.1.0` and then increment the minor version for each subsequent release.

### How do I know when to release 1.0.0?

If your software is being used in production, it should probably already be 1.0.0. If you have a stable API on which users have come to depend, you should be 1.0.0. If you're worrying a lot about backward compatibility, you should probably already be 1.0.0.

### Doesn't this discourage rapid development and fast iteration?

Major version zero is all about rapid development. If you're changing the API every day you should either still be in version `0.y.z` or on a separate development branch working on the next major version.

### If even the tiniest backward incompatible changes require a major version bump, won't I end up at version 42.0.0 very rapidly?

This is a question of responsible development and foresight. Incompatible changes should not be introduced lightly to software that has a lot of dependent code. The cost that must be incurred to upgrade can be significant. Having to bump major versions means you'll think through the impact of your changes, and evaluate the cost/benefit ratio involved.

### What do I do if I accidentally release a backward incompatible change as a minor version?

As soon as you realize that you've broken the Semantic Versioning spec, fix the problem and release a new patch version that corrects the problem and restores backward compatibility. Even under this circumstance, it is unacceptable to modify versioned releases. If it's appropriate, document the offending version and inform your users of the problem.

### What should I do if I update my own dependencies without changing the public API?

That would be considered compatible since it does not affect the public API. Determining whether the change is a patch level or minor level modification depends on whether you updated your dependencies in order to fix a bug or introduce new functionality.

### How should I handle deprecating functionality?

When you deprecate part of your public API: (1) update your documentation, (2) issue a new minor release with the deprecation in place. Before completely removing the functionality in a new major release there should be at least one minor release that contains the deprecation so that users can smoothly transition.

### Is "v1.2.3" a semantic version?

No, "v1.2.3" is not a semantic version. However, prefixing a semantic version with a "v" is a common way to indicate it is a version number. Example: `git tag v1.2.3 -m "Release version 1.2.3"`, in which case "v1.2.3" is a tag name and the semantic version is "1.2.3".

### Is there a suggested regular expression to check a SemVer string?

**Named groups (PCRE, Python, Go):**
```regex
^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
```

**Numbered groups (ECMAScript, PCRE, Python, Go):**
```regex
^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
```

See [Conventional Commits](../03-conventional-commits.md) for how commit types map to SemVer version bumps.
