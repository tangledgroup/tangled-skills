# Validation Patterns and Grammar

## Regular Expressions for SemVer Validation

### Regex with Named Groups (PCRE, Python, Go)

For systems that support named capture groups (Perl Compatible Regular Expressions, Python, Go):

```regex
^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
```

**Named groups:**
- `major`: Major version number
- `minor`: Minor version number
- `patch`: Patch version number
- `prerelease`: Pre-release identifier(s) (optional)
- `buildmetadata`: Build metadata (optional)

**Python example:**
```python
import re

SEMVER_REGEX = re.compile(
    r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
    r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
    r'(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
)

def parse_semver(version):
    match = SEMVER_REGEX.match(version)
    if not match:
        return None
    return match.groupdict()

# Usage
result = parse_semver("1.2.3-alpha.1+build.123")
# {'major': '1', 'minor': '2', 'patch': '3', 
#  'prerelease': 'alpha.1', 'buildmetadata': 'build.123'}
```

### Regex with Numbered Groups (JavaScript, PCRE, Python, Go)

For systems that use numbered capture groups:

```regex
^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
```

**Capture groups:**
- Group 1: Major version
- Group 2: Minor version
- Group 3: Patch version
- Group 4: Pre-release (optional)
- Group 5: Build metadata (optional)

**JavaScript example:**
```javascript
const SEMVER_REGEX = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/;

function parseSemver(version) {
    const match = version.match(SEMVER_REGEX);
    if (!match) return null;
    
    return {
        major: parseInt(match[1], 10),
        minor: parseInt(match[2], 10),
        patch: parseInt(match[3], 10),
        prerelease: match[4] || null,
        buildmetadata: match[5] || null
    };
}

// Usage
const result = parseSemver("2.1.0-beta+exp.sha.5114f85");
// { major: 2, minor: 1, patch: 0, prerelease: 'beta', buildmetadata: 'exp.sha.5114f85' }
```

## Regex Pattern Breakdown

### Core Version Pattern

```regex
(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)
```

**Components:**
- `0|[1-9]\d*`: Matches either `0` alone OR a non-zero digit followed by any digits
  - Allows: `0`, `1`, `42`, `123`
  - Disallows: `01`, `007`, `00` (leading zeros)
- `\.`: Literal dot separator (escaped because `.` matches any character in regex)

### Pre-Release Pattern (Optional)

```regex
(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?
```

**Components:**
- `(?:...)`: Non-capturing group (groups without creating a capture group)
- `-`: Literal hyphen separator (required for pre-release)
- Inner pattern matches identifiers:
  - `0|[1-9]\d*`: Pure numeric identifier (no leading zeros unless single `0`)
  - `\d*[a-zA-Z-][0-9a-zA-Z-]*`: Alphanumeric identifier (must contain at least one letter or hyphen)
- `(?:\.(?:...))*`: Zero or more additional identifiers separated by dots

**Valid pre-release examples:**
```
-alpha
-alpha.1
-0.3.7
-x.7.z.92
-rc.1
-1
-0
```

**Invalid pre-release examples:**
```
-01          # Leading zero in numeric identifier
-01.alpha    # Leading zero
-.alpha      # Empty identifier before dot
-alpha.      # Empty identifier after dot (trailing dot)
-            # No identifier after hyphen
```

### Build Metadata Pattern (Optional)

```regex
(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?
```

**Components:**
- `\+`: Literal plus sign separator (escaped because `+` is a regex quantifier)
- `[0-9a-zA-Z-]+`: One or more alphanumeric characters or hyphens
- `(?:\.[0-9a-zA-Z-]+)*`: Zero or more additional identifiers separated by dots

**Note:** Build metadata identifiers have no leading zero restriction (unlike pre-release numeric identifiers).

**Valid build metadata examples:**
```
+20130313144700
+exp.sha.5114f85
+21AF26D3----117B344092BD
+001
+build.123
```

**Invalid build metadata examples:**
```
+            # No identifier after plus
+.abc        # Empty identifier before dot
+abc.        # Empty identifier after dot (trailing dot)
```

## Backus-Naur Form (BNF) Grammar

The official BNF grammar for valid SemVer versions:

```bnf
<valid semver> ::= <version core>
                 | <version core> "-" <pre-release>
                 | <version core> "+" <build>
                 | <version core> "-" <pre-release> "+" <build>

<version core> ::= <major> "." <minor> "." <patch>

<major> ::= <numeric identifier>

<minor> ::= <numeric identifier>

<patch> ::= <numeric identifier>

<pre-release> ::= <dot-separated pre-release identifiers>

<dot-separated pre-release identifiers> ::= <pre-release identifier>
                                          | <pre-release identifier> "." <dot-separated pre-release identifiers>

<build> ::= <dot-separated build identifiers>

<dot-separated build identifiers> ::= <build identifier>
                                    | <build identifier> "." <dot-separated build identifiers>

<pre-release identifier> ::= <alphanumeric identifier>
                           | <numeric identifier>

<build identifier> ::= <alphanumeric identifier>
                     | <digits>

<alphanumeric identifier> ::= <non-digit>
                            | <non-digit> <identifier characters>
                            | <identifier characters> <non-digit>
                            | <identifier characters> <non-digit> <identifier characters>

<numeric identifier> ::= "0"
                       | <positive digit>
                       | <positive digit> <digits>

<identifier characters> ::= <identifier character>
                          | <identifier character> <identifier characters>

<identifier character> ::= <digit>
                         | <non-digit>

<non-digit> ::= <letter>
              | "-"

<digits> ::= <digit>
           | <digit> <digits>

<digit> ::= "0"
          | <positive digit>

<positive digit> ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<letter> ::= "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J"
           | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T"
           | "U" | "V" | "W" | "X" | "Y" | "Z" | "a" | "b" | "c" | "d"
           | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n"
           | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x"
           | "y" | "z"
```

## Valid Version Examples

### Core Versions (No Pre-Release, No Build Metadata)
```
0.0.0
0.1.0
1.0.0
1.2.3
10.20.30
123.456.789
```

### With Pre-Release Only
```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-0.3.7
1.0.0-x.7.z.92
1.0.0-x-y-z.--.
1.0.0-beta
1.0.0-beta.2
1.0.0-beta.11
1.0.0-rc.1
```

### With Build Metadata Only
```
1.0.0+20130313144700
1.0.0+exp.sha.5114f85
1.0.0+21AF26D3----117B344092BD
1.0.0+001
```

### With Both Pre-Release and Build Metadata
```
1.0.0-alpha+001
1.0.0-beta+exp.sha.5114f85
1.0.0-rc.1+build.123
```

## Invalid Version Examples

### Leading Zeros in Core Version
```
01.2.3    # Leading zero in major
1.02.3    # Leading zero in minor
1.2.03    # Leading zero in patch
1.0.0     # Valid! Single zero is allowed
```

### Invalid Pre-Release Identifiers
```
1.0.0-    # Empty pre-release (no identifier after hyphen)
1.0.0-.1  # Empty first identifier
1.0.0-01  # Leading zero in numeric identifier
1.0.0-1.02 # Leading zero in second identifier
1.0.0-alpha. # Trailing dot (empty identifier)
1.0.0-_alpha # Underscore not allowed
1.0.0-alpha_beta # Underscore not allowed
```

### Invalid Build Metadata
```
1.0.0+    # Empty build metadata (no identifier after plus)
1.0.0+.abc # Empty first identifier
1.0.0+abc. # Trailing dot (empty identifier)
1.0.0+abc_def # Underscore not allowed
```

### Other Invalid Formats
```
1.2       # Missing patch version
1         # Only major version
v1.2.3    # 'v' prefix not part of SemVer (common convention, but not valid)
1.2.3-alpha-beta # Valid! Hyphens allowed in identifiers
1.2.3.4   # Too many dots in core version
```

## Language-Specific Validation Examples

### Go Example
```go
package main

import (
    "fmt"
    "regexp"
)

var semverRegex = regexp.MustCompile(`^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$`)

func isValidSemver(version string) bool {
    return semverRegex.MatchString(version)
}

func main() {
    versions := []string{"1.2.3", "1.2.3-alpha", "v1.2.3", "1.2"}
    for _, v := range versions {
        fmt.Printf("%s: %v\n", v, isValidSemver(v))
    }
}
```

### JavaScript Example
```javascript
function isValidSemver(version) {
    const regex = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/;
    return regex.test(version);
}

// Usage
console.log(isValidSemver("1.2.3"));      // true
console.log(isValidSemver("1.2.3-alpha")); // true
console.log(isValidSemver("v1.2.3"));     // false
console.log(isValidSemver("1.2"));        // false
```

### Python Example
```python
import re

SEMVER_PATTERN = re.compile(
    r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
    r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
    r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
)

def is_valid_semver(version):
    return bool(SEMVER_PATTERN.match(version))

# Usage
print(is_valid_semver("1.2.3"))      # True
print(is_valid_semver("1.2.3-alpha")) # True
print(is_valid_semver("v1.2.3"))     # False
print(is_valid_semver("1.2"))        # False
```

## Version String Size Considerations

SemVer has no official size limit on version strings, but:

**Guidelines:**
- Use good judgment (255 characters is probably overkill)
- Specific systems may impose their own limits:
  - Git tags: Typically 64KB limit
  - Package managers: Vary by implementation
  - Filesystems: Filename length limits apply

**Recommendation:** Keep version strings under 100 characters for maximum compatibility.

## The "v" Prefix Convention

**Question:** Is "v1.2.3" a semantic version?

**Answer:** No, "v1.2.3" is NOT a semantic version. However, prefixing with "v" is a common convention to indicate it's a version number.

**Context:**
- Common in Git tags: `git tag v1.2.3 -m "Release version 1.2.3"`
- In this case, "v1.2.3" is the tag name, but the semantic version is "1.2.3"
- When validating or parsing, strip the "v" prefix first

**Handling in code:**
```python
def normalize_version(version):
    if version.startswith('v'):
        return version[1:]
    return version

normalize_version("v1.2.3")  # Returns "1.2.3"
```
