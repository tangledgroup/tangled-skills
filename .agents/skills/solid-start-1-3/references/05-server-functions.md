# SolidStart Server Functions Guide

## Introduction

Server functions enable secure backend logic that runs exclusively on the server while being called from client components. They use TanStack's server functions plugin for automatic code splitting and serialization.

## Basic Usage

### Creating a Server Function

```tsx
// src/server/create-user.tsx
"use server";

export async function createUser(name: string, email: string) {
  // This code runs ONLY on the server
  const user = await db.user.create({
    data: { name, email }
  });
  
  return {
    id: user.id,
    name: user.name,
    email: user.email,
  };
}
```

Key points:
- File must start with `"use server"` directive
- Functions are exported (not default export)
- Code is automatically removed from client bundle

### Using Server Functions in Components

```tsx
import { createUser } from "~/server/create-user";

export default function UserForm() {
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  
  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData(e.target as HTMLFormElement);
      const user = await createUser(
        formData.get("name") as string,
        formData.get("email") as string
      );
      
      console.log("Created user:", user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {error() && <div class="error">{error()}</div>}
      
      <label>
        Name:
        <input name="name" required />
      </label>
      
      <label>
        Email:
        <input name="email" type="email" required />
      </label>
      
      <button type="submit" disabled={loading()}>
        {loading() ? "Creating..." : "Create User"}
      </button>
    </form>
  );
}
```

## Validation with Seroval

Server functions integrate with seroval for type-safe validation:

```tsx
// src/server/create-post.tsx
"use server";

import { object, string, validate } from "seroval";

const createPostSchema = object({
  title: string().min(1).max(200),
  content: string().min(1),
  tags: array(string()).optional(),
});

export async function createPost(input: unknown) {
  // Validate input
  const result = validate(createPostSchema, input);
  
  if (result.errors) {
    throw new ValidationError(result.errors);
  }
  
  const post = await db.post.create({
    data: result.value
  });
  
  return post;
}

// Custom error class for validation failures
class ValidationError extends Error {
  constructor(public errors: any[]) {
    super("Validation failed");
  }
}
```

Usage with error handling:

```tsx
import { createPost } from "~/server/create-post";

export default function PostForm() {
  const [errors, setErrors] = createSignal<any[]>([]);
  
  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    const formData = Object.fromEntries(
      new FormData(e.target as HTMLFormElement)
    );
    
    try {
      await createPost(formData);
    } catch (err) {
      if (err instanceof ValidationError) {
        setErrors(err.errors);
      } else {
        throw err;
      }
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {errors().length > 0 && (
        <div class="errors">
          {errors().map(e => <div>{e.message}</div>)}
        </div>
      )}
      
      <input name="title" />
      <textarea name="content" />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

## Multiple Functions in One File

```tsx
// src/server/posts.tsx
"use server";

import { z } from "seroval";

export async function getPosts(limit = 10) {
  return db.post.findMany({ take: limit });
}

export async function getPostById(id: string) {
  return db.post.findUnique({ where: { id } });
}

export async function createPost(data: { title: string; content: string }) {
  return db.post.create({ data });
}

export async function updatePost(id: string, data: Partial<{ title: string; content: string }>) {
  return db.post.update({ where: { id }, data });
}

export async function deletePost(id: string) {
  return db.post.delete({ where: { id } });
}
```

## Server Functions with Context

Access request context in server functions:

```tsx
// src/server/protected-action.tsx
"use server";

import { getRequestEvent } from "solid-js/web";

export async function protectedAction() {
  const event = getRequestEvent();
  
  if (!event) {
    throw new Error("Server function called outside request context");
  }
  
  // Access authentication from request
  const authHeader = event.request.headers.get("authorization");
  const user = await verifyAuth(authHeader);
  
  if (!user) {
    throw new Error("Unauthorized");
  }
  
  // Store in locals for downstream use
  event.locals.user = user;
  
  return { message: "Action performed", userId: user.id };
}
```

## Redirects from Server Functions

Trigger redirects from server functions:

```tsx
// src/server/login.tsx
"use server";

export async function login(email: string, password: string) {
  const user = await authenticate(email, password);
  
  if (!user) {
    throw new Error("Invalid credentials");
  }
  
  // Create session
  const session = await createSession(user);
  
  // Return redirect instruction
  return {
    redirect: "/dashboard",
    session,
  };
}
```

Client-side handling:

```tsx
import { login } from "~/server/login";
import { useNavigate } from "@solidjs/router";

export default function LoginForm() {
  const navigate = useNavigate();
  
  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    
    const result = await login(
      formData.get("email") as string,
      formData.get("password") as string
    );
    
    if (result.redirect) {
      navigate(result.redirect);
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

## File Uploads

Handle file uploads with server functions:

```tsx
// src/server/upload-file.tsx
"use server";

export async function uploadFile(file: File) {
  // Convert File to buffer
  const arrayBuffer = await file.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  
  // Upload to storage (e.g., S3)
  const url = await uploadToS3(buffer, file.name, file.type);
  
  return { url, fileName: file.name };
}
```

Client usage with FormData:

```tsx
import { uploadFile } from "~/server/upload-file";

export default function FileUpload() {
  const [uploading, setUploading] = createSignal(false);
  const [url, setUrl] = createSignal<string | null>(null);
  
  const handleFileChange = async (e: Event) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    
    setUploading(true);
    
    try {
      const result = await uploadFile(file);
      setUrl(result.url);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <>
      <input type="file" onChange={handleFileChange} disabled={uploading()} />
      {url() && <img src={url()} alt="Uploaded" />}
    </>
  );
}
```

## Single-Flight Request Deduplication

SolidStart automatically deduplicates concurrent identical requests:

```tsx
// Multiple simultaneous calls will be deduplicated
"use server";

export async function getExpensiveData(id: string) {
  console.log("Fetching data..."); // Only logged once
  const data = await fetchExpensiveData(id);
  return data;
}
```

This prevents thundering herd problems when multiple components request the same data.

## Error Handling

### Server-Side Errors

```tsx
// src/server/delete-user.tsx
"use server";

export async function deleteUser(id: string) {
  const user = await db.user.findUnique({ where: { id } });
  
  if (!user) {
    throw new Error("User not found");
  }
  
  if (user.role !== "admin" && user.id !== currentUserId) {
    throw new Error("Unauthorized");
  }
  
  await db.user.delete({ where: { id } });
  return { success: true };
}
```

### Client-Side Error Display

```tsx
import { deleteUser } from "~/server/delete-user";

export default function UserList() {
  const [error, setError] = createSignal<string | null>(null);
  
  const handleDelete = async (id: string) => {
    try {
      await deleteUser(id);
      // Remove from list...
    } catch (err) {
      setError(err.message);
    }
  };
  
  return (
    <div>
      {error() && <div class="error">{error()}</div>}
      {/* User list with delete buttons */}
    </div>
  );
}
```

## Serialization Modes

Server functions support two serialization modes:

### JS Mode (Default)

Uses a custom binary format with `eval()` for deserialization:

```ts
// app.config.ts
export default defineConfig({
  serialization: {
    mode: "js", // Faster, requires eval()
  },
});
```

Pros: More efficient, supports more types  
Cons: Requires `eval()`, may violate strict CSP

### JSON Mode

Uses standard JSON serialization:

```ts
// app.config.ts
export default defineConfig({
  serialization: {
    mode: "json", // Slower, CSP-friendly
  },
});
```

Pros: Works with strict CSP, no eval required  
Cons: Less efficient, limited to JSON-serializable types

## Server Function Metadata

Access server function metadata:

```tsx
import { getServerFunctionMeta } from "@solidjs/start";

export default function DebugComponent() {
  const meta = getServerFunctionMeta();
  
  return (
    <pre>
      {JSON.stringify({
        id: meta?.id,
        // Other metadata...
      }, null, 2)}
    </pre>
  );
}
```

## Common Patterns

### Optimistic Updates

```tsx
import { updatePostStatus } from "~/server/update-post-status";

export default function PostItem({ post }) {
  const [status, setStatus] = createSignal(post.status);
  const [loading, setLoading] = createSignal(false);
  
  const handleStatusChange = async (newStatus: string) => {
    // Optimistic update
    setStatus(newStatus);
    setLoading(true);
    
    try {
      await updatePostStatus(post.id, newStatus);
    } catch {
      // Revert on error
      setStatus(post.status);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <span>Status: {status()}</span>
      <button onClick={() => handleStatusChange("published")}>
        Publish
      </button>
    </div>
  );
}
```

### Form Actions with Reactivity

```tsx
import { createComment } from "~/server/create-comment";
import { createSignal, For } from "solid-js";

export default function CommentSection({ postId }) {
  const [comments, setComments] = createSignal([]);
  const [text, setText] = createSignal("");
  
  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    
    if (!text().trim()) return;
    
    const comment = await createComment({
      postId,
      text: text(),
    });
    
    setComments([...comments(), comment]);
    setText("");
  };
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <textarea
          value={text()}
          onInput={e => setText(e.target.value)}
          placeholder="Add a comment..."
        />
        <button type="submit">Comment</button>
      </form>
      
      <For each={comments()}>
        {comment => (
          <div class="comment">
            <strong>{comment.author}</strong>
            <p>{comment.text}</p>
          </div>
        )}
      </For>
    </div>
  );
}
```

### Batch Operations

```tsx
// src/server/batch-operations.tsx
"use server";

export async function batchDelete(ids: string[]) {
  return db.user.deleteMany({
    where: { id: { in: ids } }
  });
}

export async function batchUpdate(data: Array<{ id: string; status: string }>) {
  const updates = data.map(({ id, status }) =>
    db.user.update({ where: { id }, data: { status } })
  );
  
  return Promise.all(updates);
}
```

## Best Practices

1. **Keep functions small and focused** - One function per responsibility
2. **Validate all inputs** - Use seroval or similar validation libraries
3. **Handle errors gracefully** - Catch and re-throw with meaningful messages
4. **Don't expose sensitive data** - Filter response objects before returning
5. **Use environment variables** - Never hardcode secrets in server functions

```tsx
// ✅ Good: Filtered response
export async function getUser(id: string) {
  const user = await db.user.findUnique({ where: { id } });
  
  // Return only safe fields
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    // Exclude: passwordHash, secretKey, etc.
  };
}

// ❌ Bad: Exposing all fields
export async function getUserBad(id: string) {
  return await db.user.findUnique({ where: { id } }); // May leak sensitive data
}
```

## Troubleshooting

### "use server" Not Working

Ensure:
- `"use server"` is the first line in the file
- Function is exported (not default export)
- File is not in `src/routes/` (server functions go in separate directory)

### Serialization Errors

Check:
- Returned values are serializable (no Functions, Symbols, etc.)
- Serialization mode matches your requirements
- No circular references in return values

### Function Not Found

Verify:
- Import path is correct
- Function name matches export
- Build completed successfully
