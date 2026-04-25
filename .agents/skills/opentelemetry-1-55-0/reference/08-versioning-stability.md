# Versioning & Stability

**Status**: Stable

## Signal Lifecycle

Each signal follows a lifecycle: Development → Stable → Deprecated → Removed

```
Development ──→ Stable ──→ Deprecated ──→ Removed
    │              │              │             │
    │              │              │             └── Major version bump
    │              │              └── Same guarantees as stable
    │              └── Full backward compatibility
    └── Breaking changes possible, no long-term deps
```

### Development

- Breaking changes and performance issues MAY occur
- Components SHOULD NOT be expected to be feature-complete
- Signal MAY be discarded entirely
- Long-term dependencies SHOULD NOT be taken against development signals
- "Development" was previously called "Experimental" — treated identically

### Stable

Once stable, the following guarantees apply:

#### API Stability
- Backward-incompatible changes require major version increment
- All existing API calls compile and function in all future minor versions
- Binary artifacts SHOULD offer ABI compatibility

#### SDK Stability
- Public portions (plugin interfaces + constructors) remain backward compatible
- Plugin interfaces: SpanProcessor, Exporter, Sampler
- Constructors: configuration objects, environment variables, SDK builders
- Binary artifacts SHOULD offer ABI compatibility

#### Extending Stable APIs
- New optional parameters via method overloading (backward-compatible)
- New methods on plugin interfaces with default implementations
- New methods in Development maturity level are possible and not breaking for non-users
- New Development methods SHOULD require opt-in

### Deprecated
- Replacement MUST be stable before deprecation
- Same support guarantees as stable code
- Not removed until major version bump

### Removed
- End of support for the signal
- Requires major version bump
- No plans for v2.0 — instead, new incompatible signals coexist with old ones

## Version Numbers

OpenTelemetry follows Semantic Versioning 2.0.0 with clarifications:

### Component Versioning

| Component | Version Scope | Notes |
|-----------|--------------|-------|
| API (all signals) | Single version across all signals | All stable APIs version together |
| SDK (all signals) | Single version across all signals | All stable SDKs version together |
| Semantic Conventions | Single version | — |
| Contrib packages | Independent per package | MAY have own version numbers |

### Independence Rules

- API, SDK, Semantic Conventions, and Contrib have **independent** version numbers
  - Example: `opentelemetry-python-api` v1.2.3 while `opentelemetry-python-sdk` v2.3.1
- Different languages have **independent** version numbers
  - Example: Python API v1.2.8 when Java API is v1.3.2
- Language implementations are independent of the spec they implement
  - Example: v1.8.2 of `opentelemetry-python-api` may implement v1.1.1 of the specification

### Development Signal Exception

Signals in Development MAY version independently (0.X) to retain pre-1.0 status. When a signal becomes stable, its version MUST be bumped to match other stable signals.

## Version Bump Rules

### Major Version Bump
- Breaking change to a stable interface
- Removal of a deprecated signal
- SHOULD NOT occur for non-breaking changes

### Minor Version Bump
Most changes result in minor version bump:
- New backward-compatible functionality
- Breaking changes to internal SDK components
- Breaking changes to development signals
- New signals in Development added
- Signals in Development become stable
- Stable signals are deprecated

### Patch Version Bump
No recompilation or application code breakage:
- Bug fixes not requiring minor version bump
- Security fixes
- Documentation

**Note**: No backporting of bug/security fixes to prior minor versions — only latest minor version receives fixes.

## Long Term Support

### API Support
- **Minimum 3 years** after release of next major API version
- Latest minor of last major API version maintained during LTS
- Bug and security fixes backported
- Additional feature development NOT recommended

### SDK Support
- **Minimum 1 year** after release of next major SDK version
- Stability guarantees maintained

### Contrib Support
- **Minimum 1 year** after release of next major contrib package version
- Stability guarantees maintained

## OpenTelemetry GA Requirements

Minimum requirements for declaring General Availability:
- Stable tracing AND metrics in at least 4 languages
- CI/CD, performance, and integration tests implemented for these languages

## Semantic Conventions Stability

### Breaking Changes
Breaking changes to semantic conventions MUST be described by schema files (Schema File Format v1.0.0 or v1.1.0) and published in the specification repository.

**Allowed via schema transformation**:
- Renaming of span, metric, log, and resource attributes
- Renaming of metrics
- Renaming of span events

**Always allowed (no schema needed)**:
- Adding new attributes to existing semantic conventions
- Adding new attributes that don't break existing timeseries
- Adding semantic conventions for new types of resources, spans, events, metrics, or logs

### Stability Guarantees

The following telemetry fields are covered by stability guarantees (after schema transformations):
- Resource attribute keys and Entity References
- InstrumentationScope attribute keys and well-known values
- Span: name, kind, attribute keys/values, event names/attributes
- Metrics: name, kind, unit, data point attribute keys/values
- LogRecord: attribute keys/values, event name

### NOT Stable (Allowed to Change)
- Attribute values (except well-known value lists)
- Span links
- Measurement type (float vs integer)
- Metric description
- Recorded measurement values

## Hard-Coded Resource Attributes

The following resource attributes MUST NEVER change — they are hard-coded in the specification:
- `service.*` attributes (embedded in various spec sections)
- These have corresponding environment variables defined in general SDK configuration
