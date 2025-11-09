# ScreenBridge Core

**Rust library for Microsoft Word UI automation via Windows UI Automation**

## Overview

ScreenBridge Core is a type-safe, performant Rust library that provides programmatic access to Microsoft Word UI elements through the Windows UI Automation API. It enables automation of Word features that aren't accessible through Word's COM API, including:

- Status bars and navigation panes
- Accessibility checker
- Grammar and spelling tools
- Ribbon controls
- Language settings
- Text prediction options

## Features

- **Type-Safe**: Strongly-typed API with explicit error handling via `Result` types
- **Performance**: Native Rust performance with minimal overhead
- **Memory Safe**: No runtime crashes from invalid element references
- **Windows Native**: Direct bindings to Windows UI Automation API
- **AI-Agnostic**: Can be used standalone or with AI agents (via MCP)
- **Reusable**: Embeddable in Python (PyO3), C (FFI), .NET, or other languages

## Architecture

This library is **Phase 1** of a three-layer architecture:

```
Layer 3: AI Agent (Claude via MCP)     [Future]
         ↓
Layer 2: MCP Server                    [Future]
         ↓
Layer 1: screenbridge-core (this)      [Current]
         ↓
Windows UI Automation API
```

## Project Status

**Current Phase: Phase 1 - Core Library Development**

This is a Rust rewrite of the original Python implementation (see `../python-legacy/`).

### Roadmap

- [ ] Window management
- [ ] Status bar extraction
- [ ] Navigation pane
- [ ] Accessibility features
- [ ] Grammar/spelling tools
- [ ] Ribbon controls
- [ ] Language settings
- [ ] Text prediction
- [ ] Complete API parity with Python version
- [ ] MCP server (Phase 2)
- [ ] AI integration examples (Phase 3)

## Requirements

- **Platform**: Windows 10 or later
- **Rust**: 1.70+ (2021 edition)
- **Dependencies**: Windows UI Automation API (included with Windows)

## Usage

```rust
use screenbridge_core::WordAutomation;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let word = WordAutomation::new()?;

    // Find all Word windows
    let windows = word.find_windows()?;

    // Get status bar items
    let status_bar = word.get_status_bar_items(&windows[0])?;
    println!("Page number: {:?}", status_bar.page_number);

    // Get accessibility issues
    let accessibility = word.get_accessibility_items(&windows[0])?;
    println!("Found {} issues", accessibility.issues.len());

    Ok(())
}
```

## Use Cases

- **Braille Display Integration**: Extract structured UI data for braille renderers
- **Accessibility Tools**: Programmatic access to Word's accessibility checker
- **Document Analysis**: Extract document structure and metadata
- **Automated Testing**: Test Word UI features
- **AI Agents**: Provide structured data to LLMs for intelligent document assistance

## Development

```bash
# Build the library
cargo build

# Run tests
cargo test

# Build documentation
cargo doc --open

# Run examples
cargo run --example basic_usage
```

## License

MIT License - see LICENSE file

## Reference Implementation

This Rust implementation is based on the Python version in `../python-legacy/status_bar_api.py`. See that implementation for detailed behavior and edge case handling.
