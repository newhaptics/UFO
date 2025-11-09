# Python Legacy Implementation

This directory contains the original Python implementation of ScreenBridge, archived as of January 2025.

## Original Implementation

The Python version provided UI automation for Microsoft Word through:
- `status_bar_api.py` - Main API with `WordWindowAPI` class (1,631 lines)
- `status_bar_api_test.py` - Test/example usage

## Why Archived?

ScreenBridge is being rewritten in Rust for:
- **Type Safety**: Stronger compile-time guarantees
- **Performance**: Faster UI automation operations
- **Memory Safety**: No runtime crashes from invalid element references
- **Better Error Handling**: Explicit Result types instead of None returns
- **Maintainability**: More robust for long-term development

## Current Development

The active Rust implementation is in:
- `../screenbridge-core/` - Core Rust library
- `../screenbridge-mcp/` - MCP server (future)

## Reference

This Python code serves as the reference implementation and specification for the Rust rewrite. All functionality from the Python version is being ported to Rust with improved APIs.

See git history for the full development timeline of the Python implementation.
