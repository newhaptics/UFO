# Honest API Design Philosophy

## Principle: Truth at the Foundation

The ScreenBridge API follows a **"truth at the foundation"** architecture:

**Layer 1 (Rust Core):**
- ✅ Returns **ALL** data available from Windows UI Automation
- ✅ Provides **ALL** queryable properties
- ❌ **NO** hardcoded filtering logic
- ❌ **NO** assumption about what users want

**Layer 2+ (Apps/MCP/AI):**
- ✅ Applies filtering based on **UIA properties**
- ✅ Makes context-aware decisions
- ✅ Adapts to user needs

---

## Why This Matters

### ❌ The Problem with Hardcoded Filtering

```rust
// BAD: Hardcoded list (brittle, incomplete)
fn is_system_pane(class_name: &str, title: &str) -> bool {
    let system_titles = [
        "Taskbar",
        "Program Manager",
        "NVIDIA GeForce Overlay",  // What about AMD overlay?
        // What about other overlays?
        // What about new Windows versions?
        // This list WILL break!
    ];
    system_titles.iter().any(|&t| title == t)
}
```

**Problems:**
- 🚫 Not exhaustive - breaks with new apps
- 🚫 Windows version dependent
- 🚫 Hides data from users who might need it
- 🚫 Makes assumptions about use cases

### ✅ The Solution: Property-Based Filtering

```rust
// GOOD: Query UIA properties (honest, complete)
let element = window.element();

// Let the USER decide based on REAL properties
let visible = element.is_visible()?;
let focusable = element.is_keyboard_focusable()?;
let offscreen = element.is_offscreen()?;
let bounds = element.bounding_rectangle()?;

// Now filter based on QUERYABLE truth
if visible && focusable {
    // This is probably an app window
}
```

**Benefits:**
- ✅ Based on Windows UIA properties (stable API)
- ✅ Works across Windows versions
- ✅ Users can apply their own logic
- ✅ No hidden data

---

## Available UIA Properties

ScreenBridge exposes these Windows UI Automation properties:

| Property | Method | Type | Use Case |
|----------|--------|------|----------|
| **Visibility** | `is_visible()` | bool | Filter visible windows |
| **Offscreen** | `is_offscreen()` | bool | Exclude hidden/minimized |
| **Focusable** | `is_keyboard_focusable()` | bool | Find interactive windows |
| **Enabled** | `is_enabled()` | bool | Check if active |
| **Bounds** | `bounding_rectangle()` | (i32, i32, i32, i32) | Get position/size |
| **Framework** | `framework_id()` | String | Detect tech (Win32, WPF, Electron) |
| **Class** | `class_name()` | String | Window class name |
| **Name** | `name()` | String | Window title |
| **Control Type** | `control_type()` | String | "window" vs "pane" |
| **Process ID** | `process_id()` | i32 | Which app owns it |
| **Automation ID** | `automation_id()` | String | Unique identifier |

---

## Filtering Patterns

### Pattern 1: Get Everything (Layer 1)

```rust
use screenbridge_core::{AutomationContext, WindowDiscovery};

let context = AutomationContext::new()?;
let discovery = WindowDiscovery::new(&context);

// NO filtering - returns ALL windows/panes
let all_windows = discovery.find_all_windows()?;

// Returns:
// - Application windows (Word, Chrome, etc.)
// - System UI (Taskbar, Desktop)
// - Overlays (NVIDIA, Discord, etc.)
// - Everything UI Automation can see
```

### Pattern 2: Property-Based Filtering (Layer 2)

```rust
use screenbridge_core::WindowFilter;

// Only visible, focusable windows (typical apps)
let filter = WindowFilter::default()
    .only_visible()
    .only_focusable();

let app_windows = discovery.find_windows_with_filter(&filter)?;
// Returns: Word, Chrome, Slack, VS Code, etc.
// Excludes: Taskbar, Desktop, minimized windows
```

### Pattern 3: App-Specific + Properties (Layer 2)

```rust
// Word windows that are visible and main (not dialogs)
let filter = WindowFilter::for_process("winword.exe")
    .only_visible()
    .only_main_windows();

let word_windows = discovery.find_windows_with_filter(&filter)?;
```

### Pattern 4: Custom Logic (Layer 3 - Your Code)

```rust
// Get all windows, then apply YOUR logic
let all_windows = discovery.find_all_windows()?;

for window in all_windows {
    let element = window.element();

    // YOUR custom filtering logic
    let visible = element.is_visible().unwrap_or(false);
    let (x, y, w, h) = element.bounding_rectangle().unwrap_or((0, 0, 0, 0));

    // Example: Only windows larger than 100x100 pixels
    if visible && w > 100 && h > 100 {
        println!("Large visible window: {}", window.title);
    }

    // Example: Only windows on primary monitor
    if x >= 0 && y >= 0 {
        println!("Primary monitor window: {}", window.title);
    }

    // YOUR use case, YOUR logic!
}
```

---

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: AI / User Code                                     │
│ - Custom filtering logic                                    │
│ - Context-aware decisions                                   │
│ - Use case specific rules                                   │
│                                                              │
│ Example: "Only show windows user is actively working in"   │
│          (visible, focused, on active desktop, etc.)        │
└────────────────────┬────────────────────────────────────────┘
                     │ Uses property queries
┌────────────────────┴────────────────────────────────────────┐
│ Layer 2: WindowFilter (Composable Filters)                  │
│ - only_visible()                                            │
│ - only_focusable()                                          │
│ - only_main_windows()                                       │
│ - for_process("app.exe")                                    │
│                                                              │
│ Example: WindowFilter::for_process("winword.exe")          │
│             .only_visible()                                 │
│             .only_focusable()                               │
└────────────────────┬────────────────────────────────────────┘
                     │ Queries UIA properties
┌────────────────────┴────────────────────────────────────────┐
│ Layer 1: WindowDiscovery (Honest Truth)                     │
│ - find_all_windows() → ALL windows/panes                    │
│ - NO hardcoded exclusions                                   │
│ - NO assumptions                                            │
│ - Returns: Taskbar, Desktop, Apps, Everything!              │
│                                                              │
│ + UIElement property methods:                               │
│   - is_visible(), is_offscreen()                           │
│   - is_keyboard_focusable()                                 │
│   - bounding_rectangle()                                    │
│   - framework_id(), class_name(), etc.                      │
└────────────────────┬────────────────────────────────────────┘
                     │ Direct UIA API calls
┌────────────────────┴────────────────────────────────────────┐
│ Layer 0: Windows UI Automation API                          │
│ - IUIAutomation COM interface                              │
│ - UI element tree                                           │
│ - Properties, patterns, events                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Use Case Examples

### For Braille Display Integration

```rust
// Get ALL windows with their properties
let all_windows = discovery.find_all_windows()?;

for window in all_windows {
    let element = window.element();

    // Check if visible (braille needs visible content)
    if let Ok(visible) = element.is_visible() {
        if !visible { continue; }
    }

    // Check if large enough to matter
    if let Ok((_, _, w, h)) = element.bounding_rectangle() {
        if w < 50 || h < 50 { continue; }  // Too small for content
    }

    // Check if it's a real application
    if let Ok(focusable) = element.is_keyboard_focusable() {
        if !focusable { continue; }  // System UI, skip it
    }

    // This window is relevant for braille rendering
    println!("Braille-relevant: {}", window.title);
}
```

### For MCP/AI Integration

```rust
// Layer 1: Get EVERYTHING
let all_windows = discovery.find_all_windows()?;

// Layer 2: Let AI decide what's relevant
// MCP tool exposes ALL properties, AI decides:
// - "Show me only visible windows" → filter by is_visible()
// - "Find the largest window" → sort by bounding_rectangle()
// - "What's the active Word document?" → filter by process + focusable
```

---

## Migration from Hardcoded Filtering

### Before (Brittle)

```rust
// ❌ BAD: Hardcoded assumptions
if title == "Taskbar" || title == "Program Manager" {
    return None;  // Skip it
}

// What if Windows changes these names?
// What if user actually WANTS taskbar data?
// What about third-party taskbars?
```

### After (Honest)

```rust
// ✅ GOOD: Query UIA properties
let element = window.element();

// Let users decide based on REAL properties
if let Ok(focusable) = element.is_keyboard_focusable() {
    if !focusable {
        // User can CHOOSE to skip non-focusable
        // Or they can CHOOSE to include it
    }
}
```

---

## Testing with Accessibility Insights

**Accessibility Insights for Windows** is the perfect tool for understanding UIA properties!

1. **Run Accessibility Insights** on your system
2. **Inspect any window** - see ALL UIA properties
3. **Understand what's queryable** - everything you see is accessible via our API
4. **Test filtering logic** - verify which properties distinguish app windows from system UI

**We provide the API for ALL properties you see in Accessibility Insights.**

---

## Principles Summary

1. **Truth at Layer 1**: Return everything, no filtering
2. **Properties over Lists**: Use UIA properties, not hardcoded names
3. **User Choice**: Let higher layers decide what matters
4. **Stability**: UIA properties are stable across Windows versions
5. **Completeness**: Don't hide data users might need
6. **Flexibility**: Enable use cases we haven't thought of

---

## Future: More UIA Properties

As needed, we can expose more UIA properties:

- `IsWindowPatternAvailable`
- `WindowVisualState` (minimized, maximized, normal)
- `WindowInteractionState` (running, closing, etc.)
- `IsTopmost`
- `HasKeyboardFocus`
- And hundreds more from the UIA spec

**The pattern is the same**: Expose the property, let users filter.

---

## Questions?

See `examples/honest_discovery.rs` for a working demonstration.

Run it with:
```bash
cargo run --example honest_discovery
```

You'll see:
- ALL windows (including Taskbar, Desktop)
- ALL properties for each window
- Examples of property-based filtering
