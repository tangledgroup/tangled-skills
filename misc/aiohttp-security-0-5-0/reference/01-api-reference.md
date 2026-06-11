# API Reference

## Contents
- Public API Functions
- Abstract Policies
- Built-in Identity Policies

## Public API Functions

**`setup(app, identity_policy, autz_policy)`**

Register security policies on an `aiohttp.web.Application`. Must be called before any request handling.

- `app` — the `web.Application` instance
- `identity_policy` — an `AbstractIdentityPolicy` instance (e.g., `SessionIdentityPolicy()`)
- `autz_policy` — an `AbstractAuthorizationPolicy` instance (developer-implemented)

**`remember(request, response, identity, **kwargs)`**

Store the user's identity in the response (sets cookie, session entry, etc.). Call after successful authentication.

- `request` — the current `web.Request`
- `response` — a `web.StreamResponse` to modify
- `identity` — a string identifying the user (use UUID or hash, not plain usernames)
- `**kwargs` — forwarded to the identity policy (e.g., `max_age` for cookies)

**`forget(request, response)`**

Remove the user's identity from the response (clears cookie/session). Call on logout.

**`authorized_userid(request)` → `Optional[str]`**

Return the current user's ID or `None` if anonymous. Does not raise exceptions.

**`permits(request, permission, context=None)` → `bool`**

Check if the current user has a given permission. Returns `True` or `False`. Permissions can be strings or enums.

**`is_anonymous(request)` → `bool`**

Return `True` if the current request has no authenticated identity.

**`check_authorized(request)` → `str`**

Raise `HTTPUnauthorized` if the user is anonymous; otherwise return the user's ID. Use at the top of handlers that require any logged-in user.

**`check_permission(request, permission, context=None)`**

Raise `HTTPUnauthorized` if anonymous, `HTTPForbidden` if the user lacks the permission. Use to protect routes declaratively.

## Abstract Policies

**`AbstractIdentityPolicy`** — base class for identity policies. Three methods to implement:

- `identify(request)` → `Optional[str]` — extract identity from the request (cookie, session, header)
- `remember(request, response, identity, **kwargs)` — persist identity into the response
- `forget(request, response)` — remove identity from subsequent requests

**`AbstractAuthorizationPolicy`** — base class for authorization policies. Two methods to implement:

- `authorized_userid(identity)` → `Optional[str]` — return the user ID for a given identity, or `None`
- `permits(identity, permission, context=None)` → `bool` — check if an identity has a permission

## Built-in Identity Policies

**`SessionIdentityPolicy(session_key='AIOHTTP_SECURITY')`**

Stores identity in `aiohttp-session`. Requires `aiohttp_session` package. Most commonly used for production applications.

**`CookiesIdentityPolicy()`**

Stores identity directly in an HTTP cookie named `AIOHTTP_SECURITY`. Default max_age is 30 days. Intended for demonstration only — not secure for production use.

- Constructor accepts no arguments
- `remember()` accepts optional `max_age` parameter to override the default 30-day expiry

**`JWTIdentityPolicy(secret, algorithm='HS256', key='login')`**

Reads identity from the `Authorization: Bearer <token>` header. Requires `PyJWT`. Stateless — `remember()` and `forget()` are no-ops since JWT is bearer-token based.

- `secret` — signing secret for JWT verification
- `algorithm` — JWT algorithm (default: `"HS256"`)
- `key` — the claim key within the decoded JWT to extract as identity (default: `"login"`)

Raises `InvalidAuthorizationScheme` if the `Authorization` header does not use the `Bearer` scheme.
