# ScreenBridge Architecture

## Overview

ScreenBridge is built with a **layered, generic architecture** that supports ANY Windows application, not just Microsoft Word. This makes it extensible and reusable across Office apps, browsers, and other Windows applications.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: AI Integration (Future - MCP Server)             │
│  - Claude/LLM integration                                   │
│  - Intelligent extraction & filtering                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│  Layer 3: Application-Specific APIs                         │
│  - WordAutomation (winword.exe)                            │
│  - ExcelAutomation (excel.exe) [Future]                    │
│  - PowerPointAutomation (powerpnt.exe) [Future]            │
│  - App-specific UI element extraction                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│  Layer 2: UI Element Extraction (Future)                    │
│  - Status bars, ribbons, menus                             │
│  - Navigation panes                                         │
│  - Accessibility features                                   │
│  - Generic patterns reusable across apps                   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│  Layer 1: Generic Window Discovery ✅ IMPLEMENTED           │
│  - Find windows for ANY application                        │
│  - Filter by process, title, properties                    │
│  - Return structured window information                    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│  Layer 0: Windows UI Automation API                        │
│  - COM initialization                                       │
│  - IUIAutomation interface                                 │
│  - UI element tree navigation                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Generic Window Discovery (Current)

**Module:** `src/discovery.rs`

### Purpose

Provides a **generic, reusable API** for discovering windows from ANY Windows application. This layer is application-agnostic and can be used for:

- Microsoft Office apps (Word, Excel, PowerPoint)
- Web browsers (Chrome, Edge, Firefox)
- Development tools (VS Code, Visual Studio)
- System apps (File Explorer, Notepad)
- Any Windows application with a window

### Core Components

#### 1. `WindowDiscovery` Struct

The main entry point for window discovery.

```rust
let context = AutomationContext::new()?;
let discovery = WindowDiscovery::new(&context);

// Find all windows
let all_windows = discovery.find_all_windows()?;

// Find specific app
let word_windows = discovery.find_by_process("winword.exe")?;
```

#### 2. `WindowFilter` Struct

Flexible filtering system for narrowing down windows.

```rust
// Basic filter by process
let filter = WindowFilter::for_process("excel.exe");

// Complex filter with multiple criteria
let filter = WindowFilter::for_process("winword.exe")
    .with_title("Document")
    .only_main_windows()
    .excluding_titles(vec!["Print".to_string(), "Options".to_string()]);

let windows = discovery.find_windows_with_filter(&filter)?;
```

#### 3. `WindowHandle` Struct

Represents a discovered window with:
- Window title
- Process ID
- Underlying UI element
- Access to element properties

### API Methods

| Method | Description | Example |
|--------|-------------|---------|
| `find_all_windows()` | Find all desktop windows | `discovery.find_all_windows()?` |
| `find_by_process(name)` | Find by process name | `discovery.find_by_process("chrome.exe")?` |
| `find_by_title(title)` | Find by window title | `discovery.find_by_title("Document")?` |
| `find_windows_with_filter(&filter)` | Custom filter | `discovery.find_windows_with_filter(&filter)?` |

### Filter Options

| Filter | Purpose | Example |
|--------|---------|---------|
| `for_process(name)` | Match specific process | `WindowFilter::for_process("notepad.exe")` |
| `with_title(text)` | Title substring match | `.with_title("Untitled")` |
| `excluding_titles(vec)` | Exclude specific titles | `.excluding_titles(vec!["Print"])` |
| `only_main_windows()` | Exclude dialog windows | `.only_main_windows()` |

---

## Layer 3: Application-Specific APIs

**Current:** `WordAutomation` struct

### Purpose

Provides high-level, application-specific functionality that builds on the generic window discovery layer.

```rust
// Word-specific API (convenience wrapper)
let word = WordAutomation::new()?;
let windows = word.find_windows()?;  // Uses WindowDiscovery internally

// Future: App-specific features
let status_bar = word.get_status_bar_items(&windows[0])?;
let nav_pane = word.get_navigation_pane(&windows[0])?;
```

### Future Expansion

```rust
// Excel automation (future)
let excel = ExcelAutomation::new()?;
let sheets = excel.get_sheets(&window)?;

// PowerPoint automation (future)
let ppt = PowerPointAutomation::new()?;
let slides = ppt.get_slides(&window)?;
```

---

## Design Principles

### 1. **Layered Architecture**
- Each layer builds on the one below
- Lower layers are generic and reusable
- Higher layers add domain-specific logic

### 2. **Type Safety**
- No dictionary/HashMap returns
- Strongly-typed structs for all data
- Compile-time guarantees

### 3. **Extensibility**
- Generic window discovery works for ANY app
- Easy to add new application-specific modules
- Filter system is composable and flexible

### 4. **Error Handling**
- Explicit `Result<T>` types everywhere
- Descriptive error messages
- No silent failures

### 5. **API Design**
- Consistent naming (find_*, get_*, with_*)
- Builder pattern for filters
- Method chaining where appropriate

---

## Usage Patterns

### Pattern 1: Generic Discovery

Use when you want to work with **any** application:

```rust
use screenbridge_core::{AutomationContext, WindowDiscovery};

let context = AutomationContext::new()?;
let discovery = WindowDiscovery::new(&context);

// Find any application
let chrome_windows = discovery.find_by_process("chrome.exe")?;
let vscode_windows = discovery.find_by_process("code.exe")?;
```

### Pattern 2: App-Specific API

Use when you want **convenience methods** for a specific app:

```rust
use screenbridge_core::WordAutomation;

let word = WordAutomation::new()?;
let windows = word.find_windows()?;

// Future: app-specific features
// let status_bar = word.get_status_bar_items(&windows[0])?;
```

### Pattern 3: Custom Filtering

Use when you need **precise control** over window selection:

```rust
use screenbridge_core::{WindowDiscovery, WindowFilter};

let filter = WindowFilter::for_process("winword.exe")
    .with_title("Thesis")
    .only_main_windows();

let thesis_windows = discovery.find_windows_with_filter(&filter)?;
```

---

## Future Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Generic window discovery
- [x] Type-safe error handling
- [x] Flexible filtering system
- [x] Examples and documentation

### Phase 2: UI Element Extraction (Next)
- [ ] Status bar extraction (generic)
- [ ] Navigation pane access
- [ ] Ribbon/menu extraction
- [ ] Accessibility features

### Phase 3: App-Specific Features
- [ ] Word: Status bar, navigation, accessibility
- [ ] Excel: Sheets, cells, formulas (future)
- [ ] PowerPoint: Slides, animations (future)

### Phase 4: AI Integration (MCP)
- [ ] MCP server implementation
- [ ] Tool definitions for Claude
- [ ] Intelligent filtering and extraction

### Phase 5: Cross-Platform (Future Vision)
- [ ] macOS support (Accessibility API)
- [ ] Linux support (AT-SPI)
- [ ] Abstract platform differences

---

## Code Organization

```
screenbridge-core/
├── src/
│   ├── lib.rs              # Public API surface
│   ├── error.rs            # Error types
│   ├── elements.rs         # UI element wrappers
│   ├── automation.rs       # COM/UIA initialization
│   ├── discovery.rs        # ✅ Generic window discovery
│   └── window.rs           # Deprecated (use discovery.rs)
│
├── examples/
│   ├── find_word_windows.rs          # Word-specific
│   ├── explore_window_structure.rs   # Debugging tool
│   └── discover_any_app.rs           # ✅ Generic discovery demo
│
└── tests/                  # (Future) Integration tests
```

---

## Benefits of This Architecture

### For Braille Display Integration

1. **Flexibility**: Can extract UI from Word, browsers, or any app
2. **Extensibility**: Easy to add new data sources
3. **Type Safety**: No runtime surprises when processing UI data
4. **Testability**: Each layer can be tested independently

### For Developers

1. **Clear Separation**: Each layer has a single responsibility
2. **Reusability**: Generic layers work across all apps
3. **Maintainability**: Changes to one layer don't break others
4. **Documentation**: Self-documenting through types

### For Future AI Integration

1. **MCP Ready**: Structured data perfect for tool definitions
2. **Composable**: AI can chain operations across layers
3. **Extensible**: Easy to add new tools/capabilities
4. **Type-Safe**: AI gets structured responses, not raw text

---

## Questions?

See the [examples/README.md](screenbridge-core/examples/README.md) for practical usage examples.

See the [TEST_INSTRUCTIONS.md](screenbridge-core/TEST_INSTRUCTIONS.md) for testing procedures.
