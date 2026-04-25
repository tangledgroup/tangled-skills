# SolidStart Routing Guide

## File-Based Routing

SolidStart uses a file-based routing system where files in `src/routes/` automatically become routes.

### Basic Routes

```tsx
// src/routes/index.tsx → /
export default function Home() {
  return <h1>Home</h1>;
}

// src/routes/about.tsx → /about
export default function About() {
  return <h1>About</h1>;
}

// src/routes/contact/index.tsx → /contact
export default function Contact() {
  return <h1>Contact</h1>;
}
```

### Nested Routes

Create nested layouts with `(layout)` folders:

```tsx
// src/routes/dashboard/(layout).tsx
export default function DashboardLayout(props) {
  return (
    <div class="dashboard">
      <Sidebar />
      <main>{props.children}</main>
    </div>
  );
}

// src/routes/dashboard/index.tsx → /dashboard
export default function DashboardHome() {
  return <h1>Dashboard Home</h1>;
}

// src/routes/dashboard/users.tsx → /dashboard/users
export default function UsersPage() {
  return <h1>Users</h1>;
}
```

Both `/dashboard` and `/dashboard/users` will use the layout.

### Dynamic Routes

Capture URL parameters with bracket syntax:

```tsx
// src/routes/users/[id].tsx → /users/:id
export default function UserProfile(props: { params: { id: string } }) {
  return <h1>User: {props.params.id}</h1>;
}

// Access params in component
import { useParams } from "@solidjs/router";

export default function UserProfile() {
  const { id } = useParams();
  return <h1>User: {id()}</h1>;
}
```

### Optional Parameters

Make route segments optional with double brackets:

```tsx
// src/routes/lang/[[locale]]/index.tsx
// Matches: /lang, /lang/en, /lang/es
export default function LocalizedPage(props: { params: { locale?: string } }) {
  const locale = props.params.locale || "en";
  return <h1>Locale: {locale}</h1>;
}
```

### Catch-All Routes

Match any path with spread syntax:

```tsx
// src/routes/[...slug].tsx
// Matches: /anything/here, /deep/nested/path
export default function CatchAll(props: { params: { slug: string } }) {
  return <h1>Slug: {props.params.slug}</h1>;
}
```

### Combined Patterns

```tsx
// src/routes/blog/[year]/[month]/[slug].tsx
// Matches: /blog/2024/01/my-post
export default function BlogPost(props: { params: { year: string; month: string; slug: string } }) {
  return <article>{props.params.slug}</article>;
}

// src/routes/api/[...path].tsx
// Catch-all for API routes
export async function GET(props: { params: { path: string } }) {
  return new Response(`API path: ${props.params.path}`);
}
```

## Route Groups

Group routes without creating URL segments using `(group)` syntax:

```tsx
// src/routes/(auth)/login.tsx → /login (not /(auth)/login)
export default function Login() {
  return <h1>Login</h1>;
}

// src/routes/(auth)/register.tsx → /register
export default function Register() {
  return <h1>Register</h1>;
}

// src/routes/(main)/index.tsx → /
export default function Home() {
  return <h1>Home</h1>;
}
```

Use groups to organize routes while maintaining clean URLs.

## Route Config

Export a `route` config object for route-specific settings:

```tsx
// src/routes/private/page.tsx
export const route = {
  ssr: false, // Disable SSR for this route only
};

export default function PrivatePage() {
  return <h1>Private Page</h1>;
}
```

Available options:
- `ssr?: boolean` - Override global SSR setting
- `prerender?: boolean` - Prerender this route

## Redirects

Programmatic redirects in routes:

```tsx
import { HttpStatusCode } from "@solidjs/start";

export default function OldPage() {
  return (
    <main>
      <HttpStatusCode code={301} />
      <a href="/new-page">Redirecting to new page...</a>
    </main>
  );
}
```

Or use response headers:

```tsx
export default function RedirectPage() {
  const event = getRequestEvent();
  if (event) {
    event.response.headers.set("Location", "/new-page");
    event.response.status = 302;
  }
  return <div>Redirecting...</div>;
}
```

## 404 Page

Create a custom 404 page:

```tsx
// src/routes/[...404].tsx
import { HttpStatusCode } from "@solidjs/start";

export default function NotFound() {
  return (
    <main>
      <HttpStatusCode code={404} />
      <h1>Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <a href="/">Go Home</a>
    </main>
  );
}
```

The `404` suffix is special - it catches all unmatched routes.

## Navigation

Programmatic navigation using Solid Router:

```tsx
import { useNavigate } from "@solidjs/router";

export default function FormPage() {
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    // Submit form...
    navigate("/success");
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <button type="submit">Submit</button>
    </form>
  );
}
```

Navigation options:

```tsx
const navigate = useNavigate();

// Replace current history entry
navigate("/new-page", { replace: true });

// Custom state
navigate("/page", { state: { from: "home" } });

// Scroll behavior
navigate("/page", { scroll: false });
```

## Link Component

Use `<a>` tags for client-side navigation:

```tsx
import { A } from "@solidjs/router";

export default function Navigation() {
  return (
    <nav>
      <A href="/">Home</A>
      <A href="/about" reload>About (reloads page)</A>
      <A href="/external" target="_blank">External Link</A>
    </nav>
  );
}
```

## Route Parameters Type Safety

Get typed route parameters:

```tsx
// src/routes/users/[id].tsx
import type { RouteParams } from "@solidjs/start/router";

type UserRouteParams = RouteParams<"/users/[id]">;
// { id: string }

export default function UserProfile(props: { params: UserRouteParams }) {
  const userId: string = props.params.id; // Type-safe
  return <h1>User {userId}</h1>;
}
```

## Query Parameters

Access query parameters:

```tsx
import { useLocation } from "@solidjs/router";

export default function SearchPage() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location().search);
  const query = searchParams.get("q");
  
  return <h1>Search: {query}</h1>;
}
```

## Loading States

Show loading states during navigation:

```tsx
import { useNavigate, useLocation } from "@solidjs/router";
import { createSignal, onMount } from "solid-js";

export default function PageWithLoading() {
  const [loading, setLoading] = createSignal(true);
  const location = useLocation();
  
  onMount(() => {
    // Fetch data when location changes
    fetch(`/api/data?path=${location().pathname}`)
      .then(res => res.json())
      .finally(() => setLoading(false));
  });
  
  return loading() ? <LoadingSpinner /> : <Content />;
}
```

## Code Splitting by Route

Routes are automatically code-split:

```tsx
// Each route file becomes a separate chunk
// src/routes/heavy-page.tsx
import HeavyComponent from "~/components/HeavyComponent"; // Only loaded for this route

export default function HeavyPage() {
  return <HeavyComponent />;
}
```

Manual lazy loading:

```tsx
import { lazy } from "solid-js";

const LazyComponent = lazy(() => import("~/components/Lazy"));

export default function Page() {
  return (
    <Suspense fallback={<Loading />}>
      <LazyComponent />
    </Suspense>
  );
}
```

## Common Patterns

### Authentication Guard

```tsx
// src/routes/(auth)/login.tsx
import { useNavigate } from "@solidjs/router";
import { onMount } from "solid-js";

export default function Login() {
  const navigate = useNavigate();
  
  onMount(() => {
    if (isAuthenticated()) {
      navigate("/dashboard");
    }
  });
  
  return <LoginForm />;
}

// src/routes/(app)/dashboard.tsx
import { useNavigate } from "@solidjs/router";
import { onMount } from "solid-js";

export default function Dashboard() {
  const navigate = useNavigate();
  
  onMount(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  });
  
  return <DashboardContent />;
}
```

### SEO-Optimized Routes

```tsx
// src/routes/blog/[slug].tsx
import { Title, Meta } from "@solidjs/meta";
import { HttpStatusCode } from "@solidjs/start";

export default function BlogPost(props: { params: { slug: string } }) {
  const [post, setPost] = createSignal(null);
  
  onMount(async () => {
    const data = await fetch(`/api/posts/${props.params.slug}`).then(r => r.json());
    setPost(data);
  });
  
  return (
    <article>
      <Title>{post()?.title || "Loading..."}</Title>
      <Meta name="description" content={post()?.excerpt} />
      
      {post() ? (
        <>
          <h1>{post().title}</h1>
          <div class="content">{post().content}</div>
        </>
      ) : (
        <HttpStatusCode code={404} />
      )}
    </article>
  );
}
```

### i18n Routes

```tsx
// src/routes/[[locale]]/index.tsx
export default function HomePage(props: { params: { locale?: string } }) {
  const locale = props.params.locale || "en";
  const t = useTranslations(locale);
  
  return (
    <main>
      <h1>{t("home.title")}</h1>
      <p>{t("home.subtitle")}</p>
    </main>
  );
}

// src/routes/[[locale]]/about.tsx → /about, /en/about, /es/about
export default function AboutPage() {
  return <AboutContent />;
}
```

## Troubleshooting

### Route Not Loading

Check:
- File is in `src/routes/` (or configured routeDir)
- File has a default export
- Filename doesn't conflict with reserved names

### Parameters Not Working

Verify:
- Bracket syntax is correct: `[param]` not `{param}`
- Optional params use double brackets: `[[optional]]`
- Catch-all uses spread: `[...rest]`

### Nested Routes Not Rendering

Ensure:
- Layout file uses `(name).tsx` pattern
- Children are rendered: `{props.children}`
- Route files are inside the layout folder
