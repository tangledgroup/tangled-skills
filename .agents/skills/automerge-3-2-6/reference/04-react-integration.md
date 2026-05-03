# React Integration

## Contents
- @automerge/react Hooks
- React Patterns
- @automerge/vanillajs

## @automerge/react Hooks

The `@automerge/react` package provides React hooks that integrate Automerge documents with component lifecycles. It re-exports items from `@automerge/automerge` and `@automerge/automerge-repo` plus common network and storage adapters.

### RepoProvider

Wrap your app with `RepoProvider` to share a single Repo instance across components:

```jsx
import { RepoProvider } from "@automerge/react"
import { IndexedDBStorageAdapter } from "@automerge/automerge-repo-storage-indexeddb"
import { BroadcastChannelNetworkAdapter } from "@automerge/automerge-repo-network-broadcastchannel"

function App() {
  return (
    <RepoProvider
      storage={new IndexedDBStorageAdapter()}
      network={[new BroadcastChannelNetworkAdapter()]}
    >
      <MainContent />
    </RepoProvider>
  )
}
```

### useDoc

The primary hook for working with Automerge documents in React components:

```jsx
import { useDoc } from "@automerge/react"

function TaskList() {
  // [doc, change, docHandle] — doc is current state, change applies modifications
  const [doc, change] = useDoc({ tasks: [] }, "my-todo-list")

  return (
    <div>
      {doc.tasks.map((task, i) => (
        <div key={i}>
          <input
            type="checkbox"
            checked={task.done}
            onChange={() => change((d) => { d.tasks[i].done = !d.tasks[i].done })}
          />
          {task.title}
        </div>
      ))}
      <button onClick={() => change((d) => {
        d.tasks.push({ title: "New task", done: false })
      })}>
        Add Task
      </button>
    </div>
  )
}
```

**`useDoc(initialValue, docUrl?)` options:**

```jsx
const [doc, change, docHandle] = useDoc(
  { tasks: [] },           // initial document shape
  "my-todo-list",          // document URL (auto-generated if omitted)
  {
    subscribe: true,       // subscribe to changes (default: true)
    onChange: (doc) => {}, // custom change callback
  }
)
```

The third return value is the `DocHandle`, giving access to `.url`, `.dispose()`, and other handle methods.

### useHandle

Access an existing DocHandle by URL without managing its lifecycle:

```jsx
import { useHandle } from "@automerge/react"

function Viewer() {
  const doc = useHandle("automerge:shared-document-url")

  if (!doc) return <div>Loading...</div>

  return <div>{doc.title}</div>
}
```

Returns `null` while the document is loading. Use when you need read-only access or want to share a document across multiple components.

## React Patterns

### Document Initialization and Schema

Define your initial document shape clearly. Automerge doesn't enforce schemas, but consistent initialization ensures predictable structure:

```jsx
const INITIAL_CHAT = {
  messages: [],
  settings: { theme: "light", fontSize: 14 }
}

function ChatRoom() {
  const [doc, change] = useDoc(INITIAL_CHAT, "chat-room-1")
  // ...
}
```

### Change Callbacks with React

Use the `onChange` option to trigger side effects when the document changes:

```jsx
const [doc, change] = useDoc({ count: 0 }, "counter", {
  onChange: (doc) => {
    console.log("Count changed:", doc.count)
    // Update external systems, analytics, etc.
  }
})
```

### Multi-Document Apps

Manage multiple documents by creating separate `useDoc` calls or using `repo.find()`:

```jsx
function App() {
  const [project, changeProject] = useDoc(
    { name: "Untitled", tasks: [] },
    "project-alpha"
  )
  const [settings, changeSettings] = useDoc(
    { theme: "dark" },
    "user-settings"
  )
  // Both documents sync independently
}
```

### Conditional Document Loading

Use `useHandle` for optional documents that may not exist yet:

```jsx
function TaskDetail({ taskId }) {
  const doc = useHandle(`task:${taskId}`)

  if (!doc) return null // Task doesn't exist yet

  return <div>{doc.title}</div>
}
```

### Disposing Documents

Clean up documents when components unmount (handled automatically by hooks). For manual control:

```jsx
const [doc, change, docHandle] = useDoc({ data: [] }, "temp-doc")

useEffect(() => {
  return () => {
    docHandle.dispose() // Remove from repo
  }
}, [docHandle])
```

## @automerge/vanillajs

For non-React applications, `@automerge/vanillajs` provides equivalent hooks using vanilla JavaScript with a similar API:

```javascript
import { createRepo, useDoc } from "@automerge/vanillajs"

const repo = createRepo()
const [doc, change] = useDoc(repo, { tasks: [] }, "my-tasks")

change((d) => {
  d.tasks.push({ title: "New task", done: false })
})
```

The vanillajs package follows the same patterns as the React package but without JSX or component lifecycles. Use it for Svelte, Vue, or plain DOM applications.
