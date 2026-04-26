# Two-Factor Authentication

Implements HOTP (RFC 4226) and TOTP (RFC 6238) one-time password algorithms.

## HOTP (HMAC-Based One-Time Password)

Counter-based OTP:

```python
import os
from cryptography.hazmat.primitives.twofactor.hotp import HOTP
from cryptography.hazmat.primitives.hashes import SHA1

key = os.urandom(20)  # 160-bit key recommended
hotp = HOTP(key, 6, SHA1())  # 6-digit codes

# Generate code for counter value
code = hotp.generate(counter=0)

# Verify code
hotp.verify(code, counter=0)

# Provisioning URI for authenticator apps
uri = hotp.get_provisioning_uri("alice@example.com", counter=0, issuer="MyApp")
```

Parameters: `key` (128-bit minimum, 160-bit recommended), `length` (6–8 digits), `algorithm` (SHA1, SHA256, or SHA512).

### Throttling

Due to short token length (6–8 digits), brute force is possible. Implement server-side throttling that locks out accounts after N failed attempts.

### Counter Re-synchronization

Client and server counters can drift. Use a look-ahead window:

```python
def verify_with_lookahead(hotp_value, counter, look_ahead=4):
    otp = HOTP(key, 6, SHA1())
    for count in range(counter, counter + look_ahead):
        try:
            otp.verify(hotp_value, count)
            return count  # found matching counter
        except InvalidToken:
            pass
    return None  # no match
```

Increment the server counter only on successful authentication.

## TOTP (Time-Based One-Time Password)

Time-based OTP — derives counter from current time:

```python
import os, time
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from cryptography.hazmat.primitives.hashes import SHA1

key = os.urandom(20)
totp = TOTP(key, 8, SHA1(), time_step=30)  # 8-digit codes, 30-second step

code = totp.generate(time.time())
totp.verify(code, time.time())
```

Parameters: `key`, `length` (6–8), `algorithm`, `time_step` (seconds, typically 30).

### Provisioning URI

```python
uri = totp.get_provisioning_uri("alice@example.com", issuer="MyApp")
# Returns otpauth://totp/MyApp:alice@example.com?secret=...&issuer=MyApp
```

## InvalidToken Exception

Raised when the computed OTP does not match the provided token.
