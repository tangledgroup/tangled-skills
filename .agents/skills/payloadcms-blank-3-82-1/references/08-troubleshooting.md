# Troubleshooting Guide

Comprehensive solutions to common errors, debugging techniques, and performance issues in Payload CMS blank template.

## Common Errors and Solutions

### TypeScript Errors

**"Cannot find module '@payload-config'"**

**Cause:** Type definitions not generated or Next.js cache corrupted.

**Solution:**
```bash
# Delete Next.js cache
rm -rf .next

# Regenerate types
pnpm generate:types

# Restart development server
pnpm dev
```

**"Property does not exist on type"**

**Cause:** Types not updated after schema changes.

**Solution:**
```bash
# Always run after modifying collections/globals
pnpm generate:types

# In VS Code, restart TypeScript server
Cmd+Shift>P > TypeScript: Restart TS Server
```

**"Missing field types in payload-types.ts"**

**Cause:** Collection not registered in config or syntax errors.

**Solution:**
1. Verify collection is imported in `payload.config.ts`
2. Check for TypeScript errors in collection files
3. Ensure collection slug matches import name
4. Regenerate: `pnpm generate:types`

### Database Connection Errors

**"MongoServerError: connect ECONNREFUSED"**

**Cause:** MongoDB not running or wrong connection string.

**Solution:**
```bash
# Check if MongoDB is running
pgrep mongod  # Mac/Linux
# Or check Docker
docker ps | grep mongo

# Start MongoDB locally
mongod

# Or with Docker
docker run -d -p 27017:27017 --name mongo mongo:latest

# Verify .env file
cat .env
# DATABASE_URL should be: mongodb://127.0.0.1/your-database-name
```

**"MongoServerError: Authentication failed"**

**Cause:** Wrong credentials in connection string.

**Solution:**
```env
# For MongoDB Atlas, use full connection string:
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority

# Ensure password is URL-encoded if it contains special characters
# Example: p@ssw0rd becomes p%40ssw0rd
```

**"MongoServerError: Operation `insertOne` requires a replica set"**

**Cause:** Transactions require MongoDB replica set.

**Solution:**
```bash
# Start MongoDB with replica set (development only)
mongod --replSet rs0 --port 27017

# In another terminal, initialize replica set
mongo --eval "rs.initiate()"

# Or use Docker
docker run -d -p 27017:27017 --name mongo mongo:latest --replSet rs0
docker exec -it mongo mongosh --eval "rs.initiate()"
```

### Build Errors

**"Next.js build failed"**

**Cause:** TypeScript errors, missing dependencies, or configuration issues.

**Solution:**
```bash
# Check for TypeScript errors
pnpm tsc --noEmit

# Clear all caches
rm -rf .next node_modules/.cache
pnpm install

# Try clean build
pnpm devsafe  # Removes .next before starting
```

**"Module not found: Can't resolve..."**

**Cause:** Missing dependency or incorrect import path.

**Solution:**
```bash
# Check if package is installed
pnpm list <package-name>

# Install missing dependency
pnpm add <package-name>

# For dev dependencies
pnpm add -D <package-name>

# Verify import path matches file location
ls -la src/path/to/file.ts
```

**"Sharp processing failed"**

**Cause:** Sharp library not compiled correctly or unsupported image format.

**Solution:**
```bash
# Rebuild sharp
pnpm rebuild sharp

# Or reinstall
pnpm remove sharp && pnpm add sharp

# Check image format is supported (JPEG, PNG, WebP, GIF)
```

### Runtime Errors

**"PayloadSecret is required"**

**Cause:** PAYLOAD_SECRET not set in environment.

**Solution:**
```bash
# Generate secure secret
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"

# Add to .env
echo "PAYLOAD_SECRET=your-generated-secret" >> .env

# Restart server
pnpm dev
```

**"Cannot read properties of undefined (reading 'id')"**

**Cause:** Accessing document field before checking if document exists.

**Solution:**
```typescript
// ❌ Error-prone
const author = doc.author.id

// ✅ Safe with optional chaining
const authorId = doc?.author?.id

// ✅ Or with type guard
if (doc && doc.author) {
  const authorId = doc.author.id
}
```

**"Promise returned in loop" warning**

**Cause:** Using `forEach` with async operations.

**Solution:**
```typescript
// ❌ Wrong: forEach doesn't await promises
docs.forEach(async (doc) => {
  await process(doc)
})

// ✅ Correct: Use for...of loop
for (const doc of docs) {
  await process(doc)
}

// ✅ Or use Promise.all
await Promise.all(docs.map(doc => process(doc)))
```

### Admin Panel Errors

**"Import map not found"**

**Cause:** Component import map not generated.

**Solution:**
```bash
# Generate import map
pnpm generate:importmap

# Check file exists
ls -la src/app/(payload)/admin/importMap.js

# If missing, restart server
pnpm dev
```

**"Component crashed"**

**Cause:** Custom component has errors or invalid props.

**Solution:**
1. Check browser console for specific error
2. Verify component imports are correct
3. Check prop types match Payload's component interface
4. Temporarily remove custom components to isolate issue

**"404 on admin routes"**

**Cause:** Next.js build issue or route configuration problem.

**Solution:**
```bash
# Delete .next and rebuild
rm -rf .next
pnpm build
pnpm start

# Check next.config.ts has withPayload wrapper
cat next.config.ts
```

## Debugging Techniques

### Enable Debug Logging

**Payload debug mode:**

```env
# .env
PAYLOAD_DEBUG=true
LOG_LEVEL=debug
```

**MongoDB debug:**

```typescript
// In payload.config.ts
db: mongooseAdapter({
  url: process.env.DATABASE_URL,
  mongoOptions: {
    // Enable MongoDB driver debugging
    monitorCommands: true,
  },
})
```

Then listen to commands:

```typescript
const db = mongoose.connection
db.on('commandStarted', (event) => console.log('MongoDB:', event))
db.on('commandSucceeded', (event) => console.log('Success:', event))
db.on('commandFailed', (event) => console.error('Failed:', event))
```

### Browser DevTools

**Network tab:**
- Inspect API requests to `/api/*`
- Check request/response payloads
- Identify failed requests (red status codes)
- View CORS errors

**Console tab:**
- JavaScript errors from admin panel
- React warnings
- Custom `console.log` statements

**Application tab:**
- Cookie values (check authentication)
- LocalStorage data
- Service worker status

### Source Maps

Enable source maps for better error stack traces:

```typescript
// next.config.ts
const nextConfig = {
  // ...
  productionBrowserSourceMaps: true, // Enable in production
}
```

**Warning:** Don't enable in production unless necessary (exposes source code).

### Performance Profiling

**Chrome DevTools Performance:**
1. Open DevTools (F12)
2. Go to Performance tab
3. Click Record
4. Reproduce slow operation
5. Stop recording
6. Analyze flame chart for bottlenecks

**Payload-specific metrics:**

```typescript
// Add timing to operations
const start = Date.now()

const posts = await payload.find({ collection: 'posts' })

console.log(`Query took: ${Date.now() - start}ms`)
```

## Performance Issues

### Slow Queries

**Symptom:** API endpoints taking > 1 second to respond.

**Diagnosis:**
```typescript
// Enable query timing
const start = Date.now()

const result = await payload.find({
  collection: 'posts',
  where: { status: { equals: 'published' } },
})

console.log(`Query time: ${Date.now() - start}ms`, {
  totalDocs: result.totalDocs,
  query: { where: { status: 'published' } },
})
```

**Solutions:**

1. **Add database indexes:**
   ```typescript
   {
     name: 'status',
     type: 'select',
     index: true, // Add index for frequently queried fields
   }
   
   {
     name: 'slug',
     type: 'text',
     unique: true, // Unique fields are auto-indexed
     index: true,
   }
   ```

2. **Limit returned fields:**
   ```typescript
   const posts = await payload.find({
     collection: 'posts',
     select: {
       title: true,
       slug: true,
       excerpt: true,
       // Don't fetch unnecessary fields
     },
   })
   ```

3. **Reduce relationship depth:**
   ```typescript
   // Instead of depth: 10
   const posts = await payload.find({
     collection: 'posts',
     depth: 1, // Only populate immediate relationships
   })
   ```

4. **Add pagination:**
   ```typescript
   const posts = await payload.find({
     collection: 'posts',
     limit: 10, // Always paginate
     page: 1,
   })
   ```

### Memory Leaks

**Symptom:** Node.js process memory usage grows continuously.

**Common causes:**
- Unclosed database connections
- Growing arrays/objects without cleanup
- Event listeners not removed

**Diagnosis:**
```bash
# Monitor memory usage
watch -n 1 "ps aux | grep node"

# Take heap snapshot in Node.js
import v8 from 'v8'

console.log('Heap stats:', v8.getHeapStatistics())
```

**Solutions:**

1. **Close connections on shutdown:**
   ```typescript
   process.on('SIGINT', async () => {
     await payload.db.destroy()
     process.exit(0)
   })
   ```

2. **Limit array sizes:**
   ```typescript
   // Keep only last 100 items
   if (cache.length > 100) {
     cache.shift()
   }
   ```

3. **Cleanup event listeners:**
   ```typescript
   const handler = () => { /* ... */ }
   emitter.on('event', handler)
   
   // Later, remove listener
   emitter.off('event', handler)
   ```

### Slow Image Processing

**Symptom:** Uploads take > 5 seconds.

**Solutions:**

1. **Reduce image sizes:**
   ```typescript
   upload: {
     imageSizes: [
       {
         name: 'thumbnail',
         width: 200, // Smaller dimensions
         height: 200,
       },
     ],
   }
   ```

2. **Use CDN for image optimization:**
   - Offload to Cloudinary, Imgix, or similar
   - Store original, serve optimized versions from CDN

3. **Process asynchronously:**
   ```typescript
   hooks: {
     afterChange: [
       async ({ doc, req }) => {
         // Queue for background processing
         await queueImageProcessing(doc.id)
       },
     ],
   }
   ```

## Docker Issues

**"Container exited immediately"**

**Diagnosis:**
```bash
# Check container logs
docker-compose logs payload

# Check MongoDB is running
docker-compose logs mongo
```

**Common causes:**
- Missing `.env` file
- Wrong DATABASE_URL (should use `mongo` as hostname in Docker)
- Port already in use

**Solution:**
```env
# .env for Docker
DATABASE_URL=mongodb://mongo/your-database-name
PAYLOAD_SECRET=your-secret
```

**"Permission denied" errors:**

**Cause:** Volume mount permissions.

**Solution:**
```bash
# Fix permissions
docker-compose run --rm payload chown -R node:node /home/node/app

# Or run as root (not recommended for production)
docker-compose run --rm --user 0 payload <command>
```

**"MongoDB connection timeout in Docker":**

**Cause:** Payload starting before MongoDB is ready.

**Solution:**
```yaml
# docker-compose.yml
services:
  payload:
    depends_on:
      mongo:
        condition: service_healthy
    
  mongo:
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh --quiet
      interval: 5s
      timeout: 5s
      retries: 10
```

## Security Issues

**"Access control bypassed"**

**Cause:** Forgetting `overrideAccess: false` when passing user.

**Solution:**
```typescript
// ❌ Vulnerable
const docs = await payload.find({
  collection: 'posts',
  user, // Access control ignored!
})

// ✅ Secure
const docs = await payload.find({
  collection: 'posts',
  user,
  overrideAccess: false, // Enforce permissions
})
```

**"XSS vulnerability in rich text"**

**Cause:** Rendering unescaped HTML from richText fields.

**Solution:**
```typescript
import { lexicalEditor } from '@payloadcms/richtext-lexical'

// Configure Lexical to sanitize HTML
editor: lexicalEditor({
  features: ({ defaultFeatures }) => [
    ...defaultFeatures,
    // Add sanitization features
  ],
})

// When rendering on frontend, use dangerouslySetInnerHTML carefully
<div dangerouslySetInnerHTML={{ __html: sanitizeHTML(post.content) }} />
```

## Development Workflow Issues

**"File changes not reflecting"**

**Cause:** Next.js cache or hot reload issue.

**Solution:**
```bash
# Clear cache and restart
rm -rf .next
pnpm dev

# Or use devsafe script
pnpm devsafe
```

**"TypeScript not catching errors"**

**Cause:** `noEmit: false` or incorrect tsconfig.

**Solution:**
```json
// tsconfig.json
{
  "compilerOptions": {
    "noEmit": true, // Don't emit JS (Next.js handles this)
    "strict": true, // Enable strict checking
  }
}
```

Run manually: `pnpm tsc --noEmit`

## Migration Issues

**"Field type changed, data corrupted"**

**Cause:** Changing field types without migration.

**Prevention:**
1. Always backup database before schema changes
2. Test migrations in development first
3. Use Payload's migration system for complex changes

**Solution:**
```bash
# Restore from backup
mongorestore --drop backup/production.bson

# Or manually fix data through admin panel
```

## Production Issues

**"Build works locally but fails in CI"**

**Cause:** Different Node version, missing env vars, or system dependencies.

**Solution:**
```yaml
# GitHub Actions
- name: Setup Node
  uses: actions/setup-node@v3
  with:
    node-version: '20' # Match local version
    
- name: Install system deps
  run: sudo apt-get install -y libvips-dev # For sharp
  
- name: Set environment
  run: |
    echo "DATABASE_URL=$DATABASE_URL" >> .env
    echo "PAYLOAD_SECRET=$PAYLOAD_SECRET" >> .env
```

**"Images not loading in production"**

**Cause:** Next.js images configuration or CDN issues.

**Solution:**
```typescript
// next.config.ts
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'your-cdn-domain.com',
      },
    ],
    localPatterns: [
      {
        pathname: '/api/media/file/**',
      },
    ],
  },
}
```

**"Database connection pool exhausted"**

**Cause:** Too many concurrent connections.

**Solution:**
```typescript
// payload.config.ts
db: mongooseAdapter({
  url: process.env.DATABASE_URL,
  mongoOptions: {
    maxPoolSize: 10, // Limit connections
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  },
})
```

## Getting Help

### Official Resources

1. **Payload Docs**: https://payloadcms.com/docs
2. **GitHub Issues**: https://github.com/payloadcms/payload/issues
3. **Discord Community**: https://discord.com/invite/payload
4. **Examples Repository**: https://github.com/payloadcms/payload/tree/main/examples

### Debugging Checklist

Before asking for help:

- [ ] Checked Payload version is up to date
- [ ] Reviewed error messages carefully
- [ ] Searched existing issues on GitHub
- [ ] Tried clearing caches (`rm -rf .next`)
- [ ] Verified environment variables are set
- [ ] Tested with minimal reproduction case
- [ ] Enabled debug logging
- [ ] Checked MongoDB is running and accessible

### Creating a Minimal Reproduction

```bash
# Start fresh from blank template
npx create-payload-app@latest my-debug-app --template blank --db mongodb --yes

# Add minimal code to reproduce issue
# Share the repository link when asking for help
```

## Performance Benchmarks

**Expected performance:**

- **Admin panel load**: < 2 seconds
- **List view (100 docs)**: < 500ms
- **Create document**: < 200ms
- **Update document**: < 200ms
- **Image upload (1MB)**: < 3 seconds

If significantly slower, check:
- Database indexes
- Network latency to database
- Server resources (CPU, memory)
- Query complexity (depth, where clauses)
