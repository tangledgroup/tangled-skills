# Context and Refs

## Context

Context provides a way to pass data through the component tree without prop
drilling.

### Creating Context

```tsx
import { createContext } from "solid-js";

const ThemeContext = createContext("light");
//                     ^ default value (optional)
```

With options for debugging:

```tsx
const ThemeContext = createContext("light", { name: "Theme" });
```

### Providing Context

Use the `Provider` component on the context object:

```tsx
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Dashboard />
    </ThemeContext.Provider>
  );
}
```

### Consuming Context

```tsx
import { useContext } from "solid-js";

function ThemedComponent() {
  const theme = useContext(ThemeContext);
  return <div class={theme}>Content</div>;
}
```

Returns the value from the nearest matching Provider, or the default value.

### Complex Context with Stores

For multiple values or complex state, use a store:

```tsx
import { createStore } from "solid-js/store";
import { createContext, useContext } from "solid-js";

const AppContext = createContext();

function Provider(props) {
  const [state, setState] = createStore({
    user: null,
    theme: "light",
    setUser: (user) => setState("user", user),
  });

  return (
    <AppContext.Provider value={state}>
      {props.children}
    </AppContext.Provider>
  );
}
```

## Refs

Refs provide direct access to DOM elements or component instances.

### Basic Ref Usage

```tsx
function Component() {
  let myElement;

  return (
    <div>
      <p ref={myElement}>My Element</p>
      <button onClick={() => myElement.focus()}>Focus</button>
    </div>
  );
}
```

Ref assignment occurs at **creation time** before the element is added to the
DOM. Use `onMount` if you need access after DOM attachment.

### Callback Refs

For access during creation (before DOM attachment):

```tsx
<p ref={(el) => { myElement = el; }}>Content</p>
```

### createUniqueId

Generate unique IDs for accessibility (e.g., label/input associations):

```tsx
import { createUniqueId } from "solid-js";

function LabeledInput(props) {
  const id = createUniqueId();
  return (
    <>
      <label htmlFor={id}>{props.label}</label>
      <input id={id} type="text" />
    </>
  );
}
```

### children Helper

Access and manipulate child content:

```tsx
import { children } from "solid-js";

function Wrapper(props) {
  const wrappedChildren = children(() => props.children);

  return (
    <div>
      {/* Children are only evaluated when needed */}
      {wrappedChildren()}
    </div>
  );
}
```
