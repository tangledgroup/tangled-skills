# X.509 Certificates

X.509 certificates bind public keys to identities. This reference covers certificate creation, parsing, verification, and related protocols (OCSP, CRL).

## Certificate Structure

An X.509 certificate contains:
- **Subject:** Entity the certificate identifies
- **Issuer:** Certificate Authority that signed it
- **Public Key:** Subject's public key
- **Validity Period:** Not Before / Not After dates
- **Extensions:** Additional information (SAN, key usage, etc.)
- **Signature:** Issuer's digital signature

## Creating Self-Signed Certificates

### Basic Self-Signed Certificate

```python
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
import datetime

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Build subject/issuer name (same for self-signed)
subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Org"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])

# Build certificate
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(subject)  # Same as subject for self-signed
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    )
    .sign(private_key, hashes.SHA256())
)

# Save certificate
with open("certificate.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

# Save private key
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))
```

### Certificate with Subject Alternative Names (SAN)

```python
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
import datetime

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

subject = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "example.com"),
])

# Add Subject Alternative Names
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(subject)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    .add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("example.com"),
            x509.DNSName("www.example.com"),
            x509.DNSName("api.example.com"),
            x509.IPAddress(ipaddress.ip_address("192.168.1.1")),
        ]),
        critical=False,
    )
    .sign(private_key, hashes.SHA256())
)
```

### Certificate with Key Usage Extensions

```python
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    .add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=True,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    .add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
        ]),
        critical=False,
    )
    .sign(issuer_key, hashes.SHA256())
)
```

## Creating CA and Signing Certificates

### Root CA Certificate

```python
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
import datetime

# Generate CA key (use 4096 bits for CAs)
ca_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)

ca_subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My CA"),
    x509.NameAttribute(NameOID.COMMON_NAME, "My Root CA"),
])

ca_cert = (
    x509.CertificateBuilder()
    .subject_name(ca_subject)
    .issuer_name(ca_subject)  # Self-signed
    .public_key(ca_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=10*365))  # 10 years
    .add_extension(
        x509.BasicConstraints(ca=True, path_length=0),  # CA certificate
        critical=True,
    )
    .add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_cert_sign=True,
            crl_sign=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    .sign(ca_key, hashes.SHA256())
)
```

### Signing End-Entity Certificate with CA

```python
# Generate end-entity key
ee_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

ee_subject = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "www.example.com"),
])

# Sign with CA
ee_cert = (
    x509.CertificateBuilder()
    .subject_name(ee_subject)
    .issuer_name(ca_cert.subject)  # Issuer is the CA
    .public_key(ee_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    .add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("www.example.com"),
            x509.DNSName("example.com"),
        ]),
        critical=False,
    )
    .sign(ca_key, hashes.SHA256())  # Sign with CA private key
)
```

## Parsing Certificates

### Loading Certificates

```python
from cryptography import x509
from cryptography.hazmat.primitives import serialization

# Load PEM certificate
with open("certificate.pem", "rb") as f:
    cert = x509.load_pem_x509_certificate(f.read())

# Load DER certificate
with open("certificate.der", "rb") as f:
    cert = x509.load_der_x509_certificate(f.read())

# Load from multiple PEM certificates (e.g., bundle)
with open("bundle.pem", "rb") as f:
    certs = x509.load_pem_x509_certificates(f.read())
```

### Reading Certificate Fields

```python
# Subject and issuer
print(cert.subject.rfc4514_string())  # "CN=example.com,O=Org,C=US"
print(cert.issuer.rfc4514_string())

# Get specific attributes
common_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
country = cert.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value

# Validity period
print(f"Valid from: {cert.not_valid_before_utc}")
print(f"Valid until: {cert.not_valid_after_utc}")

# Public key
public_key = cert.public_key()
print(f"Key type: {type(public_key).__name__}")

# Serial number
print(f"Serial: {cert.serial_number}")

# Version
print(f"Version: {cert.version}")  # x509.Version.v3
```

### Reading Extensions

```python
# Subject Alternative Names
try:
    san = cert.extensions.get_extension_for_oid(
        ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    )
    for name in san.value:
        print(f"  {name.value}")
except x509.ExtensionNotFound:
    print("No SAN extension")

# Key Usage
try:
    key_usage = cert.extensions.get_extension_for_oid(
        ExtensionOID.KEY_USAGE
    )
    print(f"Digital Signature: {key_usage.value.digital_signature}")
    print(f"Key Encipherment: {key_usage.value.key_encipherment}")
except x509.ExtensionNotFound:
    pass

# Basic Constraints
try:
    basic_constraints = cert.extensions.get_extension_for_oid(
        ExtensionOID.BASIC_CONSTRAINTS
    )
    print(f"Is CA: {basic_constraints.value.ca}")
    if basic_constraints.value.ca:
        print(f"Path Length: {basic_constraints.value.path_length}")
except x509.ExtensionNotFound:
    pass

# Iterate all extensions
for ext in cert.extensions:
    print(f"{ext.oid._name}: {ext.value}")
```

## Certificate Verification

### Basic Validation

```python
import datetime

def is_certificate_valid(cert: x509.Certificate) -> bool:
    """Check if certificate is currently valid."""
    now = datetime.datetime.utcnow()
    return cert.not_valid_before_utc <= now <= cert.not_valid_after_utc

def has_valid_cn(cert: x509.Certificate, expected_cn: str) -> bool:
    """Check if certificate CN matches expected value."""
    try:
        cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        return cn == expected_cn
    except IndexError:
        return False

def has_san(cert: x509.Certificate, hostname: str) -> bool:
    """Check if certificate has hostname in SAN."""
    try:
        san = cert.extensions.get_extension_for_oid(
            ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        )
        for name in san.value:
            if isinstance(name, x509.DNSName) and name.value == hostname:
                return True
        return False
    except x509.ExtensionNotFound:
        return False
```

### Chain Verification

```python
from cryptography.hazmat.primitives.asymmetric import padding

def verify_signature(cert: x509.Certificate, issuer_cert: x509.Certificate) -> bool:
    """Verify certificate was signed by issuer."""
    try:
        issuer_public_key = issuer_cert.public_key()
        
        # Get signature algorithm
        sig_alg = cert.signature_algorithm_oid
        
        # Verify signature (simplified - real implementation needs proper padding)
        if isinstance(issuer_public_key, rsa.RSAPublicKey):
            issuer_public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert.signature_hash_algorithm
            )
            return True
        # Handle other key types...
        
        return False
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

def verify_chain(leaf_cert: x509.Certificate, intermediates: list, root_cert: x509.Certificate) -> bool:
    """Verify certificate chain."""
    # Verify leaf signed by intermediate (or root if no intermediates)
    current = leaf_cert
    issuers = intermediates + [root_cert]
    
    for issuer in issuers:
        if verify_signature(current, issuer):
            if issuer == root_cert:
                return True
            # Move up chain
            current = issuer
            break
    
    return False
```

## Certificate Revocation

### CRL (Certificate Revocation List)

```python
from cryptography import x509
from cryptography.x509.oid import ExtensionOID

# Load CRL
with open("crl.pem", "rb") as f:
    crl = x509.load_pem_x509_crl(f.read())

# Check if certificate is revoked
def is_revoked(cert: x509.Certificate, crl: x509.X509CRL) -> bool:
    """Check if certificate serial is in CRL."""
    for revoked_cert in crl:
        if revoked_cert.serial_number == cert.serial_number:
            return True
    return False

# Parse CRL info
print(f"Issuer: {crl.issuer}")
print(f"Last update: {crl.last_update_utc}")
print(f"Next update: {crl.next_update_utc}")
```

### OCSP (Online Certificate Status Protocol)

```python
from cryptography.x509.ocsp import OCSPRequestBuilder, OCSPResponseStatus

# Build OCSP request
request_builder = OCSPRequestBuilder()
request_builder = request_builder.add_certificate(cert, issuer_cert, hashes.SHA256())
request = request_builder.build()

# Send to OCSP responder (requires HTTP client)
import requests

ocsp_url = cert.extensions.get_extension_for_oid(
    ExtensionOID.AUTHORITY_INFORMATION_ACCESS
).value.other_names[0].access_location.value

response_data = requests.post(ocsp_url, data=request.public_bytes(serialization.Encoding.DER)).content

# Parse response
from cryptography.x509.ocsp import OCSPResponse, OCSPCertStatus
response = OCSPResponse.load_der(response_data)

if response.response_status != OCSPResponseStatus.SUCCESSFUL:
    raise Exception(f"OCSP failed: {response.response_status}")

cert_status = response.certificate_status
if cert_status == OCSPCertStatus.GOOD:
    print("Certificate is valid")
elif cert_status == OCSPCertStatus.REVOKED:
    print("Certificate is revoked")
```

## Certificate Transparency

### CT Logs and SCTs

```python
from cryptography.x509.oid import ExtensionOID

# Extract SCT (Signed Certificate Timestamp) from certificate
try:
    sct_list = cert.extensions.get_extension_for_oid(
        ExtensionOID.PRE_CERTIFICATE_SCTS
    )
    print(f"Found {len(sct_list.value)} SCTs")
except x509.ExtensionNotFound:
    print("No SCT extension found")

# Parse CT log entry (requires ct module)
import ct

log_entry = ct.LogEntry.from_data(sct_data)
print(f"Log ID: {log_entry.log_id}")
print(f"Timestamp: {log_entry.timestamp}")
```

## Serialization

### Export Certificates

```python
from cryptography.hazmat.primitives import serialization

# PEM format (base64-encoded, human-readable)
pem = cert.public_bytes(serialization.Encoding.PEM)

# DER format (binary, compact)
der = cert.public_bytes(serialization.Encoding.DER)

# Save to file
with open("cert.pem", "wb") as f:
    f.write(pem)
```

### Certificate Bundle

```python
def create_bundle(certificates: list, filename: str):
    """Create PEM bundle of certificates."""
    with open(filename, "wb") as f:
        for cert in certificates:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
```

## Common Patterns

### TLS Server Certificate Generation

```python
def generate_tls_cert(
    common_name: str,
    alt_names: list = None,
    key_size: int = 2048,
    validity_days: int = 365,
):
    """Generate self-signed TLS certificate."""
    
    # Generate key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    
    # Build name
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    # Build cert
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=validity_days))
    )
    
    # Add SAN if provided
    if alt_names:
        san_names = [x509.DNSName(name) for name in alt_names]
        builder = builder.add_extension(
            x509.SubjectAlternativeName(san_names),
            critical=False,
        )
    
    # Add key usage
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    builder = builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    
    cert = builder.sign(private_key, hashes.SHA256())
    
    return private_key, cert

# Usage
key, cert = generate_tls_cert(
    common_name="localhost",
    alt_names=["localhost", "127.0.0.1"],
    validity_days=365,
)
```
