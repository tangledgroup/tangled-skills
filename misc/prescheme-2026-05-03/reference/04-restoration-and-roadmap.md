# Restoration Project and Roadmap

## Contents
- Project Background
- R7RS Port Status
- Planned Language Extensions
- Tooling Plans
- Future Possibilities

## Project Background

The Pre-Scheme Restoration project (Andrew Whatson, 2024-present) aims to make Pre-Scheme a practical alternative to C for the wider Scheme community. Funded by an NGI Zero grant from the NLnet Foundation.

**Motivation:** The original Pre-Scheme compiler lived inside Scheme 48's source tree and wasn't exposed as an installable package, making it awkward to depend on. Documentation was sparse until Taylor Campbell's "Nearly Complete Scheme48 Reference Manual" (2006). With the rise of systems languages like Rust and Zig, and growing interest in Scheme-level systems development driven by Guix, there is latent demand for a language bridging Scheme expressiveness with C-level control.

**Related inspiration:** Christine Lemmer-Webber's "Guile Steel: a proposal for a systems lisp" post motivated earlier porting efforts to Guile that led to the Restoration project.

## R7RS Port Status

The primary objective is porting the compiler from Scheme 48 to R7RS, enabling it to run on any standard Scheme implementation.

**Current status (as of October 2024):**
- ~75% of codebase loads on Chibi Scheme, Sagittarius Scheme, and Guile
- 100% runs via `s48-r7rs` compatibility layer on Scheme 48 itself
- Remaining unported libraries all interface with the Scheme 48 reader/macro expander

**Key technical achievements:**
- **s48-r7rs compatibility library:** Allows Scheme 48 to load R7RS library definitions, enabling end-to-end testing throughout the porting process. Includes SRFI 64 test framework implementation.
- **Macro porting:** Internal compiler macros reimplemented with `syntax-case`, shipped alongside original `er-macro-transformer` versions with SRFI 211 stubs for target selection.
- **Utility library abstraction:** Non-standard dependencies factored into `(ps-compiler util)` namespace, implemented per-target (e.g., queues via Guile's `(ice-9 q)`, SRFI 117 on Chibi/Sagittarius).
- **Library generation tool:** Script to convert Scheme 48 structures to equivalent R7RS library definitions using the procedural module interface.

**Next step:** Integrate Unsyntax as the portable expander, replacing Scheme 48's reader/macro front-end. Unsyntax expands R7RS with `syntax-case` to a simpler subset that feeds into the Pre-Scheme compiler's AST.

## Planned Language Extensions

The original Pre-Scheme offers minimal functionality sufficient for bootstrapping Scheme 48 but lacking features expected of modern systems languages:

**Sized numeric types:** Extend beyond long fixnums and flonums to cover 8/16/32/64-bit integers and 32/64-bit floats, matching other systems languages.

**Polymorphic arithmetic:** Introduce generic arithmetic operators (like `+` working across int/float) to avoid combinatorial explosion of typed operations. Pre-Scheme already supports polymorphic primitives like `deallocate`.

**Algebraic data types:** Complete the nascent tagged-union support to enable full ADTs with data-type declaration and pattern matching syntax. ADTs and pattern matching are gaining adoption in mainstream languages (Rust, Swift, Kotlin).

**UTF-8 strings:** Replace C-style null-terminated byte strings with length-prefixed, null-terminated UTF-8 as the default representation. C-style strings remain accessible via the bytevector type for legacy API interfacing.

**Bytevectors:** R6RS/R7RS-standardized byte arrays (analogous to C `char[]`), implemented with a library covering R7RS and relevant R6RS subsets.

**Ports:** Extend minimal I/O port support to cover as much of R7RS as possible, ideally with polymorphic port interface supporting string, bytevector, and SRFI-181 custom ports.

**R7RS compatibility:** Implement all other R7RS procedures that don't require intermediate allocation, lists, or vectors.

## Tooling Plans

The original compiler had minimal user interface and documentation. The Restoration project addresses this:

**Command-line interface:** Ergonomic CLI for compilation and linking, respecting established conventions (similar to Chicken, Bigloo, Gambit), simplifying integration with GNU autotools and CMake.

**Editor integration:** Extended Scheme interface for interactive development workflows. Emacs plugin as the initial editor integration example.

**Documentation and examples:** Thorough language documentation, introductory tutorials, and example projects to onboard new users.

## Future Possibilities

Beyond the Restoration objectives, several interesting directions exist:

- **Re-purposing the compiler:** As demonstrated with the TTCN-3 compiler and Scheme 48 bytecode optimizer, the Pre-Scheme transformation pipeline can serve other source languages by writing alternative front-ends and back-ends.
- **Static analysis tool:** The type reconstruction pass could serve as a static analysis engine for general Scheme code.
- **New backends:** LLVM or WebAssembly targets instead of (or alongside) C.
- **Advanced language features:** User-defined effects, ownership analysis, optional automatic memory management.