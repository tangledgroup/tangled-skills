# Cryptography and Security

## node:crypto — Hashing

### One-Way Hashes

```javascript
import crypto from 'node:crypto';

// SHA-256 hash
const hash = crypto.createHash('sha256');
hash.update('data to hash');
const digest = hash.digest('hex');
console.log(digest); // 69... (hex string)

// One-liner
const hashHex = crypto.createHash('sha256').update('data').digest('hex');

// Available algorithms
crypto.getHashes(); // ['sha1', 'sha256', 'sha512', 'md5', ...]

// Other hash formats
hash.digest('base64');
hash.digest(); // returns Buffer

// Common algorithms: sha256, sha384, sha512, sha1 (legacy), md5 (insecure)
```

### HMAC (Hash-based Message Authentication Code)

```javascript
import crypto from 'node:crypto';

const secret = crypto.randomBytes(32);
const hmac = crypto.createHmac('sha256', secret);
hmac.update('message to sign');
const signature = hmac.digest('hex');

// Verify
const verifyHmac = crypto.createHmac('sha256', secret);
verifyHmac.update('message to sign');
const expectedSig = verifyHmac.digest('hex');
console.log(signature === expectedSig); // true

// Timing-safe comparison (prevent timing attacks)
const a = Buffer.from(signature, 'hex');
const b = Buffer.from(expectedSig, 'hex');
crypto.timingSafeEqual(a, b); // true
```

### Random Bytes

```javascript
import crypto from 'node:crypto';

// Cryptographically secure random bytes
const randomBytes = crypto.randomBytes(32);
const randomHex = crypto.randomBytes(16).toString('hex');
const randomBase64 = crypto.randomBytes(48).toString('base64url');

// Random integer in range [0, max)
const randomInt = crypto.randomInt(0, 100);

// Random UUID (v4)
const uuid = crypto.randomUUID();
// 'f47ac10b-58cc-4372-a567-0e02b2c3d479'

// With options
const uuidWithOptions = crypto.randomUUID({ disableEntropyCache: true });
```

## node:crypto — Symmetric Encryption

### Cipher and Decipher (AES)

```javascript
import crypto from 'node:crypto';

const algorithm = 'aes-256-gcm';
const key = crypto.randomBytes(32); // 256-bit key
const iv = crypto.randomBytes(16);  // 128-bit IV

// Encrypt
const cipher = crypto.createCipheriv(algorithm, key, iv);
let encrypted = cipher.update('plaintext data', 'utf8', 'hex');
encrypted += cipher.final('hex');
const authTag = cipher.getAuthTag(); // GCM auth tag

console.log(encrypted);
console.log(authTag.toString('hex'));

// Decrypt
const decipher = crypto.createDecipheriv(algorithm, key, iv);
decipher.setAuthTag(authTag);
let decrypted = decipher.update(encrypted, 'hex', 'utf8');
decrypted += decipher.final('utf8');

console.log(decrypted); // 'plaintext data'
```

### Key Derivation

```javascript
import crypto from 'node:crypto';

// PBKDF2 — Password-Based Key Derivation Function
const password = 'user-password';
const salt = crypto.randomBytes(16);
const key = crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha256');

// Async version
crypto.pbkdf2(password, salt, 100000, 32, 'sha256', (err, derivedKey) => {
  console.log(derivedKey.toString('hex'));
});

// scrypt — memory-hard KDF
const scryptKey = crypto.scryptSync(password, salt, 32);

// Async version
crypto.scrypt(password, salt, 32, (err, derivedKey) => {
  console.log(derivedKey.toString('hex'));
});
```

## node:crypto — Asymmetric Cryptography

### Key Generation

```javascript
import crypto from 'node:crypto';

// RSA key pair
const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 4096,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
});

// EC key pair
const { privateKey: ecPriv, publicKey: ecPub } = crypto.generateKeyPairSync('ec', {
  namedCurve: 'prime256v1',
});

// Ed25519 (modern, recommended for signatures)
const { privateKey: edPriv, publicKey: edPub } = crypto.generateKeyPairSync('ed25519');

// DSA key pair
const { privateKey: dsaPriv, publicKey: dsaPub } = crypto.generateKeyPairSync('dsa', {
  modulusLength: 2048,
  divisorLength: 256,
});

// Async versions available: crypto.generateKeyPair()
```

### Signing and Verification

```javascript
import crypto from 'node:crypto';

const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
});

// Sign data
const sign = crypto.createSign('SHA256');
sign.update('data to sign');
const signature = sign.sign(privateKey, 'hex');

// Verify signature
const verify = crypto.createVerify('SHA256');
verify.update('data to sign');
const isValid = verify.verify(publicKey, signature, 'hex');
console.log(isValid); // true

// Ed25519 signing (simpler API)
const { privateKey: edPriv, publicKey: edPub } = crypto.generateKeyPairSync('ed25519');
const edSignature = crypto.sign(null, Buffer.from('data to sign'), edPriv);
const edValid = crypto.verify(null, Buffer.from('data to sign'), edPub, edSignature);
```

### KeyObject

```javascript
import crypto from 'node:crypto';

// Create KeyObject from PEM/JWK
const keyObj = crypto.createPrivateKey(privateKeyPem);
const pubKeyObj = crypto.createPublicKey(publicKeyPem);

// Get key info
keyObj.type;        // 'private' or 'public'
keyObj.asymmetricKeyType; // 'rsa', 'ec', 'ed25519', etc.
keyObj.isPrivate(); // true/false

// Export
keyObj.export({ type: 'pkcs8', format: 'pem' });
keyObj.export({ format: 'jwk' });

// Check public key
pubKeyObj.checkPrivateKey(privateKeyObj); // validates key pair match
```

### Diffie-Hellman Key Exchange

```javascript
import crypto from 'node:crypto';

// Alice's keys
const alice = crypto.createDiffieHellman(2048);
alice.generateKeys();

// Bob uses same parameters
const bob = crypto.createDiffieHellman(alice.getPrime(), alice.getGenerator());
bob.generateKeys();

// Exchange public keys and compute shared secret
const aliceShared = alice.computeSecret(bob.getPublicKey());
const bobShared = bob.computeSecret(alice.getPublicKey());

console.log(aliceShared.equals(bobShared)); // true

// Using named groups (simpler)
const aliceGroup = crypto.createDiffieHellmanGroup('secp256k1');
aliceGroup.generateKeys();
const bobGroup = crypto.createDiffieHellmanGroup('secp256k1');
bobGroup.generateKeys();

const shared1 = aliceGroup.computeSecret(bobGroup.getPublicKey());
const shared2 = bobGroup.computeSecret(aliceGroup.getPublicKey());

// Available groups: secp256k1, secp384r1, etc.
crypto.getDiffieHellmanGroups();
```

### ECDH (Elliptic Curve Diffie-Hellman)

```javascript
import crypto from 'node:crypto';

const alice = crypto.createECDH('prime256v1');
alice.generateKeys();

const bob = crypto.createECDH('prime256v1');
bob.generateKeys();

const sharedSecret = alice.computeSecret(bob.getPublicKey());
```

## node:crypto — X.509 Certificates

```javascript
import crypto from 'node:crypto';
import fs from 'node:fs/promises';

// Parse certificate
const certPem = await fs.readFile('certificate.pem', 'utf8');
const x509 = new crypto.X509Certificate(certPem);

// Certificate properties
x509.subject;         // subject name (e.g., '/CN=example.com')
x509.issuer;          // issuer name
x509.serialNumber;    // serial number (hex)
x509.validFrom;       // validity start (ISO string)
x509.validTo;         // validity end (ISO string)
x509.pubKey;          // public key as PEM
x509.signatureAlgorithm; // 'sha256WithRSAEncryption'

// Check validity
x509.checkIssuedBy(otherCert);    // true if issued by otherCert
x509.checkPrivateKey(privateKey); // true if matches private key
x509.verify(publicKey);           // verify signature

// Get Subject Alternative Names
x509.subjectAltName; // 'DNS:example.com,DNS:www.example.com'
```

### Certificate Class

```javascript
import crypto from 'node:crypto';

// Export SPKI from PEM
const spki = crypto.Certificate.exportPublicKey(certPem);

// Export signature from signed CSR
const signature = crypto.Certificate.exportChallenge(csrPem);
```

## node:crypto — Constants and Utilities

```javascript
import crypto from 'node:crypto';

// Random prime generation
const prime = crypto.randomPrime(256, { safe: true });

// Check if prime
crypto.isPrime(Buffer.from('7919', 'hex')); // true
crypto.isPrimeAsync(largeNumberBuffer);      // async for large numbers

// Constants
crypto.constants.OP_NO_TLSv1;
crypto.constants.SSL_OP_NO_SSLv3;
crypto.constants.NSEC_SUPPORT;
```

## webcrypto — Web Crypto API

Node.js implements the browser-compatible Web Crypto API:

```javascript
// Access via global crypto or import
import webcrypto from 'node:webcrypto';
// Or just use globalThis.crypto

// Generate key pair
const keyPair = await crypto.subtle.generateKey(
  { name: 'RSA-OAEP', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
  true, // extractable
  ['encrypt', 'decrypt']
);

// Hash
const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('data'));
const hashHex = Buffer.from(hashBuffer).toString('hex');

// HMAC
const hmacKey = await crypto.subtle.generateKey(
  { name: 'HMAC', hash: 'SHA-256' },
  true,
  ['sign', 'verify']
);
const signature = await crypto.subtle.sign('HMAC', hmacKey, new TextEncoder().encode('message'));
const isValid = await crypto.subtle.verify('HMAC', hmacKey, signature, new TextEncoder().encode('message'));

// AES-GCM encryption
const aesKey = await crypto.subtle.generateKey(
  { name: 'AES-GCM', length: 256 },
  true,
  ['encrypt', 'decrypt']
);
const iv = crypto.getRandomValues(new Uint8Array(12));
const encrypted = await crypto.subtle.encrypt(
  { name: 'AES-GCM', iv },
  aesKey,
  new TextEncoder().encode('secret message')
);
const decrypted = await crypto.subtle.decrypt(
  { name: 'AES-GCM', iv },
  aesKey,
  encrypted
);
console.log(new TextDecoder().decode(decrypted)); // 'secret message'

// Import/export keys
const exportedJwk = await crypto.subtle.exportKey('jwk', keyPair.publicKey);
const importedKey = await crypto.subtle.importKey(
  'jwk',
  exportedJwk,
  { name: 'RSA-OAEP', hash: 'SHA-256' },
  true,
  ['encrypt']
);
```

## tls — TLS/SSL Configuration

### Server Configuration

```javascript
import tls from 'node:tls';
import fs from 'node:fs/promises';

const server = tls.createServer({
  key: await fs.readFile('server-key.pem'),
  cert: await fs.readFile('server-cert.pem'),
  ca: await fs.readFile('ca-cert.pem'), // for client cert verification
  requestCert: true,    // request client certificates
  rejectUnauthorized: true, // reject without valid cert
  // Security settings
  minVersion: 'TLSv1.2',
  maxVersion: 'TLSv1.3',
  ciphers: 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256',
  honorCipherOrder: true,
  // Session resumption
  sessionTimeout: 300,
}, (socket) => {
  const cipher = socket.getCipher();
  console.log(`Cipher: ${cipher.name}, Protocol: ${socket.getProtocol()}`);
  socket.write('Secure connection established\n');
  socket.pipe(socket);
});
```

### Client Configuration

```javascript
const socket = tls.connect(443, 'example.com', {
  rejectUnauthorized: true, // default, verify server cert
  checkServerIdentity: (hostname, cert) => {
    return tls.checkServerIdentity(hostname, cert);
  },
  // Client certificate for mutual TLS
  key: await fs.readFile('client-key.pem'),
  cert: await fs.readFile('client-cert.pem'),
});

socket.on('secureConnect', () => {
  console.log('Authorized:', socket.authorized);
  console.log('Authorization error:', socket.authorizationError);
  console.log('Protocol:', socket.getProtocol());
  console.log('Cipher:', socket.getCipher().name);
  console.log('Peer cert:', socket.getPeerCertificate(true));
});
```

### TLS Constants

```javascript
import tls from 'node:tls';

tls.DEFAULT_MIN_VERSION;  // 'TLSv1.2'
tls.DEFAULT_MAX_VERSION;  // 'TLSv1.3'
tls.DEFAULT_CIPHERS;      // default cipher suite string
tls.rootCertificates;     // array of root CA certificates
tls.getCiphers();         // list of available ciphers
```

## Permission Model

Node.js 21+ includes a permission model for sandboxing:

```bash
# Run with restricted permissions
node --allow-fs-read=/data app.js
node --allow-fs-write=/output app.js
node --allow-env=NODE_ENV,PORT app.js
node --deny-fs-read=/etc/shadow app.js
```

```javascript
// Check permissions programmatically
import { permission } from 'node:process';

if (permission.has('fs', 'read', '/data')) {
  // safe to read
}

if (permission.has('env', 'NODE_ENV')) {
  console.log(process.env.NODE_ENV);
}
```
