# TUI Components

Extensions and custom tools can render custom TUI components. Source: `@mariozechner/pi-tui`.

## Component Interface

```typescript
interface Component {
  render(width: number): string[];   // Lines must not exceed width
  handleInput?(data: string): void;
  wantsKeyRelease?: boolean;          // Kitty protocol key release events
  invalidate(): void;                 // Clear cached render state
}
```

The TUI appends SGR reset at end of each rendered line. Styles don't carry across lines — reapply per line or use `wrapTextWithAnsi()`.

## Focusable Interface (IME Support)

Components displaying a text cursor for IME input:

```typescript
import { CURSOR_MARKER, type Component, type Focusable } from "@mariozechner/pi-tui";

class MyInput implements Component, Focusable {
  focused: boolean = false;

  render(width: number): string[] {
    const marker = this.focused ? CURSOR_MARKER : "";
    return [`> ${beforeCursor}${marker}\x1b[7m${atCursor}\x1b[27m${afterCursor}`];
  }
}
```

Container components with embedded `Input` or `Editor` must propagate `focused` to the child.

## Built-in Components

```typescript
import { Text, Box, Container, Spacer, Markdown, Image, SelectList, SettingsList, Input } from "@mariozechner/pi-tui";
```

### Text

Multi-line text with word wrapping:

```typescript
const text = new Text("Hello World", 1, 1);  // paddingX, paddingY
text.setText("Updated");
```

### Box

Container with padding and background:

```typescript
const box = new Box(1, 1, (s) => bgGray(s));
box.addChild(new Text("Content", 0, 0));
```

### Container

Groups children vertically:

```typescript
const container = new Container();
container.addChild(component1);
container.addChild(component2);
```

### Spacer

Empty vertical space: `new Spacer(2)` — 2 empty lines.

### Markdown

Renders markdown with syntax highlighting:

```typescript
import { getMarkdownTheme } from "@mariozechner/pi-coding-agent";
const md = new Markdown("# Title\n\n**Bold**", 1, 1, getMarkdownTheme());
```

### Image

Renders images in supported terminals (Kitty, iTerm2, Ghostty, WezTerm):

```typescript
const image = new Image(base64Data, "image/png", theme, { maxWidthCells: 80 });
```

## Keyboard Input

```typescript
import { matchesKey, Key } from "@mariozechner/pi-tui";

handleInput(data: string) {
  if (matchesKey(data, Key.up)) { this.selectedIndex--; }
  if (matchesKey(data, Key.enter)) { this.onSelect?.(this.selectedIndex); }
  if (matchesKey(data, Key.escape)) { this.onCancel?.(); }
  if (matchesKey(data, Key.ctrl("c"))) { /* Ctrl+C */ }
}
```

Key identifiers: `Key.enter`, `Key.escape`, `Key.tab`, `Key.space`, `Key.backspace`, `Key.up/down/left/right`, `Key.ctrl("c")`, `Key.shift("tab")`, `Key.alt("left")`, `Key.ctrlShift("p")`. String format also works: `"ctrl+c"`, `"shift+tab"`.

## Using Components in Extensions

### ctx.ui.custom()

Temporarily replaces the editor:

```typescript
const result = await ctx.ui.custom<boolean>((tui, theme, keybindings, done) => {
  const text = new Text("Press Enter to confirm", 1, 1);
  text.onKey = (key) => {
    if (key === "return") done(true);
    if (key === "escape") done(false);
    return true;
  };
  return text;
});
```

### Overlays

Render on top of existing content without clearing screen:

```typescript
const result = await ctx.ui.custom<string | null>(
  (tui, theme, keybindings, done) => new MyDialog({ onClose: done }),
  {
    overlay: true,
    overlayOptions: {
      width: "50%",
      anchor: "right-center",
      margin: 2,
      visible: (w, h) => w >= 80,
    },
  }
);
```

Overlay components are disposed when closed — create fresh instances each time.

## Theming

### Foreground Colors

```typescript
theme.fg("accent", text)       // Highlights
theme.fg("success", text)      // Green
theme.fg("error", text)        // Red
theme.fg("warning", text)      // Yellow
theme.fg("muted", text)        // Secondary
theme.fg("dim", text)          // Tertiary
theme.fg("toolTitle", text)    // Tool names
theme.fg("border", text)       // Borders
```

Full palette: `text`, `accent`, `muted`, `dim`, `success`, `error`, `warning`, `border`, `borderAccent`, `borderMuted`, `userMessageText`, `customMessageText`, `customMessageLabel`, `toolTitle`, `toolOutput`, `mdHeading`, `mdLink`, `mdCode`, `syntaxComment`, `syntaxKeyword`, `syntaxFunction`, `syntaxVariable`, `syntaxString`, `syntaxNumber`, `syntaxType`, `thinkingOff` through `thinkingXhigh`, `bashMode`.

### Background Colors

```typescript
theme.bg("selectedBg", text)
theme.bg("userMessageBg", text)
theme.bg("toolPendingBg", text)
theme.bg("toolSuccessBg", text)
theme.bg("toolErrorBg", text)
```

### Text Styles

```typescript
theme.bold(text)
theme.italic(text)
theme.strikethrough(text)
```

## Common Patterns

### Pattern 1: Selection Dialog (SelectList)

```typescript
import { DynamicBorder } from "@mariozechner/pi-coding-agent";
import { Container, type SelectItem, SelectList, Text } from "@mariozechner/pi-tui";

const items: SelectItem[] = [
  { value: "opt1", label: "Option 1", description: "First option" },
  { value: "opt2", label: "Option 2" },
];

const result = await ctx.ui.custom<string | null>((tui, theme, _kb, done) => {
  const container = new Container();
  container.addChild(new DynamicBorder((s: string) => theme.fg("accent", s)));
  container.addChild(new Text(theme.fg("accent", theme.bold("Pick an Option")), 1, 0));

  const selectList = new SelectList(items, Math.min(items.length, 10), {
    selectedPrefix: (t) => theme.fg("accent", t),
    selectedText: (t) => theme.fg("accent", t),
    description: (t) => theme.fg("muted", t),
    scrollInfo: (t) => theme.fg("dim", t),
  });
  selectList.onSelect = (item) => done(item.value);
  selectList.onCancel = () => done(null);
  container.addChild(selectList);
  container.addChild(new Text(theme.fg("dim", "↑↓ navigate • enter select • esc cancel"), 1, 0));
  container.addChild(new DynamicBorder((s: string) => theme.fg("accent", s)));

  return {
    render: (w) => container.render(w),
    invalidate: () => container.invalidate(),
    handleInput: (data) => { selectList.handleInput(data); tui.requestRender(); },
  };
});
```

### Pattern 2: Async Operation with Cancel (BorderedLoader)

```typescript
import { BorderedLoader } from "@mariozechner/pi-coding-agent";

const result = await ctx.ui.custom<string | null>((tui, theme, _kb, done) => {
  const loader = new BorderedLoader(tui, theme, "Fetching data...");
  loader.onAbort = () => done(null);
  fetchData(loader.signal).then((data) => done(data)).catch(() => done(null));
  return loader;
});
```

### Pattern 3: Settings/Toggles (SettingsList)

```typescript
import { getSettingsListTheme } from "@mariozechner/pi-coding-agent";
import { Container, type SettingItem, SettingsList, Text } from "@mariozechner/pi-tui";

const items: SettingItem[] = [
  { id: "verbose", label: "Verbose mode", currentValue: "off", values: ["on", "off"] },
];

await ctx.ui.custom((_tui, theme, _kb, done) => {
  const container = new Container();
  container.addChild(new Text(theme.fg("accent", theme.bold("Settings")), 1, 1));
  const settingsList = new SettingsList(items, Math.min(items.length + 2, 15), getSettingsListTheme(),
    (id, newValue) => ctx.ui.notify(`${id} = ${newValue}`, "info"),
    () => done(undefined),
    { enableSearch: true }
  );
  container.addChild(settingsList);
  return { render: (w) => container.render(w), invalidate: () => container.invalidate(), handleInput: (data) => settingsList.handleInput?.(data) };
});
```

### Pattern 4: Status Indicator

```typescript
ctx.ui.setStatus("my-ext", ctx.ui.theme.fg("accent", "● active"));
ctx.ui.setStatus("my-ext", undefined);  // Clear
```

### Pattern 5: Widgets Above/Below Editor

```typescript
ctx.ui.setWidget("my-widget", ["Line 1", "Line 2"]);
ctx.ui.setWidget("my-widget", ["Line 1"], { placement: "belowEditor" });
ctx.ui.setWidget("my-widget", undefined);  // Clear
```

### Pattern 7: Custom Editor (vim mode)

```typescript
import { CustomEditor } from "@mariozechner/pi-coding-agent";
import { matchesKey, truncateToWidth } from "@mariozechner/pi-tui";

class VimEditor extends CustomEditor {
  private mode: "normal" | "insert" = "insert";

  handleInput(data: string): void {
    if (matchesKey(data, "escape")) {
      if (this.mode === "insert") { this.mode = "normal"; return; }
      super.handleInput(data);
      return;
    }
    if (this.mode === "insert") { super.handleInput(data); return; }
    switch (data) {
      case "i": this.mode = "insert"; return;
      case "h": super.handleInput("\x1b[D"); return;
      case "l": super.handleInput("\x1b[C"); return;
    }
    if (data.length === 1 && data.charCodeAt(0) >= 32) return;
    super.handleInput(data);
  }

  render(width: number): string[] {
    const lines = super.render(width);
    if (lines.length > 0) {
      const label = this.mode === "normal" ? " NORMAL " : " INSERT ";
      lines[lines.length - 1] = truncateToWidth(lines[lines.length - 1]!, width - label.length, "") + label;
    }
    return lines;
  }
}

ctx.ui.setEditorComponent((_tui, theme, keybindings) => new VimEditor(theme, keybindings));
```

## Tool Rendering

Custom tools can provide `renderCall` and `renderResult`:

```typescript
import { highlightCode, getLanguageFromPath, keyHint } from "@mariozechner/pi-coding-agent";
import { Text } from "@mariozechner/pi-tui";

pi.registerTool({
  name: "my_tool",
  // ...
  renderCall(args, theme, context) {
    const text = (context.lastComponent as Text | undefined) ?? new Text("", 0, 0);
    let content = theme.fg("toolTitle", theme.bold("my_tool "));
    content += theme.fg("muted", args.action);
    text.setText(content);
    return text;
  },
  renderResult(result, { expanded, isPartial }, theme, context) {
    if (isPartial) return new Text(theme.fg("warning", "Processing..."), 0, 0);
    let text = theme.fg("success", "✓ Done");
    if (!expanded) text += ` (${keyHint("app.tools.expand", "to expand")})`;
    return new Text(text, 0, 0);
  },
});
```

Syntax highlighting:

```typescript
const highlighted = highlightCode("const x = 1;", "typescript", theme);
const lang = getLanguageFromPath("/path/to/file.rs"); // "rust"
```

## Key Rules

1. Always use `theme` from callback — don't import theme directly
2. Always type `DynamicBorder` color param: `(s: string) => theme.fg("accent", s)`
3. Call `tui.requestRender()` after state changes in `handleInput`
4. Return `{ render, invalidate, handleInput }` for custom components
5. Use existing components — `SelectList`, `SettingsList`, `BorderedLoader` cover 90% of cases

## Invalidation and Theme Changes

When theme changes, TUI calls `invalidate()` on all components. Components that pre-bake theme colors must rebuild content:

```typescript
class GoodComponent extends Container {
  private message: string;
  constructor(message: string) {
    super();
    this.message = message;
    this.rebuild();
  }
  private rebuild() {
    this.clear();
    this.addChild(new Text(theme.fg("accent", this.message), 1, 0));
  }
  override invalidate() {
    super.invalidate();
    this.rebuild();
  }
}
```
