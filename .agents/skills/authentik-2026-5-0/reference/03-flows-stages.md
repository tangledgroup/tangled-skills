# Flows, Stages, and Policies

## Contents
- Flow Designations
- Flow Configuration
- Stage Types
- Stage Bindings
- Executors
- Flow Context
- Policy Types
- Policy Bindings and Evaluation

## Flow Designations

Flows are designated for a single purpose. The designation changes how the flow is used:

| Designation | Purpose | Required Final Stage |
|---|---|---|
| **Authentication** | User login | User Login |
| **Authorization** | App access verification | None (implicit/explicit per provider) |
| **Enrollment** | New user registration | User Write |
| **Invalidation** | Session logout | User Logout (optional) |
| **Recovery** | Password/account recovery | User Write |
| **Stage Configuration** | General setup (e.g., TOTP enrollment) | None |
| **Unenrollment** | Account deletion | User Delete |

**Default flows**: `default-authentication-flow`, `default-provider-authorization-explicit-consent`, `default-invalidation-flow`, `default-provider-invalidation-flow`. Default flows are created by blueprints and can be overridden or extended.

## Flow Configuration

- **Name/Title/Slug**: Display name, user-facing title, URL slug
- **Authentication requirement**: None, authenticated user, superuser only, redirect-only, outpost-required
- **Compatibility mode**: Polyfill Shadow DOM for password manager compatibility on mobile
- **Denied action**: `MESSAGE_CONTINUE` (default), `MESSAGE`, `CONTINUE`
- **Policy engine mode**: Any policy passes or All policies must pass
- **Layout/Appearance**: Stacked, content left/right, sidebar left/right, background image

**Evaluate when flow is planned**: When enabled on a stage binding, all policies are evaluated at flow start and a complete plan is generated. By default, policies evaluate dynamically right before each stage.

## Stage Types

### Authentication Stages
- **Identification**: Username/email prompt, configurable fields
- **Password**: Password verification against stored hash
- **Email**: Send verification link, block until clicked
- **Source**: Authenticate via an external source (LDAP, SAML, OAuth social login)
- **Mutual TLS (mTLS)**: Client certificate authentication
- **Endpoint**: Device-based authentication check

### Authenticator Stages
- **Authenticator Validation**: Validate any configured authenticator
- **TOTP Setup**: Configure Time-based One-Time Password
- **WebAuthn/Passkeys Setup**: FIDO2/WebAuthn credential registration
- **Duo Setup**: DUO Security integration
- **Static Keys Setup**: Backup code generation
- **SMS Authenticator Setup**: SMS-based verification
- **Email Authenticator Setup**: Email-based one-time codes
- **Google Chrome Device Trust**: GDT authenticator

### User Management Stages
- **User Login**: Attach pending user to session
- **User Logout**: End authentik session, trigger Single Logout
- **User Write**: Save pending data to user (create or update)
- **User Delete**: Delete the pending user

### Control Flow Stages
- **Consent**: User approval prompt
- **Deny**: Static deny, usable with policies
- **Prompt**: Arbitrary input prompts with validation
- **Redirect**: Redirect to another flow
- **Invitation**: Limit flow to invited users
- **Captcha**: CAPTCHA challenge
- **Account Lockdown**: Account lockout enforcement

## Stage Bindings

Bind stages to a flow in ordered sequence. Each binding can have:
- Order position
- Policies that gate the stage (evaluated before presenting)
- "Evaluate when flow is planned" toggle for pre-computation

## Executors

Executors control conditional flow logic within a flow plan:
- **If-Flow**: Conditional branching based on policy evaluation
- Execute different stage sequences based on runtime conditions

## Flow Context

Each flow execution has an independent context holding arbitrary data. Stages and policies read/write context data. Context includes:
- User data (pending user, authenticated user)
- Request metadata (IP, user-agent, headers)
- Stage outputs (identification results, policy decisions)
- Custom data set by expression policies

Use the Flow Inspector to step through flow execution and observe context at each stage.

## Policy Types

| Type | Use Case |
|---|---|
| **Expression** | Custom Python logic — most flexible, inspects flow context, user data, request metadata |
| **Event Matcher** | Match authentik events for notifications/automations (action, app, model, client IP) |
| **GeoIP** | Allow/deny by country, ASN, or impossible-travel detection |
| **Password** | Validate complexity, HIBP exposure, zxcvbn strength |
| **Password Expiry** | Expire passwords after N days; deny login or mark unusable |
| **Password Uniqueness** | Prevent password reuse (enterprise) |
| **Reputation** | React to failed logins/suspicious activity (e.g., show CAPTCHA for low-reputation requests) |

## Policy Bindings and Evaluation

Policies bind to flows, stage bindings, applications, or sources. The target object combines all bound policies using:
- **Any mode**: Flow succeeds if any policy passes
- **All mode**: All policies must pass

User/group direct bindings are evaluated as simple allow/deny checks alongside policies.
