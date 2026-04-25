# Precedence Comparison Rules

## Overview

Precedence refers to how versions are compared to each other when ordered. This determines which version is "newer" or "greater than" another version for dependency resolution, upgrade paths, and release ordering.

## Precedence Calculation Steps

Precedence MUST be calculated by separating the version into components in this order:
1. Major version
2. Minor version
3. Patch version
4. Pre-release identifiers (if present)

**Important:** Build metadata does NOT figure into precedence comparisons.

## Step-by-Step Comparison Algorithm

### Step 1: Compare Major, Minor, Patch Numerically

Major, minor, and patch versions are always compared numerically from left to right. The first difference determines precedence.

**Examples:**
```
1.0.0 < 2.0.0      # Major: 1 < 2
2.0.0 < 2.1.0      # Major equal, Minor: 0 < 1
2.1.0 < 2.1.1      # Major/Minor equal, Patch: 0 < 1
1.9.0 < 1.10.0     # Numeric comparison: 9 < 10 (not lexicographic)
2.99.0 < 2.100.0   # Numeric comparison: 99 < 100
```

**Complete example chain:**
```
1.0.0 < 2.0.0 < 2.1.0 < 2.1.1
```

### Step 2: Pre-Release vs Normal Version

When major, minor, and patch are equal, a pre-release version has **lower precedence** than a normal version (one without pre-release identifier).

**Rule:** Pre-release indicates the version is unstable and might not satisfy intended compatibility requirements.

**Examples:**
```
1.0.0-alpha < 1.0.0
2.1.0-beta.1 < 2.1.0
1.5.3-rc.2 < 1.5.3
0.9.0-alpha < 0.9.0
```

**Note:** A pre-release of `1.0.0` is less than `1.0.0` but greater than `0.x.x`:
```
0.9.0 < 1.0.0-alpha < 1.0.0
```

### Step 3: Compare Pre-Release Identifiers

Precedence for two pre-release versions with the same major, minor, and patch version MUST be determined by comparing each dot-separated identifier from left to right until a difference is found.

#### Rule 3a: Numeric vs Lexical Comparison

**Identifiers consisting of only digits:** Compared numerically
```
1.0.0-alpha.1 < 1.0.0-alpha.2 < 1.0.0-alpha.10
# Note: 1 < 2 < 10 (numeric, not "1" < "10" < "2" lexicographic)
```

**Identifiers with letters or hyphens:** Compared lexically in ASCII sort order
```
1.0.0-alpha < 1.0.0-beta < 1.0.0-rc
# ASCII order: 'a' < 'b' < 'r'
1.0.0-x < 1.0.0-x-y < 1.0.0-y
```

#### Rule 3b: Numeric Identifiers Have Lower Precedence

Numeric identifiers always have **lower precedence** than non-numeric identifiers.

**Examples:**
```
1.0.0-1 < 1.0.0-alpha
1.0.0-999 < 1.0.0-a
2.0.0-7 < 2.0.0-abc
```

**Rationale:** This allows using numeric identifiers for build numbers or internal versions while reserving alphabetic identifiers for release stages (alpha, beta, rc).

#### Rule 3c: Larger Set Has Higher Precedence

A larger set of pre-release fields has a **higher precedence** than a smaller set, if all of the preceding identifiers are equal.

**Examples:**
```
1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.2
1.0.0-beta < 1.0.0-beta.1 < 1.0.0-beta.2 < 1.0.0-beta.11
1.0.0-rc < 1.0.0-rc.1 < 1.0.0-rc.2
```

**Note:** This rule only applies when preceding identifiers are equal:
```
1.0.0-alpha.2 < 1.0.0-beta      # 'alpha' < 'beta', length doesn't matter
1.0.0-alpha < 1.0.0-alpha.beta  # All preceding equal, longer wins
```

## Complete Precedence Example

Here is a comprehensive example showing the complete precedence ordering:

```
1.0.0-alpha
< 1.0.0-alpha.1
< 1.0.0-alpha.beta
< 1.0.0-beta
< 1.0.0-beta.2
< 1.0.0-beta.11
< 1.0.0-rc.1
< 1.0.0
```

**Breakdown:**
1. `1.0.0-alpha < 1.0.0-alpha.1`: Larger set has higher precedence (Rule 3c)
2. `1.0.0-alpha.1 < 1.0.0-alpha.beta`: Compare second identifier: numeric `1` < non-numeric `beta` (Rule 3b)
3. `1.0.0-alpha.beta < 1.0.0-beta`: Compare first identifier: `alpha` < `beta` lexicographically (Rule 3a)
4. `1.0.0-beta < 1.0.0-beta.2`: Larger set has higher precedence (Rule 3c)
5. `1.0.0-beta.2 < 1.0.0-beta.11`: Compare second identifier: numeric `2` < `11` (Rule 3a)
6. `1.0.0-beta.11 < 1.0.0-rc.1`: Compare first identifier: `beta` < `rc` lexicographically (Rule 3a)
7. `1.0.0-rc.1 < 1.0.0`: Pre-release has lower precedence than normal version (Step 2)

## Build Metadata and Precedence

Build metadata MUST be ignored when determining version precedence. Two versions that differ only in build metadata have the **same precedence**.

**Examples:**
```
1.0.0+20130313144700 == 1.0.0+20130313144701  # Equal precedence
1.0.0-alpha+001 == 1.0.0-alpha+999            # Equal precedence
1.0.0+abc < 1.0.1+xyz                         # Build metadata ignored, compare 1.0.0 < 1.0.1
```

**Use case:** Build metadata is for tracking build information (timestamps, commit hashes) without affecting version ordering.

## Pre-Release Identifier Rules

### Valid Identifier Formats

Pre-release identifiers MUST:
- Comprise only ASCII alphanumerics and hyphens [0-9A-Za-z-]
- NOT be empty
- Follow specific rules for numeric identifiers

**Valid examples:**
```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-0.3.7
1.0.0-x.7.z.92
1.0.0-x-y-z.--.
1.0.0-rc.1
1.0.0-beta.2.build.123
```

**Invalid examples:**
```
1.0.0-         # Empty identifier after hyphen
1.0.0-.1       # Empty first identifier
1.0.0-alpha.   # Trailing dot implies empty identifier
1.0.0-01       # Leading zero in numeric identifier (see below)
1.0.0-alpha_1  # Underscore not allowed (only alphanumerics and hyphens)
```

### Numeric Identifier Leading Zero Rule

Numeric identifiers MUST NOT include leading zeroes.

**Valid:**
```
1.0.0-0
1.0.0-1
1.0.0-10
1.0.0-0.3.7    # '0' is valid (single zero), '3' and '7' are valid
```

**Invalid:**
```
1.0.0-01       # Leading zero
1.0.0-03.7     # '03' has leading zero
1.0.0-1.02     # '02' has leading zero
```

**Rationale:** Prevents ambiguity and ensures consistent numeric comparison across systems.

## Comparison Implementation Example

Here's a conceptual algorithm for comparing two SemVer versions:

```
function compareVersions(v1, v2):
    # Parse both versions
    (major1, minor1, patch1, pre1, build1) = parse(v1)
    (major2, minor2, patch2, pre2, build2) = parse(v2)
    
    # Step 1: Compare major, minor, patch numerically
    if major1 != major2:
        return major1 - major2
    if minor1 != minor2:
        return minor1 - minor2
    if patch1 != patch2:
        return patch1 - patch2
    
    # Step 2: Handle pre-release vs normal version
    if pre1 is None and pre2 is None:
        return 0  # Equal (build metadata ignored)
    if pre1 is None:
        return 1  # v1 is normal, v2 is pre-release: v1 > v2
    if pre2 is None:
        return -1 # v1 is pre-release, v2 is normal: v1 < v2
    
    # Step 3: Compare pre-release identifiers
    identifiers1 = split(pre1, '.')
    identifiers2 = split(pre2, '.')
    
    for i from 0 to max(length(identifiers1), length(identifiers2)):
        id1 = identifiers1[i] if i < length(identifiers1) else None
        id2 = identifiers2[i] if i < length(identifiers2) else None
        
        # Larger set has higher precedence if all preceding equal
        if id1 is None:
            return -1
        if id2 is None:
            return 1
        
        # Determine if identifiers are numeric
        numeric1 = isNumeric(id1)
        numeric2 = isNumeric(id2)
        
        if numeric1 and numeric2:
            # Both numeric: compare as numbers
            diff = parseInt(id1) - parseInt(id2)
            if diff != 0:
                return diff
        elif numeric1:
            # Numeric < non-numeric
            return -1
        elif numeric2:
            # Non-numeric > numeric
            return 1
        else:
            # Both non-numeric: compare lexically (ASCII order)
            if id1 < id2:
                return -1
            if id1 > id2:
                return 1
    
    return 0  # Equal precedence
```

## Edge Cases and Special Scenarios

### Comparing Across Major Version Zero

Major version zero follows the same precedence rules, but with different semantic meaning:

```
0.1.0 < 0.2.0 < 0.9.0 < 0.9.1 < 0.10.0 < 1.0.0-alpha < 1.0.0
```

**Note:** `0.10.0 > 0.9.1` because major version (0) is equal, then minor (10 > 9).

### Pre-Release with Build Metadata

Both pre-release and build metadata can coexist:

```
1.0.0-alpha+001 < 1.0.0-alpha.1+build.999 < 1.0.0+production
```

**Comparison:**
- `1.0.0-alpha+001` vs `1.0.0-alpha.1+build.999`: Compare pre-release `alpha` < `alpha.1`, build metadata ignored
- Both < `1.0.0+production`: Pre-release versions < normal version, build metadata ignored

### Complex Pre-Release Comparisons

```
1.0.0-rc.1.2 < 1.0.0-rc.1.10 < 1.0.0-rc.2 < 1.0.0-rc.2.0 < 1.0.0
```

**Breakdown:**
- `rc.1.2` < `rc.1.10`: Third identifier: numeric 2 < 10
- `rc.1.10` < `rc.2`: Second identifier: numeric 1 < 2
- `rc.2` < `rc.2.0`: Larger set has higher precedence
- `rc.2.0` < `1.0.0`: Pre-release < normal version
