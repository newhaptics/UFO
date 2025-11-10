# ScreenBridge

**Generic Windows UI automation library with JSON query protocol for assistive devices**

[![Rust](https://img.shields.io/badge/rust-1.70%2B-orange.svg)](https://www.rust-lang.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2B-blue.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 Overview

ScreenBridge provides programmatic access to Windows UI Automation (UIA) for **any Windows application**, enabling assistive devices like braille displays to access structured UI data through a simple JSON query protocol.

### Key Features

- ✅ **Universal**: Works with ANY Windows application (Word, Excel, Chrome, VS Code, etc.)
- ✅ **Honest API**: Returns ALL UIA data without hardcoded filtering
- ✅ **Type-Safe**: Rust implementation with strong compile-time guarantees
- ✅ **Property-Based**: Query real UIA properties (visible, focusable, bounds, etc.)
- ✅ **JSON Protocol**: Simple request/response format for device integration
- ✅ **Extensible**: Easy to add new query types and properties

### Primary Use Case

**Braille Display Integration**: Extract structured UI information from Windows applications and deliver it to braille hardware devices via JSON over a communication channel (UCP Proxy.exe).

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Query Protocol](#-query-protocol)
- [Examples](#-examples)
- [Integration Guide](#-integration-guide)
- [Development](#-development)
- [Contributing](#-contributing)

---

## 🚀 Quick Start

### Prerequisites

- **Platform**: Windows 10 or later
- **Rust**: 1.70+ (for building from source)
- **Microsoft Word**: For testing Word-specific features (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/microsoft/UFO.git
cd UFO/ScreenBridge

# Build the Rust library
cd screenbridge-core
cargo build --release
```

### Basic Usage (Rust API)

```rust
use screenbridge_core::{AutomationContext, WindowDiscovery, WindowFilter};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize UI Automation
    let context = AutomationContext::new()?;
    let discovery = WindowDiscovery::new(&context);

    // Find all visible, focusable windows (typical applications)
    let filter = WindowFilter::default()
        .only_visible()
        .only_focusable();

    let windows = discovery.find_windows_with_filter(&filter)?;

    // Print window information
    for window in windows {
        println!("Found: {}", window.title);

        // Query UIA properties
        let element = window.element();
        println!("  Visible: {}", element.is_visible()?);
        println!("  Focusable: {}", element.is_keyboard_focusable()?);

        let (x, y, w, h) = element.bounding_rectangle()?;
        println!("  Position: ({}, {}), Size: {}x{}", x, y, w, h);
    }

    Ok(())
}
```

### Run Examples

```bash
# Find windows from any application
cargo run --example discover_any_app

# Demonstrate honest API (all windows + properties)
cargo run --example honest_discovery

# Explore Word window structure
cargo run --example find_word_windows
```

---

## 🏗️ Architecture

ScreenBridge uses a **layered architecture** that separates concerns and enables flexible integration:

```
┌─────────────────────────────────────────────────────────────┐
│  Device Layer (Braille Display, Screen Reader, etc.)        │
│  - Consumes JSON responses                                  │
│  - Sends JSON queries                                       │
└────────────────────┬────────────────────────────────────────┘
                     │ JSON over UCP Proxy / Named Pipe / TCP
┌────────────────────┴────────────────────────────────────────┐
│  Query Server Layer (Future - To Be Built)                  │
│  - Handles JSON requests                                    │
│  - Calls Rust API                                           │
│  - Maintains element cache                                  │
│  - Returns JSON responses                                   │
└────────────────────┬────────────────────────────────────────┘
                     │ Function Calls
┌────────────────────┴────────────────────────────────────────┐
│  Rust API Layer (Current - screenbridge-core)               │
│  - WindowDiscovery: Find windows/panes                      │
│  - UIElement: Query UIA properties                          │
│  - WindowFilter: Property-based filtering                   │
│  - No hardcoded assumptions                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ COM/UIA Calls
┌────────────────────┴────────────────────────────────────────┐
│  Windows UI Automation API                                  │
│  - IUIAutomation COM interface                              │
│  - UI element tree                                          │
│  - Properties, patterns, events                             │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Truth at the Foundation**: Layer 1 returns ALL data from UIA
2. **Property-Based Filtering**: Use queryable UIA properties, not hardcoded lists
3. **No Assumptions**: Let higher layers decide what's relevant
4. **Stability**: Based on Windows UIA API (stable across versions)
5. **Extensibility**: Easy to add new properties and query types

See [HONEST_API_DESIGN.md](HONEST_API_DESIGN.md) for detailed philosophy.

---

## 📚 API Reference

### Core Components

#### `AutomationContext`

Handles COM initialization and UI Automation setup.

```rust
let context = AutomationContext::new()?;
let automation = context.automation(); // Get IUIAutomation instance
let root = context.get_root_element()?; // Get desktop root
```

#### `WindowDiscovery`

Generic window discovery service.

```rust
let discovery = WindowDiscovery::new(&context);

// Find all windows (no filtering)
let all = discovery.find_all_windows()?;

// Find by process name
let word_windows = discovery.find_by_process("winword.exe")?;

// Find with custom filter
let filter = WindowFilter::for_process("chrome.exe")
    .only_visible()
    .only_focusable();
let chrome_windows = discovery.find_windows_with_filter(&filter)?;
```

#### `WindowFilter`

Composable filter builder for window queries.

```rust
WindowFilter::default()
    .for_process("excel.exe")      // Specific application
    .with_title("Sheet1")           // Title substring match
    .only_visible()                 // UIA: CurrentIsOffscreen = false
    .only_focusable()               // UIA: CurrentIsKeyboardFocusable = true
    .only_main_windows()            // Exclude dialogs
    .excluding_titles(vec!["Print", "Options"]) // Exclude specific titles
```

#### `UIElement`

Wrapper around Windows UI Automation elements with property accessors.

```rust
let element = window.element();

// Query UIA properties
let name = element.name()?;                    // Window title
let class = element.class_name()?;             // Window class
let visible = element.is_visible()?;           // Not hidden
let offscreen = element.is_offscreen()?;       // Off all monitors
let focusable = element.is_keyboard_focusable()?; // Can receive focus
let enabled = element.is_enabled()?;           // Enabled state
let (x, y, w, h) = element.bounding_rectangle()?; // Position & size
let framework = element.framework_id()?;       // "Win32", "WPF", etc.
let pid = element.process_id()?;               // Process ID
let auto_id = element.automation_id()?;        // Automation ID
```

#### `WindowHandle`

Represents a discovered window with metadata and element access.

```rust
pub struct WindowHandle {
    pub title: String,        // Window title
    pub process_id: i32,      // Process ID
    // ... plus methods to access underlying UIElement
}

let element = window.element();  // Get UIElement for queries
```

### Return Types

All API methods use `Result<T, ScreenBridgeError>` for explicit error handling.

```rust
pub enum ScreenBridgeError {
    InitializationError(String),
    WindowNotFound(String),
    ElementNotFound(String),
    StaleElement(String),
    PropertyError(String),
    WindowsError(windows::core::Error),
    // ... more error types
}
```

---

## 🔌 Query Protocol

ScreenBridge uses a **JSON-based query protocol** for device integration. This enables bidirectional communication between assistive devices and Windows UI Automation.

### Protocol Overview

**Transport**: JSON messages over UCP Proxy.exe, Named Pipes, TCP, or stdin/stdout

**Message Format**: Line-delimited JSON (newline-separated JSON objects)

**Request Structure**:
```json
{
  "request_id": "string (unique identifier)",
  "query": "string (query type)",
  "params": { /* query-specific parameters */ }
}
```

**Response Structure**:
```json
{
  "request_id": "string (matches request)",
  "status": "success | error",
  "data": { /* response data */ },
  "error": "string (only if status=error)"
}
```

### Supported Queries

See [API_PROTOCOL.md](API_PROTOCOL.md) for complete OpenAPI specification.

#### 1. List Windows

**Request:**
```json
{
  "request_id": "req_001",
  "query": "list_windows",
  "params": {
    "filters": {
      "process_name": "winword.exe",
      "visible_only": true,
      "focusable_only": true
    }
  }
}
```

**Response:**
```json
{
  "request_id": "req_001",
  "status": "success",
  "data": {
    "windows": [
      {
        "window_id": "win_107084_abc123",
        "title": "Introduction - Word",
        "process_name": "winword.exe",
        "process_id": 107084,
        "class_name": "OpusApp",
        "visible": true,
        "focusable": true,
        "offscreen": false,
        "bounds": {"x": 0, "y": 0, "width": 1920, "height": 1080},
        "framework": "Win32"
      }
    ],
    "count": 1
  }
}
```

#### 2. Get Window Elements

**Request:**
```json
{
  "request_id": "req_002",
  "query": "get_window_elements",
  "params": {
    "window_id": "win_107084_abc123",
    "max_depth": 2,
    "element_types": ["pane", "button", "text"]
  }
}
```

**Response:**
```json
{
  "request_id": "req_002",
  "status": "success",
  "data": {
    "window_id": "win_107084_abc123",
    "elements": [
      {
        "element_id": "elem_456",
        "name": "Status Bar",
        "control_type": "pane",
        "class_name": "MsoDockBottom",
        "visible": true,
        "enabled": true,
        "bounds": {"x": 0, "y": 1050, "width": 1920, "height": 30}
      }
    ],
    "count": 1
  }
}
```

#### 3. Get Element Properties

**Request:**
```json
{
  "request_id": "req_003",
  "query": "get_element_properties",
  "params": {
    "element_id": "elem_456",
    "properties": ["name", "visible", "focusable", "bounds", "children_count"]
  }
}
```

**Response:**
```json
{
  "request_id": "req_003",
  "status": "success",
  "data": {
    "element_id": "elem_456",
    "properties": {
      "name": "Status Bar",
      "visible": true,
      "focusable": false,
      "bounds": {"x": 0, "y": 1050, "width": 1920, "height": 30},
      "children_count": 5
    }
  }
}
```

See [API_PROTOCOL.md](API_PROTOCOL.md) for complete specification with all query types and schemas.

---

## 💡 Examples

### Example 1: Find All Visible Applications

```rust
use screenbridge_core::{AutomationContext, WindowDiscovery, WindowFilter};

let context = AutomationContext::new()?;
let discovery = WindowDiscovery::new(&context);

let filter = WindowFilter::default()
    .only_visible()
    .only_focusable();

let apps = discovery.find_windows_with_filter(&filter)?;

for app in apps {
    println!("{} - {}", app.title, app.process_id);
}
```

### Example 2: Get Word Document Structure

```rust
use screenbridge_core::WordAutomation;

let word = WordAutomation::new()?;
let windows = word.find_windows()?;

for window in windows {
    println!("Word Document: {}", window.title);

    // Future: Extract status bar, navigation pane, etc.
    // let status_bar = word.get_status_bar_items(&window)?;
    // let nav_pane = word.get_navigation_pane(&window)?;
}
```

### Example 3: Query Window Properties

```rust
let element = window.element();

// Get all available properties
println!("Title: {}", element.name()?);
println!("Class: {}", element.class_name()?);
println!("Framework: {}", element.framework_id()?);
println!("Visible: {}", element.is_visible()?);
println!("Focusable: {}", element.is_keyboard_focusable()?);

let (x, y, w, h) = element.bounding_rectangle()?;
println!("Bounds: ({}, {}) {}x{}", x, y, w, h);
```

### Example 4: Custom Filtering Logic

```rust
let all_windows = discovery.find_all_windows()?;

for window in all_windows {
    let element = window.element();

    // YOUR custom logic using UIA properties
    let visible = element.is_visible().unwrap_or(false);
    let (_, _, width, height) = element.bounding_rectangle().unwrap_or((0, 0, 0, 0));

    // Example: Only large, visible windows
    if visible && width > 800 && height > 600 {
        println!("Large window: {}", window.title);
    }
}
```

More examples in `screenbridge-core/examples/`:
- `find_word_windows.rs` - Basic Word window discovery
- `discover_any_app.rs` - Multi-application discovery
- `honest_discovery.rs` - Demonstrates honest API with all properties
- `explore_window_structure.rs` - Deep UI tree exploration

---

## 🔧 Integration Guide

### For Braille Display Devices

**Step 1**: Define your query protocol (see [API_PROTOCOL.md](API_PROTOCOL.md))

**Step 2**: Implement communication channel:
- Option A: Named Pipe (Windows IPC)
- Option B: TCP Socket (localhost)
- Option C: Stdin/Stdout (subprocess)

**Step 3**: Build Query Server (or use ours when available):

```rust
// Pseudocode for query server
let server = QueryServer::new()?;

loop {
    let request_json = read_from_channel()?;
    let response_json = server.handle_request(&request_json)?;
    write_to_channel(&response_json)?;
}
```

**Step 4**: Device sends queries:

```json
{"request_id": "1", "query": "list_windows", "params": {"visible_only": true}}
```

**Step 5**: Device receives responses:

```json
{"request_id": "1", "status": "success", "data": {"windows": [...]}}
```

### For MCP (Model Context Protocol) Integration

ScreenBridge can be exposed as MCP tools for Claude/LLM integration:

```json
{
  "tools": [
    {
      "name": "screenbridge_list_windows",
      "description": "List all visible Windows application windows",
      "inputSchema": {
        "type": "object",
        "properties": {
          "process_name": {"type": "string"},
          "visible_only": {"type": "boolean"}
        }
      }
    }
  ]
}
```

---

## 🛠️ Development

### Project Structure

```
ScreenBridge/
├── README.md                       # This file
├── ARCHITECTURE.md                 # Detailed architecture
├── HONEST_API_DESIGN.md            # Design philosophy
├── API_PROTOCOL.md                 # OpenAPI specification
│
├── python-legacy/                  # Original Python implementation
│   ├── status_bar_api.py          # Reference implementation
│   └── README.md
│
└── screenbridge-core/              # Rust library
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs                  # Public API
    │   ├── error.rs                # Error types
    │   ├── elements.rs             # UI element wrappers
    │   ├── automation.rs           # COM/UIA initialization
    │   ├── discovery.rs            # Window discovery
    │   └── window.rs               # Legacy (deprecated)
    │
    ├── examples/                   # Usage examples
    │   ├── find_word_windows.rs
    │   ├── discover_any_app.rs
    │   ├── honest_discovery.rs
    │   └── explore_window_structure.rs
    │
    └── tests/                      # Integration tests
```

### Building

```bash
cd screenbridge-core

# Development build
cargo build

# Release build (optimized)
cargo build --release

# Run tests
cargo test

# Run specific example
cargo run --example honest_discovery

# Generate documentation
cargo doc --open
```

### Testing

```bash
# Run all tests
cargo test

# Run with output
cargo test -- --nocapture

# Test specific module
cargo test discovery

# Run examples (requires Word/apps open)
cargo run --example find_word_windows
```

### Code Style

This project follows standard Rust conventions:
- `rustfmt` for formatting
- `clippy` for linting
- Comprehensive documentation comments
- Type safety and error handling

```bash
# Format code
cargo fmt

# Run linter
cargo clippy
```

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines first.

### Areas for Contribution

1. **Query Server Implementation**: Build the JSON protocol server
2. **Additional UIA Properties**: Expose more Windows UIA properties
3. **App-Specific Modules**: Excel, PowerPoint automation (like Word)
4. **Transport Layers**: Named Pipe, TCP, WebSocket implementations
5. **Testing**: More integration tests, mocking, CI/CD
6. **Documentation**: More examples, tutorials, API docs

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`cargo test`)
5. Run formatter (`cargo fmt`)
6. Run linter (`cargo clippy`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

---

## 📖 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [HONEST_API_DESIGN.md](HONEST_API_DESIGN.md) - Design philosophy and principles
- [API_PROTOCOL.md](API_PROTOCOL.md) - Complete OpenAPI specification
- [screenbridge-core/README.md](screenbridge-core/README.md) - Rust library documentation
- [examples/README.md](screenbridge-core/examples/README.md) - Example code documentation

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Part of the [UFO (UI-Focused Agent)](https://github.com/microsoft/UFO) project by Microsoft Research
- Built on Windows UI Automation API
- Original Python implementation by Microsoft Research team
- Rust rewrite architecture inspired by modern API design principles

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/microsoft/UFO/issues)
- **Discussions**: [GitHub Discussions](https://github.com/microsoft/UFO/discussions)
- **Documentation**: [Full Documentation](docs/)

---

## 🚦 Status

**Current**: Phase 1 Complete - Core Rust API with honest, property-based window discovery

**Next**: Phase 2 - Query Server implementation with JSON protocol

**Roadmap**:
- ✅ Phase 1: Core Rust API (DONE)
- 🚧 Phase 2: JSON Query Server (IN PROGRESS)
- ⏳ Phase 3: UCP Proxy Integration
- ⏳ Phase 4: MCP Server
- ⏳ Phase 5: Additional app-specific modules (Excel, PowerPoint, etc.)

---

Made with ❤️ for accessibility
