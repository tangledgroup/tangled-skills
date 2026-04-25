# Cryptography and Security Reference

This document covers Node.js 24.14 cryptographic APIs, TLS/SSL configuration, and the permission model.

## Crypto Module

### Hash Functions

#### SHA-256 Hashing

```javascript
import crypto from 'node:crypto';

// Synchronous hashing
const hash = crypto.createHash('sha256');
hash.update('Hello World');
const digest = hash.digest('hex');
console.log(digest); // 315f5bdb...

// One-line hashing
const quickHash = crypto.createHash('sha256').update('Hello World').digest('hex');

// Hash a file
import fs from 'node:fs/promises';

async function hashFile(filepath) {
  const data = await fs.readFile(filepath);
  return crypto.createHash('sha256').update(data).digest('hex');
}

// Available hash algorithms
console.log(crypto.getHashes()); // ['MD4', 'MD5', 'SHA1', 'SHA256', 'SHA512', ...]
```

#### Password Hashing with PBKDF2

```javascript
import crypto from 'node:crypto';

function generateSalt() {
  return crypto.randomBytes(32).toString('hex');
}

function hashPassword(password, salt) {
  return crypto.pbkdf2Sync(
    password,
    salt,
    100000,  // Iterations
    64,      // Key length
    'sha256'
  ).toString('hex');
}

function verifyPassword(password, salt, hashedPassword) {
  const hash = hashPassword(password, salt);
  return crypto.timingSafeEqual(
    Buffer.from(hash),
    Buffer.from(hashedPassword)
  );
}

// Usage
const salt = generateSalt();
const hash = hashPassword('my-secret-password', salt);

console.log('Store:', { salt, hash });

const isValid = verifyPassword('my-secret-password', salt, hash);
console.log('Valid:', isValid); // true
```

#### HMAC (Hash-based Message Authentication)

```javascript
import crypto from 'node:crypto';

const secret = 'my-secret-key';

// Create HMAC signature
function signMessage(message, secretKey) {
  const hmac = crypto.createHmac('sha256', secretKey);
  hmac.update(message);
  return hmac.digest('hex');
}

// Verify HMAC signature
function verifyMessage(message, signature, secretKey) {
  const expected = signMessage(message, secretKey);
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}

// Usage
const message = 'Important data';
const signature = signMessage(message, secret);

console.log('Signature:', signature);
console.log('Valid:', verifyMessage(message, signature, secret)); // true
console.log('Invalid:', verifyMessage('Tampered', signature, secret)); // false
```

### Random Number Generation

#### Cryptographically Secure Random

```javascript
import crypto from 'node:crypto';

// Generate random bytes
const randomBytes = crypto.randomBytes(32);
console.log(randomBytes.toString('hex'));

// Generate random integer
const randomInt = crypto.randomInt(0, 100);
console.log(randomInt); // 0-99

// Generate UUID v4
function generateUUID() {
  return crypto.randomUUID();
}
console.log(generateUUID()); // '123e4567-e89b-12d3-a456-426614174000'

// Generate secure token
function generateToken(length = 32) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let token = '';
  
  const randomValues = crypto.randomBytes(length);
  for (let i = 0; i < length; i++) {
    token += chars[randomValues[i] % chars.length];
  }
  
  return token;
}
console.log(generateToken());
```

### Public Key Cryptography

#### RSA Key Generation

```javascript
import crypto from 'node:crypto';
import fs from 'node:fs/promises';

// Generate RSA key pair (2048-bit)
async function generateRSAKeys() {
  const { privateKey, publicKey } = crypto.generateKeyPairSync(
    'rsa',
    {
      modulusLength: 2048,
      publicKeyEncoding: {
        type: 'spki',
        format: 'pem'
      },
      privateKeyEncoding: {
        type: 'pkcs8',
        format: 'pem'
      }
    }
  );
  
  // Save to files
  await fs.writeFile('private-key.pem', privateKey);
  await fs.writeFile('public-key.pem', publicKey);
  
  return { privateKey, publicKey };
}

const { privateKey, publicKey } = await generateRSAKeys();
```

#### RSA Encryption/Decryption

```javascript
import crypto from 'node:crypto';

// Encrypt with public key
function encryptWithPublicKey(data, publicKey) {
  const encrypted = crypto.publicEncrypt(
    {
      key: publicKey,
      padding: crypto.constants.RSA_PKCS1_OAEP_PADDING
    },
    Buffer.from(data)
  );
  return encrypted.toString('base64');
}

// Decrypt with private key
function decryptWithPrivateKey(encryptedData, privateKey) {
  const encrypted = Buffer.from(encryptedData, 'base64');
  const decrypted = crypto.privateDecrypt(
    {
      key: privateKey,
      padding: crypto.constants.RSA_PKCS1_OAEP_PADDING
    },
    encrypted
  );
  return decrypted.toString();
}

// Usage
const message = 'Secret message';
const encrypted = encryptWithPublicKey(message, publicKey);
const decrypted = decryptWithPrivateKey(encrypted, privateKey);

console.log('Original:', message);
console.log('Decrypted:', decrypted);
```

#### RSA Signing/Verification

```javascript
import crypto from 'node:crypto';

// Sign data with private key
function signData(data, privateKey) {
  const signer = crypto.createSign('SHA256');
  signer.update(data);
  signer.end();
  return signer.sign(privateKey).toString('base64');
}

// Verify signature with public key
function verifySignature(data, signature, publicKey) {
  const verifier = crypto.createVerify('SHA256');
  verifier.update(data);
  verifier.end();
  return verifier.verify(publicKey, signature, 'base64');
}

// Usage
const data = 'Important document content';
const signature = signData(data, privateKey);

console.log('Signature:', signature);
console.log('Valid:', verifySignature(data, signature, publicKey)); // true
console.log('Invalid:', verifySignature('Tampered', signature, publicKey)); // false
```

### Symmetric Encryption (AES)

```javascript
import crypto from 'node:crypto';

function generateKey() {
  return crypto.randomBytes(32); // 256-bit key for AES-256
}

function encrypt(data, key) {
  const iv = crypto.randomBytes(16); // 128-bit IV
  
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  
  let encrypted = cipher.update(data, 'utf8', 'base64');
  encrypted += cipher.final('base64');
  
  const authTag = cipher.getAuthTag();
  
  return {
    iv: iv.toString('base64'),
    data: encrypted,
    authTag: authTag.toString('base64')
  };
}

function decrypt(encryptedObj, key) {
  const iv = Buffer.from(encryptedObj.iv, 'base64');
  const authTag = Buffer.from(encryptedObj.authTag, 'base64');
  
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(authTag);
  
  let decrypted = decipher.update(encryptedObj.data, 'base64', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
}

// Usage
const key = generateKey();
const plaintext = 'Secret information';

const encrypted = encrypt(plaintext, key);
console.log('Encrypted:', encrypted);

const decrypted = decrypt(encrypted, key);
console.log('Decrypted:', decrypted);
```

### X.509 Certificates

```javascript
import crypto from 'node:crypto';
import fs from 'node:fs/promises';

// Load and inspect certificate
async function inspectCertificate(certPath) {
  const certPem = await fs.readFile(certPath, 'utf8');
  const certificate = crypto.createX509Certificate(certPem);
  
  console.log('Subject:', certificate.subject);
  console.log('Issuer:', certificate.issuer);
  console.log('Valid from:', certificate.validFrom);
  console.log('Valid to:', certificate.validTo);
  console.log('Serial:', certificate.serialNumber);
  console.log('Public key:', certificate.publicKey);
  
  // Check if expired
  console.log('Expired:', certificate.checkExpiration());
}

// Verify certificate signature
function verifyCertificate(certPem, caPem) {
  const cert = crypto.createX509Certificate(certPem);
  const ca = crypto.createX509Certificate(caPem);
  
  try {
    cert.checkIssuer(ca);
    console.log('Certificate issued by CA');
  } catch (err) {
    console.log('Certificate not issued by CA');
  }
}
```

## TLS Module

### TLS Server Configuration

```javascript
import tls from 'node:tls';
import fs from 'node:fs';

const serverOptions = {
  key: fs.readFileSync('server-key.pem'),
  cert: fs.readFileSync('server-cert.pem'),
  
  // Protocol versions to support
  secureProtocol: 'TLS_method', // Supports all TLS versions
  
  // Or specify minimum version
  // minVersion: 'TLSv1.2',
  // maxVersion: 'TLSv1.3',
  
  // Cipher suites (optional, defaults are secure)
  ciphers: [
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-CHACHA20-POLY1305'
  ].join(':'),
  
  // Elliptic curves
  ecdhCurve: 'X25512:P-256:P-384:P-521',
  
  // Client certificate verification
  requestCert: true,
  rejectUnauthorized: false, // Set to true in production
  
  // Session caching for performance
  sessionTimeout: 300, // seconds
  SNICallback: (hostname, done) => {
    // SNI-based virtual hosting
    done(null, tls.createSecureContext(optionsForHostname));
  }
};

const server = tls.createServer(serverOptions, (socket) => {
  // Get client certificate
  const cert = socket.getPeerCertificate();
  if (cert) {
    console.log('Client authenticated:', cert.subjectCN);
  }
  
  socket.write('Welcome to secure server\n');
  socket.pipe(socket); // Echo
});

server.listen(443, () => {
  console.log('TLS server running on port 443');
});
```

### TLS Client Configuration

```javascript
import tls from 'node:tls';
import fs from 'node:fs';

const clientOptions = {
  host: 'secure.example.com',
  port: 443,
  
  // Server certificate verification
  rejectUnauthorized: true, // Default, don't disable in production
  
  // Custom CA certificates
  ca: fs.readFileSync('ca-cert.pem'),
  
  // Client certificate for mutual TLS
  key: fs.readFileSync('client-key.pem'),
  cert: fs.readFileSync('client-cert.pem'),
  
  // SNI hostname
  servername: 'secure.example.com',
  
  // Protocol version
  secureProtocol: 'TLSv1_2_method',
  
  // Cipher suites
  ciphers: 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384'
};

const socket = tls.connect(clientOptions, () => {
  console.log('Connected to TLS server');
  
  // Get server certificate
  const cert = socket.getPeerCertificate();
  console.log('Server CN:', cert.subjectCN);
  console.log('Issuer:', cert.issuerCN);
  
  // Check if connection is encrypted
  console.log('Encrypted:', socket.authorized);
  
  if (!socket.authorized) {
    console.error('Authorization error:', socket.authorizationError);
    socket.end();
    return;
  }
  
  socket.write('Hello from TLS client\n');
});

socket.on('data', (data) => {
  console.log('Received:', data.toString());
});

socket.on('secureConnect', () => {
  console.log('Secure connection established');
});

socket.on('error', (err) => {
  console.error('TLS error:', err);
});
```

### HTTPS Server (Built on TLS)

```javascript
import https from 'node:https';
import fs from 'node:fs';

const options = {
  key: fs.readFileSync('server-key.pem'),
  cert: fs.readFileSync('server-cert.pem'),
  
  // OCSP stapling for certificate validation
  ocspResponseCallback: (hostname, callback) => {
    // Fetch and return OCSP response
    callback(null, ocspResponse);
  }
};

const server = https.createServer(options, (req, res) => {
  // Check TLS connection details
  const tlsSocket = req.socket;
  
  console.log('Protocol:', tlsSocket.getProtocol()); // e.g., TLSv1.3
  console.log('Cipher:', tlsSocket.getCipher().name); // e.g., ECDHE-RSA-AES256-GCM-SHA384
  console.log('Key exchange:', tlsSocket.getPeerCertificate().issuerCN);
  
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Secure response\n');
});

server.listen(443, () => {
  console.log('HTTPS server on port 443');
});
```

## Permissions Module

### Permission Model (Node.js 21+)

```javascript
// Run with: node --permission app.js

import { createRequire } from 'node:module';
import { permissions } from 'node:permissions';

// Check if permission is granted
async function checkPermission(permission) {
  const status = await permissions.requestPermission(permission);
  console.log(`${permission}: ${status}`); // 'granted' or 'denied'
}

// Request specific permissions
await checkPermission('fs-read');
await checkPermission('fs-write');
await checkPermission('net');
await checkPermission('env');
await checkPermission('child-process');

// Check with options
const fsReadStatus = await permissions.requestPermission({
  name: 'fs-read',
  paths: ['/etc/passwd']
});
```

### Running with Permissions

```bash
# Enable permission model
node --permission app.js

# Allow specific permissions
node --allow-fs-read=/home/user --allow-env=NODE_ENV app.js

# Allow network to specific hosts
node --allow-net=api.example.com,localhost app.js

# Deny specific operations
node --disallow-fs-write app.js

# Combine allow and disallow
node --allow-fs-read=* --disallow-fs-write=/etc app.js
```

### Permission-Aware Code

```javascript
import fs from 'node:fs/promises';
import { permissions } from 'node:permissions';

async function safeReadFile(filepath) {
  // Check permission before attempting operation
  const status = await permissions.requestPermission({
    name: 'fs-read',
    paths: [filepath]
  });
  
  if (status === 'denied') {
    throw new Error(`Permission denied to read ${filepath}`);
  }
  
  return await fs.readFile(filepath, 'utf8');
}

// Usage
try {
  const content = await safeReadFile('/etc/passwd');
  console.log(content);
} catch (err) {
  console.error('Cannot read file:', err.message);
}
```

## Security Best Practices

### Input Validation

```javascript
import crypto from 'node:crypto';

// Validate and sanitize user input
function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Hash sensitive data before storage
function hashSensitiveData(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

// Use parameterized queries (example with placeholder)
function safeQuery(userId) {
  // Never: `SELECT * FROM users WHERE id = ${userId}`
  // Always use parameterized queries from your DB library
  return { query: 'SELECT * FROM users WHERE id = ?', params: [userId] };
}
```

### Secure Random for Tokens

```javascript
import crypto from 'node:crypto';

// Generate CSRF token
function generateCSRFToken() {
  return crypto.randomBytes(32).toString('hex');
}

// Generate session ID
function generateSessionID() {
  return crypto.randomUUID();
}

// Generate password reset token
function generateResetToken() {
  return crypto.randomBytes(48).toString('hex');
}

// Never use Math.random() for security purposes!
```

### Environment Variable Security

```javascript
import process from 'node:process';

// Validate required environment variables
function validateEnv() {
  const required = ['DATABASE_URL', 'API_SECRET'];
  const missing = required.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    throw new Error(`Missing environment variables: ${missing.join(', ')}`);
  }
}

// Don't log sensitive data
function safeLog(obj) {
  const sensitiveKeys = ['password', 'secret', 'token', 'key'];
  const sanitized = {};
  
  for (const [key, value] of Object.entries(obj)) {
    if (sensitiveKeys.some(s => key.toLowerCase().includes(s))) {
      sanitized[key] = '[REDACTED]';
    } else {
      sanitized[key] = value;
    }
  }
  
  console.log(sanitized);
}
```

### Rate Limiting Example

```javascript
import http from 'node:http';

const requestCounts = new Map();
const WINDOW_MS = 60000; // 1 minute
const MAX_REQUESTS = 100;

function isRateLimited(ip) {
  const now = Date.now();
  const windowStart = now - WINDOW_MS;
  
  if (!requestCounts.has(ip)) {
    requestCounts.set(ip, []);
  }
  
  const requests = requestCounts.get(ip);
  
  // Remove old requests outside window
  requests.push(now);
  while (requests[0] < windowStart) {
    requests.shift();
  }
  
  return requests.length > MAX_REQUESTS;
}

const server = http.createServer((req, res) => {
  const ip = req.socket.remoteAddress;
  
  if (isRateLimited(ip)) {
    res.writeHead(429, { 'Content-Type': 'text/plain' });
    res.end('Too many requests');
    return;
  }
  
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('OK');
});

server.listen(3000);
```
